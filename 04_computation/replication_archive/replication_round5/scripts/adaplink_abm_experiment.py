import numpy as np
import pandas as pd
from dataclasses import dataclass, replace
from scipy.special import expit
from scipy import stats
from pathlib import Path
import json, platform, sys

ARCHIVE_ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ARCHIVE_ROOT / 'results' / 'main'
OUTDIR.mkdir(parents=True, exist_ok=True)

@dataclass(frozen=True)
class Params:
    n_students: int = 120
    n_jobs: int = 30
    n_skills: int = 73
    n_roles: int = 24
    n_industries: int = 10
    rounds: int = 6
    applications_per_round: int = 3
    shortlist_n: int = 5
    capacity_per_job: int = 2
    # evidence/resource mechanism
    resource_evidence_coupling: float = 0.55
    evidence_noise: float = 0.12
    # behavior
    explanation_uptake: float = 0.67
    lsm_acceptance: float = 0.58
    generic_learning_rate: float = 0.035
    explained_learning_rate: float = 0.072
    lsm_learning_rate: float = 0.120
    evidence_selfstudy_gain: float = 0.025
    evidence_task_gain: float = 0.165
    # employer
    interview_noise: float = 0.10
    hiring_temperature: float = 0.06
    hiring_threshold: float = 0.49
    credential_prior_mean: float = 0.33
    # student choice
    choice_temperature: float = 0.13
    target_switch_prob: float = 0.18

REGIMES = ['R0','R1','R2','R3']


def softmax(x, temp=1.0):
    z=(x-np.max(x))/max(temp,1e-8)
    e=np.exp(np.clip(z,-50,50)); return e/e.sum()


def weighted_gap(ability, demand):
    # 0=no gap, 1=max gap among required skills
    denom=demand.sum()+1e-9
    return np.maximum(demand-ability,0).sum()/denom


def gtf(ability, demand):
    return 1.0-weighted_gap(ability,demand)


def skill_similarity(profile, demand):
    denom=demand.sum()+1e-9
    return np.minimum(profile,demand).sum()/denom


def make_base_society(seed:int, p:Params):
    rng=np.random.default_rng(seed)
    # Role prototypes: 6 core skills each; industry prototypes: 2 cross-cutting skills.
    role_proto=np.zeros((p.n_roles,p.n_skills))
    for r in range(p.n_roles):
        core=rng.choice(p.n_skills,size=6,replace=False)
        role_proto[r,core]=1
    ind_proto=np.zeros((p.n_industries,p.n_skills))
    for q in range(p.n_industries):
        inds=rng.choice(p.n_skills,size=2,replace=False)
        ind_proto[q,inds]=1

    # Job demand: public benchmark calibration targets ~5 skills/job, 24 roles, 10 industries, balanced seniority.
    job_roles=np.arange(p.n_jobs)%p.n_roles
    rng.shuffle(job_roles)
    job_inds=np.arange(p.n_jobs)%p.n_industries
    rng.shuffle(job_inds)
    job_seniority=np.arange(p.n_jobs)%3
    rng.shuffle(job_seniority)
    demands=np.zeros((p.n_jobs,p.n_skills))
    wage=np.zeros(p.n_jobs)
    for j in range(p.n_jobs):
        pool=np.flatnonzero((role_proto[job_roles[j]]+ind_proto[job_inds[j]])>0)
        # around 5 must-have skills, as in public benchmark card
        k=int(np.clip(rng.poisson(5.0),4,7))
        chosen=rng.choice(pool,size=min(k,len(pool)),replace=False)
        demands[j,chosen]=rng.uniform(0.62,1.0,size=len(chosen))
        wage[j]=0.45+0.12*job_seniority[j]+rng.normal(0,0.05)
    wage=np.clip(wage,0.25,0.95)

    # Students: supply-demand ratio 4:1 and avg ~6.5 listed skills/resume.
    stu_roles=rng.integers(0,p.n_roles,size=p.n_students)
    stu_inds=rng.integers(0,p.n_industries,size=p.n_students)
    stu_seniority=np.arange(p.n_students)%3
    rng.shuffle(stu_seniority)
    resource=rng.beta(2.2,2.2,size=p.n_students)
    readiness=np.clip(rng.beta(4,2,size=p.n_students),0.15,1)
    school_signal=np.clip(0.55*resource+0.15*stu_seniority/2+rng.normal(0,0.18,p.n_students),0,1)

    ability=np.zeros((p.n_students,p.n_skills))
    claim=np.zeros_like(ability)
    cred=np.zeros_like(ability)
    skill_count=np.zeros(p.n_students,dtype=int)
    for i in range(p.n_students):
        pool=np.flatnonzero((role_proto[stu_roles[i]]+ind_proto[stu_inds[i]])>0)
        # target mean around 6.5 active skills; include adjacent/random skills
        k=int(np.clip(rng.poisson(6.5),4,11))
        ncore=min(len(pool),max(3,int(round(k*0.75))))
        active=list(rng.choice(pool,size=ncore,replace=False))
        remaining=[x for x in range(p.n_skills) if x not in active]
        if k>ncore:
            active += list(rng.choice(remaining,size=k-ncore,replace=False))
        active=np.array(active,dtype=int)
        skill_count[i]=len(active)
        # seniority shifts skill strength modestly
        base=0.45+0.10*stu_seniority[i]
        ability[i,active]=np.clip(rng.normal(base+0.20,0.13,size=len(active)),0.15,1.0)
        # credibility is correlated with resource access but not identical to ability
        ev_base=0.18 + p.resource_evidence_coupling*resource[i] + 0.10*stu_seniority[i]
        cred[i,active]=np.clip(ev_base+rng.normal(0,p.evidence_noise,size=len(active)),0.05,1.0)
        # claims are noisy measurements; allow some weakly evidenced mentions
        claim[i,active]=np.clip(ability[i,active]+rng.normal(0,0.10,size=len(active)),0.05,1.0)
        # 0-1 extra text-only claims
        if rng.random()<0.45:
            extra=rng.choice(np.flatnonzero(claim[i]==0))
            claim[i,extra]=rng.uniform(0.25,0.55)
            cred[i,extra]=rng.uniform(0.05,0.25)

    employer_cred_prior=np.clip(rng.beta(2.3,4.7,size=p.n_jobs),0.05,0.75)
    # Scale to requested mean without destroying heterogeneity.
    employer_cred_prior=np.clip(employer_cred_prior*(p.credential_prior_mean/(employer_cred_prior.mean()+1e-9)),0.03,0.80)

    # target job based on role/seniority affinity and latent fit, but with imperfect preference
    targets=np.zeros(p.n_students,dtype=int)
    for i in range(p.n_students):
        latent=np.array([gtf(ability[i],demands[j]) for j in range(p.n_jobs)])
        role_aff=(job_roles==stu_roles[i]).astype(float)*0.20
        ind_aff=(job_inds==stu_inds[i]).astype(float)*0.08
        sen_aff=(job_seniority<=stu_seniority[i]).astype(float)*0.06
        utility=latent+role_aff+ind_aff+sen_aff+0.10*wage+rng.normal(0,0.06,p.n_jobs)
        targets[i]=int(np.argmax(utility))

    return dict(role_proto=role_proto,ind_proto=ind_proto,job_roles=job_roles,job_inds=job_inds,
                job_seniority=job_seniority,demands=demands,wage=wage,stu_roles=stu_roles,
                stu_inds=stu_inds,stu_seniority=stu_seniority,resource=resource,readiness=readiness,
                school_signal=school_signal,ability=ability,claim=claim,cred=cred,targets=targets,
                employer_cred_prior=employer_cred_prior,skill_count=skill_count)


def pair_features(state, i, j):
    d=state['demands'][j]
    observed=state['claim'][i]
    cred=state['cred'][i]
    ev_profile=observed*cred
    kw=skill_similarity(observed,d)
    evidence=skill_similarity(ev_profile,d)
    support=(cred[d>0].mean() if np.any(d>0) else 0.0)
    # adjacent potential: claimed nonrequired skills scaled by evidence
    extra=(ev_profile*(d==0)).sum()/(max((d==0).sum(),1))
    potential=np.clip(3.0*extra,0,1)
    major=(state['stu_roles'][i]==state['job_roles'][j])
    industry=(state['stu_inds'][i]==state['job_inds'][j])
    senior=(state['stu_seniority'][i]>=state['job_seniority'][j])
    return kw,evidence,support,potential,float(major),float(industry),float(senior)


def shortlist_score(state,i,j,regime):
    kw,evidence,support,potential,major,industry,senior=pair_features(state,i,j)
    school=state['school_signal'][i]
    if regime=='R0':
        return 0.44*kw + 0.24*major + 0.10*industry + 0.15*school + 0.07*senior
    # TAI-style frozen evidence-aware score: observed evidence, support, skill relation/potential, no latent ability.
    return 0.67*evidence + 0.13*support + 0.08*kw + 0.06*potential + 0.04*industry + 0.02*senior


def student_perceived_score(state,i,j):
    # same choice information in R0/R1 initially; feedback can update target in R2/R3.
    kw,evidence,support,potential,major,industry,senior=pair_features(state,i,j)
    target_bonus=0.14*(j==state['targets'][i])
    return 0.44*kw+0.17*major+0.09*industry+0.08*senior+0.10*state['wage'][j]+target_bonus+0.12*evidence


def employer_decision_score(state,i,j,regime,rng,p:Params):
    kw,evidence,support,potential,major,industry,senior=pair_features(state,i,j)
    latent_fit=gtf(state['ability'][i],state['demands'][j])
    task_signal=np.clip(latent_fit+rng.normal(0,p.interview_noise),0,1)
    school=state['school_signal'][i]
    prior=state['employer_cred_prior'][j]
    if regime=='R0':
        evidence_conf=0.18+0.25*kw
    else:
        evidence_conf=np.clip(0.10+0.75*support+0.15*evidence,0,1)
    wcred=prior/(1.0+2.0*evidence_conf)
    wmajor=0.12/(1.0+1.3*evidence_conf)
    # explicit task signal + ranking information; weights normalized
    rank=shortlist_score(state,i,j,regime)
    weights=np.array([0.48,0.30,wcred,wmajor])
    vals=np.array([task_signal,rank,school,major])
    score=float((weights*vals).sum()/weights.sum())
    return score, latent_fit, wcred


def choose_applications(state,i,open_jobs,rng,p):
    if len(open_jobs)==0: return []
    util=np.array([student_perceived_score(state,i,j) for j in open_jobs])
    util+=rng.normal(0,0.035,len(util))
    k=min(p.applications_per_round,len(open_jobs))
    # weighted without replacement
    chosen=[]; avail=list(range(len(open_jobs)))
    for _ in range(k):
        probs=softmax(util[avail],p.choice_temperature)
        idx_local=int(rng.choice(len(avail),p=probs))
        idx=avail.pop(idx_local); chosen.append(open_jobs[idx])
    return chosen


def find_top_gap_skill(state,i,j,observed=True):
    d=state['demands'][j]
    prof=state['claim'][i]*state['cred'][i] if observed else state['ability'][i]
    gap=np.maximum(d-prof,0)
    if gap.max()<=0: return int(np.argmax(d))
    return int(np.argmax(gap))


def learning_step(state,i,regime,rng,p,round_idx,events):
    j=int(state['targets'][i])
    latent_before=weighted_gap(state['ability'][i],state['demands'][j])
    observed_top=find_top_gap_skill(state,i,j,observed=True)
    latent_top=find_top_gap_skill(state,i,j,observed=False)
    readiness=state['readiness'][i]
    resource=state['resource'][i]
    alignment_effort=0.0
    attempted=False; accepted=False; action='generic'; target_skill=None
    realized_gain=0.0; evidence_gain=0.0

    if regime in ('R0','R1'):
        # generic/job-relevant learning with limited targeting information
        relevant=np.flatnonzero(state['demands'][j]>0)
        if rng.random()<0.35 and len(relevant):
            target_skill=int(rng.choice(relevant))
        else:
            target_skill=int(rng.integers(0,p.n_skills))
        effort=1.0
        alignment_effort=float(target_skill==latent_top)
        quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
        realized_gain=p.generic_learning_rate*quality*(0.55+0.45*resource)
        evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
    elif regime=='R2':
        action='explanation-guided self-study'; attempted=True
        uptake=np.clip(p.explanation_uptake*(0.55+0.45*readiness),0,0.95)
        if rng.random()<uptake:
            accepted=True; target_skill=observed_top; effort=0.72
            alignment_effort=effort*float(target_skill==latent_top)
            # rest of effort is diffuse; it does not count as targeted alignment
            quality=np.clip(rng.beta(3.3,2.3)*readiness,0,1)
            realized_gain=p.explained_learning_rate*quality*(0.50+0.50*resource)
            evidence_gain=p.evidence_selfstudy_gain*1.35*quality*(0.35+0.65*resource)
        else:
            target_skill=int(rng.integers(0,p.n_skills)); effort=1.0
            quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
            realized_gain=p.generic_learning_rate*quality*(0.55+0.45*resource)
            evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
            alignment_effort=float(target_skill==latent_top)
    else: # R3
        action='LSM task'; attempted=True
        uptake=np.clip(p.explanation_uptake*(0.55+0.45*readiness),0,0.95)
        if rng.random()<uptake:
            target_skill=observed_top
            accept=np.clip(p.lsm_acceptance*(0.50+0.50*readiness),0,0.95)
            if rng.random()<accept:
                accepted=True; effort=0.82; alignment_effort=effort*float(target_skill==latent_top)
                # standardized task reduces resource dependence but does not eliminate it
                quality=np.clip(rng.beta(3.5,2.1)*readiness+rng.normal(0,0.05),0,1)
                realized_gain=p.lsm_learning_rate*quality*(0.92+0.08*resource)
                evidence_gain=p.evidence_task_gain*quality
            else:
                action='LSM refused; self-study'; effort=0.65; alignment_effort=effort*float(target_skill==latent_top)
                quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
                realized_gain=p.explained_learning_rate*0.70*quality*(0.50+0.50*resource)
                evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
        else:
            target_skill=int(rng.integers(0,p.n_skills)); effort=1.0
            quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
            realized_gain=p.generic_learning_rate*quality*(0.55+0.45*resource)
            evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
            alignment_effort=float(target_skill==latent_top)

    # stochastic realization: gains can be near zero and are never negative enough to make ability decrease.
    realized_gain=max(0.0,realized_gain+rng.normal(0,0.008))
    evidence_gain=max(0.0,evidence_gain+rng.normal(0,0.006))
    weak_before=state['cred'][i,target_skill] < 0.40
    state['ability'][i,target_skill]=np.clip(state['ability'][i,target_skill]+realized_gain,0,1)
    # claims follow ability only partially
    state['claim'][i,target_skill]=np.clip(max(state['claim'][i,target_skill],state['ability'][i,target_skill]-rng.uniform(0.02,0.12)),0,1)
    state['cred'][i,target_skill]=np.clip(state['cred'][i,target_skill]+evidence_gain,0,1)
    # A successfully completed LSM task is defined to create a verifiable artifact; this is a first-stage intervention check, not a behavioral discovery.
    if regime=='R3' and accepted and action=='LSM task' and quality >= 0.55:
        state['cred'][i,target_skill]=max(state['cred'][i,target_skill], min(0.72, 0.55 + 0.25*(quality-0.55)))
    strong_after=state['cred'][i,target_skill] >= 0.55
    latent_after=weighted_gap(state['ability'][i],state['demands'][j])

    # occasional target switching in explanation regimes when persistent gap remains
    if regime in ('R2','R3') and rng.random()<p.target_switch_prob*(0.3+latent_after):
        scores=np.array([skill_similarity(state['claim'][i]*state['cred'][i],state['demands'][jj])+0.08*state['wage'][jj] for jj in range(p.n_jobs)])
        state['targets'][i]=int(np.argmax(scores+rng.normal(0,0.04,p.n_jobs)))

    events.append(dict(round=round_idx,student=i,regime=regime,target_job=j,target_skill=target_skill,
                       attempted=attempted,accepted=accepted,action=action,resource=resource,
                       alignment_effort=alignment_effort,realized_gain=realized_gain,evidence_gain=evidence_gain,
                       weak_before=weak_before,strong_after=strong_after,gap_before=latent_before,gap_after=latent_after))


def credential_audit(state,regime,p):
    # Deterministic within-profile decision propensity using expected task signal; credential flipped 1-school.
    vals=[]
    for i in range(p.n_students):
        j=int(state['targets'][i])
        kw,evidence,support,potential,major,industry,senior=pair_features(state,i,j)
        latent_fit=gtf(state['ability'][i],state['demands'][j])
        rank=shortlist_score(state,i,j,regime)
        prior=state['employer_cred_prior'][j]
        if regime=='R0': evidence_conf=0.18+0.25*kw
        else: evidence_conf=np.clip(0.10+0.75*support+0.15*evidence,0,1)
        wcred=prior/(1+2.0*evidence_conf)
        wmajor=0.12/(1+1.3*evidence_conf)
        weights=np.array([0.48,0.30,wcred,wmajor]); denom=weights.sum()
        def prop(school):
            sc=(weights*np.array([latent_fit,rank,school,major])).sum()/denom
            return expit((sc-p.hiring_threshold)/p.hiring_temperature)
        orig=prop(state['school_signal'][i]); cf=prop(1-state['school_signal'][i])
        vals.append(abs(orig-cf))
    return float(np.mean(vals))


def simulate(seed:int,regime:str,p:Params):
    base=make_base_society(seed,p)
    # mutable copy arrays
    state={k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in base.items()}
    rng=np.random.default_rng(seed*1009 + {'R0':11,'R1':23,'R2':37,'R3':51}[regime])
    employed=np.zeros(p.n_students,dtype=bool)
    hire_job=np.full(p.n_students,-1,dtype=int)
    hire_round=np.full(p.n_students,-1,dtype=int)
    capacities=np.full(p.n_jobs,p.capacity_per_job,dtype=int)
    vacancy_age=np.zeros(p.n_jobs,dtype=int)
    total_apps=np.zeros(p.n_students,dtype=int)
    learning_events=[]; hire_events=[]; round_rows=[]

    initial_resource=state['resource'].copy()
    initial_cred=state['cred'].copy()
    initial_target_gap=np.array([weighted_gap(state['ability'][i],state['demands'][state['targets'][i]]) for i in range(p.n_students)])

    for t in range(1,p.rounds+1):
        open_jobs=np.flatnonzero(capacities>0).tolist()
        apps_by_job={j:[] for j in open_jobs}
        # Applications
        for i in np.flatnonzero(~employed):
            chosen=choose_applications(state,i,open_jobs,rng,p)
            total_apps[i]+=len(chosen)
            for j in chosen: apps_by_job[j].append(i)
        # Employer decisions, at most one hire per job per round, capacity remains for later rounds
        for j in open_jobs:
            candidates=apps_by_job.get(j,[])
            if not candidates: continue
            scores=np.array([shortlist_score(state,i,j,regime) for i in candidates])
            # top shortlist candidates; random tie-break noise
            order=np.argsort(-(scores+rng.normal(0,0.003,len(scores))))[:p.shortlist_n]
            shortlist=[candidates[o] for o in order if not employed[candidates[o]]]
            if not shortlist: continue
            dvals=[]
            for i in shortlist:
                sc,lf,wc=employer_decision_score(state,i,j,regime,rng,p)
                dvals.append((sc,i,lf,wc))
            dvals.sort(reverse=True,key=lambda z:z[0])
            sc,i,lf,wc=dvals[0]
            prob=expit((sc-p.hiring_threshold)/p.hiring_temperature)
            if rng.random()<prob and not employed[i] and capacities[j]>0:
                employed[i]=True; hire_job[i]=j; hire_round[i]=t; capacities[j]-=1
                hire_events.append(dict(round=t,student=i,job=j,regime=regime,decision_score=sc,ground_truth_fit=lf,credential_weight=wc,resource=state['resource'][i]))
        # vacancy ages
        vacancy_age[capacities>0]+=1
        # Feedback + learning for unemployed
        for i in np.flatnonzero(~employed):
            learning_step(state,i,regime,rng,p,t,learning_events)
        # round summary
        gaps=np.array([weighted_gap(state['ability'][i],state['demands'][state['targets'][i]]) for i in range(p.n_students)])
        round_rows.append(dict(seed=seed,regime=regime,round=t,placement=employed.mean(),mean_gap=gaps.mean(),open_capacity=capacities.sum()))

    # metrics
    hired_idx=np.flatnonzero(employed)
    gtf_hires=np.array([gtf(state['ability'][i],state['demands'][hire_job[i]]) for i in hired_idx]) if len(hired_idx) else np.array([np.nan])
    avg_search_round=float(np.mean(hire_round[hired_idx])) if len(hired_idx) else np.nan
    avg_apps=float(np.mean(total_apps[hired_idx])) if len(hired_idx) else np.nan
    fill_rate=float((p.n_jobs*p.capacity_per_job-capacities.sum())/(p.n_jobs*p.capacity_per_job))
    vac_dur=float(np.mean(vacancy_age))
    cred_sens=credential_audit(state,regime,p)
    lev=pd.DataFrame(learning_events)
    if len(lev):
        align=float(lev['alignment_effort'].mean())
        gap_reduction=float((lev['gap_before']-lev['gap_after']).mean())
        # horizon-level conversion is computed below from the initial/final state; event-level transitions are too sparse.
        task_accept=float(lev['accepted'].mean())
        mean_gain=float(lev['realized_gain'].mean())
    else:
        align=gap_reduction=evidence_conv=task_accept=mean_gain=np.nan
    # Horizon-level evidence conversion among initially weak skills required by each student's initial target job.
    weak_target=[]; strong_target=[]
    for i in range(p.n_students):
        req=base['demands'][base['targets'][i]]>0
        wk=req & (initial_cred[i] < 0.40)
        if wk.any():
            weak_target.extend([True]*int(wk.sum()))
            strong_target.extend(list((state['cred'][i,wk] >= 0.55)))
    evidence_conv=float(np.mean(strong_target)) if len(strong_target) else 0.0
    # resource opportunity gap: high Q4 minus low Q1 placement
    q1,q3=np.quantile(initial_resource,[0.25,0.75])
    low=initial_resource<=q1; high=initial_resource>=q3
    opp_gap=float(employed[high].mean()-employed[low].mean())
    # final target gap reduction against each student's initial target gap (same base target, not switched target)
    final_initial_target_gap=np.array([weighted_gap(state['ability'][i],state['demands'][base['targets'][i]]) for i in range(p.n_students)])
    total_gap_reduction=float(np.mean(initial_target_gap-final_initial_target_gap))
    return dict(seed=seed,regime=regime,placement_rate=float(employed.mean()),ground_truth_fit=float(np.nanmean(gtf_hires)),
                search_rounds=avg_search_round,applications_per_hire=avg_apps,fill_rate=fill_rate,vacancy_duration=vac_dur,
                credential_sensitivity=cred_sens,investment_alignment=align,mean_step_gap_reduction=gap_reduction,
                total_gap_reduction=total_gap_reduction,evidence_conversion=evidence_conv,task_acceptance=task_accept,
                realized_gain=mean_gain,evidence_opportunity_gap=opp_gap), pd.DataFrame(round_rows), lev, pd.DataFrame(hire_events)


def summarize_run_metrics(df):
    rows=[]
    metrics=['placement_rate','ground_truth_fit','search_rounds','applications_per_hire','fill_rate','vacancy_duration',
             'credential_sensitivity','investment_alignment','total_gap_reduction','evidence_conversion','task_acceptance','realized_gain','evidence_opportunity_gap']
    for reg in REGIMES:
        sub=df[df.regime==reg]
        for m in metrics:
            x=sub[m].dropna().to_numpy(float)
            mean=x.mean(); sd=x.std(ddof=1); se=sd/np.sqrt(len(x)); ci=stats.t.interval(0.95,len(x)-1,loc=mean,scale=se) if len(x)>1 else (np.nan,np.nan)
            rows.append(dict(regime=reg,metric=m,n=len(x),mean=mean,sd=sd,ci_low=ci[0],ci_high=ci[1]))
    return pd.DataFrame(rows)


def paired_contrasts(df):
    contrasts=[('R1-R0','R1','R0'),('R2-R1','R2','R1'),('R3-R2','R3','R2'),('R3-R0','R3','R0')]
    metrics=['placement_rate','ground_truth_fit','search_rounds','applications_per_hire','fill_rate','vacancy_duration',
             'credential_sensitivity','investment_alignment','total_gap_reduction','evidence_conversion','evidence_opportunity_gap']
    rows=[]
    piv=df.pivot(index='seed',columns='regime',values=metrics)
    for label,a,b in contrasts:
        for m in metrics:
            d=(piv[m][a]-piv[m][b]).dropna().to_numpy(float)
            n=len(d); mean=d.mean(); sd=d.std(ddof=1); se=sd/np.sqrt(n); ci=stats.t.interval(0.95,n-1,loc=mean,scale=se)
            dz=mean/sd if sd>0 else np.nan
            t,pv=stats.ttest_1samp(d,0.0)
            rows.append(dict(contrast=label,metric=m,n=n,mean_diff=mean,sd_diff=sd,ci_low=ci[0],ci_high=ci[1],cohen_dz=dz,p_value=pv,mcse=se))
    return pd.DataFrame(rows)


def run_experiment(n_seeds=100,p=Params(),label='main'):
    metrics=[]; rounds=[]; learn=[]; hires=[]
    for seed in range(1000,1000+n_seeds):
        for reg in REGIMES:
            m,r,l,h=simulate(seed,reg,p)
            metrics.append(m); rounds.append(r)
            if len(l): l=l.copy(); l['seed']=seed; learn.append(l)
            if len(h): h=h.copy(); h['seed']=seed; hires.append(h)
    mdf=pd.DataFrame(metrics); rdf=pd.concat(rounds,ignore_index=True)
    ldf=pd.concat(learn,ignore_index=True) if learn else pd.DataFrame()
    hdf=pd.concat(hires,ignore_index=True) if hires else pd.DataFrame()
    mdf.to_csv(OUTDIR/f'{label}_run_metrics.csv',index=False)
    rdf.to_csv(OUTDIR/f'{label}_round_metrics.csv',index=False)
    ldf.to_csv(OUTDIR/f'{label}_learning_events.csv',index=False)
    hdf.to_csv(OUTDIR/f'{label}_hire_events.csv',index=False)
    summarize_run_metrics(mdf).to_csv(OUTDIR/f'{label}_summary.csv',index=False)
    paired_contrasts(mdf).to_csv(OUTDIR/f'{label}_contrasts.csv',index=False)
    return mdf,rdf,ldf,hdf


def sensitivity():
    base=Params()
    scenarios={
        'low_resource_gradient': replace(base,resource_evidence_coupling=0.30),
        'high_resource_gradient': replace(base,resource_evidence_coupling=0.72),
        'low_explanation_uptake': replace(base,explanation_uptake=0.45),
        'high_explanation_uptake': replace(base,explanation_uptake=0.82),
        'low_credential_prior': replace(base,credential_prior_mean=0.20),
        'high_credential_prior': replace(base,credential_prior_mean=0.48),
    }
    out=[]
    for name,pp in scenarios.items():
        m,_,_,_=run_experiment(n_seeds=30,p=pp,label=f'sens_{name}')
        c=paired_contrasts(m)
        c['scenario']=name; out.append(c)
    pd.concat(out,ignore_index=True).to_csv(OUTDIR/'sensitivity_contrasts.csv',index=False)

if __name__=='__main__':
    p=Params()
    m,r,l,h=run_experiment(n_seeds=100,p=p,label='main')
    sensitivity()
    meta={
        'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,
        'scipy':stats.__version__ if hasattr(stats,'__version__') else 'scipy',
        'params':p.__dict__,
        'public_benchmark_calibration':{
            'dataset':'michaelozon/candidate-matching-synthetic v1.0.0 (Hugging Face, MIT)',
            'used_published_aggregate_constraints':['4:1 candidate/job ratio','24 roles','10 industries','73 skills','3 balanced seniority levels','mean 6.5 skills/resume','mean 5.0 skills/job'],
            'note':'Record-level files were not redistributed; simulation microstates are freshly generated from the published aggregate design constraints.'
        }
    }
    (OUTDIR/'run_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(m.groupby('regime')[['placement_rate','ground_truth_fit','search_rounds','credential_sensitivity','investment_alignment','total_gap_reduction','evidence_conversion','evidence_opportunity_gap']].mean().round(4))
    c=paired_contrasts(m)
    print('\nPRIMARY CONTRASTS')
    print(c[c.metric.isin(['placement_rate','ground_truth_fit','search_rounds','credential_sensitivity','investment_alignment','total_gap_reduction','evidence_conversion','evidence_opportunity_gap'])][['contrast','metric','mean_diff','ci_low','ci_high','cohen_dz','p_value']].round(4).to_string(index=False))

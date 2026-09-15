import sys, json, math
from pathlib import Path
import numpy as np, pandas as pd
from dataclasses import replace
from scipy import stats
SCRIPT_DIR=Path(__file__).resolve().parent
ARCHIVE_ROOT=SCRIPT_DIR.parent
sys.path.insert(0,str(SCRIPT_DIR))
import adaplink_abm_experiment as abm
OUT=ARCHIVE_ROOT/'results'/'main'

# Additional allocation-level metrics from existing main runs.
run=pd.read_csv(OUT/'main_run_metrics.csv')
hires=pd.read_csv(OUT/'main_hire_events.csv')
# total capacity per run = 30 jobs * 2 = 60; realized aggregate fit per capacity
agg=[]
for (seed,reg),grp in hires.groupby(['seed','regime']):
    total_fit=grp['ground_truth_fit'].sum()
    agg.append({'seed':seed,'regime':reg,'aggregate_fit_per_capacity':total_fit/60.0,
                'total_realized_fit':total_fit,'filled_positions':len(grp),
                'welfare_vacancy_penalty_0p55':total_fit-0.55*(60-len(grp))})
agg=pd.DataFrame(agg)
full=run.merge(agg,on=['seed','regime'],how='left')
for col in ['aggregate_fit_per_capacity','total_realized_fit','welfare_vacancy_penalty_0p55']:
    # fill no hire impossibility no; there are hires always
    pass
full.to_csv(OUT/'additional_system_metrics.csv',index=False)

def paired_contrast_custom(df, metrics):
    contrasts=[('R1-R0','R1','R0'),('R2-R1','R2','R1'),('R3-R2','R3','R2')]
    rows=[]
    piv=df.pivot(index='seed',columns='regime',values=metrics)
    for label,a,b in contrasts:
        for m in metrics:
            d=(piv[m][a]-piv[m][b]).dropna().to_numpy(float)
            n=len(d); mean=d.mean(); sd=d.std(ddof=1); se=sd/math.sqrt(n)
            ci=stats.t.interval(0.95,n-1,loc=mean,scale=se)
            # Wilcoxon not robust with ties; bootstrap percentile
            rng=np.random.default_rng(20260829)
            boots=np.array([rng.choice(d,size=n,replace=True).mean() for _ in range(4000)])
            bci=np.percentile(boots,[2.5,97.5])
            rows.append({'contrast':label,'metric':m,'n':n,'mean_diff':mean,'ci_low':ci[0],'ci_high':ci[1],
                         'boot_low':bci[0],'boot_high':bci[1],'cohen_dz':mean/sd if sd>0 else np.nan,
                         'mcse':se})
    return pd.DataFrame(rows)
paired_contrast_custom(full,['aggregate_fit_per_capacity','total_realized_fit','welfare_vacancy_penalty_0p55']).to_csv(OUT/'additional_system_contrasts.csv',index=False)

# Holm correction for pre-specified Table 9 metrics
main_con=pd.read_csv(OUT/'main_contrasts.csv')
primary = main_con[((main_con['contrast']=='R1-R0') & (main_con['metric'].isin(['ground_truth_fit','placement_rate','search_rounds','credential_sensitivity','evidence_opportunity_gap']))) |
                   ((main_con['contrast']=='R2-R1') & (main_con['metric'].isin(['investment_alignment','total_gap_reduction']))) |
                   ((main_con['contrast']=='R3-R2') & (main_con['metric'].isin(['total_gap_reduction','evidence_conversion','placement_rate'])))]
primary=primary.copy().sort_values('p_value')
m=len(primary)
adj=[]; prev=0
for k,pv in enumerate(primary['p_value'],start=1):
    val=min(1,(m-k+1)*pv)
    prev=max(prev,val); adj.append(prev)
primary['holm_p']=adj
primary.to_csv(OUT/'additional_primary_holm.csv',index=False)

# neutral control simulations: R2_random_gap and R3_random_task target random demanded skill rather than top gap
orig_learning=abm.learning_step

def neutral_learning_factory(mode):
    def learning_step(state,i,regime,rng,p,round_idx,events):
        j=int(state['targets'][i])
        latent_before=abm.weighted_gap(state['ability'][i],state['demands'][j])
        latent_top=abm.find_top_gap_skill(state,i,j,observed=False)
        req=np.flatnonzero(state['demands'][j]>0)
        random_req=int(rng.choice(req)) if len(req) else int(rng.integers(0,p.n_skills))
        readiness=state['readiness'][i]; resource=state['resource'][i]
        alignment_effort=0.0; attempted=False; accepted=False; action='generic'; target_skill=random_req
        realized_gain=0.0; evidence_gain=0.0
        if mode=='R2_random':
            action='random-explanation self-study'; attempted=True
            uptake=np.clip(p.explanation_uptake*(0.55+0.45*readiness),0,0.95)
            if rng.random()<uptake:
                accepted=True; target_skill=random_req; effort=0.72
                alignment_effort=effort*float(target_skill==latent_top)
                quality=np.clip(rng.beta(3.3,2.3)*readiness,0,1)
                realized_gain=p.explained_learning_rate*quality*(0.50+0.50*resource)
                evidence_gain=p.evidence_selfstudy_gain*1.35*quality*(0.35+0.65*resource)
            else:
                # generic fallback
                target_skill=int(rng.integers(0,p.n_skills)); effort=1.0
                quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
                realized_gain=p.generic_learning_rate*quality*(0.55+0.45*resource)
                evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
                alignment_effort=float(target_skill==latent_top)
        elif mode=='R3_random':
            action='random LSM task'; attempted=True
            uptake=np.clip(p.explanation_uptake*(0.55+0.45*readiness),0,0.95)
            if rng.random()<uptake:
                target_skill=random_req
                accept=np.clip(p.lsm_acceptance*(0.50+0.50*readiness),0,0.95)
                if rng.random()<accept:
                    accepted=True; effort=0.82; alignment_effort=effort*float(target_skill==latent_top)
                    quality=np.clip(rng.beta(3.5,2.1)*readiness+rng.normal(0,0.05),0,1)
                    realized_gain=p.lsm_learning_rate*quality*(0.92+0.08*resource)
                    evidence_gain=p.evidence_task_gain*quality
                else:
                    action='random LSM refused; self-study'; effort=0.65; alignment_effort=effort*float(target_skill==latent_top)
                    quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
                    realized_gain=p.explained_learning_rate*0.70*quality*(0.50+0.50*resource)
                    evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
            else:
                target_skill=int(rng.integers(0,p.n_skills)); effort=1.0
                quality=np.clip(rng.beta(3.0,2.5)*readiness,0,1)
                realized_gain=p.generic_learning_rate*quality*(0.55+0.45*resource)
                evidence_gain=p.evidence_selfstudy_gain*quality*(0.35+0.65*resource)
                alignment_effort=float(target_skill==latent_top)
        realized_gain=max(0.0,realized_gain+rng.normal(0,0.008))
        evidence_gain=max(0.0,evidence_gain+rng.normal(0,0.006))
        weak_before=state['cred'][i,target_skill] < 0.40
        state['ability'][i,target_skill]=np.clip(state['ability'][i,target_skill]+realized_gain,0,1)
        state['claim'][i,target_skill]=np.clip(max(state['claim'][i,target_skill],state['ability'][i,target_skill]-rng.uniform(0.02,0.12)),0,1)
        state['cred'][i,target_skill]=np.clip(state['cred'][i,target_skill]+evidence_gain,0,1)
        if mode=='R3_random' and accepted and action=='random LSM task' and quality>=0.55:
            state['cred'][i,target_skill]=max(state['cred'][i,target_skill], min(0.72, 0.55 + 0.25*(quality-0.55)))
        strong_after=state['cred'][i,target_skill] >= 0.55
        latent_after=abm.weighted_gap(state['ability'][i],state['demands'][j])
        if regime in ('R2','R3') and rng.random()<p.target_switch_prob*(0.3+latent_after):
            scores=np.array([abm.skill_similarity(state['claim'][i]*state['cred'][i],state['demands'][jj])+0.08*state['wage'][jj] for jj in range(p.n_jobs)])
            state['targets'][i]=int(np.argmax(scores+rng.normal(0,0.04,p.n_jobs)))
        events.append(dict(round=round_idx,student=i,regime=mode,target_job=j,target_skill=target_skill,
                           attempted=attempted,accepted=accepted,action=action,resource=resource,
                           alignment_effort=alignment_effort,realized_gain=realized_gain,evidence_gain=evidence_gain,
                           weak_before=weak_before,strong_after=strong_after,gap_before=latent_before,gap_after=latent_after))
    return learning_step

def run_controls(n=40):
    rows=[]
    # R1 original baseline present in main_run_metrics
    main=pd.read_csv(OUT/'main_run_metrics.csv')
    rows.append(main[(main.seed>=1000)&(main.seed<1000+n)&(main.regime.isin(['R1','R2','R3']))].copy())
    for label, sim_reg, mode in [('R2_random','R2','R2_random'),('R3_random','R3','R3_random')]:
        abm.learning_step=neutral_learning_factory(mode)
        ms=[]
        for seed in range(1000,1000+n):
            m,_,_,_=abm.simulate(seed, sim_reg, abm.Params())
            m['regime']=label
            ms.append(m)
        rows.append(pd.DataFrame(ms))
    abm.learning_step=orig_learning
    df=pd.concat(rows,ignore_index=True)
    df.to_csv(OUT/'additional_neutral_controls_metrics.csv',index=False)
    # contrasts of specific controls
    piv=df.pivot(index='seed',columns='regime',values=['investment_alignment','total_gap_reduction','evidence_conversion','placement_rate','ground_truth_fit'])
    ctr=[]
    pairs=[('R2-R2_random','R2','R2_random'),('R2_random-R1','R2_random','R1'),('R3-R3_random','R3','R3_random'),('R3_random-R2','R3_random','R2')]
    for label,a,b in pairs:
        for m in ['investment_alignment','total_gap_reduction','evidence_conversion','placement_rate','ground_truth_fit']:
            d=(piv[m][a]-piv[m][b]).dropna().to_numpy(float)
            mean=d.mean(); se=d.std(ddof=1)/math.sqrt(len(d)); ci=stats.t.interval(0.95,len(d)-1,loc=mean,scale=se)
            ctr.append({'contrast':label,'metric':m,'mean_diff':mean,'ci_low':ci[0],'ci_high':ci[1],'n':len(d)})
    pd.DataFrame(ctr).to_csv(OUT/'additional_neutral_controls_contrasts.csv',index=False)
    return df,pd.DataFrame(ctr)

run_controls(40)

# structural sensitivity nulls: resource-evidence coupling zero, use existing function with p replace
scens={'zero_resource_evidence': replace(abm.Params(), resource_evidence_coupling=0.0),
       'very_low_resource_evidence': replace(abm.Params(), resource_evidence_coupling=0.1),
       'high_threshold': replace(abm.Params(), hiring_threshold=0.53),
       'low_threshold': replace(abm.Params(), hiring_threshold=0.45)}
allc=[]
for name,p in scens.items():
    m,_,_,_=abm.run_experiment(n_seeds=20,p=p,label=f'extra_{name}')
    c=abm.paired_contrasts(m); c['scenario']=name; allc.append(c)
pd.concat(allc,ignore_index=True).to_csv(OUT/'additional_structural_sensitivity.csv',index=False)

print('additional checks complete')

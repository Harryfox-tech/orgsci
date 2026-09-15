import sys, math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
from scipy import stats
SCRIPT_DIR=Path(__file__).resolve().parent
sys.path.insert(0,str(SCRIPT_DIR))
import adaplink_abm_experiment_v2 as abm
ARCHIVE_ROOT=Path(__file__).resolve().parents[1]
OUT=ARCHIVE_ROOT/'results'/'revision'; OUT.mkdir(parents=True,exist_ok=True)

def neutral_step(state,i,regime,rng,p,round_idx,events):
    j=int(state['targets'][i]); latent_before=abm.weighted_gap(state['ability'][i],state['demands'][j]); latent_top=abm.find_top_gap_skill(state,i,j,observed=False)
    req=np.flatnonzero(state['demands'][j]>0); target_skill=int(rng.choice(req)) if len(req) else int(rng.integers(0,p.n_skills))
    readiness=state['readiness'][i];resource=state['resource'][i];attempted=True;accepted=False;completed=False;action='random LSM task';alignment_effort=0.;quality=np.nan;realized_gain=0.;evidence_gain=0.
    uptake=np.clip(p.explanation_uptake*(0.55+0.45*readiness),0,0.95)
    if rng.random()<uptake:
        accept=np.clip(p.lsm_acceptance*(0.50+0.50*readiness),0,0.95)
        if rng.random()<accept:
            accepted=True;effort=.82;alignment_effort=effort*float(target_skill==latent_top);quality=np.clip(rng.beta(3.5,2.1)*readiness+rng.normal(0,.05),0,1)
            realized_gain=p.lsm_learning_rate*quality*abm.learning_modifier(resource,'lsm',p);evidence_gain=p.evidence_task_gain*quality
        else:
            action='random LSM refused; self-study';effort=.65;alignment_effort=effort*float(target_skill==latent_top);quality=np.clip(rng.beta(3.,2.5)*readiness,0,1)
            realized_gain=p.explained_learning_rate*.70*quality*abm.learning_modifier(resource,'explained',p);evidence_gain=p.evidence_selfstudy_gain*quality*abm.evidence_modifier(resource,p)
    else:
        action='random task not taken; generic self-study';target_skill=int(rng.integers(0,p.n_skills));effort=1.;quality=np.clip(rng.beta(3.,2.5)*readiness,0,1)
        realized_gain=p.generic_learning_rate*quality*abm.learning_modifier(resource,'generic',p);evidence_gain=p.evidence_selfstudy_gain*quality*abm.evidence_modifier(resource,p);alignment_effort=float(target_skill==latent_top)
    realized_gain=max(0.,realized_gain+rng.normal(0,.008));evidence_gain=max(0.,evidence_gain+rng.normal(0,.006));weak_before=state['cred'][i,target_skill]<.40
    state['ability'][i,target_skill]=np.clip(state['ability'][i,target_skill]+realized_gain,0,1);state['claim'][i,target_skill]=np.clip(max(state['claim'][i,target_skill],state['ability'][i,target_skill]-rng.uniform(.02,.12)),0,1);state['cred'][i,target_skill]=np.clip(state['cred'][i,target_skill]+evidence_gain,0,1)
    if accepted and quality>=.55: state['cred'][i,target_skill]=max(state['cred'][i,target_skill],min(.72,.55+.25*(quality-.55)));completed=True
    strong_after=state['cred'][i,target_skill]>=.55;latent_after=abm.weighted_gap(state['ability'][i],state['demands'][j])
    if rng.random()<p.target_switch_prob*(.3+latent_after):
        scores=np.array([abm.skill_similarity(state['claim'][i]*state['cred'][i],state['demands'][jj])+.08*state['wage'][jj] for jj in range(p.n_jobs)]);state['targets'][i]=int(np.argmax(scores+rng.normal(0,.04,p.n_jobs)))
    events.append(dict(round=round_idx,student=i,regime='R3_random',target_job=j,target_skill=target_skill,attempted=attempted,accepted=accepted,completed=completed,action=action,resource=resource,quality=quality,alignment_effort=alignment_effort,realized_gain=realized_gain,evidence_gain=evidence_gain,weak_before=weak_before,strong_after=strong_after,gap_before=latent_before,gap_after=latent_after))

def worker(t):
 seed,mode=t;p=abm.Params();old=abm.learning_step
 try:
  if mode=='R3_random': abm.learning_step=neutral_step
  m,_,l,_=abm.simulate(seed,'R3',p);m['condition']=mode;l=l.copy();l['seed']=seed;l['condition']=mode
  return m,l.to_dict('records')
 finally: abm.learning_step=old

tasks=[(s,m) for s in range(1000,1020) for m in ['R3','R3_random']]
metrics=[];events=[]
with ProcessPoolExecutor(max_workers=8) as ex:
 for m,l in ex.map(worker,tasks,chunksize=2): metrics.append(m);events+=l
mdf=pd.DataFrame(metrics).sort_values(['seed','condition']);edf=pd.DataFrame(events)
mdf.to_csv(OUT/'task_balance_run_metrics.csv',index=False);edf.to_csv(OUT/'task_balance_learning_events.csv',index=False)
# seed-level summaries
rows=[]
for (seed,cond),sub in edf.groupby(['seed','condition']):
 acc=sub.accepted.astype(bool); comp=sub.completed.astype(bool); q=sub.loc[acc,'quality'].astype(float); r=sub.loc[acc,'resource'].astype(float)
 rows.append(dict(seed=seed,condition=cond,acceptance_rate=acc.mean(),completion_rate=comp.mean(),quality_accepted=q.mean(),resource_accepted=r.mean()))
s=pd.DataFrame(rows);s.to_csv(OUT/'task_balance_by_seed.csv',index=False)
summary=[]
for cond in ['R3','R3_random']:
 sub=s[s.condition==cond]
 summary.append(dict(condition=cond,acceptance_rate=sub.acceptance_rate.mean(),completion_rate=sub.completion_rate.mean(),quality_accepted=sub.quality_accepted.mean(),resource_accepted=sub.resource_accepted.mean()))
pd.DataFrame(summary).to_csv(OUT/'task_balance_summary.csv',index=False)
cont=[]
for metric in ['acceptance_rate','completion_rate','quality_accepted','resource_accepted']:
 piv=s.pivot(index='seed',columns='condition',values=metric);d=(piv.R3-piv.R3_random).dropna().to_numpy(float);n=len(d);mean=d.mean();sd=d.std(ddof=1);se=sd/np.sqrt(n);ci=stats.t.interval(.95,n-1,loc=mean,scale=se);cont.append(dict(metric=metric,n=n,mean_diff=mean,ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(cont).to_csv(OUT/'task_balance_contrasts.csv',index=False)
print(pd.DataFrame(summary).to_string(index=False));print(pd.DataFrame(cont).to_string(index=False))

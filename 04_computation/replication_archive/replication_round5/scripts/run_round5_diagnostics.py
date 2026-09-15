from pathlib import Path
import sys, math, itertools
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
from scipy import stats
SCRIPT_DIR=Path(__file__).resolve().parent
ROOT=SCRIPT_DIR.parent
sys.path.insert(0,str(SCRIPT_DIR))
import adaplink_abm_experiment_v2 as abm
MAIN=ROOT/'results'/'main'; REV=ROOT/'results'/'revision'
REV.mkdir(parents=True,exist_ok=True)

# T2: Main Q1/Q4 placement levels from archived hire events and deterministic base societies.
hires=pd.read_csv(MAIN/'main_hire_events.csv')
rows=[]
for seed in range(1000,1040):
    base=abm.make_base_society(seed,abm.Params())
    res=base['resource']; q1,q3=np.quantile(res,[.25,.75]); low=res<=q1; high=res>=q3
    for reg in abm.REGIMES:
        ids=set(hires[(hires.seed==seed)&(hires.regime==reg)].student.astype(int).tolist())
        emp=np.array([i in ids for i in range(abm.Params().n_students)])
        rows.append(dict(seed=seed,regime=reg,q1_placement=float(emp[low].mean()),q4_placement=float(emp[high].mean()),gap=float(emp[high].mean()-emp[low].mean())))
main_levels=pd.DataFrame(rows)
main_levels.to_csv(REV/'resource_group_placement_levels_main.csv',index=False)
# summaries and R1-R0 group changes
summ=[]
for reg,g in main_levels.groupby('regime'):
    for col in ['q1_placement','q4_placement','gap']:
        x=g[col].to_numpy(float); se=x.std(ddof=1)/np.sqrt(len(x)); ci=stats.t.interval(.95,len(x)-1,loc=x.mean(),scale=se)
        summ.append(dict(regime=reg,metric=col,n=len(x),mean=x.mean(),ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(summ).to_csv(REV/'resource_group_placement_levels_main_summary.csv',index=False)
piv=main_levels.pivot(index='seed',columns='regime',values=['q1_placement','q4_placement','gap'])
ctr=[]
for col in ['q1_placement','q4_placement','gap']:
    d=(piv[col]['R1']-piv[col]['R0']).to_numpy(float); se=d.std(ddof=1)/np.sqrt(len(d)); ci=stats.t.interval(.95,len(d)-1,loc=d.mean(),scale=se)
    ctr.append(dict(metric=col,contrast='R1-R0',n=len(d),mean_diff=d.mean(),ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(ctr).to_csv(REV/'resource_group_placement_levels_main_contrasts.csv',index=False)

# T2 structural group-level decomposition based on rerun factorial metrics with new level columns.
fac=pd.read_csv(REV/'factorial_2x2x2_run_metrics.csv')
facp=fac.pivot_table(index=['seed','scenario'],columns='regime',values=['resource_q1_placement','resource_q4_placement','evidence_opportunity_gap']).reset_index()
# flatten columns
facp.columns=['seed','scenario','gap_R0','gap_R1','q1_R0','q1_R1','q4_R0','q4_R1'] if False else facp.columns
# easier extract directly cell-by-cell
level_rows=[]
for (seed,sc),g in fac.groupby(['seed','scenario']):
    r0=g[g.regime=='R0'].iloc[0]; r1=g[g.regime=='R1'].iloc[0]
    level_rows.append(dict(seed=seed,scenario=sc,
        q1_R0=r0.resource_q1_placement,q1_R1=r1.resource_q1_placement,q1_delta=r1.resource_q1_placement-r0.resource_q1_placement,
        q4_R0=r0.resource_q4_placement,q4_R1=r1.resource_q4_placement,q4_delta=r1.resource_q4_placement-r0.resource_q4_placement,
        gap_R0=r0.evidence_opportunity_gap,gap_R1=r1.evidence_opportunity_gap,gap_delta=r1.evidence_opportunity_gap-r0.evidence_opportunity_gap))
levels=pd.DataFrame(level_rows)
levels.to_csv(REV/'factorial_resource_group_level_decomposition_by_seed.csv',index=False)
ls=[]
for sc,g in levels.groupby('scenario'):
    for col in ['q1_delta','q4_delta','gap_delta']:
        x=g[col].to_numpy(float); se=x.std(ddof=1)/np.sqrt(len(x)); ci=stats.t.interval(.95,len(x)-1,loc=x.mean(),scale=se)
        ls.append(dict(scenario=sc,metric=col,n=len(x),mean_diff=x.mean(),ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(ls).to_csv(REV/'factorial_resource_group_level_decomposition_summary.csv',index=False)
# Direct E main effects on q1/q4 deltas, same factorial averaging construction.
levels[['E','L','C']]=levels.scenario.str.extract(r'E([01])_L([01])_C([01])').astype(int)
per=[]
for seed,g in levels.groupby('seed'):
    def av(col,E=None,L=None,C=None):
        q=g
        if E is not None:q=q[q.E==E]
        if L is not None:q=q[q.L==L]
        if C is not None:q=q[q.C==C]
        return q[col].mean()
    per.append(dict(seed=seed,
        E_main_q1=av('q1_delta',E=1)-av('q1_delta',E=0),
        E_main_q4=av('q4_delta',E=1)-av('q4_delta',E=0),
        E_main_gap=av('gap_delta',E=1)-av('gap_delta',E=0)))
per=pd.DataFrame(per); per.to_csv(REV/'factorial_resource_group_direct_effects_by_seed.csv',index=False)
def one(x):
    x=np.asarray(x,float);se=x.std(ddof=1)/np.sqrt(len(x));ci=stats.t.interval(.95,len(x)-1,loc=x.mean(),scale=se);return x.mean(),ci[0],ci[1],se
out=[]
for col in ['E_main_q1','E_main_q4','E_main_gap']:
    m,lo,hi,se=one(per[col]);out.append(dict(estimand=col,n=len(per),estimate=m,ci_low=lo,ci_high=hi,mcse=se))
pd.DataFrame(out).to_csv(REV/'factorial_resource_group_direct_effects_summary.csv',index=False)

# T3 exact sign-flip and bootstrap robustness for the direct evidence-channel effect.
direct=pd.read_csv(REV/'factorial_direct_effects_by_seed.csv')['E_main_effect'].to_numpy(float)
obs=direct.mean(); vals=[]
for signs in itertools.product([-1,1],repeat=len(direct)):
    vals.append(np.mean(direct*np.array(signs)))
vals=np.asarray(vals)
p_exact=float(np.mean(np.abs(vals)>=abs(obs)-1e-15))
rng=np.random.default_rng(20260829)
boots=np.array([rng.choice(direct,size=len(direct),replace=True).mean() for _ in range(50000)])
blo,bhi=np.percentile(boots,[2.5,97.5])
pd.DataFrame([dict(estimand='Evidence-channel main effect on R1-R0 resource-linked placement-gap delta',n=len(direct),estimate=obs,exact_sign_flip_p=p_exact,bootstrap_low=blo,bootstrap_high=bhi,n_sign_flips=len(vals),n_bootstrap=50000)]).to_csv(REV/'factorial_distribution_free_robustness.csv',index=False)

# T4 main 10/20/30/40 seed convergence.
main=pd.read_csv(MAIN/'main_run_metrics.csv')
checks=[('H1 fit','R1','R0','ground_truth_fit'),('H1 placement','R1','R0','placement_rate'),('H1 search','R1','R0','search_rounds'),('H3 alignment','R2','R1','investment_alignment'),('H3 gap','R2','R1','total_gap_reduction'),('H4 gap','R3','R2','total_gap_reduction'),('H4 evidence','R3','R2','evidence_conversion'),('H4 placement','R3','R2','placement_rate')]
conv=[]
for label,a,b,metric in checks:
    for N in [10,20,30,40]:
        sub=main[main.seed<1000+N].pivot(index='seed',columns='regime',values=metric)
        d=(sub[a]-sub[b]).dropna().to_numpy(float); se=d.std(ddof=1)/np.sqrt(len(d)); ci=stats.t.interval(.95,len(d)-1,loc=d.mean(),scale=se)
        conv.append(dict(test=label,contrast=f'{a}-{b}',metric=metric,n=len(d),estimate=d.mean(),ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(conv).to_csv(REV/'main_contrast_convergence.csv',index=False)

# T1 final-hiring institution sensitivity (20 paired seeds per scenario, R0/R1 only).
def worker(task):
    name,seed,reg,pdict=task
    p=abm.Params(**pdict); m,_,_,h=abm.simulate(seed,reg,p)
    total_fit=h.ground_truth_fit.sum() if len(h) else 0.0
    return dict(scenario=name,seed=seed,regime=reg,placement_rate=m['placement_rate'],ground_truth_fit=m['ground_truth_fit'],aggregate_fit_per_capacity=total_fit/(p.n_jobs*p.capacity_per_job))
base=abm.Params()
scenarios={
 'baseline':base,
 'lower_proxy_noise':replace(base,interview_noise=0.05),
 'higher_proxy_noise':replace(base,interview_noise=0.20),
 'lower_hiring_threshold':replace(base,hiring_threshold=0.46),
 'higher_hiring_threshold':replace(base,hiring_threshold=0.52),
}
tasks=[(name,seed,reg,p.__dict__) for name,p in scenarios.items() for seed in range(1000,1020) for reg in ['R0','R1']]
with ProcessPoolExecutor(max_workers=8) as ex:
    sens=pd.DataFrame(list(ex.map(worker,tasks,chunksize=2)))
sens.to_csv(REV/'hiring_institution_sensitivity_run_metrics.csv',index=False)
srows=[]
for sc,g in sens.groupby('scenario'):
    piv=g.pivot(index='seed',columns='regime',values=['placement_rate','ground_truth_fit','aggregate_fit_per_capacity'])
    for metric in ['placement_rate','ground_truth_fit','aggregate_fit_per_capacity']:
        d=(piv[metric]['R1']-piv[metric]['R0']).to_numpy(float); se=d.std(ddof=1)/np.sqrt(len(d)); ci=stats.t.interval(.95,len(d)-1,loc=d.mean(),scale=se)
        srows.append(dict(scenario=sc,metric=metric,n=len(d),mean_diff=d.mean(),ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(srows).to_csv(REV/'hiring_institution_sensitivity_contrasts.csv',index=False)

print('Main Q1/Q4 contrast:')
print(pd.DataFrame(ctr).to_string(index=False))
print('\nFactorial direct group effects:')
print(pd.DataFrame(out).to_string(index=False))
print('\nDistribution-free:',obs,p_exact,blo,bhi)
print('\nHiring sensitivity:')
print(pd.DataFrame(srows).pivot(index='scenario',columns='metric',values='mean_diff').round(4).to_string())

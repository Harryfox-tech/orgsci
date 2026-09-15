#!/usr/bin/env python3
"""Verify deterministic revision-analysis tables from archived seed-level outputs."""
from pathlib import Path
import itertools, numpy as np, pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'/'revision'; M=ROOT/'results'/'main'
TOL=1e-12
checks=[]

def check(label,a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    diff=np.nanmax(np.abs(a-b)) if len(a) else 0.0
    checks.append((label,float(diff)))
    if diff>TOL: raise AssertionError(f'{label}: max abs diff {diff} > {TOL}')

# S5 direct factorial effects, recomputed from factorial cell metrics.
fac=pd.read_csv(R/'factorial_2x2x2_run_metrics.csv')
fg=[]
for (seed,sc),g in fac.groupby(['seed','scenario']):
    r0=g[g.regime=='R0'].iloc[0]; r1=g[g.regime=='R1'].iloc[0]
    fg.append(dict(seed=seed,scenario=sc,d=r1.evidence_opportunity_gap-r0.evidence_opportunity_gap))
fg=pd.DataFrame(fg); fg[['E','L','C']]=fg.scenario.str.extract(r'E([01])_L([01])_C([01])').astype(int)
per=[]
for seed,g in fg.groupby('seed'):
    def av(E=None,L=None,C=None):
        q=g
        if E is not None:q=q[q.E==E]
        if L is not None:q=q[q.L==L]
        if C is not None:q=q[q.C==C]
        return q.d.mean()
    per.append((seed,av(E=1)-av(E=0),(av(E=1,L=1)-av(E=0,L=1))-(av(E=1,L=0)-av(E=0,L=0)),(av(E=1,C=1)-av(E=0,C=1))-(av(E=1,C=0)-av(E=0,C=0))))
per=pd.DataFrame(per,columns=['seed','E_main_effect','E_x_L_interaction','E_x_C_interaction'])
arch=pd.read_csv(R/'factorial_direct_effects_by_seed.csv').sort_values('seed')
check('factorial_direct_effects',per[['E_main_effect','E_x_L_interaction','E_x_C_interaction']],arch[['E_main_effect','E_x_L_interaction','E_x_C_interaction']])

# S6 Holm family, recomputed from main_contrasts.
mc=pd.read_csv(M/'main_contrasts.csv')
selectors=[('H1 fit','R1-R0','ground_truth_fit'),('H1 placement','R1-R0','placement_rate'),('H1 search','R1-R0','search_rounds'),('H3 alignment','R2-R1','investment_alignment'),('H3 gap','R2-R1','total_gap_reduction'),('H4 gap','R3-R2','total_gap_reduction'),('H4 evidence','R3-R2','evidence_conversion'),('H4 placement','R3-R2','placement_rate')]
rows=[]
for test,c,m in selectors:
    q=mc[(mc.contrast==c)&(mc.metric==m)].iloc[0]
    rows.append(dict(test=test,p_value=q.p_value))
h=pd.DataFrame(rows).sort_values('p_value').reset_index(drop=True); Mx=len(h); adj=[]; cur=0
for i,pv in enumerate(h.p_value,1):
    cur=max(cur,min(1,(Mx-i+1)*pv)); adj.append(cur)
h['holm_adjusted_p']=adj; h=h.sort_values('test')
archh=pd.read_csv(R/'holm_confirmatory_family.csv').sort_values('test')
check('holm_adjusted_p',h.holm_adjusted_p,archh.holm_adjusted_p)

# Round5 direct distribution-free result, recompute from archived seed effects.
x=arch.E_main_effect.to_numpy(float); obs=x.mean()
vals=np.array([np.mean(x*np.array(s)) for s in itertools.product([-1,1],repeat=len(x))])
pex=float(np.mean(np.abs(vals)>=abs(obs)-1e-15))
rob=pd.read_csv(R/'factorial_distribution_free_robustness.csv').iloc[0]
check('sign_flip_estimate',[obs],[rob.estimate]); check('sign_flip_p',[pex],[rob.exact_sign_flip_p])

# Main convergence, recompute estimates and MCSE from main metrics.
main=pd.read_csv(M/'main_run_metrics.csv')
archc=pd.read_csv(R/'main_contrast_convergence.csv')
for _,r in archc.iterrows():
    a,b=r.contrast.split('-'); sub=main[main.seed<1000+int(r.n)].pivot(index='seed',columns='regime',values=r.metric)
    d=(sub[a]-sub[b]).dropna().to_numpy(float); est=d.mean(); mcse=d.std(ddof=1)/np.sqrt(len(d))
    check(f"conv_{r['test']}_{int(r.n)}",[est,mcse],[r.estimate,r.mcse])

# Hiring institution sensitivity contrasts from archived sensitivity runs.
sens=pd.read_csv(R/'hiring_institution_sensitivity_run_metrics.csv'); archs=pd.read_csv(R/'hiring_institution_sensitivity_contrasts.csv')
for _,r in archs.iterrows():
    g=sens[sens.scenario==r.scenario].pivot(index='seed',columns='regime',values=r.metric); d=(g.R1-g.R0).to_numpy(float)
    check(f"hire_{r.scenario}_{r.metric}",[d.mean(),d.std(ddof=1)/np.sqrt(len(d))],[r.mean_diff,r.mcse])
print('revision verification passed; max abs difference =',max(x[1] for x in checks))

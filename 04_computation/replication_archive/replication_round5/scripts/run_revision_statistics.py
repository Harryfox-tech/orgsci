from pathlib import Path
import math,json
import numpy as np,pandas as pd
from scipy import stats
ARCHIVE_ROOT=Path(__file__).resolve().parents[1]
OUT=ARCHIVE_ROOT/'results'/'revision'; MAIN=ARCHIVE_ROOT/'results'/'main'
OUT.mkdir(parents=True,exist_ok=True)
# Holm family excluding H2 manipulation check and RQ5 exploratory
mc=pd.read_csv(MAIN/'main_contrasts.csv')
selectors=[('H1 fit','R1-R0','ground_truth_fit'),('H1 placement','R1-R0','placement_rate'),('H1 search','R1-R0','search_rounds'),('H3 alignment','R2-R1','investment_alignment'),('H3 gap','R2-R1','total_gap_reduction'),('H4 gap','R3-R2','total_gap_reduction'),('H4 evidence','R3-R2','evidence_conversion'),('H4 placement','R3-R2','placement_rate')]
rows=[]
for test,c,m in selectors:
 r=mc[(mc.contrast==c)&(mc.metric==m)].iloc[0].to_dict();r['test']=test;rows.append(r)
h=pd.DataFrame(rows).sort_values('p_value').reset_index(drop=True);M=len(h);adj=[];run=0
for i,pv in enumerate(h.p_value,1):
 val=min(1,(M-i+1)*pv);run=max(run,val);adj.append(run)
h['holm_adjusted_p']=adj;h=h.sort_values('test');h.to_csv(OUT/'holm_confirmatory_family.csv',index=False)
# neutral existing 20-seed precision/convergence
nm=pd.read_csv(MAIN/'additional_neutral_controls_metrics.csv')
# expected conditions R1,R2,R3,R2_random,R3_random 20 seeds
pairs=[('R2-R2_random','R2','R2_random',['investment_alignment','total_gap_reduction','placement_rate','ground_truth_fit']),('R3-R3_random','R3','R3_random',['investment_alignment','total_gap_reduction','evidence_conversion','placement_rate','ground_truth_fit'])]
rows=[]
for label,a,b,metrics in pairs:
 for nseed in [5,10,15,20]:
  sub=nm[nm.seed<1000+nseed]
  for metric in metrics:
   piv=sub[sub.regime.isin([a,b])].pivot(index='seed',columns='regime',values=metric);d=(piv[a]-piv[b]).dropna().to_numpy(float);n=len(d);mean=d.mean();sd=d.std(ddof=1);se=sd/np.sqrt(n);ci=stats.t.interval(.95,n-1,loc=mean,scale=se) if sd>0 else (mean,mean)
   rows.append(dict(contrast=label,metric=metric,n_seed_target=nseed,n=n,mean_diff=mean,ci_low=ci[0],ci_high=ci[1],mcse=se))
pd.DataFrame(rows).to_csv(OUT/'neutral_control_convergence.csv',index=False)
# Structure summary key outcomes
fac=pd.read_csv(OUT/'factorial_2x2x2_contrasts.csv')
key=fac[fac.metric=='evidence_opportunity_gap'][['scenario','evidence_channel','learning_channel','credential_resource_channel','mean_diff','ci_low','ci_high','mcse']]
key.to_csv(OUT/'factorial_opportunity_gap_summary.csv',index=False)

# Direct paired factorial estimands for the resource-linked placement-gap outcome.
facrun=pd.read_csv(OUT/'factorial_2x2x2_run_metrics.csv')
fg=facrun[facrun.regime.isin(['R0','R1'])].pivot_table(index=['seed','scenario'],columns='regime',values='evidence_opportunity_gap').reset_index()
fg['resource_linked_placement_gap_delta']=fg['R1']-fg['R0']
fg[['E','L','C']]=fg['scenario'].str.extract(r'E([01])_L([01])_C([01])').astype(int)
per=[]
for seed,g in fg.groupby('seed'):
 def av(E=None,L=None,C=None):
  q=g
  if E is not None: q=q[q.E==E]
  if L is not None: q=q[q.L==L]
  if C is not None: q=q[q.C==C]
  return q['resource_linked_placement_gap_delta'].mean()
 per.append(dict(seed=seed,
  E_main_effect=av(E=1)-av(E=0),
  E_x_L_interaction=(av(E=1,L=1)-av(E=0,L=1))-(av(E=1,L=0)-av(E=0,L=0)),
  E_x_C_interaction=(av(E=1,C=1)-av(E=0,C=1))-(av(E=1,C=0)-av(E=0,C=0))))
per=pd.DataFrame(per); per.to_csv(OUT/'factorial_direct_effects_by_seed.csv',index=False)
def direct_summary(col,label):
 x=per[col].to_numpy(float); n=len(x); mean=x.mean(); sd=x.std(ddof=1); se=sd/np.sqrt(n); ci=stats.t.interval(.95,n-1,loc=mean,scale=se); tt,pv=stats.ttest_1samp(x,0.)
 return dict(estimand=label,n=n,estimate=mean,ci_low=ci[0],ci_high=ci[1],mcse=se,t_stat=tt,p_value=pv)
pd.DataFrame([
 direct_summary('E_main_effect','Evidence-channel main effect on R1-R0 resource-linked placement-gap delta'),
 direct_summary('E_x_L_interaction','Evidence x learning-channel interaction'),
 direct_summary('E_x_C_interaction','Evidence x credential-resource interaction')
]).to_csv(OUT/'factorial_direct_effects_summary.csv',index=False)

# machine metadata and checks
meta={'revision_date':'2026-08-29','main_seed_range':'1000-1039','factorial_seed_range':'1000-1009','neutral_control_seed_range':'1000-1019','confirmatory_family':[x[0] for x in selectors], 'H2_status':'construct/manipulation check after structural no-discount diagnostic','RQ5_status':'exploratory risk hypothesis'}
(OUT/'revision_run_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
checks={'factorial_cells':int(pd.read_csv(OUT/'factorial_2x2x2_run_metrics.csv').scenario.nunique()),'credential_scenarios':int(pd.read_csv(OUT/'credential_discount_controls_run_metrics.csv').scenario.nunique()),'task_balance_seeds':int(pd.read_csv(OUT/'task_balance_by_seed.csv').seed.nunique()),'holm_tests':len(h)}
(OUT/'revision_integrity_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(h[['test','contrast','metric','mean_diff','ci_low','ci_high','p_value','holm_adjusted_p']].to_string(index=False))

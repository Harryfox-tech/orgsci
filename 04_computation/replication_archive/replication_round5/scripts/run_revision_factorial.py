from __future__ import annotations
import sys, math
from pathlib import Path
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd, numpy as np
from scipy import stats
SCRIPT_DIR=Path(__file__).resolve().parent
sys.path.insert(0,str(SCRIPT_DIR))
import adaplink_abm_experiment_v2 as abm
ARCHIVE_ROOT=Path(__file__).resolve().parents[1]
OUT=ARCHIVE_ROOT/'results'/'revision'; OUT.mkdir(parents=True,exist_ok=True)

def worker(t):
 name,seed,reg,pdct=t
 p=abm.Params(**pdct); m,*_=abm.simulate(seed,reg,p); m['scenario']=name; return m

def paired(sub,a,b,metrics):
 piv=sub.pivot(index='seed',columns='regime',values=metrics); rows=[]
 for m in metrics:
  d=(piv[m][a]-piv[m][b]).dropna().to_numpy(float); n=len(d); mean=d.mean(); sd=d.std(ddof=1); se=sd/np.sqrt(n); ci=stats.t.interval(.95,n-1,loc=mean,scale=se) if sd>0 else (mean,mean)
  rows.append(dict(metric=m,n=n,mean_diff=mean,ci_low=ci[0],ci_high=ci[1],mcse=se))
 return pd.DataFrame(rows)
base=abm.Params(); scenarios=[]
for e in [0,1]:
 for l in [0,1]:
  for c in [0,1]:
   name=f'E{e}_L{l}_C{c}'
   p=replace(base,resource_evidence_coupling=.55 if e else 0.,resource_evidence_update_strength=1. if e else 0.,resource_learning_strength=1. if l else 0.,school_resource_coupling=.55 if c else 0.)
   scenarios.append((name,p,e,l,c))
tasks=[(name,seed,reg,p.__dict__) for name,p,*_ in scenarios for seed in range(1000,1010) for reg in ['R0','R1']]
rows=[]
with ProcessPoolExecutor(max_workers=8) as ex:
 for r in ex.map(worker,tasks,chunksize=2): rows.append(r)
df=pd.DataFrame(rows).sort_values(['scenario','seed','regime']); df.to_csv(OUT/'factorial_2x2x2_run_metrics.csv',index=False)
cons=[]
for name,p,e,l,c in scenarios:
 x=paired(df[df.scenario==name],'R1','R0',['evidence_opportunity_gap','resource_q1_placement','resource_q4_placement','placement_rate','ground_truth_fit','credential_sensitivity','total_gap_reduction'])
 x['scenario']=name;x['evidence_channel']=e;x['learning_channel']=l;x['credential_resource_channel']=c;cons.append(x)
con=pd.concat(cons,ignore_index=True);con.to_csv(OUT/'factorial_2x2x2_contrasts.csv',index=False)
channel={'both_off':'E0_L0_C0','evidence_only':'E1_L0_C0','learning_only':'E0_L1_C0','evidence_plus_learning':'E1_L1_C0','full_baseline':'E1_L1_C1'}
out=[]
for label,sc in channel.items():
 x=con[con.scenario==sc].copy();x['channel_condition']=label;out.append(x)
pd.concat(out,ignore_index=True).to_csv(OUT/'resource_channel_decomposition.csv',index=False)
print(con[con.metric=='evidence_opportunity_gap'][['scenario','mean_diff','ci_low','ci_high']].sort_values('scenario').to_string(index=False))

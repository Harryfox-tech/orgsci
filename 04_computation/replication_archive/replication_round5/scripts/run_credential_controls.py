import sys, math
from pathlib import Path
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
from scipy import stats
SCRIPT_DIR=Path(__file__).resolve().parent
sys.path.insert(0,str(SCRIPT_DIR))
import adaplink_abm_experiment_v2 as abm
ARCHIVE_ROOT=Path(__file__).resolve().parents[1]
OUT=ARCHIVE_ROOT/'results'/'revision'; OUT.mkdir(parents=True,exist_ok=True)

def worker(t):
 name,seed,reg,pdct=t; p=abm.Params(**pdct); m,*_=abm.simulate(seed,reg,p);m['scenario']=name;return m

def paired(sub,metric):
 piv=sub.pivot(index='seed',columns='regime',values=metric);d=(piv['R1']-piv['R0']).dropna().to_numpy(float);n=len(d);mean=d.mean();sd=d.std(ddof=1);se=sd/np.sqrt(n);ci=stats.t.interval(.95,n-1,loc=mean,scale=se);return n,mean,ci[0],ci[1],se
b=abm.Params(); sc={'baseline_discount':b,'no_discount':replace(b,credential_discount_strength=0,major_discount_strength=0),'half_discount':replace(b,credential_discount_strength=1,major_discount_strength=.65),'strong_discount':replace(b,credential_discount_strength=3,major_discount_strength=1.95)}
tasks=[(name,seed,reg,p.__dict__) for name,p in sc.items() for seed in range(1000,1020) for reg in ['R0','R1']]
with ProcessPoolExecutor(max_workers=8) as ex: rows=list(ex.map(worker,tasks,chunksize=2))
df=pd.DataFrame(rows).sort_values(['scenario','seed','regime']);df.to_csv(OUT/'credential_discount_controls_run_metrics.csv',index=False)
out=[]
for name in sc:
 for m in ['credential_sensitivity','placement_rate','ground_truth_fit']:
  n,mean,lo,hi,se=paired(df[df.scenario==name],m);out.append(dict(scenario=name,metric=m,n=n,mean_diff=mean,ci_low=lo,ci_high=hi,mcse=se))
res=pd.DataFrame(out);res.to_csv(OUT/'credential_discount_controls_contrasts.csv',index=False)
print(res[res.metric=='credential_sensitivity'].to_string(index=False))

import sys, pandas as pd, time
SCRIPT_DIR=Path(__file__).resolve().parent
ARCHIVE_ROOT=SCRIPT_DIR.parent
sys.path.insert(0,str(SCRIPT_DIR))
from adaplink_abm_experiment import simulate, Params, REGIMES
from pathlib import Path
import argparse
ap=argparse.ArgumentParser(); ap.add_argument('--start',type=int,required=True); ap.add_argument('--n',type=int,default=10); ap.add_argument('--label',required=True)
a=ap.parse_args(); p=Params(); out=ARCHIVE_ROOT/'results'/'main'; out.mkdir(parents=True,exist_ok=True)
metrics=[]; rounds=[]; learn=[]; hires=[]; t0=time.time()
for seed in range(a.start,a.start+a.n):
  for reg in REGIMES:
    m,r,l,h=simulate(seed,reg,p); metrics.append(m); rounds.append(r)
    if len(l): l=l.copy(); l['seed']=seed; learn.append(l)
    if len(h): h=h.copy(); h['seed']=seed; hires.append(h)
pd.DataFrame(metrics).to_csv(out/f'{a.label}_metrics.csv',index=False)
pd.concat(rounds,ignore_index=True).to_csv(out/f'{a.label}_rounds.csv',index=False)
pd.concat(learn,ignore_index=True).to_csv(out/f'{a.label}_learning.csv',index=False)
pd.concat(hires,ignore_index=True).to_csv(out/f'{a.label}_hires.csv',index=False)
print(a.label, 'elapsed', time.time()-t0, 'metrics', len(metrics))

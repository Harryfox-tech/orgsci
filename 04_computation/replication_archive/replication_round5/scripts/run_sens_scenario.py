import sys, argparse, pandas as pd, time
from dataclasses import replace
SCRIPT_DIR=Path(__file__).resolve().parent
ARCHIVE_ROOT=SCRIPT_DIR.parent
sys.path.insert(0,str(SCRIPT_DIR))
from adaplink_abm_experiment import simulate, Params, REGIMES, paired_contrasts
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('scenario'); ap.add_argument('--start',type=int,default=2000); ap.add_argument('--n',type=int,default=10)
a=ap.parse_args(); base=Params()
mods={
'low_resource_gradient':dict(resource_evidence_coupling=0.30),
'high_resource_gradient':dict(resource_evidence_coupling=0.72),
'low_explanation_uptake':dict(explanation_uptake=0.45),
'high_explanation_uptake':dict(explanation_uptake=0.82),
'low_credential_prior':dict(credential_prior_mean=0.20),
'high_credential_prior':dict(credential_prior_mean=0.48),
}
p=replace(base,**mods[a.scenario]); rows=[]; t=time.time()
for seed in range(a.start,a.start+a.n):
  for reg in REGIMES:
    m,_,_,_=simulate(seed,reg,p); rows.append(m)
df=pd.DataFrame(rows); out=ARCHIVE_ROOT/'results'/'main'; out.mkdir(parents=True,exist_ok=True); df.to_csv(out/f'sens_{a.scenario}_metrics.csv',index=False)
c=paired_contrasts(df); c['scenario']=a.scenario; c.to_csv(out/f'sens_{a.scenario}_contrasts.csv',index=False)
print(a.scenario, 'elapsed',time.time()-t)

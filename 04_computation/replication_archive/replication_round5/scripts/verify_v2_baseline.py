import sys
from concurrent.futures import ProcessPoolExecutor
import pandas as pd, numpy as np
from pathlib import Path
SCRIPT_DIR=Path(__file__).resolve().parent
ARCHIVE_ROOT=SCRIPT_DIR.parent
sys.path.insert(0,str(SCRIPT_DIR))
import adaplink_abm_experiment_v2 as a

def worker(t):
 s,r=t;m,*_=a.simulate(s,r,a.Params());return m
rows=[]
with ProcessPoolExecutor(max_workers=8) as ex:
 rows=list(ex.map(worker,[(s,r) for s in range(1000,1040) for r in a.REGIMES],chunksize=2))
new=pd.DataFrame(rows).sort_values(['seed','regime']).reset_index(drop=True)
old=pd.read_csv(ARCHIVE_ROOT/'results'/'main'/'main_run_metrics.csv').sort_values(['seed','regime']).reset_index(drop=True)
cols=['placement_rate','ground_truth_fit','search_rounds','applications_per_hire','fill_rate','vacancy_duration','credential_sensitivity','investment_alignment','total_gap_reduction','evidence_conversion','evidence_opportunity_gap']
diff=(new[cols]-old[cols]).abs().max().max()
print('max_abs_diff',diff)
assert diff<1e-12

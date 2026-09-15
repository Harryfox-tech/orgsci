#!/usr/bin/env python3
"""Reproduce or verify the manuscript analysis from the archive root.

Examples
--------
python scripts/reproduce_manuscript.py --verify
python scripts/reproduce_manuscript.py --main
python scripts/reproduce_manuscript.py --revision
python scripts/reproduce_manuscript.py --verify-revision
python scripts/reproduce_manuscript.py --all
"""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'scripts'

def run(script):
    print(f'\n>>> {script}')
    subprocess.run([sys.executable, str(S/script)], cwd=ROOT, check=True)

def reproduce_main():
    # Run exactly the 40 paired seeds used in the manuscript, without silently changing n.
    code=(
      "from pathlib import Path; import sys; "
      f"sys.path.insert(0,{str(S)!r}); "
      "import adaplink_abm_experiment_v2 as a; "
      "a.run_experiment(n_seeds=40,p=a.Params(),label='main')"
    )
    subprocess.run([sys.executable,'-c',code],cwd=ROOT,check=True)

def reproduce_revision():
    run('run_revision_factorial.py')
    run('run_credential_controls.py')
    run('run_task_balance.py')
    run('run_revision_statistics.py')
    run('run_round5_diagnostics.py')

ap=argparse.ArgumentParser()
g=ap.add_mutually_exclusive_group(required=True)
g.add_argument('--verify',action='store_true',help='Recompute the 40-seed main run metrics and compare them with the archived table.')
g.add_argument('--verify-revision',action='store_true',help='Recompute deterministic revision summaries from archived seed-level outputs and assert equality.')
g.add_argument('--main',action='store_true',help='Regenerate the exact 40-seed R0-R3 main outputs.')
g.add_argument('--revision',action='store_true',help='Regenerate structural, credential, task-balance, multiplicity, convergence, and direct-factorial diagnostics.')
g.add_argument('--all',action='store_true',help='Regenerate main and revision outputs, then verify the main run metrics.')
a=ap.parse_args()
if a.verify: run('verify_v2_baseline.py')
elif a.verify_revision: run('verify_revision_outputs.py')
elif a.main: reproduce_main()
elif a.revision: reproduce_revision()
elif a.all:
    reproduce_main(); reproduce_revision(); run('verify_v2_baseline.py'); run('verify_revision_outputs.py')

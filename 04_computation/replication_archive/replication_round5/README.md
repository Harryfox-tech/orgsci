# AdapLink / Technology in Society replication archive

This archive reproduces the controlled stochastic ABM and all structural diagnostics reported in the manuscript. No private applicant records are included.

## 1. Environment
- Python 3.13.x
- From the archive root: `python -m pip install -r requirements.txt`
- All paths are relative to this archive; no `/mnt/data` directory is required.

## 2. Recommended reproduction entry point
Use `scripts/reproduce_manuscript.py` rather than executing individual model files blindly.

- Verify the archived 40-seed main results: `python scripts/reproduce_manuscript.py --verify`
- Regenerate the exact 40-seed R0-R3 main experiment: `python scripts/reproduce_manuscript.py --main`
- Regenerate the revision diagnostics: `python scripts/reproduce_manuscript.py --revision`
- Regenerate everything and verify: `python scripts/reproduce_manuscript.py --all`

Main inference unit: paired society seed. Main seeds: 1000-1039. Factorial seeds: 1000-1009. Neutral/task and credential-control seeds: 1000-1019.

`adaplink_abm_experiment_v2.py` now defaults to 40 seeds, matching the manuscript. The legacy result-column name `evidence_opportunity_gap` corresponds to the manuscript's **resource-linked placement gap**, defined as final placement rate in the initial-resource Q4 group minus the corresponding Q1 rate.

## 3. Expected outputs
### Main experiment (`--main`)
Written to `results/main/`:
- `main_run_metrics.csv`: run-level outcomes for 40 seeds × 4 regimes.
- `main_round_metrics.csv`: round-level trajectories.
- `main_learning_events.csv`, `main_hire_events.csv`: event logs.
- `main_summary.csv`, `main_contrasts.csv`: regime summaries and paired sequential contrasts.

### Revision diagnostics (`--revision`)
Written to `results/revision/`:
- `factorial_2x2x2_run_metrics.csv`, `factorial_2x2x2_contrasts.csv`: eight structural cells.
- `factorial_direct_effects_by_seed.csv`, `factorial_direct_effects_summary.csv`: direct evidence-channel main effect and E×L/E×C paired interactions.
- `credential_discount_controls_*.csv`: credential-sensitivity construct controls.
- `task_balance_*.csv`: targeted-versus-random task diagnostics.
- `holm_confirmatory_family.csv`: eight-test Holm family.
- `neutral_control_convergence.csv`: n=5/10/15/20 convergence sequence.
- `revision_run_metadata.json`, `revision_integrity_checks.json`: run metadata and checks.

### Verification (`--verify`)
Recomputes all 40 main paired seeds from the exact model and asserts a maximum absolute difference below `1e-12` against `results/main/main_run_metrics.csv` for the manuscript metrics.

## 4. Structural diagnostics
- `run_revision_factorial.py`: 2×2×2 resource-channel design, 10 paired seeds per cell. E toggles resource→evidence, L resource→learning, C resource→credential correlation.
- `run_credential_controls.py`: no/half/baseline/strong evidence-confidence discount, 20 paired seeds.
- `run_task_balance.py`: targeted-versus-random active-task balance, 20 paired seeds.
- `run_revision_statistics.py`: Holm correction, convergence summaries, and direct paired factorial estimands.

## 5. Interpretation boundary
The public benchmark supplies aggregate design constraints only; every simulated microstate is freshly generated. Structural controls are model-based robustness tests rather than empirical labor-market estimates. The historical proxy TAI experiment is documented in the Supplementary Material and is not part of the confirmatory simulation evidence.

## 6. Integrity and provenance
`SHA256SUMS.txt` records the immutable archive contents. `metadata/` contains the baseline parameters and environment record. Results are analysis-ready CSVs used to populate the manuscript and Supplementary tables.

## 7. Round-5 reviewer diagnostics
The final reviewer-resolved archive adds four low-cost robustness checks without changing the main estimand definitions:
- `hiring_institution_sensitivity_*.csv`: 20 paired seeds under baseline, lower/higher post-shortlist proxy noise (0.05/0.20), and lower/higher hiring thresholds (0.46/0.52). The R1-R0 conditional-fit increase, placement decrease, and aggregate-realized-fit decrease preserve direction in every tested setting.
- `resource_group_placement_levels_*.csv` and `factorial_resource_group_*.csv`: Q1 and Q4 placement levels are reported separately so the resource-linked placement gap can be interpreted as group-specific allocation change rather than a difference alone.
- `factorial_distribution_free_robustness.csv`: exact two-sided sign-flip test and deterministic bootstrap interval for the 10-seed evidence-channel factorial main effect.
- `main_contrast_convergence.csv`: cumulative 10/20/30/40-seed estimates and MCSE for all eight confirmatory contrasts.

Use `python scripts/reproduce_manuscript.py --verify-revision` to recompute deterministic revision summaries from their archived seed-level inputs and assert equality. `--all` now regenerates both the original revision analyses and the round-5 diagnostics, then runs both main and revision verification.

The public archive is released under the MIT License. Build caches are intentionally excluded from the packaged release.

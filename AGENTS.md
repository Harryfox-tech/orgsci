# Orgsci research-agent operating rules

This repository supports a theory-building Organization Science paper on AI-enabled recruitment as a feedback institution. The central loop is evaluation at time t -> candidate adaptation -> skill investment and verifiable evidence -> the future talent pool -> evaluation at time t+1. The current draft is a controlled stochastic agent-based model (ABM), not a machine-learning accuracy benchmark.

## Source of truth

- Read `README.md`, `00_project_management/research_notes.md`, and the relevant archive README before changing project materials.
- Treat `01_manuscript/drafts/v0_initial/` as immutable historical source. Create a new version for substantive revisions.
- Treat the current replication archive, baseline parameter values, paired-seed policy, and already reported numerical results as locked until the user explicitly asks to revise them. Do not improve a result by tuning a parameter or changing random-number call order.
- Keep author claims, source facts, agent analysis, and untested hypotheses distinct. Never invent citations, page locations, model details, or simulation outputs. Mark unavailable full-text evidence as not assessable.
- A simulation mechanism is useful only when it changes a stated organizational-theory assumption and produces a testable, non-obvious implication. Favor a minimal model over adding agents or parameters for their own sake.

## Parallel-work boundaries

- `literature_mapper` owns new notes and reference metadata in `02_literature/`.
- `theory_architect` owns theory-gap and proposition work in `00_project_management/`; it proposes manuscript changes but does not edit the manuscript.
- `model_auditor` is read-first and reports theory-to-code mismatches. It does not refactor the executable archive on its own.
- `experiment_designer` owns new experiment plans and, when explicitly tasked to implement, new scripts/configurations under `04_computation/`; it must not silently change baseline code or locked configs.
- `manuscript_editor` owns new versions under `01_manuscript/`, using verified outputs and approved theory decisions. It does not manufacture results or change simulation code.
- `replication_auditor` owns validation reports and tests. It reports findings before changing model or analysis code owned by another role.

If a task crosses another role's file ownership, write a handoff proposal instead of editing that file. Preserve unrelated user changes. Do not commit, push, publish, submit to a journal, upload manuscript files, or alter sharing/access without a separate user request.

## Required handoff

Every substantive result ends with: (1) the theoretical question or claim, (2) source or code pointers, (3) what was verified versus inferred, (4) files created or changed, (5) remaining uncertainty, and (6) the next decision needed from the user or another role. For computational results, also report config, seed policy, experimental unit, and the command that reproduces them.

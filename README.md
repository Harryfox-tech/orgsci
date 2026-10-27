# Orgsci research repository

This repository supports a research paper on how AI-enabled recruitment reshapes talent allocation over time. The current project uses a controlled stochastic agent-based model (ABM) to study recruitment regimes, feedback, skill investment, verifiable evidence, matching quality, throughput, and resource-linked inequality.

The initial manuscript and its Chinese working translation are retained without content edits. The computational archive contains the executable replication package for the current draft.

## Research direction status

As of 2026-10-27, a two-page research-proposal draft on low-score diagnostic mismatch is prepared following the user's request and adviser feedback. It includes targeted literature checks and a minimal model outline, but is not an approved novelty claim or a final topic decision. The draft has not been sent to the adviser. AI-agent opportunity filtering remains an empirical alternative. The historical manuscript and ABM remain unchanged; they are not evidence that the new mechanism has been established.

See [current research status](00_project_management/CURRENT_STATUS.md), the [research proposal](00_project_management/proposal_2026_10_27/README.md), and the [adviser-feedback review](00_project_management/advisor_guidance_2026_10_26/README.md). Journal choice for the new question remains open.

## Repository map

| Folder | Purpose |
| --- | --- |
| `00_project_management/` | research decisions, task planning, and internal notes |
| `01_manuscript/` | draft manuscripts, translations, and later journal-ready source |
| `02_literature/` | reference-library exports and reading notes |
| `03_data/` | raw and processed data; raw data are ignored by Git by default |
| `04_computation/` | ABM, reproduction archive, future analysis code, and environments |
| `05_outputs/` | publication-ready figures and tables generated from analysis |
| `06_submission/` | journal targeting, cover letters, response letters, and submission packages |

## Current study

**Working topic:** AI recruitment as a feedback institution in the talent market.

The baseline replication archive compares four recruitment regimes (R0--R3) across paired random seeds. It documents how credential-based selection, evidence-aware ranking, explanations, and active tasks change conditional person-job fit, placement, learning, evidence conversion, and the resource-linked placement gap. Structural 2×2×2 controls separate resource-to-evidence, resource-to-learning, and resource-to-credential channels.

## Reproducing the current results

From `04_computation/replication_archive/replication_round5/`:

```powershell
python -m pip install -r requirements.txt
python scripts/reproduce_manuscript.py --verify
python scripts/reproduce_manuscript.py --verify-revision
```

See that archive's README for full regeneration commands and model boundaries.

## Working conventions

- Keep original drafts immutable. Create a dated or versioned copy for substantive revisions.
- Put only shareable, documented data under version control. Record source, access date, license, and processing steps for each dataset.
- Generate figures and tables from scripts/notebooks; do not manually overwrite analytical outputs.
- Do not commit credentials, API keys, participant data, or temporary environments.
- Before a paper milestone, run the replication checks and record the commit hash used to generate the manuscript outputs.

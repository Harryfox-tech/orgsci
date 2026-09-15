# Paper Card 02 Levinthal and Schliesmann 2025

> Source coverage: Substantial official HTML text and metadata
> Extraction confidence: High for theory move and major findings; mixed for complete model inventory
> Locator mode: structure-grounded
> Primary analytical lens: methods
> Secondary analytical lens: None
> Context verification: Targeted external check
> Card completeness: Partial

## 01 基本信息

- Title: *Cautious Exploitation: Learning and Search in Problems of Evaluation and Discovery*
- Authors: Daniel A. Levinthal and Daniel Schliesmann
- Venue: *Organization Science* 36(2), 903-917
- Published online: 2024; issue year: 2025
- DOI: https://doi.org/10.1287/orsc.2023.17538
- Position in our project: closest methodological neighbor because feedback is noisy and actors must both evaluate current alternatives and decide whether to search. [Paper: Metadata; Abstract]

## 02 一句话总结

The paper revises the conventional exploration-exploitation account by separating belief updating from action selection, showing that slow updating combined with an exploitative decision rule can outperform explicit exploration when evaluation feedback is noisy, but not when the task is mainly discovery. [Paper: Abstract; Discussion]

## 03 研究问题

[Paper] How should an organization combine learning from noisy experience with an explicit exploration strategy when it must determine both whether its current alternative is good and whether to search for another? [Paper: Introduction; Discussion]

**Your reading fill-in:** Copy the authors' clearest distinction between an evaluation problem and a discovery problem in your own words: `_____`.

## 04 研究背景与发展路径

[Paper-framed] Prior work often foregrounds either belief revision or exploration-exploitation choice while leaving the other in the background. This paper models their joint operation. [Paper: Discussion]

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause | Evidence |
| --- | --- | --- | --- |
| Noisy evaluation | Good alternatives sometimes produce bad outcomes | Stochastic action-payoff relationship | [Paper: Model; Discussion] |
| Discovery-persistence tension | Search can find alternatives but can also abandon good ones | Explicit exploration is insensitive to accumulated evidence | [Paper: Discussion] |

## 06 核心思想

- Surface method: vary belief-updating speed and exploration/exploitation strategy in a computational search model.
- Core insight: “learning rate” and “exploration rate” are different organizational levers and interact.
- [Analysis] General lesson: feedback design should be evaluated jointly with recipients' update rule and action policy.

## 07 方法概览

[Paper] Baseline analyses use 100 alternatives and 100 periods; performance is cumulative loss relative to the optimal policy. Merit is uncertain and realized feedback is noisy. [Paper: Model; Results]

`action -> noisy outcome -> belief update -> ranked alternatives -> persist or switch`

**Your reading fill-in:** payoff distribution `_____`; belief update equation `_____`; exploration parameter `_____`; number of replications `_____`.

## 08 核心模块拆解

| Module | Function | Why needed | Supporting evidence | Removal/change question |
| --- | --- | --- | --- | --- |
| Belief updating | Aggregates experience | Filters or amplifies noisy feedback | [Paper: Discussion] | What happens under one-shot perfect evaluation? `_____` |
| Decision rule | Maps beliefs to persistence/search | Separates directed switching from random exploration | [Paper: Discussion] | Exact action-selection function `_____` |
| Task context | Tunes evaluation versus discovery difficulty | Establishes boundary condition | [Paper: Boundary-condition discussion] | Exact parameterization `_____` |

## 09 关键公式与符号

Not fully assessable from current extraction. **Your reading fill-in:** belief update `_____`; action choice `_____`; regret/performance `_____`.

## 10 实验设计与证据链

| Experiment | Claim tested | Result | Supported conclusion | Source |
| --- | --- | --- | --- | --- |
| Updating speed × search strategy | Joint effect of learning and choice | Slow updating plus high exploitation performs well under evaluation difficulty | Conditional joint mechanism | [Paper: Results; Discussion] |
| Discovery-dominant task | Boundary of cautious exploitation | Explicit exploration regains value | Result is task-contingent | [Paper: Boundary-condition discussion] |
| Changing payoffs | Responsiveness under environmental change | Preferred updating becomes somewhat faster | Old evidence should depreciate faster | [Paper: Boundary-condition discussion] |

## 11 结论的正确边界

Cautious exploitation is not a universal recommendation for inertia. Its advantage requires noisy, experience-based evaluation; in discovery-dominant settings, conventional exploration remains important. [Paper: Discussion]

## 12 作者明确承认的局限

[Paper] The authors describe the joint representation as stylized. [Paper: Conclusion] **Your reading fill-in:** list any additional explicit limitations from the full paper or supplement: `_____`.

## 13 批判性分析

| [Analysis] Observation | Why it matters | How to test it |
| --- | --- | --- |
| Alternatives appear fixed while beliefs evolve | Our candidates change the quality and observability of alternatives themselves | Endogenize payoff/evidence production after feedback |
| Feedback comes from chosen actions | Recruiting also generates feedback for rejected applicants | Compare feedback only after shortlist versus feedback to all applicants |

## 14 学到的知识

Keep the information-update rule separate from the behavioral response rule. The same feedback can produce different market trajectories under different update speeds and action thresholds. [Analysis]

## 15 与已有知识的连接

[Analysis] Map belief updating to candidates' interpretation of explanations; map action selection to skill-investment choice; map evaluation noise to imperfect AI evidence and employer signals.

## 16 研究想法

**Agent-derived candidate:** Candidate cautious adaptation. Hypothesis: when AI feedback is noisy, slower candidate updating can preserve useful skill diversity and improve long-run matching, whereas rapid updating creates overreaction and homogenized evidence. Delta: alternatives evolve because candidates invest. Validation: feedback-noise × update-rate factorial design with diversity, placement gap, and realized-fit outcomes. Falsifier: update rate has no interaction with noise. Failure modes: the model may encode diversity benefits mechanically; feedback noise may be confounded with signal strength. Innovation status: prior-art search required.


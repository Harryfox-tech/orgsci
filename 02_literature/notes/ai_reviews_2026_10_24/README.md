# 先读这里：AI招聘、人才治理与能力评估反馈综述

截至2026年10月24日，用 academic-search 的检索与核验流程整理了24篇综述性文献：招聘5篇，人才管理／治理9篇，能力评估／发展／反馈8篇，教育反馈元分析2篇。不是24篇都已全文精读；每篇的核验程度写在目录中。

结论先说：没有找到一篇能同时包办这三条线的“最新最全综述”。较好的做法是用“近期全景综述＋评估专业综述＋组织治理理论锚点”组合。不同综述的研究问题和纳入范围不同，255篇、187篇、124篇不能直接当作质量或完整性的排名。

## 最值得先拿到的8篇

以下顺序是针对本项目的阅读建议，不是期刊质量排名。

|顺序|文献与链接|为什么先读|覆盖提醒|
|---|---|---|---|
|1|A01 Stanikzai & Mittal (2026)，[AI virtual assistance in recruitment](https://doi.org/10.1108/SAMAMJ-06-2026-0038)|本次检索找到的很新招聘专门综述；作者报告255篇|10月15日上线，检索到2026年6月1日；目前仅核摘要，需全文|
|2|B01 Dasaklis et al. (2026)，[Large Language Models in human resource management](https://doi.org/10.1016/j.techfore.2026.124800)|补LLM时代的HRM全景；作者报告141项研究|2026年10月卷期；本轮未核实检索截止日，需全文|
|3|B02 Theodorsson & Dosanjh (2026)，[Augmentative or autonomous?](https://doi.org/10.1108/OMJ-09-2025-2716)|把招聘、发展、绩效与留任放到一张人才管理地图上|124篇，覆盖到2025年初；开放正文|
|4|B03 Asemota (2026)，[AI and the reconfiguration of competency management systems](https://doi.org/10.1007/s44163-026-02055-9)|最贴近“能力如何被界定、组合与治理”|187篇；2025年9月执行Scopus检索；开放正文|
|5|C01 Boyce, Hickman & Boyce (2026)，[The Future of Selection Enabled by AI](https://doi.org/10.1093/9780197809013.003.0018)|用人员测评的语言看AI，而不只看预测准确率|手册章节，不是SLR；目前仅核摘要，需全文|
|6|C05 Passmore, Olafsson & Tee (2026；2025 online)，[AI in coaching: a systematic literature review](https://doi.org/10.1108/JWAM-11-2024-0164)|反馈如何接到目标、发展与行为；同时看质量和偏倚评估|作者报16项，检索到2024年3月；跨情境，正文计数需复核|
|7|C06 Sipondo & Terblanche (2026)，[Designing AI coaches](https://doi.org/10.1080/17521882.2026.2640932)|补更新的AI教练设计、反思与反馈文献|17项实证研究；不全是员工能力提升试验|
|8|B06 Bankins et al. (2024；2023 online)，[A multilevel review of AI in organizations](https://doi.org/10.1002/job.2735)|为OrgSci目标补个人—团队—组织层次的理论定位|68篇实证；不是招聘专门综述；开放正文|

如果只读三篇先建地图：A01＋B02＋C05。若A01暂时拿不到全文，用开放的[A02招聘全景综述](https://doi.org/10.1007/s44163-026-01488-6)先起步，再补A01。

## 按问题补读

- 招聘流程与AI技术分类：A02、A04；LLM招聘专门更新：A03。
- 人才治理不只是采用AI，还涉及公平与权力：A05（招聘伦理）、B04（DEI）、B09（算法控制）。
- 想看技术覆盖面：B08 Qin et al. (2025) 的47页人才分析survey；不把技术分类当作组织理论。
- 想区分“当前绩效”与“未来潜力”：C03；评估后如何发展、训练和反馈：C04。
- 想看人员测评的效度与专业标准：C02；其中积极结论应与伦理综述对读，不作普遍有效或合规保证。
- 想补工作情境反馈：C08；但virtual feedback并非都由AI提供。
- D01、D02是教育场景元分析，只作学习机制补充，不直接代表求职者或员工。

## OrgSci定位与证据边界

本次优先兼顾了主题贴合度和组织理论接口，没有把“必须发表于Organization Science”当作筛选条件。本目录没有Organization Science本刊综述；Organization Management Journal不能当作Organization Science。组织理论入口主要是Journal of Organizational Behavior与Academy of Management Annals，HRM总框架另见Human Resource Management Review。

目前能够确认的是这些文献的身份、综述类型，以及部分语料、方法和时间范围；阅读优先级是整理者判断。不能据综述中的“future research”一句话就宣布我们的反馈闭环是理论空白，也不能据某综述没有纳入就宣布无人研究。具体闭环的新颖性仍需对相关原始研究逐篇核查。

## 这次保存了什么

- [24篇完整目录](01_三条主线综述清单.md)：完整题名、作者、期刊、DOI、阅读用途、时间范围、全文状态和限制。
- [检索与核验说明](02_检索范围与证据边界.md)：检索范围、访问失败及不能保证穷尽的原因。
- [结构化文献记录](records_enriched.json)、[BibTeX](references.bib)：方便后续筛选和导入文献管理器；不是最终投稿参考文献排版。
- `search_records/`和`query_log.json`：API原始响应及状态；`source_coverage.json`：人工核验事实与阅读判断。
- `validation.json`与`deduplicated.json`：academic-search规定的格式校验与保守去重结果。

本轮只新增文献目录，不改论文、模型、参数或既有精读，不下载付费全文，不commit或push。

下一步需要的决定：优先补齐A01、B01、C01的全文，还是先读已开放的B02、B03、B06、C05。若要继续判断具体理论空白，需另做原始研究的证据核查。

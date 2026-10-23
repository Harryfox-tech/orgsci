# Academic Search补查结果

2026-10-20。本次按用户要求安装并使用Academic Search，继续处理彭诗清负责的选题一，不扩展到评价者实验。

## 技能与检索记录

技能来源：[ustc-ai4science/academic-search](https://github.com/ustc-ai4science/academic-search)，版本1.4.0，安装时固定提交`b9b692ed1334c858eb42d1f2710ccfcae1a43eb8`。安装目录为`C:/Users/shiqing peng/.codex/skills/academic-search`。该技能提供检索、来源核验和文件检查流程；全文访问仍取决于原始来源。

本次使用经济与社会科学路由，精确查询六个DOI，并通过四组OpenAlex查询发现相关研究。Broad query实际结果保存在`academic_search_followup/discovery.json`，未把所有命中都算作已阅读文献。Crossref核对书目信息；OpenAlex提供跨源记录和开放版本线索；另核验出版方与大学仓储。两篇关键反馈论文也查询了Semantic Scholar的开放全文字段，其空值没有被当作不存在全文的证明。

技能自带校验与去重工具已用于记录检查；当前六条记录无重复标识，校验无错误或缺失来源警告。原始查询、访问时间、字段来源及下载尝试都保留，见同目录JSON。

## 新增的规则依据

### 多技能人才规划已有成熟研究

De Bruecker、Van den Bergh、Beliën与Demeulemeester（2015），*Workforce planning incorporating skills: State of the art*，European Journal of Operational Research，243(1):1–16。[正式DOI](https://doi.org/10.1016/j.ejor.2014.10.038)；[KU Leuven公开稿](https://lirias.kuleuven.be/retrieve/c02fa0fc-2336-4fb8-ba63-83a8de3b874c)。

已下载并读取相关章节，取得的是带KBI_1411封面的40页工作稿，不能称为16页正式排版版。重点是技能分类、技能池改变、学习／遗忘，以及技能作为资格约束还是目标函数组成。定位为该公开稿§3.1、§3.3、§4.1与结论；PDF第14—15页讨论训练及学习／遗忘，第19—21页讨论建模方式。

对本任务的影响：技能向量、培训和岗位配置的结合并非空白；我们需要明确技能是否可替代、哪些要求是硬约束，以及学习曲线的现实依据。综述中的模型传统可以支持选择操作化方案，却不能提供我们的员工采纳率或具体学习率。

### 培训时机和生产容量已经被共同建模

Heuser、Letmathe与Schinner（2022），*Workforce planning in production with flexible or budgeted employee training and volatile demand*，Journal of Business Economics，92:1093–1124。[正式全文](https://doi.org/10.1007/s11573-022-01090-z)；[RWTH仓储](https://publications.rwth-aachen.de/record/843931)；[EconStor记录](https://www.econstor.eu/handle/10419/309949)。

已核验出版方开放HTML，并成功下载EconStor的33页PDF（1页仓储封面加32页正式版），题名、作者与DOI一致。§4.1及§4.1.1、正式pp.1101—1102（PDF第10—11页）表示技能随培训、做中学与遗忘变化，并让培训和生产共享时间容量；研究用混合整数优化比较培训可用时机等条件。这是计算规划研究，600个计算情景不是600名真实员工。

对本任务的影响：仅声称“考虑学习、成本与波动需求”不能构成新意。我们的候选增量需要落在建议如何影响员工自主选择、这些选择如何与组织岗位需求相互作用。该文中的自主学习／自然学习表述不能直接当成员工决定是否采纳建议的行为规则。

另一项需要补充的模型边界是时间：基础模型若把B定义为专门培训窗口，应说明这个窗口如何获得；若培训占用生产时间，则需要共同时间约束。不能在提升技能后仍无成本地保留所有当期生产能力，再解释为净组织收益。

## 原先待补全文的状态

|论文|本次新增证据|目前可支持的阅读范围|
|---|---|---|
|Goodman等2004 Feedback Specificity, Exploration, and Learning|核验DOI及作者ResearchGate公开页的相关原文文本；大学旧PDF链接404|可以核对部分方法与讨论；本地PDF和完整图表仍未核验|
|Clark等2018 Goal Relatedness and Learning|初次只有Crossref、OpenAlex、Semantic Scholar及出版方记录；随后用户补充19页正式PDF|现已核验全文相关章节及4图4表，见`clark_2018/paper-card.md`；这不是检索器下载成功|
|Kluger与DeNisi1996|核验DOI，发现CiteSeer历史记录|历史落地页不等于已取得全文，保留为可选补读|
|Fang等2010正式版|核验DOI与出版记录|仍以已持有的2008工作稿为主要规则证据，正式版待对照|

Goodman作者页：[公开文本入口](https://www.researchgate.net/publication/8635575_Feedback_Specificity_Exploration_and_Learning)。本次能读到四种反馈条件、迁移测试及结论的相关文字，但还没有可逐页核对的本地PDF。因此它的状态比“只有摘要”有所改善，也不能写成完整PDF精读。

## 对研究问题的修订

建议保留本周文档中的三类反馈比较，但将理论问题进一步明确为：组织如何通过发展建议协调分散的技能投资，以及这种协调何时改善岗位覆盖、何时产生重复投资。

必须检验三件事。第一，相同培训资源下，建议是否改变学习方向，而非只是增加投入。第二，岗位结构和必要技能是否让重复投资真的造成机会成本；不能预设集中学习一定有害。第三，员工是否可以拒绝或部分采纳，组织是否依据更新后的技能供给修正建议。

这些仍是本项目的提案。新增文献收窄了新颖性主张，没有证明新的模拟结果或保证该题独特。

## 文件与后续

元数据、去重及验证在`academic_search_followup/`；成功取得的PDF保存在本机`outputs/academic_search_20261020/papers/`，未加入文献笔记的公开源码目录。下载器结果、解析验证与论文身份核对分开记录；失败候选保留失败原因。

两篇PDF均通过下载器的结构与pdfinfo解析检查，并另核对题名及作者；Heuser正式版还核对DOI。De Bruecker文件是对应论文的工作稿，版本差别保留。下载成功2篇；Springer与RWTH先前失败的Heuser入口保留在历史manifest，不与最终成功结果混算为三篇论文。`verified_records.json`是合并实际文件结果后的最终记录；`identity_checks.json`记录页数、哈希、版本和核对范围。

|本机全文|版本与用途|
|---|---|
|[De Bruecker等2015](../../../outputs/academic_search_20261020/papers/2015_Workforce_planning_incorporating_skills_State_of_the_art_ffb59d1052b3.pdf)|40页工作稿；对照技能建模、训练及配置的既有传统|
|[Heuser等2022](../../../outputs/academic_search_20261020/papers/2022_Workforce_planning_in_production_with_flexible_or_budgeted_employee_training_and_238f9c9ff17b.pdf)|33页含封面正式版；核对动态技能与培训—生产时间约束|

本次新增本补查说明与可复用的检索脚本，并将两篇研究补入任务报告。没有修改或运行现有ABM。后续用户已补充Clark等2018全文并完成相关核验，因此不再等待该文；Goodman本地PDF仍有助于最终核对，但其相关公开原文已可读。其他可选材料仍见待补全文清单。

状态沿革：`academic_search_followup/`保留的是本轮联网补查当时的结果，不把用户上传改写成检索器的第三篇成功下载；Clark后续的全文证据及页码在`clark_2018/`和对应source bundle。阅读后明确，“目标影响学习”和“努力配置”均已有直接理论对话；候选增量需进一步落实到技能供给与下一轮建议的内生更新。

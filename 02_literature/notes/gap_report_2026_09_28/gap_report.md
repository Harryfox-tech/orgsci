# 人才评价系统研究空白报告：证据感知招聘、反馈与人才池的内生变化

> **2026-09-28 后续评估说明：** 以下原报告保留，不能将其“空白”表述直接视为已成立的新颖性结论。新增核验发现 Bai 等含理论模型；再申请动态、反馈信息与未来申请池已有直接近邻。请优先结合[修订判断与候选选题](../seven_topic_readings_2026_09_28/08_选题比较与缺口修订.md)及[七篇阅读的证据等级](../seven_topic_readings_2026_09_28/README.md)使用。原 Word 版未同步改写，仍是原报告。

> 生成时间：2026-09-28（北京时间）。依据：草稿 draft.txt（"When AI recruitment shapes talent…"）、团队repo（只读）中的10篇阅读笔记与《前五篇_写作与仿真迁移指南》。研究方向按草稿与repo界定，本报告不另起方向，只在该方向内部定位空白。
> 核验规则：正文和参考文献中的每一条都经过核验。有DOI的条目经Crossref核验；没有Crossref DOI的PMLR和NeurIPS论文，以出版方页面（proceedings.mlr.press、proceedings.neurips.cc）核验。完整记录见 verified_refs.json。"全文"指本次实际读过全文的公开版本（arXiv、NBER或IZA工作论文版），"仅摘要"指只读了Crossref、OpenAlex或出版方页面上的摘要。

## (a) 一页摘要

**方向（不变）。** 人才评价系统不只"挑人"，也在塑造下一轮被评价的人。评价规则经由反馈改变技能投资和证据生产，进而改变人才池与机会分配，其中包括与资源相关的不平等。草稿中的ABM已经用R0–R3四种制度（文本/credential筛选 → 证据感知排序 → 加解释 → 加主动发展任务）和2×2×2资源通道设计展示了三件事：匹配质量与出清之间存在权衡；解释改变投资方向，但6轮内不改善就业；仅证据通道就能扩大资源相关的就业差距（+0.133）。

**最近文献已经覆盖了什么。** 共对照25篇最接近的文献：经济学5篇，CS/公平性8篇，管理学/IS 9篇，社会学/计算社会科学3篇。其中10篇读了全文，1篇为团队已读的全文，14篇只读了摘要。这些文献已分别做到：
1. 评价规则会诱发两类投资，一类是真实改进，一类是博弈（Kleinberg & Raghavan, 2020；Wang et al., 2023）；
2. 群体间调整成本不同，会让评价均衡强化不平等，而补贴的效果可正可负（Hu, Immorlica & Vaughan, 2019；Liu et al., 2020；Hu & Chen, 2018）；
3. 静态公平约束的长期效果可能与直觉相反，差距可以长期存在（Liu et al., 2018；Raab & Liu, 2021）；
4. 可信、可分享的技能信息能改善求职结果，对缺乏经验的人尤其如此（Carranza et al., 2022；Abel et al., 2020）；但证书被大规模供给时会贬值，新手受害最大（Bai et al., 2026）；
5. 筛选工具会改变被面试池并把成本推到录用阶段（Barach, 2026），前置把关会引起候选人退出（Koren, 2026）。

**仍然缺失的部分。** 没有一项研究同时做到以下三点：(i) 把"能力发展"与"证据形成"（让已有能力变得可以被评价者看见，本文称为**可辨识性投资**）当作两种不同的投资；(ii) 让组织本身提供证据生产机会（解释、发展任务）；(iii) 让评价者对证据的信任随证据供给**内生**变化，从而追踪资源分层如何演化。草稿自己的结构检验已经指出这里是关键：取消证据置信折扣后，credential敏感度的下降消失甚至反转。

**推荐空白1（主推）：可辨识性投资与证据贬值。** 当评价系统奖励可验证证据，并且主动帮助候选人生产证据时，证据供给的扩张会不会促使评价者降低证据权重，从而把优势交还给高资源候选人，或者让评价重新依赖credential？这件事在什么边界条件下成立？主要依据：Bai et al. (2026)、Cowgill et al. (2026)、Carranza et al. (2022)、Hu et al. (2019)、Liu et al. (2020)、Kleinberg & Raghavan (2020)，以及团队已读的Sharapov & Dahlander (2025)、Levinthal & Schliesmann (2025)。

**推荐空白2（次推或作为扩展）：反馈的方向价值、参与时滞与选择性退出。** 如果候选人会因被拒而决定继续投资、转换目标或退出，那么解释和发展任务是在维持低资源候选人留在池中，还是加快他们在早期失败后退出（热炉效应）？它的配置价值需要多长的时间尺度才能显现？主要依据：Denrell & March (2001)、Bol et al. (2018)、Koren (2026)、Belot et al. (2019)、Kluger & DeNisi (1996)、Raab & Liu (2021)、Eren (2026)。

**建议。** 以空白1作为本文的理论贡献。它直接延伸了草稿中最稳健的发现（证据通道效应）和最薄弱的一环（折扣规则是外生的），也契合写作指南把"能力发展与证据形成拆开"列为优先事项的安排。空白2可以作为稳健性扩展，或者留作第二篇论文。

**引用核查。** 草稿中21个DOI全部能够解析，只有4处小问题：[10]缺变音符且标题被截断；[20]出版年份应为2025；[6]缺DOI；[20]作者缺变音符。repo中BibTeX的10个DOI全部一致，只有变音符写法不同。详见第(f)节。

## (b) 最近文献对比表

说明：按"与本方向的接近程度"分组排列。"阅读"一栏：全文 = 读了公开全文版本；团队已读 = 在repo的10篇精读笔记中；仅摘要 = 只读了摘要。

| # | 文献 | 领域 | 研究问题 | 理论框架 | 方法 | 主要发现 | 遗留空白（相对本方向） | 阅读 |
|---|---|---|---|---|---|---|---|---|
| 1 | Kleinberg & Raghavan (2020), ACM TEAC | CS/机制设计 | 评价规则怎样引导被评价者把努力投向"真实改进"而不是"博弈" | 委托代理；Goodhart定律；努力分配图 | 形式模型 | 只要某种单调机制能诱发目标努力，简单线性机制就足够 | 只有单一或同质代理人；作者把异质群体和有限理性列为开放问题；没有区分"让已有能力可见"的第三类投资 | 全文（arXiv） |
| 2 | Hu, Immorlica & Vaughan (2019), FAT* | CS/公平性 | 群体调整成本不同时，策略性分类的均衡结果如何 | 策略性操纵；社会分层 | 博弈模型 | 高成本群体被错误排除，低成本群体被错误录取；补贴可能让双方都变差 | 静态均衡；特征只有"操纵"一种含义；没有多轮池演化，也没有组织提供的发展机会 | 全文（arXiv） |
| 3 | Liu, Wilson, Haghtalab et al. (2020), FAT* | CS/公平性 | 个人按群体预期收益理性投资、规则按机构收益更新时，长期均衡如何 | 动态学习；统计歧视 | 均衡分析与数值实验 | 群体异质和不可实现性会导致不利均衡；补贴投资成本对弱势群体更有利 | 投资直接改变资格Y，没有证据层；有选择性标注问题；没有参与或退出 | 全文（arXiv） |
| 4 | Hu & Chen (2018), WWW | CS/劳动市场 | 短期公平干预能否带来长期的群体公平 | 声誉动态；统计歧视（Arrow/Phelps） | 双重劳动市场模型 | 临时劳动市场施加统计平等后，可形成帕累托更优的长期均衡 | 群体层面的声誉；信号就是投资本身，没有能力与证据之分；没有解释或反馈的内容 | 全文（arXiv） |
| 5 | Liu et al. (2018), ICML | CS/公平性 | 静态公平标准的延迟影响 | 单步反馈模型；结果曲线 | 理论与FICO数据 | 常用公平标准通常不促进改善，还可能造成伤害；测量误差会扩大公平标准有利的区域 | 只有单步；没有投资行为，也没有证据生产 | 全文（arXiv） |
| 6 | Raab & Liu (2021), NeurIPS | CS/公平性 | 贝叶斯最优分类器反复再训练时，资格率差距能否长期存在 | 复制子动态；模仿学习 | 动态系统与仿真 | 两组仅初始条件不同，差距也可以无限期存在；提出反馈控制干预 | 组间完全隔离；作者把自愿参与列为未来工作；没有证据层 | 全文（arXiv） |
| 7 | Milli et al. (2019), FAT* | CS/公平性 | 抗策略的分类器给个人带来多大负担 | 社会负担；策略性分类 | 理论与FICO数据 | 机构准确率与社会负担存在内在权衡，且负担集中于弱势群体 | 权衡发生在个体成本层面，不涉及市场出清或匹配容量 | 全文（arXiv） |
| 8 | Ustun et al. (2019), FAT* | CS/可追索性 | 线性分类器能否给被拒者提供可行动的改变路径 | 可追索性（recourse） | 整数规划；信用数据 | 标准建模做法会显著影响是否存在可追索路径 | 静态；不考虑个人照建议行动后对总体和评价者的反馈 | 全文（arXiv） |
| 9 | Carranza et al. (2022), AER | 劳动经济学 | 技能信息不足如何扭曲求职与招聘 | 双边信息摩擦 | 南非6,891名求职者的现场实验 | 可分享的认证提高就业17%、收入34%；私下告知效果较小；只告诉企业会改变面试决策 | 一次性外生信息干预；作者把退出/参与认证、报告精度和市场均衡列为未来问题 | 全文（IZA工作论文版） |
| 10 | Li, Raymond & Bergman (2026), RES | 劳动经济学/算法招聘 | 招聘算法应只做"利用"，还是也做"探索" | 上下文老虎机 | 《财富》500强企业的简历数据 | 探索型算法同时提高面试质量和多样性；监督学习型算法大幅减少少数族裔 | 评价者在学习，但候选人不会因规则而改变；没有投资或证据生产 | 全文（NBER工作论文版） |
| 11 | Abel, Burger & Piraino (2020), AEJ: Applied | 劳动经济学 | 推荐信能否缓解低技能市场中的信息摩擦 | 信号与筛选 | 简历审计与鼓励实验 | 推荐信使回电率提高60%，效果主要来自女性 | 推荐信获取机会的分层与均衡贬值都没有研究 | 仅摘要 |
| 12 | Bohren, Imas & Rosenberg (2019), AER | 经济学/歧视 | 歧视如何随评价历史演变 | 动态歧视；信念偏差 | 平台现场实验 | 没有评价历史时女性受歧视；积累正面评价后方向反转 | 评价历史外生赋予，候选人不投资 | 仅摘要 |
| 13 | Belot, Kircher & Muller (2019), RES | 劳动经济学 | 低成本的定制建议能否改变求职 | 搜索理论 | 实验室里的12周真实求职 | 建议拓宽搜索范围，面试增加，对搜索面窄的人效果更大 | 建议针对搜索方向，不针对技能或证据，也没有分层结果 | 仅摘要 |
| 14 | Barach (2026), Organization Science | 管理/组织 | 候选人筛选器如何重新分配招聘成本 | 搜索与筛选；成本再分配 | 在线劳动市场随机现场实验 | 面试人数减少3.4%，低/高质量申请者分别少28.9%/36.9%；offer被拒率+8.9%，工资+2.5% | 静态的单轮雇主行为；候选人不因筛选规则而投资 | 仅摘要 |
| 15 | Koren (2026), Management Science | 管理/运营 | 增设前置把关如何影响效率和候选人决策 | 筛选理论；自我选择 | 形式模型 | 把关会改变候选人自己的决策；带有历史偏差的把关促使受影响者退出，从而延续偏差 | 退出是二元的，没有技能/证据投资，也没有反馈内容 | 仅摘要 |
| 16 | Wang, Huang, Jasin & Singh (2023), Management Science | IS | 企业是否应公开算法 | 策略性用户；透明度 | 解析模型 | 在一系列条件下公开对企业有利，甚至能提高预测力；用户未必受益 | 用户同质；不涉及资源分层和多轮池效应 | 仅摘要 |
| 17 | Bai et al. (2026), ISR | IS | 免除测试费后，技能认证的价值如何变化 | 信号理论 | 平台政策的准自然实验 | 认证率上升、招聘加快，但信号力下降，新手受害最大；展示更细的认证信息可以缓解 | 只有一次政策冲击；证书与能力的耦合没有被建模；没有组织提供的发展路径 | 仅摘要 |
| 18 | Cowgill, Hernández-Lagos & Wright (2026), Management Science | IS/经济学 | 生成式AI降低信号生产成本后，筛选准确率如何变化 | 成本信号 | 模型加招聘与投资实验 | 筛选准确率下降4%–9%；对非英语国家的申请者反而提高 | 单轮；评价者会不会随后调整权重没有研究 | 仅摘要 |
| 19 | Bauer & Gill (2024), ISR | IS | 向被评者披露算法评分会引起什么行为 | 自我实现预言；锚定 | 五组实验 | 披露错误评分会把行为推向评分所预测的方向 | 实验室单轮；不涉及技能投资和就业配置 | 仅摘要 |
| 20 | Eren (2026), Organization Science | 组织/社会学 | 没有CS学位的求职者如何回应"技能即入场券" | 精英制；需求侧信号 | 访谈、社交媒体与民族志，并有三年追踪 | 对merit门槛的不同解读产生三种进入策略，只有特定群体集中于高就业策略，从而再生产不平等 | 质性研究；没有反事实规则比较 | 仅摘要 |
| 21 | Skowronek & He (2026), Organization Science | 组织 | 算法本身无偏时，导航差异是否仍造成不平等 | 性别化能动性 | 激励仿真数据加66份访谈（NRMP） | 男性更多主动寻求额外建议，因而更成功 | 解释/建议是外生给定的；没有技能或证据投资 | 仅摘要 |
| 22 | Sharapov & Dahlander (2025), Organization Science | 组织 | 选择制度如何同时影响选择错误与投稿池 | 选择制度；选择视角 | 实证 | 选择规则同时改变投稿池和选择视角 | 没有投资或证据层；没有资源分层 | 团队已读 |
| 23 | Bol, de Vaan & van de Rijt (2018), PNAS | 社会学/科学学 | 早期成功如何带来累积优势 | 马太效应 | 断点回归（资助门槛） | 门槛上方者8年内累积的资助多出一倍以上，部分因为未获资助者停止参与竞争 | 评价规则不变；没有反馈内容 | 仅摘要 |
| 24 | Lukac & Grow (2021), J. Computational Social Science | 计算社会科学/ABM | 在线劳动市场的声誉系统如何影响招聘 | 声誉与累积优势 | ABM | 声誉系统会造成与客观能力脱钩的赢者通吃；信息不对称较低时，结果不平等反而可能更高 | 没有解释、发展任务或证据可信度 | 仅摘要（草稿已引用） |
| 25 | Bullinaria (2018), JASSS | 计算社会科学/ABM | 职业晋升中性别不平等如何涌现 | 竞争晋升 | ABM | 提供一个框架，用抽象案例比较能力差异、歧视与职业偏好对晋升分布的影响 | 评价规则固定；没有反馈或投资内生性 | 仅摘要 |

**扩展阅读（已核验、已读摘要，但不在主表中）。**
- 动态公平/仿真：D'Amour et al. (2020)；Mouzannar et al. (2019)；Kannan, Roth & Ziani (2019)；Heidari, Nanda & Gummadi (2019)。
- 策略性分类的基础：Hardt et al. (2016)；Miller, Milli & Hardt (2020)；Perdomo et al. (2020)（草稿[31]）；Karimi et al. (2021)。
- 池与筛选：Abebe, Caria & Ortiz-Ospina (2021)；Fernandez-Mateo & King (2011)；Sarabi & Lehmann (2024)。
- 平台推荐：Kokkodis & Ipeirotis (2023)。
- AI面试透明度：Lakhiwal et al. (2026)。
- AI招聘系统的开发过程：van den Broek, Sergeeva & Huysman (2021)（MIS Quarterly，民族志）。
- 非认知技能认证：Bassi & Nansamba (2022)。
- 反应性：Espeland & Sauder (2007)（草稿[30]）；Chatterji & Toffel (2010)。
- 组织学习：Denrell & March (2001)；Knudsen & Levinthal (2007)；Kluger & DeNisi (1996)；Harrison & Carroll (1991)。

## (c) 精读卡片（12张）

说明：卡片1–9读了公开全文，卡片10–12只读了摘要（已明确标注）。团队已精读的10篇不再重做卡片，它们与新文献的关系见本节末尾的"对团队已读10篇的延伸"。

### 卡片1｜Kleinberg & Raghavan (2020)：How do classifiers induce agents to invest effort strategically?（全文，arXiv v5）
- **研究问题。** 评价者只能观察由真实属性生成的特征。怎样设计评价规则，才能让代理人把努力投向评价者看重的行动（真实改进），而不是只抬高代理特征（博弈）？
- **框架与方法。** 用"努力图"刻画行动如何影响特征、特征如何进入评估，属于委托代理式的机制设计。作者明确援引Goodhart定律，以及"评估同时承担识别与激励两项功能"这一经济学洞见。
- **主要发现。** 只要存在某种单调机制能诱发指定的努力分配，简单的线性机制就足够。
- **局限（作者自述）。** 分析只针对单一代理人或参数相同的群体。异质群体、有限理性代理人、输出受约束（如二元分类）的情形都是开放问题。
- **与本方向的关系。** 这是"评价塑造投资"最直接的理论起点。它缺少她的ABM已有的两样东西：资源异质，以及"可见主张/证据可信度/潜在能力"三层分离。它也没有第三类投资，即不改变能力、只让能力可以被看见的证据生产。

### 卡片2｜Hu, Immorlica & Vaughan (2019)：The disparate effects of strategic manipulation（全文，arXiv v4）
- **研究问题。** 不同群体调整特征的成本不同时，学习者的均衡策略会怎样对待两个群体？
- **框架与方法。** 在策略性操纵模型中引入社会分层，即群体之间成本不同，用博弈均衡分析。
- **主要发现。** 只要一方成本更高，均衡就会错误录取优势群体的部分成员，同时错误排除弱势群体的部分成员。补贴弱势群体的成本可能只提高学习者的效用，却让两个群体都变差，原因是学习者会随之提高标准。作者还指出，操纵若真能提高质量，差异化的获取途径会带来"更成问题的情形"。
- **与本方向的关系。** 这篇和她的"资源相关证据获取"最接近。区别在于：它的特征调整是一维的"操纵"，而且只有单期均衡。"补贴导致评价者提高标准"正是评价者适应机制（M7），而她的ABM目前没有这一机制，折扣规则是固定的。

### 卡片3｜Liu, Wilson, Haghtalab et al. (2020)：The disparate equilibria of algorithmic decision making when individuals invest rationally（全文，arXiv）
- **研究问题。** 个人根据本群体的预期收益决定是否投资，机构则周期性地更新决策规则以最大化自身收益。这样的动态会收敛到什么样的长期均衡？
- **框架与方法。** 动态学习加均衡刻画，辅以数值实验，应用情境包括招聘和入学。
- **主要发现。** 群体异质和不可实现性（realizability不成立）会产生不利于某一群体的均衡。群体分离决策（decoupling）在可实现时最优，否则效果取决于初始条件。补贴投资成本即使在不可实现时也能为弱势群体带来更好的均衡。
- **局限（作者自述）。** 假设机构能无偏地估计真/假阳性率，而实际存在选择性标注问题。假设个人能直接改变资格Y，理性投资以外的情形留给未来工作。
- **与本方向的关系。** 它有"规则更新 ↔ 群体投资"的双向动态，但投资就是资格本身，没有证据层。它与卡片2在"补贴是否有益"上结论相反，而关键差异正是评价者如何回应。这正好说明，"评价者如何对证据供给作出反应"是理论上的枢纽。

### 卡片4｜Hu & Chen (2018)：A short-term intervention for long-term fairness in the labor market（全文，arXiv v2）
- **研究问题。** 在形式上机会平等的背景下，劳动市场的群体差距为何持续存在？短期公平约束能否带来长期公平？
- **框架与方法。** 以Arrow和Phelps的统计歧视理论为基础，构建动态声誉模型。市场分为临时劳动市场（TLM，施加统计平等）和永久劳动市场（PLM，自由择优）。
- **主要发现。** 即使满足个体公平，群体差距也可能纹丝不动。个人声誉对本群体有外部性；在TLM施加的短期干预可以提升弱势群体的集体声誉，并在一定市场条件下形成帕累托占优的均衡。
- **与本方向的关系。** 这是"资源获取差异 → 投资选择 → 群体声誉"的经典动态，而且明确设在劳动市场。但信号就是投资结果本身，没有"证据生产成本"与"能力"的分离，也没有解释或发展任务的内容维度。

### 卡片5｜Liu et al. (2018)：Delayed impact of fair machine learning（全文，arXiv v2）
- **研究问题。** 静态公平标准（人口统计平等、机会平等）能否促进受保护群体的长期福利？
- **框架与方法。** 单步反馈模型，用"结果曲线"刻画各标准的适用区域，并用FICO数据做实验。
- **主要发现。** 常用公平标准一般不能促进改善，在无约束目标本不会造成伤害的地方，它们还可能造成伤害。测量误差（低估弱势群体）会扩大公平标准有利的区域。作者认为需要"仔细的时间建模"。
- **与本方向的关系。** 这是动态公平的奠基之作，给她提供了"评价规则的长期效应与短期直觉可能相反"的论证资源。它只有单步，个人不投资，也不生产证据。

### 卡片6｜Raab & Liu (2021)：Unintended selection: Persistent qualification rate disparities and interventions（全文，arXiv，NeurIPS 2021）
- **研究问题。** 两个群体仅初始资格密度不同，贝叶斯最优分类器反复在全体人口上再训练，资格率差距能否持续？
- **框架与方法。** 个人模仿本群体中成功的策略，用复制子方程描述资格率演化，并用仿真比较各种公平干预与反馈控制。
- **主要发现。** 存在非平凡的均衡，使差距无限期持续。常见的公平干预可能失败，而新的反馈控制机制可以永久消除差距。
- **局限（作者自述）。** 组间完全隔离是最脆弱的假设。作者建议未来研究多个分类器作用于同一人口，以及把自愿参与作为额外策略。
- **与本方向的关系。** 它说明"模型重训练 + 群体学习"就足以让差距持续。但它没有证据层，没有参与和退出，也没有组织提供的发展机会。作者列出的未来方向与空白2（参与）一致。

### 卡片7｜Milli et al. (2019)：The social cost of strategic classification（全文，arXiv）
- **研究问题。** 为抵御策略行为而更保守的分类器，会给"本应通过"的个人带来多大成本？
- **框架与方法。** 定义"社会负担"，即正类个体为获得正确分类所需的期望最小成本，并在结果单调成本下证明其性质，辅以FICO数据。
- **主要发现。** 机构准确率与社会负担之间存在内在权衡，任何准确率提升都伴随负担上升。稳健性提升会扩大子群体之间的差距。
- **与本方向的关系。** 这与她的"匹配质量–吞吐"权衡是形式上的类比：R1提高了条件匹配度，却降低出清并加重搜索摩擦。但Milli等人的负担是个体层面的成本，不是市场容量约束下的出清。她的ABM把这一权衡推进到了市场配置层面。

### 卡片8｜Carranza, Garlick, Orkin & Rankin (2022)：Job search and hiring with limited information about workseekers' skills（全文，IZA DP 14529工作论文版；AER发表版只读了摘要）
- **研究问题。** 关于求职者技能的信息不足，是否同时扭曲了求职者和企业的行为？
- **框架与方法。** 双边信息摩擦。在南非对6,891名低收入青年求职者评估技能，随机分配公开认证（可分享给企业）、私下告知和只告诉企业等处理，另做回电实验。
- **主要发现。** 公开认证使就业提高17%（5个百分点）、收入提高34%，并让信念与搜索策略更贴近真实技能。私下告知对信念和搜索的影响相近，但就业与收入效应较小。只告诉企业会增加回电。认证对没有工作经验、没有大学学历的人效果最大。
- **局限（作者自述）。** 未来问题包括：谁付费、第三方如何建立声誉、信息报告的粗细，以及参与者何时选择参加或退出评估，并需要结合双方信息都有限的筛选与信号模型。
- **与本方向的关系。** 这篇给"证据可信度 + 可分享性"提供了最强的因果证据，也区分了"告诉候选人"与"告诉企业"两条路径，对应她的R2（解释）与R1（证据感知排序）。但这是一次性的外生干预，没有研究证据被大规模供给之后企业是否重新定价。这恰好由Bai et al. (2026)从反面补上，而把两者连起来正是空白1的内容。

### 卡片9｜Li, Raymond & Bergman (2026)：Hiring as exploration（全文，NBER w27736工作论文版；RES发表版只读了摘要）
- **研究问题。** 招聘算法只做"利用"（从有记录的群体中挑人），会不会错过对代表性不足群体的学习？
- **框架与方法。** 上下文老虎机（UCB）。用《财富》500强专业服务公司的申请数据，比较监督学习、在线更新的监督学习和UCB算法。
- **主要发现。** UCB算法提高了被选面试者的质量（最终录用率），同时增加了黑人和西班牙裔的比例。监督学习算法提高质量，却显著减少少数族裔。作者据此认为，人类招聘者其实处在帕累托前沿以内。
- **与本方向的关系。** 这是"评价者学习"最接近的实证，对应M7。但候选人被当作外生，不会因规则而投资或生产证据。在她的ABM中加入探索型评价者，可以检验"探索"是否能抵消证据通道导致的资源分层。

### 卡片10｜Bai, Gao, Goes & Lin (2026)：All that glitters is not gold: The impact of certification test costs in online labor markets（仅摘要）
- **研究问题。** 在线劳动平台免除技能认证的测试费后，认证的价值如何变化？
- **方法。** 平台政策冲击，即准自然实验（依摘要）。
- **主要发现（依摘要）。** 认证率急升、招聘加快，但认证的信号力下降：雇主更少雇用认证者，也更少给他们高薪，因为认证者的平均表现下降了。新手受害最大。展示分数和认证时效等更细的信息可以缓解。
- **与本方向的关系。** 这是"证据供给扩张 → 评价者贬值 → 最依赖证据的人受损"的直接实证，也是空白1的经验锚点。但它只有一次冲击，没有组织提供的发展路径，也没有"证据与能力耦合度"的机制分解。

### 卡片11｜Barach (2026)：Filtering the labor pool: How digitalization redistributes hiring costs（仅摘要）
- **研究问题。** 候选人筛选器是否把招聘成本从搜索筛选阶段转移到了录用阶段？
- **方法。** 在线劳动市场的随机现场实验，用机器学习代理雇主看不见的申请者质量（依摘要）。
- **主要发现（依摘要）。** 使用筛选器的雇主面试人数减少3.4%，低质量申请者减少28.9%，高质量申请者减少36.9%。在主动使用者中，offer被拒率增加8.9%，工资提高2.5%。作者认为，当多家企业追逐同样的易观察信号时，会发生拥挤。
- **与本方向的关系。** 这是"评价规则改变被评价池、并带来出清代价"的最新组织学实证，与她R1的匹配–吞吐权衡相互呼应。但它是单轮的，候选人不会因规则而改变自己，这正是她的ABM能够补上的动态部分。

### 卡片12｜Koren (2026)：The gatekeeper effect: The implications of pre-screening, self-selection, and bias for hiring processes（仅摘要）
- **研究问题。** 增设前置把关如何影响筛选效率与候选人自身的决策？
- **方法。** 形式模型（依摘要）。
- **主要发现（依摘要）。** 把关会改变候选人的决策。面对带有统计偏差的把关，候选人更可能退出申请，从而延续历史偏差。平权措施可以缓解。
- **与本方向的关系。** 这是评价规则引起"参与/退出"这一池内生机制的形式化，对应空白2。但它没有技能或证据投资，也没有反馈内容（解释与粗粒度拒绝之间的差别）。

### 对团队已读10篇的延伸

| 团队已读文献 | 在本方向中的角色 | 新文献如何延伸 |
|---|---|---|
| March (1991) | 利用与探索；适应的短视 | Li et al. (2026) 把"探索"落到招聘评价者身上；空白2中候选人的投资方向也是一种探索与利用的选择 |
| Levinthal & Schliesmann (2025) | 评价问题与发现问题的区分；谨慎利用 | Bai et al. (2026) 和 Cowgill et al. (2026) 显示评价者面对的是信号可信度会漂移的评价问题，这为空白1中评价者的适应规则提供理论依据 |
| Sharapov & Dahlander (2025) | 选择规则同时改变投稿池与选择视角 | Barach (2026) 和 Koren (2026) 在招聘中给出池效应的实证与模型；空白1、2把池效应推进到能力、证据与参与三个维度 |
| Koçak, Levinthal & Puranam (2023) | 搜索与协调的双重挑战；影响结构 | 评价者（雇主）与平台之间对证据权重的协调，可以作为空白1的组织结构扩展 |
| Kane & Alavi (2007)；Fang, Lee & Schilling (2010) | IT与组织学习；子群隔离 | Raab & Liu (2021) 的"组间隔离导致差距持续"与Fang等人的子群隔离机制可以相互印证 |
| Hu & Bettis (2018) | 多目标与共享任务环境中的反馈 | 匹配质量与吞吐是两个目标，Milli et al. (2019) 和 Barach (2026) 提供了跨学科的对应 |
| Brahm & Poblete (2024)；Anderson (1999) | 适应、文化与复杂性 | 作为ABM方法合法性的背景；Harrison & Carroll (1991) 是组织人口与筛选仿真的先例 |
| Kellogg et al. (2020) | 算法控制 | Bauer & Gill (2024) 和 Wang et al. (2023) 说明算法透明本身就是一种"控制/诱导"工具 |

## (d) 覆盖矩阵：机制 × 最接近的文献

符号：● = 核心机制，文献对其作了明确的建模或识别；◐ = 部分涉及、隐含或作为扩展讨论；○ = 未涉及。只读摘要的文献依据摘要判断，可能低估其涉及程度。

**机制定义。**
- **M1 证据感知排序**：区分潜在能力、可见主张与证据可信度，评价依据证据加权。
- **M2 解释诱发投资**：反馈或透明度改变投资方向。
- **M3 主动发展**：组织或平台提供能力或证据的生产机会（任务、补贴、测试）。
- **M4 资源相关的证据获取**：生产证据或调整特征的成本随资源或群体而不同。
- **M5 匹配质量–吞吐权衡**：条件质量与出清、成本或负担之间的权衡。
- **M6 池内生性**：未来被评价池的构成或资格分布随规则变化。
- **M7 评价者适应**：评价者或模型随证据供给与结果更新权重或标准。
- **M8 参与与退出**：申请、坚持或退出由规则或反馈内生决定。

**矩阵A：CS/经济学文献**

| 机制 | Kleinberg & Raghavan 2020 | Hu et al. 2019 | Liu et al. 2020 | Hu & Chen 2018 | Liu et al. 2018 | Raab & Liu 2021 | Milli et al. 2019 | Carranza et al. 2022 | Li et al. 2026 |
|---|---|---|---|---|---|---|---|---|---|
| M1 证据感知排序 | ◐ 特征与真实属性分离 | ◐ 可操纵特征 | ○ | ◐ 含噪投资信号 | ◐ 测量误差 | ○ | ◐ | ● 可分享的可信认证 | ○ |
| M2 解释诱发投资 | ◐ 透明线性规则诱导努力 | ○ | ◐ 按群体预期收益投资 | ○ | ○ | ◐ 模仿成功策略 | ○ | ◐ 告知结果改变信念与搜索 | ○ |
| M3 主动发展 | ○ | ◐ 成本补贴 | ◐ 投资补贴 | ◐ 临时劳动市场入口 | ○ | ○ | ○ | ◐ 免费评估 | ○ |
| M4 资源相关证据获取 | ○（列为未来工作） | ● 群体成本差异 | ● | ● 资源获取差异 | ◐ | ◐ 初始条件差异 | ● 负担不均 | ◐ 对低经验者效果更大 | ○ |
| M5 质量–吞吐权衡 | ○ | ◐ | ◐ | ◐ | ◐ | ○ | ● 准确率与社会负担 | ○ | ● 质量与多样性 |
| M6 池内生性 | ◐ | ○ | ● | ● | ● 单步 | ● | ○ | ○ | ◐ 训练数据 |
| M7 评价者适应 | ○ | ● 补贴后提高标准 | ● 规则更新 | ● 企业信念 | ○ | ● 反复再训练 | ● 抗策略规则 | ◐ 企业改变面试 | ● 探索式学习 |
| M8 参与与退出 | ○ | ○ | ○ | ○ | ○ | ○（列为未来工作） | ○ | ◐ 搜索策略 | ○ |

**矩阵B：管理学/IS/社会学文献，以及她的ABM**

| 机制 | Barach 2026 | Koren 2026 | Wang et al. 2023 | Bai et al. 2026 | Cowgill et al. 2026 | Sharapov & Dahlander 2025（团队已读） | Bol et al. 2018 | 她的ABM（草稿） |
|---|---|---|---|---|---|---|---|---|
| M1 证据感知排序 | ◐ 易观察信号 | ○ | ◐ 因果特征与相关特征 | ● 认证信号 | ● 信号生产成本 | ○ | ○ | ● 三层分离 + 证据置信折扣 |
| M2 解释诱发投资 | ○ | ○ | ● 透明度诱导投资 | ○ | ○ | ○ | ○ | ● R2（有R2-random中性对照） |
| M3 主动发展 | ○ | ○ | ○ | ◐ 免费测试 | ◐ 生成式AI作为生产工具 | ○ | ○ | ● R3（有R3-random中性对照） |
| M4 资源相关证据获取 | ○ | ◐ 历史偏差 | ○ | ● 新手依赖认证 | ◐ 非英语申请者 | ○ | ○ | ● 2×2×2通道开关 |
| M5 质量–吞吐权衡 | ● | ● 效率 | ◐ | ◐ 招聘加快但质量下降 | ◐ 准确率 | ◐ 选择错误 | ○ | ● 条件匹配度与出清 |
| M6 池内生性 | ● 面试池构成 | ● | ○ | ◐ | ○ | ● 投稿池 | ● 累积优势 | ◐ 固定队列内的状态变化，无进入/退出 |
| M7 评价者适应 | ○ | ◐ 把关策略 | ● 透明度选择 | ● 雇主贬值 | ◐ | ◐ 选择视角 | ○ | ○ 折扣规则外生固定 |
| M8 参与与退出 | ○ | ● 退出申请 | ○ | ○ | ○ | ◐ 投稿选择 | ● 停止参与竞争 | ○ 未建模 |

**读图要点。**
1. **覆盖较充分的机制**：M4（成本异质，CS理论中有4篇以上●）、M6（动态公平）、M7（CS中的规则更新，IS中的雇主贬值）和M5（Barach、Milli、Li）。仅就这些单项而言，她的ABM不能宣称新颖。
2. **她的ABM独有的组合**：M1×M2×M3在同一模型中逐级引入，并带中性对照；再加上M4的通道分解。这是现有文献都没有的，也是草稿当前贡献的来源。
3. **真正的空缺是两类交叉**：
   - **M1×M3×M4×M7**：证据被组织性地大规模生产时，评价者会不会重新定价？这对资源分层意味着什么？只有Bai et al. (2026)（单次冲击，实证）和Cowgill et al. (2026)（单轮）部分触及，没有任何动态模型。
   - **M2×M8**：反馈的内容如何影响坚持与退出？只有Koren (2026)和Bol et al. (2018)研究了退出或参与，但都与反馈内容无关。她的ABM恰好在M7和M8上都是○，这两处也就是最自然的扩展点。

## (e) 推荐的研究空白（均在既定方向之内）

### 空白1（主推）：可辨识性投资与证据贬值，即证据感知评价下资源分层的内生演化

**候选研究问题。**
- **RQ1**：组织评价规则奖励可验证证据，并通过解释和发展任务帮助候选人生产证据。在这种情况下，证据供给的扩张怎样改变评价者对证据的信任（证据权重）？这种再定价又怎样决定资源相关的机会差距：是缩小、扩大，还是让评价重新依赖credential？
- **RQ1a**：能力发展与证据形成（可辨识性投资）什么时候互补、什么时候替代？"发展型评价"（R3）的分配效应，是否取决于证据与能力之间的耦合度？

**可写成的命题（示意，"命题 + 机制 + 边界条件"格式）。**
- **P1**：评价者会根据证据的事后表现调整证据权重，而低耦合证据（例如模板化作品、生成式AI辅助产出）的生产成本对高资源者更低。此时，证据供给扩张会先缩小、后扩大资源相关的就业差距，形成U形时间路径。
- **P2**：组织提供的发展任务如果同时生成能力与证据（高耦合），可以抵消证据贬值；如果只生成证据（低耦合），会加速贬值，并让评价者更依赖credential。
- **P3**：展示更细的证据信息（分数、时效、来源）相当于提高证据的可区分度，能够在不减少证据供给的前提下缓解贬值。这是Bai et al. (2026)设计含义的动态版本。

**为什么是空白（对应具体文献）。**
1. **策略性分类只有"改进与博弈"两类投资。** Kleinberg & Raghavan (2020)、Miller, Milli & Hardt (2020) 和 Wang et al. (2023) 把被评价者的调整分为提高真实质量与只抬高代理特征两种，缺少第三类：真实但有成本、只让已有能力可以被看见的投资，即证据生产。Kleinberg & Raghavan (2020) 还把异质群体明确列为开放问题。
2. **成本异质模型对"补贴是否有益"给出相反结论，分歧点就在评价者如何回应。** Hu et al. (2019) 发现补贴可能让学习者提高标准，使双方都变差；Liu et al. (2020) 发现补贴投资成本能改善弱势群体的均衡。两者都只有单一特征或资格，没有能力与证据的分离，所以无法回答"组织帮候选人生产证据"属于哪一种情形。
3. **经济学现场实验证明了证据的价值，但都是一次性的外生干预。** Carranza et al. (2022)、Abel et al. (2020) 和 Bassi & Nansamba (2022) 显示，可信、可分享的技能信息能改善结果，对低经验者和女性尤其明显。Carranza et al. (2022) 自己把参与或退出评估、报告精度和市场层面的均衡列为未来问题。
4. **最新IS实证已经看到"反面"，但没有机制模型。** Bai et al. (2026) 发现免费认证使信号贬值，新手受害最大；Cowgill et al. (2026) 发现生成式AI降低信号成本后，筛选准确率一般下降，但对非英语申请者上升，方向取决于专家与非专家的相对成本。两者都是单次冲击或单轮实验，没有多轮的评价者适应，也没有组织提供的发展路径。
5. **组织理论有框架，没有这一机制。** Sharapov & Dahlander (2025) 指出选择规则同时改变投稿池与选择视角；Levinthal & Schliesmann (2025) 区分评价问题与发现问题；Knudsen & Levinthal (2007) 区分备选的生成与评估。一个既"培养"候选人、又"评价"候选人的组织安排，必然让生成与评估相互耦合，但还没有人把这一点落到"证据的可信度会随组织自身的培养行为而漂移"上。
6. **草稿本身已经暴露了这一枢纽。** credential敏感度的下降在取消证据置信折扣后消失甚至反转，而草稿把它降格为构念检验。把折扣规则从外生参数变成评价者可学习的内生变量，正好把这个弱点转成理论贡献。

**现有ABM已经能支持的部分。**
- 潜在能力、可见主张与证据可信度的三层分离（M1）。
- R0–R3逐级引入，并有R2-random、R3-random中性对照，可以识别"定向"成分（M2、M3）。
- 2×2×2资源通道开关，可以分离证据、学习与credential通道（M4）；Q1/Q4分解可以区分"排除"与"累积优势"。
- 配对种子、Holm校正、ODD文档和可复现包都已具备。

**需要补充的部分。**
1. **评价者适应模块（M7）。** 雇主或平台根据录用后的表现代理，按证据类型更新证据权重，例如加入滞后的贝叶斯更新或信度估计，并与"固定折扣"做2×2对照。
2. **证据–能力耦合参数。** 为每类证据设定耦合度κ（κ=1时证据只能由能力产生；κ<1时可由资源"购买"），并让κ的生产成本随资源分位变化。R3的任务可以设为高耦合与低耦合两种版本。
3. **更长的时间尺度与多队列。** 从6轮延长到20–30轮，每轮有新队列进入，才能观察贬值的时间路径和U形差距。
4. **新的结果指标。** 证据信息量（证据与潜在能力的相关）的时间序列；credential的回归依赖度；Q1/Q4差距的轨迹；证据通道效应随评价者学习速率的变化。
5. **相图或边界条件图。** 在（κ，学习速率，资源–成本梯度）空间上画出差距缩小与扩大的区域，并配一个可解析的简化模型，用来证明至少一个核心命题。

**主要风险与审稿人可能的质疑。**
- **"这不就是信号理论和信号干扰吗？"** 需要写清增量：一是证据机会由组织提供；二是可辨识性成本与资源相关；三是评价者适应。三者同时存在时，才会出现"发展型评价何时缩小、何时扩大差距"的边界条件，而信号模型通常把信号成本当作外生。建议补上与统计歧视和信号文献的正式对话（Hu & Chen, 2018 已提供劳动市场版本）。
- **"ABM参数是任意设定的。"** 用相图替代点估计，用简化解析模型支撑核心命题，并用Bai et al. (2026)（认证贬值、新手受害）和Carranza et al. (2022)（可分享认证的正效应）作为定性校准目标，即"模式导向"的验证。
- **"这是CS公平性的工作，不是组织理论。"** 在Organization Science的定位上，应把评价看作与被评价群体共同演化的组织安排，以Carnegie传统和March (1991)、Levinthal & Schliesmann (2025)、Sharapov & Dahlander (2025)为主要对话对象，把CS文献放在"形式化先例"的位置。
- **与Bai et al. (2026)重叠。** ABM的角色是给出Bai的发现在什么条件下成立、什么条件下反转，而不是重复它。
- **范围膨胀。** 加入M7以后，建议只保留R1与R3两个核心对比，以控制实验单元数量。

### 空白2（次推或作为扩展）：反馈的方向价值、参与时滞与选择性退出

**候选研究问题。**
- **RQ2**：在固定的匹配容量下，解释和发展任务带来的技能与证据增益，需要多长的时间尺度才能转化为配置结果？如果候选人会根据被拒经历决定继续投资、转换目标或退出，那么定向反馈是缓解还是放大早期失败引发的选择性退出（热炉效应）？这种差异是否沿资源分层？

**为什么是空白。**
1. **草稿自己发现了时滞。** R2和R3改变了投资与证据形成，但6轮内没有就业改善。草稿把原因解释为时间跨度，但没有建模时滞期间有谁留在池中。
2. **组织学习理论预测会有选择性退出。** Denrell & March (2001) 的热炉效应指出，从自身经验中学习的行动者会系统性地放弃早期结果不好的选项。放在求职者身上，这意味着证据转化较慢的低资源候选人更可能在早期被拒后停止投资或退出。
3. **参与机制已有实证，但与反馈内容无关。** Bol et al. (2018) 发现，未获资助者停止竞争是马太效应的重要来源；Koren (2026) 发现有偏的把关会引起退出；Abebe et al. (2021) 发现申请成本与能力正相关，会塑造人才池；Fernandez-Mateo & King (2011) 发现第一轮筛选者的预期性分类会造成隔离。这些研究都没有区分粗粒度拒绝与定向解释。
4. **反馈研究显示方向不确定。** Kluger & DeNisi (1996) 发现，三分之一以上的反馈干预会降低绩效；Bauer & Gill (2024) 发现，披露错误评分会产生自我实现；Belot et al. (2019) 发现，定制建议能拓宽搜索，对搜索面窄的人效果更大；Eren (2026) 发现，对merit门槛的不同解读导致进入时机的分层。
5. **CS动态公平没有参与选择。** Liu et al. (2018)、Raab & Liu (2021) 和 D'Amour et al. (2020) 讨论了人口分布的演化，但个人不会退出。Raab & Liu (2021) 明确把自愿参与列为未来工作。

**现有ABM已经能支持的部分。** R1、R2与R2-random的对比，可以在学习强度相同的条件下识别反馈的"方向价值"。模型已有出清、搜索轮数、空缺时长等吞吐指标，以及Q1/Q4分解。

**需要补充的部分。**
- **参与模块。** 采用基于抱负水平的坚持或退出规则（Carnegie式的抱负更新），或连续被拒k次后以一定概率退出。
- **新队列进入与更长的时间跨度。**
- **新的结果指标。** 各资源分位的存活曲线；池构成随时间的变化；R2与R1就业差距的收敛时间；容量敏感性。
- **核心对比。** 粗粒度拒绝、定向解释与随机解释三者之间，在低资源与高资源候选人中退出率的差异。

**主要风险。** 退出规则是新增的行为假设，需要用Bol et al. (2018)、Koren (2026) 和求职文献做定性校准。时滞结果可能对时间跨度和容量设定敏感，需要做敏感性分析。与空白1同时推进会使论文过重，所以建议作为扩展，或者单独成文。

### 两个空白的取舍

| 维度 | 空白1：可辨识性投资与证据贬值 | 空白2：反馈时滞与选择性退出 |
|---|---|---|
| 与草稿最强发现的衔接 | 直接延伸证据通道效应（+0.133），并修补外生折扣规则这一弱点 | 延伸"解释不带来6轮就业改善"的发现 |
| 与写作指南优先级的一致性 | 高："把能力发展与证据形成拆开" | 中："检验机会约束"与"反馈是否有方向价值" |
| 文献空缺的清晰度 | 高：多个领域各覆盖一部分，交叉处没有工作 | 中：参与机制已知，缺的是反馈内容维度 |
| 实现成本 | 中：评价者学习、κ参数、多队列 | 中低：参与规则、多队列 |
| 主要风险 | 被视为信号理论的变体 | 行为假设较多 |

## (f) 参考文献DOI的Crossref核查（只列不匹配或无法解析的条目）

核查范围包括：草稿参考文献中的全部21个DOI（[22]为DataCite DOI，经DataCite与doi.org核验），草稿[31] PMLR论文（无DOI，经proceedings.mlr.press核验），以及repo中 `02_literature/references/theory_decomposition_2026_09_15.bib` 的10个DOI。**没有无法解析的DOI**。其余条目的标题、作者、期刊、年份、卷期页码均与记录一致，这里不再列出。

| 来源 | 条目 | 问题 | Crossref / 出版方记录 | 建议 |
|---|---|---|---|---|
| 草稿 [10] | Kochling & Wehner (2020), Business Research | 作者姓缺变音符；标题被截断 | 作者为 Köchling, A.；完整标题为 "Discriminated by an algorithm: a systematic review of discrimination and fairness by algorithmic decision-making in the context of HR recruitment and HR development"；13, 795–848；DOI 10.1007/s40685-020-00134-w 正确 | 改为 Köchling，并补全标题 |
| 草稿 [20] | Larooij & Tornberg (2026), Artificial Intelligence Review | 年份不一致；作者姓缺变音符 | 在线发表于2025-11-18，issued为2025；59卷，Article 15；作者为 Törnberg, P.；DOI 10.1007/s10462-025-11412-6 正确 | 年份改为2025，并改为 Törnberg |
| 草稿 [6] | Blair, Debroy & Heck (2025), Economics of Education Review | 缺DOI（其余信息一致） | 108, 102704；DOI 10.1016/j.econedurev.2025.102704 | 补上DOI |
| repo BibTeX | Kocak, Ozgecan et al. (2023) | 变音符写法不同（不影响检索） | Crossref作 Koçak, Özgecan | 可改为 Ko{\c{c}}ak, {\"O}zgecan |
| repo BibTeX | Kellogg et al. (2020) 中的 Ang{\`e}le Christin | 变音符与Crossref不同 | Crossref作 Angéle；作者通常写作 Angèle | 保持原样即可（Crossref记录本身可疑） |

说明：草稿[19] Gelling et al. 在线发表于2025-11，印刷版为2026-02，写2026是正确的，所以没有列入问题表。

## 附：检索与核验方法
- **检索。** 用Crossref按期刊ISSN与主题词检索：Org Sci、ASQ、AMJ、AMR、SMJ、MS、ISR、MISQ、ASR、AJS、AER、RES、QJE、AEJ、PNAS、JASSS、JCSS等。对FAccT/FAT*、ICML、NeurIPS的定向文献，用DOI、PMLR或NeurIPS出版方页面核验。另外使用了网络检索，用于定位公开全文。
- **全文来源。** arXiv（8篇CS论文）、NBER w27736（Li, Raymond & Bergman）、IZA DP 14529（Carranza et al.）。Sarabi & Lehmann (2024)、Bauer & Gill (2024)、van den Broek et al. (2021) 等的仓储PDF被机器人验证页拦截，只读了摘要。
- **未收录的原因。** Coate & Loury (1993, AER) 没有Crossref DOI，也未用出版方页面核验，因此不收录。另有两个DOI对应的并不是预期论文：10.1287/mnsc.1120.1678 实为Han & Yang，10.1287/mnsc.2017.2870 实为Exley & Terry，均已排除。

## 参考文献（仅收录已核验条目）

- Abebe, G., Caria, A. S., & Ortiz-Ospina, E. (2021). The Selection of Talent: Experimental and Structural Evidence from Ethiopia. *American Economic Review*, *111*(6), 1757–1806. https://doi.org/10.1257/aer.20190586
- Abel, M., Burger, R., & Piraino, P. (2020). The Value of Reference Letters: Experimental Evidence from South Africa. *American Economic Journal: Applied Economics*, *12*(3), 40–71. https://doi.org/10.1257/app.20180666
- Anderson, P. (1999). Perspective: Complexity Theory and Organization Science. *Organization Science*, *10*(3), 216–232. https://doi.org/10.1287/orsc.10.3.216
- Bai, J., Gao, Q., Goes, P., & Lin, M. (2026). All That Glitters Is Not Gold: The Impact of Certification Test Costs in Online Labor Markets. *Information Systems Research*, *37*(1), 236–258. https://doi.org/10.1287/isre.2023.0303
- Barach, M. (2026). Filtering the labor pool: How digitalization redistributes hiring costs. *Organization Science*. Advance online publication. https://doi.org/10.1287/orsc.2024.19407
- Bassi, V., & Nansamba, A. (2022). Screening and Signalling Non-Cognitive Skills: Experimental Evidence from Uganda. *The Economic Journal*, *132*(642), 471–511. https://doi.org/10.1093/ej/ueab071
- Bauer, K., & Gill, A. (2024). Mirror, Mirror on the Wall: Algorithmic Assessments, Transparency, and Self-Fulfilling Prophecies. *Information Systems Research*, *35*(1), 226–248. https://doi.org/10.1287/isre.2023.1217
- Belot, M., Kircher, P., & Muller, P. (2019). Providing Advice to Jobseekers at Low Cost: An Experimental Study on Online Advice. *Review of Economic Studies*, *86*(4), 1411–1447. https://doi.org/10.1093/restud/rdy059
- Bohren, J. A., Imas, A., & Rosenberg, M. (2019). The Dynamics of Discrimination: Theory and Evidence. *American Economic Review*, *109*(10), 3395–3436. https://doi.org/10.1257/aer.20171829
- Bol, T., de Vaan, M., & van de Rijt, A. (2018). The Matthew effect in science funding. *Proceedings of the National Academy of Sciences*, *115*(19), 4887–4890. https://doi.org/10.1073/pnas.1719557115
- Brahm, F., & Poblete, J. (2024). Organizational Culture, Adaptation, and Performance. *Organization Science*, *35*(5), 1823–1848. https://doi.org/10.1287/orsc.2022.16791
- Bullinaria, J. (2018). Agent-Based Models of Gender Inequalities in Career Progression. *Journal of Artificial Societies and Social Simulation*, *21*(3), Article 7. https://doi.org/10.18564/jasss.3738
- Carranza, E., Garlick, R., Orkin, K., & Rankin, N. (2022). Job Search and Hiring with Limited Information about Workseekers’ Skills. *American Economic Review*, *112*(11), 3547–3583. https://doi.org/10.1257/aer.20200961
- Chatterji, A. K., & Toffel, M. W. (2010). How firms respond to being rated. *Strategic Management Journal*, *31*(9), 917–945. https://doi.org/10.1002/smj.840
- Cowgill, B., Hernández-Lagos, P., & Wright, N. L. (2026). Does AI Cheapen Talk? Theory and Evidence from Global Entrepreneurship and Hiring. *Management Science*. Advance online publication. https://doi.org/10.1287/mnsc.2024.07027
- D'Amour, A., Srinivasan, H., Atwood, J., Baljekar, P., Sculley, D., & Halpern, Y. (2020). Fairness is not static: deeper understanding of long term fairness via simulation studies. In *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency* (pp. 525–534). https://doi.org/10.1145/3351095.3372878
- Denrell, J., & March, J. G. (2001). Adaptation as Information Restriction: The Hot Stove Effect. *Organization Science*, *12*(5), 523–538. https://doi.org/10.1287/orsc.12.5.523.10092
- Eren, D. (2026). When Interpretations of Merit Thresholds Vary and Reproduce Inequality: Entering the Tech Industry Without Computer Science Credentials. *Organization Science*, *37*(2), 490–515. https://doi.org/10.1287/orsc.2023.17752
- Espeland, W. N., & Sauder, M. (2007). Rankings and Reactivity: How Public Measures Recreate Social Worlds. *American Journal of Sociology*, *113*(1), 1–40. https://doi.org/10.1086/517897
- Fang, C., Lee, J., & Schilling, M. A. (2010). Balancing Exploration and Exploitation Through Structural Design: The Isolation of Subgroups and Organizational Learning. *Organization Science*, *21*(3), 625–642. https://doi.org/10.1287/orsc.1090.0468
- Fernandez-Mateo, I., & King, Z. (2011). Anticipatory Sorting and Gender Segregation in Temporary Employment. *Management Science*, *57*(6), 989–1008. https://doi.org/10.1287/mnsc.1110.1333
- Hardt, M., Megiddo, N., Papadimitriou, C., & Wootters, M. (2016). Strategic Classification. In *Proceedings of the 2016 ACM Conference on Innovations in Theoretical Computer Science* (pp. 111–122). https://doi.org/10.1145/2840728.2840730
- Harrison, J. R., & Carroll, G. R. (1991). Keeping the Faith: A Model of Cultural Transmission in Formal Organizations. *Administrative Science Quarterly*, *36*(4), 552. https://doi.org/10.2307/2393274
- Heidari, H., Nanda, V., & Gummadi, K. (2019). On the long-term impact of algorithmic decision policies: Effort unfairness and feature segregation through social learning. In *Proceedings of the 36th International Conference on Machine Learning* (PMLR 97, pp. 2692–2701). https://proceedings.mlr.press/v97/heidari19a.html
- Hu, L., & Chen, Y. (2018). A Short-term Intervention for Long-term Fairness in the Labor Market. In *Proceedings of the 2018 World Wide Web Conference on World Wide Web - WWW '18* (pp. 1389–1398). https://doi.org/10.1145/3178876.3186044
- Hu, L., Immorlica, N., & Vaughan, J. W. (2019). The Disparate Effects of Strategic Manipulation. In *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 259–268). https://doi.org/10.1145/3287560.3287597
- Hu, S., & Bettis, R. A. (2018). Multiple Organization Goals with Feedback from Shared Technological Task Environments. *Organization Science*, *29*(5), 873–889. https://doi.org/10.1287/orsc.2018.1207
- Kane, G. C., & Alavi, M. (2007). Information Technology and Organizational Learning: An Investigation of Exploration and Exploitation Processes. *Organization Science*, *18*(5), 796–812. https://doi.org/10.1287/orsc.1070.0286
- Kannan, S., Roth, A., & Ziani, J. (2019). Downstream Effects of Affirmative Action. In *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 240–248). https://doi.org/10.1145/3287560.3287578
- Karimi, A.-H., Schölkopf, B., & Valera, I. (2021). Algorithmic Recourse: from Counterfactual Explanations to Interventions. In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency* (pp. 353–362). https://doi.org/10.1145/3442188.3445899
- Kellogg, K. C., Valentine, M. A., & Christin, A. (2020). Algorithms at Work: The New Contested Terrain of Control. *Academy of Management Annals*, *14*(1), 366–410. https://doi.org/10.5465/annals.2018.0174
- Kleinberg, J., & Raghavan, M. (2020). How Do Classifiers Induce Agents to Invest Effort Strategically? *ACM Transactions on Economics and Computation*, *8*(4), 1–23. https://doi.org/10.1145/3417742
- Kluger, A. N., & DeNisi, A. (1996). The effects of feedback interventions on performance: A historical review, a meta-analysis, and a preliminary feedback intervention theory. *Psychological Bulletin*, *119*(2), 254–284. https://doi.org/10.1037/0033-2909.119.2.254
- Knudsen, T., & Levinthal, D. A. (2007). Two Faces of Search: Alternative Generation and Alternative Evaluation. *Organization Science*, *18*(1), 39–54. https://doi.org/10.1287/orsc.1060.0216
- Koçak, Ö., Levinthal, D. A., & Puranam, P. (2023). The Dual Challenge of Search and Coordination for Organizational Adaptation: How Structures of Influence Matter. *Organization Science*, *34*(2), 851–869. https://doi.org/10.1287/orsc.2022.1601
- Kokkodis, M., & Ipeirotis, P. G. (2023). The Good, the Bad, and the Unhirable: Recommending Job Applicants in Online Labor Markets. *Management Science*, *69*(11), 6969–6987. https://doi.org/10.1287/mnsc.2023.4690
- Koren, M. (2026). The Gatekeeper Effect: The Implications of Pre-Screening, Self-Selection, and Bias for Hiring Processes. *Management Science*, *72*(1), 426–441. https://doi.org/10.1287/mnsc.2021.03918
- Lakhiwal, A., Liu, C.-W., Bala, H., & Suen, H.-Y. (2026). From Opacity to Transparency: User Behavior and Downstream Effects in Algorithmic Evaluation. *Information Systems Research*. Advance online publication. https://doi.org/10.1287/isre.2023.0579
- Levinthal, D. A., & Schliesmann, D. (2025). Cautious Exploitation: Learning and Search in Problems of Evaluation and Discovery. *Organization Science*, *36*(2), 903–917. https://doi.org/10.1287/orsc.2023.17538
- Li, D., Raymond, L., & Bergman, P. (2026). Hiring as Exploration. *Review of Economic Studies*, *93*(2), 1200–1240. https://doi.org/10.1093/restud/rdaf040
- Liu, L. T., Dean, S., Rolf, E., Simchowitz, M., & Hardt, M. (2018). Delayed impact of fair machine learning. In *Proceedings of the 35th International Conference on Machine Learning* (PMLR 80, pp. 3150–3158). https://proceedings.mlr.press/v80/liu18c.html
- Liu, L. T., Wilson, A., Haghtalab, N., Kalai, A. T., Borgs, C., & Chayes, J. (2020). The disparate equilibria of algorithmic decision making when individuals invest rationally. In *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency* (pp. 381–391). https://doi.org/10.1145/3351095.3372861
- Lukac, M., & Grow, A. (2021). Reputation systems and recruitment in online labor markets: insights from an agent-based model. *Journal of Computational Social Science*, *4*(1), 207–229. https://doi.org/10.1007/s42001-020-00072-x
- March, J. G. (1991). Exploration and Exploitation in Organizational Learning. *Organization Science*, *2*(1), 71–87. https://doi.org/10.1287/orsc.2.1.71
- Miller, J., Milli, S., & Hardt, M. (2020). Strategic classification is causal modeling in disguise. In *Proceedings of the 37th International Conference on Machine Learning* (PMLR 119, pp. 6917–6926). https://proceedings.mlr.press/v119/miller20b.html
- Milli, S., Miller, J., Dragan, A. D., & Hardt, M. (2019). The Social Cost of Strategic Classification. In *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 230–239). https://doi.org/10.1145/3287560.3287576
- Mouzannar, H., Ohannessian, M. I., & Srebro, N. (2019). From Fair Decision Making To Social Equality. In *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 359–368). https://doi.org/10.1145/3287560.3287599
- Perdomo, J., Zrnic, T., Mendler-Dünner, C., & Hardt, M. (2020). Performative prediction. In *Proceedings of the 37th International Conference on Machine Learning* (PMLR 119, pp. 7599–7609). https://proceedings.mlr.press/v119/perdomo20a.html
- Raab, R., & Liu, Y. (2021). Unintended selection: Persistent qualification rate disparities and interventions. In *Advances in Neural Information Processing Systems 34 (NeurIPS 2021)*. https://proceedings.neurips.cc/paper_files/paper/2021/hash/db00f1b7fdf48fd26b5fb5f309e9afaf-Abstract.html
- Sarabi, A., & Lehmann, N. (2024). Who Shortlists? Evidence on Gender Disparities in Hiring Outcomes. *Administrative Science Quarterly*, *69*(4), 1044–1084. https://doi.org/10.1177/00018392241283946
- Sharapov, D., & Dahlander, L. (2025). Selection Regimes and Selection Errors. *Organization Science*, *36*(6), 2324–2348. https://doi.org/10.1287/orsc.2023.17482
- Skowronek, S. E., & He, J. C. (2026). Gendered Navigation of Advice and Suboptimal Behavior in Matching Algorithms: Evidence from the Residency Match. *Organization Science*, *37*(3), 1165–1192. https://doi.org/10.1287/orsc.2024.19652
- Ustun, B., Spangher, A., & Liu, Y. (2019). Actionable Recourse in Linear Classification. In *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 10–19). https://doi.org/10.1145/3287560.3287566
- van den Broek, E., Sergeeva, A., & Huysman, M. (2021). When the Machine Meets the Expert: An Ethnography of Developing AI for Hiring. *MIS Quarterly*, *45*(3), 1557–1580. https://doi.org/10.25300/MISQ/2021/16559
- Wang, Q., Huang, Y., Jasin, S., & Singh, P. V. (2023). Algorithmic Transparency with Strategic Users. *Management Science*, *69*(4), 2297–2317. https://doi.org/10.1287/mnsc.2022.4475


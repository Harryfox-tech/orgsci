# 前置数据示例

本目录提供O*NET® 30.0数据库三个职业的35项技能评分，共105条职业—技能记录。它验证职业画像能够实际取得并整理，不是本组织的真实岗位数据，也不是员工微观能力数据。

输出文件：`onet30_three_roles_skills.csv`；来源与完整性记录：`source_metadata.json`。转换脚本：`../tools/build_pack.py`。原始文件保存在本机临时阅读目录，不重复纳入仓库。

## 来源与使用

- 官方固定版本原始文件：https://www.onetcenter.org/dl_files/database/db_30_0_text/Skills.txt
- 字段定义：https://www.onetcenter.org/dictionary/30.0/text/skills.html
- 量表定义：https://www.onetcenter.org/dictionary/30.0/text/scales_reference.html
- 来源：U.S. Department of Labor, Employment and Training Administration，O*NET 30.0 Database。
- 许可：CC BY 4.0，https://creativecommons.org/licenses/by/4.0/ 。官方说明允许旧版本按此许可使用：https://www.onetcenter.org/license_db.html 。O*NET®为USDOL/ETA商标。

本项目修改：筛选三个职业，按职业与技能合并IM/LV两行，保留质量标记，并新增归一化代理。USDOL/ETA未批准、背书或测试这些修改。

## 三个职业

13-1071.00 Human Resources Specialists；15-1252.00 Software Developers；15-2031.00 Operations Research Analysts。三者只是数据可用性示例，不代表本组织实际岗位组合；不由此设定名额占比。

实际核验发现：本次固定版本Skills文件没有15-2051.00 Data Scientists的评分行。因此示例选用具有评分的15-2031.00，不把相邻职业的分数冒充数据科学家的分数。职业代码存在于分类中，不代表在每个评分文件都已有观测。

## 字段与转换

`importance_raw`：官方IM评分，1到5；`level_raw`：官方LV评分，0到7。二者均为职业画像，不是个人测试分数。

`importance_rescaled`：把IM按(值−1)/4映射到0到1；`level_proxy_0_1`：把LV除以7，仅作为岗位技能目标画像的可选代理。线性转换不是测量尺度等值的证明，不能据此把员工能力自动放进同一尺度。

`weight_within_role`：在同一职业内，将可用的非负importance_rescaled归一化，使其和为1。该权重是本项目构造，官方没有推荐用它作为录用评分。

`eligible_for_proxy`：IM/LV不存在建议抑制标记且技能未标为Not Relevant。不可用记录保留原值，派生level代理留空，权重为0；不将缺失当作低技能。

其他字段保留原技能代码、名称、样本量、标准误、更新日期和来源。数据中没有岗位数量、资格阈值、员工初始能力、采纳率、学习成本或学习率。

## 实际建模还需准备

建议输入分别为`employees`、`role_requirements`、`vacancies_by_round`、`learning_options`及`feedback_config`。每个字段标明公共数据、合成假设或真实观测。具体定义见技术说明；首版可用合成情境，但不得称作已经估计的真实组织。

## 复现

在仓库根目录使用工作区所提供的Python运行：

```powershell
& 'C:\Users\shiqing peng\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '02_literature/notes/peng_weekly_task_2026_10_20/tools/build_pack.py' --raw 'C:\Users\shiqing peng\AppData\Local\Temp\orgsci_peng_task_20261020\onet30_Skills.txt'
```

若临时文件已清理，先从上述官方固定版本链接重新下载，并核对source_metadata中的SHA-256。此命令转换公开数据并生成报告，不运行ABM。

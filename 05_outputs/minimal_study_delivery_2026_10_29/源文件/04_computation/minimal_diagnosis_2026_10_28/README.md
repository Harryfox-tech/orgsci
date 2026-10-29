# 低分诊断的独立最小研究 v1

日期：2026-10-28。授权依据：用户“顺着做方案一的最小研究”。这是一次适应、一次后续选拔的有限状态决策模型，先解析再作确定性枚举，不是新市场 ABM。未改旧稿、旧配置、随机数政策或旧结果。

## 复现

仅需 Python 标准库；从仓库根运行：

```powershell
python -X utf8 04_computation/minimal_diagnosis_2026_10_28/run_study.py
```

单独验证：

```powershell
python -m unittest discover -s 04_computation/minimal_diagnosis_2026_10_28 -p test_model.py -v
```

本机实际执行使用 bundled Python，不要求用户更改 Python 环境。所有结果写入本目录 `results/`。

## 设计边界

- 参数来自本次内部机制检查的显式选择，未经现实数据校准；这不是预注册研究。配置先写出，再运行数值检查，不据结果修改旧基线。
- 起点是“可信证明不足的初筛低分者”，其中既有能力不足者（能力与证明同时缺少），也有已有能力者；不声称涵盖所有低分成因。
- 候选人根据先验与私下诊断作贝叶斯选择，允许学习、验证、不行动。没有把真实能力提供给选择函数，也没有强制执行建议。
- 学习可以使能力达标，并包含结业测评；独立验证原则上不培养技能，二者的测评标准相同且有误差。结业测评不自动通过。
- 基准中培训的结业测评不占独立验证名额，这是关键制度假设；`shared_verification_bottleneck` 检查两者共用瓶颈的情况。
- `unequal` 与 `equal_same_slots` 仅匹配事前可用验证名额总量，不匹配实际参与、私人支出或完整机构预算。其他两个机会情形只作机制消融。
- 诊断免费、可忽略、不传给雇主；精度为对称二元信号的质量，形成 Blackwell 信息序。无诊断由质量 0.5 表示；质量 1 仅为理想边界。
- 学习与测试均在最终选拔前完成。没有岗位容量竞争、机构重训、多轮均衡、新生代或现实因果估计。
- 核心输出是初始低分人群中的概率质量；不把网格单元当独立受试者，不计算 p 值或置信区间。所谓“精确枚举”仍使用浮点运算，误差容差见 `checks.json`。

## 文件

- `config.json`：固定的内部比较、参数网格、交叉效果及异质成本情形。
- `model.py`：信息、选择与概率分支，独立于历史 ABM。
- `test_model.py`：全策略穷举最优性、解析恒等式、概率守恒、信息价值及不行动边界。
- `run_study.py`：统一运行、网格检查、文件哈希与数值摘要。
- `results/base_cases.csv`：各情形、各组及总体的精确期望。
- `results/base_branches.csv`：基准分支明细，可追踪信念、行动、技能和录用。
- `results/boundary_cases.csv`、`heterogeneous_costs.csv`、`parameter_grid.csv`：边界与完整网格，保留不支持主机制的情形。
- `results/checks.json`、`test_output.txt`、`run_manifest.json`：验证结果、配置哈希、代码哈希、命令环境与单位。
- `results/protected_files_sha256.json`：旧稿及旧复制包运行前后哈希。

理论解释与下一步决策见 [同日研究包](../../00_project_management/minimal_diagnosis_2026_10_28/README.md)。不能把可复现结果或检查通过当作理论原创性成立。

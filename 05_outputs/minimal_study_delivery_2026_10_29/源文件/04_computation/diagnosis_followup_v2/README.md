# 方案一v2：自我信息与非二元产出审查

本目录依据用户“继续推进”请求新增，保留v1与历史复制包。它审查两项假定，不是替换原模型或扩大为市场ABM。

## 复现

只用Python标准库，需保留相邻的v1目录。从仓库根运行：

```powershell
python -X utf8 04_computation/diagnosis_followup_v2/run_audit.py
```

源码：`bridge_model.py`；配置：`config.json`；独立检查：`test_bridge.py`；入口：`run_audit.py`。v1的模型文件通过唯一模块名只读导入，并核对既有哈希。嵌套检查调用v1函数比较期望值，但没有运行v1批处理入口或覆盖其源码/输出。

## 新增什么

1. 私人自我信息h，质量r；候选人结合h和AI信号z更新。二者给定真实技能条件独立，雇主都不看。
2. 潜在产出：未达标/达标基准1/2，已达标者参加培训仍可提高b。
3. 对新增产出的私人价值μ。招聘规则仍只看达标，不形成内生工资或完整福利模型。

类型和产出结果仍有限，不能称连续技能分布；产出为未校准的说明单位。b=0、r=.5时，μ×产出差可还原v1的skill_value项。

## 结果与单位

- `results/all_cases.csv`：320个参数组合×四种可及安排×两组及总体=3,840行。
- `results/diagnostic_contrasts.csv`：固定r、b、μ及可及安排，相对q=.5的诊断增量。
- `results/illustrative_branches.csv`：示例信念、行动、成长和录用分支。
- `results/checks.json`、`test_output.txt`、`manifest.json`：10项检验、信息价值与解析式核验、版本和哈希。

单位为每名初始低分者的期望概率质量；新增潜在产出与新增达标比例分开。不抽样，不使用随机种子、p值、置信区间或MC标准误。v1与历史稿件/复制包合计79个受保护文件运行前后不变。

候选人效用与潜在产出不可直接相减成“社会福利”。同名额只保持事前可及性总量，不配平所有实际支出。计算通过不代表理论创新性成立。

[研究结果与贡献判断](../../00_project_management/diagnosis_followup_v2/03_推进结果与选题决策.md)；[验证草案](../../00_project_management/diagnosis_followup_v2/04_机制验证草案与继续门槛.md)。本轮不修改稿件、招募参与者、预注册或推送。

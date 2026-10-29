"""Render participant pages from authored JSON. Do not distribute the researcher answer key."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    ("重复ID", "如无则填无；多个以逗号分隔"),
    ("重复处理方式", "说明保留或删除哪些记录"),
    ("纳入ID", "全部符合目标状态的ID，即使其数值尚不完整"),
    ("排除ID", "不符合目标状态的ID"),
    ("不完整的纳入ID", "目标范围内不能完整计算的记录"),
    ("缺失处理", "说明如何处理空白和相应不确定性"),
    ("已知小计", "可确定部分的数额"),
    ("完整总额是否可确定", "能或不能，并简述原因"),
]


def main():
    data = json.loads((ROOT / "task_data.json").read_text(encoding="utf-8"))
    out = ROOT / "stimuli"
    out.mkdir(exist_ok=True)
    for task in data["tasks"]:
        if task["id"] == "D":
            continue
        lines = [
            "# 材料" + task["id"] + "：" + task["title"], "",
            "内部试做版M1。数据全部虚构。研究者应只在相应阶段提供这一页，不能同时提供答案或其他任务。", "",
            "## 任务", "",
            "请检查以下记录，回答下方八项。可以使用熟悉的表格工具或纸笔。", "",
            f"本任务只纳入状态为 `{task['target_status']}` 的记录。相同ID且所有字段相同的重复行代表同一笔记录；其他状态不计入。空白是未知信息，不代表零。只依据给出的信息作答，并区分已知部分与完整总额。", "",
            "数额以虚构计量单位表示。请不要从外部寻找这些记录。", "",
            "| ID | 状态 | 数量 | 单位数值 |",
            "|---|---|---:|---:|",
        ]
        lines += ["| " + " | ".join(row) + " |" for row in task["rows"]]
        lines += ["", "## 回答", ""]
        lines += [f"{i}. **{name}**：______（{hint}）" for i,(name,hint) in enumerate(FIELDS, 1)]
        lines += ["", "请按自己的判断完成。资料卡的认可情况与本次作答分分别记录；研究者将在流程说明中告知本阶段的用途。", ""]
        (out / ("participant_" + task["id"] + ".md")).write_text("\n".join(lines), encoding="utf-8")
    d = next(t for t in data["tasks"] if t["id"] == "D")
    lines = [
        "# 学习材料D：先核对记录，再说明总额", "",
        "内部试做版M1；仅学习路径使用。以下是教学示例，不含A/B/C的答案。", "",
        "## 一套可检查的步骤", "",
        "1. 先读纳入范围。不能因为某行有数字就把它算入。", 
        "2. 检查重复。完全相同的同一笔记录只保留一次；内容冲突则先查证，不能悄悄任选一条。",
        "3. 检查空白。空白表示信息缺失，不是默认零。",
        "4. 对范围内且信息完整的记录计算数量×单位数值。",
        "5. 将可计算部分称为已知小计；范围内尚有缺失时，明确完整总额仍不能确定。", "",
        "## 示例", "", "只纳入paid状态。", "",
        "| ID | 状态 | 数量 | 单位数值 |", "|---|---|---:|---:|",
    ]
    lines += ["| " + " | ".join(row) + " |" for row in d["rows"]]
    lines += ["", "D402重复，只计一次；D404不符合目标状态；D403数量未知。",
              "因此已知小计为2×60+1×40=160。160不是完整总额，因为D403仍可能贡献未知数值。",
              "", "## 自查", "", 
              "如果D403的数量后来明确为0，已知小计仍是160，但现在可以确定完整总额。数值碰巧相同，不代表信息完整度相同。",
              "如果出现同一ID、不同数量的两行，当前规则不足以决定取哪行，应说明需要查证。",
              "", "学习完后将参加与直接验证路径相同的B测评。学习材料本身不更新认可记录。", ""]
    (out / "learning_D.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"participant_task_pages": 3, "learning_pages": 1, "participant_data": False}))


if __name__ == "__main__":
    main()


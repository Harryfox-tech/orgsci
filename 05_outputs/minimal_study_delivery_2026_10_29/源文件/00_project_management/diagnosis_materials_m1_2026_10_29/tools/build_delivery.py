"""Collect the minimal-study documents without changing their source bytes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote, unquote
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
OUT = ROOT / "05_outputs/minimal_study_delivery_2026_10_29"
ARCHIVE = ROOT / "05_outputs/最小研究_历轮文档与材料_20261029.zip"
PREFIXES = [
    "00_project_management/proposal_2026_10_27",
    "00_project_management/minimal_diagnosis_2026_10_28",
    "00_project_management/diagnosis_followup_v2",
    "00_project_management/diagnosis_institution_check_2026_10_29",
    "00_project_management/diagnosis_materials_m1_2026_10_29",
    "04_computation/minimal_diagnosis_2026_10_28",
    "04_computation/diagnosis_followup_v2",
]
EXTRA = [
    "00_project_management/CURRENT_STATUS.md",
    "02_literature/notes/seven_topic_readings_2026_09_28/06_Carranza_双边信息与可信证据.md",
]
SUFFIXES = {".md", ".json", ".py", ".bib", ".txt", ".csv", ".docx"}
LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def excluded(path):
    parts = {part.lower() for part in path.parts}
    return bool(parts & {"local_cache", "__pycache__", "node_modules", ".git",
                         "rendered", "renders", "render_cache", "docx_render"})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    original = OUT / "源文件"
    selected = set()
    for prefix in PREFIXES:
        for p in (ROOT / prefix).rglob("*"):
            if (p.is_file() and not p.is_symlink() and not excluded(p)
                    and (p.suffix.lower() in SUFFIXES or p.name == ".gitignore")):
                selected.add(p.resolve())
    selected.update((ROOT / path).resolve() for path in EXTRA)
    assert all(p.is_relative_to(ROOT) for p in selected)
    copied, manifest = {}, []
    for source in sorted(selected):
        relative = source.relative_to(ROOT)
        target = original / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert digest(source) == digest(target)
        copied[source] = target
        manifest.append({"source": relative.as_posix(),
                         "copy": target.relative_to(OUT).as_posix(),
                         "sha256": digest(source), "bytes": source.stat().st_size})
    omitted = []

    def rewrite(source, text):
        def replace(match):
            label, target_text = match.groups()
            target_text = target_text.strip("<>")
            if "://" in target_text:
                return match.group(0)
            local, _, fragment = target_text.partition("#")
            target = (source.parent / unquote(local)).resolve() if local else source
            if target in {OUT / "00_先读我.md", OUT / "01_最小研究_完整原文合订本.md"}:
                dest = target
            elif target in copied:
                dest = copied[target]
            elif target.is_dir() and any(p.is_relative_to(target) for p in copied):
                dest = original / target.relative_to(ROOT)
            else:
                ref = target.relative_to(ROOT).as_posix() if target.is_relative_to(ROOT) else str(target)
                omitted.append({"source": source.relative_to(ROOT).as_posix(), "reference": ref})
                return label + "（仓库背景文件：" + "`" + ref + "`，未收入本包）"
            link = quote(dest.relative_to(OUT).as_posix(), safe="/")
            if fragment:
                link += "#" + fragment
            return "[" + label + "](" + link + ")"
        return LINK.sub(replace, text)

    def headings(text):
        inside = False
        result = []
        for line in text.splitlines():
            if line.lstrip().startswith(("```", "~~~")):
                inside = not inside
            if not inside:
                found = re.match(r"^(#{1,6}) (.*)", line)
                if found:
                    line = "#" * min(6, len(found[1]) + 2) + " " + found[2]
            result.append(line)
        return "\n".join(result)

    ordered = []
    for prefix in PREFIXES:
        paths = [p for p in selected if p.suffix == ".md" and p.is_relative_to(ROOT / prefix)]
        paths.sort(key=lambda p: (p.name != "README.md", p.relative_to(ROOT / prefix).as_posix()))
        ordered.extend(paths)
    ordered += [ROOT / path for path in EXTRA if path.endswith(".md")]
    assert len(ordered) == len(set(ordered))
    chunks = [
        "# 最小研究：历轮文档完整合订本", "",
        "2026-10-29。本文件完整收入本地保存的研究文档正文，不是逐字导出的聊天记录。"
        "为合订阅读仅调整标题层级与本地链接；逐文件原样副本及SHA-256在源文件与manifest中。", "",
        "**先读00_先读我。历史结论不因合订而重新获批；数学判断以v2审查为准，现实依据以制度核查为准，当前材料边界以M1为准。**", "",
        "## 目录", "",
    ]
    for i, source in enumerate(ordered, 1):
        loc = quote(copied[source].relative_to(OUT).as_posix(), safe="/")
        chunks.append(f"{i}. [{source.name}]({loc}) — {source.parent.name}")
    for i, source in enumerate(ordered, 1):
        text = source.read_text(encoding="utf-8-sig")
        chunks += ["", "---", "", f"## 文档{i}：{source.name}",
                   "", "原路径：`" + source.relative_to(ROOT).as_posix() + "`。",
                   "该文档的历史日期、条件和限制保留。", "",
                   headings(rewrite(source, text)), ""]
    reader = OUT / "01_最小研究_完整原文合订本.md"
    reader.write_text("\n".join(chunks), encoding="utf-8")

    def page(path):
        return quote(("源文件/" + path), safe="/")

    intro = f"""# 最小研究交付：先看哪里

2026-10-29。本包包含{len(ordered)}份Markdown文档全文、原样源文件和计算附件；既有内容没有被新摘要覆盖。它覆盖10月27日背景计划、v1最小模型、Acemoglu—Pischke全文对照、v2审查、制度核查及本轮M1材料。

## 如果只读三份

1. [本轮材料与继续门槛]({page('00_project_management/diagnosis_materials_m1_2026_10_29/05_本轮核验与继续门槛.md')})：现在已经做了什么，为什么还不能开正式实验。
2. [v2结果与选题决策]({page('00_project_management/diagnosis_followup_v2/03_推进结果与选题决策.md')})：原结果为什么还不足以构成新理论贡献。
3. [当前工作问题]({page('00_project_management/diagnosis_institution_check_2026_10_29/02_研究问题与选题决策.md')})：现在保留哪条机制，暂缓哪条。

要完整看原文，直接打开[完整合订本](01_最小研究_完整原文合订本.md)。

## 这几轮到底推进了什么

| 轮次 | 实际产物 | 应保留的判断 |
|---|---|---|
| 10月27日背景计划 | 两页proposal与理论准备 | 历史初稿，没有因本包生成而重新定题或发给导师 |
| v1最小研究 | 有限状态模型、条件公式、4,455格计算与检查 | 有条件的净收益/新增达标分离，不是现实因果估计 |
| 关键全文核对 | Acemoglu—Pischke全文精读及页码台账 | 认证改变培训、能力与努力替代不是可直接宣称的新缺口 |
| v2审查 | 主结果投资化简、私人信息与产出边界、320组合 | 行为方向可变或消失；模型跑通不证明独立贡献 |
| 制度与近邻核查 | 自主学习/验证流程和4篇排重 | 有现实路径，但强制成因分流尚无本轮直接依据 |
| 本轮M1 | 三套任务、教学示例、反馈、评分、测量；22项固定检查 | 材料可审阅，尚未验证难度、诊断效度或真实行为 |

## 本轮建议

暂把问题收紧为：低分反馈如何改变继续学习与证明已有能力的选择？当前任务只操作化私人作答反馈和研究内认可，不声称已经准确诊断真实低分成因。

下一关是团队内部试做和难度校准。无需先有AdaptLink或企业数据；但不能把独立任务实验直接写成真实招聘或人才池均衡证据。

## 文件怎么用

- `源文件/`保留原仓库层级，复制文件与源文件哈希相同。
- 历轮文件可能引用没有收入的更早仓库背景；合订本已将这些指针标为背景，见`omitted_context_links.json`。原样副本不改链接。
- 两套计算包的代码、配置、CSV和检查记录放在原层级，方便追溯。**完整复现仍需完整Git仓库**，因为入口会检查历史文件；本包不是删去历史档案后的独立复制包。
- 用户提供的论文PDF、全文提取缓存、页面图片、运行环境和私人附件没有打包。已有的两页proposal Word是历史文档，不是当前定稿。
- 本包给研究者阅读，包含答案与处理设计，**不能整包发给参与者**。
- 本轮没有新增文献检索、真实受试者数据、随机试验、预注册或ABM扫描；未commit或push。

## 六项交接

1. 问题：反馈是否重排学习/证明选择，表现变化与证据更新能否分开。
2. 依据：各轮原文及原路径、文献出处、模型配置与检查记录均收入或明确标注背景。
3. 核实：数学/程序条件、公开流程说明与材料内部一致性；未核实：原创性、量表效度、真实行为与招聘外推。
4. 文件：本交付包及M1新增材料，原始历轮文件保留。
5. 不确定性：原主结果有普通投资形式；当前反馈仍不是已验证的潜在成因诊断。
6. 下一决定：内部试做后决定修材料、收窄问题或停止这一操作化，不以新增参数维持选题。

材料检查命令：在完整仓库根运行`python -X utf8 00_project_management/diagnosis_materials_m1_2026_10_29/tools/check_materials.py`。单位是固定材料，不是参与者；没有种子或统计显著性。
"""
    first = OUT / "00_先读我.md"
    first.write_text(intro, encoding="utf-8")
    uniq = sorted({(x["source"], x["reference"]) for x in omitted})
    omitted_path = OUT / "omitted_context_links.json"
    omitted_path.write_text(json.dumps([{"source": a, "reference": b} for a,b in uniq],
                                      ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps({"generated_at_utc": datetime.now(timezone.utc).isoformat(),
                                        "source_files": manifest, "markdown_documents": len(ordered),
                                        "copy_policy": "Byte-identical selected source snapshots; caches/full-text PDFs excluded.",
                                        "reader_sha256": digest(reader)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bad_links = []
    for doc in [reader, first]:
        for _, target in LINK.findall(doc.read_text(encoding="utf-8")):
            if "://" not in target and not target.startswith("#"):
                if not (OUT / unquote(target.split("#")[0])).exists():
                    bad_links.append({"document": doc.name, "target": target})
    protected = json.loads((ROOT / "00_project_management/diagnosis_institution_check_2026_10_29/protected_files_before.json").read_text(encoding="utf-8"))
    changed = [path for path, h in protected.items() if digest(ROOT / path) != h]
    assert not bad_links and not changed
    qa_path = OUT / "delivery_checks.json"
    qa_path.write_text(json.dumps({"source_file_count": len(manifest), "markdown_documents": len(ordered),
                                  "all_copies_match_source_hashes": True,
                                  "protected_files_count": len(protected), "changed_protected_files": changed,
                                  "broken_reader_links": bad_links, "omitted_background_pointers": len(uniq),
                                  "original_notes_preserved": True, "participant_count": 0,
                                  "new_model_runs": 0}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    planned = list(copied.values()) + [first, reader, omitted_path, manifest_path, qa_path]
    assert len(planned) == len(set(planned))
    assert not any(p.suffix.lower() in {".pdf", ".png", ".pyc", ".zip"} or excluded(p) for p in planned)
    with ZipFile(ARCHIVE, "w", ZIP_DEFLATED, compresslevel=6) as archive:
        for p in sorted(planned):
            archive.write(p, arcname="最小研究_20261029/" + p.relative_to(OUT).as_posix())
    with ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(planned)
    receipt = {"archive": ARCHIVE.relative_to(ROOT).as_posix(), "bytes": ARCHIVE.stat().st_size,
               "sha256": digest(ARCHIVE), "zip_crc_check": "passed", "archived_files": len(planned),
               "markdown_documents": len(ordered), "source_files_match": True,
               "protected_files_unchanged": True}
    (OUT / "archive_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()


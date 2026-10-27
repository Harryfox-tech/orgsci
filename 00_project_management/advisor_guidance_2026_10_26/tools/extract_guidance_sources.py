"""Archive supplied DOCX sources unchanged and expose text/review structure.

No manuscript, model, or original attachment is edited. The screenshot is
hashed but not copied because its signature contains contact information.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = Path(
    "C:/Users/shiqing peng/.codex/codex-remote-attachments/"
    "01a0a394-57f8-76f1-bf40-8a7b0652d4af/"
    "5B971FDF-4A53-4D5E-A075-3EE8F7CA9476"
)
SOURCES = [
    ("1-AI人才评估与招聘研究_候选选题及文献空白讨论整理稿.docx", "01_发导师的候选选题整理稿.docx"),
    ("2-261026-AI人才评估与招聘__-研究-选题指导意见-王哲.docx", "02_王哲导师选题指导意见.docx"),
]
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def texts(root):
    return ["".join(node.text or "" for node in paragraph.findall(".//w:t", NS))
            for paragraph in root.findall(".//w:p", NS)]


def main():
    output = ROOT / "sources"
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"checked_at": datetime.now(timezone.utc).isoformat(), "documents": []}
    for name, archived_name in SOURCES:
        source = ATTACHMENTS / name
        destination = output / archived_name
        if destination.exists():
            if digest(source) != digest(destination):
                raise RuntimeError("Archive exists with different content: " + str(destination))
        else:
            shutil.copy2(source, destination)
        with zipfile.ZipFile(source) as archive:
            main_xml = ET.fromstring(archive.read("word/document.xml"))
            review_parts = [part for part in archive.namelist()
                            if part.startswith("word/comments") and part.endswith(".xml")]
            auxiliary = {}
            for part in ["word/footnotes.xml", "word/endnotes.xml"]:
                if part in archive.namelist():
                    auxiliary[part] = [text for text in texts(ET.fromstring(archive.read(part))) if text.strip()]
            paragraphs = texts(main_xml)
            structural = {
                "paragraphs_including_tables": len(paragraphs),
                "tables": len(main_xml.findall(".//w:tbl", NS)),
                "tracked_insertions": len(main_xml.findall(".//w:ins", NS)),
                "tracked_deletions": len(main_xml.findall(".//w:del", NS)),
                "comment_parts": review_parts,
                "nonempty_auxiliary_text": auxiliary,
            }
            source_record = {
                "original_path": str(source), "archived_path": str(destination.relative_to(ROOT)),
                "sha256": digest(source), "archive_sha256": digest(destination),
                "structure": structural,
            }
            if source_record["sha256"] != source_record["archive_sha256"]:
                raise RuntimeError("Copy verification failed")
            manifest["documents"].append(source_record)
            lines = ["# " + archived_name.removesuffix(".docx"), "",
                     "段落编号为本次 XML 提取定位，不是 Word 页码。表格单元格中的段落按文档顺序列出。", ""]
            lines.extend("[P" + str(index) + "] " + text for index, text in enumerate(paragraphs, 1))
            (output / (destination.stem + "_正文提取.md")).write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    screenshot = ATTACHMENTS / "3-照片-3.jpg"
    manifest["email_screenshot"] = {
        "original_path": str(screenshot), "sha256": digest(screenshot),
        "copied": False, "reason": "Keep original attachment; do not propagate signature contact details.",
    }
    (output / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"documents": len(manifest["documents"]),
                      "copies_verified": all(x["sha256"] == x["archive_sha256"] for x in manifest["documents"]),
                      "structures": [x["structure"] for x in manifest["documents"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Inspect the explicitly supplied PDF; keep full text/page renders local-only."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    path = args.pdf.resolve(strict=True)
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise ValueError("Not a PDF file")
    reader = PdfReader(path)
    cache = HERE / "local_cache"
    cache.mkdir(exist_ok=True)
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n\n".join(f"--- PDF page {i+1}; printed page {917+i} ---\n{body}"
                       for i, body in enumerate(pages))
    (cache / "full_text.txt").write_text(text, encoding="utf-8")
    first = pages[0].lower()
    identity = ("acemoglu" in first and "pischke" in first
                and "917" in first and "training outcomes" in first)
    if not identity or len(pages) != 11:
        raise ValueError("Paper identity / page count requires manual review")
    manifest = {
        "checked_date": "2026-10-28", "source_type": "explicit_user_supplied_pdf",
        "source_path": str(path), "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data), "pdf_pages": len(pages), "printed_pages": "917-927",
        "doi": "10.1016/S0014-2921(99)00049-5", "identity_checks_passed": identity,
        "scope": "Explicit PDF takes precedence over the earlier multi-article ZIP",
        "full_pdf_copied_to_repository": False,
        "extraction": "pypdf; legacy font encodings corrupt some formula glyphs; verify PNGs",
        "local_cache_gitignored": True,
    }
    if args.render:
        binary = shutil.which("pdftoppm")
        fallback = (Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies"
                    / "native/poppler/Library/bin/pdftoppm.exe")
        if binary is None and fallback.exists():
            binary = str(fallback)
        if binary is None:
            raise RuntimeError("Poppler pdftoppm not found")
        target = cache / "pages"
        target.mkdir(exist_ok=True)
        subprocess.run([binary, "-r", "130", "-png", str(path), str(target / "page")], check=True)
        manifest["rendered_pages"] = len(list(target.glob("page-*.png")))
        manifest["renderer"] = "Poppler pdftoppm, 130 dpi"
    (HERE / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()

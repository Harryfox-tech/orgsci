"""Merge checked primary-page observations with the API audit; no model runs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manual = json.loads((ROOT / "manual_sources.json").read_text(encoding="utf-8"))
observations = manual["records"]
records = json.loads((ROOT / "records.json").read_text(encoding="utf-8"))
checked = manual["checked_at"]
for item in observations:
    record = dict(item)
    platform = "arxiv" if item.get("arxiv_id") else ("acl_anthology" if item.get("doi") else "author_website")
    evidence = dict(platform=platform, source_url=item["source_url"], checked_at=checked,
                    evidence_type="page_text", note="Primary source checked with web tool; local Python arXiv TLS failures remain in query_log.json.")
    record.update(source_platforms=[platform], fetched_at=checked[:10],
                  abstract=None, citation_count=None, download_status="not_requested",
                  publication_type=item.get("publication_type", "preprint"),
                  venue=item.get("venue", "arXiv" if item.get("arxiv_id") else None),
                  missing_fields={"citation_count":"Not queried.", "abstract":"No verbatim abstract exported."})
    record["field_sources"] = {key: [evidence] for key in [
        "title", "authors", "year", "publication_type", "venue", "doi", "arxiv_id"] if record.get(key) is not None}
    records.append(record)

# Preserve the relationship, not a fictitious second independent replication.
for record in records:
    if record.get("doi") == "10.1609/aies.v8i3.36755" or record.get("arxiv_id", "").startswith("2509.00462"):
        record["study_family"] = "xu_li_jiang_self_preference"
        record["version_relation"] = "AIES two-page entry and later full arXiv paper; statistics differ across versions."
(ROOT / "combined_records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

bib = []
for index, record in enumerate(records, 1):
    publication_type = record.get("publication_type")
    kind = "misc" if publication_type in ["preprint", "working-paper"] else (
        "inproceedings" if publication_type in ["conference", "proceedings-article"] else "article")
    fields = dict(title=record["title"], author=" and ".join(record["authors"]), year=record["year"],
                  url=record.get("source_url"), doi=record.get("doi"), eprint=record.get("arxiv_id"))
    if fields["eprint"]:
        fields["archivePrefix"] = "arXiv"
    if record.get("venue"):
        fields["booktitle" if kind == "inproceedings" else ("journal" if kind == "article" else "note")] = record["venue"]
    content = ",\n".join("  " + key + " = {" + str(value) + "}" for key, value in fields.items() if value is not None)
    bib.append("@" + kind + "{selector_candidate_" + str(index).zfill(2) + ",\n" + content + "\n}")
(ROOT / "references.bib").write_text("\n\n".join(bib) + "\n", encoding="utf-8")
print(json.dumps(dict(records=len(records), checked_at=checked), ensure_ascii=False))

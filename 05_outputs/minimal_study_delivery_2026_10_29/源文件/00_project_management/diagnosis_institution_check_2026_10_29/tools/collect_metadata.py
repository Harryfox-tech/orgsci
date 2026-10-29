"""Recheck three exact DOIs; store selected metadata, not article text."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DOIS = [
    "10.1257/aer.20200961",
    "10.3368/jhr.0519-10226R3",
    "10.1145/3351095.3372830",
]


def fetch(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    log = {"url": url, "checked_at": datetime.now(timezone.utc).isoformat(),
           "platform": "crossref", "query_type": "exact_doi"}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OrgsciResearch/academic-search"})
        with urllib.request.urlopen(req, timeout=25) as response:
            item = json.load(response)["message"]
            log.update(http_status=response.status, final_url=response.url)
        keep = ["DOI", "title", "author", "container-title", "type", "published",
                "published-print", "published-online", "issued", "volume", "issue", "page", "URL"]
        return log, {k: item[k] for k in keep if k in item}
    except Exception as exc:
        log.update(http_status=getattr(exc, "code", None), error=str(exc))
        if getattr(exc, "headers", None):
            log["retry_after"] = exc.headers.get("Retry-After")
        return log, None


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        responses = list(pool.map(fetch, DOIS))
    records = []
    extracted = []
    for log, item in responses:
        extracted.append({"request": log, "selected_metadata": item})
        if item is None:
            continue
        date = item.get("published-print", item.get("published", item.get("issued", {})))
        parts = date.get("date-parts", [[None]])[0]
        evidence = {"platform": "crossref", "source_url": log["url"],
                    "checked_at": log["checked_at"], "evidence_type": "source_metadata"}
        record = {"title": item["title"][0],
                  "authors": [" ".join(filter(None, [a.get("given"), a.get("family")]))
                              for a in item.get("author", [])],
                  "year": parts[0], "venue": (item.get("container-title") or [None])[0],
                  "publication_type": item.get("type"), "doi": item["DOI"],
                  "source_platforms": ["crossref"], "fetched_at": log["checked_at"][:10],
                  "volume": item.get("volume"), "issue": item.get("issue"),
                  "pages": item.get("page"), "publication_date_parts": parts,
                  "first_online_date_parts": item.get("published-online", {}).get("date-parts"),
                  "abstract": None, "citation_count": None, "citation_counts": [],
                  "download_status": "not_requested", "open_access_status": None,
                  "full_text_status": None, "field_sources": {},
                  "missing_fields": {"abstract": "Not exported; source claims are paraphrased separately.",
                                     "citation_count": "Not queried.",
                                     "open_access_status": "Not inferred from DOI metadata.",
                                     "full_text_status": "Availability not assessed by this DOI check; see reading annotation."}}
        record["field_sources"] = {key: [evidence] for key in
                                   ("title", "authors", "year", "venue", "publication_type", "doi",
                                    "volume", "issue", "pages") if record.get(key) is not None}
        records.append(record)
    extra = ROOT / "primary_records.json"
    if extra.exists():
        records.extend(json.loads(extra.read_text(encoding="utf-8")))
    annotation_file = ROOT / "record_annotations.json"
    if annotation_file.exists():
        annotations = json.loads(annotation_file.read_text(encoding="utf-8"))
        for record in records:
            key = (record.get("doi") or record.get("arxiv_id") or "").lower()
            annotation = annotations.get(key, {})
            record.update(annotation.get("fields", {}))
            record.setdefault("field_sources", {}).update(annotation.get("field_sources", {}))
            record.setdefault("missing_fields", {}).update(annotation.get("missing_fields", {}))
            for field, value in annotation.get("fields", {}).items():
                if value is not None:
                    record["missing_fields"].pop(field, None)
    (ROOT / "crossref_checks.json").write_text(
        json.dumps(extracted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "records.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"requests": len(responses),
                      "crossref_successful_records": sum(item is not None for _, item in responses),
                      "exported_records": len(records),
                      "papers": [{k: r.get(k) for k in ("title", "year", "volume", "issue", "doi")}
                                 for r in records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

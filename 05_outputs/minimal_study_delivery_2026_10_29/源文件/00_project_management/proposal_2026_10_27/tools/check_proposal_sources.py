"""Bounded metadata check for a proposal, not a systematic review or ABM run."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "search_records"
OLD = ROOT.parent / "endogenous_talent_supply_2026_10_24/records.json"
QUERIES = [
    '"strategic classification" verification improvement',
    '"algorithmic recourse" information acquisition',
    'skills certification training diagnosis investment',
]
DOIS = ["10.2307/1882010", "10.1214/aoms/1177729032"]
KEEP = {"10.1162/003355301753265615", "10.1257/aer.20200961",
        "10.1145/3351095.3372861", "10.1145/3630106.3658929",
        "10.1145/3708359.3712095", "10.1016/s0014-2921(99)00049-5"}


def fetch(task):
    key, platform, url = task
    path = RAW / (key + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    request = {"platform": platform, "url": url,
               "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    data = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OrgsciResearch/academic-search"})
        with urllib.request.urlopen(req, timeout=15) as response:
            request.update(http_status=response.status, final_url=response.url)
            raw = response.read().decode("utf-8")
            data = raw if platform == "arxiv" else json.loads(raw)
    except Exception as exc:
        request.update(http_status=getattr(exc, "code", None), error=str(exc))
        if getattr(exc, "headers", None):
            request["retry_after"] = exc.headers.get("Retry-After")
    result = {"request": request, "data": data}
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def crossref_record(item, request):
    dates = item.get("published", {}).get("date-parts", [[None]])[0]
    full_date = "-".join(str(x).zfill(2) for x in dates) if len(dates) == 3 else None
    evidence = {"platform": "crossref", "source_url": request["url"],
                "checked_at": request["checked_at"], "evidence_type": "source_metadata"}
    record = {"title": item["title"][0], "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in item.get("author", [])],
              "year": dates[0], "publication_date": full_date,
              "publication_type": item.get("type"), "venue": (item.get("container-title") or [None])[0],
              "doi": item.get("DOI"), "source_platforms": ["crossref"],
              "fetched_at": request["checked_at"][:10], "abstract": None,
              "citation_count": None, "download_status": "not_requested",
              "missing_fields": {"abstract": "Not exported verbatim.", "citation_count": "Not queried."}}
    record["field_sources"] = {field: [evidence] for field in (
        "title", "authors", "year", "publication_date", "publication_type", "venue", "doi")
        if record.get(field) is not None}
    return record


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    tasks = [("discovery_" + str(i), "openalex", "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "search": q, "per-page": 8, "filter": "to_publication_date:2026-10-27"})) for i, q in enumerate(QUERIES)]
    tasks += [("doi_" + str(i), "crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")) for i, doi in enumerate(DOIS)]
    tasks += [("arxiv_batch", "arxiv", "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "id_list": "2502.02328,2609.12179,2609.22534", "max_results": 3}))]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(fetch, tasks))
    records = [item for item in json.loads(OLD.read_text(encoding="utf-8"))
               if (item.get("doi") or "").lower() in KEEP or item["title"] == "Strategic Classification is Causal Modeling in Disguise"]
    for item in records:
        item["reuse_note"] = "Metadata carried from 2026-10-24; original fetched_at and provenance preserved. Relevant source rechecks are described in the evidence memo."
    for result in results:
        if result["request"]["platform"] == "crossref" and result.get("data"):
            records.append(crossref_record(result["data"]["message"], result["request"]))
    primary = ROOT / "primary_records.json"
    if primary.exists():
        supplement = json.loads(primary.read_text(encoding="utf-8"))
        for item in supplement:
            evidence = {"platform": item["source_platforms"][0], "source_url": item["url"],
                        "checked_at": item["verified_at"], "evidence_type": "page_text",
                        "note": item["verification_note"]}
            item["field_sources"] = {field: [evidence] for field in (
                "title", "authors", "year", "publication_date", "publication_type", "venue", "doi")
                if item.get(field) is not None}
            item["missing_fields"] = {"citation_count": "Not queried.", "abstract": "Not exported verbatim."}
        records.extend(supplement)
    (ROOT / "records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "query_log.json").write_text(json.dumps([r["request"] for r in results], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    discovery = []
    for task, result in zip(tasks, results):
        if task[1] == "openalex":
            hits = (result.get("data") or {}).get("results", [])
            discovery.append({"query": QUERIES[len(discovery)], "hits": len(hits),
                              "titles": [x.get("title") for x in hits]})
    (ROOT / "discovery_summary.json").write_text(json.dumps(discovery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bib = []
    for index, item in enumerate(records, 1):
        kind = "book" if item.get("publication_type") == "book" else "misc" if item.get("publication_type") == "preprint" else "inproceedings" if item.get("publication_type") == "proceedings-article" else "article"
        fields = {"title": item["title"], "author": " and ".join(item["authors"]), "year": item["year"],
                  "doi": item.get("doi"), "url": item.get("url") or ("https://doi.org/" + item["doi"] if item.get("doi") else None)}
        if item.get("venue"):
            fields["publisher" if kind == "book" else "howpublished" if kind == "misc" else "booktitle" if kind == "inproceedings" else "journal"] = item["venue"]
        if item.get("arxiv_id"):
            fields.update(eprint=item["arxiv_id"], archivePrefix="arXiv")
        bib.append("@" + kind + "{proposal_" + str(index).zfill(2) + ",\n" + ",\n".join(
            "  " + k + " = {" + str(v) + "}" for k, v in fields.items() if v is not None) + "\n}")
    (ROOT / "references.bib").write_text("\n\n".join(bib) + "\n", encoding="utf-8")
    print(json.dumps({"requests": len(results), "statuses": [r["request"].get("http_status") for r in results],
                      "records": len(records), "discovery": discovery}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

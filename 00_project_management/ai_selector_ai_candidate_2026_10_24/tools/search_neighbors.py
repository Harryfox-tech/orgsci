"""Bounded academic-search audit. Literature retrieval only; no model execution.

Raw requests are cached with their actual timestamps. Re-running reuses the
cache; remove no files automatically. No credentials or private data are used.
"""
import concurrent.futures
import datetime as dt
from html.parser import HTMLParser
import json
import re
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "search_records"
RAW.mkdir(parents=True, exist_ok=True)
QUERIES = [
    "AI self preferencing algorithmic hiring",
    "LLM hiring strategic manipulation model choice",
    "LLM judge generator co evolution",
    "AI agent labor market evaluation reputation",
    "LLM judge reward overoptimization",
    "algorithmic monoculture hiring",
]
ARXIV = [
    "2509.00462", "2404.13076", "2502.13221", "2501.16355",
    "2604.06688", "2604.23897", "2608.26582", "2608.18091",
    "2604.06996", "2609.21325", "2605.27371", "2604.06047",
    "2609.09776",
]
DOIS = [
    "10.1609/aies.v8i3.36755", "10.1287/mnsc.2024.07027",
    "10.1037/a0026078", "10.1111/phpe.70018",
    "10.18653/v1/2025.acl-long.649", "10.2139/ssrn.7592711",
    "10.1016/j.respol.2026.105568",
]


def fetch(platform, url, key, as_json=True):
    path = RAW / (key + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    request = dict(platform=platform, url=url,
                   checked_at=dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"))
    payload = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OrgsciResearch/academic-search"})
        with urllib.request.urlopen(req, timeout=15) as response:
            request.update(http_status=response.status, final_url=response.url,
                           content_type=response.headers.get("Content-Type"))
            body = response.read().decode("utf-8")
            payload = json.loads(body) if as_json else body
    except Exception as error:
        request.update(http_status=getattr(error, "code", None), error=str(error))
        if getattr(error, "headers", None):
            request["retry_after"] = error.headers.get("Retry-After")
    output = dict(request=request, data=payload)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


class CitationMeta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").startswith("citation_"):
            self.meta.setdefault(attrs["name"], []).append(attrs.get("content", ""))


def base_record(request):
    evidence = dict(platform=request["platform"], source_url=request["url"],
                    checked_at=request["checked_at"], evidence_type="source_metadata")
    return dict(title=None, authors=[], year=None, source_platforms=[request["platform"]],
                fetched_at=request["checked_at"][:10], citation_count=None, abstract=None,
                download_status="not_requested", missing_fields={
                    "citation_count": "Not queried; counts are not evidence of novelty.",
                    "abstract": "See original source; no verbatim abstract exported."}), evidence


def arxiv_record(identifier):
    output = fetch("arxiv", "https://arxiv.org/abs/" + identifier, "arxiv_" + identifier, False)
    if not output["data"]:
        return None
    parser = CitationMeta()
    parser.feed(output["data"])
    meta = parser.meta
    if not meta.get("citation_title"):
        return None
    record, evidence = base_record(output["request"])
    publication = (meta.get("citation_date") or [""])[0].replace("/", "-")
    record.update(title=meta["citation_title"][0], authors=meta.get("citation_author", []),
                  year=int(publication[:4]) if publication else None,
                  publication_date=publication if len(publication) == 10 else None,
                  publication_type="preprint", venue="arXiv", arxiv_id=identifier,
                  version_identifier=(meta.get("citation_arxiv_id") or [identifier])[0],
                  source_url=output["request"]["url"],
                  pdf_url=(meta.get("citation_pdf_url") or [None])[0])
    record["full_text_status"] = "open_pdf" if record["pdf_url"] else "unknown"
    record["field_sources"] = {key: [evidence] for key in [
        "title", "authors", "year", "publication_date", "publication_type", "venue",
        "arxiv_id", "pdf_url", "full_text_status"] if record.get(key) is not None}
    return record


def crossref_record(doi):
    output = fetch("crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"),
                   "doi_" + re.sub(r"[^a-zA-Z0-9]", "_", doi))
    source = (output.get("data") or {}).get("message") or {}
    if not source:
        return None
    record, evidence = base_record(output["request"])
    dates = {key: "-".join(str(x).zfill(2) if i else str(x) for i, x in enumerate(source[key]["date-parts"][0]))
             for key in ["published-online", "published-print", "published"]
             if source.get(key, {}).get("date-parts")}
    publication = dates.get("published-online") or dates.get("published")
    record.update(title=(source.get("title") or [None])[0],
                  authors=[" ".join(filter(None, [a.get("given"), a.get("family")])) for a in source.get("author", [])],
                  year=int(publication[:4]) if publication else None,
                  publication_date=publication if publication and len(publication) == 10 else None,
                  publication_dates=dates, publication_type=source.get("type"),
                  venue=(source.get("container-title") or [None])[0], doi=doi,
                  source_url="https://doi.org/" + doi)
    record["field_sources"] = {key: [evidence] for key in [
        "title", "authors", "year", "publication_date", "publication_type", "venue", "doi"]
        if record.get(key) is not None}
    return record


def main():
    for i, query in enumerate(QUERIES):
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "search": query, "per-page": 8,
            "filter": "from_publication_date:2021-01-01,to_publication_date:2026-10-24"})
        output = fetch("openalex", url, "discovery_" + str(i))
        results = (output.get("data") or {}).get("results", [])
        print(json.dumps(dict(query=query, status=output["request"].get("http_status"),
                              hits=len(results), titles=[r.get("title") for r in results[:4]]), ensure_ascii=False), flush=True)
    # Low concurrency, no unbounded rate-limit retries or key discovery.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = [record for record in pool.map(crossref_record, DOIS) if record]
    for identifier in ARXIV:
        record = arxiv_record(identifier)
        if record:
            records.append(record)
            print(json.dumps(dict(arxiv_id=identifier, title=record["title"]), ensure_ascii=False), flush=True)
    # PMLR exposes citation metadata but does not necessarily register a DOI.
    output = fetch("pmlr", "https://proceedings.mlr.press/v350/ebling26a.html", "pmlr_ebling26a", False)
    if output["data"]:
        parser = CitationMeta()
        parser.feed(output["data"])
        meta = parser.meta
        if meta.get("citation_title"):
            record, evidence = base_record(output["request"])
            record.update(title=meta["citation_title"][0], authors=meta.get("citation_author", []),
                          year=2026, publication_type="conference",
                          venue="Proceedings of Fifth European Conference on Algorithmic Fairness, PMLR 350",
                          source_url=output["request"]["url"],
                          pdf_url=(meta.get("citation_pdf_url") or [None])[0])
            record["full_text_status"] = "open_pdf" if record["pdf_url"] else "unknown"
            record["field_sources"] = {key: [evidence] for key in [
                "title", "authors", "year", "publication_type", "venue", "pdf_url", "full_text_status"]
                if record.get(key) is not None}
            records.append(record)
    (ROOT / "records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    requests = [json.loads(path.read_text(encoding="utf-8"))["request"] for path in sorted(RAW.glob("*.json"))]
    (ROOT / "query_log.json").write_text(json.dumps(requests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(records=len(records), requests=len(requests)), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

"""Bounded scholarly metadata audit for endogenous talent supply; no ABM runs."""
import datetime as dt
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "search_records"
RAW.mkdir(parents=True, exist_ok=True)
QUERIES = [
    "strategic classification human capital investment evidence",
    "certification training skills signaling",
    "algorithmic recourse explanation opportunity constraints",
    "recruitment feedback endogenous talent supply",
    "evaluation feedback skill improvement evidence production",
    "testing training screening worker ability",
]
DOIS = [
    "10.1145/3630106.3658929",
    "10.1016/S0014-2921(99)00049-5",
    "10.1257/aer.20200961",
    "10.1145/3708359.3712095",
    "10.4230/LIPIcs.FORC.2022.3",
    "10.1609/aaai.v40i20.38772",
    "10.1037/a0026078",
]
TITLES = [
    "The Disparate Equilibria of Algorithmic Decision Making when Individuals Invest Rationally",
    "Rankings and Reactivity: How Public Measures Recreate Social Worlds",
    "Why Do Temporary Help Firms Provide Free General Skills Training?",
]


def get(platform, url, key):
    path = RAW / (key + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    request = dict(platform=platform, url=url,
                   checked_at=dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"))
    data = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OrgsciResearch/academic-search"})
        with urllib.request.urlopen(req, timeout=15) as response:
            request.update(http_status=response.status, final_url=response.url)
            data = json.load(response)
    except Exception as error:
        request.update(http_status=getattr(error, "code", None), error=str(error))
        if getattr(error, "headers", None):
            request["retry_after"] = error.headers.get("Retry-After")
    output = dict(request=request, data=data)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def normalize(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def record(source, request):
    dates = {key: "-".join(str(v).zfill(2) if i else str(v) for i, v in enumerate(source[key]["date-parts"][0]))
             for key in ["published-online", "published-print", "published"]
             if source.get(key, {}).get("date-parts")}
    first = dates.get("published-online") or dates.get("published")
    issue = dates.get("published-print") or dates.get("published") or first
    evidence = dict(platform="crossref", source_url=request["url"], checked_at=request["checked_at"],
                    evidence_type="source_metadata")
    item = dict(title=(source.get("title") or [None])[0],
                authors=[" ".join(filter(None, [a.get("given"), a.get("family")])) for a in source.get("author", [])],
                year=int(issue[:4]) if issue else None,
                publication_date=first if first and len(first) == 10 else None,
                publication_dates=dates, publication_type=source.get("type"),
                venue=(source.get("container-title") or [None])[0], doi=source.get("DOI"),
                abstract=None, citation_count=None, download_status="not_requested",
                source_platforms=["crossref"], fetched_at=request["checked_at"][:10],
                missing_fields={"abstract":"Original response retained; no verbatim abstract exported.",
                                "citation_count":"Not queried; citation counts do not establish novelty."})
    item["field_sources"] = {key: [evidence] for key in [
        "title", "authors", "year", "publication_date", "publication_type", "venue", "doi"]
        if item.get(key) is not None}
    return item


def main():
    for index, query in enumerate(QUERIES):
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "search":query, "per-page":8, "filter":"to_publication_date:2026-10-24"})
        output = get("openalex", url, "discovery_" + str(index))
        hits = (output.get("data") or {}).get("results", [])
        print(json.dumps(dict(query=query, status=output["request"].get("http_status"),
                              hits=len(hits), titles=[r.get("title") for r in hits[:3]]), ensure_ascii=False), flush=True)
    records = []
    for index, doi in enumerate(DOIS):
        output = get("crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"),
                     "doi_" + str(index))
        source = (output.get("data") or {}).get("message") or {}
        if source:
            records.append(record(source, output["request"]))
    for index, title in enumerate(TITLES):
        output = get("crossref", "https://api.crossref.org/works?" + urllib.parse.urlencode({
            "query.title":title, "rows":3}), "title_" + str(index))
        matches = [source for source in (output.get("data") or {}).get("message", {}).get("items", [])
                   if normalize((source.get("title") or [""])[0]) == normalize(title)]
        # Exact normalized title is a candidate metadata match, not proof of full-text identity.
        if matches:
            records.append(record(matches[0], output["request"]))
        print(json.dumps(dict(title_query=title, exact_matches=len(matches)), ensure_ascii=False), flush=True)
    primary_records = ROOT / "primary_records.json"
    if primary_records.exists():
        records.extend(json.loads(primary_records.read_text(encoding="utf-8")))
    (ROOT / "records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    requests = [json.loads(path.read_text(encoding="utf-8"))["request"] for path in sorted(RAW.glob("*.json"))]
    (ROOT / "query_log.json").write_text(json.dumps(requests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bib = []
    for index, item in enumerate(records, 1):
        kind = ("inproceedings" if item.get("publication_type") == "proceedings-article"
                else "misc" if item.get("publication_type") == "preprint" else "article")
        fields = {"title":item["title"], "author":" and ".join(item["authors"]), "year":item["year"],
                  "doi":item.get("doi"), "url":item.get("url") or (
                      "https://doi.org/" + item["doi"] if item.get("doi") else None)}
        if item.get("venue"):
            fields["booktitle" if kind == "inproceedings" else "journal"] = item["venue"]
        body = ",\n".join("  " + key + " = {" + str(value) + "}" for key, value in fields.items() if value is not None)
        bib.append("@" + kind + "{talent_supply_" + str(index).zfill(2) + ",\n" + body + "\n}")
    (ROOT / "references.bib").write_text("\n\n".join(bib) + "\n", encoding="utf-8")
    print(json.dumps(dict(records=len(records), requests=len(requests))), flush=True)


if __name__ == "__main__":
    main()

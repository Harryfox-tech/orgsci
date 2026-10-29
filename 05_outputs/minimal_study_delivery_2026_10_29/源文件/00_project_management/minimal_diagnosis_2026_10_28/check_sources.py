"""Bounded precise Crossref checks. Raw API responses are not canonical records.

No citation counts, journal ranking, paywall bypass, or automatic full-text claims.
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "source_checks"
DOIS = (
    "10.1016/S0014-2921(99)00049-5",
    "10.1162/003355301753265615",
    "10.1145/3351095.3372861",
    "10.1257/aer.20200961",
)


def main():
    OUT.mkdir(exist_ok=True)
    log = []
    for index, doi in enumerate(DOIS):
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        row = {"doi": doi, "url": url, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
               "timeout_seconds": 15, "retries_used": 0,
               "scope": "Exact identity metadata only; no full-text verification"}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "AcademicSearch-MinimalResearch/1.0"})
            with urllib.request.urlopen(request, timeout=15) as response:
                body = response.read()
                row["http_status"] = response.status
            name = f"crossref_{index}.json"
            (OUT / name).write_bytes(body)
            message = json.loads(body)["message"]
            row.update({"raw_response_file": name, "sha256": hashlib.sha256(body).hexdigest(),
                        "returned_title": message.get("title"),
                        "returned_doi": message.get("DOI"),
                        "returned_venue": message.get("container-title"),
                        "identity_matches": message.get("DOI", "").lower() == doi.lower()})
        except urllib.error.HTTPError as error:
            row.update({"http_status": error.code, "error": str(error),
                        "retry_after": error.headers.get("Retry-After"),
                        "decision": "Stop this source request without retry or bypass"})
        except Exception as error:
            row.update({"http_status": None, "error": type(error).__name__ + ": " + str(error)})
        log.append(row)
        time.sleep(.35)
    (OUT / "query_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(log, ensure_ascii=False))


if __name__ == "__main__":
    main()

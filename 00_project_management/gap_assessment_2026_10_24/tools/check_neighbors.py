"""Bounded academic-search verification for the theory-gap memo; no model runs."""
import concurrent.futures
import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'search_records'
RAW.mkdir(parents=True, exist_ok=True)
QUERIES = [
    'AI feedback skill development organizational coordination',
    'AI coaching evaluative feedback confidentiality',
    'personnel selection generative AI coaching validity',
    'algorithmic hiring skill investment performative policy',
    'career recommendations skill development congestion',
    'human capital complementary skill investment coordination',
]
DOIS = [
    '10.1111/ijsa.12516',
    '10.1016/j.dss.2026.114681',
    '10.3390/merits6040032',
    '10.3390/admsci16080372',
    '10.1177/0001839212453028',
    '10.5465/amr.2009.0318',
    '10.1037/a0026078',
    '10.1002/hrm.70071',
    '10.1016/j.jvb.2024.104011',
    '10.1111/ijsa.70060',
    '10.1145/3715275.3732008',
    '10.1145/3708359.3712095',
    '10.1287/mnsc.2024.04528',
]


def get(platform, url, key):
    path = RAW / (key + '.json')
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    request = dict(platform=platform, url=url,
                   checked_at=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'))
    data = None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OrgsciResearch/academic-search', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as response:
            request['http_status'] = response.status
            data = json.load(response)
    except Exception as error:
        request.update(http_status=getattr(error, 'code', None), error=str(error))
        if getattr(error, 'headers', None):
            request['retry_after'] = error.headers.get('Retry-After')
    out = dict(request=request, data=data)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out


def check(doi):
    response = get('crossref', 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/'),
                   re.sub('[^a-zA-Z0-9]', '_', doi) + '_crossref')
    c = (response.get('data') or {}).get('message') or {}
    if not c:
        return None
    req = response['request']
    evidence = dict(platform='crossref', source_url=req['url'], checked_at=req['checked_at'], evidence_type='source_metadata')
    dates = {k: '-'.join(str(v).zfill(2) if i else str(v) for i, v in enumerate(c[k]['date-parts'][0]))
             for k in ['published-online', 'published-print', 'published'] if c.get(k, {}).get('date-parts')}
    issue = dates.get('published-print') or dates.get('published')
    online = dates.get('published-online') or dates.get('published')
    record = dict(title=(c.get('title') or [None])[0],
                  authors=[' '.join(filter(None, [a.get('given'), a.get('family')])) for a in c.get('author', [])],
                  year=int(issue[:4]) if issue else None,
                  publication_date=online if online and len(online) == 10 else None,
                  publication_dates=dates, publication_type=c.get('type'),
                  venue=(c.get('container-title') or [None])[0], doi=doi,
                  abstract=None, citation_count=None, open_access_status=None,
                  full_text_status='unknown', download_status='not_requested',
                  source_platforms=['crossref'], fetched_at='2026-10-24',
                  field_sources={k: [evidence] for k in ['title', 'authors', 'year', 'publication_date', 'publication_type', 'venue', 'doi', 'full_text_status']},
                  missing_fields=dict(abstract='原始摘要保留于API响应；本轮不导出逐字摘要。', citation_count='本轮未查询引用数。',
                                      open_access_status='未作独立OA判定；公开网页/正文证据另见报告。'))
    if online and len(online) != 10:
        record['missing_fields']['publication_date'] = '来源只给部分日期：' + online
    print(json.dumps(dict(title=record['title'], doi=doi, dates=dates), ensure_ascii=False), flush=True)
    return record


def main():
    for i, query in enumerate(QUERIES):
        result = get('openalex', 'https://api.openalex.org/works?' + urllib.parse.urlencode(dict(
            search=query, filter='from_publication_date:2021-01-01,to_publication_date:2026-10-24',
            per_page=8)).replace('per_page=', 'per-page='), 'discovery_' + str(i))
        hits = (result.get('data') or {}).get('results', [])
        print(json.dumps(dict(query=query, status=result['request'].get('http_status'), hits=len(hits),
                              titles=[x.get('title') for x in hits[:4]]), ensure_ascii=False), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = [r for r in pool.map(check, DOIS) if r]
    (ROOT / 'neighbor_records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    log = [json.loads(p.read_text(encoding='utf-8'))['request'] for p in sorted(RAW.glob('*.json'))]
    (ROOT / 'query_log.json').write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(records=len(records), requests=len(log))))


if __name__ == '__main__':
    main()

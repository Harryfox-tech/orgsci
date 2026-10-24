"""Academic-search metadata verification; no downloads, model edits, or pushes."""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'search_records'
DATA.mkdir(parents=True, exist_ok=True)
DATE = '2026-10-24'
CANDIDATES = [
    ('A01', '10.1108/SAMAMJ-06-2026-0038'),
    ('A02', '10.1007/s44163-026-01488-6'),
    ('A03', '10.3389/frai.2026.1798519'),
    ('A04', '10.1177/21582440251361746'),
    ('A05', '10.1007/s10551-022-05049-6'),
    ('B01', '10.1016/j.techfore.2026.124800'),
    ('B02', '10.1108/OMJ-09-2025-2716'),
    ('B03', '10.1007/s44163-026-02055-9'),
    ('B04', '10.1007/s11301-025-00580-y'),
    ('B05', '10.4102/sajhrm.v24i0.3649'),
    ('B06', '10.1002/job.2735'),
    ('B07', '10.1016/j.hrmr.2022.100924'),
    ('B08', '10.1109/JPROC.2025.3572744'),
    ('B09', '10.5465/annals.2018.0174'),
    ('C01', '10.1093/9780197809013.003.0018'),
    ('C02', '10.1002/hrm.70025'),
    ('C03', '10.1016/j.heliyon.2023.e14694'),
    ('C04', '10.1016/j.jjimei.2024.100288'),
    ('C05', '10.1108/JWAM-11-2024-0164'),
    ('C06', '10.1080/17521882.2026.2640932'),
    ('C07', '10.1145/3820900'),
    ('C08', '10.1108/PR-01-2024-0077'),
    ('D01', '10.1007/s10648-026-10166-z'),
    ('D02', '10.1080/01443410.2025.2553639'),
]
DISCOVERY = [
    'artificial intelligence recruitment systematic review',
    'artificial intelligence talent management systematic review',
    'artificial intelligence assessment feedback coaching review',
]


def fetch(platform, url, name):
    cache = DATA / f'{name}.json'
    if cache.exists():
        return json.loads(cache.read_text(encoding='utf-8'))
    request = {'platform': platform, 'url': url,
               'checked_at': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')}
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'OrgsciAcademicSearch/1.4', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=16) as response:
            data = json.load(response)
            request['http_status'] = response.status
    except Exception as error:
        data = None
        request.update(http_status=getattr(error, 'code', None), error=str(error),
                       retry_after=getattr(error, 'headers', {}).get('Retry-After')
                       if getattr(error, 'headers', None) else None)
    envelope = {'request': request, 'data': data}
    cache.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return envelope


def dates(cr):
    return {key: '-'.join(str(n).zfill(2) if i else str(n)
                         for i, n in enumerate(cr[key]['date-parts'][0]))
            for key in ['published-online', 'published-print', 'published']
            if cr.get(key, {}).get('date-parts')}


def source(envelope):
    req = envelope['request']
    return {'platform': req['platform'], 'source_url': req['url'],
            'checked_at': req['checked_at'], 'evidence_type': 'source_metadata'}


def verify(item):
    identifier, doi = item
    key = re.sub(r'[^a-zA-Z0-9]', '_', doi)
    cr = fetch('crossref', 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/'), key + '_crossref')
    if cr['request'].get('http_status') == 429:
        cr = fetch('crossref', 'https://api.crossref.org/works/' + urllib.parse.quote(doi.lower(), safe='/'), key + '_crossref_retry1')
    oa = fetch('openalex', 'https://api.openalex.org/works/https://doi.org/' + urllib.parse.quote(doi, safe='/'), key + '_openalex')
    c = (cr.get('data') or {}).get('message', {})
    o = oa.get('data') or {}
    publication_dates = dates(c)
    selected_date = publication_dates.get('published-online') or publication_dates.get('published') or o.get('publication_date')
    issue_date = publication_dates.get('published-print')
    authors = [' '.join(x for x in [a.get('given'), a.get('family')] if x)
               for a in c.get('author', [])]
    if not authors:
        authors = [a['author']['display_name'] for a in o.get('authorships', [])]
    location = o.get('best_oa_location') or {}
    pdf_url = location.get('pdf_url')
    fs = {key: [source(cr if c else oa)] for key in ['title', 'authors', 'doi', 'year', 'publication_date', 'venue', 'publication_type'] if c or o}
    if o:
        for key in ['open_access_status', 'full_text_status']:
            fs[key] = [source(oa)]
        if pdf_url:
            fs['pdf_url'] = [source(oa)]
    count = o.get('cited_by_count')
    record = {
        'review_id': identifier, 'title': (c.get('title') or [o.get('title')])[0],
        'authors': authors, 'year': int((issue_date or selected_date)[:4]) if selected_date else None,
        'publication_date': selected_date if selected_date and len(selected_date) == 10 else None,
        'publication_date_partial': selected_date if selected_date and len(selected_date) != 10 else None,
        'publication_dates': publication_dates,
        'publication_type': c.get('type') or o.get('type'),
        'venue': (c.get('container-title') or [(o.get('primary_location') or {}).get('source', {}).get('display_name')])[0],
        'volume': c.get('volume'), 'issue': c.get('issue'), 'pages': c.get('page'),
        'article_number': c.get('article-number'), 'doi': doi,
        'arxiv_id': '2307.03195v3' if identifier == 'B08' else None,
        'abstract': None, 'citation_count': count,
        'citation_counts': [{'platform': 'openalex', 'count': count,
                             'checked_at': oa['request']['checked_at'],
                             'source_url': oa['request']['url']}] if count is not None else [],
        'open_access_status': (o.get('open_access') or {}).get('oa_status'),
        'full_text_status': 'open_pdf' if pdf_url else 'unknown',
        'pdf_url': pdf_url, 'download_status': 'not_requested',
        'pdf_verification_status': 'unverified', 'paper_identity_status': 'unverified',
        'field_sources': fs,
        'source_platforms': [p for p, data in [('crossref', c), ('openalex', o)] if data],
        'missing_fields': {'abstract': '未请求逐字摘要；范围与阅读建议另见人工核验清单。'},
        'fetched_at': DATE,
    }
    if selected_date and len(selected_date) != 10:
        record['missing_fields']['publication_date'] = '来源仅给到年/月：' + selected_date + '；保留部分日期，不编造具体日。'
    print(json.dumps({'id': identifier, 'title': record['title'],
                      'dates': publication_dates, 'doi': doi,
                      'status': [cr['request'].get('http_status'), oa['request'].get('http_status')]},
                     ensure_ascii=False), flush=True)
    return record


def main():
    for index, query in enumerate(DISCOVERY):
        url = 'https://api.openalex.org/works?' + urllib.parse.urlencode({
            'search': query, 'filter': 'from_publication_date:2023-01-01,to_publication_date:2026-10-24',
            'per-page': 12})
        result = fetch('openalex', url, f'discovery_{index}')
        print(json.dumps({'discovery': query, 'returned': len((result.get('data') or {}).get('results', [])),
                          'status': result['request'].get('http_status')}, ensure_ascii=False), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(verify, CANDIDATES))
    (ROOT / 'records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    log = [json.loads(path.read_text(encoding='utf-8'))['request']
           for path in sorted(DATA.glob('*.json'))]
    (ROOT / 'query_log.json').write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'records': len(records), 'queries': len(log)}, ensure_ascii=False))


if __name__ == '__main__':
    main()

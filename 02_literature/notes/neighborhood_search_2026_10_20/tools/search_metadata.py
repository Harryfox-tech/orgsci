"""Source-traceable metadata and targeted discovery; not a systematic review."""
from __future__ import annotations

import datetime as dt
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'search_records'
DATA.mkdir(parents=True, exist_ok=True)
LOG = []

DOIS = [
    '10.1287/mnsc.2020.3727',
    '10.1287/mnsc.2023.01373',
    '10.1287/orsc.2022.16738',
    '10.1002/hrm.22192',
    '10.5465/amj.2023.0311',
    '10.1287/orsc.2020.14214',
    '10.1287/orsc.2023.1688',
    '10.1016/j.euroecorev.2025.105238',
    '10.5465/annals.2016.0117',
    '10.1093/restud/rdy059',
    '10.1177/001979397602900204',
    '10.1093/qje/qjag017',
    '10.1145/3604915.3608817',
    '10.1109/ACCESS.2024.3390229',
]
TITLE_QUERIES = [
    'Algorithmic Fairness in Performative Policy Learning: Escaping the Impossibility of Group Fairness',
    'Learning the Distribution Map in Reverse Causal Performative Prediction',
    'Providing Advice to Jobseekers at Low Cost: An Experimental Study on Online Advice',
]
DISCOVERY = [
    'demand aware career path recommendations',
    'internal talent markets skill development',
    'algorithmic recommendations experiential learning',
    'performative prediction human capital investment',
    'skill investment information labor market training',
    'skill recommendations competition labor supply',
]


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def fetch(url, cache_name):
    cache = DATA / cache_name
    if cache.exists():
        existing = json.loads(cache.read_text(encoding='utf-8'))
        LOG.append(existing['request'])
        return existing.get('data') or {}, existing['request']['checked_at']
    request = {'url': url, 'checked_at': stamp()}
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'OrgsciAcademicSearch/1.0', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=14) as response:
            data = json.load(response)
            if isinstance(data, str):
                data = json.loads(data)
            request['http_status'] = response.status
    except Exception as error:
        data = {}
        request.update(http_status=getattr(error, 'code', None), error=str(error))
    cache.write_text(json.dumps({'request': request, 'data': data}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    LOG.append(request)
    return data, request['checked_at']


def norm(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', value).lower())


def abstract(index):
    if not index:
        return None
    return ' '.join(word for _, word in sorted((i, word) for word, positions in index.items() for i in positions))


def evidence(platform, url, when):
    return {'platform': platform, 'source_url': url, 'checked_at': when, 'evidence_type': 'source_metadata'}


resolved = []
for index, title in enumerate(TITLE_QUERIES):
    url = 'https://api.crossref.org/works?' + urllib.parse.urlencode({'query.title': title, 'rows': 4})
    data, when = fetch(url, f'crossref_title_{index}.json')
    candidates = data.get('message', {}).get('items', [])
    exact = [p for p in candidates if any(norm(t) == norm(title) for t in p.get('title', []))]
    resolved.append({'query': title, 'url': url, 'checked_at': when,
                     'exact_doi': exact[0]['DOI'] if exact else None,
                     'candidates': [{'title': p.get('title'), 'doi': p.get('DOI')} for p in candidates]})
    if exact:
        DOIS.append(exact[0]['DOI'])
    print(json.dumps({'title_query': title, 'exact_doi': resolved[-1]['exact_doi']}, ensure_ascii=False), flush=True)

records = []
for doi in dict.fromkeys(DOIS):
    key = re.sub(r'[^a-zA-Z0-9]', '_', doi)
    cr_url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/')
    oa_url = 'https://api.openalex.org/works/https://doi.org/' + urllib.parse.quote(doi, safe='/')
    cr_raw, cr_time = fetch(cr_url, key + '_crossref.json')
    oa, oa_time = fetch(oa_url, key + '_openalex.json')
    cr = cr_raw.get('message', {})
    title = (cr.get('title') or [oa.get('title')])[0]
    date = cr.get('published-print', cr.get('published', {})).get('date-parts', [[None]])[0]
    locations = [x for x in oa.get('locations', []) if x]
    candidates = [x for x in locations if x.get('is_oa') and x.get('pdf_url')]
    selected = candidates[0] if candidates else None
    source = {f: [evidence('crossref', cr_url, cr_time)] for f in
              ['title', 'authors', 'year', 'venue', 'doi', 'publication_type'] if cr}
    abs_text = re.sub('<[^>]+>', '', cr.get('abstract', '')) or abstract(oa.get('abstract_inverted_index'))
    if abs_text:
        source['abstract'] = [evidence('crossref' if cr.get('abstract') else 'openalex',
                                      cr_url if cr.get('abstract') else oa_url,
                                      cr_time if cr.get('abstract') else oa_time)]
    for f in ['open_access_status', 'full_text_status']:
        source[f] = [evidence('openalex', oa_url, oa_time)]
    if selected:
        source['pdf_url'] = [evidence('openalex', oa_url, oa_time)]
    records.append({
        'title': title, 'authors': [' '.join(filter(None, [p.get('given'), p.get('family')])) for p in cr.get('author', [])],
        'year': date[0] or oa.get('publication_year'), 'doi': doi,
        'venue': (cr.get('container-title') or [None])[0], 'volume': cr.get('volume'),
        'issue': cr.get('issue'), 'pages': cr.get('page'),
        'publication_type': cr.get('type'),
        'published_online': cr.get('published-online', {}).get('date-parts'),
        'published_print': cr.get('published-print', {}).get('date-parts'),
        'abstract': abs_text, 'jel_codes': [], 'study_type': None,
        'population': None, 'geography': None, 'sample_size': None,
        'open_access_status': oa.get('open_access', {}).get('oa_status', 'unknown'),
        'full_text_status': 'open_pdf' if selected else 'no_open_pdf',
        'pdf_url': selected.get('pdf_url') if selected else None,
        'download_status': 'not_requested', 'pdf_verification_status': 'unverified',
        'paper_identity_status': 'unverified',
        'source_platforms': (['crossref'] if cr else []) + (['openalex'] if oa else []),
        'field_sources': source, 'fetched_at': cr_time[:10],
        'candidate_locations': [{'landing_page_url': x.get('landing_page_url'),
                                 'pdf_url': x.get('pdf_url'), 'is_oa': x.get('is_oa'),
                                 'version': x.get('version')} for x in locations],
        'missing_fields': {f: 'Not inferred from metadata; consult the screened source assessment.'
                           for f in ['jel_codes', 'study_type', 'population', 'geography', 'sample_size']},
    })
    print(json.dumps({'title': title, 'year': records[-1]['year'], 'doi': doi,
                      'pdf_url': records[-1]['pdf_url']}, ensure_ascii=False), flush=True)

discoveries = []
for index, query in enumerate(DISCOVERY):
    url = 'https://api.openalex.org/works?' + urllib.parse.urlencode({
        'search': query, 'per_page': 8, 'filter': 'from_publication_date:2020-01-01,to_publication_date:2026-10-20'})
    data, when = fetch(url, f'openalex_discovery_{index}.json')
    discoveries.append({'query': query, 'url': url, 'checked_at': when,
                        'reported_count': data.get('meta', {}).get('count'),
                        'results': [{'title': p.get('title'), 'doi': p.get('doi'),
                                     'year': p.get('publication_year'),
                                     'venue': ((p.get('primary_location') or {}).get('source') or {}).get('display_name'),
                                     'abstract': abstract(p.get('abstract_inverted_index'))}
                                    for p in data.get('results', [])]})
    print(json.dumps({'discovery': query, 'titles': [p['title'] for p in discoveries[-1]['results']]}, ensure_ascii=False), flush=True)

for name, data in [('records.json', records), ('discovery.json', discoveries),
                   ('title_resolution.json', resolved), ('query_log.json', LOG)]:
    (DATA / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'records': len(records), 'discovery_queries': len(discoveries)}, ensure_ascii=False))

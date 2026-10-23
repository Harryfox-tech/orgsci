"""Traceable Crossref/OpenAlex follow-up using academic-search 1.4.0 guidance."""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'academic_search_followup'
ROOT.mkdir(exist_ok=True)
LOG = []
TARGETS = [
    '10.1037/0021-9010.89.2.248',
    '10.1287/orsc.2017.1166',
    '10.1037/0033-2909.119.2.254',
    '10.1287/orsc.1090.0468',
    '10.1016/j.ejor.2014.10.038',
    '10.1007/s11573-022-01090-z',
]


def get_json(url):
    now = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'AcademicSearchResearchFollowup/1.0',
            'Accept': 'application/json',
        })
        with urllib.request.urlopen(req, timeout=18) as response:
            value = json.load(response)
            if isinstance(value, str):
                value = json.loads(value)
            LOG.append({'url': url, 'checked_at': now, 'status': response.status})
            return value, now
    except Exception as error:
        LOG.append({'url': url, 'checked_at': now,
                    'status': getattr(error, 'code', None), 'error': str(error)})
        return {}, now


def evidence(platform, url, stamp, kind='source_metadata'):
    return {'platform': platform, 'source_url': url,
            'checked_at': stamp, 'evidence_type': kind}


def abstract_from_index(index):
    if not index:
        return None
    pairs = sorted((position, word) for word, positions in index.items() for position in positions)
    return ' '.join(word for _, word in pairs)


records = []
cached_records = {}
if (ROOT / 'records.json').exists():
    cached_records = {r['doi']: r for r in json.loads((ROOT / 'records.json').read_text(encoding='utf-8'))}
if (ROOT / 'query_log.json').exists():
    LOG.extend(json.loads((ROOT / 'query_log.json').read_text(encoding='utf-8')))
for doi in TARGETS:
    if doi in cached_records:
        records.append(cached_records[doi])
        continue
    cr_url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/')
    oa_url = 'https://api.openalex.org/works/https://doi.org/' + urllib.parse.quote(doi, safe='/')
    cr_raw, cr_time = get_json(cr_url)
    cr = cr_raw.get('message', {})
    oa, oa_time = get_json(oa_url)
    date = cr.get('published-print', cr.get('published', {})).get('date-parts', [[None]])[0]
    title = (cr.get('title') or [oa.get('title')])[0]
    authors = [' '.join(filter(None, [a.get('given'), a.get('family')])) for a in cr.get('author', [])]
    locations = [x for x in oa.get('locations', []) if x]
    eligible = [x for x in locations if x.get('is_oa') and x.get('pdf_url')]
    selected = eligible[0] if eligible else None
    abstract = re.sub('<[^>]+>', '', cr.get('abstract', '')) or abstract_from_index(oa.get('abstract_inverted_index'))
    source_list = (['crossref'] if cr else []) + (['openalex'] if oa else [])
    field_sources = {field: [evidence('crossref', cr_url, cr_time)]
                     for field in ['title', 'authors', 'year', 'doi', 'venue', 'publication_type'] if cr}
    if abstract:
        field_sources['abstract'] = [evidence('crossref' if cr.get('abstract') else 'openalex',
                                              cr_url if cr.get('abstract') else oa_url,
                                              cr_time if cr.get('abstract') else oa_time)]
    if oa:
        field_sources['open_access_status'] = [evidence('openalex', oa_url, oa_time)]
        field_sources['full_text_status'] = [evidence('openalex', oa_url, oa_time)]
    if selected:
        field_sources['pdf_url'] = [evidence('openalex', oa_url, oa_time)]
    record = {
        'title': title, 'authors': authors, 'year': date[0] or oa.get('publication_year'),
        'venue': (cr.get('container-title') or [None])[0], 'doi': doi,
        'publication_type': cr.get('type'), 'publication_status': 'published-journal-article',
        'abstract': abstract, 'jel_codes': [], 'study_type': None, 'sample_size': None,
        'population': None, 'geography': None,
        'open_access_status': oa.get('open_access', {}).get('oa_status', 'unknown'),
        'full_text_status': 'open_pdf' if selected else 'no_open_pdf',
        'pdf_url': selected.get('pdf_url') if selected else None,
        'pdf_verification_status': 'unverified', 'paper_identity_status': 'unverified',
        'download_status': 'eligible' if selected else 'skipped',
        'source_platforms': source_list, 'field_sources': field_sources,
        'fetched_at': cr_time[:10],
        'missing_fields': {
            'study_type': 'Not assigned from metadata; requires methods inspection.',
            'sample_size': 'Not extracted from methods.',
            'population': 'Not extracted from methods.',
            'geography': 'Not extracted from methods.',
            'jel_codes': 'Not provided by checked records.',
        },
        'candidate_locations': [{
            'landing_page_url': x.get('landing_page_url'),
            'pdf_url': x.get('pdf_url'), 'is_oa': x.get('is_oa'),
            'version': x.get('version'),
            'source': (x.get('source') or {}).get('display_name'),
        } for x in locations],
        'crossref_links': cr.get('link', []),
    }
    records.append(record)
    print(json.dumps({'title': title, 'oa_status': record['open_access_status'],
                      'pdf_url': record['pdf_url'], 'locations': record['candidate_locations']},
                     ensure_ascii=False), flush=True)

queries = ['employee training guidance skill development',
           'workforce learning skill allocation agent based',
           'adaptive guidance self regulated learning',
           'multi skill workforce planning learning training']
discovery = []
if (ROOT / 'discovery.json').exists():
    discovery = json.loads((ROOT / 'discovery.json').read_text(encoding='utf-8'))
for query in queries:
    if any(x.get('query') == query for x in discovery):
        continue
    url = 'https://api.openalex.org/works?' + urllib.parse.urlencode({'search': query, 'per_page': 6})
    response, stamp = get_json(url)
    items = response.get('results', [])
    discovery.append({'query': query, 'url': url, 'checked_at': stamp,
                      'reported_count': response.get('meta', {}).get('count'),
                      'results': [{'title': x.get('title'), 'doi': x.get('doi'),
                                   'year': x.get('publication_year'),
                                   'source': ((x.get('primary_location') or {}).get('source') or {}).get('display_name'),
                                   'abstract': abstract_from_index(x.get('abstract_inverted_index'))}
                                  for x in items]})
    print(json.dumps({'query': query, 'papers': [(x.get('title'), x.get('publication_year')) for x in items]},
                     ensure_ascii=False), flush=True)

for record in records:
    if record['doi'] == '10.1007/s11573-022-01090-z':
        repository = 'https://www.econstor.eu/handle/10419/309949'
        record['pdf_url'] = 'https://www.econstor.eu/bitstream/10419/309949/1/s11573-022-01090-z.pdf'
        record['source_platforms'] = list(dict.fromkeys(record['source_platforms'] + ['econstor']))
        stamp = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
        record['field_sources']['pdf_url'] = [evidence('econstor', repository, stamp, 'page_text')]
        if not any(x.get('platform') == 'econstor' for x in record['field_sources']['full_text_status']):
            record['field_sources']['full_text_status'].append(evidence('econstor', repository, stamp, 'page_text'))
        record['jel_codes'] = ['M11']
        record['field_sources']['jel_codes'] = [evidence('econstor', 'https://www.econstor.eu/handle/10419/309949', stamp, 'page_text')]

for filename, data in [('records.json', records), ('discovery.json', discovery), ('query_log.json', LOG)]:
    (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

prior_dois = set()
if (ROOT / 'download_manifest.json').exists():
    prior_dois = {r['doi'] for r in json.loads((ROOT / 'download_manifest.json').read_text(encoding='utf-8'))
                  if r.get('download_status') == 'downloaded'}
(ROOT / 'download_queue.json').write_text(json.dumps(
    [r for r in records if r.get('full_text_status') == 'open_pdf' and r['doi'] not in prior_dois],
    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

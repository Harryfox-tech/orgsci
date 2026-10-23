"""Join checked primary-source access notes with API metadata; no PDF download."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'search_records'
NOW = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')

records = json.loads((ROOT / 'records.json').read_text(encoding='utf-8'))
primary = {
    '10.1287/mnsc.2020.3727': (
        'author_website', 'https://ipeirotis.org/wp-content/uploads/2020/06/mnsc.2020.3727.pdf',
        'A*: published PDF parsed on web; Algorithm 1, sections 5.1 and 6.2 checked; not locally downloaded'),
    '10.1287/mnsc.2023.01373': (
        'publisher', 'https://pubsonline.informs.org/doi/10.1287/mnsc.2023.01373',
        'B: official abstract; IZA 2024 working-paper entry exists but full formal-model review not completed'),
    '10.1287/orsc.2022.16738': (
        'publisher', 'https://pubsonline.informs.org/doi/10.1287/orsc.2022.16738',
        'A*: open HTML abstract, introduction and discussion checked'),
    '10.1145/3630106.3658929': (
        'official_conference', 'https://facctconference.org/static/papers24/facct24-44.pdf',
        'A*: formal paper section 2, Example 2.1 and section 2.1 checked on web'),
    '10.1145/3604915.3608817': (
        'university_repository', 'https://biblio.ugent.be/publication/01HBRHT17WDBN3P9KEABD0XEJ6',
        'B: official repository abstract and version entries; author code README checked, not run'),
    '10.1109/ACCESS.2024.3390229': (
        'author_repository', 'https://github.com/aida-ugent/ReCon',
        'B/C: author README confirms follow-up publication and code association; full paper not audited'),
    '10.1002/hrm.22192': (
        'publisher', 'https://onlinelibrary.wiley.com/doi/10.1002/hrm.22192',
        'A*: abstract and sections 4-5 checked; qualitative study, not a randomized feedback intervention'),
    '10.1093/qje/qjag017': (
        'publisher', 'https://academic.oup.com/qje/article/141/3/1871/8537773',
        'A*: abstract, introduction and conclusion checked; not a skill-guidance RCT'),
    '10.5465/annals.2016.0117': (
        'publisher', 'https://journals.aom.org/doi/abs/10.5465/annals.2016.0117',
        'B: publisher abstract; complete theoretical model not assessed'),
    '10.1093/restud/rdy059': (
        'publisher', 'https://academic.oup.com/restud/article/86/4/1411/5115940',
        'A*: abstract and introduction checked; occupational search advice rather than skill-production treatment'),
    '10.1016/j.euroecorev.2025.105238': (
        'publisher', 'https://doi.org/10.1016/j.euroecorev.2025.105238',
        'A*: primary-source results and conclusion checked via indexed publisher text; repository PDF available'),
    '10.5465/amj.2023.0311': (
        'publisher', 'https://journals.aom.org/doi/10.5465/amj.2023.0311', 'B: publisher abstract'),
    '10.1287/orsc.2020.14214': (
        'publisher', 'https://pubsonline.informs.org/doi/10.1287/orsc.2020.14214', 'B: publisher abstract'),
    '10.1287/orsc.2023.1688': (
        'publisher', 'https://pubsonline.informs.org/doi/10.1287/orsc.2023.1688', 'B: publisher abstract'),
    '10.1177/001979397602900204': (
        'publisher', 'https://journals.sagepub.com/doi/abs/10.1177/001979397602900204',
        'C: 1976 bibliographic page only; cobweb discussion checked separately in author 2005 paper'),
}


def source(platform, url, kind='page_text', note=None):
    value = {'platform': platform, 'source_url': url, 'checked_at': NOW, 'evidence_type': kind}
    if note:
        value['note'] = note
    return value


for record in records:
    platform, url, scope = primary[record['doi']]
    record['primary_source_url'] = url
    record['reading_scope'] = scope
    record['source_platforms'] = list(dict.fromkeys(record['source_platforms'] + [platform]))
    record['field_sources']['reading_scope'] = [source(platform, url, note=scope)]
    if record['doi'] in {'10.1287/mnsc.2020.3727', '10.1145/3630106.3658929'}:
        record['pdf_url'] = url
        record['full_text_status'] = 'open_pdf'
        record['field_sources']['pdf_url'] = [source(platform, url)]
        record['field_sources']['full_text_status'].append(source(platform, url))

preprints = [
    {
        'title': 'A Job I Like or a Job I Can Get: Designing Job Recommender Systems Using Field Experiments',
        'authors': ['Guillaume Bied', 'Philippe Caillou', 'Bruno Crépon', 'Christophe Gaillac', 'Elia Pérennes', 'Michèle Sebag'],
        'year': 2026, 'arxiv_id': '2603.21699v1', 'venue': 'arXiv',
        'publication_type': 'preprint', 'publication_status': 'preprint',
        'primary_source_url': 'https://arxiv.org/abs/2603.21699',
        'source_platforms': ['arxiv'], 'full_text_status': 'unknown', 'pdf_url': None,
        'reading_scope': 'A*: arXiv v1 HTML, abstract and section 2.7; known HTML text access is recorded independently of the PDF-status enum',
    },
    {
        'title': 'Learning the Distribution Map in Reverse Causal Performative Prediction',
        'authors': ['Daniele Bracale', 'Subha Maity', 'Moulinath Banerjee', 'Yuekai Sun'],
        'year': 2024, 'arxiv_id': '2405.15172v1', 'venue': 'arXiv',
        'publication_type': 'preprint', 'publication_status': 'preprint-version-reviewed',
        'primary_source_url': 'https://arxiv.org/abs/2405.15172',
        'source_platforms': ['arxiv'], 'full_text_status': 'unknown', 'pdf_url': None,
        'reading_scope': 'A*: arXiv v1 HTML section 2 and Example 2.2; latest journal publication status not inferred',
    },
    {
        'title': 'The Geometry of Learning Under AI Delegation',
        'authors': ['Lingxiao Huang', 'Nisheeth K. Vishnoi'], 'year': 2026,
        'venue': 'Cowles Foundation Discussion Paper 2499', 'arxiv_id': None,
        'publication_type': 'working-paper', 'publication_status': 'working-paper',
        'primary_source_url': 'https://cowles.yale.edu/sites/default/files/2026-03/d2499.pdf',
        'source_platforms': ['cowles_yale'], 'full_text_status': 'open_pdf',
        'pdf_url': 'https://cowles.yale.edu/sites/default/files/2026-03/d2499.pdf',
        'reading_scope': 'A*: abstract, model overview and conclusions checked in official working paper; not locally downloaded',
    },
]

for record in preprints:
    platform = record['source_platforms'][0]
    url = record['primary_source_url']
    record.update(doi=None, fetched_at=NOW[:10], abstract=None, jel_codes=[], study_type=None,
                  sample_size=None, population=None, geography=None, open_access_status='unknown',
                  download_status='not_requested', pdf_verification_status='unverified', paper_identity_status='unverified')
    record['field_sources'] = {field: [source(platform, url)] for field in
                               ['title', 'authors', 'year', 'venue', 'publication_type', 'full_text_status', 'open_access_status']}
    if record['pdf_url']:
        record['field_sources']['pdf_url'] = [source(platform, url)]
    record['missing_fields'] = {field: 'Not extracted; no value inferred from topic or access.' for field in
                                ['doi', 'abstract', 'jel_codes', 'study_type', 'sample_size', 'population', 'geography']}
    records.append(record)

assert len(records) == 18
(ROOT / 'verified_records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'records': len(records), 'doi_records': 15, 'working_paper_records': 3,
                  'local_pdf_downloads': 0, 'finalized_at': NOW}))

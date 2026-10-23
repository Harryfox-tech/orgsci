"""Join actual downloads and explicit identity checks; never equate OA with retrieval."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK / 'academic_search_followup'
PAPERS = TASK.parents[2] / 'outputs' / 'academic_search_20261020' / 'papers'
STAMP = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def normalized(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', value).lower())


records = json.loads((ROOT / 'records.json').read_text(encoding='utf-8'))
downloads = {}
for name in ['download_manifest.json', 'econstor_download_manifest.json']:
    for row in json.loads((ROOT / name).read_text(encoding='utf-8')):
        if row.get('download_status') == 'downloaded':
            downloads[row['doi']] = row

checks = []
for record in records:
    doi = record['doi']
    if doi not in downloads:
        continue
    download = downloads[doi]
    pdf = PAPERS / download['filename']
    actual_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert actual_hash == download['sha256'], pdf
    reader = PdfReader(pdf)
    opening = '\n'.join(p.extract_text() or '' for p in reader.pages[:2])
    compact = normalized(opening)
    assert normalized(record['title']) in compact, pdf
    if doi == '10.1016/j.ejor.2014.10.038':
        assert all(token in compact for token in ['bruecker', 'bergh', 'beli', 'demeulemeester'])
        assert len(reader.pages) == 40 and 'KBI_1411' in opening
        version = 'KU Leuven KBI_1411 working paper; not the 16-page journal layout'
        study = 'literature review and classification'
        scope = 'Opening title/authors; PDF pp.14-15 and 19-21; working-paper version retained.'
    else:
        assert all(token in compact for token in ['heuser', 'letmathe', 'schinner'])
        assert doi in opening and len(reader.pages) == 33
        version = 'Published journal version with one EconStor cover page'
        study = 'mixed-integer optimization computational study'
        scope = 'PDF pp.1-2 identity; pp.10-11 methods, journal pp.1101-1102; 600 scenarios are not employees.'
    for field in ['download_status', 'download_error', 'download_source', 'final_url',
                  'content_type', 'checked_at', 'byte_length', 'sha256', 'http_status',
                  'retry_after', 'download_error_code', 'pdf_verification_status']:
        record[field] = download.get(field)
    record['local_pdf_path'] = str(pdf.resolve())
    record['paper_identity_status'] = 'matched'
    record['local_document_version'] = version
    record['study_type'] = study
    record['missing_fields'].pop('study_type', None)
    record['missing_fields']['sample_size'] = 'No empirical participant sample extracted; review or computational model.'
    source_url = download['final_url']
    pdf_evidence = {'platform': download['download_source'], 'source_url': source_url,
                    'checked_at': STAMP, 'evidence_type': 'pdf_text', 'note': scope}
    record['field_sources']['paper_identity_status'] = [pdf_evidence]
    record['field_sources']['study_type'] = [pdf_evidence]
    record['field_sources']['local_pdf_path'] = [{
        'platform': download['download_source'], 'source_url': source_url,
        'checked_at': STAMP, 'evidence_type': 'download_response',
        'note': 'Local persistent copy SHA-256 equals the parser-validated downloaded file.'}]
    checks.append({'doi': doi, 'title': record['title'], 'local_pdf_path': str(pdf.resolve()),
                   'pages': len(reader.pages), 'sha256': actual_hash,
                   'pdf_verification_status': download['pdf_verification_status'],
                   'paper_identity_status': 'matched', 'version': version,
                   'scope': scope, 'checked_at': STAMP})

assert len(checks) == 2
for filename, data in [('verified_records.json', records), ('identity_checks.json', checks)]:
    (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'records': len(records), 'downloaded_and_identity_matched': len(checks)}, ensure_ascii=False))

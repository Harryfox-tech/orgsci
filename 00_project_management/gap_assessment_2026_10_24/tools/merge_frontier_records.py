"""Combine Crossref records and explicitly page-verified frontier records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'neighbor_records.json').read_text(encoding='utf-8'))
for item in json.loads((ROOT / 'manual_frontier_records.json').read_text(encoding='utf-8')):
    record = {key: value for key, value in item.items() if key not in ['source_url', 'source_platform', 'inspection']}
    record.update(source_platforms=[item['source_platform']], fetched_at='2026-10-24',
                  abstract=None, citation_count=None, open_access_status=None,
                  full_text_status='unknown', download_status='not_requested',
                  missing_fields={'abstract': '不导出逐字摘要；证据范围见inspection_scope。',
                                  'citation_count': '本轮未查询引用数。',
                                  'open_access_status': '未独立审核开放许可。'},
                  inspection_scope=item['inspection'])
    if not item.get('doi'):
        record['missing_fields']['doi'] = '本轮未核实正式DOI；保留已核实的论文/仓储标识。'
    evidence = dict(platform=item['source_platform'], source_url=item['source_url'],
                    checked_at='2026-10-24T02:39:23Z', evidence_type='page_text',
                    note=item['inspection'] + ' 时间为本轮人工元数据核验记录时间。')
    record['field_sources'] = {key: [evidence] for key in ['title', 'authors', 'year', 'publication_date', 'publication_type', 'venue', 'full_text_status']}
    if not any((r.get('doi') and r.get('doi').lower() == (record.get('doi') or '').lower()) or r['title'] == record['title'] for r in records):
        records.append(record)
(ROOT / 'combined_neighbor_records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'combined_records': len(records)}))

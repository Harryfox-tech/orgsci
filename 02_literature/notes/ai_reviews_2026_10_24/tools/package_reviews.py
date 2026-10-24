"""Render the curated review catalogue from verified metadata and manual evidence."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = json.loads((ROOT / 'records.json').read_text(encoding='utf-8'))
    coverage = {x['review_id']: x for x in json.loads((ROOT / 'source_coverage.json').read_text(encoding='utf-8'))}
    sections = {
        'A': '一、AI＋招聘与人员甄选（5篇）',
        'B': '二、AI＋人才管理、能力治理与组织治理（9篇）',
        'C': '三、AI＋能力评估、人才发展与工作反馈（8篇）',
        'D': '四、跨情境补充：教育中的AI反馈元分析（2篇）',
    }
    lines = ['# AI＋招聘／人才治理／能力评估反馈：24篇综述目录', '',
             '检索核验日期：2026-10-24。以2025—2026年更新为主，补充必要的基础综述。', '',
             '这是一份定向检索与阅读导航，不是24篇全文精读，也不是穷尽性系统综述。篇数均为相应作者报告，不是本项目重新筛选得到。', '',
             '“核验”指本轮实际检查的摘要、方法或版本信息；“阅读用途／局限”是整理者的评估，不是已证实的新理论。没有确认的检索日期与数量明确留空。', '']
    bib = []
    last = None
    for r in records:
        x = coverage[r['review_id']]
        if r['review_id'][0] != last:
            last = r['review_id'][0]
            lines += ['## ' + sections[last], '']
        evidence = {'platform': 'publisher_or_author', 'source_url': x['source_url'],
                    'checked_at': '2026-10-24T02:19:56Z', 'evidence_type': 'page_text',
                    'note': x['inspection'] + '；时间为本轮人工来源记录复核时间，原网页响应时间未逐条保存。'}
        r['study_type'] = x['study_type']
        r['review_corpus_size'] = x['review_corpus_size']
        r['review_coverage'] = x['coverage']
        r['inspection_scope'] = x['inspection']
        r['access_note'] = x['access']
        for field in ['study_type', 'review_corpus_size', 'review_coverage', 'inspection_scope', 'access_note']:
            r['field_sources'][field] = [evidence]
        if x.get('full_text_status_override'):
            r['full_text_status'] = x['full_text_status_override']
            r['field_sources']['full_text_status'] = [evidence]
        if x.get('date_note'):
            r['date_resolution_note'] = x['date_note']
        if r['review_corpus_size'] is None:
            r['missing_fields']['review_corpus_size'] = '本轮未从已检查的来源确认；不可据页数或参考文献条数补填。'
        authors = '; '.join(r['authors'])
        venue = r['venue']
        if r.get('volume'):
            venue += ', ' + r['volume']
        if r.get('issue'):
            venue += '(' + r['issue'] + ')'
        if r.get('pages'):
            venue += ': ' + r['pages']
        elif r.get('article_number'):
            venue += ': ' + r['article_number']
        lines += [f"### {r['review_id']}｜{r['title']}", '',
                  f"{authors}（{r['year']}）。{venue}。", '',
                  f"- 论文：[DOI／正式版本](https://doi.org/{r['doi']})；[本轮核验来源]({x['source_url']})。",
                  f"- 综述类型：{x['study_type']}。",
                  f"- 语料与时间：{str(x['review_corpus_size']) + ' ' + x.get('corpus_unit', '') + '；' if x['review_corpus_size'] is not None else ''}{x['coverage']}。",
                  f"- 阅读用途：{x['use']}", f"- 证据边界：{x['limit']}",
                  f"- 本轮核验：{x['inspection']}。", f"- 全文状态：{x['access']}。"]
        if x.get('additional_source_url'):
            lines += [f"- 补充入口：[作者版本或正式版]({x['additional_source_url']})。"]
        if x.get('date_note'):
            lines += [f"- 年份／版本说明：{x['date_note']}"]
        lines += ['']
        fields = {'title': r['title'], 'author': ' and '.join(r['authors']), 'year': str(r['year']),
                  'doi': r['doi'], 'url': 'https://doi.org/' + r['doi']}
        fields['booktitle' if r['publication_type'] == 'book-chapter' else 'journal'] = r['venue']
        for k in ['volume', 'issue', 'pages']:
            if r.get(k):
                fields['number' if k == 'issue' else k] = r[k].replace('-', '--') if k == 'pages' else r[k]
        fields['note'] = 'Date and version distinctions: see the curated catalogue (checked 2026-10-24).'
        kind = 'incollection' if r['publication_type'] == 'book-chapter' else 'article'
        bib.append('@' + kind + '{' + r['review_id'] + '_' + str(r['year']) + ',\n' +
                   ',\n'.join('  ' + k + ' = {' + v + '}' for k, v in fields.items()) + '\n}')
    (ROOT / 'records_enriched.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / '01_三条主线综述清单.md').write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    (ROOT / 'references.bib').write_text('\n\n'.join(bib) + '\n', encoding='utf-8')
    print(json.dumps({'curated_records': len(records), 'report': '01_三条主线综述清单.md'}, ensure_ascii=False))


if __name__ == '__main__':
    main()

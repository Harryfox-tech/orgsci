"""Convert an official O*NET subset and typeset the weekly report; no simulation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    '13-1071.00': 'Human Resources Specialists',
    '15-1252.00': 'Software Developers',
    '15-2031.00': 'Operations Research Analysts',
}
EXPECTED_HASH = 'D6832C9C195742524A9E48598D962140AAA499C2F78046D4BE3AF0B69F2686BE'


def convert_data(raw: Path) -> dict:
    checksum = hashlib.sha256(raw.read_bytes()).hexdigest().upper()
    if checksum != EXPECTED_HASH:
        raise ValueError('Official source hash differs; inspect before generating data.')
    indexed = defaultdict(dict)
    with raw.open(encoding='utf-8-sig', newline='') as source:
        for row in csv.DictReader(source, delimiter='\t'):
            role = row['O*NET-SOC Code']
            if role in ROLES and row['Scale ID'] in {'IM', 'LV'}:
                key = (role, row['Element ID'])
                if row['Scale ID'] in indexed[key]:
                    raise ValueError(f'Duplicate input scale: {key}')
                indexed[key][row['Scale ID']] = row
    output = []
    for (role, skill), scales in sorted(indexed.items()):
        if set(scales) != {'IM', 'LV'}:
            raise ValueError(f'Incomplete scale pair: {role}/{skill}')
        im, lv = scales['IM'], scales['LV']
        importance, level = float(im['Data Value']), float(lv['Data Value'])
        assert 1 <= importance <= 5 and 0 <= level <= 7
        valid = (im['Recommend Suppress'] != 'Y'
                 and lv['Recommend Suppress'] != 'Y'
                 and lv['Not Relevant'] != 'Y')
        output.append({
            'onet_version': '30.0', 'occupation_code': role,
            'occupation_title': ROLES[role], 'skill_id': skill,
            'skill_name': im['Element Name'], 'importance_raw': importance,
            'level_raw': level, 'importance_rescaled': (importance - 1) / 4,
            'level_proxy_0_1': level / 7 if valid else '',
            'eligible_for_proxy': valid,
            'importance_suppress': im['Recommend Suppress'],
            'level_suppress': lv['Recommend Suppress'],
            'level_not_relevant': lv['Not Relevant'],
            'importance_sample_n': im['N'], 'level_sample_n': lv['N'],
            'importance_standard_error': im['Standard Error'],
            'level_standard_error': lv['Standard Error'],
            'importance_date': im['Date'], 'level_date': lv['Date'],
            'importance_source': im['Domain Source'], 'level_source': lv['Domain Source'],
        })
    totals = {
        role: sum(r['importance_rescaled'] for r in output
                  if r['occupation_code'] == role and r['eligible_for_proxy'])
        for role in ROLES
    }
    for row in output:
        total = totals[row['occupation_code']]
        if total <= 0:
            raise ValueError('No usable within-role weights.')
        row['weight_within_role'] = (row['importance_rescaled'] / total
                                     if row['eligible_for_proxy'] else 0)
    counts = {role: sum(r['occupation_code'] == role for r in output) for role in ROLES}
    assert counts == {role: 35 for role in ROLES}, counts
    for role in ROLES:
        assert abs(sum(r['weight_within_role'] for r in output
                       if r['occupation_code'] == role) - 1) < 1e-10
    destination = ROOT / 'data' / 'onet30_three_roles_skills.csv'
    with destination.open('w', encoding='utf-8-sig', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    metadata = {
        'retrieved_on': '2026-10-20', 'source_version': 'O*NET 30.0',
        'source_url': 'https://www.onetcenter.org/dl_files/database/db_30_0_text/Skills.txt',
        'source_sha256': checksum,
        'attribution': 'U.S. Department of Labor, Employment and Training Administration; O*NET 30.0 Database',
        'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'rows': len(output), 'rows_per_occupation': counts,
        'eligible_proxy_rows': sum(r['eligible_for_proxy'] for r in output),
        'changes': ['Select 3 occupations', 'Join IM and LV by occupation and skill',
                    'Add linear scale proxies and within-role weights',
                    'Keep quality flags and exclude flagged rows from derived proxies'],
        'not_included': ['Employee abilities', 'Job counts', 'Hiring thresholds',
                         'Training participation', 'Training costs', 'Learning rates'],
        'not_a_simulation_result': True,
    }
    (ROOT / 'data' / 'source_metadata.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return metadata


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'(https?://[^\s]+)',
                  lambda m: '<link href="' + m.group(1) + '">' + m.group(1) + '</link>', text)
    return text


def render_report(output_name: str = '彭诗清_选题一_任务报告_Clark全文更新.pdf') -> tuple[Path, int, Path]:
    pdfmetrics.registerFont(TTFont('TaskCJK', r'C:\Windows\Fonts\msyh.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('TaskCJKBold', r'C:\Windows\Fonts\msyhbd.ttc', subfontIndex=0))
    pdfmetrics.registerFontFamily('TaskCJK', normal='TaskCJK', bold='TaskCJKBold')
    base = dict(fontName='TaskCJK', textColor=colors.black, wordWrap='CJK',
                splitLongWords=True, allowWidows=0, allowOrphans=0)
    styles = {
        'title': ParagraphStyle('title', fontSize=20, leading=29, spaceAfter=13, **base),
        'h2': ParagraphStyle('h2', fontSize=14, leading=21, spaceBefore=13,
                             spaceAfter=7, keepWithNext=True, **base),
        'h3': ParagraphStyle('h3', fontSize=11.7, leading=18, spaceBefore=9,
                             spaceAfter=5, keepWithNext=True, **base),
        'body': ParagraphStyle('body', fontSize=10.2, leading=17, spaceAfter=7, **base),
        'cell': ParagraphStyle('cell', fontSize=8.8, leading=13.8, spaceAfter=0, **base),
        'head': ParagraphStyle('head', fontSize=8.8, leading=13.8,
                              spaceAfter=0, fontName='TaskCJKBold',
                              textColor=colors.black, wordWrap='CJK'),
        'ref': ParagraphStyle('ref', fontSize=8.7, leading=14, spaceAfter=7, **base),
    }
    if Path(output_name).name != output_name or not output_name.lower().endswith('.pdf'):
        raise ValueError('PDF name must be a plain .pdf filename within the task directory.')
    destination = ROOT / output_name
    doc = SimpleDocTemplate(str(destination), pagesize=A4,
                            rightMargin=45, leftMargin=45, topMargin=40, bottomMargin=43,
                            title='选题一仿真规则与前置数据核验报告', author='彭诗清')
    lines = (ROOT / '01_选题一仿真规则与前置数据核验报告.md').read_text(encoding='utf-8').splitlines()
    story, paragraph = [], []
    in_refs = False

    def flush():
        if paragraph:
            style = styles['ref'] if in_refs else styles['body']
            story.append(Paragraph(inline(' '.join(paragraph)), style))
            paragraph.clear()

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            flush()
        elif line.startswith('# '):
            flush()
            story.append(Paragraph(inline(line[2:]), styles['title']))
        elif line.startswith('## '):
            flush()
            if line[3:] == '参考文献与数据入口':
                in_refs = True
            story.append(Paragraph(inline(line[3:]), styles['h2']))
        elif line.startswith('### '):
            flush()
            story.append(Paragraph(inline(line[4:]), styles['h3']))
        elif line.startswith('|'):
            flush()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                row = [c.strip() for c in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in row):
                    table_lines.append(row)
                index += 1
            index -= 1
            count = len(table_lines[0])
            ratios = {2: [0.30, 0.70], 3: [0.20, 0.36, 0.44],
                      4: [0.23, 0.25, 0.25, 0.27]}[count]
            cells = [[Paragraph(inline(c), styles['head' if r == 0 else 'cell'])
                      for c in row] for r, row in enumerate(table_lines)]
            table = Table(cells, colWidths=[doc.width * x for x in ratios],
                          repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.45, colors.HexColor('#D9D9D9')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EEF3')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ]))
            story.extend([table, Spacer(1, 10)])
        else:
            paragraph.append(line)
        index += 1
    flush()

    def page_number(canvas, _doc):
        canvas.setFont('TaskCJK', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawRightString(A4[0] - 45, 24, str(_doc.page))

    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(destination))
    qa = Path(tempfile.gettempdir()) / 'orgsci_peng_task_20261020' / 'report_qa'
    qa.mkdir(parents=True, exist_ok=True)
    for number in range(len(pdf)):
        page = pdf[number]
        page.render(scale=1.5).to_pil().save(qa / f'page-{number+1:02}.png')
    pages = len(pdf)
    pdf.close()
    return destination, pages, qa


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', required=True, type=Path)
    parser.add_argument('--pdf-name', default='彭诗清_选题一_任务报告_Clark全文更新.pdf')
    args = parser.parse_args()
    metadata = convert_data(args.raw)
    output, page_count, qa = render_report(args.pdf_name)
    print(json.dumps({'data_rows': metadata['rows'], 'pdf': str(output),
                      'pages': page_count, 'qa': str(qa)}, ensure_ascii=False))

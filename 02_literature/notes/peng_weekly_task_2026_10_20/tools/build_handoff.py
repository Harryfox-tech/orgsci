"""Typeset and verify the task-scoped handoff; never runs or edits an ABM."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

NOTES = Path(__file__).resolve().parents[2]
PACK = NOTES / 'peng_weekly_handoff_2026_10_22'
QA = Path(tempfile.gettempdir()) / 'orgsci_handoff_20261022_qa'


def inline(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r'`([^`]+)`', r'\1', escaped)
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escaped)
    return re.sub(
        r'https?://[^\s]+',
        lambda match: f'<link href="{match.group(0)}">{match.group(0)}</link>',
        escaped,
    )


def render(stem: str) -> dict:
    base = dict(fontName='HandoffCJK', wordWrap='CJK', textColor=colors.black,
                splitLongWords=True, allowWidows=0, allowOrphans=0)
    styles = {
        'title': ParagraphStyle('title', fontSize=21, leading=30,
                                spaceAfter=12, **base),
        'h2': ParagraphStyle('h2', fontSize=14, leading=22, spaceBefore=9,
                             spaceAfter=8, keepWithNext=True, **base),
        'h3': ParagraphStyle('h3', fontSize=11.5, leading=18, spaceBefore=8,
                             spaceAfter=5, keepWithNext=True, **base),
        'body': ParagraphStyle('body', fontSize=10.6, leading=17,
                               spaceAfter=7, **base),
        'ref': ParagraphStyle('ref', fontSize=9.3, leading=14.8,
                              spaceAfter=6, **base),
        'code': ParagraphStyle('code', fontSize=9, leading=14,
                               leftIndent=7, spaceAfter=4, **base),
        'cell': ParagraphStyle('cell', fontSize=9.1, leading=14,
                               spaceAfter=0, **base),
        'head': ParagraphStyle('head', fontSize=9.1, leading=14,
                               fontName='HandoffBold', wordWrap='CJK',
                               textColor=colors.black),
    }
    source = PACK / f'{stem}.md'
    destination = PACK / f'{stem}.pdf'
    doc = SimpleDocTemplate(
        str(destination), pagesize=A4, leftMargin=44, rightMargin=44,
        topMargin=36, bottomMargin=40, title=stem[3:], author='彭诗清',
    )
    lines = source.read_text(encoding='utf-8').splitlines()
    story, pending = [], []

    def flush():
        if pending:
            value = ' '.join(pending)
            style = styles['ref'] if (
                value.startswith('https://') or
                re.match(r'^[A-Z][A-Za-z, .&()0-9\'-]+\(20\d\d\)', value)
            ) else styles['body']
            story.append(Paragraph(inline(value), style))
            pending.clear()

    index, code = 0, False
    while index < len(lines):
        line = lines[index].strip()
        if line == '<!-- PAGE -->':
            flush()
            story.append(PageBreak())
        elif line.startswith('```'):
            flush()
            code = not code
        elif code:
            if line:
                story.append(Paragraph(inline(line), styles['code']))
        elif not line:
            flush()
        elif line.startswith('# '):
            flush()
            story.append(Paragraph(inline(line[2:]), styles['title']))
        elif line.startswith('## '):
            flush()
            story.append(Paragraph(inline(line[3:]), styles['h2']))
        elif line.startswith('### '):
            flush()
            story.append(Paragraph(inline(line[4:]), styles['h3']))
        elif line.startswith('|'):
            flush()
            rows = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                cells = [value.strip() for value in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', value) for value in cells):
                    rows.append(cells)
                index += 1
            index -= 1
            count = len(rows[0])
            if any(len(row) != count for row in rows):
                raise ValueError(f'Ragged table in {source}')
            ratios = {2: [0.28, 0.72], 3: [0.22, 0.40, 0.38]}[count]
            cells = [[Paragraph(inline(value), styles['head' if r == 0 else 'cell'])
                      for value in row] for r, row in enumerate(rows)]
            table = Table(cells, colWidths=[doc.width * ratio for ratio in ratios],
                          repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), .45, colors.HexColor('#D9D9D9')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EEF3')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.extend([table, Spacer(1, 7)])
        elif re.match(r'^\d+\. ', line):
            flush()
            story.append(Paragraph(inline(line), styles['body']))
        else:
            pending.append(line)
        index += 1
    flush()

    def footer(canvas, document):
        canvas.setFont('HandoffCJK', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawRightString(A4[0] - 44, 20, str(document.page))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    parsed = PdfReader(destination)
    image_dir = QA / stem
    image_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(destination))
    for number in range(len(pdf)):
        page = pdf[number]
        page.render(scale=1.6).to_pil().save(image_dir / f'page-{number + 1:02}.png')
        page.close()
    result = {
        'file': destination.name, 'pages': len(pdf), 'qa': str(image_dir),
        'characters_per_page': [len(page.extract_text()) for page in parsed.pages],
    }
    pdf.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack', action='store_true', help='Validate and package inspected PDFs only.')
    args = parser.parse_args()
    if args.pack:
        package()
        return
    pdfmetrics.registerFont(TTFont('HandoffCJK', r'C:\Windows\Fonts\msyh.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('HandoffBold', r'C:\Windows\Fonts\msyhbd.ttc', subfontIndex=0))
    pdfmetrics.registerFontFamily('HandoffCJK', normal='HandoffCJK', bold='HandoffBold')
    reports = [render(stem) for stem in ['01_本周任务直接回应', '02_规则与文献核验附件']]
    QA.mkdir(parents=True, exist_ok=True)
    (QA / 'render_results.json').write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(reports, ensure_ascii=False, indent=2))


def package():
    source = NOTES / 'peng_weekly_task_2026_10_20'
    original_task = Path(
        r'C:\Users\shiqing peng\.codex\codex-remote-attachments\01a0a394-57f8-76f1-bf40-8a7b0652d4af'
        r'\3B8B65BD-5F4D-456E-A8B7-6850895DFB8A\1-本周Task.docx')
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    copies = [(original_task, PACK / '04_任务原文' / '本周Task.docx')]
    copies += [(source / 'data' / name, PACK / '03_前置数据' / name)
               for name in ['onet30_three_roles_skills.csv', 'source_metadata.json']]
    assert all(digest(a) == digest(b) for a, b in copies), 'A copied source differs.'
    with (PACK / '03_前置数据' / 'onet30_three_roles_skills.csv').open(
        encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 105
    assert sum(row['eligible_for_proxy'] == 'True' for row in rows) == 83
    assert len({(row['occupation_code'], row['skill_id']) for row in rows}) == 105
    roles = sorted({row['occupation_code'] for row in rows})
    for role in roles:
        subset = [row for row in rows if row['occupation_code'] == role]
        assert len(subset) == 35
        assert abs(sum(float(row['weight_within_role']) for row in subset) - 1) < 1e-10
    for row in rows:
        assert abs(float(row['importance_rescaled']) -
                   (float(row['importance_raw']) - 1) / 4) < 1e-10
        if row['eligible_for_proxy'] == 'True':
            assert abs(float(row['level_proxy_0_1']) - float(row['level_raw']) / 7) < 1e-10
        else:
            assert row['level_proxy_0_1'] == '' and float(row['weight_within_role']) == 0
    main_text = (PACK / '01_本周任务直接回应.md').read_text(encoding='utf-8')
    evidence_text = (PACK / '02_规则与文献核验附件.md').read_text(encoding='utf-8')
    assert set(re.findall(r'\b(?:R|N)\d{2}\b', main_text)).issubset(
        set(re.findall(r'\b(?:R|N)\d{2}\b', evidence_text)))
    for name in ['01_本周任务直接回应', '02_规则与文献核验附件']:
        reader = PdfReader(PACK / f'{name}.pdf')
        assert len(reader.pages) == 5
        assert all(page.extract_text().strip() for page in reader.pages)
        assert len(list((QA / name).glob('page-*.png'))) == 5
    metadata_path = PACK / '文件核对清单.json'
    items = []
    for path in sorted(PACK.rglob('*')):
        if path.is_file() and path != metadata_path:
            items.append({'path': path.relative_to(PACK).as_posix(),
                          'bytes': path.stat().st_size, 'sha256': digest(path)})
    assert len(items) == 10, 'Unexpected extra or missing handoff files.'
    metadata = {'packaged_on': '2026-10-22', 'evidence_as_of': '2026-10-20',
                'scope': 'Peng Shiqing, weekly task Topic 1: rule grounding and prerequisite data',
                'not_simulation_results': True,
                'manifest_excludes_itself': True, 'files': items}
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8')
    destination = NOTES / '彭诗清_本周任务提交包_2026-10-22.zip'
    if destination.exists():
        raise FileExistsError('Refusing to replace an existing handoff archive.')
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACK.rglob('*')):
            if path.is_file():
                archive.write(path, arcname=f'彭诗清_本周任务提交包/{path.relative_to(PACK).as_posix()}')
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) == 11
        for entry in items:
            data = archive.read(f"彭诗清_本周任务提交包/{entry['path']}")
            assert hashlib.sha256(data).hexdigest() == entry['sha256']
    print(json.dumps({'archive': str(destination), 'bytes': destination.stat().st_size,
                      'archive_sha256': digest(destination), 'files': 11,
                      'task_original_unchanged': True, 'data_copies_identical': True,
                      'data_rows': len(rows), 'eligible_rows': 83,
                      'weights_and_transforms_validated': True, 'zip_integrity': 'pass'},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

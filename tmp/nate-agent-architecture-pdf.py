from pathlib import Path
from html import escape
import re

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Preformatted, PageBreak, Image, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path('/home/egor/agent-second-brain')
project = ROOT / 'vault/projects/Белянин'
source = project / 'Разбор Нейта — архитектура ИИ-группы.md'
output = project / 'Нейт — архитектура ИИ-группы.pdf'

for name, file in [('Ru', 'DejaVuSans.ttf'), ('Ru-Bold', 'DejaVuSans-Bold.ttf'), ('Ru-Mono', 'DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/' + file))
pdfmetrics.registerFontFamily('Ru', normal='Ru', bold='Ru-Bold', italic='Ru', boldItalic='Ru-Bold')

width, height = A4
margin = 42
usable = width - margin * 2
styles = getSampleStyleSheet()
for name in ['Normal', 'BodyText', 'Title', 'Heading1', 'Heading2']:
    styles[name].fontName = 'Ru'
styles['Title'].fontName = 'Ru-Bold'
styles['Title'].fontSize = 23
styles['Title'].leading = 29
styles['Title'].textColor = HexColor('#153E50')
styles['Title'].spaceAfter = 15
styles['BodyText'].fontSize = 9.3
styles['BodyText'].leading = 14
styles['BodyText'].spaceAfter = 8
styles['BodyText'].textColor = HexColor('#24313B')
for name, size in [('Heading1', 14), ('Heading2', 11)]:
    styles[name].fontName = 'Ru-Bold'
    styles[name].fontSize = size
    styles[name].leading = size + 4
    styles[name].spaceBefore = 13
    styles[name].spaceAfter = 8
    styles[name].textColor = HexColor('#153E50')
    styles[name].keepWithNext = True
styles.add(ParagraphStyle(name='TableRu', fontName='Ru', fontSize=8, leading=11, spaceAfter=1))
styles.add(ParagraphStyle(name='CodeRu', fontName='Ru-Mono', fontSize=8.1, leading=11.5, spaceBefore=6, spaceAfter=10))
styles.add(ParagraphStyle(name='SmallRu', fontName='Ru', fontSize=8, leading=11.5, spaceAfter=8))

def inline(value):
    value = re.sub(r'\[\[([^]|]+)\|([^]]+)\]\]', r'\2', value)
    parts = re.split(r'(\[[^\]]+\]\([^\)]+\)|\*\*[^*]+\*\*|`[^`]+`)', value)
    result = []
    for part in parts:
        match = re.fullmatch(r'\[([^\]]+)\]\(([^\)]+)\)', part)
        if match:
            label, url = match.groups()
            result.append('<link href="' + escape(url, quote=True) + '" color="#176A81">' + escape(label) + '</link>')
        elif part.startswith('`') and part.endswith('`'):
            result.append('<font name="Ru-Mono" size="8">' + escape(part[1:-1]) + '</font>')
        elif part.startswith('**') and part.endswith('**'):
            result.append('<b>' + escape(part[2:-2]) + '</b>')
        else:
            result.append(escape(part))
    return ''.join(result)

lines = source.read_text().split('---\n', 2)[2].strip().splitlines()
flow = []
index = 0
while index < len(lines):
    line = lines[index].strip()
    if not line:
        index += 1
        continue
    if line.startswith('```'):
        code = []
        index += 1
        while index < len(lines) and not lines[index].startswith('```'):
            code.append(lines[index])
            index += 1
        flow.append(Preformatted('\n'.join(code), styles['CodeRu']))
        index += 1
        continue
    if line.startswith('|'):
        rows = []
        while index < len(lines) and lines[index].strip().startswith('|'):
            row = lines[index].strip()
            index += 1
            if re.fullmatch(r'\|[\s:|\-]+\|', row):
                continue
            cells = row.strip('|').split('|')
            rows.append([Paragraph(inline(cell.strip()), styles['TableRu']) for cell in cells])
        count = len(rows[0])
        column_widths = [usable / count] * count
        if count == 2:
            column_widths = [75, usable - 75]
        if count == 4:
            column_widths = [121, (usable - 121) / 3, (usable - 121) / 3, (usable - 121) / 3]
        table = Table(rows, colWidths=column_widths, repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E8F1F4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), .8, HexColor('#A4BBC3')),
            ('LINEBELOW', (0, 1), (-1, -1), .3, HexColor('#DAE2E5')),
            ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        flow.extend([table, Spacer(1, 9)])
        continue
    if line.startswith('# '):
        style, line = styles['Title'], line[2:]
    elif line.startswith('## '):
        style, line = styles['Heading1'], line[3:]
    elif line.startswith('### '):
        style, line = styles['Heading2'], line[4:]
    else:
        style = styles['BodyText']
    flow.append(Paragraph(inline(line), style))
    index += 1

flow.append(PageBreak())
flow.append(Paragraph('Два подтверждения на экране', styles['Heading1']))
for file, title, note in [
    (ROOT / 'vault/projects/Nate Herk/videos/001-every-codex-concept-explained-for-non-coders/frames-timed/frame-00406.jpg',
     'Codex: запущенные помощники, около 29:46',
     'Основная сессия сообщает о пяти отдельных исполнителях; справа видна панель их работы. Источник: DFlELTiSPk8.'),
    (Path('/tmp/nate-kylon-check-3.jpg'),
     'Kylon: реально подключённый Codex, 20:15',
     'Профиль показывает Codex CLI, Kylon CLI и компьютер исполнения. Номер версии относится к записи Нейта. Источник: KZiF2J83zaY.'),
]:
    flow.append(KeepTogether([
        Paragraph(title, styles['Heading2']),
        Image(str(file), width=usable, height=usable * 9 / 16),
        Spacer(1, 5),
        Paragraph(note, styles['SmallRu']),
    ]))

def decorate(canvas, document):
    canvas.setFont('Ru', 8)
    canvas.setFillColor(HexColor('#60727B'))
    canvas.drawString(margin, height - 25, 'Белянин · Архитектуры из материалов Нейта · 20 октября 2026')
    canvas.setStrokeColor(HexColor('#DAE2E5'))
    canvas.line(margin, 33, width - margin, 33)
    canvas.drawString(margin, 21, 'Разбор источников; система для проекта ещё не выбрана')
    canvas.drawRightString(width - margin, 21, str(document.page))

document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=margin,
    leftMargin=margin, topMargin=48, bottomMargin=46,
    title='Нейт — архитектура ИИ-группы для проекта «Белянин»',
    author='Помощник Егора')
document.build(flow, onFirstPage=decorate, onLaterPages=decorate)
print(str(output))
print(f'Размер: {output.stat().st_size} байт')

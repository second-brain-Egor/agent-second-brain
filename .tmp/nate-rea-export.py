from pathlib import Path
import re
import html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

p = Path('vault/projects/Nate Herk/videos/001-i-tested-the-viral-reverse-engineer-anything-skill-what-you-need-to-know')
for name, fn in [('DV', 'DejaVuSans.ttf'), ('DV-Bold', 'DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/' + fn))
pdfmetrics.registerFontFamily('DV', normal='DV', bold='DV-Bold', italic='DV', boldItalic='DV-Bold')
styles = {
    'body': ParagraphStyle('body', fontName='DV', fontSize=9.2, leading=13.4, spaceAfter=7, textColor=colors.HexColor('#202b37')),
    'title': ParagraphStyle('title', fontName='DV-Bold', fontSize=20, leading=25, spaceAfter=16, textColor=colors.HexColor('#16324a')),
    'h2': ParagraphStyle('h2', fontName='DV-Bold', fontSize=12.5, leading=17, spaceBefore=13, spaceAfter=8, keepWithNext=True, textColor=colors.HexColor('#16324a')),
    'table': ParagraphStyle('table', fontName='DV', fontSize=8.2, leading=11.6, spaceAfter=0),
    'caption': ParagraphStyle('caption', fontName='DV', fontSize=9, leading=13, spaceAfter=12),
}

def inline(s):
    values = []
    def link(m):
        label, target = m.groups()
        label = html.escape(label)
        value = f'<link href="{html.escape(target, quote=True)}" color="#24658a">{label}</link>' if target.startswith('https://') else label
        values.append(value)
        return f'ZZLINK{len(values)-1}ZZ'
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, s)
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`([^`]+)`', r'\1', s)
    for i, value in enumerate(values):
        s = s.replace(f'ZZLINK{i}ZZ', value)
    return s

text = re.sub(r'\A---\n.*?\n---\n', '', (p / 'analysis.md').read_text(), flags=re.S)
lines = text.splitlines()
story = []
i = 0
width = 499
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue
    if line.startswith('# '):
        story.append(Paragraph(inline(line[2:]), styles['title']))
        i += 1
        continue
    if line.startswith('## '):
        story.append(Paragraph(inline(line[3:]), styles['h2']))
        i += 1
        continue
    if line.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            i += 1
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            rows.append([Paragraph(inline(c), styles['table']) for c in cells])
        widths = [width*.23, width*.77] if len(rows[0]) == 2 else [width*.21, width*.415, width*.375]
        tab = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
        tab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6eff6')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7f9fb')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), .35, colors.HexColor('#d6e0e8')),
        ]))
        story.extend([tab, Spacer(1, 8)])
        continue
    if re.match(r'^(- |\d+\. )', line):
        story.append(Paragraph(inline(re.sub(r'^- ', '• ', line)), styles['body']))
        i += 1
        continue
    para = [line]
    i += 1
    while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#', '|', '- ')) and not re.match(r'^\d+\. ', lines[i]):
        para.append(lines[i].strip())
        i += 1
    story.append(Paragraph(inline(' '.join(para)), styles['body']))

story.append(PageBreak())
story.append(Paragraph('Ключевые экраны ролика', styles['title']))
for name, caption in [
    ('frame-00015.jpg', 'Herk Recorder и Loom: автор показывает собственную реализацию выбранных функций.'),
    ('доп-09-47.jpg', '09:47. Найденное, предполагаемое и неизвестное: внутреннее устройство записывающего модуля остаётся неизвестным.'),
    ('доп-10-51.jpg', '10:51. 3 205 проверок относятся к DX-Ball. Отдельно показано решение сделать Herk Recorder без нативных дополнений.'),
]:
    story.append(KeepTogether([
        Image(str(p / 'frames' / name), width=width, height=width*720/1280),
        Spacer(1, 6), Paragraph(html.escape(caption), styles['caption']),
    ]))

def page(c, doc):
    c.saveState()
    c.setFont('DV', 8)
    c.setFillColor(colors.HexColor('#657586'))
    c.drawString(48, 27, 'Nate Herk · REA · 14 октября 2026')
    c.drawRightString(547, 27, str(doc.page))
    c.restoreState()

file = p / 'Разбор ролика — REA.pdf'
SimpleDocTemplate(
    str(file), pagesize=(595.28, 841.89), leftMargin=48, rightMargin=48,
    topMargin=43, bottomMargin=46, title='Нейт проверяет REA: разбор ролика',
    author='Материалы проекта Nate Herk',
).build(story, onFirstPage=page, onLaterPages=page)
print(file)

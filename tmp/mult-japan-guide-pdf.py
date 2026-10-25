#!/usr/bin/env python3
"""Сверстать «Механику создания» в PDF без внешнего конвертера Markdown.

Запуск из корня проекта:
    uv run python tmp/mult-japan-guide-pdf.py

Для проверки другого исходника:
    uv run python tmp/mult-japan-guide-pdf.py --source FILE.md --output FILE.pdf

Поддерживаются frontmatter, заголовки, таблицы, списки, цитаты, ссылки,
выделение, разделители и блоки кода. Нужны ReportLab и шрифты DejaVu.
"""

from __future__ import annotations

import argparse
from collections import Counter
from html import escape
from pathlib import Path
import re
from urllib.parse import unquote

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, HRFlowable, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "vault/projects/Мульт Япония"
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 48
TOP = 51
BOTTOM = 49
TEXT_W = PAGE_W - LEFT - RIGHT
INK = colors.HexColor("#26343D")
BLUE = colors.HexColor("#174A60")
LINK = "#176B87"
MUTED = colors.HexColor("#667781")
LINE = colors.HexColor("#D8E2E7")
PALE = colors.HexColor("#EEF4F6")


def register_fonts() -> None:
    font_dir = Path("/usr/share/fonts/truetype/dejavu")
    names = {
        "Guide": "DejaVuSans.ttf",
        "Guide-Bold": "DejaVuSans-Bold.ttf",
        "Guide-Italic": "DejaVuSans-Oblique.ttf",
        "Guide-BoldItalic": "DejaVuSans-BoldOblique.ttf",
        "Guide-Mono": "DejaVuSansMono.ttf",
        "Guide-MonoBold": "DejaVuSansMono-Bold.ttf",
    }
    for name, filename in names.items():
        candidate = font_dir / filename
        if not candidate.is_file():
            if "Italic" in name:
                candidate = font_dir / ("DejaVuSans-Bold.ttf" if "Bold" in name else "DejaVuSans.ttf")
            else:
                raise FileNotFoundError(f"Не найден шрифт: {candidate}")
        pdfmetrics.registerFont(TTFont(name, str(candidate)))
    pdfmetrics.registerFontFamily("Guide", normal="Guide", bold="Guide-Bold",
                                  italic="Guide-Italic", boldItalic="Guide-BoldItalic")
    pdfmetrics.registerFontFamily("Guide-Mono", normal="Guide-Mono", bold="Guide-MonoBold",
                                  italic="Guide-Mono", boldItalic="Guide-MonoBold")


def make_styles() -> dict[str, ParagraphStyle]:
    base = ParagraphStyle(
        "body", fontName="Guide", fontSize=9.5, leading=14.5,
        textColor=INK, alignment=TA_LEFT, spaceAfter=7,
        allowWidows=0, allowOrphans=0, splitLongWords=1,
        uriWasteReduce=0.3,
    )
    styles = {"body": base}
    styles["h2"] = ParagraphStyle(
        "h2", parent=base, fontName="Guide-Bold", fontSize=15,
        leading=20, textColor=BLUE, spaceBefore=19, spaceAfter=10,
        keepWithNext=1,
    )
    styles["h3"] = ParagraphStyle(
        "h3", parent=base, fontName="Guide-Bold", fontSize=11.3,
        leading=16.5, textColor=BLUE, spaceBefore=14, spaceAfter=7,
        keepWithNext=1,
    )
    styles["h4"] = ParagraphStyle(
        "h4", parent=base, fontName="Guide-Bold", fontSize=10,
        leading=14.5, textColor=BLUE, spaceBefore=10, spaceAfter=5,
        keepWithNext=1,
    )
    styles["quote"] = ParagraphStyle(
        "quote", parent=base, leftIndent=12, rightIndent=9,
        borderColor=LINE, borderWidth=0.6, borderPadding=9,
        backColor=PALE, spaceBefore=6, spaceAfter=11,
    )
    styles["table"] = ParagraphStyle(
        "table", parent=base, fontSize=8.1, leading=11.8,
        spaceAfter=0, allowWidows=1, allowOrphans=1,
    )
    styles["table_head"] = ParagraphStyle(
        "table_head", parent=styles["table"], fontName="Guide-Bold",
        textColor=BLUE,
    )
    styles["toc"] = ParagraphStyle(
        "toc_entry", parent=base, fontSize=9.1, leading=13.3,
        leftIndent=0, firstLineIndent=0, rightIndent=29,
        spaceBefore=3, spaceAfter=0, allowWidows=1, allowOrphans=1,
    )
    styles["cover_label"] = ParagraphStyle(
        "cover_label", parent=base, fontName="Guide-Bold", fontSize=10,
        leading=15, textColor=BLUE, spaceAfter=20,
    )
    styles["cover_title"] = ParagraphStyle(
        "cover_title", parent=base, fontName="Guide-Bold", fontSize=29,
        leading=37, textColor=BLUE, spaceAfter=23,
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle", parent=base, fontSize=13, leading=21,
        textColor=MUTED, spaceAfter=20,
    )
    styles["small"] = ParagraphStyle(
        "small", parent=base, fontSize=8.2, leading=12.5, textColor=MUTED,
    )
    return styles


def plain(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]", r"\2", value)
    value = re.sub(r"\[\[([^]]+)\]\]", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    return value.replace("**", "").replace("`", "").replace("__", "").strip()


def slugify(value: str) -> str:
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", plain(value).lower()))


INLINE = re.compile(
    r"(?P<escape>\\[\\`*_{}\[\]()#+.!|>-])"
    r"|(?P<code>`+)(?P<code_text>.+?)(?P=code)"
    r"|\[\[(?P<wiki>[^\]]+)\]\]"
    r"|\[(?P<label>[^\]]+)\]\((?P<url>(?:[^\s()]|\([^)]*\))+)(?:\s+\"[^\"]*\")?\)"
    r"|\*\*(?P<bold>.+?)\*\*|__(?P<bold2>.+?)__"
    r"|(?<!\*)\*(?P<italic>[^*\n]+)\*(?!\*)"
    r"|(?<!\w)_(?P<italic2>[^_\n]+)_(?!\w)"
    r"|(?P<br><br\s*/?>)"
    r"|(?P<auto><https?://[^>]+>)",
    re.IGNORECASE,
)


def inline(value: str, anchors: dict[str, str], depth: int = 0) -> str:
    """Преобразовать только поддержанные элементы, экранируя остальной HTML."""
    if depth > 8:
        return escape(value)
    out: list[str] = []
    pos = 0
    for match in INLINE.finditer(value):
        out.append(escape(value[pos:match.start()]))
        group = match.groupdict()
        if group["escape"]:
            out.append(escape(group["escape"][1:]))
        elif group["code"]:
            out.append('<font name="Guide-Mono" size="8.4">' + escape(group["code_text"]) + '</font>')
        elif group["wiki"]:
            parts = group["wiki"].split("|", 1)
            out.append(inline(parts[-1], anchors, depth + 1))
        elif group["label"] or group["auto"]:
            url = group["url"] or group["auto"][1:-1]
            label = inline(group["label"], anchors, depth + 1) if group["label"] else escape(url)
            if url.startswith("#"):
                bookmark = anchors.get(unquote(url[1:]))
                out.append(f'<link href="#{bookmark}" color="{LINK}">{label}</link>' if bookmark else label)
            elif re.match(r"^(?:https?://|mailto:)", url, re.I):
                out.append(f'<link href="{escape(url, quote=True)}" color="{LINK}">{label}</link>')
            else:
                # Пути к локальным материалам остаются читаемыми подписями.
                out.append(label)
        elif group["bold"] is not None or group["bold2"] is not None:
            out.append("<b>" + inline(group["bold"] or group["bold2"], anchors, depth + 1) + "</b>")
        elif group["italic"] is not None or group["italic2"] is not None:
            out.append("<i>" + inline(group["italic"] or group["italic2"], anchors, depth + 1) + "</i>")
        elif group["br"]:
            out.append("<br/>")
        pos = match.end()
    out.append(escape(value[pos:]))
    return "".join(out)


def read_markdown(source: Path) -> tuple[dict[str, str], list[str]]:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    meta: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        closing = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
        if closing is not None:
            for line in lines[1:closing]:
                if ":" in line and not line.startswith(" "):
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip().strip('"\'')
            lines = lines[closing + 1:]
    return meta, lines


class CodeBlock(Flowable):
    """Моноширинный блок, который переносится по строкам и между страницами."""

    font_name = "Guide-Mono"
    font_size = 7.8
    leading = 11.3
    padding = 10
    spaceBefore = 6
    spaceAfter = 10

    def __init__(self, lines: list[str], *, wrapped: bool = False):
        super().__init__()
        self.raw_lines = lines or [""]
        self.wrapped = wrapped
        self.lines: list[str] = []

    def wrap(self, availWidth: float, availHeight: float) -> tuple[float, float]:
        self.width = availWidth
        inside = max(30, availWidth - 2 * self.padding)
        if self.wrapped:
            self.lines = self.raw_lines
        else:
            self.lines = []
            for raw in self.raw_lines:
                raw = raw.expandtabs(4)
                if pdfmetrics.stringWidth(raw, self.font_name, self.font_size) <= inside:
                    self.lines.append(raw)
                    continue
                prefix = " " * min(len(raw) - len(raw.lstrip()) + 2, 12)
                while pdfmetrics.stringWidth(raw, self.font_name, self.font_size) > inside:
                    lo, hi = 1, len(raw)
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if pdfmetrics.stringWidth(raw[:mid], self.font_name, self.font_size) <= inside:
                            lo = mid
                        else:
                            hi = mid - 1
                    # Сохраняем все символы; по возможности переносим на пробеле.
                    cut = raw.rfind(" ", max(1, int(lo * 0.65)), lo + 1)
                    cut = cut + 1 if cut > 0 else lo
                    self.lines.append(raw[:cut])
                    raw = prefix + raw[cut:]
                self.lines.append(raw)
        self.height = 2 * self.padding + len(self.lines) * self.leading
        return self.width, self.height

    def split(self, availWidth: float, availHeight: float) -> list[Flowable]:
        self.wrap(availWidth, availHeight)
        count = int((availHeight - 2 * self.padding) // self.leading)
        if count < 2:
            return []
        if count >= len(self.lines):
            return [self]
        # Не оставляем единственную строку на следующей странице.
        if len(self.lines) - count == 1 and count > 2:
            count -= 1
        return [CodeBlock(self.lines[:count], wrapped=True), CodeBlock(self.lines[count:], wrapped=True)]

    def draw(self) -> None:
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F3F6F8"))
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=1)
        canvas.setFillColor(INK)
        text = canvas.beginText(self.padding, self.height - self.padding - self.font_size)
        text.setFont(self.font_name, self.font_size)
        text.setLeading(self.leading)
        for line in self.lines:
            text.textLine(line)
        canvas.drawText(text)
        canvas.restoreState()


HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")
LIST = re.compile(r"^(\s*)([-+*]|\d+[.)])\s+(.+)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
RULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")


def table_cells(line: str) -> list[str]:
    """Разделитель | внутри inline-code или с обратной косой чертой не разрезаем."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, current = [], []
    in_code = False
    escaped = False
    for char in line:
        if escaped:
            current.extend(["\\", char])
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "`":
            in_code = not in_code
            current.append(char)
        elif char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def is_table_rule(line: str) -> bool:
    cells = table_cells(line)
    return len(cells) > 1 and all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells)


class GuideDocument(BaseDocTemplate):
    def __init__(self, filename: str, title: str, **kwargs):
        super().__init__(filename, pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
                         topMargin=TOP, bottomMargin=BOTTOM, title=title,
                         author="Помощник Егора", subject="Проект «Мульт Япония»",
                         pageCompression=1, **kwargs)
        frame = Frame(LEFT, BOTTOM, TEXT_W, PAGE_H - TOP - BOTTOM,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                      id="body")
        self.addPageTemplates(PageTemplate(id="guide", frames=[frame], onPage=self.decorate))

    def beforeDocument(self) -> None:
        self.canv.setTitle(self.title)
        self.canv.setAuthor("Помощник Егора")
        self.canv.showOutline()
        self._outline_root_seen = False

    def decorate(self, canvas, document) -> None:
        canvas.saveState()
        if document.page == 1:
            canvas.setFillColor(BLUE)
            canvas.rect(LEFT, PAGE_H - 93, 52, 4, fill=1, stroke=0)
        else:
            canvas.setFillColor(MUTED)
            canvas.setFont("Guide", 7.3)
            canvas.drawString(LEFT, PAGE_H - 29, "МУЛЬТ ЯПОНИЯ")
            canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 29, "Механика создания")
            canvas.setStrokeColor(LINE)
            canvas.setLineWidth(0.5)
            canvas.line(LEFT, PAGE_H - 37, PAGE_W - RIGHT, PAGE_H - 37)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(LEFT, 35, PAGE_W - RIGHT, 35)
        canvas.setFont("Guide", 7.4)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 23, "Проект «Мульт Япония» · Механика создания")
        canvas.drawRightString(PAGE_W - RIGHT, 23, str(document.page))
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        if not hasattr(flowable, "bookmark_key"):
            return
        key = flowable.bookmark_key
        title = flowable.heading_title
        level = flowable.heading_level
        self.canv.bookmarkPage(key)
        if level == 0:
            self._outline_root_seen = True
        # PDF запрещает перескакивать на второй уровень без первого.
        outline_level = level if self._outline_root_seen else 0
        self.canv.addOutlineEntry(title, key, level=outline_level, closed=False)
        if getattr(flowable, "include_in_toc", False):
            self.notify("TOCEntry", (0, escape(title), self.page, key))


def make_table(rows: list[list[str]], anchors: dict[str, str], styles) -> Table:
    count = max(map(len, rows))
    for row in rows:
        row.extend([""] * (count - len(row)))
    # Длинные колонки получают больше места, но короткая остаётся читаемой.
    scores = []
    for column in range(count):
        lengths = sorted(len(plain(row[column])) for row in rows)
        typical = lengths[min(len(lengths) - 1, int(0.75 * len(lengths)))]
        scores.append(max(12, min(100, typical)) ** 0.45)
    weights = [score / sum(scores) for score in scores]
    floor = 0.17 if count <= 4 else 0.10
    for _ in range(4):
        weights = [max(floor, weight) for weight in weights]
        weights = [weight / sum(weights) for weight in weights]
    widths = [TEXT_W * weight for weight in weights]
    data = [[Paragraph(inline(cell, anchors), styles["table_head" if i == 0 else "table"])
             for cell in row] for i, row in enumerate(rows)]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT",
                  splitByRow=1, splitInRow=1, spaceBefore=5, spaceAfter=11)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EEF2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFB")]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#A8C1CC")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def parse_body(lines: list[str], styles) -> list[Flowable]:
    anchors: dict[str, str] = {}
    heading_info: dict[int, tuple[str, str, int]] = {}
    slugs: Counter[str] = Counter()
    fence_open = None
    skipped_title = False
    for i, line in enumerate(lines):
        fence = FENCE.match(line)
        if fence:
            if fence_open is None:
                fence_open = fence.group(1)[0]
            elif fence.group(1)[0] == fence_open:
                fence_open = None
            continue
        match = HEADING.match(line) if fence_open is None else None
        if not match:
            continue
        depth, heading = len(match.group(1)), match.group(2)
        if depth == 1 and not skipped_title:
            skipped_title = True
            continue
        slug = slugify(heading)
        serial = slugs[slug]
        slugs[slug] += 1
        if serial:
            slug += f"-{serial}"
        key = f"section-{i}"
        if depth <= 3:
            anchors[slug] = key
        heading_info[i] = (key, heading, depth)

    def special(i: int) -> bool:
        line = lines[i]
        return bool(HEADING.match(line) or FENCE.match(line) or LIST.match(line)
                    or RULE.match(line) or line.lstrip().startswith(">")
                    or (i + 1 < len(lines) and "|" in line and is_table_rule(lines[i + 1])))

    flow: list[Flowable] = []
    i = 0
    skipped_title = False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            code = []
            i += 1
            while i < len(lines) and not re.match(r"^\s*" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*$", lines[i]):
                code.append(lines[i])
                i += 1
            flow.append(CodeBlock(code))
            i += 1
            continue
        heading = HEADING.match(line)
        if heading:
            depth = len(heading.group(1))
            if depth == 1 and not skipped_title:
                skipped_title = True
                i += 1
                continue
            key, text, depth = heading_info[i]
            style = styles["h2" if depth <= 2 else "h3" if depth == 3 else "h4"]
            paragraph = Paragraph(inline(text, anchors), style)
            if depth <= 3:
                paragraph.bookmark_key = key
                paragraph.heading_title = plain(text)
                paragraph.heading_level = 0 if depth <= 2 else 1
                paragraph.include_in_toc = depth <= 2
            flow.append(paragraph)
            i += 1
            continue
        if i + 1 < len(lines) and "|" in line and is_table_rule(lines[i + 1]):
            rows = [table_cells(line)]
            i += 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i] and not HEADING.match(lines[i]):
                rows.append(table_cells(lines[i]))
                i += 1
            flow.append(make_table(rows, anchors, styles))
            continue
        if RULE.match(line):
            flow.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=9, spaceAfter=12))
            i += 1
            continue
        if line.lstrip().startswith(">"):
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            flow.append(Paragraph(inline(" ".join(quote), anchors), styles["quote"]))
            continue
        item = LIST.match(line)
        if item:
            indent, marker, body = item.groups()
            level = min(5, len(indent.expandtabs(4)) // 2)
            bullet = "•" if marker in "-+*" else marker
            check = re.match(r"\[([ xX])\]\s*(.*)", body)
            if check:
                bullet, body = ("☑" if check.group(1).lower() == "x" else "□"), check.group(2)
            i += 1
            continuation = [body]
            while i < len(lines) and lines[i].strip() and not special(i):
                continuation.append(lines[i].strip())
                i += 1
            style = ParagraphStyle(
                f"item_{level}", parent=styles["body"], leftIndent=19 + 13 * level,
                bulletIndent=13 * level, bulletFontName="Guide", bulletFontSize=9.0,
                spaceAfter=5,
            )
            flow.append(Paragraph(inline(" ".join(continuation), anchors), style, bulletText=bullet))
            continue
        paragraph = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not special(i):
            paragraph.append(lines[i].strip())
            i += 1
        flow.append(Paragraph(inline(" ".join(paragraph), anchors), styles["body"]))
    return flow


def build(source: Path, output: Path) -> int:
    if not source.is_file():
        raise FileNotFoundError(f"Исходный документ ещё не создан: {source}")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Папка назначения не существует: {output.parent}")
    register_fonts()
    styles = make_styles()
    metadata, lines = read_markdown(source)
    title = next((plain(m.group(2)) for line in lines
                  if (m := HEADING.match(line)) and len(m.group(1)) == 1),
                 metadata.get("title", "Механика создания"))
    if not any(HEADING.match(line) and line.lstrip().startswith("## ") for line in lines):
        raise ValueError("Для оглавления документу нужен хотя бы один заголовок второго уровня (##).")
    flow: list[Flowable] = [
        Spacer(1, 95),
        Paragraph("ПРОЕКТ «МУЛЬТ ЯПОНИЯ»", styles["cover_label"]),
        Paragraph(escape(title), styles["cover_title"]),
        HRFlowable(width=95, thickness=2.3, color=BLUE, hAlign="LEFT", spaceAfter=25),
        Paragraph("Подробное руководство<br/>по созданию проекта", styles["cover_subtitle"]),
        Spacer(1, 38),
        Paragraph("Порядок работы, структура системы, инструкции<br/>и проверка результатов.", styles["small"]),
    ]
    date = metadata.get("updated") or metadata.get("date") or metadata.get("created")
    if date:
        flow.extend([Spacer(1, 20), Paragraph("Дата документа: " + escape(date), styles["small"])])
    flow.extend([PageBreak(), Paragraph("Содержание", styles["h2"]),
                 Paragraph("Нажмите на название раздела или номер страницы для перехода. "
                           "В панели закладок PDF также доступны подразделы.", styles["small"]),
                 Spacer(1, 9)])
    toc = TableOfContents()
    toc.levelStyles = [styles["toc"]]
    toc.dotsMinLevel = 0
    toc.tableStyle = TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])
    flow.extend([toc, PageBreak()])
    flow.extend(parse_body(lines, styles))
    temporary = output.with_name(output.name + ".part")
    document = GuideDocument(str(temporary), title=title)
    try:
        document.multiBuild(flow, maxPasses=8)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return document.page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=PROJECT / "Механика создания.md")
    parser.add_argument("--output", type=Path, default=PROJECT / "Механика создания.pdf")
    args = parser.parse_args()
    pages = build(args.source.resolve(), args.output.resolve())
    print(f"Готово: {args.output.resolve()}")
    print(f"Страниц: {pages}; размер: {args.output.stat().st_size:,} байт")


if __name__ == "__main__":
    main()

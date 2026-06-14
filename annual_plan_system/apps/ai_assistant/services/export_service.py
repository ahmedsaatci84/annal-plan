from io import BytesIO
from pathlib import Path
import re

try:
    import arabic_reshaper
except ImportError:  # pragma: no cover
    arabic_reshaper = None

try:
    from bidi.algorithm import get_display
except ImportError:  # pragma: no cover
    get_display = None
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


_ARABIC_FONT_PATH = Path(r'C:\Windows\Fonts\tahoma.ttf')
_ARABIC_FONT_NAME = 'Tahoma'
_FONT_REGISTERED = False


def _register_font():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont(_ARABIC_FONT_NAME, str(_ARABIC_FONT_PATH)))
    _FONT_REGISTERED = True


def _contains_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text or ''))


def _shape(text):
    if text is None:
        return ''
    value = str(text)
    if not value.strip():
        return ''
    if _contains_arabic(value):
        if arabic_reshaper and get_display:
            try:
                return get_display(arabic_reshaper.reshape(value))
            except Exception:
                return value
    return value


def build_analysis_pdf_bytes(export_title, meta_lines, analysis_text):
    _register_font()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=_shape(export_title),
    )

    title_style = ParagraphStyle(
        'title',
        fontName=_ARABIC_FONT_NAME,
        fontSize=16,
        leading=22,
        alignment=1,
    )
    meta_style = ParagraphStyle(
        'meta',
        fontName=_ARABIC_FONT_NAME,
        fontSize=10,
        leading=14,
        alignment=2,
    )
    body_style = ParagraphStyle(
        'body',
        fontName=_ARABIC_FONT_NAME,
        fontSize=11,
        leading=16,
        alignment=2,
    )

    story = [
        Paragraph(_shape(export_title), title_style),
        Spacer(1, 0.4 * cm),
    ]

    for line in meta_lines:
        story.append(Paragraph(_shape(line), meta_style))

    story.append(Spacer(1, 0.45 * cm))

    text = analysis_text or 'No analysis content.'
    for chunk in text.split('\n'):
        if not chunk.strip():
            story.append(Spacer(1, 0.15 * cm))
            continue
        story.append(Paragraph(_shape(chunk), body_style))

    doc.build(story)
    return buffer.getvalue()

from io import BytesIO
from pathlib import Path
import re
from xml.sax.saxutils import escape

import arabic_reshaper
from bidi.algorithm import get_display
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from apps.core.middleware import AuditLogMiddleware, log_action
from apps.plans.services.completion_service import compute_plan_summary


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
        try:
            return get_display(arabic_reshaper.reshape(value))
        except Exception:
            return value
    return value


def _points(value):
    if value is None:
        return ['—']
    text = str(value).replace('\r\n', '\n').replace('\r', '\n').strip()
    if not text:
        return ['—']
    text = text.replace('•', '\n•')
    lines = []
    for raw in text.split('\n'):
        line = re.sub(r'^\s*[-*•]+\s*', '', raw).strip()
        if line:
            lines.append(line)
    return lines or ['—']


def _para(text, style):
    return Paragraph(_shape(text), style)


def _points_para(value, style):
    lines = _points(value)
    body = '<br/>'.join(escape(_shape(line)) for line in lines)
    return Paragraph(body, style)


def _table(rows, widths):
    table = Table(rows, colWidths=widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d5e8f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9aa0a6')),
        ('FONTNAME', (0, 0), (-1, -1), _ARABIC_FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return table


def export_plan_pdf(request, plan):
    _register_font()

    width, _ = A4
    margin = 1.5 * cm
    content_width = width - 2 * margin

    styles = {
        'title': ParagraphStyle('title', fontName=_ARABIC_FONT_NAME, fontSize=16, leading=22, alignment=1),
        'h2': ParagraphStyle('h2', fontName=_ARABIC_FONT_NAME, fontSize=12.5, leading=18, alignment=2, spaceBefore=10, spaceAfter=6),
        'normal': ParagraphStyle('normal', fontName=_ARABIC_FONT_NAME, fontSize=10, leading=15, alignment=2),
        'small': ParagraphStyle('small', fontName=_ARABIC_FONT_NAME, fontSize=9, leading=13, alignment=2),
    }

    summary = compute_plan_summary(plan)
    goals = plan.goals.prefetch_related('activities').order_by('sequence')
    risks = plan.risks.all()
    swot = getattr(plan, 'swot', None)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=f'الخطة السنوية - {plan.plan_year}',
    )

    elements = []
    elements.append(_para('الخطة السنوية', styles['title']))
    elements.append(_para(f'{plan.formation.name_ar} - {plan.plan_year}', styles['title']))
    elements.append(Spacer(1, 0.35 * cm))

    elements.append(_para('أولاً: معلومات الخطة', styles['h2']))
    info_rows = [
        [_shape('البند'), _shape('البيانات')],
        [_shape('التشكيل'), _shape(plan.formation.name_ar)],
        [_shape('السنة'), str(plan.plan_year)],
        [_shape('الحالة'), _shape(plan.get_status_display())],
        [_shape('مدير التشكيل'), _shape(plan.manager_name)],
        [_shape('منظم الاستمارة'), _shape(plan.organizer_name)],
    ]
    if plan.endorsement_ref_no:
        info_rows.append([_shape('رقم الإشارة'), str(plan.endorsement_ref_no)])
    if plan.endorsement_date:
        info_rows.append([_shape('تاريخ المصادقة'), str(plan.endorsement_date)])
    if plan.endorsement_text:
        info_rows.append([_shape('نص المصادقة'), _points_para(plan.endorsement_text, styles['small'])])
    elements.append(_table(info_rows, [content_width * 0.35, content_width * 0.65]))

    elements.append(_para('ثانياً: تحليل SWOT', styles['h2']))
    swot_rows = [
        [_shape('المحور'), _shape('النقاط')],
        [_shape('نقاط القوة'), _points_para(getattr(swot, 'strengths', ''), styles['small'])],
        [_shape('نقاط الضعف'), _points_para(getattr(swot, 'weaknesses', ''), styles['small'])],
        [_shape('الفرص'), _points_para(getattr(swot, 'opportunities', ''), styles['small'])],
        [_shape('التهديدات'), _points_para(getattr(swot, 'threats', ''), styles['small'])],
    ]
    elements.append(_table(swot_rows, [content_width * 0.25, content_width * 0.75]))

    elements.append(_para('ثالثاً: الأهداف والأنشطة', styles['h2']))
    for goal in goals:
        elements.append(_para(f'{goal.code} - {goal.title}', styles['normal']))
        elements.append(_para(f'KPI: {goal.kpi_type} | النوع: {goal.goal_type}', styles['small']))
        acts = list(goal.activities.all())
        if acts:
            rows = [[
                _shape('الحالة'), _shape('منجز %'), _shape('مخطط %'), _shape('النهاية'),
                _shape('البداية'), _shape('المسؤول'), _shape('النشاط'), _shape('الرمز')
            ]]
            for act in acts:
                rows.append([
                    _shape(act.get_activity_status_display()),
                    f'{act.actual_completion_pct}%',
                    f'{act.planned_completion_pct}%',
                    str(act.end_date),
                    str(act.start_date),
                    _shape(act.responsible_formation.name_ar) if act.responsible_formation else '—',
                    _shape(act.title),
                    str(act.code),
                ])
            elements.append(_table(rows, [content_width * x for x in [0.10, 0.08, 0.08, 0.11, 0.11, 0.14, 0.30, 0.08]]))
        else:
            elements.append(_para('لا توجد أنشطة', styles['small']))
        elements.append(Spacer(1, 0.2 * cm))

    elements.append(_para('رابعاً: ملخص الأهداف', styles['h2']))
    summary_rows = [[
        _shape('%'), _shape('متأخرة'), _shape('غير منجزة'), _shape('منقولة'), _shape('قيد التنفيذ'),
        _shape('مكتملة'), _shape('الكلي'), _shape('العنوان'), _shape('الهدف')
    ]]
    for g in summary.get('goals', []):
        summary_rows.append([
            f"{g.get('completion_pct', 0)}%",
            str(g.get('delayed', 0)),
            str(g.get('not_completed', 0)),
            str(g.get('rolled_over', 0)),
            str(g.get('in_progress', 0)),
            str(g.get('completed', 0)),
            str(g.get('total', 0)),
            _shape(g['goal'].title),
            str(g['goal'].code),
        ])
    summary_rows.append([
        f"{summary.get('overall_pct', 0)}%", '—', '—', '—', '—',
        str(summary.get('total_completed', 0)),
        str(summary.get('total_activities', 0)),
        _shape('الإجمالي'),
        '',
    ])
    elements.append(_table(summary_rows, [content_width * x for x in [0.07, 0.08, 0.10, 0.08, 0.10, 0.09, 0.08, 0.32, 0.08]]))

    elements.append(_para('خامساً: المخاطر', styles['h2']))
    if risks:
        risk_rows = [[_shape('#'), _shape('الخطر'), _shape('الاحتمالية'), _shape('التأثير'), _shape('المعالجة')]]
        for i, risk in enumerate(risks, start=1):
            risk_rows.append([
                str(i),
                _points_para(risk.risk_description, styles['small']),
                _shape(risk.get_probability_display()),
                _points_para(risk.impact_description, styles['small']),
                _points_para(risk.treatment_plan, styles['small']),
            ])
        elements.append(_table(risk_rows, [content_width * x for x in [0.06, 0.30, 0.10, 0.24, 0.30]]))
    else:
        elements.append(_para('لا توجد مخاطر مسجلة.', styles['small']))

    elements.append(_para('سادساً: التوصيات', styles['h2']))
    elements.append(_points_para(plan.recommendations, styles['normal']))

    doc.build(elements)

    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'EXPORT', 'AnnualPlan', plan, ip_address=ip)

    filename = f'annual_plan_{plan.plan_year}.pdf'
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


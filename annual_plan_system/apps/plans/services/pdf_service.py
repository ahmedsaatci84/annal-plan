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


def _section_header(text, width, style, bg_color='#0f4c81'):
    table = Table([[_para(text, style)]], colWidths=[width])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('BOX', (0, 0), (-1, -1), 0.7, colors.HexColor(bg_color)),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


def _table(rows, widths, header_bg='#dbeafe', header_text='#0f2940', grid='#d0d7de', stripe='#f8fafc'):
    table = Table(rows, colWidths=widths)
    commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(header_text)),
        ('FONTNAME', (0, 0), (-1, -1), _ARABIC_FONT_NAME),
        ('FONTNAME', (0, 0), (-1, 0), _ARABIC_FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.65, colors.HexColor(grid)),
        ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor(grid)),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    if len(rows) > 2:
        commands.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(stripe)]))
    table.setStyle(TableStyle(commands))
    return table


def export_plan_pdf(request, plan):
    _register_font()

    width, _ = A4
    margin = 1.5 * cm
    content_width = width - 2 * margin

    styles = {
        'cover_title': ParagraphStyle('cover_title', fontName=_ARABIC_FONT_NAME, fontSize=18, leading=24, alignment=1, textColor=colors.white),
        'cover_subtitle': ParagraphStyle('cover_subtitle', fontName=_ARABIC_FONT_NAME, fontSize=11, leading=16, alignment=1, textColor=colors.HexColor('#ecfeff')),
        'section': ParagraphStyle('section', fontName=_ARABIC_FONT_NAME, fontSize=12, leading=17, alignment=2, textColor=colors.white),
        'normal': ParagraphStyle('normal', fontName=_ARABIC_FONT_NAME, fontSize=10, leading=15, alignment=2, textColor=colors.HexColor('#0f172a')),
        'small': ParagraphStyle('small', fontName=_ARABIC_FONT_NAME, fontSize=9, leading=13, alignment=2, textColor=colors.HexColor('#1f2937')),
        'muted': ParagraphStyle('muted', fontName=_ARABIC_FONT_NAME, fontSize=8.5, leading=12.5, alignment=2, textColor=colors.HexColor('#475569')),
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
    cover = Table([
        [_para('الخطة السنوية', styles['cover_title'])],
        [_para(f'{plan.formation.name_ar} - {plan.plan_year}', styles['cover_subtitle'])],
    ], colWidths=[content_width])
    cover.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0b4f6c')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#0b4f6c')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#1a759f')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cover)
    elements.append(Spacer(1, 0.35 * cm))

    elements.append(_section_header('أولاً: معلومات الخطة', content_width, styles['section'], bg_color='#1d4e89'))
    elements.append(Spacer(1, 0.12 * cm))
    info_rows = [
        [_shape('البيانات'), _shape('البند')],
        [_shape(plan.formation.name_ar) ,_shape('التشكيل') ],
        [str(plan.plan_year), _shape('السنة')],
        [_shape(plan.get_status_display()), _shape('الحالة')],
        [_shape(plan.manager_name), _shape('مدير التشكيل')],
        [_shape(plan.organizer_name), _shape('منظم الاستمارة')],
    ]
    if plan.endorsement_ref_no:
        info_rows.append([str(plan.endorsement_ref_no), _shape('رقم الإشارة')])
    if plan.endorsement_date:
        info_rows.append([str(plan.endorsement_date), _shape('تاريخ المصادقة')])
    if plan.endorsement_text:
        info_rows.append([_points_para(plan.endorsement_text, styles['small']), _shape('نص المصادقة')])
    elements.append(_table(info_rows, [content_width * 0.65, content_width * 0.35], header_bg='#dbeafe', header_text='#0f3b65', grid='#bfd0e5', stripe='#f8fbff'))
    elements.append(Spacer(1, 0.18 * cm))

    elements.append(_section_header('ثانياً: تحليل SWOT', content_width, styles['section'], bg_color='#0f766e'))
    elements.append(Spacer(1, 0.12 * cm))
    swot_rows = [
        [_shape('النقاط'), _shape('المحور')],
        [_points_para(getattr(swot, 'strengths', ''), styles['small']), _shape('نقاط القوة')],
        [_points_para(getattr(swot, 'weaknesses', ''), styles['small']), _shape('نقاط الضعف')],
        [_points_para(getattr(swot, 'opportunities', ''), styles['small']), _shape('الفرص')],
        [_points_para(getattr(swot, 'threats', ''), styles['small']), _shape('التهديدات')],
    ]
    elements.append(_table(swot_rows, [content_width * 0.75, content_width * 0.25], header_bg='#ccfbf1', header_text='#115e59', grid='#99d7cc', stripe='#f2fffb'))
    elements.append(Spacer(1, 0.18 * cm))

    elements.append(_section_header('ثالثاً: الأهداف والأنشطة', content_width, styles['section'], bg_color='#1e40af'))
    elements.append(Spacer(1, 0.12 * cm))
    for goal in goals:
        elements.append(_para(f'{goal.code} - {goal.title}', styles['normal']))
        elements.append(_para(f'KPI: {goal.kpi_type} | النوع: {goal.goal_type}', styles['muted']))
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
            elements.append(_table(rows, [content_width * x for x in [0.10, 0.08, 0.08, 0.11, 0.11, 0.14, 0.30, 0.08]], header_bg='#dbeafe', header_text='#1e3a8a', grid='#c8d5f0', stripe='#f7faff'))
        else:
            elements.append(_para('لا توجد أنشطة', styles['small']))
        elements.append(Spacer(1, 0.22 * cm))

    elements.append(_section_header('رابعاً: ملخص الأهداف', content_width, styles['section'], bg_color='#334155'))
    elements.append(Spacer(1, 0.12 * cm))
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
    elements.append(_table(summary_rows, [content_width * x for x in [0.07, 0.08, 0.10, 0.08, 0.10, 0.09, 0.08, 0.32, 0.08]], header_bg='#e2e8f0', header_text='#334155', grid='#cbd5e1', stripe='#f8fafc'))
    elements.append(Spacer(1, 0.18 * cm))

    elements.append(_section_header('خامساً: المخاطر', content_width, styles['section'], bg_color='#9a3412'))
    elements.append(Spacer(1, 0.12 * cm))
    if risks:
        risk_rows = [[_shape('المعالجة'),
                      _shape('التأثير'),
                      _shape('الاحتمالية'),
                      _shape('الخطر'),
                      _shape('#')                                             
                      ]]
        for i, risk in enumerate(risks, start=1):
            risk_rows.append([                                                    
                   _points_para(risk.treatment_plan, styles['small']),                   
                   _points_para(risk.impact_description, styles['small']),
                   _shape(risk.get_probability_display()),
                  _points_para(risk.risk_description, styles['small']),
                   str(i)                       
            ])
        elements.append(_table(risk_rows, [content_width * x for x in [0.30,0.24,0.10,0.30,0.06]], header_bg='#ffedd5', header_text='#9a3412', grid='#f7c8a0', stripe='#fff9f3'))
    else:
        elements.append(_para('لا توجد مخاطر مسجلة.', styles['small']))

    elements.append(Spacer(1, 0.1 * cm))
    elements.append(_section_header('سادساً: التوصيات', content_width, styles['section'], bg_color='#0f766e'))
    elements.append(Spacer(1, 0.12 * cm))
    elements.append(_points_para(plan.recommendations, styles['normal']))

    doc.build(elements)

    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'EXPORT', 'AnnualPlan', plan, ip_address=ip)

    filename = f'annual_plan_{plan.plan_year}.pdf'
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def export_workflow_log_pdf(request, plan):
    _register_font()

    width, _ = A4
    margin = 1.5 * cm
    content_width = width - 2 * margin

    styles = {
        'cover_title': ParagraphStyle('wf_cover_title', fontName=_ARABIC_FONT_NAME, fontSize=17, leading=22, alignment=1, textColor=colors.white),
        'cover_subtitle': ParagraphStyle('wf_cover_subtitle', fontName=_ARABIC_FONT_NAME, fontSize=10.5, leading=15, alignment=1, textColor=colors.HexColor('#ecfeff')),
        'section': ParagraphStyle('wf_section', fontName=_ARABIC_FONT_NAME, fontSize=11.5, leading=16, alignment=2, textColor=colors.white),
        'small': ParagraphStyle('wf_small', fontName=_ARABIC_FONT_NAME, fontSize=9, leading=12.5, alignment=2, textColor=colors.HexColor('#1f2937')),
    }

    logs = plan.workflow_logs.select_related('performed_by').order_by('-created_at')

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=f'Workflow Log - {plan.plan_year}',
    )

    elements = []
    cover = Table([
        [_para('سجل سير العمل', styles['cover_title'])],
        [_para(f'{plan.formation.name_ar} - {plan.plan_year}', styles['cover_subtitle'])],
    ], colWidths=[content_width])
    cover.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0b4f6c')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#0b4f6c')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#1a759f')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cover)
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(_section_header('تفاصيل السجل', content_width, styles['section'], bg_color='#1d4e89'))
    elements.append(Spacer(1, 0.12 * cm))

    rows = [[
        _shape('التاريخ'),
        _shape('المنفذ بواسطة'),
        _shape('من'),
        _shape('إلى'),
        _shape('التعليق'),
    ]]
    for log in logs:
        actor = log.performed_by.get_full_name() or log.performed_by.username
        rows.append([
            str(log.created_at.strftime('%Y/%m/%d %H:%M')),
            _shape(actor),
            _shape(log.get_from_status_display() if log.from_status else '—'),
            _shape(log.get_to_status_display()),
            _points_para(log.comment, styles['small']),
        ])

    if len(rows) == 1:
        rows.append(['—', '—', '—', '—', _shape('لا توجد سجلات سير عمل')])

    elements.append(
        _table(
            rows,
            [content_width * x for x in [0.18, 0.20, 0.16, 0.16, 0.30]],
            header_bg='#dbeafe',
            header_text='#0f3b65',
            grid='#bfd0e5',
            stripe='#f8fbff',
        )
    )

    doc.build(elements)

    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'EXPORT', 'PlanWorkflowLog', plan, ip_address=ip)

    filename = f'workflow_log_{plan.plan_year}_{plan.pk}.pdf'
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


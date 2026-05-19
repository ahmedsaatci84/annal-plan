from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.plans.models import SwotAnalysis
from apps.plans.services.completion_service import compute_plan_summary
from apps.plans.services.gantt_service import build_gantt_data
from apps.core.middleware import log_action, AuditLogMiddleware


def export_plan_pdf(request, plan):
    try:
        import weasyprint
    except ImportError:
        from django.http import HttpResponseServerError
        return HttpResponseServerError('WeasyPrint غير مثبت. يرجى تشغيل: pip install WeasyPrint')

    swot = getattr(plan, 'swot', None)
    goals = plan.goals.prefetch_related('activities').order_by('sequence')
    risks = plan.risks.all()
    summary = compute_plan_summary(plan)
    gantt = build_gantt_data(plan)

    html_string = render_to_string('plans/pdf/plan_pdf.html', {
        'plan': plan,
        'swot': swot,
        'goals': goals,
        'risks': risks,
        'summary': summary,
        'gantt': gantt,
        'request': request,
    })

    pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'EXPORT', 'AnnualPlan', plan, ip_address=ip)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    filename = f'annual_plan_{plan.formation.code}_{plan.plan_year}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

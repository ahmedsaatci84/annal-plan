import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from apps.ai_assistant.services.analysis_service import (
    build_plan_analysis_context,
    get_accessible_plans_for_user,
)
from apps.ai_assistant.services.export_service import build_analysis_pdf_bytes
from apps.ai_assistant.services.qwen_client import QwenClient, QwenClientError
from apps.plans.models import AnnualPlan


CHAT_SYSTEM_PROMPT = (
    'You are an Arabic-first assistant for government annual planning workflows. '
    'Be concise, practical, and structured. Avoid policy violations. '
    'If user asks for decision authority, remind them that final decisions belong to authorized reviewers.'
)

ANALYSIS_SYSTEM_PROMPT = (
    'You are a planning analysis assistant. Analyze plan data and return:\n'
    '1) top strengths\n'
    '2) top gaps\n'
    '3) risk hot-spots\n'
    '4) prioritized action list (short, practical)\n'
    'Write in Arabic unless user asked otherwise.'
)

LAST_ANALYSIS_SESSION_KEY = 'ai_assistant_last_analysis'


@login_required
def assistant_home(request):
    plans = get_accessible_plans_for_user(request.user)
    client = QwenClient()
    ai_status = client.get_status()
    return render(request, 'ai_assistant/home.html', {
        'plans': plans,
        'chat_response': None,
        'analysis_response': None,
        'chat_prompt': '',
        'selected_plan_id': '',
        'ai_status': ai_status,
    })


@login_required
@require_POST
def assistant_chat(request):
    plans = get_accessible_plans_for_user(request.user)
    client = QwenClient()
    ai_status = client.get_status()
    chat_prompt = (request.POST.get('chat_prompt') or '').strip()
    analysis_response = None
    chat_response = None
    selected_plan_id = ''

    if not ai_status.get('ok'):
        messages.error(request, ai_status.get('message', 'المساعد الذكي غير جاهز حالياً.'))
        return render(request, 'ai_assistant/home.html', {
            'plans': plans,
            'chat_response': chat_response,
            'analysis_response': analysis_response,
            'chat_prompt': chat_prompt,
            'selected_plan_id': selected_plan_id,
            'ai_status': ai_status,
        })

    if not chat_prompt:
        messages.error(request, 'الرجاء إدخال رسالة للدردشة.')
        return render(request, 'ai_assistant/home.html', {
            'plans': plans,
            'chat_response': chat_response,
            'analysis_response': analysis_response,
            'chat_prompt': chat_prompt,
            'selected_plan_id': selected_plan_id,
            'ai_status': ai_status,
        })

    try:
        chat_response = client.chat(CHAT_SYSTEM_PROMPT, chat_prompt)
    except QwenClientError as exc:
        messages.error(request, f'تعذر الاتصال بالمساعد الذكي: {exc}')

    return render(request, 'ai_assistant/home.html', {
        'plans': plans,
        'chat_response': chat_response,
        'analysis_response': analysis_response,
        'chat_prompt': chat_prompt,
        'selected_plan_id': selected_plan_id,
        'ai_status': ai_status,
    })


@login_required
@require_POST
def assistant_analyze_plan(request):
    plans = get_accessible_plans_for_user(request.user)
    client = QwenClient()
    ai_status = client.get_status()
    selected_plan_id = (request.POST.get('plan_id') or '').strip()
    analysis_response = None
    chat_response = None
    chat_prompt = ''

    if not ai_status.get('ok'):
        messages.error(request, ai_status.get('message', 'المساعد الذكي غير جاهز حالياً.'))
        return render(request, 'ai_assistant/home.html', {
            'plans': plans,
            'chat_response': chat_response,
            'analysis_response': analysis_response,
            'chat_prompt': chat_prompt,
            'selected_plan_id': selected_plan_id,
            'ai_status': ai_status,
        })

    if not selected_plan_id:
        messages.error(request, 'يرجى اختيار خطة للتحليل.')
        return render(request, 'ai_assistant/home.html', {
            'plans': plans,
            'chat_response': chat_response,
            'analysis_response': analysis_response,
            'chat_prompt': chat_prompt,
            'selected_plan_id': selected_plan_id,
            'ai_status': ai_status,
        })

    plan = get_object_or_404(AnnualPlan.objects.select_related('formation'), pk=selected_plan_id)
    if not _user_can_access_plan(request.user, plan):
        messages.error(request, 'ليست لديك صلاحية للوصول إلى هذه الخطة.')
        return render(request, 'ai_assistant/home.html', {
            'plans': plans,
            'chat_response': chat_response,
            'analysis_response': analysis_response,
            'chat_prompt': chat_prompt,
            'selected_plan_id': '',
            'ai_status': ai_status,
        })

    context_payload = build_plan_analysis_context(plan)
    user_prompt = (
        'Analyze this annual plan payload and return concise actionable insights:\n\n'
        + json.dumps(context_payload, ensure_ascii=False)
    )

    try:
        analysis_response = client.chat(ANALYSIS_SYSTEM_PROMPT, user_prompt)
        _save_last_analysis(request, plan, analysis_response, client.get_active_model())
    except QwenClientError as exc:
        request.session.pop(LAST_ANALYSIS_SESSION_KEY, None)
        messages.error(request, f'تعذر تشغيل تحليل الخطة: {exc}')

    return render(request, 'ai_assistant/home.html', {
        'plans': plans,
        'chat_response': chat_response,
        'analysis_response': analysis_response,
        'chat_prompt': chat_prompt,
        'selected_plan_id': str(selected_plan_id),
        'ai_status': ai_status,
    })


@login_required
@require_GET
def assistant_export_analysis_json(request):
    payload = _get_last_analysis_payload(request)
    if not payload:
        messages.error(request, 'لا يوجد تحليل محفوظ للتصدير. يرجى تنفيذ تحليل أولاً.')
        return render_assistant_home_with_defaults(request)

    plan = get_object_or_404(AnnualPlan.objects.select_related('formation'), pk=payload['plan_id'])
    if not _user_can_access_plan(request.user, plan):
        messages.error(request, 'ليست لديك صلاحية لتصدير هذا التحليل.')
        return render_assistant_home_with_defaults(request)

    filename = f"ai_analysis_{plan.plan_year}_{plan.id}.json"
    response = JsonResponse(payload, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_GET
def assistant_export_analysis_pdf(request):
    payload = _get_last_analysis_payload(request)
    if not payload:
        messages.error(request, 'لا يوجد تحليل محفوظ للتصدير. يرجى تنفيذ تحليل أولاً.')
        return render_assistant_home_with_defaults(request)

    plan = get_object_or_404(AnnualPlan.objects.select_related('formation'), pk=payload['plan_id'])
    if not _user_can_access_plan(request.user, plan):
        messages.error(request, 'ليست لديك صلاحية لتصدير هذا التحليل.')
        return render_assistant_home_with_defaults(request)

    title = f"AI Analysis Report - {plan.formation.name_ar} - {plan.plan_year}"
    meta_lines = [
        f"Plan ID: {plan.id}",
        f"Formation: {plan.formation.name_ar}",
        f"Year: {plan.plan_year}",
        f"Model: {payload.get('model', '')}",
        f"Generated At: {payload.get('generated_at', '')}",
    ]
    pdf_bytes = build_analysis_pdf_bytes(title, meta_lines, payload.get('analysis_text', ''))
    filename = f"ai_analysis_{plan.plan_year}_{plan.id}.pdf"

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _user_can_access_plan(user, plan):
    profile = user.profile
    if profile.is_admin() or profile.is_reviewer():
        return True
    if not profile.formation_id:
        return False
    return plan.formation_id == profile.formation_id


def _save_last_analysis(request, plan, analysis_text, model_name):
    request.session[LAST_ANALYSIS_SESSION_KEY] = {
        'plan_id': plan.id,
        'formation': plan.formation.name_ar,
        'plan_year': plan.plan_year,
        'status': plan.status,
        'model': model_name,
        'generated_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'analysis_text': analysis_text,
    }


def _get_last_analysis_payload(request):
    payload = request.session.get(LAST_ANALYSIS_SESSION_KEY)
    if isinstance(payload, dict):
        return payload
    return None


def render_assistant_home_with_defaults(request):
    plans = get_accessible_plans_for_user(request.user)
    client = QwenClient()
    ai_status = client.get_status()
    return render(request, 'ai_assistant/home.html', {
        'plans': plans,
        'chat_response': None,
        'analysis_response': None,
        'chat_prompt': '',
        'selected_plan_id': '',
        'ai_status': ai_status,
    })

import json
from urllib import request, error
from urllib.parse import urlparse

from django.conf import settings


class QwenClientError(Exception):
    pass


class QwenClient:
    def __init__(self):
        self.enabled = getattr(settings, 'AI_ASSISTANT_ENABLED', False)
        self.endpoint = getattr(settings, 'AI_ASSISTANT_ENDPOINT', 'http://localhost:11434/api/chat')
        self.model = getattr(settings, 'AI_ASSISTANT_MODEL', 'qwen2.5:7b-instruct')
        self.timeout = getattr(settings, 'AI_ASSISTANT_TIMEOUT', 60)
        self.active_model = self.model

    def get_status(self):
        if not self.enabled:
            return {
                'ok': False,
                'code': 'disabled',
                'message': 'المساعد الذكي معطل من الإعدادات (AI_ASSISTANT_ENABLED=False).',
                'model': self.model,
            }

        try:
            parsed = self._fetch_tags_payload()
        except error.HTTPError as exc:
            return {
                'ok': False,
                'code': 'http_error',
                'message': f'تعذر قراءة حالة Ollama (HTTP {exc.code}).',
                'model': self.model,
            }
        except error.URLError:
            return {
                'ok': False,
                'code': 'unreachable',
                'message': 'لا يمكن الوصول إلى Ollama. تأكد من تشغيل ollama serve.',
                'model': self.model,
            }
        except TimeoutError:
            return {
                'ok': False,
                'code': 'timeout',
                'message': 'انتهت مهلة الاتصال بـ Ollama.',
                'model': self.model,
            }
        except json.JSONDecodeError:
            return {
                'ok': False,
                'code': 'invalid_json',
                'message': 'استجابة غير صالحة من Ollama.',
                'model': self.model,
            }

        models = parsed.get('models') or []
        names = [str(m.get('name', '')).strip().lower() for m in models if isinstance(m, dict)]
        resolved_model = self._resolve_model(models)

        if not resolved_model:
            return {
                'ok': False,
                'code': 'model_missing',
                'message': f'النموذج {self.model} غير موجود ولا يوجد نموذج محلي بديل متاح. نفذ: ollama pull {self.model}',
                'model': self.model,
            }

        self.active_model = resolved_model

        if str(resolved_model).strip().lower() != str(self.model).strip().lower():
            return {
                'ok': True,
                'code': 'ready_fallback',
                'message': f'النموذج {self.model} غير موجود. سيتم استخدام النموذج المحلي {resolved_model} بدلاً منه.',
                'model': resolved_model,
                'configured_model': self.model,
            }

        return {
            'ok': True,
            'code': 'ready',
            'message': f'Ollama جاهز والنموذج {resolved_model} متاح.',
            'model': resolved_model,
        }

    def _build_tags_url(self):
        parsed = urlparse(self.endpoint)
        base = f'{parsed.scheme}://{parsed.netloc}'
        return f'{base}/api/tags'

    def _fetch_tags_payload(self):
        tags_url = self._build_tags_url()
        req = request.Request(tags_url, method='GET')
        with request.urlopen(req, timeout=self.timeout) as resp:
            raw = resp.read().decode('utf-8')
        return json.loads(raw)

    def _resolve_model(self, models):
        names = [str(m.get('name', '')).strip() for m in models if isinstance(m, dict)]
        normalized = {name.lower(): name for name in names if name}
        configured_key = str(self.model).strip().lower()

        if configured_key in normalized:
            return normalized[configured_key]

        fallback_candidates = [
            'qwen2.5:7b-instruct',
            'qwen2.5:latest',
            'llama3.2:latest',
            'llama3.1:latest',
        ]
        for candidate in fallback_candidates:
            candidate_key = candidate.lower()
            if candidate_key in normalized:
                return normalized[candidate_key]

        for name in names:
            lowered = name.lower()
            if 'cloud' not in lowered and 'embedding' not in lowered:
                return name

        return None

    def get_active_model(self):
        return self.active_model

    def chat(self, system_prompt, user_prompt):
        if not self.enabled:
            raise QwenClientError('AI assistant is disabled in settings.')

        try:
            parsed = self._fetch_tags_payload()
        except error.HTTPError as exc:
            raise QwenClientError(f'AI HTTP error: {exc.code}') from exc
        except error.URLError as exc:
            raise QwenClientError('Cannot connect to AI endpoint. Ensure Ollama is running.') from exc
        except TimeoutError as exc:
            raise QwenClientError('AI request timed out.') from exc
        except json.JSONDecodeError as exc:
            raise QwenClientError('Invalid JSON response from AI endpoint.') from exc

        runtime_model = self._resolve_model(parsed.get('models') or [])
        if not runtime_model:
            raise QwenClientError(
                f'Configured model {self.model} is missing and no local fallback model is available.'
            )
        self.active_model = runtime_model

        payload = {
            'model': runtime_model,
            'stream': False,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
        }
        data = json.dumps(payload).encode('utf-8')
        req = request.Request(
            self.endpoint,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode('utf-8')
        except error.HTTPError as exc:
            raise QwenClientError(f'AI HTTP error: {exc.code}') from exc
        except error.URLError as exc:
            raise QwenClientError('Cannot connect to AI endpoint. Ensure Ollama is running.') from exc
        except TimeoutError as exc:
            raise QwenClientError('AI request timed out.') from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise QwenClientError('Invalid JSON response from AI endpoint.') from exc

        message = parsed.get('message', {})
        content = message.get('content', '').strip()
        if not content:
            raise QwenClientError('AI returned an empty response.')

        return content

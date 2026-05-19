from .models import AuditLog


def log_action(user, action, model_name, obj=None, changes=None, ip_address=None):
    """Helper to create an audit log entry."""
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=obj.pk if obj else None,
        object_repr=str(obj) if obj else '',
        changes_json=changes,
        ip_address=ip_address,
    )


class AuditLogMiddleware:
    """
    Middleware that attaches the client IP to the request for audit logging.
    Does not log automatically — views call log_action() explicitly.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

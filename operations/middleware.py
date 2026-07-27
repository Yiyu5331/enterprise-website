from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class SameOriginFrameMiddleware:
    """兼容 SimpleUI 同源 iframe，同时阻止第三方网站嵌入页面。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response


class SuperuserTwoFactorMiddleware:
    """生产环境要求超级管理员完成 TOTP 验证后才能使用后台。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "REQUIRE_SUPERUSER_2FA", False):
            return self.get_response(request)
        user = getattr(request, "user", None)
        path = request.path
        allowed = (
            reverse("admin:login"),
            reverse("admin:logout"),
            reverse("operations:two-factor-setup"),
            reverse("operations:two-factor-verify"),
        )
        if (
            user
            and user.is_authenticated
            and user.is_superuser
            and path.startswith("/admin/")
            and not path.startswith("/admin/jsi18n/")
            and path not in allowed
            and not user.is_verified()
        ):
            target = "operations:two-factor-verify" if user.totpdevice_set.filter(confirmed=True).exists() else "operations:two-factor-setup"
            return redirect(target)
        return self.get_response(request)

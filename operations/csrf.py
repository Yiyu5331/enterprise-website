from django.http import JsonResponse


def csrf_failure(request, reason=""):
    return JsonResponse(
        {"code": "csrf_failed", "message": "安全令牌已失效，请刷新页面后重新提交。"},
        status=403,
        json_dumps_params={"ensure_ascii": False},
    )

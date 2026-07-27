import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import LianxiForm, XunpanForm


def form_error_response(form):
    errors = {
        field: [error["message"] for error in error_list]
        for field, error_list in form.errors.get_json_data().items()
    }
    return JsonResponse(
        {"success": False, "message": "提交信息有误，请检查后重试。", "errors": errors},
        status=400,
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
@require_POST
def create_inquiry(request):
    """接收在线询盘，支持 multipart/form-data 附件上传。"""
    form = XunpanForm(request.POST, request.FILES)
    if not form.is_valid():
        return form_error_response(form)

    inquiry = form.save()
    response = JsonResponse(
        {"success": True, "message": "询盘提交成功。", "id": inquiry.pk},
        status=201,
        json_dumps_params={"ensure_ascii": False},
    )
    response["Deprecation"] = "true"
    response["Link"] = '</api/v1/inquiries/>; rel="successor-version"'
    return response


@csrf_exempt
@require_POST
def create_contact(request):
    """接收联系我们页面提交的 JSON 或普通表单数据。"""
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "请求中的 JSON 格式不正确。"},
                status=400,
                json_dumps_params={"ensure_ascii": False},
            )
    else:
        data = request.POST

    form = LianxiForm(data)
    if not form.is_valid():
        return form_error_response(form)

    contact = form.save()
    response = JsonResponse(
        {"success": True, "message": "留言提交成功。", "id": contact.pk},
        status=201,
        json_dumps_params={"ensure_ascii": False},
    )
    response["Deprecation"] = "true"
    response["Link"] = '</api/v1/contacts/>; rel="successor-version"'
    return response

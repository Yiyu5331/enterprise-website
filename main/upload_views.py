from pathlib import Path

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .content_utils import process_uploaded_image


@staff_member_required
@require_POST
def richtext_image_upload(request, kind):
    permission = "products.change_product" if kind == "products" else "news.change_article"
    if kind not in {"products", "news"} or not request.user.has_perm(permission):
        return JsonResponse({"code": "permission_denied", "message": "没有上传权限。"}, status=403)
    upload = request.FILES.get("image")
    alt = request.POST.get("alt", "")
    if not upload:
        return JsonResponse({"code": "image_required", "message": "请选择图片。"}, status=400)
    try:
        _, web, _ = process_uploaded_image(
            upload,
            prefix=f"{kind}-content",
            thumb_size=(960, 540),
        )
        path = default_storage.save(f"{kind}/content/{Path(web.name).name}", web)
    except Exception as exc:
        return JsonResponse({"code": "invalid_image", "message": str(exc)}, status=400)
    return JsonResponse({"url": default_storage.url(path), "alt": alt})

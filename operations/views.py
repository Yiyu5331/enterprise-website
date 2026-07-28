import base64
import hashlib
import io
import secrets

import qrcode
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from axes.models import AccessAttempt, AccessFailureLog, AccessLog
from django.http import FileResponse, Http404
from django_otp import login as otp_login
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import AuditLog, RecoveryCode
from main.models import Xunpan


def _recovery_hash(code):
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


@staff_member_required
def two_factor_setup(request):
    if not request.user.is_superuser:
        return redirect("admin:index")
    device, _ = TOTPDevice.objects.get_or_create(user=request.user, name="default", defaults={"confirmed": False})
    already_bound = device.confirmed
    recovery_codes = None
    if request.method == "POST" and not already_bound and device.verify_token(request.POST.get("token", "").strip()):
        device.confirmed = True
        device.save(update_fields=("confirmed",))
        RecoveryCode.objects.filter(user=request.user).delete()
        recovery_codes = [f"{secrets.token_hex(2)}-{secrets.token_hex(2)}" for _ in range(10)]
        RecoveryCode.objects.bulk_create([
            RecoveryCode(user=request.user, code_hash=_recovery_hash(code)) for code in recovery_codes
        ])
        otp_login(request, device)
        AuditLog.objects.create(actor=request.user, action="totp_enabled", target_type="user", target_id=str(request.user.pk), summary="超级管理员启用双重验证")
    elif request.method == "POST" and not already_bound:
        messages.error(request, "验证码不正确，请确认手机时间准确后重试。")

    image = qrcode.make(device.config_url)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return render(request, "operations/two_factor_setup.html", {
        "qr_code": base64.b64encode(output.getvalue()).decode("ascii"),
        "secret": device.key,
        "recovery_codes": recovery_codes,
        "already_bound": already_bound,
    })


@staff_member_required
def two_factor_verify(request):
    if not request.user.is_superuser:
        return redirect("admin:index")
    if request.user.is_verified():
        return redirect("admin:index")
    device = request.user.totpdevice_set.filter(confirmed=True).first()
    if not device:
        return redirect("operations:two-factor-setup")
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        verified_device = device if device.verify_token(token) else None
        if not verified_device:
            code_hash = _recovery_hash(token.lower())
            recovery = RecoveryCode.objects.filter(user=request.user, code_hash=code_hash, used_at__isnull=True).first()
            if recovery:
                from django.utils import timezone
                recovery.used_at = timezone.now()
                recovery.save(update_fields=("used_at",))
                verified_device = device
        if verified_device:
            otp_login(request, verified_device)
            AuditLog.objects.create(actor=request.user, action="totp_verified", target_type="user", target_id=str(request.user.pk), summary="双重验证通过")
            return redirect("admin:index")
        messages.error(request, "动态验证码或恢复码不正确。")
    return render(request, "operations/two_factor_verify.html")


@staff_member_required
def private_inquiry_attachment(request, pk):
    inquiry = Xunpan.objects.filter(pk=pk).first()
    if not inquiry or not inquiry.attachment:
        raise Http404
    AuditLog.objects.create(actor=request.user, action="private_attachment_download", target_type="inquiry", target_id=str(pk), summary="下载询盘私有附件")
    return FileResponse(inquiry.attachment.open("rb"), as_attachment=True, filename=inquiry.attachment.name.rsplit("/", 1)[-1])


@staff_member_required
def security_center(request):
    if not request.user.is_superuser:
        return redirect("admin:index")
    return render(request, "operations/security_center.html", {
        "totp_devices": request.user.totpdevice_set.all(),
        "recent_failures": AccessFailureLog.objects.order_by("-attempt_time")[:10],
        "recent_attempts": AccessAttempt.objects.order_by("-attempt_time")[:10],
        "recent_logins": AccessLog.objects.order_by("-attempt_time")[:10],
    })

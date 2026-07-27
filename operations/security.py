import base64
import hashlib
import hmac
import io
import secrets
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from .models import CaptchaChallenge, FormToken


FORM_TOKEN_MAX_AGE = 30 * 60
CAPTCHA_MAX_AGE = timedelta(minutes=5)


class FormSecurityError(Exception):
    def __init__(self, code, message, status_code=400, extra=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "unknown"


def ip_fingerprint(request):
    return hmac.new(
        settings.FORM_SECURITY_KEY.encode("utf-8"),
        client_ip(request).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def issue_form_token(request, kind):
    token = FormToken.objects.create(kind=kind, ip_fingerprint=ip_fingerprint(request))
    return signing.dumps({"id": str(token.pk), "kind": kind}, salt="huali-form-token")


def get_form_token(request, signed_value, kind):
    try:
        payload = signing.loads(signed_value or "", salt="huali-form-token", max_age=FORM_TOKEN_MAX_AGE)
        token = FormToken.objects.select_for_update().get(pk=payload.get("id"))
    except (signing.BadSignature, signing.SignatureExpired, FormToken.DoesNotExist, ValueError, TypeError) as exc:
        raise FormSecurityError("form_token_invalid", "表单已过期，请刷新页面后重试。") from exc
    if payload.get("kind") != kind or token.kind != kind or token.ip_fingerprint != ip_fingerprint(request):
        raise FormSecurityError("form_token_invalid", "表单令牌与当前请求不匹配，请刷新页面后重试。")
    if token.used_at:
        raise FormSecurityError("form_token_reused", "该表单已提交，请刷新页面后重新填写。")
    return token


def captcha_required(request, token, lead_model):
    if timezone.now() - token.created_at < timedelta(seconds=3):
        return True
    if not request.META.get("HTTP_USER_AGENT", "").strip():
        return True
    return lead_model.objects.filter(
        ip_fingerprint=token.ip_fingerprint,
        created_at__gte=timezone.now() - timedelta(minutes=10),
    ).exists()


def _answer_hash(challenge_id, answer):
    value = f"{challenge_id}:{answer}".encode("utf-8")
    return hmac.new(settings.FORM_SECURITY_KEY.encode("utf-8"), value, hashlib.sha256).hexdigest()


def create_captcha(request):
    answer = f"{secrets.randbelow(10000):04d}"
    challenge = CaptchaChallenge.objects.create(
        answer_hash="pending",
        ip_fingerprint=ip_fingerprint(request),
        expires_at=timezone.now() + CAPTCHA_MAX_AGE,
    )
    challenge.answer_hash = _answer_hash(challenge.pk, answer)
    challenge.save(update_fields=("answer_hash",))

    image = Image.new("RGB", (150, 54), "#f4f5f7")
    draw = ImageDraw.Draw(image)
    for _ in range(8):
        x1, y1 = secrets.randbelow(150), secrets.randbelow(54)
        x2, y2 = secrets.randbelow(150), secrets.randbelow(54)
        draw.line((x1, y1, x2, y2), fill="#b8bec7", width=1)
    font = ImageFont.load_default(size=28)
    for index, digit in enumerate(answer):
        draw.text((18 + index * 30, 10 + secrets.randbelow(5)), digit, fill="#20242a", font=font)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return challenge, base64.b64encode(output.getvalue()).decode("ascii")


def validate_captcha(request, captcha_id, answer):
    try:
        with transaction.atomic():
            challenge = CaptchaChallenge.objects.select_for_update().get(pk=captcha_id)
            valid = (
                challenge.used_at is None
                and challenge.expires_at >= timezone.now()
                and challenge.ip_fingerprint == ip_fingerprint(request)
                and hmac.compare_digest(challenge.answer_hash, _answer_hash(challenge.pk, str(answer or "").strip()))
            )
            challenge.used_at = timezone.now()
            challenge.save(update_fields=("used_at",))
    except (CaptchaChallenge.DoesNotExist, ValueError, TypeError) as exc:
        raise FormSecurityError("captcha_invalid", "验证码无效或已过期，请重新获取。") from exc
    if not valid:
        raise FormSecurityError("captcha_invalid", "验证码无效或已过期，请重新获取。")

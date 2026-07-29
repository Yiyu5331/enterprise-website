import re
import uuid
from io import BytesIO
from pathlib import Path

import bleach
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageOps


class ContentStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PUBLISHED = "published", "已发布"
    ARCHIVED = "archived", "归档"


class VerificationStatus(models.TextChoices):
    PENDING = "pending", "待核验"
    VERIFIED = "verified", "已核验"
    REJECTED = "rejected", "已拒绝"


def public_content_allowed(*, is_demo=False, verification_status=VerificationStatus.PENDING):
    """测试模式可展示演示内容，生产模式只展示已核验的真实内容。"""
    from django.conf import settings

    if getattr(settings, "SITE_CONTENT_MODE", "test") == "test":
        return True
    return not is_demo and verification_status == VerificationStatus.VERIFIED


def validate_production_publish(*, status, is_demo, verification_status):
    from django.conf import settings

    if getattr(settings, "SITE_CONTENT_MODE", "test") != "production":
        return
    if status != ContentStatus.PUBLISHED:
        return
    errors = []
    if is_demo:
        errors.append("生产模式不能发布演示内容。")
    if verification_status != VerificationStatus.VERIFIED:
        errors.append("生产模式只能发布已核验内容。")
    if errors:
        raise ValidationError(" ".join(errors))


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_PDF_SIZE = 20 * 1024 * 1024


def validate_image_upload(upload):
    if not upload:
        return
    if upload.size > MAX_IMAGE_SIZE:
        raise ValidationError("图片大小不能超过 5 MB。")
    if Path(upload.name).suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("图片仅支持 JPG、PNG 和 WebP。")
    try:
        upload.seek(0)
        with Image.open(upload) as image:
            if image.format not in ALLOWED_IMAGE_FORMATS:
                raise ValidationError("图片格式不受支持。")
            image.verify()
    except (OSError, ValueError) as exc:
        raise ValidationError("图片文件损坏或格式不正确。") from exc
    finally:
        upload.seek(0)


def validate_pdf_upload(upload):
    if not upload:
        return
    if upload.size > MAX_PDF_SIZE:
        raise ValidationError("PDF 文件大小不能超过 20 MB。")
    if Path(upload.name).suffix.lower() != ".pdf":
        raise ValidationError("产品资料仅支持 PDF。")
    position = upload.tell()
    upload.seek(0)
    signature = upload.read(5)
    upload.seek(position)
    if signature != b"%PDF-":
        raise ValidationError("PDF 文件格式不正确。")


def _safe_image(image):
    image = ImageOps.exif_transpose(image)
    if image.mode not in {"RGB", "RGBA"}:
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
    if image.mode == "RGBA":
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        return background
    return image.convert("RGB")


def _webp_content(image, *, max_edge=None, size=None, focal=(0.5, 0.5)):
    output = image.copy()
    if size:
        output = ImageOps.fit(output, size, method=Image.Resampling.LANCZOS, centering=focal)
    elif max_edge and max(output.size) > max_edge:
        output.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    output.save(buffer, format="WEBP", quality=82, method=6)
    return ContentFile(buffer.getvalue())


def process_uploaded_image(source, *, prefix, thumb_size, focal_x=0.5, focal_y=0.5):
    """重新编码原图并生成网页图与缩略图，返回三个 ContentFile。"""
    validate_image_upload(source)
    source.seek(0)
    with Image.open(source) as opened:
        image = _safe_image(opened)
        image.load()
        token = uuid.uuid4().hex
        original = _webp_content(image)
        web = _webp_content(image, max_edge=1600)
        thumb = _webp_content(
            image,
            size=thumb_size,
            focal=(max(0, min(1, focal_x)), max(0, min(1, focal_y))),
        )
    original.name = f"{prefix}-{token}-original.webp"
    web.name = f"{prefix}-{token}-web.webp"
    thumb.name = f"{prefix}-{token}-thumb.webp"
    return original, web, thumb


ALLOWED_TAGS = {
    "h2", "h3", "h4", "p", "br", "strong", "em", "ul", "ol", "li",
    "blockquote", "a", "img", "figure", "figcaption", "table", "thead",
    "tbody", "tr", "th", "td",
}
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "loading"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
}


def _attribute_filter(tag, name, value):
    if name not in ALLOWED_ATTRIBUTES.get(tag, []):
        return False
    if tag == "img" and name == "src":
        return value.startswith("/media/") or value.startswith("https://")
    if tag == "a" and name == "href":
        return value.startswith(("/", "#", "https://", "mailto:", "tel:"))
    return True


def sanitize_rich_text(value):
    cleaned = bleach.clean(
        value or "",
        tags=ALLOWED_TAGS,
        attributes=_attribute_filter,
        protocols={"https", "mailto", "tel"},
        strip=True,
    )

    def secure_link(match):
        attributes = match.group(1)
        href = re.search(r'href=["\']([^"\']+)', attributes, re.I)
        if href and href.group(1).startswith("https://"):
            attributes = re.sub(r'\s+(target|rel)=["\'][^"\']*["\']', "", attributes, flags=re.I)
            attributes += ' target="_blank" rel="noopener noreferrer"'
        return f"<a{attributes}>"

    cleaned = re.sub(r"<a([^>]*)>", secure_link, cleaned, flags=re.I)
    cleaned = re.sub(r"<img([^>]*)>", lambda m: f'<img{m.group(1)} loading="lazy">' if "loading=" not in m.group(1) else m.group(0), cleaned, flags=re.I)
    return cleaned


def rich_text_to_plain(value):
    text = bleach.clean(value or "", tags=[], strip=True)
    return re.sub(r"\s+", " ", text).strip()


def rich_text_images_have_alt(value):
    for attributes in re.findall(r"<img\s+([^>]+)>", value or "", flags=re.I):
        if not re.search(r'\balt=["\'][^"\']*["\']', attributes, flags=re.I):
            return False
    return True


def delete_field_file(field_file):
    if field_file and field_file.name:
        field_file.delete(save=False)

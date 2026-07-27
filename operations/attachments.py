import io
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


ALLOWED_TYPES = {
    ".pdf": {"application/pdf"},
    ".doc": {"application/msword", "application/octet-stream"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/zip", "application/octet-stream"},
    ".xls": {"application/vnd.ms-excel", "application/octet-stream"},
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/zip", "application/octet-stream"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
}
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024
MAX_EMAIL_ATTACHMENT_SIZE = 20 * 1024 * 1024


class AttachmentScanUnavailable(ValidationError):
    pass


def _read_bytes(uploaded_file):
    uploaded_file.seek(0)
    content = uploaded_file.read()
    uploaded_file.seek(0)
    return content


def _validate_signature(extension, content):
    if extension == ".pdf" and not content.startswith(b"%PDF-"):
        raise ValidationError("PDF 文件结构无效。")
    if extension in {".jpg", ".jpeg"} and not content.startswith(b"\xff\xd8\xff"):
        raise ValidationError("JPG 文件结构无效。")
    if extension == ".png" and not content.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValidationError("PNG 文件结构无效。")
    if extension in {".doc", ".xls"} and not content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        raise ValidationError("Office 文件结构无效。")
    if extension in {".docx", ".xlsx"}:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                names = set(archive.namelist())
        except zipfile.BadZipFile as exc:
            raise ValidationError("Office 文件压缩结构无效。") from exc
        required = "word/document.xml" if extension == ".docx" else "xl/workbook.xml"
        if "[Content_Types].xml" not in names or required not in names:
            raise ValidationError("Office 文件内容与扩展名不匹配。")


def _validate_image(content):
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("图片无法解码或已损坏。") from exc


def _scan_clamav(content):
    if not settings.CLAMAV_ENABLED:
        return "skipped_development"
    try:
        import clamd

        client = clamd.ClamdNetworkSocket(settings.CLAMAV_HOST, settings.CLAMAV_PORT, timeout=8)
        result = client.instream(io.BytesIO(content))
    except Exception as exc:
        raise AttachmentScanUnavailable("病毒扫描服务暂不可用，请移除附件后提交纯文本内容。") from exc
    status, signature = result.get("stream", ("ERROR", "unknown"))
    if status == "FOUND":
        raise ValidationError(f"附件未通过病毒安全检查：{signature}。")
    if status != "OK":
        raise AttachmentScanUnavailable("病毒扫描服务暂不可用，请移除附件后提交纯文本内容。")
    return "clean"


def validate_and_scan_attachment(uploaded_file, *, max_size=MAX_ATTACHMENT_SIZE):
    if not uploaded_file:
        return "not_applicable"
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in ALLOWED_TYPES:
        raise ValidationError("附件仅支持 PDF、Word、Excel、JPG 和 PNG。")
    if uploaded_file.size > max_size:
        raise ValidationError(f"附件大小不能超过 {max_size // 1024 // 1024} MB。")
    content_type = (getattr(uploaded_file, "content_type", "") or "application/octet-stream").lower()
    if content_type not in ALLOWED_TYPES[extension]:
        raise ValidationError("附件 MIME 类型与扩展名不匹配。")
    content = _read_bytes(uploaded_file)
    _validate_signature(extension, content)
    if extension in {".jpg", ".jpeg", ".png"}:
        _validate_image(content)
    return _scan_clamav(content)

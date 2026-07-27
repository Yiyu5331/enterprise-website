import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403,F401


DEBUG = False
SILENCED_SYSTEM_CHECKS = ["security.W002"]  # SimpleUI 需要同源 iframe，由自定义中间件提供 SAMEORIGIN。

required = {
    "DJANGO_SECRET_KEY": os.getenv("DJANGO_SECRET_KEY"),
    "SITE_DOMAIN": os.getenv("SITE_DOMAIN"),
    "SITE_URL": os.getenv("SITE_URL"),
    "ALLOWED_HOSTS": os.getenv("ALLOWED_HOSTS"),
    "CSRF_TRUSTED_ORIGINS": os.getenv("CSRF_TRUSTED_ORIGINS"),
    "FORM_SECURITY_KEY": os.getenv("FORM_SECURITY_KEY"),
    "BACKUP_ENCRYPTION_KEY": os.getenv("BACKUP_ENCRYPTION_KEY"),
    "EMAIL_HOST_USER": os.getenv("EMAIL_HOST_USER"),
    "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD"),
    "SALES_EMAILS": os.getenv("SALES_EMAILS"),
}
missing = [name for name, value in required.items() if not value]
if missing:
    raise ImproperlyConfigured(f"生产环境缺少必要配置：{', '.join(missing)}")
if not CLAMAV_ENABLED:
    raise ImproperlyConfigured("生产环境必须设置 CLAMAV_ENABLED=true。")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "SAMEORIGIN"
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
REQUIRE_SUPERUSER_2FA = True

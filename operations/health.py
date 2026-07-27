import shutil
import socket
import ssl
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.utils import timezone

from .models import EmailTask, SystemAlert, TaskRun


def public_health_status():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return "unavailable"
    unresolved = SystemAlert.objects.filter(resolved_at__isnull=True).exists()
    return "degraded" if unresolved else "ok"


def health_snapshot():
    disk = shutil.disk_usage(settings.BASE_DIR)
    db_path = Path(settings.DATABASES["default"]["NAME"])
    latest = {kind: TaskRun.objects.filter(kind=kind).first() for kind in ("backup", "email_queue", "prerender_full", "prerender_incremental")}
    certificate_days = None
    if settings.SITE_DOMAIN not in {"", "localhost"}:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((settings.SITE_DOMAIN, 443), timeout=4) as sock:
                with context.wrap_socket(sock, server_hostname=settings.SITE_DOMAIN) as secure:
                    expires = ssl.cert_time_to_seconds(secure.getpeercert()["notAfter"])
                    certificate_days = int((datetime.fromtimestamp(expires, dt_timezone.utc) - datetime.now(dt_timezone.utc)).total_seconds() / 86400)
        except OSError:
            certificate_days = -1
    return {
        "pending_email": EmailTask.objects.filter(status=EmailTask.Status.PENDING).count(),
        "failed_email": EmailTask.objects.filter(status=EmailTask.Status.FAILED).count(),
        "unresolved_alerts": SystemAlert.objects.filter(resolved_at__isnull=True).count(),
        "database_size_mb": round(db_path.stat().st_size / 1024 / 1024, 2) if db_path.exists() else 0,
        "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
        "certificate_days": certificate_days,
        "clamav_enabled": settings.CLAMAV_ENABLED,
        "latest_runs": latest,
        "generated_at": timezone.now(),
    }

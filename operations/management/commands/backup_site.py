from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from operations.backup import create_backup
from operations.models import SystemAlert, TaskRun


class Command(BaseCommand):
    help = "在线快照 SQLite，并加密备份数据库与媒体文件。"

    def handle(self, *args, **options):
        run = TaskRun.objects.create(kind="backup", status="running")
        try:
            record = create_backup()
        except Exception as exc:
            run.status = "failed"
            run.summary = str(exc)[:500]
            SystemAlert.objects.create(source="backup", message=f"备份失败：{run.summary}")
            raise CommandError(run.summary) from exc
        else:
            run.status = "success"
            run.summary = f"备份完成：{record.filename}"
            self.stdout.write(self.style.SUCCESS(run.summary))
        finally:
            run.finished_at = timezone.now()
            run.save(update_fields=("status", "summary", "finished_at"))

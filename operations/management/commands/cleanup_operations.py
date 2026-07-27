from django.core.management.base import BaseCommand
from django.utils import timezone

from operations.maintenance import anonymize_old_leads, cleanup_expired_data
from operations.models import TaskRun


class Command(BaseCommand):
    help = "匿名化到期线索，并清理过期安全记录、任务和备份。"

    def handle(self, *args, **options):
        run = TaskRun.objects.create(kind="cleanup", status="running")
        count = anonymize_old_leads()
        cleanup_expired_data()
        run.status = "success"
        run.summary = f"匿名化 {count} 条线索并完成过期数据清理。"
        run.finished_at = timezone.now()
        run.save(update_fields=("status", "summary", "finished_at"))
        self.stdout.write(self.style.SUCCESS(run.summary))

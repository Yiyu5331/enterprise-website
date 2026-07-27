from django.core.management.base import BaseCommand
from django.utils import timezone

from operations.mail_queue import process_one
from operations.models import EmailTask, TaskRun


class Command(BaseCommand):
    help = "处理到期的数据库邮件任务。"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        run = TaskRun.objects.create(kind="email_queue", status="running")
        task_ids = list(
            EmailTask.objects.filter(
                status=EmailTask.Status.PENDING,
                next_attempt_at__lte=timezone.now(),
            ).order_by("next_attempt_at").values_list("pk", flat=True)[:options["limit"]]
        )
        sent = sum(1 for task_id in task_ids if process_one(task_id))
        run.status = "success"
        run.summary = f"处理 {len(task_ids)} 个任务，成功 {sent} 个。"
        run.finished_at = timezone.now()
        run.save(update_fields=("status", "summary", "finished_at"))
        self.stdout.write(self.style.SUCCESS(run.summary))

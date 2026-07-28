from datetime import timedelta

from django.utils import timezone

from main.models import LeadStatus, Lianxi, Xunpan

from .backup import cleanup_old_backups
from .models import AuditLog, CaptchaChallenge, FormToken, PrerenderTask, SystemAlert, TaskRun


def anonymize_old_leads():
    cutoff = timezone.now() - timedelta(days=365 * 3)
    total = 0
    for model in (Xunpan, Lianxi):
        queryset = model.objects.filter(
            status__in=(LeadStatus.COMPLETED, LeadStatus.INVALID),
            created_at__lte=cutoff,
            anonymized_at__isnull=True,
        )
        for lead in queryset.iterator():
            for task in lead.email_tasks.all():
                for attachment in list(task.attachments.all()):
                    attachment.delete()
                task.recipients = []
                task.subject = "历史邮件已匿名化"
                task.text_body = "邮件内容已按数据保留政策匿名化。"
                task.html_body = "<p>邮件内容已按数据保留政策匿名化。</p>"
                task.save(update_fields=("recipients", "subject", "text_body", "html_body"))
            if isinstance(lead, Xunpan) and lead.attachment:
                lead.attachment.delete(save=False)
            lead.contact_name = "已匿名化"
            lead.phone = ""
            lead.email = f"anonymous-{lead.pk}@invalid.local"
            if hasattr(lead, "company_brand"):
                lead.company_brand = ""
                lead.detailed_requirements = "内容已按数据保留政策匿名化。"
                lead.attachment = None
            else:
                lead.message = "内容已按数据保留政策匿名化。"
            lead.internal_note = ""
            lead.anonymized_at = timezone.now()
            fields = ["contact_name", "phone", "email", "internal_note", "anonymized_at"]
            fields += ["company_brand", "detailed_requirements", "attachment"] if isinstance(lead, Xunpan) else ["message"]
            lead.save(update_fields=fields)
            AuditLog.objects.create(action="lead_anonymized", target_type=model._meta.model_name, target_id=str(lead.pk), summary="线索达到三年保留期后自动匿名化")
            total += 1
    return total


def cleanup_expired_data():
    now = timezone.now()
    CaptchaChallenge.objects.filter(expires_at__lt=now - timedelta(days=1)).delete()
    FormToken.objects.filter(created_at__lt=now - timedelta(days=1)).delete()
    AuditLog.objects.filter(created_at__lt=now - timedelta(days=365 * 3)).delete()
    PrerenderTask.objects.filter(pending=False, updated_at__lt=now - timedelta(days=30)).delete()
    cleanup_old_backups(30)


def recover_stale_task_runs(max_age=timedelta(hours=2)):
    """将异常中断后遗留的运行中任务收敛为失败，避免后台状态永久卡住。"""
    cutoff = timezone.now() - max_age
    stale_runs = TaskRun.objects.filter(status="running", started_at__lt=cutoff)
    recovered = 0
    for run in stale_runs:
        run.status = "failed"
        run.summary = "任务超过 2 小时未结束，已自动标记为失败。"
        run.finished_at = timezone.now()
        run.save(update_fields=("status", "summary", "finished_at"))
        SystemAlert.objects.create(
            level="error",
            source="task_run",
            message=f"任务运行记录 {run.pk}（{run.kind}）疑似异常中断，已标记为失败。",
        )
        recovered += 1
    return recovered

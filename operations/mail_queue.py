from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.utils import timezone

from main.models import LeadStatus

from .models import AuditLog, EmailTask, SystemAlert


RETRY_DELAYS = (timedelta(minutes=1), timedelta(minutes=5), timedelta(minutes=30))


def send_email_task(task):
    message = EmailMultiAlternatives(
        subject=task.subject,
        body=task.text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=task.recipients,
    )
    if task.html_body:
        message.attach_alternative(task.html_body, "text/html")
    for attachment in task.attachments.all():
        with attachment.file.open("rb") as source:
            message.attach(attachment.original_name, source.read())
    message.send(fail_silently=False)


def process_one(task_id):
    with transaction.atomic():
        task = EmailTask.objects.select_for_update().filter(pk=task_id).first()
        if not task or task.status != EmailTask.Status.PENDING:
            return False
        if task.next_attempt_at > timezone.now():
            return False
        task.status = EmailTask.Status.SENDING
        task.attempts += 1
        task.save(update_fields=("status", "attempts"))

    try:
        send_email_task(task)
    except Exception as exc:
        with transaction.atomic():
            task = EmailTask.objects.select_for_update().get(pk=task_id)
            task.last_error = str(exc)[:500]
            retry_index = task.attempts - 1
            if retry_index < len(RETRY_DELAYS):
                task.status = EmailTask.Status.PENDING
                task.next_attempt_at = timezone.now() + RETRY_DELAYS[retry_index]
            else:
                task.status = EmailTask.Status.FAILED
                SystemAlert.objects.create(source="email", message=f"邮件任务 {task.pk} 最终发送失败：{task.last_error}")
                if settings.OPS_ALERT_EMAILS and task.kind != EmailTask.Kind.OPS_ALERT:
                    EmailTask.objects.create(
                        kind=EmailTask.Kind.OPS_ALERT,
                        recipients=settings.OPS_ALERT_EMAILS,
                        subject="华丽电器网站邮件队列告警",
                        text_body=f"邮件任务 {task.pk} 最终失败：{task.last_error}",
                        html_body=f"<p>邮件任务 {task.pk} 最终失败。</p><p>{task.last_error}</p>",
                    )
            task.save(update_fields=("status", "next_attempt_at", "last_error"))
        return False

    with transaction.atomic():
        task = EmailTask.objects.select_for_update().get(pk=task_id)
        now = timezone.now()
        task.status = EmailTask.Status.SENT
        task.sent_at = now
        task.last_error = ""
        task.save(update_fields=("status", "sent_at", "last_error"))
        lead = task.inquiry or task.contact
        if task.kind == EmailTask.Kind.FOLLOW_UP and lead:
            lead.last_followed_at = now
            fields = ["last_followed_at"]
            if lead.status == LeadStatus.PENDING:
                lead.status = LeadStatus.FOLLOWING
                fields.append("status")
            lead.save(update_fields=fields)
        AuditLog.objects.create(
            actor=task.created_by,
            action="email_sent",
            target_type="email_task",
            target_id=str(task.pk),
            summary=f"邮件发送成功，类型：{task.get_kind_display()}",
        )
    return True

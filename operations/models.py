import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .storage import private_storage


class PrivacyPolicy(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"
        RETIRED = "retired", "已停用"

    version = models.CharField("版本号", max_length=30, unique=True)
    title_zh = models.CharField("中文标题", max_length=200)
    body_zh = models.TextField("中文正文")
    title_en = models.CharField("英文标题", max_length=200)
    body_en = models.TextField("英文正文")
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField("发布时间", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "隐私政策版本"
        verbose_name_plural = "隐私政策版本"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).values("status", "version", "title_zh", "body_zh", "title_en", "body_en", "published_at").first()
            if old and old["status"] == self.Status.PUBLISHED:
                changed = any((
                    old["version"] != self.version,
                    old["title_zh"] != self.title_zh,
                    old["body_zh"] != self.body_zh,
                    old["title_en"] != self.title_en,
                    old["body_en"] != self.body_en,
                    old["published_at"] != self.published_at,
                ))
                if changed:
                    raise ValidationError("已发布的隐私政策不可修改，请创建新版本。")
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
            type(self).objects.filter(status=self.Status.PUBLISHED).exclude(pk=self.pk).update(status=self.Status.RETIRED)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.version} - {self.get_status_display()}"


class FormToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField("表单类型", max_length=20)
    ip_fingerprint = models.CharField("IP 指纹", max_length=64, db_index=True)
    created_at = models.DateTimeField("签发时间", auto_now_add=True)
    used_at = models.DateTimeField("使用时间", null=True, blank=True)

    class Meta:
        verbose_name = "表单令牌"
        verbose_name_plural = "表单令牌"


class CaptchaChallenge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    answer_hash = models.CharField("答案摘要", max_length=64)
    ip_fingerprint = models.CharField("IP 指纹", max_length=64, db_index=True)
    expires_at = models.DateTimeField("过期时间")
    used_at = models.DateTimeField("使用时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "验证码"
        verbose_name_plural = "验证码"


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField("操作", max_length=80, db_index=True)
    target_type = models.CharField("对象类型", max_length=80, blank=True)
    target_id = models.CharField("对象编号", max_length=80, blank=True)
    summary = models.CharField("摘要", max_length=300, blank=True)
    created_at = models.DateTimeField("时间", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "审计日志"
        verbose_name_plural = "审计日志"
        ordering = ("-created_at",)


class EmailTemplate(models.Model):
    key = models.SlugField("模板键", max_length=60, unique=True)
    name = models.CharField("模板名称", max_length=100)
    subject = models.CharField("邮件主题", max_length=200)
    html_body = models.TextField("HTML 正文")
    text_body = models.TextField("纯文本正文")
    allowed_variables = models.CharField("允许变量", max_length=500, blank=True)
    is_active = models.BooleanField("启用", default=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "邮件模板"
        verbose_name_plural = "邮件模板"

    def __str__(self):
        return self.name


class EmailTask(models.Model):
    class Kind(models.TextChoices):
        SALES_NOTICE = "sales_notice", "销售通知"
        CUSTOMER_RECEIPT = "customer_receipt", "客户回执"
        FOLLOW_UP = "follow_up", "跟进邮件"
        OPS_ALERT = "ops_alert", "运维告警"

    class Status(models.TextChoices):
        PENDING = "pending", "待发送"
        SENDING = "sending", "发送中"
        SENT = "sent", "已发送"
        FAILED = "failed", "失败"

    template = models.ForeignKey(EmailTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    kind = models.CharField("邮件类型", max_length=30, choices=Kind.choices, default=Kind.CUSTOMER_RECEIPT)
    inquiry = models.ForeignKey("main.Xunpan", null=True, blank=True, on_delete=models.SET_NULL, related_name="email_tasks")
    contact = models.ForeignKey("main.Lianxi", null=True, blank=True, on_delete=models.SET_NULL, related_name="email_tasks")
    recipients = models.JSONField("收件人", default=list)
    subject = models.CharField("主题", max_length=200)
    html_body = models.TextField("HTML 正文")
    text_body = models.TextField("纯文本正文")
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    attempts = models.PositiveSmallIntegerField("尝试次数", default=0)
    next_attempt_at = models.DateTimeField("下次尝试", default=timezone.now, db_index=True)
    last_error = models.CharField("错误摘要", max_length=500, blank=True)
    sent_at = models.DateTimeField("发送时间", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "邮件任务"
        verbose_name_plural = "邮件任务"
        ordering = ("-created_at",)


class EmailAttachment(models.Model):
    task = models.ForeignKey(EmailTask, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField("附件", upload_to="mail/%Y/%m/", storage=private_storage)
    original_name = models.CharField("原文件名", max_length=255)
    size = models.PositiveBigIntegerField("大小", default=0)
    scan_status = models.CharField("扫描状态", max_length=30, default="pending")

    class Meta:
        verbose_name = "邮件附件"
        verbose_name_plural = "邮件附件"

    def delete(self, *args, **kwargs):
        field_file = self.file
        result = super().delete(*args, **kwargs)
        if field_file:
            field_file.storage.delete(field_file.name)
        return result


class RecoveryCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="otp_recovery_codes", on_delete=models.CASCADE)
    code_hash = models.CharField("恢复码摘要", max_length=64)
    used_at = models.DateTimeField("使用时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "双重验证恢复码"
        verbose_name_plural = "双重验证恢复码"


class TaskRun(models.Model):
    kind = models.CharField("任务类型", max_length=40, db_index=True)
    status = models.CharField("状态", max_length=20, db_index=True)
    summary = models.CharField("摘要", max_length=500, blank=True)
    started_at = models.DateTimeField("开始时间", default=timezone.now)
    finished_at = models.DateTimeField("结束时间", null=True, blank=True)

    class Meta:
        verbose_name = "任务运行记录"
        verbose_name_plural = "任务运行记录"
        ordering = ("-started_at",)


class SystemAlert(models.Model):
    level = models.CharField("级别", max_length=20, default="error")
    source = models.CharField("来源", max_length=50, db_index=True)
    message = models.CharField("告警内容", max_length=500)
    resolved_at = models.DateTimeField("解决时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "系统告警"
        verbose_name_plural = "系统告警"
        ordering = ("-created_at",)


class PrerenderTask(models.Model):
    path = models.CharField("页面路径", max_length=500, unique=True)
    reason = models.CharField("触发原因", max_length=200, blank=True)
    pending = models.BooleanField("等待重建", default=True, db_index=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "预渲染任务"
        verbose_name_plural = "预渲染任务"


class BackupRecord(models.Model):
    filename = models.CharField("文件名", max_length=255)
    sha256 = models.CharField("SHA-256", max_length=64)
    size = models.PositiveBigIntegerField("大小")
    status = models.CharField("状态", max_length=20)
    remote_uploaded = models.BooleanField("已上传异地", default=False)
    migration_signature = models.CharField("迁移版本摘要", max_length=64, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "备份记录"
        verbose_name_plural = "备份记录"
        ordering = ("-created_at",)

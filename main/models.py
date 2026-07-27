from django.conf import settings
from django.db import models

from operations.storage import private_storage


class LeadStatus(models.TextChoices):
    PENDING = "pending", "待处理"
    FOLLOWING = "following", "跟进中"
    QUOTED = "quoted", "已报价"
    COMPLETED = "completed", "已完成"
    INVALID = "invalid", "无效"


class Xunpan(models.Model):
    """在线询盘表单记录。"""

    contact_name = models.CharField("联系人姓名", max_length=100)
    phone = models.CharField("联系电话", max_length=50, blank=True)
    email = models.EmailField("邮箱")
    company_brand = models.CharField("公司/品牌", max_length=200, blank=True)
    project_type = models.CharField("感兴趣的产品", max_length=100, blank=True)
    product_name_snapshot = models.CharField("产品名称快照", max_length=150, blank=True)
    product_model_snapshot = models.CharField("产品型号快照", max_length=80, blank=True)
    product = models.ForeignKey(
        "products.Product",
        verbose_name="关联产品",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inquiries",
    )
    estimated_quantity = models.CharField("预计数量", max_length=100, blank=True)
    country_region = models.CharField("国家/地区", max_length=100, blank=True)
    detailed_requirements = models.TextField("详细需求")
    attachment = models.FileField(
        "附件",
        upload_to="inquiry_attachments/%Y/%m/",
        storage=private_storage,
        blank=True,
        null=True,
    )
    privacy_policy = models.ForeignKey(
        "operations.PrivacyPolicy",
        verbose_name="同意的隐私政策",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inquiries",
    )
    privacy_consented_at = models.DateTimeField("隐私同意时间", null=True, blank=True)
    ip_fingerprint = models.CharField("IP 指纹", max_length=64, blank=True, db_index=True)
    form_token_id = models.CharField("表单令牌编号", max_length=36, blank=True)
    attachment_scan_status = models.CharField("附件扫描状态", max_length=30, default="not_applicable")
    anonymized_at = models.DateTimeField("匿名化时间", null=True, blank=True)
    status = models.CharField("处理状态", max_length=20, choices=LeadStatus.choices, default=LeadStatus.PENDING)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="负责人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_inquiries",
    )
    internal_note = models.TextField("内部备注", blank=True)
    last_followed_at = models.DateTimeField("最后跟进时间", null=True, blank=True)
    created_at = models.DateTimeField("提交时间", auto_now_add=True)

    class Meta:
        db_table = "xunpan"
        verbose_name = "询盘表单"
        verbose_name_plural = "询盘表单"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contact_name} - {self.project_type or '未选择产品'}"

    def delete(self, *args, **kwargs):
        attachment = self.attachment
        result = super().delete(*args, **kwargs)
        if attachment:
            attachment.storage.delete(attachment.name)
        return result


class Lianxi(models.Model):
    """联系我们页面的在线留言记录。"""

    contact_name = models.CharField("联系人姓名", max_length=100)
    phone = models.CharField("联系电话", max_length=50, blank=True)
    email = models.EmailField("邮箱")
    subject = models.CharField("主题", max_length=100, blank=True)
    message = models.TextField("留言内容")
    privacy_policy = models.ForeignKey(
        "operations.PrivacyPolicy",
        verbose_name="同意的隐私政策",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="contacts",
    )
    privacy_consented_at = models.DateTimeField("隐私同意时间", null=True, blank=True)
    ip_fingerprint = models.CharField("IP 指纹", max_length=64, blank=True, db_index=True)
    form_token_id = models.CharField("表单令牌编号", max_length=36, blank=True)
    security_scan_status = models.CharField("安全检查状态", max_length=30, default="not_applicable")
    anonymized_at = models.DateTimeField("匿名化时间", null=True, blank=True)
    status = models.CharField("处理状态", max_length=20, choices=LeadStatus.choices, default=LeadStatus.PENDING)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="负责人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_contacts",
    )
    internal_note = models.TextField("内部备注", blank=True)
    last_followed_at = models.DateTimeField("最后跟进时间", null=True, blank=True)
    created_at = models.DateTimeField("提交时间", auto_now_add=True)

    class Meta:
        db_table = "lianxi"
        verbose_name = "联系表单"
        verbose_name_plural = "联系表单"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contact_name} - {self.subject or '未选择主题'}"

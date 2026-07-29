from django.db import models
from django.utils import timezone

from company_content.models import ContentSource
from main.content_utils import (
    ContentStatus, VerificationStatus, validate_image_upload, validate_pdf_upload,
    validate_production_publish,
)


class HonorCategory(models.Model):
    name = models.CharField("分类名称", max_length=100, unique=True)
    slug = models.SlugField("固定 slug", max_length=100, unique=True)
    description = models.CharField("分类说明", max_length=300, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("启用", default=True)

    class Meta:
        verbose_name = "荣誉分类"
        verbose_name_plural = "荣誉分类"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class Honor(models.Model):
    category = models.ForeignKey(HonorCategory, verbose_name="分类", related_name="honors", on_delete=models.PROTECT)
    slug = models.SlugField("固定 slug", max_length=120, unique=True)
    title = models.CharField("荣誉名称", max_length=200)
    summary = models.TextField("公开摘要", blank=True)
    reference_number = models.CharField("证书/公告编号", max_length=100, blank=True)
    issuer = models.CharField("颁发/认定机构", max_length=200, blank=True)
    awarded_on = models.DateField("获得日期", null=True, blank=True)
    display_image = models.ImageField("展示图片", upload_to="honors/images/", blank=True, validators=[validate_image_upload])
    document = models.FileField("公开 PDF", upload_to="honors/documents/", blank=True, validators=[validate_pdf_upload])
    use_watermark = models.BooleanField("展示图使用水印", default=False)
    allow_document_download = models.BooleanField("允许下载 PDF", default=False)
    status = models.CharField("状态", max_length=20, choices=ContentStatus.choices, default=ContentStatus.DRAFT)
    verification_status = models.CharField(
        "核验状态", max_length=20, choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING, db_index=True,
    )
    is_demo = models.BooleanField("演示内容", default=False, db_index=True)
    source = models.ForeignKey(ContentSource, verbose_name="内容来源", null=True, blank=True, on_delete=models.SET_NULL)
    verified_at = models.DateTimeField("内容核验时间", null=True, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "荣誉资质"
        verbose_name_plural = "荣誉资质"
        ordering = ("sort_order", "-awarded_on", "id")

    def __str__(self):
        return self.title

    def clean(self):
        validate_production_publish(
            status=self.status, is_demo=self.is_demo,
            verification_status=self.verification_status,
        )

    def save(self, *args, **kwargs):
        if self.verification_status == VerificationStatus.VERIFIED and not self.verified_at:
            self.verified_at = timezone.now()
        elif self.verification_status != VerificationStatus.VERIFIED:
            self.verified_at = None
        if kwargs.get("update_fields") is not None and "verification_status" in kwargs["update_fields"]:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"verified_at"}
        super().save(*args, **kwargs)

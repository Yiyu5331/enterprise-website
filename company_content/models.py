from django.db import models
from django.utils import timezone

from main.content_utils import ContentStatus, VerificationStatus, validate_production_publish


class ContentSource(models.Model):
    name = models.CharField("来源名称", max_length=200)
    url = models.URLField("来源网址", blank=True)
    reference_file = models.FileField("来源文件", upload_to="content_sources/", blank=True)
    notes = models.TextField("核验备注", blank=True)
    verified_by = models.ForeignKey("auth.User", verbose_name="核验人", null=True, blank=True, on_delete=models.SET_NULL)
    verified_at = models.DateTimeField("核验时间", null=True, blank=True)
    is_public = models.BooleanField("前台显示来源", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "内容来源"
        verbose_name_plural = "内容来源"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class PublishableCompanyContent(models.Model):
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
        abstract = True

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


class CompanyProfile(PublishableCompanyContent):
    name_zh = models.CharField("公司中文名", max_length=200)
    name_en = models.CharField("公司英文名", max_length=200, blank=True)
    brand_name = models.CharField("英文品牌简称", max_length=50, default="HUALI")
    summary = models.TextField("公司简介")
    legal_representative = models.CharField("法人代表", max_length=100, blank=True)
    founded_on = models.DateField("成立日期", null=True, blank=True)
    registered_capital = models.CharField("注册资本", max_length=100, blank=True)
    credit_code = models.CharField("统一社会信用代码", max_length=50, blank=True)
    registered_address = models.CharField("注册地址", max_length=300, blank=True)

    class Meta:
        verbose_name = "企业资料"
        verbose_name_plural = "企业资料"

    def __str__(self):
        return self.name_zh


class CompanyFact(PublishableCompanyContent):
    label = models.CharField("指标名称", max_length=100)
    value = models.CharField("指标值", max_length=100)
    unit = models.CharField("单位", max_length=30, blank=True)
    description = models.CharField("说明", max_length=300, blank=True)

    class Meta:
        verbose_name = "企业事实与指标"
        verbose_name_plural = "企业事实与指标"
        ordering = ("sort_order", "id")

    def __str__(self):
        return f"{self.label}: {self.value}{self.unit}"


class CompanyTimeline(PublishableCompanyContent):
    year = models.PositiveSmallIntegerField("年份")
    title = models.CharField("标题", max_length=150)
    description = models.TextField("说明")

    class Meta:
        verbose_name = "发展历程"
        verbose_name_plural = "发展历程"
        ordering = ("year", "sort_order", "id")

    def __str__(self):
        return f"{self.year} - {self.title}"


class SupplyChainItem(PublishableCompanyContent):
    class Kind(models.TextChoices):
        PROCESS = "process", "采购流程"
        CATEGORY = "category", "核心采购品类"
        REQUIREMENT = "requirement", "合作要求"

    kind = models.CharField("内容类型", max_length=20, choices=Kind.choices)
    title = models.CharField("标题", max_length=150)
    description = models.TextField("说明")

    class Meta:
        verbose_name = "供应链内容"
        verbose_name_plural = "供应链内容"
        ordering = ("kind", "sort_order", "id")

    def __str__(self):
        return self.title


class DealerBenefit(PublishableCompanyContent):
    title = models.CharField("权益名称", max_length=150)
    description = models.TextField("权益说明")

    class Meta:
        verbose_name = "经销商权益"
        verbose_name_plural = "经销商权益"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.title


class Location(PublishableCompanyContent):
    class Kind(models.TextChoices):
        HEADQUARTERS = "headquarters", "总部"
        FACTORY = "factory", "工厂"
        OFFICE = "office", "办事处"

    kind = models.CharField("地点类型", max_length=20, choices=Kind.choices, default=Kind.FACTORY)
    name = models.CharField("地点名称", max_length=150)
    address_zh = models.CharField("中文地址", max_length=300)
    address_en = models.CharField("英文地址", max_length=300, blank=True)
    longitude = models.DecimalField("经度", max_digits=10, decimal_places=7, null=True, blank=True)
    latitude = models.DecimalField("纬度", max_digits=10, decimal_places=7, null=True, blank=True)
    phone = models.CharField("电话", max_length=50, blank=True)
    email = models.EmailField("邮箱", blank=True)
    business_hours = models.CharField("工作时间", max_length=150, blank=True)

    class Meta:
        verbose_name = "地点与联系方式"
        verbose_name_plural = "地点与联系方式"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class FAQCategory(models.Model):
    name = models.CharField("分类名称", max_length=100, unique=True)
    slug = models.SlugField("固定 slug", max_length=100, unique=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("启用", default=True)

    class Meta:
        verbose_name = "常见问题分类"
        verbose_name_plural = "常见问题分类"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class FAQ(PublishableCompanyContent):
    category = models.ForeignKey(FAQCategory, verbose_name="分类", related_name="faqs", on_delete=models.PROTECT)
    question = models.CharField("问题", max_length=300)
    answer = models.TextField("回答")

    class Meta:
        verbose_name = "常见问题"
        verbose_name_plural = "常见问题"
        ordering = ("category__sort_order", "sort_order", "id")

    def __str__(self):
        return self.question

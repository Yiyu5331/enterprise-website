import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image

from main.content_utils import validate_image_upload


class MediaFolder(models.Model):
    name = models.CharField("文件夹名称", max_length=100)
    parent = models.ForeignKey("self", verbose_name="上级文件夹", null=True, blank=True, related_name="children", on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "媒体文件夹"
        verbose_name_plural = "媒体文件夹"
        ordering = ("sort_order", "name")
        constraints = [models.UniqueConstraint(fields=("parent", "name"), name="unique_media_folder_name")]

    def __str__(self):
        return self.name


class MediaTag(models.Model):
    name = models.CharField("标签名称", max_length=50, unique=True)
    slug = models.SlugField("固定 slug", max_length=50, unique=True)

    class Meta:
        verbose_name = "媒体标签"
        verbose_name_plural = "媒体标签"

    def __str__(self):
        return self.name


class AssetLicense(models.Model):
    class LicenseType(models.TextChoices):
        OWNED = "owned", "自有素材"
        CC0 = "cc0", "CC0"
        CC_BY = "cc_by", "CC BY"
        MIT = "mit", "MIT"
        APACHE = "apache", "Apache-2.0"
        OTHER = "other", "其他"
        UNKNOWN = "unknown", "未知"

    name = models.CharField("许可名称", max_length=120)
    license_type = models.CharField("许可类型", max_length=30, choices=LicenseType.choices, default=LicenseType.UNKNOWN)
    author = models.CharField("作者/版权方", max_length=150, blank=True)
    source_url = models.URLField("来源网址", blank=True)
    attribution = models.TextField("署名要求", blank=True)
    allows_commercial_use = models.BooleanField("允许商业使用", default=False)
    notes = models.TextField("备注", blank=True)

    class Meta:
        verbose_name = "素材许可"
        verbose_name_plural = "素材许可台账"

    def __str__(self):
        return self.name


class PublicMediaAsset(models.Model):
    class AssetType(models.TextChoices):
        IMAGE = "image", "图片"
        VIDEO = "video", "视频"
        LOTTIE = "lottie", "Lottie"
        RIVE = "rive", "Rive"
        MODEL_3D = "model_3d", "3D 模型"
        OTHER = "other", "其他"

    class Origin(models.TextChoices):
        REAL = "real", "真实素材"
        AI = "ai", "AI 占位素材"
        OPEN_SOURCE = "open_source", "开源素材"
        INTERNAL = "internal", "内部制作"

    title = models.CharField("素材名称", max_length=150)
    folder = models.ForeignKey(MediaFolder, verbose_name="文件夹", null=True, blank=True, related_name="assets", on_delete=models.SET_NULL)
    tags = models.ManyToManyField(MediaTag, verbose_name="标签", related_name="assets", blank=True)
    asset_type = models.CharField("素材类型", max_length=20, choices=AssetType.choices, default=AssetType.IMAGE)
    origin = models.CharField("素材来源类型", max_length=20, choices=Origin.choices, default=Origin.AI)
    file = models.FileField("素材文件", upload_to="page_builder/assets/%Y/%m/")
    desktop_file = models.FileField("桌面变体", upload_to="page_builder/variants/desktop/%Y/%m/", blank=True)
    mobile_file = models.FileField("手机变体", upload_to="page_builder/variants/mobile/%Y/%m/", blank=True)
    preview_image = models.ImageField("预览/封面", upload_to="page_builder/previews/%Y/%m/", blank=True, validators=[validate_image_upload])
    alt_zh = models.CharField("中文 Alt 草稿", max_length=250, blank=True)
    alt_en = models.CharField("英文 Alt 草稿", max_length=250, blank=True)
    alt_reviewed = models.BooleanField("Alt 已审核", default=False)
    is_decorative = models.BooleanField("装饰图", default=False)
    focal_x_desktop = models.FloatField("桌面焦点 X", default=0.5)
    focal_y_desktop = models.FloatField("桌面焦点 Y", default=0.5)
    focal_x_mobile = models.FloatField("手机焦点 X", default=0.5)
    focal_y_mobile = models.FloatField("手机焦点 Y", default=0.5)
    width = models.PositiveIntegerField("宽度", default=0, editable=False)
    height = models.PositiveIntegerField("高度", default=0, editable=False)
    size = models.PositiveBigIntegerField("文件大小", default=0, editable=False)
    sha256 = models.CharField("SHA-256", max_length=64, blank=True, editable=False)
    license = models.ForeignKey(AssetLicense, verbose_name="素材许可", null=True, blank=True, related_name="assets", on_delete=models.PROTECT)
    generation_prompt = models.TextField("最终生成提示词", blank=True)
    generation_model = models.CharField("生成模型", max_length=100, blank=True)
    generated_at = models.DateTimeField("生成时间", null=True, blank=True)
    needs_replacement = models.BooleanField("上线前待替换", default=True, db_index=True)
    is_approved = models.BooleanField("素材已审核", default=False, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "公开媒体素材"
        verbose_name_plural = "公开媒体库"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.file and not self.file._committed:
            position = self.file.tell()
            self.file.seek(0)
            content = self.file.read()
            self.file.seek(position)
            self.size = len(content)
            self.sha256 = hashlib.sha256(content).hexdigest()
            if self.asset_type == self.AssetType.IMAGE:
                try:
                    self.file.seek(0)
                    with Image.open(self.file) as image:
                        self.width, self.height = image.size
                except (OSError, ValueError):
                    self.width = 0
                    self.height = 0
                finally:
                    self.file.seek(position)
        super().save(*args, **kwargs)

    def clean(self):
        if not self.is_approved:
            return
        errors = []
        if not self.license_id:
            errors.append("审核素材前必须登记许可证。")
        elif self.license.license_type == AssetLicense.LicenseType.UNKNOWN:
            errors.append("许可证未知的素材不能通过审核。")
        elif not self.license.allows_commercial_use:
            errors.append("不允许商业使用的素材不能通过审核。")
        if self.asset_type == self.AssetType.IMAGE and not (self.alt_reviewed or self.is_decorative):
            errors.append("图片必须审核中英文 Alt，或明确标记为装饰图。")
        if errors:
            raise ValidationError(" ".join(errors))

    def __str__(self):
        return self.title


class AssetSlot(models.Model):
    key = models.SlugField("槽位键", max_length=100, unique=True)
    name = models.CharField("槽位名称", max_length=150)
    description = models.CharField("用途说明", max_length=300, blank=True)
    recommended_ratio = models.CharField("建议比例", max_length=30, blank=True)
    min_width = models.PositiveIntegerField("最小宽度", default=0)
    min_height = models.PositiveIntegerField("最小高度", default=0)
    current_asset = models.ForeignKey(PublicMediaAsset, verbose_name="当前素材", null=True, blank=True, related_name="active_slots", on_delete=models.PROTECT)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "全局素材槽位"
        verbose_name_plural = "全局素材槽位"

    def __str__(self):
        return self.name


class MediaUsage(models.Model):
    asset = models.ForeignKey(PublicMediaAsset, verbose_name="素材", related_name="usages", on_delete=models.PROTECT)
    owner_type = models.CharField("引用类型", max_length=80)
    owner_key = models.CharField("引用对象", max_length=150)
    slot_key = models.CharField("局部槽位", max_length=100, blank=True)
    is_override = models.BooleanField("页面独立覆盖", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "素材引用"
        verbose_name_plural = "素材引用关系"
        constraints = [models.UniqueConstraint(fields=("asset", "owner_type", "owner_key", "slot_key"), name="unique_media_usage")]

    def __str__(self):
        return f"{self.asset} -> {self.owner_type}:{self.owner_key}"

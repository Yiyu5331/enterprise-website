import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from main.content_utils import (
    ContentStatus,
    delete_field_file,
    process_uploaded_image,
    rich_text_to_plain,
    rich_text_images_have_alt,
    sanitize_rich_text,
    validate_image_upload,
    validate_pdf_upload,
)


class ProcessedProductImageMixin(models.Model):
    image_web = models.ImageField("网页图", upload_to="products/web/", blank=True, editable=False)
    image_thumb = models.ImageField("缩略图", upload_to="products/thumbs/", blank=True, editable=False)
    focal_x = models.FloatField("焦点 X", default=0.5)
    focal_y = models.FloatField("焦点 Y", default=0.5)

    class Meta:
        abstract = True

    image_field_name = "image"
    image_prefix = "product"
    thumbnail_size = (800, 533)

    def save(self, *args, **kwargs):
        image_field = getattr(self, self.image_field_name)
        new_upload = bool(image_field and not image_field._committed)
        old_files = []
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).first()
            if old:
                old_field = getattr(old, self.image_field_name)
                if new_upload or old.focal_x != self.focal_x or old.focal_y != self.focal_y:
                    old_files.extend([old_field, old.image_web, old.image_thumb])

        if new_upload:
            original, web, thumb = process_uploaded_image(
                image_field.file,
                prefix=self.image_prefix,
                thumb_size=self.thumbnail_size,
                focal_x=self.focal_x,
                focal_y=self.focal_y,
            )
            getattr(self, self.image_field_name).save(original.name, original, save=False)
            self.image_web.save(web.name, web, save=False)
            self.image_thumb.save(thumb.name, thumb, save=False)
        elif image_field and self.image_web and self.image_thumb and self.pk:
            old = type(self).objects.filter(pk=self.pk).first()
            if old and (old.focal_x != self.focal_x or old.focal_y != self.focal_y):
                with image_field.storage.open(image_field.name, "rb") as source:
                    _, web, thumb = process_uploaded_image(
                        source,
                        prefix=self.image_prefix,
                        thumb_size=self.thumbnail_size,
                        focal_x=self.focal_x,
                        focal_y=self.focal_y,
                    )
                self.image_web.save(web.name, web, save=False)
                self.image_thumb.save(thumb.name, thumb, save=False)

        super().save(*args, **kwargs)
        for field_file in (getattr(self, self.image_field_name), self.image_web, self.image_thumb):
            if field_file:
                field_file.close()
        current_names = {
            getattr(self, self.image_field_name).name,
            self.image_web.name,
            self.image_thumb.name,
        }
        for field_file in old_files:
            if field_file and field_file.name not in current_names:
                delete_field_file(field_file)

    def delete(self, *args, **kwargs):
        files = [getattr(self, self.image_field_name), self.image_web, self.image_thumb]
        result = super().delete(*args, **kwargs)
        for field_file in files:
            delete_field_file(field_file)
        return result


class ProductCategory(ProcessedProductImageMixin):
    name = models.CharField("分类名称", max_length=100, unique=True)
    slug = models.SlugField("固定 slug", max_length=100, unique=True)
    description = models.CharField("分类简介", max_length=300, blank=True)
    image = models.ImageField(
        "分类封面",
        upload_to="products/categories/original/",
        blank=True,
        validators=[validate_image_upload],
    )
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    image_prefix = "product-category"

    class Meta:
        verbose_name = "产品分类"
        verbose_name_plural = "产品分类"
        ordering = ("sort_order", "id")
        indexes = [models.Index(fields=("is_active", "sort_order"))]

    def clean(self):
        if self.pk:
            old_slug = type(self).objects.filter(pk=self.pk).values_list("slug", flat=True).first()
            if old_slug and old_slug != self.slug:
                raise ValidationError({"slug": "分类创建后不能修改 slug。"})
        if self.is_active and not self.image:
            raise ValidationError({"image": "启用产品分类前必须上传封面图。"})

    def delete(self, *args, **kwargs):
        if self.products.exists():
            raise ValidationError("分类下仍有产品，不能删除；请改为停用。")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    name = models.CharField("标签名称", max_length=50, unique=True)
    slug = models.SlugField("标签 slug", max_length=50, unique=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("启用", default=True)

    class Meta:
        verbose_name = "产品标签"
        verbose_name_plural = "产品标签"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class Product(ProcessedProductImageMixin):
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="产品分类",
        related_name="products",
        on_delete=models.PROTECT,
    )
    tags = models.ManyToManyField(ProductTag, verbose_name="产品标签", related_name="products", blank=True)
    name = models.CharField("产品名称", max_length=150)
    model = models.CharField("产品型号", max_length=80, unique=True)
    level = models.CharField("产品等级", max_length=50)
    summary = models.CharField("产品摘要", max_length=200)
    description = models.TextField("详细说明")
    description_text = models.TextField("说明纯文本", blank=True, editable=False)
    image = models.ImageField(
        "产品主图",
        upload_to="products/original/",
        blank=True,
        validators=[validate_image_upload],
    )
    status = models.CharField("状态", max_length=20, choices=ContentStatus.choices, default=ContentStatus.DRAFT)
    sort_order = models.PositiveIntegerField("公开排序", default=0)
    is_featured = models.BooleanField("首页推荐", default=False)
    featured_order = models.PositiveIntegerField("推荐排序", default=0)
    homepage_badge = models.CharField("首页角标", max_length=20, blank=True)
    seo_title = models.CharField("SEO 标题", max_length=160, blank=True)
    seo_description = models.CharField("SEO 描述", max_length=300, blank=True)
    search_text = models.TextField("搜索索引", blank=True, editable=False)
    first_published_at = models.DateTimeField("首次发布时间", null=True, blank=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        related_name="created_products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="最后修改人",
        related_name="updated_products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    related_products = models.ManyToManyField(
        "self",
        verbose_name="手动相关产品",
        symmetrical=False,
        blank=True,
    )

    image_prefix = "product"

    class Meta:
        verbose_name = "产品"
        verbose_name_plural = "产品"
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("status", "sort_order")),
            models.Index(fields=("category", "status", "sort_order")),
            models.Index(fields=("is_featured", "featured_order")),
        ]

    @property
    def normalized_model(self):
        return re.sub(r"[\s-]+", "", self.model).lower()

    def clean(self):
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).values("model", "first_published_at").first()
            if old and old["first_published_at"] and old["model"] != self.model:
                raise ValidationError({"model": "产品发布后不能修改型号。"})
        if len(self.summary) > 200:
            raise ValidationError({"summary": "产品摘要不能超过 200 字。"})
        if self.status == ContentStatus.PUBLISHED:
            errors = {}
            if not self.image:
                errors["image"] = "发布产品前必须上传主图。"
            if not self.summary:
                errors["summary"] = "发布产品前必须填写摘要。"
            if not rich_text_to_plain(self.description):
                errors["description"] = "发布产品前必须填写详细说明。"
            elif not rich_text_images_have_alt(self.description):
                errors["description"] = "详细说明中的每张图片都必须包含 alt 属性。"
            if errors:
                raise ValidationError(errors)

    def validate_for_publish(self):
        """校验所有发布入口都必须满足的完整度要求。"""
        self.full_clean()
        if not self.pk:
            raise ValidationError("产品必须先保存，才能校验关联内容。")
        errors = []
        if not self.specifications.exists():
            errors.append("至少需要 1 条产品参数")
        if not self.highlights.exists():
            errors.append("至少需要 1 条产品特点")
        if not self.applications.exists():
            errors.append("至少需要 1 条应用场景")
        if self.specifications.filter(show_on_card=True).count() > 4:
            errors.append("卡片展示参数不能超过 4 项")
        if errors:
            raise ValidationError("；".join(errors) + "。")

    def save(self, *args, **kwargs):
        self.description = sanitize_rich_text(self.description)
        self.description_text = rich_text_to_plain(self.description)
        super().save(*args, **kwargs)

    def rebuild_search_text(self, save=True):
        parts = [self.name, self.model, self.normalized_model, self.summary, self.description_text, self.level]
        parts.extend(f"{item.name} {item.value}" for item in self.specifications.all())
        parts.extend(f"{item.title} {item.description}" for item in self.highlights.all())
        parts.extend(f"{item.name} {item.description}" for item in self.applications.all())
        self.search_text = " ".join(filter(None, parts))
        if save:
            type(self).objects.filter(pk=self.pk).update(search_text=self.search_text)

    def __str__(self):
        return f"{self.name}（{self.model}）"


class ProductGalleryImage(ProcessedProductImageMixin):
    product = models.ForeignKey(Product, verbose_name="产品", related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(
        "详情图片",
        upload_to="products/gallery/original/",
        validators=[validate_image_upload],
    )
    alt_text = models.CharField("图片说明/Alt", max_length=200)
    caption = models.CharField("图片说明", max_length=250, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    image_prefix = "product-gallery"

    class Meta:
        verbose_name = "产品图库"
        verbose_name_plural = "产品图库"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.alt_text


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, verbose_name="产品", related_name="specifications", on_delete=models.CASCADE)
    name = models.CharField("参数名称", max_length=100)
    value = models.CharField("参数值", max_length=150)
    show_on_card = models.BooleanField("卡片展示", default=False)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "产品参数"
        verbose_name_plural = "产品参数"
        ordering = ("sort_order", "id")

    def __str__(self):
        return f"{self.name}: {self.value}"


class ProductHighlight(models.Model):
    product = models.ForeignKey(Product, verbose_name="产品", related_name="highlights", on_delete=models.CASCADE)
    title = models.CharField("特点标题", max_length=100)
    description = models.CharField("特点说明", max_length=300)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "产品特点"
        verbose_name_plural = "产品特点"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.title


class ProductApplication(models.Model):
    product = models.ForeignKey(Product, verbose_name="产品", related_name="applications", on_delete=models.CASCADE)
    name = models.CharField("场景名称", max_length=100)
    description = models.CharField("场景说明", max_length=250, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "应用场景"
        verbose_name_plural = "应用场景"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class ProductDocument(models.Model):
    class DocumentType(models.TextChoices):
        MANUAL = "manual", "说明书"
        CATALOG = "catalog", "产品目录"
        CERTIFICATE = "certificate", "认证文件"
        OTHER = "other", "其他"

    class Language(models.TextChoices):
        ZH = "zh", "中文"
        EN = "en", "英文"
        DE = "de", "德语"
        ES = "es", "西班牙语"
        FR = "fr", "法语"
        RU = "ru", "俄语"
        AR = "ar", "阿拉伯语"
        OTHER = "other", "其他"

    product = models.ForeignKey(Product, verbose_name="产品", related_name="documents", on_delete=models.CASCADE)
    name = models.CharField("资料名称", max_length=150)
    document_type = models.CharField("资料类型", max_length=30, choices=DocumentType.choices)
    language = models.CharField("语言", max_length=20, choices=Language.choices, default=Language.ZH)
    file = models.FileField("PDF 文件", upload_to="products/documents/", validators=[validate_pdf_upload])
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "产品资料"
        verbose_name_plural = "产品资料"
        ordering = ("sort_order", "id")

    def delete(self, *args, **kwargs):
        field_file = self.file
        result = super().delete(*args, **kwargs)
        delete_field_file(field_file)
        return result

    def __str__(self):
        return self.name

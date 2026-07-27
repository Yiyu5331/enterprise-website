from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from main.content_utils import (
    ContentStatus,
    delete_field_file,
    process_uploaded_image,
    rich_text_images_have_alt,
    rich_text_to_plain,
    sanitize_rich_text,
    validate_image_upload,
)


class NewsCategory(models.Model):
    name = models.CharField("分类名称", max_length=100, unique=True)
    slug = models.SlugField("固定 slug", max_length=100, unique=True)
    description = models.CharField("分类说明", max_length=300, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "新闻分类"
        verbose_name_plural = "新闻分类"
        ordering = ("sort_order", "id")
        indexes = [models.Index(fields=("is_active", "sort_order"))]

    def clean(self):
        if self.pk:
            old_slug = type(self).objects.filter(pk=self.pk).values_list("slug", flat=True).first()
            if old_slug and old_slug != self.slug:
                raise ValidationError({"slug": "分类创建后不能修改 slug。"})

    def delete(self, *args, **kwargs):
        if self.articles.exists():
            raise ValidationError("分类下仍有新闻，不能删除；请改为停用。")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(
        NewsCategory,
        verbose_name="新闻分类",
        related_name="articles",
        on_delete=models.PROTECT,
    )
    title = models.CharField("新闻标题", max_length=200)
    slug = models.SlugField("固定 slug", max_length=180, unique=True)
    summary = models.CharField("摘要", max_length=300, blank=True)
    body = models.TextField("新闻正文")
    body_text = models.TextField("正文纯文本", blank=True, editable=False)
    cover = models.ImageField(
        "新闻封面",
        upload_to="news/original/",
        blank=True,
        validators=[validate_image_upload],
    )
    cover_web = models.ImageField("网页封面", upload_to="news/web/", blank=True, editable=False)
    cover_thumb = models.ImageField("封面缩略图", upload_to="news/thumbs/", blank=True, editable=False)
    cover_alt = models.CharField("封面 Alt", max_length=200, blank=True)
    focal_x = models.FloatField("焦点 X", default=0.5)
    focal_y = models.FloatField("焦点 Y", default=0.5)
    source = models.CharField("公开来源", max_length=100, default="华丽电器")
    published_at = models.DateTimeField("发布时间", null=True, blank=True)
    first_published_at = models.DateTimeField("首次发布时间", null=True, blank=True, editable=False)
    status = models.CharField("状态", max_length=20, choices=ContentStatus.choices, default=ContentStatus.DRAFT)
    is_featured = models.BooleanField("首页推荐", default=False)
    featured_order = models.PositiveIntegerField("推荐排序", default=0)
    seo_title = models.CharField("SEO 标题", max_length=160, blank=True)
    seo_description = models.CharField("SEO 描述", max_length=300, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        related_name="created_articles",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="最后修改人",
        related_name="updated_articles",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "新闻"
        verbose_name_plural = "新闻"
        ordering = ("-published_at", "-id")
        indexes = [
            models.Index(fields=("status", "published_at")),
            models.Index(fields=("category", "status", "published_at")),
            models.Index(fields=("is_featured", "featured_order")),
        ]

    def clean(self):
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).values("slug", "first_published_at").first()
            if old and old["first_published_at"] and old["slug"] != self.slug:
                raise ValidationError({"slug": "新闻发布后不能修改 slug。"})
        if self.status == ContentStatus.PUBLISHED:
            errors = {}
            if not self.cover:
                errors["cover"] = "发布新闻前必须上传封面图。"
            if not self.cover_alt:
                errors["cover_alt"] = "发布新闻前必须填写封面替代文本。"
            if not self.published_at:
                errors["published_at"] = "发布新闻前必须设置发布时间。"
            if not rich_text_to_plain(self.body):
                errors["body"] = "发布新闻前必须填写正文。"
            if not rich_text_images_have_alt(self.body):
                errors["body"] = "正文中的每张图片都必须包含 alt 属性。"
            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.body = sanitize_rich_text(self.body)
        self.body_text = rich_text_to_plain(self.body)
        if not self.summary:
            self.summary = self.body_text[:120]

        new_upload = bool(self.cover and not self.cover._committed)
        old_files = []
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        if old and (new_upload or old.focal_x != self.focal_x or old.focal_y != self.focal_y):
            old_files = [old.cover, old.cover_web, old.cover_thumb]

        if new_upload:
            original, web, thumb = process_uploaded_image(
                self.cover.file,
                prefix="news-cover",
                thumb_size=(960, 540),
                focal_x=self.focal_x,
                focal_y=self.focal_y,
            )
            self.cover.save(original.name, original, save=False)
            self.cover_web.save(web.name, web, save=False)
            self.cover_thumb.save(thumb.name, thumb, save=False)
        elif old and self.cover and (old.focal_x != self.focal_x or old.focal_y != self.focal_y):
            with self.cover.storage.open(self.cover.name, "rb") as source:
                _, web, thumb = process_uploaded_image(
                    source,
                    prefix="news-cover",
                    thumb_size=(960, 540),
                    focal_x=self.focal_x,
                    focal_y=self.focal_y,
                )
            self.cover_web.save(web.name, web, save=False)
            self.cover_thumb.save(thumb.name, thumb, save=False)

        super().save(*args, **kwargs)
        for field_file in (self.cover, self.cover_web, self.cover_thumb):
            if field_file:
                field_file.close()
        current_names = {self.cover.name, self.cover_web.name, self.cover_thumb.name}
        for field_file in old_files:
            if field_file and field_file.name not in current_names:
                delete_field_file(field_file)

    def delete(self, *args, **kwargs):
        files = [self.cover, self.cover_web, self.cover_thumb]
        result = super().delete(*args, **kwargs)
        for field_file in files:
            delete_field_file(field_file)
        return result

    def __str__(self):
        return self.title

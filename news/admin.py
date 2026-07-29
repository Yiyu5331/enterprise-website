from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from main.admin_filters import DefaultDateRangeAdminMixin
from main.content_utils import ContentStatus
from operations.models import AuditLog

from .forms import ArticleAdminForm
from .models import Article, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active", "updated_at", "edit_link")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "slug", "description")
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def delete_model(self, request, obj):
        AuditLog.objects.create(actor=request.user, action="article_deleted", target_type="article", target_id=str(obj.pk), summary="超级管理员删除新闻")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            AuditLog.objects.create(actor=request.user, action="article_deleted", target_type="article", target_id=str(obj.pk), summary="超级管理员批量删除新闻")
        super().delete_queryset(request, queryset)

    @admin.display(description="操作")
    def edit_link(self, obj):
        url = reverse("admin:news_newscategory_change", args=[obj.pk])
        return format_html('<a href="{}">编辑</a>', url)


@admin.register(Article)
class ArticleAdmin(DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "published_at"
    form = ArticleAdminForm
    list_display = (
        "cover_preview", "title", "category", "status", "is_demo", "verification_status",
        "is_featured", "source", "published_at", "updated_at", "edit_link",
    )
    list_filter = ("status", "verification_status", "is_demo", "category", "is_featured", "source", "published_at")
    search_fields = ("title", "summary", "source", "body_text")
    readonly_fields = ("cover_preview_large", "cover_web", "cover_thumb", "first_published_at", "created_by_display", "updated_by_display", "created_at", "updated_at")
    list_per_page = 20
    actions = ("publish_selected", "draft_selected", "archive_selected", "feature_selected", "unfeature_selected")
    fieldsets = (
        ("基本信息", {"fields": ("category", "title", "slug", "summary", "source", "body")}),
        ("封面与焦点", {"fields": ("cover", "cover_alt", "cover_preview_large", "focal_x", "focal_y")}),
        ("测试与核验", {"fields": ("is_demo", "verification_status", "source_url", "verified_at")}),
        ("发布与推荐", {"fields": ("status", "published_at", "is_featured", "featured_order")}),
        ("SEO", {"fields": ("seo_title", "seo_description")}),
        ("记录信息", {"fields": ("first_published_at", "created_by_display", "updated_by_display", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.first_published_at and not request.user.is_superuser:
            fields.append("slug")
        return fields

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        if obj.status == ContentStatus.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        if obj.status == ContentStatus.PUBLISHED and not obj.first_published_at:
            obj.first_published_at = timezone.now()
        obj.full_clean()
        super().save_model(request, obj, form, change)
        AuditLog.objects.create(actor=request.user, action="article_saved", target_type="article", target_id=str(obj.pk), summary=f"保存新闻，状态：{obj.status}，推荐：{obj.is_featured}")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="操作")
    def edit_link(self, obj):
        url = reverse("admin:news_article_change", args=[obj.pk])
        return format_html('<a href="{}">编辑</a>', url)

    @admin.display(description="封面")
    def cover_preview(self, obj):
        if not obj.cover_thumb:
            return "无"
        return format_html('<img src="{}" style="width:86px;height:48px;object-fit:cover">', obj.cover_thumb.url)

    @admin.display(description="封面预览")
    def cover_preview_large(self, obj):
        if not obj or not obj.cover_web:
            return "上传后生成预览"
        return format_html(
            '<div class="focal-point-preview" data-focal-preview>'
            '<img src="{}" alt="封面焦点预览"><span class="focal-point-marker"></span></div>'
            '<div class="focal-point-help">点击图片设置缩略图裁切焦点。</div>',
            obj.cover_web.url,
        )

    class Media:
        css = {"all": ("admin/content_editor/editor.css", "admin/date_range_split.css")}
        js = ("admin/content_editor/editor.js", "admin/date_range_split.js")

    @admin.display(description="创建人")
    def created_by_display(self, obj):
        return obj.created_by or "系统导入"

    @admin.display(description="最后修改人")
    def updated_by_display(self, obj):
        return obj.updated_by or "系统导入"

    def _bulk_status(self, request, queryset, status):
        success = 0
        failures = []
        for article in queryset:
            old_status = article.status
            article.status = status
            if status == ContentStatus.PUBLISHED and not article.published_at:
                article.published_at = timezone.now()
            if status == ContentStatus.PUBLISHED and not article.first_published_at:
                article.first_published_at = timezone.now()
            article.updated_by = request.user
            try:
                article.full_clean()
                article.save()
                AuditLog.objects.create(actor=request.user, action="article_bulk_status", target_type="article", target_id=str(article.pk), summary=f"批量修改新闻状态为 {status}")
                success += 1
            except ValidationError as exc:
                article.status = old_status
                failures.append(f"{article}: {' '.join(exc.messages)}")
        if success:
            self.message_user(request, f"成功处理 {success} 条新闻。", messages.SUCCESS)
        if failures:
            self.message_user(request, "；".join(failures), messages.ERROR)

    @admin.action(description="发布所选新闻")
    def publish_selected(self, request, queryset):
        self._bulk_status(request, queryset, ContentStatus.PUBLISHED)

    @admin.action(description="转为草稿")
    def draft_selected(self, request, queryset):
        self._bulk_status(request, queryset, ContentStatus.DRAFT)

    @admin.action(description="归档所选新闻")
    def archive_selected(self, request, queryset):
        self._bulk_status(request, queryset, ContentStatus.ARCHIVED)

    @admin.action(description="设为首页推荐")
    def feature_selected(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="取消首页推荐")
    def unfeature_selected(self, request, queryset):
        queryset.update(is_featured=False)

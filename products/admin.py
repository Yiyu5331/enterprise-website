from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from main.content_utils import ContentStatus
from main.admin_filters import DefaultDateRangeAdminMixin
from operations.models import AuditLog

from .forms import (
    ApplicationInlineFormSet,
    HighlightInlineFormSet,
    ProductAdminForm,
    SpecificationInlineFormSet,
)
from .models import (
    Product,
    ProductApplication,
    ProductCategory,
    ProductDocument,
    ProductGalleryImage,
    ProductHighlight,
    ProductSpecification,
    ProductTag,
    ParameterMappingSuggestion,
    StandardParameter,
    StandardParameterOption,
)


class SortableInline(admin.TabularInline):
    extra = 0
    ordering = ("sort_order", "id")


class ProductGalleryInline(SortableInline):
    model = ProductGalleryImage
    fields = ("image", "alt_text", "caption", "focal_x", "focal_y", "sort_order")


class ProductSpecificationInline(SortableInline):
    model = ProductSpecification
    formset = SpecificationInlineFormSet
    fields = ("name", "value", "standard_parameter", "normalized_number", "normalized_text", "show_on_card", "sort_order")


class ProductHighlightInline(SortableInline):
    model = ProductHighlight
    formset = HighlightInlineFormSet


class ProductApplicationInline(SortableInline):
    model = ProductApplication
    formset = ApplicationInlineFormSet


class ProductDocumentInline(SortableInline):
    model = ProductDocument


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("cover_preview", "name", "slug", "sort_order", "is_active", "updated_at", "edit_link")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "slug", "description")
    readonly_fields = ("cover_preview_large", "image_web", "image_thumb", "created_at", "updated_at")
    fields = (
        "name", "slug", "description", "image", "cover_preview_large",
        "focal_x", "focal_y", "sort_order", "is_active", "created_at", "updated_at",
    )

    @admin.display(description="封面")
    def cover_preview(self, obj):
        if not obj.image_thumb:
            return "无"
        return format_html('<img src="{}" style="width:72px;height:48px;object-fit:cover">', obj.image_thumb.url)

    @admin.display(description="当前封面预览")
    def cover_preview_large(self, obj):
        if not obj or not obj.image_web:
            return "上传后生成预览"
        return format_html('<img src="{}" style="max-width:420px;max-height:240px;object-fit:cover">', obj.image_web.url)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def delete_model(self, request, obj):
        AuditLog.objects.create(actor=request.user, action="product_deleted", target_type="product", target_id=str(obj.pk), summary="超级管理员删除产品")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            AuditLog.objects.create(actor=request.user, action="product_deleted", target_type="product", target_id=str(obj.pk), summary="超级管理员批量删除产品")
        super().delete_queryset(request, queryset)

    @admin.display(description="操作")
    def edit_link(self, obj):
        url = reverse("admin:products_productcategory_change", args=[obj.pk])
        return format_html('<a href="{}">编辑</a>', url)


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active", "edit_link")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "slug")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="操作")
    def edit_link(self, obj):
        url = reverse("admin:products_producttag_change", args=[obj.pk])
        return format_html('<a href="{}">编辑</a>', url)


@admin.register(Product)
class ProductAdmin(DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "updated_at"
    form = ProductAdminForm
    inlines = (
        ProductGalleryInline,
        ProductSpecificationInline,
        ProductHighlightInline,
        ProductApplicationInline,
        ProductDocumentInline,
    )
    list_display = (
        "image_preview", "name", "model", "category", "level", "status",
        "is_demo", "verification_status", "is_featured", "sort_order", "gallery_count", "document_count",
        "first_published_at", "created_at", "updated_at", "edit_link",
    )
    list_filter = ("status", "verification_status", "is_demo", "category", "is_featured", "tags", "level", "updated_at")
    search_fields = ("name", "model", "summary", "search_text")
    filter_horizontal = ("tags", "related_products")
    readonly_fields = (
        "image_preview_large", "image_web", "image_thumb", "first_published_at",
        "created_by_display", "updated_by_display", "created_at", "updated_at",
    )
    list_per_page = 20
    actions = ("publish_selected", "draft_selected", "archive_selected", "feature_selected", "unfeature_selected")
    fieldsets = (
        ("基本信息", {"fields": ("category", "tags", "name", "model", "level", "summary", "description")}),
        ("主图与焦点", {"fields": ("image", "image_preview_large", "focal_x", "focal_y")}),
        ("测试与核验", {"fields": ("is_demo", "verification_status", "source_name", "source_url", "verified_at")}),
        ("发布与推荐", {"fields": ("status", "sort_order", "is_featured", "featured_order", "homepage_badge", "related_products")}),
        ("SEO", {"fields": ("seo_title", "seo_description")}),
        ("记录信息", {"fields": ("first_published_at", "created_by_display", "updated_by_display", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.first_published_at and not request.user.is_superuser:
            fields.append("model")
        return fields

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        if obj.status == ContentStatus.PUBLISHED and not obj.first_published_at:
            obj.first_published_at = timezone.now()
        super().save_model(request, obj, form, change)
        AuditLog.objects.create(actor=request.user, action="product_saved", target_type="product", target_id=str(obj.pk), summary=f"保存产品，状态：{obj.status}，推荐：{obj.is_featured}")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.instance.status == ContentStatus.PUBLISHED:
            form.instance.validate_for_publish()
        form.instance.rebuild_search_text()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="操作")
    def edit_link(self, obj):
        url = reverse("admin:products_product_change", args=[obj.pk])
        return format_html('<a href="{}">编辑</a>', url)

    @admin.display(description="主图")
    def image_preview(self, obj):
        if not obj.image_thumb:
            return "无"
        return format_html('<img src="{}" style="width:72px;height:48px;object-fit:cover">', obj.image_thumb.url)

    @admin.display(description="主图预览")
    def image_preview_large(self, obj):
        if not obj or not obj.image_web:
            return "上传后生成预览"
        return format_html(
            '<div class="focal-point-preview" data-focal-preview>'
            '<img src="{}" alt="主图焦点预览"><span class="focal-point-marker"></span></div>'
            '<div class="focal-point-help">点击图片设置缩略图裁切焦点。</div>',
            obj.image_web.url,
        )

    class Media:
        css = {"all": ("admin/content_editor/editor.css", "admin/date_range_split.css")}
        js = ("admin/content_editor/editor.js", "admin/date_range_split.js")

    @admin.display(description="图库数")
    def gallery_count(self, obj):
        return obj.gallery.count()

    @admin.display(description="资料数")
    def document_count(self, obj):
        return obj.documents.count()

    @admin.display(description="创建人")
    def created_by_display(self, obj):
        return obj.created_by or "系统导入"

    @admin.display(description="最后修改人")
    def updated_by_display(self, obj):
        return obj.updated_by or "系统导入"

    def _bulk_status(self, request, queryset, status):
        success = 0
        failures = []
        for obj in queryset:
            old_status = obj.status
            obj.status = status
            try:
                if status == ContentStatus.PUBLISHED:
                    obj.validate_for_publish()
                    if not obj.first_published_at:
                        obj.first_published_at = timezone.now()
                obj.updated_by = request.user
                obj.save()
                AuditLog.objects.create(actor=request.user, action="product_bulk_status", target_type="product", target_id=str(obj.pk), summary=f"批量修改产品状态为 {status}")
                success += 1
            except ValidationError as exc:
                obj.status = old_status
                failures.append(f"{obj}: {' '.join(exc.messages)}")
        if success:
            self.message_user(request, f"成功处理 {success} 条产品。", messages.SUCCESS)
        if failures:
            self.message_user(request, "；".join(failures), messages.ERROR)

    @admin.action(description="发布所选产品")
    def publish_selected(self, request, queryset):
        self._bulk_status(request, queryset, ContentStatus.PUBLISHED)

    @admin.action(description="转为草稿")
    def draft_selected(self, request, queryset):
        self._bulk_status(request, queryset, ContentStatus.DRAFT)

    @admin.action(description="归档所选产品")
    def archive_selected(self, request, queryset):
        self._bulk_status(request, queryset, ContentStatus.ARCHIVED)

    @admin.action(description="设为首页推荐")
    def feature_selected(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="取消首页推荐")
    def unfeature_selected(self, request, queryset):
        queryset.update(is_featured=False)


class StandardParameterOptionInline(admin.TabularInline):
    model = StandardParameterOption
    extra = 0


@admin.register(StandardParameter)
class StandardParameterAdmin(admin.ModelAdmin):
    list_display = ("name_zh", "name_en", "slug", "value_type", "standard_unit", "sort_order", "is_active")
    list_filter = ("value_type", "is_active")
    search_fields = ("name_zh", "name_en", "slug", "aliases_zh", "aliases_en")
    list_editable = ("sort_order", "is_active")
    inlines = (StandardParameterOptionInline,)


@admin.register(ParameterMappingSuggestion)
class ParameterMappingSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "source_name", "suggested_parameter", "confidence", "affected_count",
        "status", "reviewed_by", "reviewed_at",
    )
    list_filter = ("status", "suggested_parameter")
    search_fields = ("source_name", "matched_alias", "suggested_parameter__name_zh")
    readonly_fields = (
        "source_name", "suggested_parameter", "matched_alias", "confidence",
        "affected_count", "reviewed_by", "reviewed_at", "created_at", "updated_at",
    )
    actions = ("accept_selected", "reject_selected")

    @admin.action(description="接受建议并映射同名参数")
    def accept_selected(self, request, queryset):
        count = 0
        for suggestion in queryset.select_related("suggested_parameter"):
            ProductSpecification.objects.filter(
                name=suggestion.source_name,
                standard_parameter__isnull=True,
            ).update(standard_parameter=suggestion.suggested_parameter)
            suggestion.status = ParameterMappingSuggestion.Status.ACCEPTED
            suggestion.reviewed_by = request.user
            suggestion.reviewed_at = timezone.now()
            suggestion.save(update_fields=("status", "reviewed_by", "reviewed_at", "updated_at"))
            count += 1
        self.message_user(request, f"已接受 {count} 条参数映射建议。")

    @admin.action(description="拒绝所选映射建议")
    def reject_selected(self, request, queryset):
        count = queryset.update(
            status=ParameterMappingSuggestion.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"已拒绝 {count} 条参数映射建议。")

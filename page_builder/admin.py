from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from main.admin_filters import DefaultDateRangeAdminMixin

from .models import AssetLicense, AssetSlot, MediaFolder, MediaTag, MediaUsage, PublicMediaAsset


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("name",)


@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(AssetLicense)
class AssetLicenseAdmin(admin.ModelAdmin):
    list_display = ("name", "license_type", "author", "allows_commercial_use", "source_url")
    list_filter = ("license_type", "allows_commercial_use")
    search_fields = ("name", "author", "source_url", "attribution")


@admin.register(PublicMediaAsset)
class PublicMediaAssetAdmin(DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "created_at"
    list_display = (
        "title", "asset_type", "origin", "folder", "needs_replacement",
        "is_approved", "license", "usage_count", "created_at",
    )
    list_filter = ("asset_type", "origin", "needs_replacement", "is_approved", "folder", "created_at")
    search_fields = ("title", "alt_zh", "alt_en", "generation_prompt", "sha256")
    filter_horizontal = ("tags",)
    readonly_fields = ("size", "sha256", "width", "height", "created_at", "updated_at", "mode_notice")
    fieldsets = (
        ("素材文件", {"fields": ("title", "folder", "tags", "asset_type", "origin", "file", "desktop_file", "mobile_file", "preview_image")}),
        ("可访问性与裁切", {"fields": ("alt_zh", "alt_en", "alt_reviewed", "is_decorative", "focal_x_desktop", "focal_y_desktop", "focal_x_mobile", "focal_y_mobile")}),
        ("许可与 AI 记录", {"fields": ("license", "generation_prompt", "generation_model", "generated_at", "needs_replacement", "is_approved")}),
        ("文件信息", {"fields": ("size", "sha256", "width", "height", "created_at", "updated_at", "mode_notice"), "classes": ("collapse",)}),
    )

    @admin.display(description="内容模式")
    def mode_notice(self, obj=None):
        mode = settings.SITE_CONTENT_MODE
        color = "#c41e24" if mode == "production" else "#287a45"
        return format_html('<strong style="color:{}">当前为 {} 模式</strong>', color, mode)

    @admin.display(description="引用数")
    def usage_count(self, obj):
        return obj.usages.count() + obj.active_slots.count()


@admin.register(AssetSlot)
class AssetSlotAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "recommended_ratio", "min_width", "min_height", "current_asset", "updated_at")
    search_fields = ("name", "key", "description")
    readonly_fields = ("updated_at",)


@admin.register(MediaUsage)
class MediaUsageAdmin(admin.ModelAdmin):
    list_display = ("asset", "owner_type", "owner_key", "slot_key", "is_override", "created_at")
    list_filter = ("owner_type", "is_override")
    search_fields = ("asset__title", "owner_type", "owner_key", "slot_key")
    readonly_fields = ("created_at",)

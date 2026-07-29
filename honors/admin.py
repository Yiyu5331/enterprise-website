from django.contrib import admin

from main.admin_filters import DefaultDateRangeAdminMixin

from .models import Honor, HonorCategory


@admin.register(HonorCategory)
class HonorCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "slug", "description")


@admin.register(Honor)
class HonorAdmin(DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "updated_at"
    list_display = (
        "title", "category", "status", "verification_status", "is_demo",
        "awarded_on", "allow_document_download", "updated_at",
    )
    list_filter = ("category", "status", "verification_status", "is_demo", "allow_document_download", "updated_at")
    search_fields = ("title", "summary", "reference_number", "issuer")
    readonly_fields = ("created_at", "updated_at")

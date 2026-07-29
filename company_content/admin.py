from django.contrib import admin

from main.admin_filters import DefaultDateRangeAdminMixin

from .models import (
    CompanyFact, CompanyProfile, CompanyTimeline, ContentSource, DealerBenefit,
    FAQ, FAQCategory, Location, SupplyChainItem,
)


class PublishableAdmin(DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "updated_at"
    list_filter = ("status", "verification_status", "is_demo", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ContentSource)
class ContentSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "verified_by", "verified_at", "is_public", "created_at")
    list_filter = ("is_public", "verified_at")
    search_fields = ("name", "url", "notes")
    readonly_fields = ("created_at",)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(PublishableAdmin):
    list_display = ("name_zh", "brand_name", "status", "verification_status", "is_demo", "updated_at")
    search_fields = ("name_zh", "name_en", "brand_name", "credit_code")


@admin.register(CompanyFact)
class CompanyFactAdmin(PublishableAdmin):
    list_display = ("label", "value", "unit", "status", "verification_status", "is_demo", "sort_order", "updated_at")
    search_fields = ("label", "value", "description")
    list_editable = ("sort_order",)


@admin.register(CompanyTimeline)
class CompanyTimelineAdmin(PublishableAdmin):
    list_display = ("year", "title", "status", "verification_status", "is_demo", "sort_order", "updated_at")
    search_fields = ("title", "description")


@admin.register(SupplyChainItem)
class SupplyChainItemAdmin(PublishableAdmin):
    list_display = ("title", "kind", "status", "verification_status", "is_demo", "sort_order", "updated_at")
    list_filter = ("kind", "status", "verification_status", "is_demo", "updated_at")
    search_fields = ("title", "description")


@admin.register(DealerBenefit)
class DealerBenefitAdmin(PublishableAdmin):
    list_display = ("title", "status", "verification_status", "is_demo", "sort_order", "updated_at")
    search_fields = ("title", "description")


@admin.register(Location)
class LocationAdmin(PublishableAdmin):
    list_display = ("name", "kind", "address_zh", "status", "verification_status", "is_demo", "updated_at")
    list_filter = ("kind", "status", "verification_status", "is_demo", "updated_at")
    search_fields = ("name", "address_zh", "address_en", "phone", "email")


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "slug")


@admin.register(FAQ)
class FAQAdmin(PublishableAdmin):
    list_display = ("question", "category", "status", "verification_status", "is_demo", "sort_order", "updated_at")
    list_filter = ("category", "status", "verification_status", "is_demo", "updated_at")
    search_fields = ("question", "answer")

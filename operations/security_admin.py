from django.contrib import admin

from axes.models import AccessAttempt, AccessFailureLog, AccessLog
from django_otp.plugins.otp_totp.models import TOTPDevice

from main.admin_filters import DefaultDateRangeAdminMixin


class SecurityDateRangeAdminMixin(DefaultDateRangeAdminMixin):
    class Media:
        css = {"all": ("admin/date_range_split.css",)}
        js = ("admin/date_range_split.js",)


def replace_admin(model):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


class BilingualSecurityAdmin(SecurityDateRangeAdminMixin, admin.ModelAdmin):
    list_per_page = 20
    ordering = ("-attempt_time",)
    readonly_fields = tuple(field.name for field in AccessAttempt._meta.fields)


class AccessAttemptAdmin(BilingualSecurityAdmin):
    date_range_field = "attempt_time"
    list_display = ("username", "ip_address", "path_info", "failures_since_start", "attempt_time")
    list_filter = ("attempt_time",)
    search_fields = ("username", "ip_address", "path_info")
    fieldsets = (
        ("登录信息（Login information）", {"fields": ("username", "ip_address", "path_info", "attempt_time")}),
        ("请求信息（Request information）", {"fields": ("user_agent", "http_accept", "get_data", "post_data")}),
        ("失败统计（Failure statistics）", {"fields": ("failures_since_start",)}),
    )


class AccessFailureLogAdmin(BilingualSecurityAdmin):
    date_range_field = "attempt_time"
    list_display = ("username", "ip_address", "path_info", "locked_out", "attempt_time")
    list_filter = ("locked_out", "attempt_time")
    search_fields = ("username", "ip_address", "path_info")
    readonly_fields = tuple(field.name for field in AccessFailureLog._meta.fields)
    fieldsets = (
        ("登录信息（Login information）", {"fields": ("username", "ip_address", "path_info", "attempt_time", "locked_out")}),
        ("客户端信息（Client information）", {"fields": ("user_agent", "http_accept")}),
    )


class AccessLogAdmin(BilingualSecurityAdmin):
    date_range_field = "attempt_time"
    list_display = ("username", "ip_address", "path_info", "attempt_time", "logout_time")
    list_filter = ("attempt_time",)
    search_fields = ("username", "ip_address", "path_info")
    readonly_fields = tuple(field.name for field in AccessLog._meta.fields)
    fieldsets = (
        ("登录信息（Login information）", {"fields": ("username", "ip_address", "path_info", "attempt_time", "logout_time")}),
        ("会话信息（Session information）", {"fields": ("session_hash",)}),
        ("客户端信息（Client information）", {"fields": ("user_agent", "http_accept")}),
    )


class TOTPDeviceAdmin(SecurityDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "created_at"
    list_display = ("name", "user", "confirmed", "created_at", "last_used_at")
    list_filter = ("confirmed", "created_at")
    search_fields = ("name", "user__username", "user__email")
    list_per_page = 20
    readonly_fields = ("key", "created_at", "last_used_at", "throttling_failure_timestamp", "throttling_failure_count", "last_t", "drift")
    fieldsets = (
        ("设备信息（Device information）", {"fields": ("user", "name", "confirmed")}),
        ("验证参数（Verification settings）", {"fields": ("step", "digits", "tolerance", "t0")}),
        ("密钥与使用记录（Secret and usage records）", {"fields": ("key", "created_at", "last_used_at", "last_t", "drift")}),
        ("失败限制（Failure throttling）", {"fields": ("throttling_failure_timestamp", "throttling_failure_count")}),
    )


replace_admin(AccessAttempt)
admin.site.register(AccessAttempt, AccessAttemptAdmin)
replace_admin(AccessFailureLog)
admin.site.register(AccessFailureLog, AccessFailureLogAdmin)
replace_admin(AccessLog)
admin.site.register(AccessLog, AccessLogAdmin)
replace_admin(TOTPDevice)
admin.site.register(TOTPDevice, TOTPDeviceAdmin)

from django.contrib import admin
from django.contrib.admin import helpers
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    AuditLog, BackupRecord, CaptchaChallenge, EmailAttachment, EmailTask,
    EmailTemplate, FormToken, PrerenderTask, PrivacyPolicy, RecoveryCode,
    SystemAlert, TaskRun,
)
from .health import health_snapshot
from .signals import DEFAULT_TEMPLATES
from .emailing import create_email_task

original_index = admin.site.index


def operations_index(request, extra_context=None):
    context = dict(extra_context or {})
    context["health_snapshot"] = health_snapshot()
    context["two_factor_setup_url"] = reverse("operations:two-factor-setup")
    return original_index(request, context)


admin.site.index = operations_index
admin.site.index_template = "admin/operations_index.html"


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ("version", "status", "published_at", "created_at", "edit_link")
    list_filter = ("status",)
    search_fields = ("version", "title_zh", "title_en")
    readonly_fields = ("published_at", "created_at")
    actions = ("publish_selected", "retire_selected")
    change_form_template = "admin/operations/privacypolicy/change_form.html"

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if request.method == "POST" and "_publish" in request.POST:
            request.POST = request.POST.copy()
            request.POST["status"] = PrivacyPolicy.Status.PUBLISHED
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.action(description="发布所选隐私政策（生成正式版本）")
    def publish_selected(self, request, queryset):
        count = 0
        for policy in queryset:
            if policy.status == PrivacyPolicy.Status.PUBLISHED:
                continue
            policy.status = PrivacyPolicy.Status.PUBLISHED
            policy.save()
            count += 1
        self.message_user(request, f"已发布 {count} 个隐私政策版本。")

    @admin.action(description="停用所选隐私政策")
    def retire_selected(self, request, queryset):
        updated = queryset.exclude(status=PrivacyPolicy.Status.RETIRED).update(status=PrivacyPolicy.Status.RETIRED)
        self.message_user(request, f"已停用 {updated} 个隐私政策版本。")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.status == PrivacyPolicy.Status.PUBLISHED:
            fields.extend(("version", "title_zh", "body_zh", "title_en", "body_en", "status"))
        return fields

    @admin.display(description="编辑")
    def edit_link(self, obj):
        url = reverse("admin:operations_privacypolicy_change", args=(obj.pk,))
        return format_html('<a href="{}">编辑此版本</a>', url)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "key", "subject")
    readonly_fields = ("key", "allowed_variables", "updated_at")
    actions = ("restore_defaults", "send_test_email")

    @admin.action(description="恢复所选模板的系统默认内容")
    def restore_defaults(self, request, queryset):
        count = 0
        for template in queryset:
            defaults = DEFAULT_TEMPLATES.get(template.key)
            if not defaults:
                continue
            for field in ("name", "subject", "html_body", "text_body", "allowed_variables"):
                setattr(template, field, defaults[field])
            template.save()
            count += 1
        self.message_user(request, f"已恢复 {count} 个邮件模板。")

    @admin.action(description="向当前管理员邮箱发送所选模板测试邮件")
    def send_test_email(self, request, queryset):
        if not request.user.email:
            self.message_user(request, "当前管理员没有邮箱，无法发送测试邮件。", level="error")
            return
        count = 0
        context = {
            "lead_type": "测试线索",
            "contact_name": "测试客户",
            "email": "customer@example.com",
            "phone": "13800000000",
            "summary": "这是一封模板测试邮件。",
            "message": "这是一封模板测试邮件。",
        }
        for template in queryset.filter(is_active=True):
            task = create_email_task(
                template.key,
                [request.user.email],
                context,
                kind=EmailTask.Kind.CUSTOMER_RECEIPT,
                created_by=request.user,
            )
            count += bool(task)
        self.message_user(request, f"已创建 {count} 个测试邮件任务，请运行邮件队列。")


class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0
    readonly_fields = ("original_name", "size", "scan_status")


@admin.register(EmailTask)
class EmailTaskAdmin(admin.ModelAdmin):
    list_display = ("subject", "kind", "recipient_preview", "status", "attempts", "sent_at", "created_at")
    list_filter = ("kind", "status", "created_at")
    search_fields = ("subject", "recipients", "last_error")
    readonly_fields = ("template", "kind", "inquiry", "contact", "recipients", "subject", "html_body", "text_body", "status", "attempts", "next_attempt_at", "last_error", "sent_at", "created_by", "created_at")
    inlines = (EmailAttachmentInline,)

    @admin.display(description="收件人")
    def recipient_preview(self, obj):
        return ", ".join(obj.recipients)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(ReadOnlyAdmin):
    list_display = ("created_at", "actor", "action", "target_type", "target_id", "summary")
    list_filter = ("action", "created_at")
    search_fields = ("actor__username", "action", "target_type", "target_id", "summary")
    readonly_fields = tuple(field.name for field in AuditLog._meta.fields)


@admin.register(TaskRun)
class TaskRunAdmin(ReadOnlyAdmin):
    list_display = ("kind", "status", "summary", "started_at", "finished_at")
    list_filter = ("kind", "status")
    readonly_fields = tuple(field.name for field in TaskRun._meta.fields)


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ("level", "source", "message", "resolved_at", "created_at")
    list_filter = ("level", "source", "resolved_at")
    readonly_fields = ("level", "source", "message", "created_at")


@admin.register(PrerenderTask)
class PrerenderTaskAdmin(ReadOnlyAdmin):
    list_display = ("path", "reason", "pending", "updated_at")
    list_filter = ("pending",)
    readonly_fields = tuple(field.name for field in PrerenderTask._meta.fields)


@admin.register(BackupRecord)
class BackupRecordAdmin(ReadOnlyAdmin):
    list_display = ("filename", "size", "status", "remote_uploaded", "created_at")
    list_filter = ("status", "remote_uploaded")
    readonly_fields = tuple(field.name for field in BackupRecord._meta.fields)


admin.site.register(FormToken, ReadOnlyAdmin)
admin.site.register(CaptchaChallenge, ReadOnlyAdmin)
admin.site.register(RecoveryCode, ReadOnlyAdmin)

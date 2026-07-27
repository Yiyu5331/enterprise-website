import csv
from io import BytesIO

from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from openpyxl import Workbook

from .admin_filters import DefaultDateRangeAdminMixin
from .models import LeadStatus, Lianxi, Xunpan
from operations.emailing import create_email_task
from operations.forms import FollowUpEmailForm
from operations.models import AuditLog, EmailAttachment, EmailTask, EmailTemplate


def export_csv(response, headers, rows):
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def export_xlsx(filename, headers, rows):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "数据导出"
    worksheet.append(headers)
    for row in rows:
        worksheet.append(list(row))
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    for column_cells in worksheet.columns:
        width = min(max(max(len(str(cell.value or "")) for cell in column_cells) + 2, 10), 42)
        worksheet.column_dimensions[column_cells[0].column_letter].width = width
    output = BytesIO()
    workbook.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class LeadAdminMixin:
    change_form_template = "admin/main/lead/change_form.html"

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path("<path:object_id>/follow-up/", self.admin_site.admin_view(self.follow_up_view), name="%s_%s_follow_up" % info),
        ] + super().get_urls()

    def follow_up_view(self, request, object_id):
        lead = get_object_or_404(self.model, pk=object_id)
        template = EmailTemplate.objects.filter(key="follow-up", is_active=True).first()
        initial = {
            "recipient": lead.email,
            "subject": template.subject if template else "关于您向华丽电器提交的需求",
            "text_body": (template.text_body if template else "{{ contact_name }}，您好！")
                .replace("{{ contact_name }}", lead.contact_name)
                .replace("{{ message }}", ""),
            "html_body": (template.html_body if template else "<p>{{ contact_name }}，您好！</p>")
                .replace("{{ contact_name }}", lead.contact_name)
                .replace("{{ message }}", ""),
        }
        form = FollowUpEmailForm(request.POST or None, request.FILES or None, initial=initial)
        if request.method == "POST" and form.is_valid():
            with transaction.atomic():
                relation = {"inquiry": lead} if isinstance(lead, Xunpan) else {"contact": lead}
                task = EmailTask.objects.create(
                    template=template,
                    kind=EmailTask.Kind.FOLLOW_UP,
                    recipients=[form.cleaned_data["recipient"]],
                    subject=form.cleaned_data["subject"],
                    text_body=form.cleaned_data["text_body"],
                    html_body=form.cleaned_data["html_body"],
                    created_by=request.user,
                    **relation,
                )
                for attachment in form.cleaned_data.get("attachments", []):
                    EmailAttachment.objects.create(
                        task=task,
                        file=attachment,
                        original_name=attachment.name,
                        size=attachment.size,
                        scan_status="clean",
                    )
                AuditLog.objects.create(actor=request.user, action="follow_up_queued", target_type=self.model._meta.model_name, target_id=str(lead.pk), summary="创建客户跟进邮件任务")
            messages.success(request, "跟进邮件已加入发送队列。")
            return redirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change", args=(lead.pk,)))
        context = {**self.admin_site.each_context(request), "title": "发送跟进邮件", "form": form, "lead": lead, "opts": self.model._meta}
        return render(request, "admin/main/lead/follow_up.html", context)

    def save_model(self, request, obj, form, change):
        old = self.model.objects.filter(pk=obj.pk).first() if change else None
        super().save_model(request, obj, form, change)
        tracked = []
        if old:
            for field in ("status", "assignee_id"):
                if getattr(old, field) != getattr(obj, field):
                    tracked.append(field)
        if tracked:
            AuditLog.objects.create(actor=request.user, action="lead_updated", target_type=self.model._meta.model_name, target_id=str(obj.pk), summary=f"更新线索字段：{', '.join(tracked)}")

    def delete_model(self, request, obj):
        raise PermissionError("请使用列表中的“永久删除所选线索”操作并完成二次确认。")

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            actions["permanent_delete_selected"] = (self.permanent_delete_selected, "permanent_delete_selected", "永久删除所选线索（需二次确认）")
        return actions

    def permanent_delete_selected(self, request, queryset):
        if request.POST.get("confirmation") == "DELETE":
            count = queryset.count()
            for obj in queryset:
                AuditLog.objects.create(actor=request.user, action="lead_deleted", target_type=self.model._meta.model_name, target_id=str(obj.pk), summary="超级管理员二次确认后物理删除线索")
                obj.delete()
            self.message_user(request, f"已永久删除 {count} 条线索。", messages.WARNING)
            return None
        return render(request, "admin/main/lead/confirm_delete.html", {
            **self.admin_site.each_context(request),
            "title": "永久删除线索",
            "queryset": queryset,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
        })


@admin.register(Xunpan)
class XunpanAdmin(LeadAdminMixin, DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "created_at"
    list_display = (
        "contact_name",
        "phone",
        "email",
        "company_brand",
        "project_type",
        "product_model_snapshot",
        "product_name_snapshot",
        "estimated_quantity",
        "country_region",
        "status",
        "assignee",
        "attachment_link",
        "created_at",
    )
    search_fields = ("contact_name", "company_brand", "email", "phone", "project_type", "product_name_snapshot", "product_model_snapshot")
    list_filter = ("status", "assignee", "project_type", "country_region", "created_at")
    readonly_fields = ("privacy_policy", "privacy_consented_at", "ip_fingerprint", "form_token_id", "attachment_scan_status", "anonymized_at", "created_at")
    list_per_page = 20
    actions = ("export_csv", "export_xlsx")

    def _export_headers(self):
        return [
            "联系人姓名", "联系电话", "邮箱", "公司/品牌", "感兴趣的产品",
            "产品名称", "产品型号", "预计数量", "国家/地区", "详细需求",
            "处理状态", "负责人", "内部备注", "最后跟进时间", "提交时间",
        ]

    def _export_rows(self, queryset):
        return queryset.values_list(
            "contact_name", "phone", "email", "company_brand", "project_type",
            "product_name_snapshot", "product_model_snapshot", "estimated_quantity",
            "country_region", "detailed_requirements", "status", "assignee__username",
            "internal_note", "last_followed_at", "created_at",
        )

    @admin.display(description="附件")
    def attachment_link(self, obj):
        if not obj.attachment:
            return "无"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">查看附件</a>',
            reverse("admin-private-inquiry-attachment", args=(obj.pk,)),
        )

    @admin.action(description="导出所选询盘 CSV")
    def export_csv(self, request, queryset):
        AuditLog.objects.create(actor=getattr(request, "user", None), action="lead_exported", target_type="inquiry", summary=f"导出 {queryset.count()} 条询盘 CSV")
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="inquiries.csv"'
        return export_csv(response, self._export_headers(), self._export_rows(queryset))

    @admin.action(description="导出所选询盘 Excel")
    def export_xlsx(self, request, queryset):
        AuditLog.objects.create(actor=getattr(request, "user", None), action="lead_exported", target_type="inquiry", summary=f"导出 {queryset.count()} 条询盘 Excel")
        return export_xlsx("inquiries.xlsx", self._export_headers(), self._export_rows(queryset))


@admin.register(Lianxi)
class LianxiAdmin(LeadAdminMixin, DefaultDateRangeAdminMixin, admin.ModelAdmin):
    date_range_field = "created_at"
    list_display = (
        "contact_name",
        "phone",
        "email",
        "subject",
        "message_preview",
        "status",
        "assignee",
        "created_at",
    )
    search_fields = ("contact_name", "email", "phone", "message")
    list_filter = ("status", "assignee", "subject", "created_at")
    readonly_fields = ("privacy_policy", "privacy_consented_at", "ip_fingerprint", "form_token_id", "security_scan_status", "anonymized_at", "created_at")
    list_per_page = 20
    actions = ("export_csv", "export_xlsx")

    def _export_headers(self):
        return [
            "联系人姓名", "联系电话", "邮箱", "主题", "留言内容", "处理状态",
            "负责人", "内部备注", "最后跟进时间", "提交时间",
        ]

    def _export_rows(self, queryset):
        return queryset.values_list(
            "contact_name", "phone", "email", "subject", "message", "status",
            "assignee__username", "internal_note", "last_followed_at", "created_at",
        )

    @admin.display(description="留言内容")
    def message_preview(self, obj):
        if len(obj.message) <= 40:
            return obj.message
        return f"{obj.message[:40]}..."

    @admin.action(description="导出所选留言 CSV")
    def export_csv(self, request, queryset):
        AuditLog.objects.create(actor=getattr(request, "user", None), action="lead_exported", target_type="contact", summary=f"导出 {queryset.count()} 条留言 CSV")
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="contacts.csv"'
        return export_csv(response, self._export_headers(), self._export_rows(queryset))

    @admin.action(description="导出所选留言 Excel")
    def export_xlsx(self, request, queryset):
        AuditLog.objects.create(actor=getattr(request, "user", None), action="lead_exported", target_type="contact", summary=f"导出 {queryset.count()} 条留言 Excel")
        return export_xlsx("contacts.xlsx", self._export_headers(), self._export_rows(queryset))

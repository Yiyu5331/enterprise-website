from django import forms

from operations.attachments import validate_and_scan_attachment

from .models import Lianxi, Xunpan


class StripTextMixin:
    """清理用户输入两侧的空白字符。"""

    def clean(self):
        cleaned_data = super().clean()
        for field_name, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data
        return cleaned_data


class XunpanForm(StripTextMixin, forms.ModelForm):
    class Meta:
        model = Xunpan
        fields = (
            "contact_name",
            "phone",
            "email",
            "company_brand",
            "project_type",
            "product_name_snapshot",
            "product_model_snapshot",
            "estimated_quantity",
            "country_region",
            "detailed_requirements",
            "attachment",
        )

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if not attachment:
            return attachment

        validate_and_scan_attachment(attachment)
        return attachment


class LianxiForm(StripTextMixin, forms.ModelForm):
    class Meta:
        model = Lianxi
        fields = ("contact_name", "phone", "email", "subject", "message")

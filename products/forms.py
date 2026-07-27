from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from main.admin_widgets import QuillWidget
from main.content_utils import ContentStatus, rich_text_images_have_alt, rich_text_to_plain

from .models import Product


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {"description": QuillWidget(upload_kind="products")}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") == ContentStatus.PUBLISHED:
            errors = {}
            if not cleaned.get("image"):
                errors["image"] = "发布产品前必须上传主图。"
            if not cleaned.get("summary"):
                errors["summary"] = "发布产品前必须填写摘要。"
            if not rich_text_to_plain(cleaned.get("description")):
                errors["description"] = "发布产品前必须填写详细说明。"
            elif not rich_text_images_have_alt(cleaned.get("description")):
                errors["description"] = "详细说明中的每张图片都必须包含 alt 属性。"
            if errors:
                raise ValidationError(errors)
        return cleaned


class RequiredWhenPublishedFormSet(BaseInlineFormSet):
    item_label = "内容"

    def clean(self):
        super().clean()
        if any(self.errors) or self.instance.status != ContentStatus.PUBLISHED:
            return
        active_forms = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        if not active_forms:
            raise ValidationError(f"发布产品前至少需要 1 条{self.item_label}。")


class SpecificationInlineFormSet(RequiredWhenPublishedFormSet):
    item_label = "产品参数"

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        card_count = sum(
            1 for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get("DELETE", False)
            and form.cleaned_data.get("show_on_card")
        )
        if card_count > 4:
            raise ValidationError("每款产品最多选择 4 项卡片展示参数。")


class HighlightInlineFormSet(RequiredWhenPublishedFormSet):
    item_label = "产品特点"


class ApplicationInlineFormSet(RequiredWhenPublishedFormSet):
    item_label = "应用场景"

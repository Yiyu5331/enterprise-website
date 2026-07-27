from django import forms

from .attachments import MAX_EMAIL_ATTACHMENT_SIZE, validate_and_scan_attachment


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data] if data else []
        return [super().clean(item, initial) for item in files]


class FollowUpEmailForm(forms.Form):
    recipient = forms.EmailField(label="收件人")
    subject = forms.CharField(label="邮件主题", max_length=200)
    text_body = forms.CharField(label="纯文本正文", widget=forms.Textarea(attrs={"rows": 10}))
    html_body = forms.CharField(label="HTML 正文", widget=forms.Textarea(attrs={"rows": 10}), required=False)
    attachments = MultipleFileField(label="附件（可多选，总计不超过 20 MB）", required=False)

    def clean_attachments(self):
        attachments = self.cleaned_data.get("attachments") or []
        total_size = sum(item.size for item in attachments)
        if total_size > MAX_EMAIL_ATTACHMENT_SIZE:
            raise forms.ValidationError("单封邮件的附件总计不能超过 20 MB。")
        for attachment in attachments:
            validate_and_scan_attachment(attachment, max_size=MAX_EMAIL_ATTACHMENT_SIZE)
        return attachments

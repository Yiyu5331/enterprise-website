from django import forms


class QuillWidget(forms.Textarea):
    template_name = "django/forms/widgets/textarea.html"

    def __init__(self, attrs=None, upload_kind="news"):
        attrs = {
            "class": "vLargeTextField richtext-source",
            "data-upload-kind": upload_kind,
            **(attrs or {}),
        }
        super().__init__(attrs)

    class Media:
        css = {
            "all": (
                "admin/content_editor/quill.snow.css",
                "admin/content_editor/table-up.css",
                "admin/content_editor/editor.css",
            )
        }
        js = (
            "admin/content_editor/quill.js",
            "admin/content_editor/table-up.js",
            "admin/content_editor/editor.js",
        )

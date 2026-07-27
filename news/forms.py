from django import forms

from main.admin_widgets import QuillWidget

from .models import Article


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {"body": QuillWidget(upload_kind="news")}

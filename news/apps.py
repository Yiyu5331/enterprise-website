from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'news'
    verbose_name = "新闻管理"

    def ready(self):
        from . import signals  # noqa: F401

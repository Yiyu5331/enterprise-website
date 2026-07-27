from django.apps import AppConfig


class OperationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'operations'
    verbose_name = "安全与运维"

    def ready(self):
        from . import signals  # noqa: F401
        # 第三方安全模型默认英文名称，这里只调整后台显示名称，不改变表名和数据结构。
        from axes.models import AccessAttempt, AccessFailureLog, AccessLog
        from django_otp.plugins.otp_totp.models import TOTPDevice

        AccessAttempt._meta.verbose_name = "登录尝试记录"
        AccessAttempt._meta.verbose_name_plural = "登录尝试记录"
        AccessFailureLog._meta.verbose_name = "登录失败记录"
        AccessFailureLog._meta.verbose_name_plural = "登录失败记录"
        AccessLog._meta.verbose_name = "登录日志"
        AccessLog._meta.verbose_name_plural = "登录日志"
        TOTPDevice._meta.verbose_name = "双重验证设备"
        TOTPDevice._meta.verbose_name_plural = "双重验证设备"

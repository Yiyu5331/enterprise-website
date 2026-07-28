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

        field_labels = {
            "user_agent": "浏览器标识（User agent）",
            "ip_address": "IP 地址（IP address）",
            "username": "用户名（Username）",
            "http_accept": "请求类型（HTTP accept）",
            "path_info": "访问路径（Path）",
            "attempt_time": "尝试时间（Attempt time）",
            "get_data": "GET 数据（GET data）",
            "post_data": "POST 数据（POST data）",
            "failures_since_start": "连续失败次数（Failed logins）",
            "locked_out": "是否锁定（Locked out）",
            "logout_time": "退出时间（Logout time）",
            "session_hash": "会话摘要（Session hash）",
            "user": "用户（User）",
            "name": "设备名称（Name）",
            "confirmed": "已确认（Confirmed）",
            "created_at": "创建时间（Created at）",
            "last_used_at": "最近使用时间（Last used at）",
            "key": "验证密钥（Secret key）",
            "step": "验证码周期（Step）",
            "digits": "验证码位数（Digits）",
            "tolerance": "容错范围（Tolerance）",
            "t0": "起始时间（T0）",
            "last_t": "最近计数（Last counter）",
            "drift": "时间漂移（Drift）",
            "throttling_failure_timestamp": "失败限制时间（Throttling time）",
            "throttling_failure_count": "失败限制次数（Throttling failures）",
        }

        AccessAttempt._meta.verbose_name = "登录尝试记录"
        AccessAttempt._meta.verbose_name_plural = "登录尝试记录"
        AccessFailureLog._meta.verbose_name = "登录失败记录"
        AccessFailureLog._meta.verbose_name_plural = "登录失败记录"
        AccessLog._meta.verbose_name = "登录日志"
        AccessLog._meta.verbose_name_plural = "登录日志"
        TOTPDevice._meta.verbose_name = "双重验证设备"
        TOTPDevice._meta.verbose_name_plural = "双重验证设备"
        for model in (AccessAttempt, AccessFailureLog, AccessLog, TOTPDevice):
            for field in model._meta.fields:
                if field.name in field_labels:
                    field.verbose_name = field_labels[field.name]

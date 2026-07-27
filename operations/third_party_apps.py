from axes.apps import AppConfig as AxesAppConfig
from django_otp.plugins.otp_totp.apps import DefaultConfig as TotpAppConfig


class ChineseAxesConfig(AxesAppConfig):
    verbose_name = "登录保护（Axes）"


class ChineseTotpConfig(TotpAppConfig):
    verbose_name = "双重验证（OTP-TOTP）"

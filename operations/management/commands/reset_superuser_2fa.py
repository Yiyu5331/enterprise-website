from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from operations.models import AuditLog, RecoveryCode


class Command(BaseCommand):
    help = "重置指定超级管理员的 TOTP 设备和恢复码。"

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        user = get_user_model().objects.filter(username=options["username"], is_superuser=True).first()
        if not user:
            raise CommandError("未找到该超级管理员。")
        user.totpdevice_set.all().delete()
        RecoveryCode.objects.filter(user=user).delete()
        AuditLog.objects.create(actor=user, action="totp_reset", target_type="user", target_id=str(user.pk), summary="通过服务器命令重置双重验证")
        self.stdout.write(self.style.SUCCESS("双重验证已重置，下次进入后台时需要重新绑定。"))

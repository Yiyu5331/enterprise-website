import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from operations.backup import verify_and_extract_backup
from operations.models import AuditLog, BackupRecord
from operations.backup import _sha256


class Command(BaseCommand):
    help = "验证加密备份并恢复数据库及媒体文件。"

    def add_arguments(self, parser):
        parser.add_argument("archive")
        parser.add_argument("--confirm", default="")

    def handle(self, *args, **options):
        if options["confirm"] != "RESTORE-HUALI":
            raise CommandError("请确认已停止 Gunicorn，并添加 --confirm RESTORE-HUALI。")
        archive = Path(options["archive"]).resolve()
        if not archive.exists():
            raise CommandError("备份文件不存在。")
        record = BackupRecord.objects.filter(filename=archive.name, status="success").first()
        if record and _sha256(archive) != record.sha256:
            raise CommandError("加密备份包 SHA-256 与备份记录不一致。")
        required = archive.stat().st_size * 2
        if shutil.disk_usage(settings.BASE_DIR).free < required:
            raise CommandError("磁盘空间不足，无法安全恢复。")
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest, db_path = verify_and_extract_backup(archive, temp_dir)
            if manifest["migration_signature"] != __import__("operations.backup", fromlist=["migration_signature"]).migration_signature():
                raise CommandError("备份迁移版本与当前代码不一致，请使用匹配版本恢复。")
            connection.close()
            shutil.copy2(db_path, settings.DATABASES["default"]["NAME"])
            for folder, destination in (("media", settings.MEDIA_ROOT), ("private_media", settings.PRIVATE_MEDIA_ROOT)):
                source = Path(temp_dir) / folder
                if source.exists():
                    shutil.rmtree(destination, ignore_errors=True)
                    shutil.copytree(source, destination)
        AuditLog.objects.create(action="backup_restored", target_type="backup", target_id=archive.name, summary="通过服务器命令恢复加密备份")
        self.stdout.write(self.style.SUCCESS("恢复完成。启动服务前请运行 manage.py check 和数据库检查。"))

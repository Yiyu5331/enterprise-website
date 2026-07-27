import hashlib
import json
import shutil
import sqlite3
import tempfile
from datetime import timedelta
from pathlib import Path

import pyzipper
from django.conf import settings
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.utils import timezone

from .models import BackupRecord, SystemAlert


def migration_signature():
    rows = MigrationRecorder.Migration.objects.order_by("app", "name").values_list("app", "name")
    payload = "\n".join(f"{app}:{name}" for app, name in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sqlite_online_backup(destination):
    connection.ensure_connection()
    source = connection.connection
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
    finally:
        target.close()


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_backup():
    if len(settings.BACKUP_ENCRYPTION_KEY) < 32:
        raise ValueError("BACKUP_ENCRYPTION_KEY 至少需要 32 个字符。")
    settings.BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
    filename = settings.BACKUP_ROOT / f"huali-backup-{timestamp}.zip.aes"
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        db_snapshot = temp / "db.sqlite3"
        sqlite_online_backup(db_snapshot)
        manifest = {
            "created_at": timezone.now().isoformat(),
            "migration_signature": migration_signature(),
            "database_sha256": _sha256(db_snapshot),
            "includes": ["db.sqlite3", "media", "private_media"],
        }
        (temp / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        with pyzipper.AESZipFile(filename, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as archive:
            archive.setpassword(settings.BACKUP_ENCRYPTION_KEY.encode("utf-8"))
            archive.setencryption(pyzipper.WZ_AES, nbits=256)
            archive.write(db_snapshot, "db.sqlite3")
            archive.write(temp / "manifest.json", "manifest.json")
            for root, prefix in ((settings.MEDIA_ROOT, "media"), (settings.PRIVATE_MEDIA_ROOT, "private_media")):
                root = Path(root)
                if root.exists():
                    for item in root.rglob("*"):
                        if item.is_file():
                            archive.write(item, str(Path(prefix) / item.relative_to(root)))
    checksum = _sha256(filename)
    record = BackupRecord.objects.create(
        filename=filename.name,
        sha256=checksum,
        size=filename.stat().st_size,
        status="success",
        migration_signature=manifest["migration_signature"],
    )
    upload_to_s3(filename, record)
    return record


def upload_to_s3(path, record):
    if not settings.S3_BACKUP_BUCKET:
        return
    try:
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )
        client.upload_file(str(path), settings.S3_BACKUP_BUCKET, path.name)
    except Exception as exc:
        SystemAlert.objects.create(source="backup", message=f"本地备份成功，但异地上传失败：{str(exc)[:400]}")
    else:
        record.remote_uploaded = True
        record.save(update_fields=("remote_uploaded",))


def cleanup_old_backups(days=30):
    cutoff = timezone.now() - timedelta(days=days)
    for record in BackupRecord.objects.filter(created_at__lt=cutoff):
        (settings.BACKUP_ROOT / record.filename).unlink(missing_ok=True)
        record.delete()


def verify_and_extract_backup(archive_path, target_dir):
    archive_path = Path(archive_path)
    if len(settings.BACKUP_ENCRYPTION_KEY) < 32:
        raise ValueError("备份密钥无效。")
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with pyzipper.AESZipFile(archive_path) as archive:
        archive.setpassword(settings.BACKUP_ENCRYPTION_KEY.encode("utf-8"))
        archive.extractall(target_dir)
    manifest = json.loads((target_dir / "manifest.json").read_text(encoding="utf-8"))
    db_path = target_dir / "db.sqlite3"
    if _sha256(db_path) != manifest["database_sha256"]:
        raise ValueError("数据库快照哈希校验失败。")
    restored = sqlite3.connect(db_path)
    try:
        result = restored.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        restored.close()
    if result != "ok":
        raise ValueError(f"SQLite 完整性检查失败：{result}")
    return manifest, db_path

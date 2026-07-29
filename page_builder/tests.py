from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.test import TestCase
from PIL import Image
from io import BytesIO

from .models import AssetLicense, PublicMediaAsset


class MediaLibraryTests(TestCase):
    def test_asset_records_size_and_sha256(self):
        license = AssetLicense.objects.create(
            name="项目自有素材", license_type=AssetLicense.LicenseType.OWNED,
            allows_commercial_use=True,
        )
        asset = PublicMediaAsset.objects.create(
            title="测试文件", file=ContentFile(b"huali", name="test.bin"), license=license,
        )
        self.assertEqual(asset.size, 5)
        self.assertEqual(len(asset.sha256), 64)

    def test_unknown_or_noncommercial_license_cannot_be_approved(self):
        license = AssetLicense.objects.create(name="未知素材")
        asset = PublicMediaAsset(
            title="待审核图片",
            file=ContentFile(b"not-used", name="test.bin"),
            license=license,
            is_approved=True,
            is_decorative=True,
        )

        with self.assertRaisesMessage(ValidationError, "许可证未知"):
            asset.full_clean()

    def test_image_asset_records_dimensions(self):
        license = AssetLicense.objects.create(
            name="自有图片",
            license_type=AssetLicense.LicenseType.OWNED,
            allows_commercial_use=True,
        )
        source = BytesIO()
        Image.new("RGB", (320, 180), "red").save(source, format="PNG")
        asset = PublicMediaAsset.objects.create(
            title="尺寸测试",
            file=ContentFile(source.getvalue(), name="dimensions.png"),
            license=license,
        )

        self.assertEqual((asset.width, asset.height), (320, 180))

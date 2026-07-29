import tempfile
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image
from pypdf import PdfReader

from main.content_utils import ContentStatus, VerificationStatus, process_uploaded_image
from main.models import Lianxi, Xunpan

from .models import (
    ParameterMappingSuggestion, Product, ProductCategory, ProductDocument,
    ProductSpecification,
)


class ContentSeedAndProductApiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media = tempfile.TemporaryDirectory()
        cls.media_override = override_settings(MEDIA_ROOT=cls.temp_media.name)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        cls.temp_media.cleanup()
        super().tearDownClass()

    def test_seed_content_imports_products_and_keeps_form_records(self):
        Xunpan.objects.create(
            contact_name="原有询盘",
            email="old@example.com",
            detailed_requirements="不要被初始化命令覆盖。",
        )

        call_command("seed_content", verbosity=0)
        call_command("seed_content", verbosity=0)
        call_command("seed_content", check=True, verbosity=0)

        self.assertEqual(Product.objects.count(), 18)
        self.assertEqual(Xunpan.objects.count(), 1)
        self.assertEqual(Lianxi.objects.count(), 0)

    def test_product_category_list_hides_empty_categories(self):
        call_command("seed_content", verbosity=0)
        response = self.client.get("/api/v1/product-categories/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 6)
        self.assertTrue(all(item["item_count"] > 0 for item in response.json()))

    def test_product_list_search_and_detail(self):
        call_command("seed_content", verbosity=0)

        list_response = self.client.get("/api/v1/products/?q=HL ID201")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["count"], 1)

        detail_response = self.client.get("/api/v1/products/hl-id201/")
        self.assertEqual(detail_response.status_code, 200)
        detail = detail_response.json()
        self.assertEqual(detail["model"], "HL-ID201")
        self.assertTrue(detail["specifications"])
        self.assertTrue(detail["related_products"])

    def test_invalid_category_returns_400_and_out_of_range_page_returns_404(self):
        call_command("seed_content", verbosity=0)

        bad_category = self.client.get("/api/v1/products/?category=missing")
        self.assertEqual(bad_category.status_code, 400)
        self.assertEqual(bad_category.json()["code"], "validation_error")

        bad_page = self.client.get("/api/v1/products/?page=9")
        self.assertEqual(bad_page.status_code, 404)

    def test_hidden_category_hides_public_products(self):
        call_command("seed_content", verbosity=0)
        ProductCategory.objects.filter(slug="drills").update(is_active=False)

        response = self.client.get("/api/v1/products/?category=drills")
        self.assertEqual(response.status_code, 400)
        options = self.client.get("/api/v1/product-options/").json()
        self.assertNotIn("HL-D101", [item["model"] for item in options])

    def test_media_processing_creates_webp_without_exif(self):
        image = Image.new("RGB", (1800, 1200), "red")
        source = BytesIO()
        image.save(source, format="JPEG", exif=b"Exif\x00\x00fake")
        source.seek(0)
        upload = ContentFile(source.read(), name="source.jpg")

        original, web, thumb = process_uploaded_image(upload, prefix="test", thumb_size=(800, 533))

        self.assertTrue(original.name.endswith(".webp"))
        self.assertTrue(web.name.endswith(".webp"))
        self.assertTrue(thumb.name.endswith(".webp"))

    def test_draft_product_is_hidden(self):
        call_command("seed_content", verbosity=0)
        Product.objects.filter(model="HL-ID201").update(status=ContentStatus.DRAFT)

        response = self.client.get("/api/v1/products/HL-ID201/")
        self.assertEqual(response.status_code, 404)

    @override_settings(SITE_CONTENT_MODE="production")
    def test_production_mode_rejects_demo_product_publish(self):
        category = ProductCategory.objects.create(name="测试分类", slug="test-category", is_active=False)
        product = Product(
            category=category,
            name="演示产品",
            model="DEMO-TEST",
            level="演示级",
            summary="测试摘要",
            description="<p>测试说明</p>",
            status=ContentStatus.PUBLISHED,
            is_demo=True,
            verification_status=VerificationStatus.PENDING,
        )

        with self.assertRaisesMessage(ValidationError, "生产模式不能发布演示内容"):
            product.full_clean()

    def test_verification_status_records_timestamp_with_update_fields(self):
        category = ProductCategory.objects.create(name="核验分类", slug="verification-category", is_active=False)
        product = Product.objects.create(
            category=category,
            name="待核验产品",
            model="VERIFY-100",
            level="测试级",
            summary="测试摘要",
            description="<p>测试说明</p>",
        )
        product.verification_status = VerificationStatus.VERIFIED
        product.save(update_fields=("verification_status",))
        product.refresh_from_db()

        self.assertIsNotNone(product.verified_at)

    @override_settings(SITE_CONTENT_MODE="production")
    def test_production_api_hides_demo_product_and_empty_category(self):
        category = ProductCategory.objects.create(name="演示分类", slug="demo-category", is_active=False)
        Product.objects.create(
            category=category,
            name="演示产品",
            model="DEMO-HIDDEN",
            level="演示级",
            summary="测试摘要",
            description="<p>测试说明</p>",
            status=ContentStatus.PUBLISHED,
            is_demo=True,
        )
        ProductCategory.objects.filter(pk=category.pk).update(is_active=True)

        self.assertEqual(self.client.get("/api/v1/products/").json()["count"], 0)
        self.assertEqual(self.client.get("/api/v1/product-categories/").json(), [])


class PhaseThreeFoundationSeedTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media = tempfile.TemporaryDirectory()
        cls.media_override = override_settings(MEDIA_ROOT=cls.temp_media.name)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        cls.temp_media.cleanup()
        super().tearDownClass()

    def test_phase_three_seed_is_idempotent_and_keeps_leads(self):
        Xunpan.objects.create(
            contact_name="原有询盘",
            email="phase3@example.com",
            detailed_requirements="第三阶段初始化不得删除。",
        )
        call_command("seed_content", verbosity=0)
        call_command("seed_phase3_foundation", verbosity=0)
        call_command("seed_phase3_foundation", verbosity=0)
        call_command("seed_phase3_foundation", check=True, verbosity=0)

        self.assertEqual(Product.objects.count(), 30)
        self.assertEqual(Product.objects.filter(is_demo=True).count(), 12)
        self.assertEqual(ProductDocument.objects.filter(is_demo=True).count(), 4)
        self.assertEqual(Xunpan.objects.count(), 1)
        self.assertEqual(Lianxi.objects.count(), 0)

        for document in ProductDocument.objects.filter(is_demo=True):
            with document.file.open("rb") as stream:
                reader = PdfReader(stream)
                self.assertEqual(len(reader.pages), 4)
                text = "".join(page.extract_text() or "" for page in reader.pages)
                self.assertIn("测试资料", text)
                self.assertIn("DEMO", text)

    def test_parameter_mapping_suggestions_need_manual_confirmation(self):
        call_command("seed_content", verbosity=0)
        call_command("seed_phase3_foundation", verbosity=0)

        suggestions = ParameterMappingSuggestion.objects.filter(status=ParameterMappingSuggestion.Status.PENDING)
        self.assertTrue(suggestions.exists())
        suggestion = suggestions.first()
        self.assertTrue(ProductSpecification.objects.filter(
            name=suggestion.source_name,
            standard_parameter__isnull=True,
        ).exists())

    def test_check_mode_does_not_write_data(self):
        call_command("seed_phase3_foundation", check=True, verbosity=0)

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductDocument.objects.count(), 0)
        self.assertEqual(ParameterMappingSuggestion.objects.count(), 0)

    def test_overwrite_restores_demo_content_without_resetting_verified_real_product(self):
        call_command("seed_content", verbosity=0)
        real_product = Product.objects.get(model="HL-ID201")
        real_product.verification_status = VerificationStatus.VERIFIED
        real_product.save(update_fields=("verification_status",))
        call_command("seed_phase3_foundation", verbosity=0)

        demo_product = Product.objects.get(model="DEMO-DR101")
        demo_product.name = "被修改的演示名称"
        demo_product.save(update_fields=("name",))
        call_command("seed_phase3_foundation", overwrite=True, verbosity=0)

        real_product.refresh_from_db()
        demo_product.refresh_from_db()
        self.assertEqual(real_product.verification_status, VerificationStatus.VERIFIED)
        self.assertEqual(demo_product.name, "概念无刷电钻")

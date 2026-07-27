import tempfile
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from main.content_utils import ContentStatus, process_uploaded_image
from main.models import Lianxi, Xunpan

from .models import Product, ProductCategory


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

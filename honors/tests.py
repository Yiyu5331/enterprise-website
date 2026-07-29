from django.test import TestCase, override_settings

from main.content_utils import ContentStatus, VerificationStatus

from .models import Honor, HonorCategory


class HonorApiTests(TestCase):
    def setUp(self):
        category = HonorCategory.objects.create(name="技术创新", slug="innovation")
        Honor.objects.create(
            category=category, slug="demo-honor", title="演示荣誉",
            status=ContentStatus.PUBLISHED, is_demo=True,
        )
        Honor.objects.create(
            category=category, slug="verified-honor", title="已核验荣誉",
            status=ContentStatus.PUBLISHED, verification_status=VerificationStatus.VERIFIED,
        )

    @override_settings(SITE_CONTENT_MODE="test")
    def test_test_mode_returns_all_published_honors(self):
        self.assertEqual(len(self.client.get("/api/v1/honors/").json()), 2)

    @override_settings(SITE_CONTENT_MODE="production")
    def test_production_mode_only_returns_verified_honors(self):
        response = self.client.get("/api/v1/honors/")
        self.assertEqual([item["slug"] for item in response.json()], ["verified-honor"])

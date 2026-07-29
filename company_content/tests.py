from django.test import TestCase, override_settings

from main.content_utils import ContentStatus, VerificationStatus

from .models import CompanyFact, FAQ, FAQCategory


class CompanyContentApiTests(TestCase):
    def setUp(self):
        category = FAQCategory.objects.create(name="产品选型", slug="product-selection")
        FAQ.objects.create(
            category=category, question="测试问题", answer="测试回答", status=ContentStatus.PUBLISHED,
            is_demo=True,
        )
        CompanyFact.objects.create(
            label="演示产能", value="100", unit="万台", status=ContentStatus.PUBLISHED, is_demo=True,
        )
        CompanyFact.objects.create(
            label="成立时间", value="2003", status=ContentStatus.PUBLISHED,
            verification_status=VerificationStatus.VERIFIED,
        )

    @override_settings(SITE_CONTENT_MODE="test")
    def test_test_mode_returns_demo_content(self):
        response = self.client.get("/api/v1/site-content/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["facts"]), 2)
        self.assertEqual(len(self.client.get("/api/v1/faqs/").json()), 1)

    @override_settings(SITE_CONTENT_MODE="production")
    def test_production_mode_hides_demo_and_unverified_content(self):
        response = self.client.get("/api/v1/site-content/")
        self.assertEqual([item["label"] for item in response.json()["facts"]], ["成立时间"])
        self.assertEqual(self.client.get("/api/v1/faqs/").json(), [])

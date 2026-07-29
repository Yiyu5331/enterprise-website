import tempfile

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings

from main.content_utils import ContentStatus, VerificationStatus, sanitize_rich_text

from .models import Article, NewsCategory


class NewsApiTests(TestCase):
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

    def test_news_list_detail_and_homepage(self):
        call_command("seed_content", verbosity=0)

        list_response = self.client.get("/api/v1/news/?q=5G")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["count"], 1)

        detail_response = self.client.get("/api/v1/news/5g-factory-2025/")
        self.assertEqual(detail_response.status_code, 200)
        detail = detail_response.json()
        self.assertEqual(detail["slug"], "5g-factory-2025")
        self.assertTrue(detail["related_news"])

        homepage = self.client.get("/api/v1/homepage/").json()
        self.assertEqual(len(homepage["products"]), 6)
        self.assertEqual(len(homepage["news"]), 3)

    def test_news_category_count_and_hidden_category(self):
        call_command("seed_content", verbosity=0)
        response = self.client.get("/api/v1/news-categories/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

        NewsCategory.objects.filter(slug="company-news").update(is_active=False)
        bad_category = self.client.get("/api/v1/news/?category=company-news")
        self.assertEqual(bad_category.status_code, 400)

    def test_archived_news_is_hidden(self):
        call_command("seed_content", verbosity=0)
        Article.objects.filter(slug="5g-factory-2025").update(status=ContentStatus.ARCHIVED)

        response = self.client.get("/api/v1/news/5g-factory-2025/")
        self.assertEqual(response.status_code, 404)

    def test_rich_text_sanitizer_removes_unsafe_markup(self):
        cleaned = sanitize_rich_text('<p>正常</p><script>alert(1)</script><a href="http://bad.test">坏链接</a>')

        self.assertNotIn("<script", cleaned)
        self.assertNotIn("http://bad.test", cleaned)

    @override_settings(SITE_CONTENT_MODE="production")
    def test_production_mode_rejects_demo_article_publish(self):
        category = NewsCategory.objects.create(name="测试新闻", slug="test-news")
        article = Article(
            category=category,
            title="演示新闻",
            slug="demo-test-news",
            body="<p>测试正文</p>",
            status=ContentStatus.PUBLISHED,
            is_demo=True,
            verification_status=VerificationStatus.PENDING,
        )

        with self.assertRaisesMessage(ValidationError, "生产模式不能发布演示内容"):
            article.full_clean()

    @override_settings(SITE_CONTENT_MODE="production")
    def test_production_api_hides_demo_article_and_empty_category(self):
        category = NewsCategory.objects.create(name="演示新闻", slug="demo-news")
        Article.objects.create(
            category=category,
            title="演示新闻",
            slug="demo-hidden-news",
            body="<p>测试正文</p>",
            status=ContentStatus.PUBLISHED,
            is_demo=True,
        )

        self.assertEqual(self.client.get("/api/v1/news/").json()["count"], 0)
        self.assertEqual(self.client.get("/api/v1/news-categories/").json(), [])

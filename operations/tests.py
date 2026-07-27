import json
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from main.models import LeadStatus, Lianxi, Xunpan
from main.content_utils import ContentStatus
from products.models import Product, ProductApplication, ProductCategory, ProductHighlight, ProductSpecification
from news.models import Article, NewsCategory

from .attachments import AttachmentScanUnavailable, validate_and_scan_attachment
from .backup import create_backup, verify_and_extract_backup
from .mail_queue import process_one
from .maintenance import anonymize_old_leads
from .models import AuditLog, EmailTask, FormToken, PrivacyPolicy


class SecureFormTests(TestCase):
    def setUp(self):
        self.policy = PrivacyPolicy.objects.create(
            version="2026-01",
            title_zh="隐私政策",
            body_zh="正文",
            title_en="Privacy Policy",
            body_en="Body",
            status=PrivacyPolicy.Status.PUBLISHED,
        )

    def bootstrap(self, kind):
        response = self.client.get(f"/api/v1/forms/bootstrap/?kind={kind}", HTTP_USER_AGENT="test-browser")
        token = FormToken.objects.latest("created_at")
        FormToken.objects.filter(pk=token.pk).update(created_at=timezone.now() - timedelta(seconds=4))
        return response.json()

    def contact_payload(self, bootstrap):
        return {
            "contact_name": "安全测试",
            "email": "security@example.com",
            "message": "需要了解产品目录。",
            "form_token": bootstrap["form_token"],
            "privacy_consent": "true",
            "privacy_version": bootstrap["privacy_version"],
            "website": "",
        }

    def csrf_header(self):
        return {"HTTP_X_CSRFTOKEN": self.client.cookies["huali_csrftoken"].value}

    def test_bootstrap_sets_csrf_and_returns_policy(self):
        response = self.client.get("/api/v1/forms/bootstrap/?kind=contact")
        self.assertEqual(response.status_code, 200)
        self.assertIn("huali_csrftoken", response.cookies)
        self.assertEqual(response.json()["privacy_version"], self.policy.version)

    def test_honeypot_returns_success_without_saving(self):
        data = self.contact_payload(self.bootstrap("contact"))
        data["website"] = "https://spam.example"
        response = self.client.post("/api/v1/contacts/", data, HTTP_USER_AGENT="test-browser", **self.csrf_header())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lianxi.objects.count(), 0)
        self.assertEqual(EmailTask.objects.count(), 0)

    def test_token_replay_is_rejected(self):
        data = self.contact_payload(self.bootstrap("contact"))
        first = self.client.post("/api/v1/contacts/", data, HTTP_USER_AGENT="test-browser", **self.csrf_header())
        second = self.client.post("/api/v1/contacts/", data, HTTP_USER_AGENT="test-browser", **self.csrf_header())
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.json()["code"], "form_token_reused")

    def test_fast_submission_requires_captcha(self):
        bootstrap = self.client.get("/api/v1/forms/bootstrap/?kind=contact", HTTP_USER_AGENT="test-browser").json()
        response = self.client.post("/api/v1/contacts/", self.contact_payload(bootstrap), HTTP_USER_AGENT="test-browser", **self.csrf_header())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "captcha_required")

    def test_missing_csrf_header_returns_unified_error(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get("/api/v1/forms/bootstrap/?kind=contact", HTTP_USER_AGENT="test-browser")
        token = FormToken.objects.latest("created_at")
        FormToken.objects.filter(pk=token.pk).update(created_at=timezone.now() - timedelta(seconds=4))
        payload = self.contact_payload(response.json())
        rejected = client.post("/api/v1/contacts/", payload, HTTP_USER_AGENT="test-browser")
        self.assertEqual(rejected.status_code, 403)
        self.assertEqual(rejected.json()["code"], "csrf_failed")


class AttachmentSecurityTests(TestCase):
    @override_settings(CLAMAV_ENABLED=False)
    def test_valid_pdf_is_accepted_in_development(self):
        attachment = SimpleUploadedFile("safe.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")
        self.assertEqual(validate_and_scan_attachment(attachment), "skipped_development")

    def test_fake_pdf_is_rejected(self):
        attachment = SimpleUploadedFile("fake.pdf", b"not a pdf", "application/pdf")
        with self.assertRaisesMessage(Exception, "PDF 文件结构无效"):
            validate_and_scan_attachment(attachment)

    @override_settings(CLAMAV_ENABLED=True)
    @patch("clamd.ClamdNetworkSocket")
    def test_eicar_detection_is_rejected(self, socket_class):
        socket_class.return_value.instream.return_value = {"stream": ("FOUND", "Eicar-Signature")}
        attachment = SimpleUploadedFile("eicar.pdf", b"%PDF-1.4\nEICAR", "application/pdf")
        with self.assertRaisesMessage(Exception, "Eicar-Signature"):
            validate_and_scan_attachment(attachment)

    @override_settings(CLAMAV_ENABLED=True)
    @patch("clamd.ClamdNetworkSocket", side_effect=OSError("offline"))
    def test_clamav_unavailable_rejects_attachment(self, socket_class):
        attachment = SimpleUploadedFile("safe.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")
        with self.assertRaises(AttachmentScanUnavailable):
            validate_and_scan_attachment(attachment)


class PrivateAttachmentTests(TestCase):
    def test_anonymous_user_cannot_download_private_attachment(self):
        inquiry = Xunpan.objects.create(contact_name="私有附件", email="private@example.com", detailed_requirements="测试")
        response = self.client.get(f"/admin/private/inquiries/{inquiry.pk}/attachment/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="test@example.com")
class EmailQueueTests(TestCase):
    def test_follow_up_updates_pending_lead_after_send(self):
        lead = Lianxi.objects.create(contact_name="邮件测试", email="customer@example.com", message="测试")
        task = EmailTask.objects.create(
            kind=EmailTask.Kind.FOLLOW_UP,
            contact=lead,
            recipients=[lead.email],
            subject="跟进",
            text_body="正文",
            html_body="<p>正文</p>",
        )
        self.assertTrue(process_one(task.pk))
        lead.refresh_from_db()
        task.refresh_from_db()
        self.assertEqual(task.status, EmailTask.Status.SENT)
        self.assertEqual(lead.status, LeadStatus.FOLLOWING)
        self.assertEqual(len(mail.outbox), 1)


class RetentionTests(TestCase):
    def test_completed_three_year_old_lead_is_anonymized(self):
        lead = Xunpan.objects.create(
            contact_name="待匿名化",
            email="old@example.com",
            detailed_requirements="历史需求",
            status=LeadStatus.COMPLETED,
        )
        Xunpan.objects.filter(pk=lead.pk).update(created_at=timezone.now() - timedelta(days=365 * 3 + 1))
        self.assertEqual(anonymize_old_leads(), 1)
        lead.refresh_from_db()
        self.assertEqual(lead.contact_name, "已匿名化")
        self.assertTrue(lead.anonymized_at)
        self.assertTrue(AuditLog.objects.filter(action="lead_anonymized").exists())


class BackupTests(TestCase):
    def test_encrypted_backup_can_be_verified(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(BACKUP_ROOT=Path(temp_dir), BACKUP_ENCRYPTION_KEY="x" * 32, MEDIA_ROOT=Path(temp_dir) / "media", PRIVATE_MEDIA_ROOT=Path(temp_dir) / "private"):
                record = create_backup()
                archive = Path(temp_dir) / record.filename
                self.assertTrue(archive.exists())
                with tempfile.TemporaryDirectory() as restore_dir:
                    manifest, db_path = verify_and_extract_backup(archive, restore_dir)
                    self.assertTrue(db_path.exists())
                    self.assertEqual(manifest["migration_signature"], record.migration_signature)


class SeoRedirectTests(TestCase):
    def test_old_product_and_news_urls_redirect_permanently(self):
        product_category = ProductCategory.objects.create(name="测试产品分类", slug="test-products", image="products/test.webp")
        product = Product.objects.create(
            category=product_category,
            name="测试产品",
            model="TEST-100",
            level="专业级",
            summary="测试摘要",
            description="<p>测试说明</p>",
            image="products/test.webp",
            status=ContentStatus.PUBLISHED,
        )
        ProductSpecification.objects.create(product=product, name="功率", value="100W")
        ProductHighlight.objects.create(product=product, title="特点", description="说明")
        ProductApplication.objects.create(product=product, name="测试场景")
        news_category = NewsCategory.objects.create(name="测试新闻分类", slug="test-news")
        Article.objects.create(
            category=news_category,
            title="测试新闻",
            slug="test-article",
            body="<p>新闻正文</p>",
            cover="news/test.webp",
            cover_alt="测试封面",
            published_at=timezone.now(),
            status=ContentStatus.PUBLISHED,
        )

        product_response = self.client.get("/products/TEST-100")
        news_response = self.client.get("/news/test-article")
        self.assertRedirects(product_response, "/products/test-products/TEST-100/", status_code=301, fetch_redirect_response=False)
        self.assertRedirects(news_response, "/news/test-news/test-article/", status_code=301, fetch_redirect_response=False)

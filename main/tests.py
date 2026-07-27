import json
import tempfile

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .admin import LianxiAdmin, XunpanAdmin
from .models import LeadStatus, Lianxi, Xunpan
from operations.models import FormToken, PrivacyPolicy


class FormApiTests(TestCase):
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

    def setUp(self):
        self.policy = PrivacyPolicy.objects.create(
            version="test-1",
            title_zh="测试隐私政策",
            body_zh="测试正文",
            title_en="Test privacy policy",
            body_en="Test body",
            status=PrivacyPolicy.Status.PUBLISHED,
        )

    def secure_payload(self, kind, payload):
        response = self.client.get(f"/api/v1/forms/bootstrap/?kind={kind}", HTTP_USER_AGENT="Django test browser")
        token = FormToken.objects.latest("created_at")
        FormToken.objects.filter(pk=token.pk).update(created_at=timezone.now() - timedelta(seconds=4))
        return {
            **payload,
            "form_token": response.json()["form_token"],
            "privacy_consent": "true",
            "privacy_version": self.policy.version,
            "website": "",
        }

    def csrf_header(self):
        return {"HTTP_X_CSRFTOKEN": self.client.cookies["huali_csrftoken"].value}

    def test_create_inquiry_with_attachment(self):
        attachment = SimpleUploadedFile("spec.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")
        response = self.client.post(
            reverse("main:create-inquiry"),
            self.secure_payload("inquiry", {
                "contact_name": "张三",
                "phone": "13800138000",
                "email": "zhangsan@example.com",
                "company_brand": "测试工具公司",
                "project_type": "电锤",
                "product_name_snapshot": "电锤",
                "product_model_snapshot": "HL-RH501",
                "estimated_quantity": "1000 台",
                "country_region": "中国",
                "detailed_requirements": "需要 OEM 定制和报价。",
                "attachment": attachment,
            }),
            HTTP_USER_AGENT="Django test browser",
            **self.csrf_header(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Xunpan.objects.count(), 1)
        inquiry = Xunpan.objects.get()
        self.assertEqual(inquiry.contact_name, "张三")
        self.assertTrue(inquiry.attachment.name.lower().endswith(".pdf"))
        self.assertIn("inquiry_attachments/", inquiry.attachment.name)
        self.assertEqual(inquiry.product_model_snapshot, "HL-RH501")
        self.assertEqual(inquiry.status, LeadStatus.PENDING)

    def test_inquiry_rejects_missing_required_fields(self):
        payload = self.secure_payload("inquiry", {"email": "bad"})
        response = self.client.post(reverse("main:create-inquiry"), payload, HTTP_USER_AGENT="Django test browser", **self.csrf_header())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Xunpan.objects.count(), 0)
        self.assertIn("contact_name", response.json()["errors"])

    def test_create_contact_from_json(self):
        response = self.client.post(
            reverse("main:create-contact"),
            data=json.dumps(self.secure_payload("contact", {
                    "contact_name": "李四",
                    "phone": "13900139000",
                    "email": "lisi@example.com",
                    "subject": "产品咨询",
                    "message": "请提供无刷电锤产品目录。",
                }), ensure_ascii=False),
            content_type="application/json",
            HTTP_USER_AGENT="Django test browser",
            **self.csrf_header(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lianxi.objects.count(), 1)
        self.assertEqual(Lianxi.objects.get().subject, "产品咨询")

    def test_contact_rejects_invalid_json(self):
        self.client.get("/api/v1/forms/bootstrap/?kind=contact", HTTP_USER_AGENT="Django test browser")
        response = self.client.post(
            reverse("main:create-contact"),
            data="{invalid-json",
            content_type="application/json",
            HTTP_USER_AGENT="Django test browser",
            **self.csrf_header(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Lianxi.objects.count(), 0)

    def test_v1_contact_and_inquiry_create_records(self):
        inquiry_response = self.client.post(
            "/api/v1/inquiries/",
            self.secure_payload("inquiry", {
                "contact_name": "王五",
                "phone": "13700137000",
                "email": "wangwu@example.com",
                "company_brand": "采购公司",
                "project_type": "其他",
                "estimated_quantity": "500 台",
                "country_region": "中国",
                "detailed_requirements": "需要批量采购报价。",
            }),
            HTTP_USER_AGENT="Django test browser",
            **self.csrf_header(),
        )
        contact_response = self.client.post(
            "/api/v1/contacts/",
            data=json.dumps(self.secure_payload("contact", {
                "contact_name": "赵六",
                "phone": "13600136000",
                "email": "zhaoliu@example.com",
                "subject": "供应商合作",
                "message": "希望了解合作流程。",
            }), ensure_ascii=False),
            content_type="application/json",
            HTTP_USER_AGENT="Django test browser",
            **self.csrf_header(),
        )

        self.assertEqual(inquiry_response.status_code, 201)
        self.assertEqual(contact_response.status_code, 201)
        self.assertEqual(Xunpan.objects.filter(contact_name="王五").count(), 1)
        self.assertEqual(Lianxi.objects.filter(contact_name="赵六").count(), 1)

    def test_legacy_form_paths_include_deprecation_headers(self):
        response = self.client.post(
            reverse("main:create-contact"),
            data=json.dumps(self.secure_payload("contact", {
                    "contact_name": "兼容路径",
                    "email": "legacy@example.com",
                    "message": "旧接口仍然可以提交。",
                }), ensure_ascii=False),
            content_type="application/json",
            HTTP_USER_AGENT="Django test browser",
            **self.csrf_header(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Deprecation"], "true")


class AdminFormMenuTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="form-admin",
            email="admin@example.com",
            password="test-password-123",
        )
        self.client.force_login(self.admin_user)
        self.contact = Lianxi.objects.create(
            contact_name="后台联系测试",
            phone="13800138002",
            email="contact-admin@example.com",
            subject="合作洽谈",
            message="这是一条用于验证后台真实数据列表的联系留言。",
        )
        self.inquiry = Xunpan.objects.create(
            contact_name="后台询盘测试",
            phone="13900139002",
            email="inquiry-admin@example.com",
            company_brand="测试品牌",
            project_type="电锤",
            estimated_quantity="200 台",
            country_region="中国",
            detailed_requirements="这是一条用于验证后台真实数据列表的询盘。",
        )

    def test_admin_can_edit_lead_fields(self):
        self.inquiry.status = LeadStatus.FOLLOWING
        self.inquiry.assignee = self.admin_user
        self.inquiry.internal_note = "已发送报价资料。"
        self.inquiry.last_followed_at = timezone.now()
        self.inquiry.save()
        self.assertEqual(Xunpan.objects.get(pk=self.inquiry.pk).status, LeadStatus.FOLLOWING)

    def test_export_actions_return_csv(self):
        inquiry_admin = XunpanAdmin(Xunpan, admin.site)
        contact_admin = LianxiAdmin(Lianxi, admin.site)
        inquiry_response = inquiry_admin.export_csv(self.client, Xunpan.objects.all())
        contact_response = contact_admin.export_csv(self.client, Lianxi.objects.all())
        self.assertEqual(inquiry_response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("后台询盘测试", inquiry_response.content.decode("utf-8-sig"))
        self.assertIn("后台联系测试", contact_response.content.decode("utf-8-sig"))

    def test_admin_index_contains_form_menus(self):
        response = self.client.get(reverse("admin:index"))

        form_app = next(
            app for app in response.context["app_list"] if app["app_label"] == "main"
        )
        self.assertEqual(form_app["name"], "表单管理")
        self.assertEqual(
            {model["name"] for model in form_app["models"]},
            {"联系表单", "询盘表单"},
        )

    def test_contact_admin_reads_database_records(self):
        response = self.client.get(reverse("admin:main_lianxi_changelist"))
        if response.status_code == 302:
            response = self.client.get(response["Location"])

        self.assertContains(response, self.contact.contact_name)
        self.assertContains(response, self.contact.email)
        self.assertContains(response, self.contact.message)

    def test_inquiry_admin_reads_database_records(self):
        response = self.client.get(reverse("admin:main_xunpan_changelist"))
        if response.status_code == 302:
            response = self.client.get(response["Location"])

        self.assertContains(response, self.inquiry.contact_name)
        self.assertContains(response, self.inquiry.company_brand)
        self.assertContains(response, self.inquiry.project_type)

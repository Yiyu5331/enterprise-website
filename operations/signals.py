from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.backends.signals import connection_created
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditLog, EmailTemplate, PrivacyPolicy
from .prerender import queue_prerender


DEFAULT_TEMPLATES = {
    "sales-notice": {
        "name": "销售通知",
        "subject": "新网站线索：{{ lead_type }} - {{ contact_name }}",
        "text_body": "收到新的{{ lead_type }}。\n联系人：{{ contact_name }}\n邮箱：{{ email }}\n电话：{{ phone }}\n摘要：{{ summary }}",
        "html_body": "<h2>收到新的{{ lead_type }}</h2><p>联系人：{{ contact_name }}</p><p>邮箱：{{ email }}</p><p>电话：{{ phone }}</p><p>摘要：{{ summary }}</p>",
        "allowed_variables": "lead_type,contact_name,email,phone,summary",
    },
    "inquiry-receipt": {
        "name": "询盘客户回执",
        "subject": "华丽电器已收到您的询盘 / Inquiry received",
        "text_body": "{{ contact_name }}，您好！我们已收到您的询盘，将尽快与您联系。\n\nDear {{ contact_name }}, we have received your inquiry and will contact you soon.",
        "html_body": "<p>{{ contact_name }}，您好！我们已收到您的询盘，将尽快与您联系。</p><p>Dear {{ contact_name }}, we have received your inquiry and will contact you soon.</p>",
        "allowed_variables": "contact_name",
    },
    "contact-receipt": {
        "name": "留言客户回执",
        "subject": "华丽电器已收到您的留言 / Message received",
        "text_body": "{{ contact_name }}，您好！我们已收到您的留言。\n\nDear {{ contact_name }}, we have received your message.",
        "html_body": "<p>{{ contact_name }}，您好！我们已收到您的留言。</p><p>Dear {{ contact_name }}, we have received your message.</p>",
        "allowed_variables": "contact_name",
    },
    "follow-up": {
        "name": "客户跟进",
        "subject": "关于您向华丽电器提交的需求",
        "text_body": "{{ contact_name }}，您好！\n\n感谢您的联系，以下是本次跟进内容：\n{{ message }}",
        "html_body": "<p>{{ contact_name }}，您好！</p><p>感谢您的联系，以下是本次跟进内容：</p><p>{{ message }}</p>",
        "allowed_variables": "contact_name,message",
    },
}


@receiver(post_migrate)
def create_operations_defaults(sender, **kwargs):
    if sender.label != "operations":
        return
    PrivacyPolicy.objects.get_or_create(
        version="draft-1",
        defaults={
            "title_zh": "华丽电器网站隐私政策（待审核）",
            "body_zh": "本草稿需由公司负责人审核后发布。网站将仅为处理询盘和联系请求收集必要信息。",
            "title_en": "Huali Electric Website Privacy Policy (Draft)",
            "body_en": "This draft must be reviewed before publication. Necessary information is collected only to handle inquiries and contact requests.",
        },
    )
    for key, defaults in DEFAULT_TEMPLATES.items():
        EmailTemplate.objects.get_or_create(key=key, defaults=defaults)


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    AuditLog.objects.create(actor=user, action="login_success", target_type="user", target_id=str(user.pk), summary="后台登录成功")


@receiver(user_login_failed)
def audit_login_failure(sender, credentials, request, **kwargs):
    AuditLog.objects.create(action="login_failed", target_type="user", summary=f"后台登录失败：{credentials.get('username', '未知用户')}")


@receiver(connection_created)
def configure_sqlite(sender, connection, **kwargs):
    if connection.vendor != "sqlite":
        return
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")


@receiver(post_save, sender="products.Product")
def product_prerender_changed(sender, instance, **kwargs):
    queue_prerender(f"/products/{instance.category.slug}/{instance.model}/", "产品内容变更")
    queue_prerender(f"/products/category/{instance.category.slug}/", "产品分类内容变更")
    queue_prerender("/", "产品推荐或内容变更")


@receiver(post_save, sender="news.Article")
def news_prerender_changed(sender, instance, **kwargs):
    queue_prerender(f"/news/{instance.category.slug}/{instance.slug}/", "新闻内容变更")
    queue_prerender(f"/news/category/{instance.category.slug}/", "新闻分类内容变更")
    queue_prerender("/", "新闻推荐或内容变更")

import math
import re
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q
from django.middleware.csrf import get_token
from django.urls import path
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers, status
from rest_framework.authentication import CSRFCheck
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_field

from main.content_utils import ContentStatus, VerificationStatus
from company_content.api import faqs, locations, site_content
from honors.api import honor_categories, honors
from main.models import Lianxi, Xunpan
from news.models import Article, NewsCategory
from operations.attachments import AttachmentScanUnavailable, validate_and_scan_attachment
from operations.emailing import queue_lead_messages
from operations.health import public_health_status
from operations.models import PrivacyPolicy
from operations.security import (
    FormSecurityError,
    captcha_required,
    create_captcha,
    get_form_token,
    ip_fingerprint,
    issue_form_token,
    validate_captcha,
)
from products.models import Product, ProductCategory


def absolute_media_url(request, field_file):
    if not field_file:
        return ""
    url = field_file.url
    if url.startswith(settings.MEDIA_URL):
        return url
    return request.build_absolute_uri(url)


def normalize_model(value):
    return re.sub(r"[\s-]+", "", value or "").lower()


def published_products():
    filters = {"status": ContentStatus.PUBLISHED, "category__is_active": True}
    if settings.SITE_CONTENT_MODE == "production":
        filters.update(is_demo=False, verification_status=VerificationStatus.VERIFIED)
    return (
        Product.objects.filter(**filters)
        .select_related("category")
        .prefetch_related("specifications", "highlights", "applications", "gallery", "documents", "related_products")
    )


def published_articles():
    filters = {"status": ContentStatus.PUBLISHED, "category__is_active": True}
    if settings.SITE_CONTENT_MODE == "production":
        filters.update(is_demo=False, verification_status=VerificationStatus.VERIFIED)
    return Article.objects.filter(**filters).select_related("category")


def public_product_filter(prefix=""):
    filters = {f"{prefix}status": ContentStatus.PUBLISHED}
    if settings.SITE_CONTENT_MODE == "production":
        filters.update({
            f"{prefix}is_demo": False,
            f"{prefix}verification_status": VerificationStatus.VERIFIED,
        })
    return filters


def public_article_filter(prefix=""):
    filters = {f"{prefix}status": ContentStatus.PUBLISHED}
    if settings.SITE_CONTENT_MODE == "production":
        filters.update({
            f"{prefix}is_demo": False,
            f"{prefix}verification_status": VerificationStatus.VERIFIED,
        })
    return filters


def error_response(code, message, status_code, errors=None):
    payload = {"code": code, "message": message}
    if errors:
        payload["errors"] = errors
    return Response(payload, status=status_code)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    code = "error"
    message = "请求处理失败。"
    errors = None

    if isinstance(exc, NotFound):
        code = "not_found"
        message = "请求的内容不存在。"
    elif isinstance(exc, ValidationError):
        code = "validation_error"
        message = "提交信息有误，请检查后重试。"
        errors = response.data
    elif isinstance(exc, APIException):
        code = getattr(exc, "default_code", "api_error")
        message = str(response.data.get("detail", "请求处理失败。")) if isinstance(response.data, dict) else "请求处理失败。"

    response.data = {"code": code, "message": message}
    if errors:
        response.data["errors"] = errors
    return response


class PublicPagination:
    def __init__(self, *, page_size):
        self.page_size = page_size

    def paginate(self, request, queryset):
        try:
            page = int(request.query_params.get("page", "1"))
        except ValueError as exc:
            raise ValidationError({"page": ["页码必须是数字。"]}) from exc
        if page < 1:
            raise ValidationError({"page": ["页码不能小于 1。"]})

        count = queryset.count()
        total_pages = max(1, math.ceil(count / self.page_size))
        if count and page > total_pages:
            raise NotFound("页码超出范围。")

        start = (page - 1) * self.page_size
        end = start + self.page_size
        self.page = page
        self.count = count
        self.total_pages = total_pages
        return queryset[start:end]

    def response(self, request, results):
        path = request.path
        query = request.GET.copy()

        def page_url(page):
            query["page"] = page
            return f"{path}?{query.urlencode()}"

        return Response({
            "count": self.count,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "next": page_url(self.page + 1) if self.page < self.total_pages else None,
            "previous": page_url(self.page - 1) if self.page > 1 else None,
            "results": results,
        })


class ProductCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    item_count = serializers.IntegerField()

    class Meta:
        model = ProductCategory
        fields = ("name", "slug", "description", "image", "item_count")

    @extend_schema_field(OpenApiTypes.STR)
    def get_image(self, obj) -> str:
        return absolute_media_url(self.context["request"], obj.image_thumb or obj.image_web or obj.image)


class ProductCardSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    category_slug = serializers.CharField(source="category.slug")
    image = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "name", "model", "level", "summary", "category", "category_slug",
            "image", "homepage_badge", "specs", "is_demo", "verification_status",
        )

    @extend_schema_field(OpenApiTypes.STR)
    def get_image(self, obj) -> str:
        return absolute_media_url(self.context["request"], obj.image_thumb or obj.image_web or obj.image)

    def get_specs(self, obj) -> list[dict]:
        return [
            {"name": item.name, "value": item.value}
            for item in obj.specifications.all()
            if item.show_on_card
        ][:4]


class ProductDetailSerializer(ProductCardSerializer):
    description = serializers.CharField()
    image_web = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    highlights = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta(ProductCardSerializer.Meta):
        fields = ProductCardSerializer.Meta.fields + (
            "description", "image_web", "gallery", "specifications", "highlights",
            "applications", "documents", "related_products", "seo",
        )

    def get_image_web(self, obj) -> str:
        return absolute_media_url(self.context["request"], obj.image_web or obj.image)

    def get_gallery(self, obj) -> list[dict]:
        images = [
            {
                "image": absolute_media_url(self.context["request"], obj.image_web or obj.image),
                "thumb": absolute_media_url(self.context["request"], obj.image_thumb or obj.image),
                "alt": f"{obj.name}产品主图",
                "caption": obj.summary,
            }
        ]
        images.extend({
            "image": absolute_media_url(self.context["request"], item.image_web or item.image),
            "thumb": absolute_media_url(self.context["request"], item.image_thumb or item.image),
            "alt": item.alt_text,
            "caption": item.caption,
        } for item in obj.gallery.all())
        return images

    def get_specifications(self, obj) -> list[dict]:
        return [{"name": item.name, "value": item.value, "show_on_card": item.show_on_card} for item in obj.specifications.all()]

    def get_highlights(self, obj) -> list[dict]:
        return [{"title": item.title, "description": item.description} for item in obj.highlights.all()]

    def get_applications(self, obj) -> list[dict]:
        return [{"name": item.name, "description": item.description} for item in obj.applications.all()]

    def get_documents(self, obj) -> list[dict]:
        return [{
            "name": item.name,
            "type": item.document_type,
            "language": item.language,
            "file": absolute_media_url(self.context["request"], item.file),
            "is_demo": item.is_demo,
            "disclaimer": item.disclaimer,
        } for item in obj.documents.all()]

    def get_related_products(self, obj) -> list[dict]:
        manual_ids = list(obj.related_products.filter(status=ContentStatus.PUBLISHED, category__is_active=True).values_list("id", flat=True))
        related = list(published_products().filter(id__in=manual_ids).exclude(id=obj.id)[:3])
        if len(related) < 3:
            existing_ids = [item.id for item in related] + [obj.id]
            related.extend(list(
                published_products()
                .filter(category=obj.category)
                .exclude(id__in=existing_ids)
                .order_by("sort_order", "id")[: 3 - len(related)]
            ))
        return ProductCardSerializer(related, many=True, context=self.context).data

    def get_seo(self, obj) -> dict:
        return {
            "title": obj.seo_title or f"{obj.name} {obj.model} - 华丽电器",
            "description": obj.seo_description or obj.summary,
        }


class ProductOptionSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("name", "model", "label", "image")

    def get_label(self, obj) -> str:
        return f"{obj.name}（{obj.model}）"

    @extend_schema_field(OpenApiTypes.STR)
    def get_image(self, obj) -> str:
        return absolute_media_url(self.context["request"], obj.image_thumb or obj.image_web or obj.image)


class NewsCategorySerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField()

    class Meta:
        model = NewsCategory
        fields = ("name", "slug", "description", "item_count")


class NewsCardSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    category_slug = serializers.CharField(source="category.slug")
    image = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "title", "slug", "summary", "category", "category_slug", "source", "date", "image",
            "is_demo", "verification_status",
        )

    def get_image(self, obj) -> str:
        return absolute_media_url(self.context["request"], obj.cover_thumb or obj.cover_web or obj.cover)

    def get_date(self, obj) -> str:
        return timezone.localtime(obj.published_at).date().isoformat() if obj.published_at else ""


class NewsDetailSerializer(NewsCardSerializer):
    body = serializers.CharField()
    cover = serializers.SerializerMethodField()
    related_news = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta(NewsCardSerializer.Meta):
        fields = NewsCardSerializer.Meta.fields + ("body", "cover", "related_news", "seo")

    def get_cover(self, obj) -> str:
        return absolute_media_url(self.context["request"], obj.cover_web or obj.cover)

    def get_related_news(self, obj) -> list[dict]:
        related = list(
            published_articles()
            .filter(category=obj.category)
            .exclude(id=obj.id)
            .order_by("-published_at", "-id")[:3]
        )
        if len(related) < 3:
            existing_ids = [item.id for item in related] + [obj.id]
            related.extend(list(
                published_articles()
                .exclude(id__in=existing_ids)
                .order_by("-published_at", "-id")[: 3 - len(related)]
            ))
        return NewsCardSerializer(related, many=True, context=self.context).data

    def get_seo(self, obj) -> dict:
        return {
            "title": obj.seo_title or f"{obj.title} - 华丽电器",
            "description": obj.seo_description or obj.summary,
        }


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Xunpan
        fields = (
            "contact_name", "phone", "email", "company_brand", "project_type",
            "product_name_snapshot", "product_model_snapshot", "estimated_quantity",
            "country_region", "detailed_requirements", "attachment",
        )

    def validate(self, attrs):
        model = attrs.get("product_model_snapshot")
        if model:
            product = published_products().filter(model=model).first()
            if product:
                attrs["product"] = product
                attrs["product_name_snapshot"] = product.name
                attrs["project_type"] = attrs.get("project_type") or f"{product.name}（{product.model}）"
        return attrs


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lianxi
        fields = ("contact_name", "phone", "email", "subject", "message")


def validate_filters(request, categories):
    category = request.query_params.get("category", "").strip()
    q = request.query_params.get("q", "").strip()
    if len(q) > 100:
        raise ValidationError({"q": ["搜索词不能超过 100 个字符。"]})
    if category and category not in categories:
        raise ValidationError({"category": ["分类不存在或未启用。"]})
    return category, q


@extend_schema(operation_id="product_categories_list", responses=ProductCategorySerializer(many=True))
@api_view(["GET"])
def product_categories(request):
    public_filter = public_product_filter("products__")
    queryset = (
        ProductCategory.objects.filter(is_active=True)
        .annotate(item_count=Count("products", filter=Q(**public_filter)))
        .filter(item_count__gt=0)
        .order_by("sort_order", "id")
    )
    return Response(ProductCategorySerializer(queryset, many=True, context={"request": request}).data)


@extend_schema(operation_id="products_list", responses=ProductCardSerializer(many=True))
@api_view(["GET"])
def product_list(request):
    category_slugs = set(ProductCategory.objects.filter(is_active=True).values_list("slug", flat=True))
    category, q = validate_filters(request, category_slugs)
    queryset = published_products().order_by("sort_order", "id")
    if category:
        queryset = queryset.filter(category__slug=category)
    if q:
        normalized = normalize_model(q)
        queryset = queryset.filter(Q(search_text__icontains=q) | Q(search_text__icontains=normalized))
    paginator = PublicPagination(page_size=12)
    page_items = paginator.paginate(request, queryset)
    data = ProductCardSerializer(page_items, many=True, context={"request": request}).data
    return paginator.response(request, data)


@extend_schema(operation_id="product_detail", responses=ProductDetailSerializer)
@api_view(["GET"])
def product_detail(request, model):
    normalized = normalize_model(model)
    product = next((item for item in published_products() if item.normalized_model == normalized), None)
    if not product:
        raise NotFound("产品不存在。")
    return Response(ProductDetailSerializer(product, context={"request": request}).data)


@extend_schema(operation_id="product_options_list", responses=ProductOptionSerializer(many=True))
@api_view(["GET"])
def product_options(request):
    queryset = published_products().order_by("category__sort_order", "sort_order", "id")
    return Response(ProductOptionSerializer(queryset, many=True, context={"request": request}).data)


@extend_schema(operation_id="news_categories_list", responses=NewsCategorySerializer(many=True))
@api_view(["GET"])
def news_categories(request):
    public_filter = public_article_filter("articles__")
    queryset = (
        NewsCategory.objects.filter(is_active=True)
        .annotate(item_count=Count("articles", filter=Q(**public_filter)))
        .filter(item_count__gt=0)
        .order_by("sort_order", "id")
    )
    return Response(NewsCategorySerializer(queryset, many=True).data)


@extend_schema(operation_id="news_list", responses=NewsCardSerializer(many=True))
@api_view(["GET"])
def news_list(request):
    category_slugs = set(NewsCategory.objects.filter(is_active=True).values_list("slug", flat=True))
    category, q = validate_filters(request, category_slugs)
    queryset = published_articles().order_by("-published_at", "-id")
    if category:
        queryset = queryset.filter(category__slug=category)
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(source__icontains=q) | Q(body_text__icontains=q))
    paginator = PublicPagination(page_size=8)
    page_items = paginator.paginate(request, queryset)
    data = NewsCardSerializer(page_items, many=True, context={"request": request}).data
    return paginator.response(request, data)


@extend_schema(operation_id="news_detail", responses=NewsDetailSerializer)
@api_view(["GET"])
def news_detail(request, slug):
    article = published_articles().filter(slug=slug).first()
    if not article:
        raise NotFound("新闻不存在。")
    return Response(NewsDetailSerializer(article, context={"request": request}).data)


@extend_schema(operation_id="homepage_retrieve", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def homepage(request):
    product_query = published_products().order_by("is_featured", "featured_order", "sort_order", "id")
    featured_products = list(published_products().filter(is_featured=True).order_by("featured_order", "sort_order", "id")[:6])
    if len(featured_products) < 6:
        existing_ids = [item.id for item in featured_products]
        featured_products.extend(list(product_query.exclude(id__in=existing_ids)[: 6 - len(featured_products)]))

    featured_news = list(published_articles().filter(is_featured=True).order_by("featured_order", "-published_at", "-id")[:3])
    if len(featured_news) < 3:
        existing_ids = [item.id for item in featured_news]
        featured_news.extend(list(published_articles().exclude(id__in=existing_ids).order_by("-published_at", "-id")[: 3 - len(featured_news)]))

    return Response({
        "products": ProductCardSerializer(featured_products, many=True, context={"request": request}).data,
        "news": NewsCardSerializer(featured_news, many=True, context={"request": request}).data,
    })


def current_privacy_policy():
    return PrivacyPolicy.objects.filter(status=PrivacyPolicy.Status.PUBLISHED).order_by("-published_at", "-id").first()


def security_error_response(exc):
    payload = {"code": exc.code, "message": exc.message}
    payload.update(exc.extra)
    return Response(payload, status=exc.status_code)


def validate_csrf(request):
    django_request = request._request
    check = CSRFCheck(lambda current_request: None)
    check.process_request(django_request)
    reason = check.process_view(django_request, None, (), {})
    if reason:
        raise FormSecurityError("csrf_failed", "安全令牌已失效，请刷新页面后重新提交。", status_code=403)


def rate_limit_or_raise(model, fingerprint, *, minutes, limit):
    since = timezone.now() - timedelta(minutes=minutes)
    recent = model.objects.filter(ip_fingerprint=fingerprint, created_at__gte=since).order_by("created_at")
    if recent.count() < limit:
        return
    oldest = recent.first()
    retry_after = max(1, int((oldest.created_at + timedelta(minutes=minutes) - timezone.now()).total_seconds()))
    raise FormSecurityError(
        "rate_limited",
        f"提交过于频繁，请在 {max(1, (retry_after + 59) // 60)} 分钟后重试。",
        status_code=429,
        extra={"retry_after": retry_after},
    )


@extend_schema(operation_id="forms_bootstrap", responses=OpenApiTypes.OBJECT)
@ensure_csrf_cookie
@api_view(["GET"])
def forms_bootstrap(request):
    kind = request.query_params.get("kind", "")
    if kind not in {"inquiry", "contact"}:
        return error_response("validation_error", "kind 必须是 inquiry 或 contact。", 400)
    policy = current_privacy_policy()
    get_token(request)
    return Response({
        "form_enabled": bool(policy),
        "form_token": issue_form_token(request, kind) if policy else "",
        "privacy_version": policy.version if policy else "",
        "privacy_title": policy.title_zh if policy else "隐私政策待审核",
        "captcha_required": False,
        "message": "" if policy else "当前隐私政策尚未发布，在线表单暂不可提交。",
    })


@extend_schema(operation_id="captcha_create", request=None, responses=OpenApiTypes.OBJECT)
@api_view(["POST"])
def captcha(request):
    challenge, image = create_captcha(request)
    return Response({
        "captcha_id": str(challenge.pk),
        "image": f"data:image/png;base64,{image}",
        "expires_at": challenge.expires_at.isoformat(),
    }, status=201)


@extend_schema(operation_id="privacy_policy_retrieve", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def privacy_policy(request):
    policy = current_privacy_policy()
    if not policy:
        raise NotFound("当前没有已发布的隐私政策。")
    return Response({
        "version": policy.version,
        "title_zh": policy.title_zh,
        "body_zh": policy.body_zh,
        "title_en": policy.title_en,
        "body_en": policy.body_en,
        "published_at": policy.published_at,
    })


@extend_schema(operation_id="health_retrieve", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def health(request):
    service_status = public_health_status()
    return Response({"status": service_status, "version": "2.0.0"}, status=200 if service_status != "unavailable" else 503)


def secure_form_submit(request, *, kind, serializer_class, model, minutes, limit):
    try:
        validate_csrf(request)
    except FormSecurityError as exc:
        return security_error_response(exc)
    policy = current_privacy_policy()
    if not policy:
        return error_response("privacy_policy_unavailable", "隐私政策尚未发布，在线表单暂不可用。", 503)
    if request.data.get("website", "").strip():
        return Response({"message": "提交成功。"}, status=201)
    if request.data.get("privacy_consent") not in {True, "true", "True", "1", 1, "on"}:
        return error_response("privacy_consent_required", "请阅读并同意隐私政策。", 400)
    if request.data.get("privacy_version") != policy.version:
        return error_response("privacy_consent_required", "隐私政策版本已更新，请刷新页面后重新确认。", 400)

    try:
        with transaction.atomic():
            token = get_form_token(request, request.data.get("form_token"), kind)
            fingerprint = token.ip_fingerprint
            rate_limit_or_raise(model, fingerprint, minutes=minutes, limit=limit)
            needs_captcha = captcha_required(request, token, model)
            if needs_captcha and not request.data.get("captcha_id"):
                raise FormSecurityError("captcha_required", "请完成验证码后再次提交。")
            if needs_captcha:
                validate_captcha(request, request.data.get("captcha_id"), request.data.get("captcha_answer"))

            scan_status = "not_applicable"
            attachment = request.FILES.get("attachment")
            if attachment:
                try:
                    scan_status = validate_and_scan_attachment(attachment)
                except AttachmentScanUnavailable as exc:
                    raise FormSecurityError("attachment_scan_unavailable", str(exc)) from exc
                except Exception as exc:
                    raise FormSecurityError("attachment_unsafe", str(exc)) from exc

            serializer = serializer_class(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            extra = {
                "privacy_policy": policy,
                "privacy_consented_at": timezone.now(),
                "ip_fingerprint": fingerprint,
                "form_token_id": str(token.pk),
            }
            if kind == "inquiry":
                extra["attachment_scan_status"] = scan_status
            else:
                extra["security_scan_status"] = "passed"
            lead = serializer.save(**extra)
            token.used_at = timezone.now()
            token.save(update_fields=("used_at",))
            queue_lead_messages(lead, kind)
    except FormSecurityError as exc:
        return security_error_response(exc)
    return Response({"id": lead.pk, "message": "询盘提交成功。" if kind == "inquiry" else "留言提交成功。"}, status=201)


@extend_schema(operation_id="inquiries_create", request=InquirySerializer, responses=OpenApiTypes.OBJECT)
@csrf_protect
@api_view(["POST"])
def inquiries(request):
    return secure_form_submit(request, kind="inquiry", serializer_class=InquirySerializer, model=Xunpan, minutes=30, limit=3)


@extend_schema(operation_id="contacts_create", request=ContactSerializer, responses=OpenApiTypes.OBJECT)
@csrf_protect
@api_view(["POST"])
def contacts(request):
    return secure_form_submit(request, kind="contact", serializer_class=ContactSerializer, model=Lianxi, minutes=10, limit=5)


def deprecated_alias(view_func):
    def wrapped(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response["Deprecation"] = "true"
        response["Link"] = '</api/v1/>; rel="successor-version"'
        return response
    return wrapped


urlpatterns = [
    path("forms/bootstrap/", forms_bootstrap, name="forms-bootstrap"),
    path("captcha/", captcha, name="captcha"),
    path("privacy-policy/", privacy_policy, name="privacy-policy"),
    path("health/", health, name="health"),
    path("site-content/", site_content, name="site-content"),
    path("locations/", locations, name="locations"),
    path("faqs/", faqs, name="faqs"),
    path("honor-categories/", honor_categories, name="honor-categories"),
    path("honors/", honors, name="honors"),
    path("product-categories/", product_categories, name="product-categories"),
    path("products/", product_list, name="products"),
    path("products/<str:model>/", product_detail, name="product-detail"),
    path("product-options/", product_options, name="product-options"),
    path("news-categories/", news_categories, name="news-categories"),
    path("news/", news_list, name="news-list"),
    path("news/<slug:slug>/", news_detail, name="news-detail"),
    path("homepage/", homepage, name="homepage"),
    path("inquiries/", inquiries, name="v1-inquiries"),
    path("contacts/", contacts, name="v1-contacts"),
]

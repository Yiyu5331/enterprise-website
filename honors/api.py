from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_field

from main.content_utils import ContentStatus, public_content_allowed

from .models import Honor, HonorCategory


def visible_honors():
    return [
        item for item in Honor.objects.select_related("category", "source").filter(
            status=ContentStatus.PUBLISHED, category__is_active=True,
        )
        if public_content_allowed(is_demo=item.is_demo, verification_status=item.verification_status)
    ]


class HonorCategorySerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField()

    class Meta:
        model = HonorCategory
        fields = ("name", "slug", "description", "item_count")


class HonorSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.slug")
    image = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()

    class Meta:
        model = Honor
        fields = (
            "slug", "category", "title", "summary", "reference_number", "issuer",
            "awarded_on", "image", "document", "use_watermark", "is_demo",
        )

    @extend_schema_field(OpenApiTypes.STR)
    def get_image(self, obj):
        return obj.display_image.url if obj.display_image else None

    @extend_schema_field(OpenApiTypes.STR)
    def get_document(self, obj):
        if not obj.document or not obj.allow_document_download:
            return None
        return obj.document.url


@extend_schema(operation_id="honor_categories_list", responses=HonorCategorySerializer(many=True))
@api_view(["GET"])
def honor_categories(request):
    visible_ids = [item.pk for item in visible_honors()]
    queryset = HonorCategory.objects.filter(is_active=True).annotate(
        item_count=Count("honors", filter=Q(honors__pk__in=visible_ids)),
    ).filter(item_count__gt=0)
    return Response(HonorCategorySerializer(queryset, many=True).data)


@extend_schema(operation_id="honors_list", responses=HonorSerializer(many=True))
@api_view(["GET"])
def honors(request):
    category = request.query_params.get("category", "").strip()
    items = visible_honors()
    if category:
        if not HonorCategory.objects.filter(slug=category, is_active=True).exists():
            return Response({"code": "invalid_category", "message": "荣誉分类不存在。"}, status=400)
        items = [item for item in items if item.category.slug == category]
    return Response(HonorSerializer(items, many=True).data)

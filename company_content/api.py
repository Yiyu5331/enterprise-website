from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from main.content_utils import ContentStatus, public_content_allowed

from .models import (
    CompanyFact, CompanyProfile, CompanyTimeline, DealerBenefit, FAQ,
    FAQCategory, Location, SupplyChainItem,
)


def visible(queryset):
    return [
        item for item in queryset.filter(status=ContentStatus.PUBLISHED)
        if public_content_allowed(is_demo=item.is_demo, verification_status=item.verification_status)
    ]


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = (
            "name_zh", "name_en", "brand_name", "summary", "legal_representative",
            "founded_on", "registered_capital", "credit_code", "registered_address", "is_demo",
        )


class CompanyFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyFact
        fields = ("label", "value", "unit", "description", "is_demo")


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyTimeline
        fields = ("year", "title", "description", "is_demo")


class SupplyChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyChainItem
        fields = ("kind", "title", "description", "is_demo")


class DealerBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerBenefit
        fields = ("title", "description", "is_demo")


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            "kind", "name", "address_zh", "address_en", "longitude", "latitude",
            "phone", "email", "business_hours", "is_demo",
        )


class FAQSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.slug")

    class Meta:
        model = FAQ
        fields = ("id", "category", "question", "answer", "is_demo")


@extend_schema(operation_id="site_content_retrieve", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def site_content(request):
    profiles = visible(CompanyProfile.objects.select_related("source").order_by("sort_order", "id"))
    return Response({
        "profile": CompanyProfileSerializer(profiles[0]).data if profiles else None,
        "facts": CompanyFactSerializer(visible(CompanyFact.objects.all()), many=True).data,
        "timeline": TimelineSerializer(visible(CompanyTimeline.objects.all()), many=True).data,
        "supply_chain": SupplyChainSerializer(visible(SupplyChainItem.objects.all()), many=True).data,
        "dealer_benefits": DealerBenefitSerializer(visible(DealerBenefit.objects.all()), many=True).data,
        "locations": LocationSerializer(visible(Location.objects.all()), many=True).data,
    })


@extend_schema(operation_id="locations_list", responses=LocationSerializer(many=True))
@api_view(["GET"])
def locations(request):
    return Response(LocationSerializer(visible(Location.objects.all()), many=True).data)


@extend_schema(operation_id="faqs_list", responses=FAQSerializer(many=True))
@api_view(["GET"])
def faqs(request):
    categories = set(FAQCategory.objects.filter(is_active=True).values_list("slug", flat=True))
    category = request.query_params.get("category", "").strip()
    if category and category not in categories:
        return Response({"code": "invalid_category", "message": "常见问题分类不存在。"}, status=400)
    queryset = FAQ.objects.select_related("category").filter(category__is_active=True)
    if category:
        queryset = queryset.filter(category__slug=category)
    return Response(FAQSerializer(visible(queryset), many=True).data)

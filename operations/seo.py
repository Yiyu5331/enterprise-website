from django.conf import settings

from main.content_utils import ContentStatus
from news.models import Article, NewsCategory
from products.models import Product, ProductCategory


STATIC_INDEXABLE_PATHS = ("/", "/about/", "/products/", "/news/", "/supply-chain/", "/dealer/", "/contact/")


def indexable_paths():
    paths = list(STATIC_INDEXABLE_PATHS)
    paths.extend(f"/products/category/{slug}/" for slug in ProductCategory.objects.filter(is_active=True).values_list("slug", flat=True))
    paths.extend(
        f"/products/{category_slug}/{model}/"
        for category_slug, model in Product.objects.filter(status=ContentStatus.PUBLISHED, category__is_active=True).values_list("category__slug", "model")
    )
    paths.extend(f"/news/category/{slug}/" for slug in NewsCategory.objects.filter(is_active=True).values_list("slug", flat=True))
    paths.extend(
        f"/news/{category_slug}/{slug}/"
        for category_slug, slug in Article.objects.filter(status=ContentStatus.PUBLISHED, category__is_active=True).values_list("category__slug", "slug")
    )
    return sorted(set(paths))


def absolute_url(path):
    return f"{settings.SITE_URL}{path}"

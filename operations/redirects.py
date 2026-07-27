from django.http import Http404, HttpResponsePermanentRedirect

from main.content_utils import ContentStatus
from news.models import Article
from products.models import Product


def old_product_url(request, model):
    product = Product.objects.filter(model=model, status=ContentStatus.PUBLISHED, category__is_active=True).select_related("category").first()
    if not product:
        raise Http404
    return HttpResponsePermanentRedirect(f"/products/{product.category.slug}/{product.model}/")


def old_news_url(request, slug):
    article = Article.objects.filter(slug=slug, status=ContentStatus.PUBLISHED, category__is_active=True).select_related("category").first()
    if not article:
        raise Http404
    return HttpResponsePermanentRedirect(f"/news/{article.category.slug}/{article.slug}/")

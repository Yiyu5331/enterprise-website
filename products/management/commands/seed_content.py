from datetime import datetime, time
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from main.content_utils import ContentStatus
from main.models import Lianxi, Xunpan
from news.models import Article, NewsCategory
from news.seed_data import ARTICLES, NEWS_CATEGORIES
from products.models import (
    Product,
    ProductApplication,
    ProductCategory,
    ProductHighlight,
    ProductSpecification,
)
from products.seed_data import COMMON_HIGHLIGHTS, PRODUCT_CATEGORIES, PRODUCTS


def article_body(data):
    return "".join(f"<p>{paragraph}</p>" for paragraph in data["content"])


class Command(BaseCommand):
    help = "幂等导入网站现有的产品、新闻及媒体资产。"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的种子内容。")
        parser.add_argument("--check", action="store_true", help="只检查缺失或差异，不写数据库。")

    def handle(self, *args, **options):
        self.overwrite = options["overwrite"]
        self.check_only = options["check"]
        self.asset_root = Path(settings.BASE_DIR) / "seed_assets"
        self.changes = []
        if not self.asset_root.exists():
            raise CommandError("找不到 seed_assets 目录。")

        form_counts = (Xunpan.objects.count(), Lianxi.objects.count())
        with transaction.atomic():
            self.seed_product_categories()
            self.seed_products()
            self.seed_news_categories()
            self.seed_articles()

            if form_counts != (Xunpan.objects.count(), Lianxi.objects.count()):
                raise CommandError("检测到表单数据数量变化，已回滚本次导入。")

        if self.check_only:
            if self.changes:
                self.stdout.write(self.style.WARNING(f"检测到 {len(self.changes)} 项缺失或差异："))
                for message in self.changes:
                    self.stdout.write(f"- {message}")
            else:
                self.stdout.write(self.style.SUCCESS("数据库内容与种子数据一致。"))
            return

        self.stdout.write(self.style.SUCCESS(
            f"内容导入完成：{Product.objects.count()} 款产品，{Article.objects.count()} 条新闻；"
            f"询盘/联系表单保持 {form_counts[0]}/{form_counts[1]} 条。"
        ))

    def asset_file(self, kind, name):
        path = self.asset_root / kind / name
        if not path.is_file():
            raise CommandError(f"缺少种子媒体：{path}")
        return path

    def note(self, message):
        self.changes.append(message)

    def compare_fields(self, label, obj, expected):
        if not obj:
            self.note(f"缺少：{label}")
            return
        for field, value in expected.items():
            if getattr(obj, field) != value:
                self.note(f"{label} 字段差异：{field}")

    def seed_product_categories(self):
        for index, data in enumerate(PRODUCT_CATEGORIES):
            obj = ProductCategory.objects.filter(slug=data["slug"]).first()
            if self.check_only:
                self.asset_file("products", data["image"])
                self.compare_fields(f"产品分类 {data['slug']}", obj, {
                    "name": data["name"],
                    "description": data["description"],
                    "sort_order": index,
                    "is_active": True,
                })
                continue
            if obj and not self.overwrite:
                continue
            obj = obj or ProductCategory(slug=data["slug"])
            obj.name = data["name"]
            obj.description = data["description"]
            obj.sort_order = index
            obj.is_active = True
            with self.asset_file("products", data["image"]).open("rb") as source:
                obj.image = File(source, name=data["image"])
                obj.full_clean()
                obj.save()

    def seed_products(self):
        categories = {item.name: item for item in ProductCategory.objects.all()}
        for data in PRODUCTS:
            obj = Product.objects.filter(model=data["model"]).first()
            if self.check_only:
                category_asset = next(item["image"] for item in PRODUCT_CATEGORIES if item["name"] == data["category"])
                self.asset_file("products", category_asset)
                self.compare_fields(f"产品 {data['model']}", obj, {
                    "name": data["name"],
                    "level": data["level"],
                    "summary": data["summary"],
                    "description": data["description"],
                    "status": ContentStatus.PUBLISHED,
                    "sort_order": data["sort_order"],
                    "is_featured": data["is_featured"],
                    "featured_order": data["sort_order"],
                })
                if obj:
                    if obj.category.name != data["category"]:
                        self.note(f"产品 {data['model']} 字段差异：category")
                    specs = list(obj.specifications.values_list("name", "value"))
                    if specs != data["specs"]:
                        self.note(f"产品 {data['model']} 参数差异")
                    highlights = list(obj.highlights.values_list("title", "description"))
                    if highlights != COMMON_HIGHLIGHTS:
                        self.note(f"产品 {data['model']} 特点差异")
                    applications = list(obj.applications.values_list("name", flat=True))
                    if applications != data["applications"]:
                        self.note(f"产品 {data['model']} 应用场景差异")
                continue
            if obj and not self.overwrite:
                continue
            category = categories[data["category"]]
            obj = obj or Product(model=data["model"])
            obj.category = category
            obj.name = data["name"]
            obj.level = data["level"]
            obj.summary = data["summary"]
            obj.description = data["description"]
            obj.status = ContentStatus.DRAFT
            obj.sort_order = data["sort_order"]
            obj.is_featured = data["is_featured"]
            obj.featured_order = data["sort_order"]
            with self.asset_file("products", next(item["image"] for item in PRODUCT_CATEGORIES if item["name"] == data["category"])).open("rb") as source:
                obj.image = File(source, name=f"{data['model']}.webp")
                obj.full_clean()
                obj.save()

            obj.specifications.all().delete()
            obj.highlights.all().delete()
            obj.applications.all().delete()
            ProductSpecification.objects.bulk_create([
                ProductSpecification(product=obj, name=name, value=value, show_on_card=True, sort_order=index)
                for index, (name, value) in enumerate(data["specs"])
            ])
            ProductHighlight.objects.bulk_create([
                ProductHighlight(product=obj, title=title, description=description, sort_order=index)
                for index, (title, description) in enumerate(COMMON_HIGHLIGHTS)
            ])
            ProductApplication.objects.bulk_create([
                ProductApplication(product=obj, name=name, description=f"适用于{name}相关工况。", sort_order=index)
                for index, name in enumerate(data["applications"])
            ])
            obj.status = ContentStatus.PUBLISHED
            obj.first_published_at = obj.first_published_at or timezone.now()
            obj.validate_for_publish()
            obj.save()
            obj.rebuild_search_text()

    def seed_news_categories(self):
        for index, data in enumerate(NEWS_CATEGORIES):
            obj = NewsCategory.objects.filter(slug=data["slug"]).first()
            if self.check_only:
                self.compare_fields(f"新闻分类 {data['slug']}", obj, {
                    "name": data["name"],
                    "description": f"华丽电器的{data['name']}内容。",
                    "sort_order": index,
                    "is_active": True,
                })
                continue
            if obj and not self.overwrite:
                continue
            obj = obj or NewsCategory(slug=data["slug"])
            obj.name = data["name"]
            obj.description = f"华丽电器的{data['name']}内容。"
            obj.sort_order = index
            obj.is_active = True
            obj.full_clean()
            obj.save()

    def seed_articles(self):
        categories = {item.name: item for item in NewsCategory.objects.all()}
        for index, data in enumerate(ARTICLES):
            obj = Article.objects.filter(slug=data["slug"]).first()
            if self.check_only:
                self.asset_file("news", data["image"])
                published_at = timezone.make_aware(datetime.combine(datetime.fromisoformat(data["date"]).date(), time(9)))
                self.compare_fields(f"新闻 {data['slug']}", obj, {
                    "title": data["title"],
                    "summary": data["summary"],
                    "body": article_body(data),
                    "source": "华丽电器",
                    "published_at": published_at,
                    "status": ContentStatus.PUBLISHED,
                    "is_featured": index < 3,
                    "featured_order": index,
                    "cover_alt": data["title"],
                })
                if obj and obj.category.name != data["category"]:
                    self.note(f"新闻 {data['slug']} 字段差异：category")
                continue
            if obj and not self.overwrite:
                continue
            published_at = timezone.make_aware(datetime.combine(datetime.fromisoformat(data["date"]).date(), time(9)))
            obj = obj or Article(slug=data["slug"])
            obj.category = categories[data["category"]]
            obj.title = data["title"]
            obj.summary = data["summary"]
            obj.body = article_body(data)
            obj.source = "华丽电器"
            obj.published_at = published_at
            obj.first_published_at = obj.first_published_at or published_at
            obj.status = ContentStatus.PUBLISHED
            obj.is_featured = index < 3
            obj.featured_order = index
            obj.cover_alt = data["title"]
            with self.asset_file("news", data["image"]).open("rb") as source:
                obj.cover = File(source, name=data["image"])
                obj.full_clean()
                obj.save()

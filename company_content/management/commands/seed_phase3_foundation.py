from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from company_content.models import (
    CompanyFact, CompanyProfile, CompanyTimeline, ContentSource, DealerBenefit,
    FAQ, FAQCategory, Location, SupplyChainItem,
)
from company_content.seed_data import (
    DEALER_BENEFITS, FACTS, FAQ_CATEGORIES, FAQS, HONOR_CATEGORIES, HONORS,
    MEDIA_SLOTS, PROFILE, SUPPLY_CHAIN, TIMELINE,
)
from honors.models import Honor, HonorCategory
from main.content_utils import ContentStatus, VerificationStatus
from main.content_utils import delete_field_file
from main.models import Lianxi, Xunpan
from news.demo_data import DEMO_ARTICLES
from news.models import Article, NewsCategory
from page_builder.models import AssetLicense, AssetSlot, MediaFolder, MediaTag
from products.demo_data import DEMO_CATEGORIES, DEMO_PRODUCTS, STANDARD_PARAMETERS
from products.models import (
    ParameterMappingSuggestion, Product, ProductApplication, ProductCategory,
    ProductDocument, ProductHighlight, ProductSpecification, StandardParameter,
)


class Command(BaseCommand):
    help = "幂等初始化第三阶段基础数据、演示内容、标准参数和媒体槽位。"

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true", help="只检查差异，不写数据库。")
        parser.add_argument("--overwrite", action="store_true", help="覆盖已有的第三阶段种子记录。")

    def handle(self, *args, **options):
        self.check_only = options["check"]
        self.overwrite = options["overwrite"]
        self.changes = []
        self.asset_root = Path(settings.BASE_DIR) / "seed_assets"
        self.product_assets = {slug: image for _, slug, image in DEMO_CATEGORIES}
        form_counts = (Xunpan.objects.count(), Lianxi.objects.count())

        with transaction.atomic():
            self.seed_sources_and_company()
            self.seed_company_sections()
            self.seed_faqs()
            self.seed_honors()
            self.seed_media_foundation()
            self.seed_standard_parameters()
            self.seed_demo_products()
            self.seed_demo_news()
            if form_counts != (Xunpan.objects.count(), Lianxi.objects.count()):
                raise CommandError("检测到询盘或联系表单数量变化，已回滚初始化。")
            if self.check_only:
                transaction.set_rollback(True)

        if self.check_only:
            if self.changes:
                self.stdout.write(self.style.WARNING(f"检测到 {len(self.changes)} 项待处理："))
                for item in self.changes:
                    self.stdout.write(f"- {item}")
            else:
                self.stdout.write(self.style.SUCCESS("第三阶段基础数据与种子定义一致。"))
            return

        self.stdout.write(self.style.SUCCESS(
            "第三阶段基础数据完成："
            f"演示产品 {Product.objects.filter(is_demo=True).count()} 款，"
            f"演示新闻 {Article.objects.filter(is_demo=True).count()} 条，"
            f"荣誉 {Honor.objects.count()} 条，FAQ {FAQ.objects.count()} 条；"
            f"询盘/联系表单保持 {form_counts[0]}/{form_counts[1]} 条。"
        ))

    def upsert(self, model, lookup, defaults, label):
        obj = model.objects.filter(**lookup).first()
        if self.check_only:
            if not obj:
                self.changes.append(f"缺少 {label}")
                return None
            for field, value in defaults.items():
                if getattr(obj, field) != value:
                    self.changes.append(f"{label} 字段差异：{field}")
            return obj
        if obj and not self.overwrite:
            return obj
        obj = obj or model(**lookup)
        for field, value in defaults.items():
            setattr(obj, field, value)
        obj.full_clean()
        obj.save()
        return obj

    def seed_sources_and_company(self):
        source = self.upsert(ContentSource, {"name": "项目现有公司资料"}, {
            "notes": "来源于 AGENTS.md 中当前项目记录，正式上线前需补权威网页或文件。",
            "is_public": False,
        }, "公司资料来源")
        defaults = dict(PROFILE)
        defaults["founded_on"] = date.fromisoformat(defaults["founded_on"])
        defaults.update(
            status=ContentStatus.PUBLISHED,
            verification_status=VerificationStatus.PENDING,
            is_demo=False,
            source=source,
        )
        self.upsert(CompanyProfile, {"name_zh": PROFILE["name_zh"]}, defaults, "企业资料")
        self.upsert(Location, {"name": "华丽电器制造基地"}, {
            "kind": Location.Kind.FACTORY,
            "address_zh": PROFILE["registered_address"],
            "address_en": "Wangyuan Industrial Zone, Quanxi Town, Wuyi County, Jinhua, Zhejiang, China",
            "status": ContentStatus.PUBLISHED,
            "verification_status": VerificationStatus.PENDING,
            "is_demo": False,
            "source": source,
        }, "公司地点")

    def seed_company_sections(self):
        source = ContentSource.objects.filter(name="项目现有公司资料").first()
        for index, (label, value, unit, description, is_demo) in enumerate(FACTS):
            self.upsert(CompanyFact, {"label": label}, {
                "value": value, "unit": unit, "description": description,
                "status": ContentStatus.PUBLISHED, "is_demo": is_demo,
                "verification_status": VerificationStatus.PENDING,
                "source": source, "sort_order": index,
            }, f"企业指标 {label}")
        for index, (year, title, description) in enumerate(TIMELINE):
            self.upsert(CompanyTimeline, {"year": year, "title": title}, {
                "description": description, "status": ContentStatus.PUBLISHED,
                "verification_status": VerificationStatus.PENDING, "source": source,
                "sort_order": index,
            }, f"发展历程 {year}")
        for index, (kind, title, description) in enumerate(SUPPLY_CHAIN):
            self.upsert(SupplyChainItem, {"kind": kind, "title": title}, {
                "description": description, "status": ContentStatus.PUBLISHED,
                "verification_status": VerificationStatus.PENDING, "is_demo": True,
                "sort_order": index,
            }, f"供应链内容 {title}")
        for index, (title, description) in enumerate(DEALER_BENEFITS):
            self.upsert(DealerBenefit, {"title": title}, {
                "description": description, "status": ContentStatus.PUBLISHED,
                "verification_status": VerificationStatus.PENDING, "is_demo": True,
                "sort_order": index,
            }, f"经销商权益 {title}")

    def seed_faqs(self):
        categories = {}
        for index, (name, slug) in enumerate(FAQ_CATEGORIES):
            categories[slug] = self.upsert(FAQCategory, {"slug": slug}, {
                "name": name, "sort_order": index, "is_active": True,
            }, f"FAQ 分类 {name}")
        for index, (category_slug, question, answer) in enumerate(FAQS):
            self.upsert(FAQ, {"question": question}, {
                "category": categories[category_slug], "answer": answer,
                "status": ContentStatus.PUBLISHED, "is_demo": True,
                "verification_status": VerificationStatus.PENDING, "sort_order": index,
            }, f"FAQ {question}")

    def seed_honors(self):
        categories = {}
        for index, (name, slug) in enumerate(HONOR_CATEGORIES):
            categories[slug] = self.upsert(HonorCategory, {"slug": slug}, {
                "name": name, "description": f"{name}相关内容。", "sort_order": index, "is_active": True,
            }, f"荣誉分类 {name}")
        source = ContentSource.objects.filter(name="项目现有公司资料").first()
        for index, (category_slug, slug, title) in enumerate(HONORS):
            self.upsert(Honor, {"slug": slug}, {
                "category": categories[category_slug], "title": title,
                "summary": "该条目来自当前项目记录，正式使用前需补充权威来源和真实媒体。",
                "status": ContentStatus.PUBLISHED, "verification_status": VerificationStatus.PENDING,
                "is_demo": False, "source": source, "sort_order": index,
            }, f"荣誉 {title}")

    def seed_media_foundation(self):
        license = self.upsert(AssetLicense, {"name": "项目自有或已授权素材"}, {
            "license_type": AssetLicense.LicenseType.OWNED,
            "author": "华丽电器网站项目",
            "allows_commercial_use": True,
            "notes": "正式上线前仍需逐项确认真实图片与品牌素材权属。",
        }, "默认素材许可")
        for index, name in enumerate(("首页", "公司", "产品", "新闻", "供应链", "经销商", "荣誉", "联系")):
            self.upsert(MediaFolder, {"parent": None, "name": name}, {"sort_order": index}, f"媒体文件夹 {name}")
        for name, slug in (("AI占位", "ai-placeholder"), ("待替换", "needs-replacement"), ("测试内容", "demo-content"), ("真实素材", "real-media")):
            self.upsert(MediaTag, {"slug": slug}, {"name": name}, f"媒体标签 {name}")
        for key, name, ratio, width, height in MEDIA_SLOTS:
            self.upsert(AssetSlot, {"key": key}, {
                "name": name, "description": "里程碑三根据已确认页面线框生成并绑定素材。",
                "recommended_ratio": ratio, "min_width": width, "min_height": height,
            }, f"素材槽位 {name}")
        return license

    def seed_standard_parameters(self):
        for index, (name_zh, slug, name_en, unit, aliases) in enumerate(STANDARD_PARAMETERS):
            self.upsert(StandardParameter, {"slug": slug}, {
                "name_zh": name_zh, "name_en": name_en,
                "standard_unit": unit, "aliases_zh": "\n".join(aliases),
                "sort_order": index, "is_active": True,
            }, f"标准参数 {name_zh}")
        alias_map = {}
        for parameter in StandardParameter.objects.all():
            alias_map[parameter.name_zh] = (parameter, parameter.name_zh)
            for alias in parameter.aliases_zh.splitlines():
                if alias.strip():
                    alias_map[alias.strip()] = (parameter, alias.strip())
        source_names = ProductSpecification.objects.filter(
            standard_parameter__isnull=True,
        ).values_list("name", flat=True).distinct()
        for source_name in source_names:
            match = alias_map.get(source_name)
            if not match:
                continue
            parameter, matched_alias = match
            affected_count = ProductSpecification.objects.filter(
                name=source_name, standard_parameter__isnull=True,
            ).count()
            self.upsert(ParameterMappingSuggestion, {
                "source_name": source_name,
                "suggested_parameter": parameter,
            }, {
                "matched_alias": matched_alias,
                "confidence": 1,
                "affected_count": affected_count,
            }, f"参数映射建议 {source_name}")

    def seed_demo_products(self):
        representative_models = {}
        for category_slug, _, model, _ in DEMO_PRODUCTS:
            representative_models.setdefault(category_slug, model)
        categories = {}
        for index, (name, slug, image_name) in enumerate(DEMO_CATEGORIES):
            category = ProductCategory.objects.filter(slug=slug).first()
            if self.check_only:
                if not category:
                    self.changes.append(f"缺少演示产品分类 {name}")
                categories[slug] = category
                continue
            if category and not self.overwrite:
                categories[slug] = category
                continue
            category = category or ProductCategory(slug=slug)
            category.name = name
            category.description = "仅用于第三阶段产品分类、对比和视觉设计测试。"
            category.sort_order = 100 + index
            category.is_active = True
            with (self.asset_root / "products" / image_name).open("rb") as source:
                category.image = File(source, name=f"{slug}.webp")
                category.full_clean()
                category.save()
            categories[slug] = category

        for index, (category_slug, name, model, specs) in enumerate(DEMO_PRODUCTS):
            product = Product.objects.filter(model=model).first()
            if self.check_only:
                if not product:
                    self.changes.append(f"缺少演示产品 {model}")
                elif representative_models[category_slug] == model:
                    self.ensure_demo_document(product, category_slug)
                continue
            if product and not self.overwrite:
                if representative_models[category_slug] == model:
                    self.ensure_demo_document(product, category_slug)
                continue
            product = product or Product(model=model)
            product.category = categories[category_slug]
            product.name = name
            product.level = "演示级"
            product.summary = "用于测试产品列表、详情、标准参数、对比和询盘联动的概念产品。"
            product.description = "<p>该产品为网站功能测试用概念型号，不代表华丽电器真实量产产品或正式技术规格。</p>"
            product.status = ContentStatus.DRAFT
            product.sort_order = 1000 + index
            product.is_demo = True
            product.verification_status = VerificationStatus.PENDING
            product.homepage_badge = "演示数据"
            with (self.asset_root / "products" / self.product_assets[category_slug]).open("rb") as source:
                product.image = File(source, name=f"{model.lower()}.webp")
                product.full_clean()
                product.save()
            product.specifications.all().delete()
            product.highlights.all().delete()
            product.applications.all().delete()
            parameters = {item.name_zh: item for item in StandardParameter.objects.all()}
            ProductSpecification.objects.bulk_create([
                ProductSpecification(
                    product=product, name=spec_name, value=value,
                    standard_parameter=parameters.get(spec_name), show_on_card=True, sort_order=spec_index,
                )
                for spec_index, (spec_name, value) in enumerate(specs)
            ])
            ProductHighlight.objects.bulk_create([
                ProductHighlight(product=product, title="演示结构", description="仅用于测试特点模块。", sort_order=0),
                ProductHighlight(product=product, title="可替换素材", description="后续可替换真实产品图片和规格。", sort_order=1),
            ])
            ProductApplication.objects.bulk_create([
                ProductApplication(product=product, name="功能测试", description="用于本地网站功能验收。", sort_order=0),
            ])
            product.status = ContentStatus.PUBLISHED
            product.first_published_at = product.first_published_at or timezone.now()
            product.validate_for_publish()
            product.save()
            product.rebuild_search_text()
            if representative_models[category_slug] == model:
                self.ensure_demo_document(product, category_slug)

    def ensure_demo_document(self, product, category_slug):
        name = f"{product.category.name}测试资料册"
        document = ProductDocument.objects.filter(product=product, name=name).first()
        if document and not self.overwrite:
            return
        if self.check_only:
            if not document:
                self.changes.append(f"缺少测试资料 {product.model}")
            return
        old_file = document.file if document and document.file else None
        document = document or ProductDocument(product=product, name=name)
        document.document_type = ProductDocument.DocumentType.CATALOG
        document.language = ProductDocument.Language.ZH
        document.is_demo = True
        document.disclaimer = "测试资料，非真实产品规格，不可用于采购、认证或技术决策。"
        document.file = ContentFile(self.build_demo_pdf(product.category.name, category_slug), name=f"{category_slug}-demo-catalog.pdf")
        document.full_clean()
        document.save()
        if old_file and old_file.name != document.file.name:
            delete_field_file(old_file)

    def build_demo_pdf(self, series_name, category_slug):
        font_path = next((path for path in (
            Path("C:/Windows/Fonts/msyh.ttc"), Path("C:/Windows/Fonts/simhei.ttf"),
        ) if path.exists()), None)
        if font_path:
            font_name = "HualiDemoCJK"
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        else:
            font_name = "STSong-Light"
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
        styles = getSampleStyleSheet()
        title = ParagraphStyle("DemoTitle", parent=styles["Title"], fontName=font_name, textColor=colors.HexColor("#C41E24"), alignment=TA_CENTER)
        heading = ParagraphStyle("DemoHeading", parent=styles["Heading2"], fontName=font_name, textColor=colors.HexColor("#222222"))
        body = ParagraphStyle("DemoBody", parent=styles["BodyText"], fontName=font_name, leading=18)
        warning = ParagraphStyle("DemoWarning", parent=body, textColor=colors.HexColor("#C41E24"), alignment=TA_CENTER)
        story = [
            Paragraph("华丽电器测试资料册", title), Spacer(1, 8 * mm),
            Paragraph(series_name, heading), Spacer(1, 6 * mm),
            Paragraph("测试资料 / DEMO DOCUMENT", warning), Spacer(1, 8 * mm),
            Paragraph("本文件用于验证网站资料申请、邮件、签名链接与下载流程，不代表真实产品规格、认证、价格或交付承诺。", body),
            Spacer(1, 5 * mm),
            Paragraph("This bilingual file is for testing document requests, email delivery, signed links and downloads. It does not represent real specifications, certifications, prices or delivery commitments.", body),
            PageBreak(), Paragraph("概念系列说明", heading),
            Paragraph("该系列属于第三阶段网站测试内容。页面中的产品名称、型号和参数均为演示数据，后续可从后台替换为真实资料。", body),
            Spacer(1, 5 * mm),
            Paragraph("This concept series is demonstration content for phase three. Product names, models and parameters can be replaced with verified company data in the administration site.", body),
            Spacer(1, 8 * mm),
            Table([["系列键", category_slug], ["内容状态", "AI/种子演示数据"], ["可用于采购", "否"]], colWidths=[45 * mm, 105 * mm], style=[
                ("FONTNAME", (0, 0), (-1, -1), font_name), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F3F5")), ("PADDING", (0, 0), (-1, -1), 7),
            ]),
            PageBreak(), Paragraph("示例参数", heading),
            Paragraph("示例参数仅用于页面表格、搜索和产品对比测试。正式网站必须以公司审核后的产品资料为准。", body),
            Spacer(1, 5 * mm),
            Paragraph("Sample parameters are only used to test tables, search and comparison. A production site must use company-approved product documents.", body),
            Spacer(1, 8 * mm),
            Table([["参数", "演示值"], ["动力系统", "概念配置"], ["使用场景", "功能测试"], ["资料版本", "DEMO-1"]], colWidths=[55 * mm, 95 * mm], style=[
                ("FONTNAME", (0, 0), (-1, -1), font_name), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]),
            PageBreak(), Paragraph("替换说明", heading),
            Paragraph("后续获得真实资料后，管理员可在产品后台新增正式文件版本。页面入口、权限流程和下载统计不需要重新开发。", body),
            Spacer(1, 5 * mm),
            Paragraph("When verified documents become available, administrators can upload formal versions without rebuilding page entry points, access control or download tracking.", body),
            Spacer(1, 15 * mm), Paragraph("再次提醒：测试资料，非真实产品规格。", warning),
        ]
        doc.build(story)
        return buffer.getvalue()

    def seed_demo_news(self):
        category = self.upsert(NewsCategory, {"slug": "demo-knowledge"}, {
            "name": "制造知识（测试）", "description": "通用制造知识和测试站更新。",
            "sort_order": 100, "is_active": True,
        }, "演示新闻分类")
        image_names = [path.name for path in (self.asset_root / "news").glob("*.webp")]
        for index, (slug, title, summary) in enumerate(DEMO_ARTICLES):
            article = Article.objects.filter(slug=slug).first()
            if self.check_only:
                if not article:
                    self.changes.append(f"缺少演示新闻 {slug}")
                continue
            if article and not self.overwrite:
                continue
            article = article or Article(slug=slug)
            article.category = category
            article.title = title
            article.summary = summary
            article.body = f"<p>{summary}</p><p>本文为网站功能测试内容，不代表公司新闻、合作承诺或经营数据。</p>"
            article.source = "华丽电器测试站"
            article.published_at = timezone.now() - timedelta(days=index)
            article.first_published_at = article.first_published_at or article.published_at
            article.status = ContentStatus.PUBLISHED
            article.is_demo = True
            article.verification_status = VerificationStatus.PENDING
            article.cover_alt = f"{title}测试封面"
            with (self.asset_root / "news" / image_names[index % len(image_names)]).open("rb") as source:
                article.cover = File(source, name=f"{slug}.webp")
                article.full_clean()
                article.save()

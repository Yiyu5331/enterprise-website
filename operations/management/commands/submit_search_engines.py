import json
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from operations.models import AuditLog, SystemAlert
from operations.seo import absolute_url, indexable_paths


class Command(BaseCommand):
    help = "向百度站长和 Bing IndexNow 提交公开 URL。Google 通过 sitemap.xml 收录。"

    def handle(self, *args, **options):
        urls = [absolute_url(path) for path in indexable_paths()]
        submitted = []
        try:
            if settings.BAIDU_SITE and settings.BAIDU_TOKEN:
                endpoint = "https://data.zz.baidu.com/urls?" + urllib.parse.urlencode({"site": settings.BAIDU_SITE, "token": settings.BAIDU_TOKEN})
                request = urllib.request.Request(endpoint, data="\n".join(urls).encode("utf-8"), headers={"Content-Type": "text/plain"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    response.read()
                submitted.append("Baidu")
            if settings.INDEXNOW_KEY:
                payload = json.dumps({"host": settings.SITE_DOMAIN, "key": settings.INDEXNOW_KEY, "urlList": urls}).encode("utf-8")
                request = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    response.read()
                submitted.append("IndexNow")
        except Exception as exc:
            SystemAlert.objects.create(source="seo_submit", message=f"搜索引擎 URL 提交失败：{str(exc)[:400]}")
            raise
        AuditLog.objects.create(action="search_engine_submitted", target_type="site", summary=f"提交 {len(urls)} 个 URL：{', '.join(submitted) or '未配置平台'}")
        self.stdout.write(self.style.SUCCESS(f"URL 清单共 {len(urls)} 条；已提交：{', '.join(submitted) or '未配置平台'}。"))

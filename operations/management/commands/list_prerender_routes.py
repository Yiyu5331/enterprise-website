import json

from django.core.management.base import BaseCommand

from operations.seo import indexable_paths


class Command(BaseCommand):
    help = "以 JSON 输出所有需要预渲染的公开路由。"

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(indexable_paths(), ensure_ascii=False))

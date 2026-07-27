import json
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from operations.models import PrerenderTask, SystemAlert, TaskRun
from operations.seo import indexable_paths


class Command(BaseCommand):
    help = "调用 Playwright 执行增量或全量预渲染。"

    def add_arguments(self, parser):
        parser.add_argument("--full", action="store_true")

    def handle(self, *args, **options):
        run = TaskRun.objects.create(kind="prerender_full" if options["full"] else "prerender_incremental", status="running")
        queryset = PrerenderTask.objects.filter(pending=True)
        paths = indexable_paths() if options["full"] else list(queryset.values_list("path", flat=True))
        if not paths:
            run.status = "success"
            run.summary = "没有待处理的预渲染任务。"
            run.finished_at = timezone.now()
            run.save(update_fields=("status", "summary", "finished_at"))
            self.stdout.write(run.summary)
            return
        env = os.environ.copy()
        env["PRERENDER_PATHS"] = json.dumps(paths, ensure_ascii=False)
        env["PRERENDER_SITEMAP_PATHS"] = json.dumps(indexable_paths(), ensure_ascii=False)
        env["PRERENDER_ROOT"] = str(settings.PRERENDER_ROOT)
        env["SITE_URL"] = settings.SITE_URL
        env["VITE_SITE_URL"] = settings.SITE_URL
        preview = None
        try:
            npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
            if not npm:
                raise RuntimeError("未找到 npm，请安装 Node.js 22。")
            subprocess.run([npm, "run", "build"], cwd=Path(settings.BASE_DIR) / "frontend", env=env, check=True)
            preview = subprocess.Popen(
                [npm, "run", "preview", "--", "--host", "127.0.0.1", "--port", "4173"],
                cwd=Path(settings.BASE_DIR) / "frontend",
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(30):
                try:
                    urllib.request.urlopen("http://127.0.0.1:4173/", timeout=1)
                    break
                except OSError:
                    time.sleep(0.5)
            else:
                raise RuntimeError("Vite 预览服务启动超时。")
            subprocess.run([npm, "run", "prerender"], cwd=Path(settings.BASE_DIR) / "frontend", env=env, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            run.status = "failed"
            run.summary = str(exc)[:500]
            SystemAlert.objects.create(source="prerender", message=f"预渲染失败：{run.summary}")
            raise CommandError(run.summary) from exc
        else:
            PrerenderTask.objects.filter(path__in=paths).update(pending=False)
            SystemAlert.objects.filter(source="prerender", resolved_at__isnull=True).update(resolved_at=timezone.now())
            run.status = "success"
            run.summary = f"完成 {len(paths)} 个页面预渲染。"
        finally:
            if preview:
                preview.terminate()
                try:
                    preview.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    preview.kill()
            run.finished_at = timezone.now()
            run.save(update_fields=("status", "summary", "finished_at"))
        self.stdout.write(self.style.SUCCESS(run.summary))

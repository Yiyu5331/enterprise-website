from .models import PrerenderTask


def queue_prerender(path, reason):
    task, _ = PrerenderTask.objects.get_or_create(path=path, defaults={"reason": reason})
    task.reason = reason
    task.pending = True
    task.save(update_fields=("reason", "pending", "updated_at"))

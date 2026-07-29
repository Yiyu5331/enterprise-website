from datetime import datetime, time, timedelta

from django.shortcuts import redirect
from django.utils import timezone


class DefaultDateRangeAdminMixin:
    """让 SimpleUI 使用原生日期范围控件，并默认筛选最近 30 日。"""

    date_range_field = ""
    date_range_days = 30

    def changelist_view(self, request, extra_context=None):
        start_parameter = f"{self.date_range_field}__gte"
        end_parameter = f"{self.date_range_field}__lte"
        if self.date_range_field and start_parameter not in request.GET and end_parameter not in request.GET:
            today = timezone.localdate()
            query = request.GET.copy()
            start_date = today - timedelta(days=self.date_range_days - 1)
            start_at = timezone.make_aware(datetime.combine(start_date, time.min))
            end_at = timezone.make_aware(datetime.combine(today, time.max.replace(microsecond=0)))
            query[start_parameter] = start_at.isoformat()
            # 日期框显示日期，但查询截止到当天 23:59:59，避免漏掉当天提交的记录。
            query[end_parameter] = end_at.isoformat()
            return redirect(f"{request.path}?{query.urlencode()}")
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        css = {"all": ("admin/date_range_split.css",)}
        js = ("admin/date_range_split.js",)

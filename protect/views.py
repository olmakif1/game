from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from news.models import Announcement


class ModeratorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "protect/dashboard.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total": Announcement.objects.count(),
                "pinned": Announcement.objects.filter(is_pinned=True).count(),
                "recent": Announcement.objects.order_by("-published_at")[:5],
            }
        )
        return context

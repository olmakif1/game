from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView

from .forms import AnnouncementForm
from .models import Announcement


class AnnouncementBoardView(ListView):
    template_name = "news/announcement_board.html"
    context_object_name = "announcements"

    def get_queryset(self):  # type: ignore[override]
        queryset = Announcement.objects.all().pinned_first()
        search_term = self.request.GET.get("q")
        category = self.request.GET.get("category")
        return queryset.search(search_term).for_category(category)

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        announcements = context["announcements"]
        form = kwargs.get("form") or AnnouncementForm()
        pinned_announcements = announcements.filter(is_pinned=True)
        regular_announcements = announcements.filter(is_pinned=False)
        context.update(
            {
                "categories": Announcement.CATEGORY_CHOICES,
                "form": form,
                "metrics": {
                    "total": announcements.count(),
                    "pinned": pinned_announcements.count(),
                },
                "pinned_announcements": pinned_announcements,
                "regular_announcements": regular_announcements,
                "search_term": self.request.GET.get("q", ""),
                "selected_category": self.request.GET.get("category", ""),
            }
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement: Announcement = form.save(commit=False)
            if not announcement.published_at:
                announcement.published_at = timezone.now()
            announcement.save()
            messages.success(request, "Announcement published to the board.")
            return redirect("news:board")

        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


def board(request: HttpRequest) -> HttpResponse:
    view = AnnouncementBoardView.as_view()
    return view(request)

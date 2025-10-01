from __future__ import annotations

import json

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from .forms import AnnouncementForm
from .models import Announcement


class AnnouncementBoardView(ListView):
    template_name = "news/announcement_board.html"
    context_object_name = "announcements"

    def get_queryset(self):  # type: ignore[override]
        queryset = Announcement.objects.all()
        search_term = self.request.GET.get("q")
        category = self.request.GET.get("category")
        queryset = queryset.search(search_term).for_category(category).pinned_first()
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        announcements = context['announcements']
        context.update(
            {
                "categories": Announcement.CATEGORY_CHOICES,
                "form": AnnouncementForm(),
                "metrics": {
                    "total": announcements.count(),
                    "pinned": announcements.filter(is_pinned=True).count(),
                },
                "initial_payload": [item.to_dict() for item in announcements],
            }
        )
        return context


class AnnouncementFeedView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        queryset = Announcement.objects.all().pinned_first()
        search_term = request.GET.get("q")
        category = request.GET.get("category")
        queryset = queryset.search(search_term).for_category(category)
        return JsonResponse({"announcements": [item.to_dict() for item in queryset]})


class AnnouncementCreateView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        if request.content_type == "application/json":
            payload = json.loads(request.body or "{}")
            form = AnnouncementForm(payload)
        else:
            form = AnnouncementForm(request.POST)

        if form.is_valid():
            announcement: Announcement = form.save(commit=False)
            announcement.published_at = timezone.now()
            announcement.save()
            messages.success(request, "Announcement published to the board.")
            return JsonResponse({"success": True, "announcement": announcement.to_dict()})

        return JsonResponse({"success": False, "errors": form.errors}, status=400)


def board(request: HttpRequest) -> HttpResponse:
    view = AnnouncementBoardView.as_view()
    return view(request)

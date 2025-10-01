from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_pinned", "published_at")
    search_fields = ("title", "summary", "content", "tags")
    list_filter = ("category", "is_pinned")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-is_pinned", "-published_at")

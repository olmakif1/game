from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class AnnouncementQuerySet(models.QuerySet):
    def pinned_first(self) -> "AnnouncementQuerySet":
        return self.order_by(models.F("is_pinned").desc(), "-published_at")

    def search(self, term: str | None) -> "AnnouncementQuerySet":
        if not term:
            return self
        return self.filter(
            models.Q(title__icontains=term)
            | models.Q(summary__icontains=term)
            | models.Q(content__icontains=term)
            | models.Q(tags__icontains=term)
        )

    def for_category(self, category: str | None) -> "AnnouncementQuerySet":
        if not category:
            return self
        return self.filter(category=category)


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General"),
        ("events", "Events"),
        ("releases", "Releases"),
        ("creative", "Creative Projects"),
        ("behind_the_scenes", "Behind the Scenes"),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=180)
    summary = models.CharField(max_length=280)
    content = models.TextField()
    author_display = models.CharField(max_length=80, default="Starwave Mod Team")
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="general")
    tags = models.JSONField(default=list, blank=True)
    is_pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        ordering = ("-is_pinned", "-published_at")

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.title) or slugify(self.summary[:40]) or "announcement"
            slug = base_slug
            index = 1
            while Announcement.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                index += 1
                slug = f"{base_slug}-{index}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def category_label(self) -> str:
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category.title())

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.pk,
            "slug": self.slug,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "author": self.author_display,
            "category": self.category,
            "category_label": self.category_label,
            "tags": self.tags,
            "is_pinned": self.is_pinned,
            "published_at": self.published_at.isoformat(),
        }

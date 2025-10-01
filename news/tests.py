from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import AnnouncementForm
from .models import Announcement


class AnnouncementModelTests(TestCase):
    def test_slug_is_generated_and_unique(self) -> None:
        Announcement.objects.all().delete()
        first = Announcement.objects.create(
            title="Starwave Transmission",
            summary="Initial broadcast",
            content="All systems nominal.",
        )
        second = Announcement.objects.create(
            title="Starwave Transmission",
            summary="Second broadcast",
            content="Signal boost engaged.",
        )

        self.assertTrue(first.slug.startswith("starwave-transmission"))
        self.assertTrue(second.slug.startswith("starwave-transmission"))
        self.assertNotEqual(first.slug, second.slug)


class AnnouncementBoardViewTests(TestCase):
    def setUp(self) -> None:
        Announcement.objects.all().delete()
        self.pinned = Announcement.objects.create(
            title="Pinned",
            summary="Pinned summary",
            content="Pinned content",
            is_pinned=True,
            category="events",
        )
        self.regular = Announcement.objects.create(
            title="Regular",
            summary="Regular summary",
            content="Regular content",
            category="general",
        )

    def test_board_context_splits_pinned_and_regular(self) -> None:
        response = self.client.get(reverse("news:board"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.pinned, response.context["pinned_announcements"])
        self.assertIn(self.regular, response.context["regular_announcements"])
        self.assertEqual(response.context["metrics"], {"total": 2, "pinned": 1})

    def test_board_search_filters_results(self) -> None:
        response = self.client.get(reverse("news:board"), {"q": "Pinned"})

        announcements = list(response.context["announcements"])
        self.assertEqual(announcements, [self.pinned])

    def test_board_category_filter(self) -> None:
        response = self.client.get(reverse("news:board"), {"category": "events"})

        announcements = list(response.context["announcements"])
        self.assertEqual(announcements, [self.pinned])

    def test_post_requires_authentication(self) -> None:
        response = self.client.post(
            reverse("news:board"),
            {
                "title": "New",
                "summary": "Sum",
                "content": "Body",
                "category": "general",
                "tags": "alpha, beta",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_authenticated_post_creates_announcement(self) -> None:
        user = get_user_model().objects.create_user("crew@example.com", "crew@example.com", "pw12345!")
        self.client.force_login(user)

        response = self.client.post(
            reverse("news:board"),
            {
                "title": "Mission Update",
                "summary": "Launch confirmed",
                "content": "Coordinates locked in.",
                "category": "general",
                "tags": "launch, update",
                "author_display": "Flight Director",
                "is_pinned": "on",
            },
        )

        self.assertRedirects(response, reverse("news:board"))
        announcement = Announcement.objects.order_by("-published_at").first()
        assert announcement is not None
        self.assertEqual(announcement.title, "Mission Update")
        self.assertEqual(announcement.tags, ["launch", "update"])
        self.assertTrue(announcement.is_pinned)

    def test_form_parses_tags_string_into_list(self) -> None:
        form = AnnouncementForm(
            data={
                "title": "Tag Test",
                "summary": "Test summary",
                "content": "Test content",
                "category": "general",
                "tags": "one, two , three",
                "author_display": "Ops",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["tags"], ["one", "two", "three"])

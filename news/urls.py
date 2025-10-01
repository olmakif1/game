from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("", views.board, name="board"),
    path("api/announcements/", views.AnnouncementFeedView.as_view(), name="announcement-feed"),
    path("api/announcements/create/", views.AnnouncementCreateView.as_view(), name="announcement-create"),
]

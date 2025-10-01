from django.urls import path

from .views import ModeratorDashboardView

app_name = "protect"

urlpatterns = [
    path("", ModeratorDashboardView.as_view(), name="dashboard"),
]

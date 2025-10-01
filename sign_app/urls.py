from django.urls import path

from .views import ModeratorApplicationView

app_name = "sign"

urlpatterns = [
    path("", ModeratorApplicationView.as_view(), name="apply"),
]

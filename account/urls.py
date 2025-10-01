from django.urls import path

from .views import FanSignupView

app_name = "account"

urlpatterns = [
    path("signup/", FanSignupView.as_view(), name="signup"),
]

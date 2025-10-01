from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("account.urls")),
    path("protect/", include("protect.urls")),
    path("sign/", include("sign_app.urls")),
    path("", include("news.urls")),
]

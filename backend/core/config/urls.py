from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def index(request):
    return JsonResponse({"status": "ok", "service": "django_next_starter backend"})


urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("_allauth/", include("allauth.headless.urls")),
    path("api/", include("core.apps.api.urls")),
]

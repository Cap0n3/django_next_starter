from django.urls import path

from .views import MeView, PingView

urlpatterns = [
    path("ping/", PingView.as_view(), name="api-ping"),
    path("me/", MeView.as_view(), name="api-me"),
]

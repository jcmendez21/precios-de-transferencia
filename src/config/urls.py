"""URL configuration del proyecto."""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def home(request):
    return HttpResponse("PT-Docs — Sprint 0 activo", content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
]

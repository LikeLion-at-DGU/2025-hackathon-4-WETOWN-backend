from django.urls import path, include
from rest_framework import routers
from .views import PostViewSet

from django.conf.urls.static import static
from django.conf import settings

app_name = "posts"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("posts", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(default_router.urls)), 
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

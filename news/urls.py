from django.urls import path, include
from rest_framework import routers
from .views import NewsViewSet

app_name = "news"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("news", NewsViewSet, basename="news")

urlpatterns = [
  path("", include(default_router.urls)),  
]
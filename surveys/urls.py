from django.urls import path, include
from rest_framework import routers
from .views import SurveyViewSet

app_name = "surveys"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("surveys", SurveyViewSet, basename="surveys")

urlpatterns = [
  path("", include(default_router.urls)),
]
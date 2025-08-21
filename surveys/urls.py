from django.urls import path, include
from rest_framework import routers
from .views import SurveyViewSet, VerifySurveyCodeView

app_name = "surveys"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("", SurveyViewSet, basename="surveys")

urlpatterns = [
  path("verify-code", VerifySurveyCodeView.as_view(), name="surveys-verify-code"),
  path("", include(default_router.urls)),
]
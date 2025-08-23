# chatbot/urls.py
from django.urls import path
from .views import simple_chat

urlpatterns = [
    path("", simple_chat),  # /chat/ 로 POST 요청 받음
]

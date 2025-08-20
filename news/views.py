from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import News
from .serializers import NewsSerializer, NewsListSerializer, NewsImageSerializer

class NewsViewSet(viewsets.ModelViewSet):
  queryset = News.objects.all().order_by("-created_at")

  def get_serializer_class(self):
    if self.action in ("list", "latest"):
      return NewsListSerializer
    return NewsSerializer
  
  def get_serializer_context(self):
    ctx = super().get_serializer_context()
    ctx["request"] = self.request
    return ctx
  
  def get_queryset(self):
    return super().get_queryset()
  
  @action(methods=["GET"], detail=False, url_path="latest")
  def latest(self, request):
    obj = self.get_queryset().first()
    if not obj:
      return Response({})
    ser = self.get_serializer(obj)
    return Response(ser.data)

# 최신 3개의 이미지용 데이터만 반환
  @action(methods=["GET"], detail=False, url_path="latest-images")
  def latest_images(self, request):
      qs = self.get_queryset()[:3]
      ser = self.get_serializer(qs, many=True)
      return Response(ser.data)
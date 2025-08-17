from django.shortcuts import render, get_object_or_404

from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, mixins 
from .models import Post, Comment
from .serializers import PostSerializer,  PostListSerializer, CommentSerializer

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at") #최신순 정렬
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        post = serializer.instance

        return Response(serializer.data)
    
    def _parse_date(self, s : str) -> datetime:
        try:
            #yyyy-mm-dd
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            raise ValidationError({"detail":"날짜 형식은 YYYY-MM-DD 이어야 합니다."})
        
    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params

        #카테고리 필터
        category = p.get("category")
        if category:
            qs = qs.filter(category=category)

        #동 필터 (사용자가 글 작성시 선택한 동 카테고리로 검색)
        dong = p.get("dong")
        if dong:
            qs = qs.filter(dong=dong)

        #키워드 필터
        q = p.get("q")
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) 
            )

        #기간 필터
        start = p.get("start")
        end = p.get("end")

        if start or end:
            start_naive = self._parse_date(start) if start else datetime(1970, 1, 1)
            end_naive = self._parse_date(end) if end else None

            if end_naive:
                end_naive = end_naive + timedelta(days=1)
                
            tz = timezone.get_current_timezone()
            start_dt = timezone.make_aware(start_naive, tz)
            end_dt = timezone.make_aware(end_naive, tz) if end_naive else (timezone.now() + timedelta(days=365*50))

            qs = qs.filter(created_at__gte=start_dt, created_at__lt=end_dt)

        return qs
    
class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset
    
    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer




from django.shortcuts import render, get_object_or_404

from django.db.models import Q,F
from django.utils import timezone
from datetime import datetime, timedelta

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, mixins 
from .models import Post, Comment, Like
from .serializers import PostSerializer,  PostListSerializer, CommentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at") #최신순 정렬
    
    def get_serializer_class(self):
        if self.action in ("list", "top_liked"):
            return PostListSerializer
        return PostSerializer

    #serializer가 현재 요청한 사용자 알 수 있도록 request->context 포함시킴
    def get_serializer_context(self):
        ctx = super().get_serializer_context()  
        ctx["request"] = self.request           
        return ctx

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

    #좋아요 top3
    @action(methods=["GET"], detail=False, url_path="top-liked")
    def top_liked(self, request):
        top3 = self.get_queryset().order_by("-likes_count", "-created_at")[:3]  #좋아요 탑3 반환
        serializer = self.get_serializer(top3, many=True)
        return Response(serializer.data)

    #세션키 확보
    def _ensure_session(self, request):
        if not request.session.session_key:
            request.session.save()
        return request.session.session_key

    #좋아요 생성(이미 눌러져있으면 취소, 안눌렀으면 생성)
    @action(methods=["POST", "DELETE"], detail=True, url_path="like")
    def like(self, request, pk=None):
        session_key = self._ensure_session(request)
        post = self.get_object()

        if request.method == "DELETE":
            deleted, _ = Like.objects.filter(post=post, session_key=session_key).delete()
            if not deleted:
                return Response({"detail": "본인이 누른 좋아요가 없습니다."}, status=404)
            post.likes_count = max(0, post.likes_count - 1)
            post.save(update_fields=["likes_count"])
            return Response({"post_id": post.id, "likes_count": post.likes_count, "is_liked": False}, status=200)

        like_qs = Like.objects.filter(post=post, session_key=session_key)
        if like_qs.exists():
            like_qs.delete()
            post.likes_count = max(0, post.likes_count -1)
            post.save(update_fields=["likes_count"])
            return Response({"post_id":post.id, "likes_count": post.likes_count, "is_liked": False}, status=200)
        
        else:
            Like.objects.create(post=post, session_key=session_key)
            post.likes_count += 1
            post.save(update_fields=["likes_count"])
            return Response({"post_id": post.id, "likes_count": post.likes_count, "is_liked": True}, status=201)

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




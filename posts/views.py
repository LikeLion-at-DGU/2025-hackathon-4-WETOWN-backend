from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, mixins 
from .models import Post
from .serializers import PostSerializer

from rest_framework.response import Response

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at") #최신순 정렬
    serializer_class = PostSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        post = serializer.instance

        return Response(serializer.data)
    
    

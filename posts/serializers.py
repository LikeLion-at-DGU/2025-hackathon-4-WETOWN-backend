from rest_framework import serializers
from .models import *

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post', 'id', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)
    comments = serializers.SerializerMethodField(read_only=True)
    
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many=True)
        return serializer.data

    def get_is_liked(self, instance):
        request = self.context.get("request")
        if not request:
            return False  
        session_key = request.session.session_key
        if not session_key: #세션이 없다면
            return False
        return Like.objects.filter(post=instance, session_key=session_key).exists()
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "comments",
            "likes_count",
            "is_liked"
        ]

class PostListSerializer(serializers.ModelSerializer):
    comments_cnt = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)

    def get_comments_cnt(self, instance):
        return instance.comments.count()
    
    def get_is_liked(self, instance):
        request = self.context.get("request")
        if not request:
            return False
        session_key = request.session.session_key
        if not session_key:
            return False
        return Like.objects.filter(post=instance, session_key=session_key).exists()
    class Meta:
        model = Post
        fields = [
            "id",
            "writer",
            "title",
            "created_at",
            "updated_at",
            "image",
            "comments_cnt",
            "likes_count",
            "is_liked",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id","created_at","updated_at","comments_cnt"]


from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        # fields = ('writer', 'title', 'content', 'created_at', 'updated_at', 'image', 'category', 'dong', 'location_detail')
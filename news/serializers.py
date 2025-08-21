from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
  class Meta:
    model = News
    fields = "__all__"
    read_only_fields = [
      "id",
      "created_at",
    ]


class NewsListSerializer(serializers.ModelSerializer):

  class Meta:
    model = News
    fields = [
      "id",
      "title",
      "short_title",
      "image_url",
      "created_at",
      "published_at",
      "source_name",
      "source_url",
      "author",
    ]

    read_only_fields = [
      "id",
      "created_at",
    ]

class NewsImageSerializer(serializers.ModelSerializer): # 홈 화면 뉴스 리스트를 위한 serializer
    class Meta:
        model = News
        fields = ["id", "image_url"]
        read_only_fields = ["id"] 
from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
  image = serializers.ImageField(
    use_url=True,
    required=False,
    allow_null=True
  )

  class Meta:
    model = News
    fields = "__all__"
    read_only_fields = [
      "id",
      "created_at",
    ]


class NewsListSerializer(serializers.ModelSerializer):
  image = serializers.ImageField(
    use_url=True,
    required=False,
    allow_null=True
  )

  class Meta:
    model = News
    fields = [
      "id",
      "title",
      "image",
      "created_at",
    ]
    read_only_fields = [
      "id",
      "created_at",
    ]
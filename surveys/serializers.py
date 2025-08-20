from rest_framework import serializers
from .models import Survey, SurveyOption, SurveyVote

class SurveyVoteSerializer(serializers.ModelSerializer):
  class Meta:
    model = SurveyVote
    fields = "__all__"
    read_only_fields = [
      "survey",
      "id",
      "created_at",
    ]

class SurveyOptionSerializer(serializers.ModelSerializer):
  class Meta:
    model = SurveyOption
    fields = "__all__"
    read_only_fields = [
      "survey",
      "id",
    ]

class SurveySerializer(serializers.ModelSerializer):
  options = serializers.SerializerMethodField(read_only=True)
  is_voted = serializers.SerializerMethodField(read_only=True)
  my_vote_option = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Survey
    fields = "__all__"
    read_only_fields = [
      "id",
      "created_at",
      "options",
      "is_voted",
      "my_vote_option",
    ]

  def get_options(self, instance): # 옵션 목록 직렬화
    qs = instance.options.order_by("order_num", "id")
    serializers = SurveyOptionSerializer(qs, many=True)
    return serializers.data
  
  def get_is_voted(self, instance): # 현재 세션에서의 투표 여부
    request = self.context.get("request")
    if not request: # 컨텍스트 없으면 False 반환함.
      return False
    session_key = request.session.session_key
    if not session_key:
      return False
    return SurveyVote.objects.filter(survey=instance, session_key=session_key).exists()
  

  def get_my_vote_option(self, instance):
    request = self.context.get("request")
    if not request:
      return False
    session_key = request.session.session_key
    if not session_key:
      return None
    
    vote = (
      SurveyVote.objects.filter(survey=instance, session_key=session_key)
      .select_related("option")
      .first()
    )
    return vote.option_id if vote else None


class SurveyListSerializer(serializers.ModelSerializer):
  is_voted = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Survey
    fields = [
      "id",
      "title",
      "start_at",
      "end_at",
      "created_at",
      "is_voted",
    ]
    read_only_fields = [
      "id",
      "created_at",
      "is_voted",
    ]

  def get_is_voted(self, instance):
    request = self.context.get("request")
    if not request:
      return False
    session_key = request.session.session_key
    if not session_key:
      return False
    return SurveyVote.objects.filter(survey=instance, session_key=session_key).exists()

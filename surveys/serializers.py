from rest_framework import serializers
from django.utils import timezone
from .models import Survey, SurveyOption, SurveyVote, AuthCode

class SurveyVoteSerializer(serializers.ModelSerializer):
  class Meta:
    model = SurveyVote
    fields = "__all__"
    read_only_fields = ["survey", "id", "created_at"]

class SurveyOptionSerializer(serializers.ModelSerializer):
  class Meta:
    model = SurveyOption
    fields = "__all__"
    read_only_fields = ["survey", "id"]

class SurveySerializer(serializers.ModelSerializer):
  options = serializers.SerializerMethodField(read_only=True)
  is_voted = serializers.SerializerMethodField(read_only=True)
  my_vote_option = serializers.SerializerMethodField(read_only=True)

  # 추가 : 인증코드 발급 및 agency 이름 제공
  code = serializers.CharField(write_only=True, required=True)
  agency_name = serializers.CharField(source="agency.name", read_only=True)


  class Meta:
    model = Survey
    fields = "__all__"
    read_only_fields = [
      "id",
      "created_at",
      "options",
      "is_voted",
      "my_vote_option",
      "agency", # 클라이언트가 직접 넘기지 못하게 설정
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
  
  # 인증 코드 검증
  def validate(self, attrs):
    if self.instance is None:
        code = (attrs.pop("code", "") or "").strip()
        if not code:
            raise serializers.ValidationError({"code": "인증코드를 입력해 주세요."})
        try:
            obj = AuthCode.objects.select_related("agency").get(code=code, is_active=True)
            self.context["resolved_agency"] = obj.agency
        except AuthCode.DoesNotExist:
            raise serializers.ValidationError({"code": "유효하지 않은 인증코드입니다."})
    return attrs
  
  def create(self, validated_data):
    validated_data["agency"] = self.context["resolved_agency"]
    return super().create(validated_data)


class SurveyListSerializer(serializers.ModelSerializer):
  is_voted = serializers.SerializerMethodField(read_only=True)

  agency_name = serializers.CharField(source="agency.name", read_only=True)

  class Meta:
    model = Survey
    fields = [
      "id",
      "title",
      "start_at",
      "end_at",
      "created_at",
      "is_voted",
      "agency_name",
    ]
    read_only_fields = ["id", "created_at", "is_voted", "agency_name"]


  def get_is_voted(self, instance):
    request = self.context.get("request")
    if not request:
      return False
    session_key = request.session.session_key
    if not session_key:
      return False
    return SurveyVote.objects.filter(survey=instance, session_key=session_key).exists()

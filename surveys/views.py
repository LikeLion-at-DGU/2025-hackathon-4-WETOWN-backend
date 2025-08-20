from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.db.models import Q 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Survey, SurveyOption, SurveyVote
from .serializers import SurveySerializer, SurveyListSerializer, SurveyVoteSerializer, SurveyOptionSerializer


class SurveyViewSet(viewsets.ModelViewSet):
  queryset = Survey.objects.all().order_by("-created_at")

  def get_serializer_class(self):
    if self.action == "list":
      return SurveyListSerializer
    return SurveySerializer
  
  def get_serializer_context(self):
    ctx = super().get_serializer_context()
    ctx["request"] = self.request
    return ctx
  
  def get_queryset(self):
    qs = super().get_queryset()
    p = self.request.query_params
    status_param = p.get("status")
    now = timezone.now()
    if status_param == "active":
      qs = qs.filter(end_at__gt=now).filter(Q(start_at__isnull=True) | Q(start_at__lte=now))
    elif status_param == "expired":
      qs = qs.filter(end_ata__lte=now)
    return qs
  
  def _ensure_session(self, request):
    if not request.session.session_key:
      request.session.save()
    return request.session.session_key
  
  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True) 
    survey = serializer.save()

    options = request.data.get("options")
    if isinstance(options, list):
      bulk = []
      order = 0
      for item in options:
        if isinstance(item, dict):
          label = item.get("label", "")
          order_num = item.get("order_num", order)
        else:
          label = str(item)
          order_num = order
        bulk.append(SurveyOption(survey=survey, label=label, order_num=order_num))
        order+=1

      if bulk:
        SurveyOption.objects.bulk_create(bulk)
      
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  @action(methods=["POST"], detail=True, url_path="vote")
  def vote(self, request, pk=None):
    survey = self.get_object()
    now = timezone.now()
    if not (survey.start_at is None or survey.start_at <= now):
      return Response({"detail": "아직 시작되지 않은 설문입니다."}, status=400)
    if not (now < survey.end_at):
      return Response({"detail": "설문이 종료되었습니다."}, status=400)
    
    session_key = self._ensure_session(request)
    if SurveyVote.objects.filter(survey=survey, session_key=session_key).exists():
      return Response({"detail": "이미 투표하셨습니다."}, status=400)
    
    option_id = request.data.get("option_id")
    if not option_id:
      return Response({"detail": "option_id가 필요합니다."}, status=400)
    
    try:
      option = SurveyOption.objects.get(id=option_id, survey=survey)
    except SurveyOption.DoesNotExist:
      return Response({"detail": "유효하지 않은 옵션입니다."}, status=400)
    
    opinion_text = request.data.get("opinion_text", "")
    SurveyVote.objects.create(survey=survey, option=option, session_key=session_key, opinion_text=opinion_text)

    return Response({
      "survey_id": survey.id,
      "option_id": option.id,
      "is_voted": True
    }, status=201)

  @action(methods=["GET"], detail=True, url_path="results")
  def results(self, request, pk=None):
    survey = self.get_object()
    options = survey.options.order_by("order_num", "id")
    counts = []
    total = 0
    for opt in options:
      c = opt.votes.count()
      counts.append({"option_id": opt.id, "label": opt.label, "count": c})
      total += c
    
    for row in counts:
      row["percent"] = 0.0 if total == 0 else round(row["count"] * 100.0 / total, 1)
    
    return Response({"survey_id": survey.id, "total_votes": total, "options": counts})

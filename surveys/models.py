from django.db import models
from django.utils import timezone

# Create your models here.

# 인증 기관 추가 모델
class Agency(models.Model):
    name = models.CharField(max_length=100, unique = True)
    def __str__(self): return self.name

class AuthCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name='codes')
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"{self.code} -> {self.agency.name}"


# 기존 코드
class Survey(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField()
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name='surveys')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["end_at"])]

    def __str__(self):
        return f"[Survey {self.id}] {self.title}"


class SurveyOption(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=50)
    order_num = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order_num", "id"]
        indexes = [models.Index(fields=["survey", "order_num"])]

    def __str__(self):
        return f"surveyOption(survey={self.survey_id}, label={self.label})"


class SurveyVote(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(SurveyOption, on_delete=models.CASCADE, related_name="votes")
    session_key = models.CharField(max_length=40, db_index=True)
    opinion_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["survey", "session_key"],
                name="uniq_vote_per_session_per_survey",
            )
        ]

    def __str__(self):
        return f"SurveyVote(survey={self.survey_id}, option={self.option_id}, session={self.session_key})"

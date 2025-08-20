from django.db import models

def news_image_upload_path(instance,filename):
  return f"news/{instance.pk}/{filename}"

class News(models.Model): # 뉴스 모델 임시 설계 (차후 ai 도입 시 변경)
  title = models.CharField(max_length=150, db_index=True)
  body = models.TextField(blank=True)
  image = models.ImageField(upload_to=news_image_upload_path, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]
    indexes = [models.Index(fields=["-created_at"])]

  def __str__(self):
    return f"[News {self.id}] (self.title)"
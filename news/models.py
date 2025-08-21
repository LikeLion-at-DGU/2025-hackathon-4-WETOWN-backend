from django.db import models
from django.db.models import Index

def news_image_upload_path(instance, filename):
    return f"news/{getattr(instance, 'pk', 'tmp')}/{filename}"

class News(models.Model): 
  title = models.CharField(max_length=150, db_index=True)
  short_title = models.CharField(max_length=30, blank=True)
  summary = models.TextField(blank=True)
  image_url = models.URLField(max_length=500, blank=True, null=True)
  
  source_url = models.URLField(max_length=500, blank=True, null=True, unique=True, db_index=True)
  source_name = models.CharField(max_length=100, blank=True, default="")
  author = models.CharField(max_length=100, blank=True, default="")
  published_at = models.DateTimeField(null=True, blank=True)
  
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]
    indexes = [Index(fields=["-created_at"])]

  def __str__(self):
    return f"[News {self.id}] {self.title}"
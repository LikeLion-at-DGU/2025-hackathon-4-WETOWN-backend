from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
def image_upload_path(instance, filename):
    return f'{instance.pk}/{filename}'

class Post(models.Model):
    writer = models.CharField(max_length=50)
    title = models.CharField(max_length=120)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)

    category = models.CharField(max_length=50, blank=True)  #아래 세개는 문자열로 우선 등록
    dong = models.CharField(max_length=50, blank=True)
    location_detail = models.CharField(max_length=200, blank=True)

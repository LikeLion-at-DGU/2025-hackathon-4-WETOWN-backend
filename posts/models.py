from django.db import models
from django.db.models import F
# Create your models here.

# Create your models here.
def image_upload_path(instance, filename):
    return f'{instance.pk}/{filename}'

class Post(models.Model):
    writer = models.CharField(max_length=50)
    title = models.CharField(max_length=120, db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)

    category = models.CharField(max_length=50, blank=True, db_index=True)  
    dong = models.CharField(max_length=50, blank=True, db_index=True)
    location_detail = models.CharField(max_length=200, blank=True)

    likes_count = models.PositiveIntegerField(default=0, db_index=True)
    
    def __str__(self):
        return f'[{self.id}] {self.title}'
    
    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["category", "dong"]),
            models.Index(fields=["-likes_count", "-created_at"]),
        ]
    
class Comment(models.Model):
    id = models.AutoField(primary_key = True)
    post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE, related_name="comments")
    writer = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    session_key = models.CharField(max_length=40, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "session_key"], name="uniq_like_per_session_per_post")
        ]

    def __str__(self):
        return f"Like(post={self.post_id}, session={self.session_key})"
    

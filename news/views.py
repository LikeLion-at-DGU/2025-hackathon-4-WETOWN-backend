from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from .models import News
from .serializers import NewsSerializer, NewsListSerializer, NewsImageSerializer

from .utils import get_article_links, get_article_detail
from .services import summarize_article, summarize_title_to_short

class NewsViewSet(viewsets.ModelViewSet):
  queryset = News.objects.all().order_by("-created_at")

  def get_serializer_class(self):
    if self.action in ("list", "latest", "latest_three"):
      return NewsListSerializer
    return NewsSerializer
  
  def get_serializer_context(self):
    ctx = super().get_serializer_context()
    ctx["request"] = self.request
    return ctx
  
  def get_queryset(self):
    return super().get_queryset()
  
  @action(methods=["GET"], detail=False, url_path="latest")
  def latest(self, request):
    obj = self.get_queryset().first()
    if not obj:
      return Response({})
    ser = self.get_serializer(obj)
    return Response(ser.data)

# 홈화면용 : 최근 3개 간단 정보
  @action(methods=["GET"], detail=False, url_path="latest-three")
  def latest_three(self, request):
      qs = self.get_queryset()[:3]
      ser = NewsListSerializer(qs, many=True, context={"request":request})
      return Response(ser.data)
  
  #사진만
  @action(methods=["GET"], detail=False, url_path="latest-images")
  def latest_images(self, request):
      qs = self.get_queryset()[:3]
      ser = NewsImageSerializer(qs, many=True, context={"request": request})
      return Response(ser.data)

  @action(methods=["GET"], detail=False, url_path="crawl-latest")
  def crawl_latest(self, request):
      area_code = request.query_params.get("area_code", "140")  # 기본: 중구(140)
      try:
          max_pages = int(request.query_params.get("pages", "1"))
      except ValueError:
          max_pages = 1

      links = get_article_links(area_code=area_code, max_pages=max_pages)
      if not links:
        return Response({"message": "기사를 찾을 수 없습니다."}, status=status.HTTP_200_OK)

      # 첫 기사만 크롤링 & 요약
      article = get_article_detail(links[0])
      summary = summarize_article(article.get("content", ""))

      return Response(
          {
              "title": article.get("title"),
              "date": article.get("date"),
              "writer": article.get("writer"),
              "summary": summary,
              "images": article.get("images", []),
              "source_url": article.get("url"),
          },
          status=status.HTTP_200_OK,
        )
  
    # ✅ 크롤링 → 요약 → DB 저장 (썸네일=image_url 첫 장, 원문 링크/출처/저자 포함)
  @action(methods=["POST"], detail=False, url_path="crawl-and-create")
  def crawl_and_create(self, request):
    area_code = request.query_params.get("area_code", "140")
    try:
        max_pages = int(request.query_params.get("pages", "1"))
    except ValueError:
        max_pages = 1
    try:
        limit = int(request.query_params.get("limit", "3"))
    except ValueError:
        limit = 3

    links = get_article_links(area_code=area_code, max_pages=max_pages)
    if not links:
        return Response({"message": "크롤링할 기사를 찾을 수 없습니다."}, status=status.HTTP_200_OK)

    created, skipped = [], []
    source_name = "서울시 미디어허브"

    for url in links[:limit]:
        # 중복 방지: 모델에 source_url 필드가 있으면 그걸로 체크
        if hasattr(News, "source_url") and News.objects.filter(source_url=url).exists():
            skipped.append(url)
            continue

        art = get_article_detail(url)
        content = art.get("content") or ""
        title = art.get("title") or "제목 없음"
        author = art.get("writer") or ""
        summary = summarize_article(content) if content else ""
        short_title = summarize_title_to_short(title) if title else ""
        
        date_str = art.get("date")
        published_at = None
        if date_str:
            import re
            date_cleaned = re.search(r"\d{4}[-.]\d{2}[-.]\d{2}( \d{2}:\d{2})?", date_str)
            if date_cleaned:
                date_str = date_cleaned.group()
            for fmt in ("%Y.%m.%d %H:%M", "%Y.%m.%d", "%Y-%m-%d", "%Y-%m-%d %H:%M"):
                try:
                    published_at = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue

        # 본문 + 요약 + 원문/출처를 body에 포함
        body_parts = [content]
        if summary:
            body_parts += ["", "---", "요약:", summary]
        body_parts += ["", f"원문: {url}", f"출처: {source_name}"]

        obj = News(
            title=title,
            short_title =short_title,
            summary=summary,
            published_at = published_at
        )

        # 선택 필드들: 모델에 있을 때만 세팅 (image_url / source_url / source_name / author)
        first_img = (art.get("images") or [None])[0]
        if hasattr(obj, "image_url"):
            obj.image_url = first_img
        if hasattr(obj, "source_url"):
            obj.source_url = url
        if hasattr(obj, "source_name"):
            obj.source_name = source_name
        if hasattr(obj, "author"):
            obj.author = author

        obj.save()

        created.append({
            "id": obj.id,
            "title": obj.title,
            "source_url": url,
        })

    return Response(
        {
            "created_count": len(created),
            "skipped_count": len(skipped),
            "created": created,
            "skipped": skipped,
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )
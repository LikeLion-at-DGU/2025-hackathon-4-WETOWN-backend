# news/services.py
from openai import OpenAI
from django.conf import settings

# ✅ API 키는 settings.py 같은 안전한 곳에서 불러오는 게 좋아요
client = OpenAI(api_key=settings.OPEN_API_KEY)

def summarize_article(content: str) -> str:
    """
    기사 본문(content)을 받아서 3문장 이내 한국어 요약 반환
    """
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "당신은 한국어 뉴스를 간결하게 요약하는 도우미입니다."},
            {"role": "user", "content": f"다음 기사를 3문장 이내로 요약해줘:\n\n{content}"}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content

def summarize_title_to_short(title: str) -> str:
    """
    긴 제목을 짧게 요약 (15자 이내)
    """
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "당신은 한국어 뉴스 제목을 짧고 간결하게 요약하는 도우미입니다."},
            {"role": "user", "content": f"다음 제목을 15자 이내로 요약해줘:\n\n{title}"}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

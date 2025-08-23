from openai import OpenAI
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

client = OpenAI(api_key=settings.OPEN_API_KEY)

@api_view(["POST"])
def simple_chat(request):
    user_msg = request.data.get("message", "")
    if not user_msg:
        return Response({"reply": "무엇을 도와드릴까요? 예: '전입신고 방법 알려줘'"})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 지역 생활/민원 관련 질문을 돕는 한국어 챗봇이야. 친절하고 정확하게 대답해."},
                {"role": "user", "content": user_msg},
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"오류가 발생했어요: \n{str(e)}"

    return Response({"reply": reply})

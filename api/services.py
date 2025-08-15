import time
from openai import AsyncOpenAI
from django.conf import settings
from asgiref.sync import sync_to_async
from .models import AILogs

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

async def get_ai_response(prompt: str, user=None) -> str:
    if not settings.OPENROUTER_API_KEY:
        return "Error!!! \nOPENROUTER_API_KEY is not set in your .env file!!!"

    start_time = time.time()
    response_text = ""

    try:
        completion = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        response_text = f"An error occurred: {str(e)}"

    duration_ms = int((time.time() - start_time) * 1000)

    await sync_to_async(AILogs.objects.create)(
        user=user,
        prompt=prompt,
        response=response_text,
        model_name=settings.OPENROUTER_MODEL,
        duration_ms=duration_ms
    )

    return response_text
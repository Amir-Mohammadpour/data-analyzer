from fastapi import HTTPException, status
from openai import AsyncOpenAI, OpenAIError

from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
)
MODEL_NAME = "gpt-4o"


def build_messages(context: str, question: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "You are a data analysis assistant. "
                "Answer questions only using the information provided in the context. "
                "If the answer cannot be determined from the context, "
                "say that you don't know instead of making up an answer."
            ),
        },
        {
            "role": "user",
            "content": (
                f"=== Data Context ===\n"
                f"{context}\n\n"
                f"=== User Question ===\n"
                f"{question}"
            ),
        },
    ]


async def ask_ai(context: str, question: str) -> tuple[str, int | None]:
    messages = build_messages(context, question)

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )

        answer = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else None

        return answer, tokens_used

    except OpenAIError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently unavailable",
        )

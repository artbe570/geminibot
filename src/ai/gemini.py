import logging
from typing import List, Dict

import httpx
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты — дружелюбный и полезный ассистент в Telegram. "
    "Отвечай на русском языке, кратко и по существу."
)

# Shared client instance, configured on startup.
_gemini_client: genai.Client | None = None


def configure_gemini(api_key: str, proxy_url: str = "") -> None:
    global _gemini_client
    http_options: dict = {}
    if proxy_url:
        logger.info("Gemini client will use proxy %s", proxy_url)
        http_options["httpx_client"] = httpx.Client(proxy=proxy_url)
        http_options["httpx_async_client"] = httpx.AsyncClient(proxy=proxy_url)

    _gemini_client = genai.Client(
        api_key=api_key,
        http_options=http_options if http_options else None,
    )
    logger.info("Gemini API configured")


def _build_contents(
    user_message: str,
    history: List[Dict[str, str]],
) -> List[types.Content]:
    contents: List[types.Content] = []
    for entry in history:
        contents.append(
            types.Content(
                role=entry["role"],
                parts=[types.Part(text=entry["text"])],
            )
        )
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        )
    )
    return contents


async def ask_gemini(
    user_id: int,
    user_message: str,
    history: List[Dict[str, str]],
    model_name: str = "gemini-2.5-flash",
) -> str:
    if _gemini_client is None:
        raise RuntimeError("Gemini client is not configured")

    contents = _build_contents(user_message, history)

    logger.info("Sending request to Gemini for user_id=%s, history_len=%s", user_id, len(history))

    try:
        response = await _gemini_client.aio.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        answer = response.text or "..."
        logger.info("Received response from Gemini for user_id=%s", user_id)
        return answer
    except Exception as exc:
        logger.exception("Gemini API error for user_id=%s: %s", user_id, exc)
        raise

import logging
from typing import Dict, List

from aiogram import F, Router
from aiogram.types import Message

from src.ai.gemini import ask_gemini

logger = logging.getLogger(__name__)

router = Router()

# In-memory storage for conversation history per user.
# Each entry: {"role": "user" | "model", "text": str}
chat_history: Dict[int, List[Dict[str, str]]] = {}

MAX_HISTORY = 10
AI_ERROR_MESSAGE = "Не удалось получить ответ от ИИ. Попробуйте позже."


def get_history(user_id: int) -> List[Dict[str, str]]:
    return chat_history.get(user_id, [])


def add_message(user_id: int, role: str, text: str) -> None:
    history = chat_history.setdefault(user_id, [])
    history.append({"role": role, "text": text})
    if len(history) > MAX_HISTORY:
        chat_history[user_id] = history[-MAX_HISTORY:]


@router.message(F.text == "Очистить контекст")
async def clear_context_handler(message: Message) -> None:
    user_id = message.from_user.id
    logger.info("Clear context requested by user_id=%s", user_id)
    chat_history.pop(user_id, None)
    await message.answer("Контекст диалога очищен.")


@router.message()
async def text_message_handler(message: Message) -> None:
    user_id = message.from_user.id
    user_text = message.text or ""

    logger.info("Incoming message from user_id=%s: %s", user_id, user_text[:200])

    history = get_history(user_id)

    try:
        answer = await ask_gemini(user_id, user_text, history)
    except Exception:
        await message.answer(AI_ERROR_MESSAGE)
        return

    add_message(user_id, "user", user_text)
    add_message(user_id, "model", answer)

    await message.answer(answer)

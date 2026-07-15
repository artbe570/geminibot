import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from config import configure_proxy, load_settings
from src.ai.gemini import configure_gemini
from src.bot.handlers import router
from src.bot.keyboards import main_keyboard

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = load_settings()

    # Configure proxy for the official Google client via env vars
    # (kept for compatibility with any Google HTTP traffic outside google-genai).
    configure_proxy(settings.proxy_url)

    # Configure Gemini client with API key and explicit proxy.
    configure_gemini(settings.gemini_api_key, settings.proxy_url)

    # Create aiohttp session wrapper with proxy for aiogram.
    session = AiohttpSession(proxy=settings.proxy_url) if settings.proxy_url else AiohttpSession()
    logger.info("aiogram aiohttp session configured")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        session=session,
    )

    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting bot")
    try:
        await bot.send_message(
            chat_id="me",
            text="Бот запущен",
            reply_markup=main_keyboard(),
        )
    except Exception:
        logger.exception("Failed to send startup test message to 'me'")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")

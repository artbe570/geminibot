import os
import logging
from dataclasses import dataclass

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    gemini_api_key: str
    proxy_url: str


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    proxy_url = os.getenv("PROXY_URL", "")

    if not bot_token:
        logger.error("BOT_TOKEN not found in environment")
        raise ValueError("BOT_TOKEN is required")
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        raise ValueError("GEMINI_API_KEY is required")
    if not proxy_url:
        logger.warning("PROXY_URL not found in environment, connections will be direct")

    return Settings(
        bot_token=bot_token,
        gemini_api_key=gemini_api_key,
        proxy_url=proxy_url,
    )


def configure_proxy(proxy_url: str) -> None:
    if not proxy_url:
        return

    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    logger.info("Proxy environment variables set to %s", proxy_url)

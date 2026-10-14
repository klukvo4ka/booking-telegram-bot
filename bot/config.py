import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_id: int


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set. Add it to your .env file.")
    return value


def load_config() -> Config:
    load_dotenv()

    bot_token = _require("BOT_TOKEN")
    raw_admin_id = _require("ADMIN_ID")

    try:
        admin_id = int(raw_admin_id)
    except ValueError:
        raise RuntimeError("ADMIN_ID must be a numeric Telegram user ID.") from None

    return Config(bot_token=bot_token, admin_id=admin_id)


config = load_config()

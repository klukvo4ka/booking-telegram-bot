from aiogram import Bot
from aiogram.types import User

from bot.config import config


def format_admin_booking_notification(booking_id: int, user: User, booking_summary: str) -> str:
    username = f"@{user.username}" if user.username else "не указан"
    first_name = user.first_name or "не указано"
    return (
        "🆕 Новая запись\n\n"
        f"ID записи: {booking_id}\n"
        f"Клиент: {first_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}\n\n"
        f"{booking_summary}"
    )


async def notify_admin(bot: Bot, text: str) -> None:
    await bot.send_message(chat_id=config.admin_id, text=text)

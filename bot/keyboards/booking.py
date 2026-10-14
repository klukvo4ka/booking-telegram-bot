from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.catalog import SERVICES

SERVICE_CALLBACK_PREFIX = "service:"


def get_services_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{service.title} — {service.price_label}",
                    callback_data=f"{SERVICE_CALLBACK_PREFIX}{service.id}",
                )
            ]
            for service in SERVICES.values()
        ]
    )

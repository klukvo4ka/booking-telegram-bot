from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.catalog import SERVICES
from bot.dates import format_date_option, get_available_dates

SERVICE_CALLBACK_PREFIX = "service:"
DATE_CALLBACK_PREFIX = "date:"


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


def get_dates_keyboard() -> InlineKeyboardMarkup:
    today = date.today()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=format_date_option(day, today),
                    callback_data=f"{DATE_CALLBACK_PREFIX}{day.isoformat()}",
                )
            ]
            for day in get_available_dates(today)
        ]
    )

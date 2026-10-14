from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.catalog import SERVICES
from bot.dates import AVAILABLE_TIMES, format_date_option, get_available_dates

SERVICE_CALLBACK_PREFIX = "service:"
DATE_CALLBACK_PREFIX = "date:"
TIME_CALLBACK_PREFIX = "time:"
TIME_BUTTONS_PER_ROW = 2


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


def get_times_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=time, callback_data=f"{TIME_CALLBACK_PREFIX}{time}")
        for time in AVAILABLE_TIMES
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[i : i + TIME_BUTTONS_PER_ROW]
            for i in range(0, len(buttons), TIME_BUTTONS_PER_ROW)
        ]
    )

from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.catalog import SERVICES
from bot.dates import format_date_option, get_available_dates, local_today

SERVICE_CALLBACK_PREFIX = "service:"
DATE_CALLBACK_PREFIX = "date:"
TIME_CALLBACK_PREFIX = "time:"
TIME_BUTTONS_PER_ROW = 2

BOOKING_CALLBACK_PREFIX = "booking:"
CONFIRM_BOOKING_CALLBACK = f"{BOOKING_CALLBACK_PREFIX}confirm"
CANCEL_BOOKING_CALLBACK = f"{BOOKING_CALLBACK_PREFIX}cancel"


def get_services_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=service.label,
                    callback_data=f"{SERVICE_CALLBACK_PREFIX}{service.id}",
                )
            ]
            for service in SERVICES.values()
        ]
    )


def get_dates_keyboard() -> InlineKeyboardMarkup:
    today = local_today()
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


def get_times_keyboard(times: Sequence[str]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=time, callback_data=f"{TIME_CALLBACK_PREFIX}{time}")
        for time in times
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[i : i + TIME_BUTTONS_PER_ROW]
            for i in range(0, len(buttons), TIME_BUTTONS_PER_ROW)
        ]
    )


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=CONFIRM_BOOKING_CALLBACK),
                InlineKeyboardButton(text="❌ Отменить", callback_data=CANCEL_BOOKING_CALLBACK),
            ]
        ]
    )

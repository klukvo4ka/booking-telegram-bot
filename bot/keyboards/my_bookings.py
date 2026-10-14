from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CANCEL_BOOKING_PREFIX = "cancel_booking:"
CONFIRM_CANCEL_PREFIX = "confirm_cancel:"
KEEP_BOOKING_PREFIX = "keep_booking:"


def get_booking_actions_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"{CANCEL_BOOKING_PREFIX}{booking_id}")],
        ]
    )


def get_cancel_confirmation_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, отменить", callback_data=f"{CONFIRM_CANCEL_PREFIX}{booking_id}")],
            [InlineKeyboardButton(text="↩️ Нет", callback_data=f"{KEEP_BOOKING_PREFIX}{booking_id}")],
        ]
    )

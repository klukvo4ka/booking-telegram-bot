from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BOOK_BUTTON = "📅 Записаться"
MY_BOOKINGS_BUTTON = "📋 Мои записи"
ABOUT_BUTTON = "ℹ️ О сервисе"


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BOOK_BUTTON), KeyboardButton(text=MY_BOOKINGS_BUTTON)],
            [KeyboardButton(text=ABOUT_BUTTON)],
        ],
        resize_keyboard=True,
    )

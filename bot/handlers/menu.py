from aiogram import F, Router
from aiogram.types import Message

from bot.catalog import SERVICES
from bot.dates import AVAILABLE_TIMES, BOOKING_DAYS
from bot.keyboards.main_menu import ABOUT_BUTTON, BOOK_BUTTON

router = Router(name="menu")

ABOUT_TEXT = (
    "ℹ️ О сервисе\n\n"
    "Онлайн-запись в барбершоп\n\n"
    "Услуги:\n"
    + "\n".join(service.label for service in SERVICES.values())
    + "\n\n"
    f"Время записи: {AVAILABLE_TIMES[0]}–{AVAILABLE_TIMES[-1]}, каждый час\n"
    f"Запись открыта на {BOOKING_DAYS} дней вперёд\n\n"
    f"Нажмите «{BOOK_BUTTON}», чтобы выбрать время"
)


@router.message(F.text == ABOUT_BUTTON)
async def show_about(message: Message) -> None:
    await message.answer(ABOUT_TEXT)

from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.main_menu import ABOUT_BUTTON, MY_BOOKINGS_BUTTON

router = Router(name="menu")


@router.message(F.text.in_({MY_BOOKINGS_BUTTON, ABOUT_BUTTON}))
async def handle_menu_placeholder(message: Message) -> None:
    await message.answer("Этот раздел будет добавлен на следующем этапе.")

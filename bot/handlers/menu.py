from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.main_menu import MAIN_MENU_BUTTONS

router = Router(name="menu")


@router.message(F.text.in_(MAIN_MENU_BUTTONS))
async def handle_menu_placeholder(message: Message) -> None:
    await message.answer("Этот раздел будет добавлен на следующем этапе.")

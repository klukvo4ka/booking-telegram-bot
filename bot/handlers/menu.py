from aiogram import F, Router
from aiogram.types import Message

from bot.catalog import BUSINESS_ADDRESS, BUSINESS_HOURS, BUSINESS_NAME
from bot.keyboards.main_menu import ABOUT_BUTTON

router = Router(name="menu")

ABOUT_TEXT = (
    f"{BUSINESS_NAME} — современный барбершоп в центре Москвы\n\n"
    "✂️ Мужские стрижки\n"
    "🧔 Оформление бороды\n"
    "👦 Детские стрижки\n"
    "🧴 Уход и укладка\n\n"
    f"📍 {BUSINESS_ADDRESS}\n"
    f"🕙 {BUSINESS_HOURS}\n\n"
    "Запись доступна прямо в Telegram — выберите услугу, дату и свободное время"
)


@router.message(F.text == ABOUT_BUTTON)
async def show_about(message: Message) -> None:
    await message.answer(ABOUT_TEXT)

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.catalog import BUSINESS_ADDRESS, BUSINESS_HOURS, BUSINESS_NAME
from bot.keyboards.main_menu import get_main_menu_keyboard

router = Router(name="start")

WELCOME_TEXT = (
    f"Добро пожаловать в {BUSINESS_NAME} 👋\n\n"
    "Здесь Вы можете выбрать услугу, удобную дату и свободное время для визита\n\n"
    f"📍 {BUSINESS_ADDRESS}\n"
    f"🕙 {BUSINESS_HOURS}\n\n"
    "Выберите действие ниже:"
)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard())

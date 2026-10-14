from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.main_menu import get_main_menu_keyboard

router = Router(name="start")

WELCOME_TEXT = (
    "Привет! 👋\n\n"
    "Я помогу тебе записаться на услугу в удобное время.\n\n"
    "Выбери действие ниже:"
)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard())

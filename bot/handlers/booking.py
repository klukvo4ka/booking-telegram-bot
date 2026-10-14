from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.catalog import SERVICES
from bot.keyboards.booking import SERVICE_CALLBACK_PREFIX, get_services_keyboard
from bot.keyboards.main_menu import BOOK_BUTTON
from bot.states.booking import BookingState

router = Router(name="booking")


@router.message(F.text == BOOK_BUTTON)
async def start_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BookingState.choosing_service)
    await message.answer("Выберите услугу:", reply_markup=get_services_keyboard())


@router.callback_query(
    BookingState.choosing_service,
    F.data.startswith(SERVICE_CALLBACK_PREFIX),
)
async def choose_service(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = callback.data.removeprefix(SERVICE_CALLBACK_PREFIX)
    service = SERVICES.get(service_id)
    if service is None:
        await callback.answer("Неизвестная услуга. Попробуйте снова.", show_alert=True)
        return

    await state.update_data(service_id=service.id)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "Вы выбрали:\n\n"
            f"{service.title}\n"
            f"Стоимость: {service.price_label}\n\n"
            "Выбор даты будет добавлен на следующем этапе."
        )
    await callback.answer()


@router.callback_query(F.data.startswith(SERVICE_CALLBACK_PREFIX))
async def handle_stale_service_choice(callback: CallbackQuery) -> None:
    await callback.answer(
        f"Этот выбор больше не активен. Нажмите «{BOOK_BUTTON}», чтобы начать заново.",
        show_alert=True,
    )

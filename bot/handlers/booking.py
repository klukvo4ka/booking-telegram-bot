from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.catalog import SERVICES, Service
from bot.dates import format_date, get_available_dates
from bot.keyboards.booking import (
    DATE_CALLBACK_PREFIX,
    SERVICE_CALLBACK_PREFIX,
    get_dates_keyboard,
    get_services_keyboard,
)
from bot.keyboards.main_menu import BOOK_BUTTON
from bot.states.booking import BookingState

router = Router(name="booking")


def _service_summary(service: Service) -> str:
    return f"{service.title}\nСтоимость: {service.price_label}"


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
        await callback.answer("Неизвестная услуга, попробуйте снова", show_alert=True)
        return

    await state.update_data(service_id=service.id)
    await state.set_state(BookingState.choosing_date)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"Вы выбрали:\n\n{_service_summary(service)}\n\nВыберите дату:",
            reply_markup=get_dates_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    BookingState.choosing_date,
    F.data.startswith(DATE_CALLBACK_PREFIX),
)
async def choose_date(callback: CallbackQuery, state: FSMContext) -> None:
    raw_date = callback.data.removeprefix(DATE_CALLBACK_PREFIX)
    try:
        if len(raw_date) != 10 or raw_date[4] != "-" or raw_date[7] != "-":
            raise ValueError
        day = date.fromisoformat(raw_date)
    except ValueError:
        await callback.answer("Некорректная дата, попробуйте выбрать снова", show_alert=True)
        return

    if day not in get_available_dates():
        await callback.answer("Эта дата больше недоступна, выберите другую", show_alert=True)
        return

    await state.update_data(date=day.isoformat())
    data = await state.get_data()
    service = SERVICES[data["service_id"]]

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"Запись:\n\n{_service_summary(service)}\nДата: {format_date(day)}\n\n"
            "Выбор времени будет добавлен на следующем этапе"
        )
    await callback.answer()


@router.callback_query(F.data.startswith((SERVICE_CALLBACK_PREFIX, DATE_CALLBACK_PREFIX)))
async def handle_stale_choice(callback: CallbackQuery) -> None:
    await callback.answer("Этот выбор больше не активен, начните запись заново", show_alert=True)

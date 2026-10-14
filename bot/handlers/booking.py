from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.catalog import SERVICES, Service
from bot.dates import AVAILABLE_TIMES, format_date, get_available_dates
from bot.keyboards.booking import (
    DATE_CALLBACK_PREFIX,
    SERVICE_CALLBACK_PREFIX,
    TIME_CALLBACK_PREFIX,
    get_dates_keyboard,
    get_services_keyboard,
    get_times_keyboard,
)
from bot.keyboards.main_menu import BOOK_BUTTON
from bot.states.booking import BookingState

router = Router(name="booking")


def _booking_summary(service: Service, day: date | None = None, time: str | None = None) -> str:
    lines = [service.title, f"Стоимость: {service.price_label}"]
    if day is not None:
        lines.append(f"Дата: {format_date(day)}")
    if time is not None:
        lines.append(f"Время: {time}")
    return "\n".join(lines)


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
            f"Вы выбрали:\n\n{_booking_summary(service)}\n\nВыберите дату:",
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
    await state.set_state(BookingState.choosing_time)
    data = await state.get_data()
    service = SERVICES[data["service_id"]]

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"Запись:\n\n{_booking_summary(service, day)}\n\nВыберите время:",
            reply_markup=get_times_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    BookingState.choosing_time,
    F.data.startswith(TIME_CALLBACK_PREFIX),
)
async def choose_time(callback: CallbackQuery, state: FSMContext) -> None:
    time = callback.data.removeprefix(TIME_CALLBACK_PREFIX)
    if time not in AVAILABLE_TIMES:
        await callback.answer("Это время недоступно, выберите другое", show_alert=True)
        return

    data = await state.get_data()
    if "time" in data:
        await callback.answer("Этот выбор больше не активен, начните запись заново", show_alert=True)
        return

    await state.update_data(time=time)
    service = SERVICES[data["service_id"]]
    day = date.fromisoformat(data["date"])

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"Ваша запись:\n\n{_booking_summary(service, day, time)}\n\n"
            "Подтверждение записи будет добавлено на следующем этапе"
        )
    await callback.answer()


@router.callback_query(
    F.data.startswith((SERVICE_CALLBACK_PREFIX, DATE_CALLBACK_PREFIX, TIME_CALLBACK_PREFIX))
)
async def handle_stale_choice(callback: CallbackQuery) -> None:
    await callback.answer("Этот выбор больше не активен, начните запись заново", show_alert=True)

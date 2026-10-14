import logging
import sqlite3
from contextlib import suppress
from datetime import date
from typing import Any

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.booking_rules import (
    MAX_UPCOMING_BOOKINGS,
    get_available_times_for_date,
    has_reached_booking_limit,
)
from bot.catalog import SERVICES, Service
from bot.database import SlotAlreadyBookedError, create_booking
from bot.dates import AVAILABLE_TIMES, format_date, get_available_dates, get_future_times
from bot.keyboards.booking import (
    BOOKING_CALLBACK_PREFIX,
    CANCEL_BOOKING_CALLBACK,
    CONFIRM_BOOKING_CALLBACK,
    DATE_CALLBACK_PREFIX,
    SERVICE_CALLBACK_PREFIX,
    TIME_CALLBACK_PREFIX,
    get_confirmation_keyboard,
    get_dates_keyboard,
    get_services_keyboard,
    get_times_keyboard,
)
from bot.keyboards.main_menu import BOOK_BUTTON
from bot.notifications import format_admin_booking_notification, notify_admin
from bot.states.booking import BookingState

router = Router(name="booking")
logger = logging.getLogger(__name__)

LIMIT_REACHED_TEXT = f"У вас уже есть {MAX_UPCOMING_BOOKINGS} предстоящие записи"
AVAILABILITY_ERROR_TEXT = "Не удалось проверить свободное время, попробуйте позже"


def _booking_summary(service: Service, day: date | None = None, time: str | None = None) -> str:
    lines = [service.title, f"Стоимость: {service.price_label}"]
    if day is not None:
        lines.append(f"Дата: {format_date(day)}")
    if time is not None:
        lines.append(f"Время: {time}")
    return "\n".join(lines)


def _parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or len(value) != 10 or value[4] != "-" or value[7] != "-":
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _load_service(data: dict[str, Any]) -> Service | None:
    service_id = data.get("service_id")
    if not isinstance(service_id, str):
        return None
    return SERVICES.get(service_id)


def _load_service_and_date(data: dict[str, Any]) -> tuple[Service, date] | None:
    service = _load_service(data)
    day = _parse_iso_date(data.get("date"))
    if service is None or day is None or day not in get_available_dates():
        return None
    return service, day


def _load_booking(data: dict[str, Any]) -> tuple[Service, date, str] | None:
    service_and_date = _load_service_and_date(data)
    if service_and_date is None:
        return None
    service, day = service_and_date
    time = data.get("time")
    if time not in AVAILABLE_TIMES:
        return None
    return service, day, time


async def _edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if isinstance(callback.message, Message):
        await callback.message.edit_text(text, reply_markup=reply_markup)


async def _load_available_times(callback: CallbackQuery, day: date) -> tuple[str, ...] | None:
    try:
        return await get_available_times_for_date(day)
    except sqlite3.Error:
        logger.exception("Failed to load available times")
        await callback.answer(AVAILABILITY_ERROR_TEXT, show_alert=True)
        return None


async def _show_time_choice(
    callback: CallbackQuery,
    state: FSMContext,
    service: Service,
    day: date,
    times: tuple[str, ...],
    heading: str = "Запись:",
    prompt: str = "Выберите время:",
) -> None:
    await state.set_data({"service_id": service.id, "date": day.isoformat()})
    await state.set_state(BookingState.choosing_time)
    await _edit_message(
        callback,
        f"{heading}\n\n{_booking_summary(service, day)}\n\n{prompt}",
        get_times_keyboard(times),
    )


async def _return_to_date_choice(callback: CallbackQuery, state: FSMContext, service: Service) -> None:
    await state.set_data({"service_id": service.id})
    await state.set_state(BookingState.choosing_date)
    await _edit_message(
        callback,
        f"На эту дату свободного времени больше нет\n\n{_booking_summary(service)}\n\nВыберите другую дату:",
        get_dates_keyboard(),
    )


async def _offer_other_time(
    callback: CallbackQuery,
    state: FSMContext,
    service: Service,
    day: date,
    heading: str,
) -> None:
    times = await _load_available_times(callback, day)
    if times is None:
        return
    if times:
        await _show_time_choice(callback, state, service, day, times, heading, "Выберите другое время:")
    else:
        await _return_to_date_choice(callback, state, service)
    await callback.answer()


@router.message(F.text == BOOK_BUTTON)
async def start_booking(message: Message, state: FSMContext) -> None:
    await state.clear()

    try:
        limit_reached = await has_reached_booking_limit(message.from_user.id)
    except sqlite3.Error:
        logger.exception("Failed to count user bookings")
        await message.answer("Не удалось начать запись, попробуйте позже")
        return

    if limit_reached:
        await message.answer(
            f"{LIMIT_REACHED_TEXT}\n\nСначала используйте одну из них или обратитесь к администратору"
        )
        return

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
    await _edit_message(
        callback,
        f"Вы выбрали:\n\n{_booking_summary(service)}\n\nВыберите дату:",
        get_dates_keyboard(),
    )
    await callback.answer()


@router.callback_query(
    BookingState.choosing_date,
    F.data.startswith(DATE_CALLBACK_PREFIX),
)
async def choose_date(callback: CallbackQuery, state: FSMContext) -> None:
    day = _parse_iso_date(callback.data.removeprefix(DATE_CALLBACK_PREFIX))
    if day is None:
        await callback.answer("Некорректная дата, попробуйте выбрать снова", show_alert=True)
        return

    if day not in get_available_dates():
        await callback.answer("Эта дата больше недоступна, выберите другую", show_alert=True)
        return

    times = await _load_available_times(callback, day)
    if times is None:
        return
    if not times:
        await callback.answer("На эту дату свободного времени нет\n\nВыберите другую дату", show_alert=True)
        return

    service = _load_service(await state.get_data())
    if service is None:
        await state.clear()
        await _edit_message(callback, "Не удалось продолжить запись, начните заново")
        await callback.answer()
        return

    await _show_time_choice(callback, state, service, day, times)
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

    service_and_date = _load_service_and_date(await state.get_data())
    if service_and_date is None:
        await state.clear()
        await _edit_message(callback, "Не удалось продолжить запись, начните заново")
        await callback.answer()
        return
    service, day = service_and_date

    times = await _load_available_times(callback, day)
    if times is None:
        return

    if time not in times:
        await callback.answer("Это время уже недоступно, выберите другое", show_alert=True)
        if not times:
            await _return_to_date_choice(callback, state, service)
        elif isinstance(callback.message, Message):
            with suppress(TelegramBadRequest):
                await callback.message.edit_reply_markup(reply_markup=get_times_keyboard(times))
        return

    await state.update_data(time=time)
    await state.set_state(BookingState.confirming_booking)
    await _edit_message(
        callback,
        f"Проверьте запись:\n\n{_booking_summary(service, day, time)}\n\nВсё верно?",
        get_confirmation_keyboard(),
    )
    await callback.answer()


@router.callback_query(BookingState.confirming_booking, F.data == CONFIRM_BOOKING_CALLBACK)
async def confirm_booking(callback: CallbackQuery, state: FSMContext) -> None:
    booking = _load_booking(await state.get_data())
    if booking is None:
        await state.clear()
        await _edit_message(callback, "Не удалось подтвердить запись, начните заново")
        await callback.answer()
        return

    service, day, time = booking
    if time not in get_future_times(day):
        await _offer_other_time(callback, state, service, day, "Это время уже недоступно")
        return

    user = callback.from_user
    try:
        if await has_reached_booking_limit(user.id):
            await state.clear()
            await _edit_message(callback, f"{LIMIT_REACHED_TEXT}\n\nНовая запись не создана")
            await callback.answer()
            return

        booking_id = await create_booking(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            service_id=service.id,
            booking_date=day.isoformat(),
            booking_time=time,
        )
    except SlotAlreadyBookedError:
        await _offer_other_time(callback, state, service, day, "Это время уже заняли")
        return
    except sqlite3.Error:
        logger.exception("Failed to save booking")
        await callback.answer("Не удалось сохранить запись, попробуйте позже", show_alert=True)
        return

    summary = _booking_summary(service, day, time)
    try:
        await notify_admin(callback.bot, format_admin_booking_notification(user, summary))
    except Exception:
        logger.exception("Failed to notify admin about booking %s", booking_id)

    await state.clear()
    await _edit_message(callback, f"✅ Запись подтверждена\n\n{summary}\n\nДо встречи!")
    await callback.answer()


@router.callback_query(BookingState.confirming_booking, F.data == CANCEL_BOOKING_CALLBACK)
async def cancel_booking(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await _edit_message(callback, "Запись отменена\n\nВы можете начать заново через меню")
    await callback.answer()


@router.callback_query(
    F.data.startswith(BOOKING_CALLBACK_PREFIX),
    ~F.data.in_({CONFIRM_BOOKING_CALLBACK, CANCEL_BOOKING_CALLBACK}),
)
async def handle_unknown_booking_action(callback: CallbackQuery) -> None:
    await callback.answer("Неизвестное действие", show_alert=True)


@router.callback_query(
    F.data.startswith(
        (SERVICE_CALLBACK_PREFIX, DATE_CALLBACK_PREFIX, TIME_CALLBACK_PREFIX, BOOKING_CALLBACK_PREFIX)
    )
)
async def handle_stale_choice(callback: CallbackQuery) -> None:
    await callback.answer("Этот выбор больше не активен, начните запись заново", show_alert=True)

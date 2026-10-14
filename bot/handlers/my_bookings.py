import logging
import sqlite3
from datetime import date

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.catalog import SERVICES
from bot.database import (
    BookingRecord,
    delete_booking_for_user,
    get_upcoming_booking_for_user,
    get_upcoming_bookings_for_user,
)
from bot.dates import format_date, local_today
from bot.keyboards.main_menu import BOOK_BUTTON, MY_BOOKINGS_BUTTON
from bot.keyboards.my_bookings import (
    CANCEL_BOOKING_PREFIX,
    CONFIRM_CANCEL_PREFIX,
    KEEP_BOOKING_PREFIX,
    get_booking_actions_keyboard,
    get_cancel_confirmation_keyboard,
)

router = Router(name="my_bookings")
logger = logging.getLogger(__name__)

EMPTY_TEXT = f"У вас пока нет предстоящих записей\n\nНажмите «{BOOK_BUTTON}», чтобы создать новую"
UNAVAILABLE_TEXT = "Эта запись больше недоступна"
LOAD_ERROR_TEXT = "Не удалось загрузить записи, попробуйте позже"


def _format_booking(booking: BookingRecord, with_price: bool = True) -> str:
    service = SERVICES.get(booking.service_id)
    try:
        booking_day = date.fromisoformat(booking.booking_date)
    except (TypeError, ValueError):
        date_label = "Неизвестная дата"
    else:
        date_label = format_date(booking_day)

    lines = [
        service.title if service else "Неизвестная услуга",
        f"Дата: {date_label}",
        f"Время: {booking.booking_time}",
    ]
    if service and with_price:
        lines.append(f"Стоимость: {service.price_label}")
    return "\n".join(lines)


def _parse_booking_id(data: str, prefix: str) -> int | None:
    value = data.removeprefix(prefix)
    if not value.isascii() or not value.isdigit() or len(value) > 18:
        return None
    return int(value)


async def _edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if isinstance(callback.message, Message):
        await callback.message.edit_text(text, reply_markup=reply_markup)


async def _load_own_booking(callback: CallbackQuery, prefix: str) -> BookingRecord | None:
    booking_id = _parse_booking_id(callback.data, prefix)
    if booking_id is None:
        await callback.answer(UNAVAILABLE_TEXT, show_alert=True)
        return None

    try:
        booking = await get_upcoming_booking_for_user(
            booking_id=booking_id,
            user_id=callback.from_user.id,
            from_date=local_today().isoformat(),
        )
    except sqlite3.Error:
        logger.exception("Failed to load booking %s", booking_id)
        await callback.answer(LOAD_ERROR_TEXT, show_alert=True)
        return None

    if booking is None:
        await callback.answer(UNAVAILABLE_TEXT, show_alert=True)
    return booking


@router.message(F.text == MY_BOOKINGS_BUTTON)
async def show_my_bookings(message: Message) -> None:
    try:
        bookings = await get_upcoming_bookings_for_user(
            user_id=message.from_user.id,
            from_date=local_today().isoformat(),
        )
    except sqlite3.Error:
        logger.exception("Failed to load bookings")
        await message.answer(LOAD_ERROR_TEXT)
        return

    if not bookings:
        await message.answer(EMPTY_TEXT)
        return

    await message.answer("📋 Ваши записи")
    for booking in bookings:
        await message.answer(_format_booking(booking), reply_markup=get_booking_actions_keyboard(booking.id))


@router.callback_query(F.data.startswith(CANCEL_BOOKING_PREFIX))
async def ask_cancel_confirmation(callback: CallbackQuery) -> None:
    booking = await _load_own_booking(callback, CANCEL_BOOKING_PREFIX)
    if booking is None:
        return

    await _edit_message(
        callback,
        f"Отменить эту запись?\n\n{_format_booking(booking, with_price=False)}",
        get_cancel_confirmation_keyboard(booking.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(CONFIRM_CANCEL_PREFIX))
async def confirm_cancellation(callback: CallbackQuery) -> None:
    booking = await _load_own_booking(callback, CONFIRM_CANCEL_PREFIX)
    if booking is None:
        return

    try:
        deleted = await delete_booking_for_user(
            booking_id=booking.id,
            user_id=callback.from_user.id,
            from_date=local_today().isoformat(),
        )
    except sqlite3.Error:
        logger.exception("Failed to cancel booking %s", booking.id)
        await callback.answer("Не удалось отменить запись, попробуйте позже", show_alert=True)
        return

    if not deleted:
        await callback.answer(UNAVAILABLE_TEXT, show_alert=True)
        return

    await _edit_message(callback, f"Запись отменена\n\n{_format_booking(booking, with_price=False)}")
    await callback.answer()


@router.callback_query(F.data.startswith(KEEP_BOOKING_PREFIX))
async def keep_booking(callback: CallbackQuery) -> None:
    booking = await _load_own_booking(callback, KEEP_BOOKING_PREFIX)
    if booking is None:
        return

    await _edit_message(callback, _format_booking(booking), get_booking_actions_keyboard(booking.id))
    await callback.answer()

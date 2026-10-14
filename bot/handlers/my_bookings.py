import logging
import sqlite3
from datetime import date

from aiogram import F, Router
from aiogram.types import Message

from bot.catalog import SERVICES
from bot.database import BookingRecord, get_upcoming_bookings_for_user
from bot.dates import format_date
from bot.keyboards.main_menu import BOOK_BUTTON, MY_BOOKINGS_BUTTON

router = Router(name="my_bookings")
logger = logging.getLogger(__name__)

EMPTY_TEXT = f"У вас пока нет предстоящих записей\n\nНажмите «{BOOK_BUTTON}», чтобы создать новую"


def _format_booking(number: int, booking: BookingRecord) -> str:
    service = SERVICES.get(booking.service_id)
    try:
        booking_day = date.fromisoformat(booking.booking_date)
    except (TypeError, ValueError):
        date_label = "Неизвестная дата"
    else:
        date_label = format_date(booking_day)

    lines = [
        f"{number}. {service.title if service else 'Неизвестная услуга'}",
        f"Дата: {date_label}",
        f"Время: {booking.booking_time}",
    ]
    if service:
        lines.append(f"Стоимость: {service.price_label}")
    return "\n".join(lines)


@router.message(F.text == MY_BOOKINGS_BUTTON)
async def show_my_bookings(message: Message) -> None:
    try:
        bookings = await get_upcoming_bookings_for_user(
            user_id=message.from_user.id,
            from_date=date.today().isoformat(),
        )
    except sqlite3.Error:
        logger.exception("Failed to load bookings")
        await message.answer("Не удалось загрузить записи, попробуйте позже")
        return

    if not bookings:
        await message.answer(EMPTY_TEXT)
        return

    items = "\n\n".join(_format_booking(i, booking) for i, booking in enumerate(bookings, start=1))
    await message.answer(f"📋 Ваши записи\n\n{items}")

from datetime import date, datetime

from bot.database import count_upcoming_bookings_for_user, get_booked_times_for_date
from bot.dates import get_future_times, local_today

MAX_UPCOMING_BOOKINGS = 3


async def get_available_times_for_date(day: date, now: datetime | None = None) -> tuple[str, ...]:
    booked = await get_booked_times_for_date(day.isoformat())
    return tuple(slot for slot in get_future_times(day, now) if slot not in booked)


async def has_reached_booking_limit(user_id: int) -> bool:
    count = await count_upcoming_bookings_for_user(user_id, local_today().isoformat())
    return count >= MAX_UPCOMING_BOOKINGS

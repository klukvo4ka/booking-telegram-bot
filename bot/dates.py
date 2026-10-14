from datetime import date, datetime, time, timedelta

BOOKING_DAYS = 7

AVAILABLE_TIMES = (
    "10:00", "11:00", "12:00", "13:00", "14:00",
    "15:00", "16:00", "17:00", "18:00", "19:00",
)

WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
MONTHS = (
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
)


def local_now() -> datetime:
    return datetime.now()


def local_today() -> date:
    return local_now().date()


def get_available_dates(today: date | None = None) -> list[date]:
    today = today or local_today()
    return [today + timedelta(days=offset) for offset in range(BOOKING_DAYS)]


def get_future_times(day: date, now: datetime | None = None) -> tuple[str, ...]:
    now = now or local_now()
    return tuple(
        slot for slot in AVAILABLE_TIMES
        if datetime.combine(day, time.fromisoformat(slot)) > now
    )


def _day_and_month(day: date) -> str:
    return f"{day.day} {MONTHS[day.month - 1]}"


def format_date(day: date) -> str:
    return f"{WEEKDAYS[day.weekday()]}, {_day_and_month(day)}"


def format_date_option(day: date, today: date) -> str:
    if day == today:
        return f"Сегодня, {_day_and_month(day)}"
    if day == today + timedelta(days=1):
        return f"Завтра, {_day_and_month(day)}"
    return format_date(day)

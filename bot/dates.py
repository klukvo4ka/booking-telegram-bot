from datetime import date, timedelta

BOOKING_DAYS = 7

WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
MONTHS = (
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
)


def get_available_dates(today: date | None = None) -> list[date]:
    today = today or date.today()
    return [today + timedelta(days=offset) for offset in range(BOOKING_DAYS)]


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

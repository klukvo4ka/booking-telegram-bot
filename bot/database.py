import sqlite3
from dataclasses import dataclass
from pathlib import Path

import aiosqlite

DATABASE_PATH = Path(__file__).resolve().parent.parent / "bookings.db"

CREATE_BOOKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    first_name TEXT,
    service_id TEXT NOT NULL,
    booking_date TEXT NOT NULL,
    booking_time TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (booking_date, booking_time)
)
"""

INSERT_BOOKING = """
INSERT INTO bookings (user_id, username, first_name, service_id, booking_date, booking_time)
VALUES (?, ?, ?, ?, ?, ?)
"""

SELECT_UPCOMING_BOOKINGS = """
SELECT id, service_id, booking_date, booking_time
FROM bookings
WHERE user_id = ? AND booking_date >= ?
ORDER BY booking_date, booking_time
"""

SELECT_BOOKED_TIMES = """
SELECT booking_time
FROM bookings
WHERE booking_date = ?
"""

COUNT_UPCOMING_BOOKINGS = """
SELECT COUNT(*)
FROM bookings
WHERE user_id = ? AND booking_date >= ?
"""

SELECT_UPCOMING_BOOKING_FOR_USER = """
SELECT id, service_id, booking_date, booking_time
FROM bookings
WHERE id = ? AND user_id = ? AND booking_date >= ?
"""

DELETE_UPCOMING_BOOKING_FOR_USER = """
DELETE FROM bookings
WHERE id = ? AND user_id = ? AND booking_date >= ?
"""


@dataclass(frozen=True)
class BookingRecord:
    id: int
    service_id: str
    booking_date: str
    booking_time: str


class SlotAlreadyBookedError(Exception):
    pass


async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(CREATE_BOOKINGS_TABLE)
        await db.commit()


async def create_booking(
    user_id: int,
    username: str | None,
    first_name: str | None,
    service_id: str,
    booking_date: str,
    booking_time: str,
) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            cursor = await db.execute(
                INSERT_BOOKING,
                (user_id, username, first_name, service_id, booking_date, booking_time),
            )
            await db.commit()
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
                raise SlotAlreadyBookedError(f"{booking_date} {booking_time} is already booked") from error
            raise
        return cursor.lastrowid


async def get_upcoming_bookings_for_user(user_id: int, from_date: str) -> list[BookingRecord]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(SELECT_UPCOMING_BOOKINGS, (user_id, from_date)) as cursor:
            rows = await cursor.fetchall()
    return [BookingRecord(*row) for row in rows]


async def get_booked_times_for_date(booking_date: str) -> set[str]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(SELECT_BOOKED_TIMES, (booking_date,)) as cursor:
            rows = await cursor.fetchall()
    return {row[0] for row in rows}


async def count_upcoming_bookings_for_user(user_id: int, from_date: str) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(COUNT_UPCOMING_BOOKINGS, (user_id, from_date)) as cursor:
            (count,) = await cursor.fetchone()
    return count


async def get_upcoming_booking_for_user(
    booking_id: int,
    user_id: int,
    from_date: str,
) -> BookingRecord | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            SELECT_UPCOMING_BOOKING_FOR_USER, (booking_id, user_id, from_date)
        ) as cursor:
            row = await cursor.fetchone()
    return BookingRecord(*row) if row else None


async def delete_booking_for_user(booking_id: int, user_id: int, from_date: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(DELETE_UPCOMING_BOOKING_FOR_USER, (booking_id, user_id, from_date))
        await db.commit()
        return cursor.rowcount > 0

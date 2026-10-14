import sqlite3
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

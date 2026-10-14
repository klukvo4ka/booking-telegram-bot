# Telegram Appointment Booking Bot

An asynchronous Telegram bot for appointment booking built with Python, aiogram 3 and SQLite. Users choose a service, a date and a free time slot, confirm the booking and can review their upcoming appointments. The administrator gets a Telegram notification for every new booking.

The included demo configuration represents North Cut, a fictional barbershop in Moscow with seven services. The same flow fits beauty services, tutoring or any other appointment-based business.

## Features

- `/start` entry point with a persistent main menu
- Service selection with prices from a single catalog
- Date selection for the next 7 days, generated dynamically
- Time selection that shows only free slots:
  - past slots are hidden for today
  - already booked slots are hidden
- Booking summary with confirmation or cancellation
- Confirmed bookings stored in SQLite
- Duplicate-slot protection enforced by a database `UNIQUE` constraint
- Recovery when a slot is taken while the user is still booking
- Administrator notification for each saved booking
- "My bookings" view with the user's upcoming appointments
- Cancelling an upcoming booking from "My bookings", with a confirmation step
- Limit of 3 upcoming bookings per user
- Defensive validation of callback data and FSM state, including stale buttons

## Demo

Screenshots are stored in [`docs/screenshots/`](docs/screenshots/).

<!--
### Main menu
![Main menu](docs/screenshots/main-menu.png)

### Service selection
![Service selection](docs/screenshots/service-selection.png)

### Date and time selection
![Date and time selection](docs/screenshots/date-time-selection.png)

### Booking confirmation
![Booking confirmation](docs/screenshots/confirmation.png)

### My bookings
![My bookings](docs/screenshots/my-bookings.png)
-->

## Booking Flow

```
/start
  ↓
Main menu → 📅 Записаться
  ↓
Service
  ↓
Date (next 7 days)
  ↓
Time (only free slots)
  ↓
Confirmation
  ↓
Saved to SQLite
  ↓
Administrator notification
```

Each step is an aiogram FSM state. Availability is checked again when a time is chosen and when the booking is confirmed. If the slot was taken in the meantime, the user is returned to time selection for the same date, or to date selection if that day is fully booked.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12+ | Language |
| aiogram 3 | Telegram Bot API, routers, FSM |
| SQLite + aiosqlite | Async storage for bookings |
| python-dotenv | Loading configuration from `.env` |

## Project Structure

```
booking-telegram-bot/
├── bot/
│   ├── handlers/
│   │   ├── booking.py        # booking flow: service → date → time → confirmation
│   │   ├── menu.py           # "About" section
│   │   ├── my_bookings.py    # upcoming bookings and cancellation
│   │   └── start.py          # /start and main menu
│   ├── keyboards/
│   │   ├── booking.py        # inline keyboards and callback data
│   │   ├── main_menu.py      # reply keyboard
│   │   └── my_bookings.py    # booking cancellation buttons
│   ├── states/
│   │   └── booking.py        # FSM states
│   ├── booking_rules.py      # slot availability and booking limit
│   ├── catalog.py            # business details, services and prices
│   ├── config.py             # environment configuration
│   ├── database.py           # SQLite schema and queries
│   ├── dates.py              # booking window, time slots, Russian date formatting
│   ├── main.py               # entry point
│   └── notifications.py      # administrator notifications
├── docs/
│   └── screenshots/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/klukvo4ka/booking-telegram-bot.git
cd booking-telegram-bot

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
```

Fill in `.env`:

```
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_user_id
```

- `BOT_TOKEN` is the token issued by [@BotFather](https://t.me/BotFather).
- `ADMIN_ID` is the numeric Telegram user ID that receives booking notifications. The administrator needs to start the bot once, otherwise Telegram does not allow the bot to message them.

`.env` is listed in `.gitignore` and is never committed.

## Running the Bot

```bash
python -m bot.main
```

The bot uses long polling. The SQLite database `bookings.db` is created in the project root on first launch.

## Database

Confirmed bookings are stored in a single table:

```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    first_name TEXT,
    service_id TEXT NOT NULL,
    booking_date TEXT NOT NULL,   -- YYYY-MM-DD
    booking_time TEXT NOT NULL,   -- HH:MM
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (booking_date, booking_time)
);
```

The example assumes one specialist, so each date and time can be booked only once. All queries are parameterized.

## Validation and Booking Rules

- Bookings are available for the next 7 days, including today.
- Working slots run hourly from 10:00 to 19:00.
- For today, only slots that start in the future are offered.
- Already booked slots are not shown.
- Availability is rechecked when a time is chosen and again right before saving.
- The `UNIQUE (booking_date, booking_time)` constraint is the final guarantee against two users confirming the same slot at the same moment.
- A user can have at most 3 upcoming bookings (today or later).
- Users can cancel only their own upcoming bookings. The ownership check is part of the `DELETE` query itself, and the freed slot becomes available immediately.
- Callback data and FSM data are validated before use; buttons from an outdated step are answered with a short notice instead of being processed.
- If the administrator notification fails, the booking is still saved and the user still gets a confirmation.

## Development Notes

- In-progress booking state uses aiogram's in-memory FSM storage, so an unfinished booking is reset when the bot restarts. Confirmed bookings are kept in SQLite.
- Dates and times use the server's local time.
- The business details, service catalog and booking slots are defined in code (`bot/catalog.py`, `bot/dates.py`), so the demo branding can be replaced without touching the booking logic.

Possible next steps include rescheduling saved bookings, notifying the administrator about cancellations, schedules for multiple specialists, configurable working hours and an administrative dashboard.

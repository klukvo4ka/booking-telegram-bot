# Telegram Appointment Booking Bot

An asynchronous Telegram bot for booking service appointments. It is designed for appointment-based businesses such as barbershops, beauty services, tutors, and other providers who want clients to book a time slot directly in Telegram.

## Tech stack

- Python 3.12+
- aiogram 3
- python-dotenv
- SQLite (aiosqlite)

## Status

This project is under active development. The booking flow covers service, date and time selection with a confirmation step. Confirmed bookings are stored in SQLite, and each date/time slot can be booked only once. The administrator receives a Telegram notification for every new booking. Users can view their upcoming bookings from the main menu. The remaining features are being added step by step.

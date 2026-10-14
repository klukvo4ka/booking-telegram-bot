import asyncio

from aiogram import Bot, Dispatcher

from bot.config import config
from bot.database import init_db
from bot.handlers import booking, menu, my_bookings, start


async def main() -> None:
    await init_db()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_routers(start.router, booking.router, my_bookings.router, menu.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

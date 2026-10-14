import asyncio

from aiogram import Bot, Dispatcher

from bot.config import config


async def main() -> None:
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

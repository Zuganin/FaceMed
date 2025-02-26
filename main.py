
import asyncio
from aiogram import Dispatcher

from bot.FaceAnalysis import router_analyzer
from bot.handlers.handlers import router_handler
from bot.config import bot, logger
from database.engine import create_db


dp = Dispatcher(bot = bot)

async def main():
    # Создаём таблицы для базы данных
    await create_db()
    logger.info("✅ Таблицы для базы данных созданы ")
    # Запускаем бота
    logger.info("✅ Бот запущен")
    dp.include_routers(router_analyzer,router_handler )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
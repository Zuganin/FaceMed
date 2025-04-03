
import asyncio
from aiogram import Dispatcher

from bot.handlers.handlers import handler_router
from bot.handlers.history_process import history_router
from bot.handlers.registration import registration_router
# from bot.handlers.history_process import history_router
from bot.FaceAnalysis import analyzer_router
from bot.config import bot, logger
from database.engine import create_db, drop_db


dp = Dispatcher(bot = bot)

async def main():
    # Запускаем бота
    dp.include_routers(registration_router, analyzer_router, history_router , handler_router)
    logger.info("✅ Бот запущен")
    await dp.start_polling(bot)



if __name__ == '__main__':
    # Создаём таблицы для базы данных
    asyncio.run(create_db())
    logger.info("✅ Таблицы для базы данных созданы ")
    asyncio.run(main())

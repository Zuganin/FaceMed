
import asyncio
from aiogram import Dispatcher

from bot.FaceAnalysis import router_analyzer
from bot.handlers.handlers import router_handler
from bot.config import bot, logger
from database.engine import create_db, drop_db
import nest_asyncio



dp = Dispatcher(bot = bot)

async def main():
    # Запускаем бота
    dp.include_routers(router_analyzer,router_handler )
    logger.info("✅ Бот запущен")
    await dp.start_polling(bot)



if __name__ == '__main__':
    nest_asyncio.apply()
    # Создаём таблицы для базы данных
    asyncio.run(create_db())
    logger.info("✅ Таблицы для базы данных созданы ")
    asyncio.run(main())

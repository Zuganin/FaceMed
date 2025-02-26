
from aiogram import Bot
from bot.logger import get_logger
from dotenv import load_dotenv
import os


# Укажите абсолютный или относительный путь к вашему файлу .env
dotenv_path = '.env'
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.environ.get('BOT_TOKEN')
bot = Bot(token=TOKEN)

logger = get_logger("general")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


from aiogram import Bot
from bot.logger import get_logger
from dotenv import load_dotenv
import os


# Укажите абсолютный или относительный путь к вашему файлу .env
dotenv_path = '.env'
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.environ.get('BOT_TOKEN')
# TOKEN = "7146359839:AAEVLnL677SrVoxSB0Q9-xA7KmKdnxu7YtM"
bot = Bot(token=TOKEN)

logger = get_logger("general")

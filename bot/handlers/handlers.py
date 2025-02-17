
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import Router


from bot.config import logger


replyCommands = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text = "/help")]],
                                 resize_keyboard=True)

router_handler = Router()

@router_handler.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я бот, созданный для проведения экспресс диагностики твоего здоровья."
                         " Просто пришли мне свое фото и я проанализирую твое здоровье!")
    logger.info(f"Пользователь {message.from_user.id} начал диалог с ботом")

@router_handler.message(Command('help'))
async def help(message: Message):
    await message.answer("Пришлите мне свое фото анфанс (лицом к камере) и выберите желаемые действия!", reply_markup=replyCommands)
    logger.info(f"Пользователь {message.from_user.id} запросил помощь")


@router_handler.message()
async def echo(message: Message):
    logger.info(f"Пользователь {message.from_user.id} отправил сообщение: {message.text} - неизвестная команда")
    await message.answer("Неизвестная команда!")


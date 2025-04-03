from cgitb import handler

from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram import Router

from bot.config import logger
# from bot.Routers import handler_router as router


replyCommands = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text = "/help")],[KeyboardButton(text = "/registration")]],
                                 resize_keyboard=True)

handler_router = Router()
#======================================================================================================================#

@handler_router.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я бот, созданный для проведения экспресс диагностики твоего здоровья."
                         " Просто пришли мне свое фото и я проанализирую твое здоровье!")
    logger.info(f"Пользователь {message.from_user.full_name} начал диалог с ботом")

@handler_router.message(Command('help'))
async def help(message: Message):
    await message.answer("Пришлите мне свое фото анфанс (лицом к камере) и выберите желаемые действия!", reply_markup=replyCommands)
    logger.info(f"Пользователь {message.from_user.full_name} запросил помощь")

#======================================================================================================================#


@handler_router.message()
async def echo(message: Message):
    logger.info(f"Пользователь {message.from_user.full_name} отправил сообщение: {message.text} - неизвестная команда")
    await message.answer("Неизвестная команда!")


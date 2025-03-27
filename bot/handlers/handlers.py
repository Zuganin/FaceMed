

from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram import Router, F , types
from aiogram.fsm.context import  FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from database.database_utils import check_user_registration, register_user
from bot.config import logger


replyCommands = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text = "/help")],[KeyboardButton(text = "/registration")]],
                                 resize_keyboard=True)

router_handler = Router()

#======================================================================================================================#

@router_handler.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я бот, созданный для проведения экспресс диагностики твоего здоровья."
                         " Просто пришли мне свое фото и я проанализирую твое здоровье!")
    logger.info(f"Пользователь {message.from_user.full_name} начал диалог с ботом")

@router_handler.message(Command('help'))
async def help(message: Message):
    await message.answer("Пришлите мне свое фото анфанс (лицом к камере) и выберите желаемые действия!", reply_markup=replyCommands)
    logger.info(f"Пользователь {message.from_user.full_name} запросил помощь")

#======================================================================================================================#



@router_handler.message()
async def echo(message: Message):
    logger.info(f"Пользователь {message.from_user.full_name} отправил сообщение: {message.text} - неизвестная команда")
    await message.answer("Неизвестная команда!")


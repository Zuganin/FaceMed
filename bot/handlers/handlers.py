

from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram import Router, F , types
from aiogram.fsm.context import  FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from bot.config import logger


replyCommands = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text = "/help")],[KeyboardButton(text = "/registration")]],
                                 resize_keyboard=True)
answerSkipAgeButton = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skipAge")]])

answerGenderStateButton = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Мужской", callback_data="мужской"),InlineKeyboardButton(text="Женский", callback_data="женский")],
            [InlineKeyboardButton(text="Пропустить", callback_data="skipGender")]
        ])


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_age = State()
    waiting_for_gender = State()
router_handler = Router()

@router_handler.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я бот, созданный для проведения экспресс диагностики твоего здоровья."
                         " Просто пришли мне свое фото и я проанализирую твое здоровье!")
    logger.info(f"Пользователь {message.from_user.full_name} начал диалог с ботом")

@router_handler.message(Command('help'))
async def help(message: Message):
    await message.answer("Пришлите мне свое фото анфанс (лицом к камере) и выберите желаемые действия!", reply_markup=replyCommands)
    logger.info(f"Пользователь {message.from_user.full_name} запросил помощь")


# Обработчик команды /register - старт регистрации
@router_handler.message(Command('registration'))
async def cmd_register(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.full_name} начал регистрацию")
    prompt_message = await message.answer("Введите ваше имя:")
    await state.update_data(prompt_message_id=prompt_message.message_id)
    await state.set_state(RegistrationStates.waiting_for_name)


# Обработчик ввода имени
@router_handler.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    logger.info(f"✅ Пользователь {message.from_user.full_name} успешно ввёл имя: {message.text}")
    await state.update_data(name=message.text)
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    await message.delete()
    await message.bot.edit_message_text(
        "Введите вашу фамилию:",
        chat_id=message.chat.id,
        message_id=prompt_message_id
    )
    await state.set_state(RegistrationStates.waiting_for_surname)


# Обработчик ввода фамилии
@router_handler.message(StateFilter(RegistrationStates.waiting_for_surname))
async def process_surname(message: Message, state: FSMContext):
    logger.info(f"✅ Пользователь {message.from_user.full_name} успешно ввёл фамилию: {message.text}")
    await state.update_data(surname=message.text)
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")
    await message.delete()
    await message.bot.edit_message_text(
        "Введите ваш возраст (числом) или нажмите «Пропустить»:",
        chat_id=message.chat.id,
        message_id=prompt_message_id,
        reply_markup=answerSkipAgeButton
    )
    await state.set_state(RegistrationStates.waiting_for_age)


@router_handler.callback_query(F.data == "skipAge", RegistrationStates.waiting_for_age)
async def skip_age(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(age=None)
    data = await state.get_data()
    error_msg_id = data.get("error_age_msg_id")
    logger.debug(f"✅ Пользователь {callback_query.from_user.full_name} успешно пропустил ввод возраста: {data.get('age')=}")
    if error_msg_id:
        await callback_query.bot.delete_message(callback_query.message.chat.id, error_msg_id)

    prompt_message_id = data.get("prompt_message_id")
    await callback_query.bot.edit_message_text(
        "Выберите ваш пол:",
        chat_id=callback_query.message.chat.id,
        message_id=prompt_message_id,
        reply_markup=answerGenderStateButton
    )
    await callback_query.answer()
    await state.set_state(RegistrationStates.waiting_for_gender)


# Обработчик ввода возраста
@router_handler.message(StateFilter(RegistrationStates.waiting_for_age))
async def process_age(message: Message, state: FSMContext):
    data = await state.get_data()
    error_msg_id = None
    if not message.text.isdigit():
        logger.info(f"🆘️ Пользователь {message.from_user.full_name} ввёл некорректный возраст: {message.text}")
        error_msg_id = data.get("error_age_msg_id")
        if error_msg_id:
            await message.bot.delete_message(message.chat.id, error_msg_id)
        error_age_msg = await message.answer("🆘️ Возраст должен быть числом. Пожалуйста, введите ваш возраст:")
        await state.update_data(error_age_msg_id=error_age_msg.message_id)
        await message.delete()
        return

    await state.update_data(age=int(message.text))
    logger.info(f"✅ Пользователь {message.from_user.full_name} успешно ввёл возраст: {message.text}")

    error_msg_id = data.get("error_age_msg_id")
    if error_msg_id:
        await message.bot.delete_message(message.chat.id, error_msg_id)

    prompt_message_id = data.get("prompt_message_id")
    await message.delete()
    await message.bot.edit_message_text(
        "Введите ваш пол:",
        chat_id=message.chat.id,
        message_id=prompt_message_id,
        reply_markup=answerGenderStateButton
    )
    await state.set_state(RegistrationStates.waiting_for_gender)

@router_handler.message(StateFilter(RegistrationStates.waiting_for_gender))
async def process_gender(message: Message):
    logger.info(f"🆘 Пользователь {message.from_user.full_name} отправил сообщение: {message.text} - неизвестная команда")
    await message.delete()
    return


# Обработчик ввода пола и сохранения данных в БД
@router_handler.callback_query(StateFilter(RegistrationStates.waiting_for_gender))
async def process_gender(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    choice = callback_query.data
    gender = None if choice == "skipGender" else choice
    logger.info(f"✅ Пользователь {callback_query.from_user.full_name} успешно ввёл пол: {gender=}")
    await state.update_data(gender=gender)

    # Получаем все данные, введённые пользователем
    data = await state.get_data()

    # Позже сделаю нормальное сохранение в БД
    # # Сохраняем данные в базу данных
    # async with async_session() as session:
    #     async with session.begin():
    #         new_user = Users(
    #             name=data['name'],
    #             surname=data['surname'],
    #             username=data['username'],
    #             age=data.get('age'),
    #             gender=data.get('gender')
    #         )
    #         session.add(new_user)
    #     # При использовании session.begin() commit выполняется автоматически

    prompt_message_id = data.get("prompt_message_id")
    await callback_query.bot.edit_message_text(
        "✅ Регистрация завершена!",
        chat_id=callback_query.message.chat.id,
        message_id=prompt_message_id
    )
    logger.info(f"✅ Пользователь {callback_query.from_user.full_name} успешно зарегистрирован: {data=}")
    await state.clear()


@router_handler.message()
async def echo(message: Message):
    logger.info(f"Пользователь {message.from_user.full_name} отправил сообщение: {message.text} - неизвестная команда")
    await message.answer("Неизвестная команда!")


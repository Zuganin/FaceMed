from aiogram.filters import Command
from aiogram.types import  Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F, types, Router
from aiogram.fsm.context import  FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


from bot.database.database_utils import check_user_registration, register_user
from bot.config import logger


answerSkipAgeButton = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skipAge")]])

answerGenderStateButton = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Мужской", callback_data="мужской"),InlineKeyboardButton(text="Женский", callback_data="женский")],
            [InlineKeyboardButton(text="Пропустить", callback_data="skipGender")]
        ])

registration_router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_age = State()
    waiting_for_gender = State()

@registration_router.message(Command('registration'))
async def cmd_register(message: Message, state: FSMContext):
    """
        Обрабатывает команду /registration. Запускает процесс регистрации пользователя, если он ещё не зарегистрирован.

        :param message: Сообщение от пользователя
        :param state: Контекст FSM состояния
        :return: None
    """
    # Проверяем, зарегистрирован ли пользователь
    user_registration = await check_user_registration(message.from_user.username)
    if user_registration:
        await message.answer("Вы уже зарегистрированы!")
        return
    logger.info(f"Пользователь {message.from_user.full_name} - {message.from_user.username} начал регистрацию")
    prompt_message = await message.answer("Введите ваше имя:")
    await state.update_data(prompt_message_id=prompt_message.message_id)
    await state.set_state(RegistrationStates.waiting_for_name)

@registration_router.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    """
        Обрабатывает ввод имени пользователя и переводит на следующий шаг — ввод фамилии.

        :param message: Сообщение от пользователя
        :param state: Контекст FSM состояния
        :return: None
    """
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

@registration_router.message(StateFilter(RegistrationStates.waiting_for_surname))
async def process_surname(message: Message, state: FSMContext):
    """
        Обрабатывает ввод фамилии пользователя и переводит на шаг ввода возраста.

        :param message: Сообщение от пользователя
        :param state: Контекст FSM состояния
        :return: None
    """
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


@registration_router.callback_query(F.data == "skipAge", RegistrationStates.waiting_for_age)
async def skip_age(callback_query: types.CallbackQuery, state: FSMContext):
    """
        Обрабатывает нажатие на кнопку «Пропустить» при вводе возраста.
        Переходит к шагу выбора пола.

        :param callback_query: Callback от пользователя
        :param state: Контекст FSM состояния
        :return: None
    """
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


@registration_router.message(StateFilter(RegistrationStates.waiting_for_age))
async def process_age(message: Message, state: FSMContext):
    """
        Обрабатывает ввод возраста пользователя. Проверяет корректность ввода (только число).
        Переходит к следующему шагу — выбор пола.

        :param message: Сообщение от пользователя
        :param state: Контекст FSM состояния
        :return: None
    """
    data = await state.get_data()
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

@registration_router.message(StateFilter(RegistrationStates.waiting_for_gender))
async def process_gender(message: Message):
    """
        Обрабатывает текстовые сообщения, отправленные вместо выбора пола.
        Удаляет сообщение и игнорирует его.

        :param message: Сообщение от пользователя
        :return: None
    """
    logger.info(f"🆘 Пользователь {message.from_user.full_name} отправил сообщение: {message.text} - неизвестная команда")
    await message.delete()
    return


@registration_router.callback_query(StateFilter(RegistrationStates.waiting_for_gender))
async def process_gender(callback_query: CallbackQuery, state: FSMContext):
    """
        Обрабатывает выбор пола пользователя и завершает регистрацию. Сохраняет все данные в базу.

        :param callback_query: Callback от пользователя с выбранным полом
        :param state: Контекст FSM состояния
        :return: None
    """
    await callback_query.answer()
    choice = callback_query.data
    gender = None if choice == "skipGender" else choice
    logger.info(f"✅ Пользователь {callback_query.from_user.full_name} успешно ввёл пол: {gender=}")
    await state.update_data(gender=gender)

    data = await state.get_data()

    # Регистрируем пользователя
    await register_user(
        name=data['name'],
        surname=data['surname'],
        username=callback_query.from_user.username,
        age=data.get('age'),
        gender=data.get('gender')
    )

    prompt_message_id = data.get("prompt_message_id")
    await callback_query.bot.edit_message_text(
        "✅ Регистрация завершена!",
        chat_id=callback_query.message.chat.id,
        message_id=prompt_message_id
    )
    logger.info(f"✅ Пользователь {callback_query.from_user.full_name} успешно зарегистрирован: {data=}")
    await state.clear()


import os

from aiogram import types, F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import  FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.config import bot, logger
from bot.database.database_utils import add_user_disease_diagnostic, check_user_registration
from bot.clients.disease_client import client as client_disease
from bot.clients.age_client import client as client_age

#======================================================================================================================#

class UserActions(StatesGroup):
    photos_processing = State()

photoProcessingCommands = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Анализировать возраст", callback_data="analyze_age")],
            [InlineKeyboardButton(text="Провести диагностику", callback_data="diagnose_disease")]
        ])

analyzer_router = Router()

#======================================================================================================================#
@analyzer_router.message(F.photo | F.document)
async def handle_photo(message: types.Message, state: FSMContext):
    """
        Обрабатывает входящее фото от пользователя, сохраняет его локально и предлагает действия.

        :param message: Сообщение с фотографией от пользователя
        :param state: Контекст FSM состояния пользователя
        :return: None
    """
    try:
        # Проверяем, является ли файл фотографией
        if message.photo:
            photo = message.photo[-1]
            file_info = await bot.get_file(photo.file_id)
            photo_path = f"{message.from_user.username}_photo.jpg"
            await bot.download_file(file_info.file_path, photo_path)
            logger.info(f"Пользователь {message.from_user.username} отправил фото {photo_path}")
        # Или если это файл изображения
        elif message.document and message.document.mime_type.startswith('image'):
            file_info = await bot.get_file(message.document.file_id)
            photo_path = f"{message.from_user.username}_{message.document.file_name}"
            await bot.download_file(file_info.file_path, photo_path)
            logger.info(f"Пользователь {message.from_user.username} отправил файл {photo_path}")
        else:
            raise ValueError("Не поддерживаемый тип файла.")

        # Сохраняем путь к фото в состоянии
        await state.update_data(photo_path=photo_path)

        # Устанавливаем состояние
        await state.set_state(UserActions.photos_processing)

        # Предлагаем выбрать действие с помощью инлайн-клавиатуры
        await message.answer("Выбери действие:", reply_markup=photoProcessingCommands)
        logger.info(f"Фото или файл успешно скачано. Пользователь {message.from_user.username} выбирает действие.")
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        await message.reply(f"Ошибка загрузки изображения: {e}")

    #
    # photo_path = f"{message.from_user.username}_photo.jpg"
    # logger.info(f"Пользователь {message.from_user.username} отправил фото {photo_path}")
    # try:
    #     # Скачиваем фото
    #     photo = message.photo[-1]
    #     file_info = await bot.get_file(photo.file_id)
    #     await bot.download_file(file_info.file_path, photo_path)
    #
    #     # Сохраняем путь к фото в состоянии
    #     await state.update_data(photo_path=photo_path)
    #
    #     # Устанавливаем состояние
    #     await state.set_state(UserActions.photos_processing)
    #
    #     # Предлагаем выбрать действие с помощью инлайн-клавиатуры
    #     await message.answer("Выбери действие:", reply_markup=photoProcessingCommands)
    #     logger.info(f"Фото успешно скачано. Пользователь {message.from_user.username} выбирает действие.")
    # except Exception as e:
    #     logger.error(f"Ошибка загрузки фото: {e}")
    #     await message.reply(f"Ошибка загрузки изображения: {e}")



#======================================================================================================================#

# Обработчик выбора действия "Анализировать возраст"
@analyzer_router.callback_query(F.data == "analyze_age", UserActions.photos_processing)
async def analyze_age(callback: types.CallbackQuery, state: FSMContext):
    """
        Обрабатывает запрос пользователя на анализ возраста.
        Запускает сервер, отправляет фото на предсказание и возвращает результат пользователю.

        :param callback: Объект callback-запроса от пользователя
        :param state: Контекст FSM состояния пользователя
        :return: None
    """
    user_data = await state.get_data()
    photo_path = user_data.get("photo_path")
    result_path = f"{callback.from_user.username}_result.jpg"

    if not photo_path:
        logger.error(f"Произошло ошибка при анализе возраста. Возможно фото не было загружено.")
        await callback.message.reply("Сначала отправь фото.")
        return

    try:
        # Обращение к клиентскому сервису
        results = client_age.get_predict(photo_path)
        annotated_photo = results.image

        logger.info(f"Пользователь {callback.from_user.username} успешно отправил фото на диагностику.")

        # Отправка результата
        await callback.message.answer_photo(
            photo=BufferedInputFile(annotated_photo, filename=result_path),
            caption=results.report
        )

        logger.info(f"✅ Пользователь {callback.from_user.username} успешно прошел анализ возраста.")

    except Exception as e:
        logger.error(f"🆘 Произошла ошибка при анализе возраста: {e}")
        await callback.message.reply(f"Ошибка анализа изображения: {e}")

    finally:
        # Удаляем временные файлы
        if os.path.exists(photo_path):
            os.remove(photo_path)
        if os.path.exists(result_path):
            os.remove(result_path)

        # Сбрасываем состояние
        await state.clear()
        logger.debug(f"Состояние пользователя {callback.from_user.username} успешно сброшено.")



#======================================================================================================================#

@analyzer_router.callback_query(F.data == "diagnose_disease", UserActions.photos_processing)
async def diagnose_disease(callback: types.CallbackQuery, state: FSMContext):
    """
        Обрабатывает запрос пользователя на диагностику заболевания.
        Запускает соответствующий сервер, получает диагноз и сохраняет результат в базу данных.

        :param callback: Объект callback-запроса от пользователя
        :param state: Контекст FSM состояния пользователя
        :return: None
    """
    user_data = await state.get_data()
    photo_path = user_data.get("photo_path")
    result_path = f"{callback.from_user.username}_diagnosis_result.jpg"

    if not photo_path:
        logger.error(f"Произошло ошибка при анализе лица. Возможно фото не было загружено.")
        await callback.message.reply("Сначала отправьте фото.")
        return

    try:
        # Обращение к клиентскому сервису

        results = client_disease.get_predict(photo_path)
        annotated_photo = results.image

        logger.info(f"Пользователь {callback.from_user.username} успешно отправил фото на диагностику.")

    

        # Загрузка результата в базу данных
        if check_user_registration(callback.from_user.username):
            await add_user_disease_diagnostic(callback.from_user.username, result_path, annotated_photo, results.disease)

        # Отправка результата
        await callback.message.answer_photo(
            photo=BufferedInputFile(annotated_photo, filename=result_path),
            caption=results.report
        )
        logger.info(f"Пользователь {callback.from_user.username} успешно прошел диагностику.")

    except Exception as e:
        logger.error(f"Произошла ошибка при диагностике: {e}")
        await callback.message.answer(f"Ошибка диагностики: {str(e)}")

    finally:
        # Очистка временных файлов
        for path in [photo_path, result_path]:
            if os.path.exists(path):
                os.remove(path)
        await state.clear()
        logger.debug(f"Состояние пользователя {callback.from_user.username} успешно сброшено.")
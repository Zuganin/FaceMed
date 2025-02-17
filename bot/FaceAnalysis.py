import io
import threading

from deepface import DeepFace
from aiogram import types, F
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import  FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router
import cv2
import os


from bot.config import bot, logger
from microservices.predict.services.server import Server, run_server
from microservices.predict.client.client import get_predict


class UserActions(StatesGroup):
    photos_processing = State()


router_analyzer = Router()

photoProcessingCommands = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Анализировать возраст", callback_data="analyze_age")],
            [InlineKeyboardButton(text="Провести диагностику", callback_data="diagnose_disease")]
        ])

#======================================================================================================================#
@router_analyzer.message(F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    photo_path = f"{message.from_user.id}_photo.jpg"
    logger.info(f"Пользователь {message.from_user.id} отправил фото {photo_path}")
    try:
        # Скачиваем фото
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        await bot.download_file(file_info.file_path, photo_path)

        # Сохраняем путь к фото в состоянии
        await state.update_data( photo_path=photo_path)

        # Устанавливаем состояние
        await state.set_state(UserActions.photos_processing)

        # Предлагаем выбрать действие с помощью инлайн-клавиатуры
        await message.answer("Выбери действие:", reply_markup=photoProcessingCommands)
        logger.info(f"Фото успешно скачано. Пользователь {message.from_user.id} выбирает действие.")
    except Exception as e:
        logger.error(f"Ошибка загрузки фото: {e}")
        await message.reply(f"Ошибка загрузки изображения: {e}")



#======================================================================================================================#

# Обработчик выбора действия "Анализировать возраст"
@router_analyzer.callback_query(F.data == "analyze_age", UserActions.photos_processing)
async def analyze_age(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    photo_path = user_data.get("photo_path")

    if not photo_path:
        logger.error(f"Произошло ошибка при анализе возраста. Возможно фото не было загружено.")
        await callback.message.reply("Сначала отправь фото.")
        return

    try:
        # Анализ возраста и пола через DeepFace
        analysis = DeepFace.analyze(img_path=photo_path, actions=['age', 'gender'])

        # Получаем данные анализа
        age = analysis[0]['age']
        gender = analysis[0]['gender']

        age_range = f"{age - 2}–{age + 2}"

        gender_translation = {"Woman": "Женщина", "Man": "Мужчина"}
        dominant_gender = max(gender, key=gender.get)

        # Читаем изображение с помощью OpenCV
        img = cv2.imread(photo_path)

        # Рисуем квадрат на лице
        if 'region' in analysis[0]:
            face_location = analysis[0]['region']
            x, y, w, h = face_location['x'], face_location['y'], face_location['w'], face_location['h']
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Сохраняем обработанное фото
        result_path = f"{callback.from_user.id}_result.jpg"
        cv2.imwrite(result_path, img)

        # Отправляем результат пользователю
        caption = f"Возможный возраст: {age_range}\nВозможный пол: {gender_translation[dominant_gender]} ({round(gender[dominant_gender],2)}%)"
        await callback.message.answer_photo(photo=FSInputFile(result_path), caption=caption)
        logger.info(f"Пользователь {callback.from_user.id} успешно прошел анализ возраста.")

    except Exception as e:
        logger.error(f"Произошла ошибка при анализе возраста: {e}")
        await callback.message.reply(f"Ошибка анализа изображения: {e}")

    finally:
        # Удаляем временные файлы
        if os.path.exists(photo_path):
            os.remove(photo_path)
        if os.path.exists(result_path):
            os.remove(result_path)

        # Сбрасываем состояние
        await state.clear()
        logger.debug(f"Состояние пользователя {callback.from_user.id} успешно сброшено.")



#======================================================================================================================#

@router_analyzer.callback_query(F.data == "diagnose_disease", UserActions.photos_processing)
async def diagnose_disease(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    photo_path = user_data.get("photo_path")
    result_path = f"{callback.from_user.id}_diagnosis_result.jpg"

    if not photo_path:
        logger.error(f"Произошло ошибка при анализе возраста. Возможно фото не было загружено.")
        await callback.message.reply("Сначала отправьте фото.")
        return

    try:
        # Обращение к клиентскому сервису
        server_instance = Server()
        server_thread = threading.Thread(target=run_server, args=(server_instance,), daemon=True)
        server_thread.start()
        results = get_predict(photo_path)
        annotated_photo = results.image

        logger.info(f"Пользователь {callback.from_user.id} успешно отправил фото на диагностику.")

        server_instance.stop()

        # Отправка результата
        await callback.message.answer_photo(
            photo=BufferedInputFile(annotated_photo, filename=result_path),
            caption=results.report
        )
        logger.info(f"Пользователь {callback.from_user.id} успешно прошел диагностику.")

    except Exception as e:
        logger.error(f"Произошла ошибка при диагностике: {e}")
        await callback.message.answer(f"Ошибка диагностики: {str(e)}")

    finally:
        # Очистка временных файлов
        for path in [photo_path, result_path]:
            if os.path.exists(path):
                os.remove(path)
        await state.clear()
        logger.debug(f"Состояние пользователя {callback.from_user.id} успешно сброшено.")
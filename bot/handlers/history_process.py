import io

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile, \
    InputFile
from aiogram import F, types, Router
from aiogram.fsm.context import  FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database_utils import check_user_registration, get_paginated_diagnostics, get_total_diagnostics_count
from bot.config import logger



history_router = Router()


class HistoryProcessStates(StatesGroup):
    waiting_for_choiсe_analysis = State()

#======================================================================================================================#

def GetHistory(message : Message, username):
    """
        Получает историю диагностики пользователя, если он зарегистрирован.

        :param message: Объект сообщения от пользователя
        :param username: Имя пользователя Telegram
        :return: Список диагностик или None, если пользователь не зарегистрирован
    """
    if check_user_registration(username):
        return get_paginated_diagnostics(username)
    else:
        logger.error(f"🆘 Ошибка: Пользователь {username} не зарегистрирован.")
        message.answer("Вы не зарегистрированы. История доступна только зарегистрированным пользователям.")
        return

def get_diagnostics_keyboard(diagnostics, page, per_page=5, total_diagnostics=0):
    """
        Создает inline-клавиатуру для отображения списка диагностик с пагинацией.

        :param diagnostics: Список диагностик для текущей страницы
        :param page: Номер текущей страницы
        :param per_page: Количество элементов на одной странице
        :param total_diagnostics: Общее количество диагностик пользователя
        :return: Объект InlineKeyboardMarkup с кнопками для выбора анализа и навигации
    """

    keyboard = []
    for diag in diagnostics:
        btn = InlineKeyboardButton(text=diag["date"].strftime("%Y-%m-%d %H:%M"), callback_data=f"diag_{diag['id']}")

        # Каждая кнопка в отдельной строке
        keyboard.append([btn])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅ Назад", callback_data=f"page_{page - 1}"))
    if (page + 1) * per_page < total_diagnostics:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡", callback_data=f"page_{page + 1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@history_router.message(Command("get_history"))
async def GetUserChoice(message: Message, state: FSMContext):
    """
        Обрабатывает команду /get_history. Загружает список диагностик пользователя и отображает их с пагинацией.

        :param message: Объект сообщения от пользователя
        :param state: Контекст состояния пользователя в FSM
        :return: None
    """

    username = message.from_user.username
    diagnostics = await get_paginated_diagnostics(username, page=0)
    if diagnostics:
        # Преобразуем каждый объект в словарь, чтобы избежать DetachedInstanceError
        diagnostics_data = [
            {"id": diag["id"], "filename": diag["filename"], "diagnosis": diag["diagnosis"], "date" : diag["date"], "file_bin" : diag["file_bin"]}
            for diag in diagnostics
        ]

        await state.update_data(diagnostics=diagnostics_data, current_page=0)
        total_diagnostics = await get_total_diagnostics_count(username)
        keyboard = get_diagnostics_keyboard(diagnostics_data, page=0, per_page=5, total_diagnostics=total_diagnostics)
        await message.answer("Выберите анализ:", reply_markup=keyboard)
        await state.set_state(HistoryProcessStates.waiting_for_choiсe_analysis)
    else:
        await message.answer("У вас пока нет диагностик.")



@history_router.callback_query(lambda c: c.data.startswith("diag_"))
async def show_diagnostic_result(callback: CallbackQuery, state: FSMContext):
    """
        Обрабатывает нажатие на кнопку с конкретной диагностикой. Показывает изображение и диагноз.

        :param callback: Callback-запрос от пользователя
        :param state: Контекст состояния FSM
        :return: None
    """

    diag_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    diagnostics = data.get("diagnostics", [])

    # Поиск нужной диагностики по id
    diagnostic = next((diag for diag in diagnostics if diag.get("id") == diag_id), None)
    if diagnostic:
        # Преобразуем бинарное изображение в поток байтов
        photo_stream = io.BytesIO(diagnostic["file_bin"])
        photo_stream.seek(0)

        # Используем BufferedInputFile вместо InputFile
        photo_file = BufferedInputFile(photo_stream.read(), filename=diagnostic["filename"])
        result_text = f"📋 **Диагноз:** {diagnostic.get('diagnosis')}"
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo_file,
            caption = result_text
        )
    else:
        await callback.answer("Анализ не найден.")




@history_router.callback_query(lambda c: c.data.startswith("page_"))
async def change_page(callback: CallbackQuery):
    """
        Обрабатывает переключение страниц с диагностиками.

        :param callback: Callback-запрос от пользователя
        :param state: Контекст состояния FSM
        :return: None
    """
    page = int(callback.data.split("_")[1])
    username = callback.from_user.username
    diagnostics, total_diagnostics = await get_paginated_diagnostics(username, page=page), await get_total_diagnostics_count(username)
    if diagnostics:
        keyboard = get_diagnostics_keyboard(
            diagnostics, page, per_page=5, total_diagnostics=total_diagnostics
        )
        await callback.message.edit_text("Выберите анализ:", reply_markup=keyboard)
    else:
        await callback.answer("Нет данных для этой страницы.")





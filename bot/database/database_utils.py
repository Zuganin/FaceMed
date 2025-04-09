from sqlalchemy.future import select


from bot.database.engine import session_maker
from bot.database.models import Users, Diagnostics
from bot.config import logger

# Функция для проверки, зарегистрирован ли пользователь в базе данных
async def check_user_registration(username: str) -> bool:
    """
        Проверяет, зарегистрирован ли пользователь в базе данных.

        :param username: Имя пользователя для проверки
        :return: Объект пользователя, если найден, иначе False
    """
    async with session_maker() as session:
        try:
            # Строим запрос для поиска пользователя по имени
            stmt = select(Users).where(Users.username == username)
            result = await session.execute(stmt)

            # Возвращаем первого найденного пользователя или None, если не найден
            return result.scalars().first()
        except Exception as e:
            logger.error(f"🆘 Ошибка при проверке пользователя: {e}")
            return False

async def register_user(name: str, surname: str,username: str, age: int, gender: str) -> None:
    """
        Регистрирует нового пользователя в базе данных.

        :param name: Имя пользователя
        :param surname: Фамилия пользователя
        :param username: Уникальное имя пользователя (username)
        :param age: Возраст пользователя
        :param gender: Пол пользователя
        :return: None
    """
    async with session_maker() as session:
        try:
            async with session.begin():
                new_user = Users(name=name, surname=surname, username=username, age=age, gender= gender)
                session.add(new_user)
            logger.debug("✅ Данные успешно загружены в базу")
        except Exception as e:
            logger.error(f"🆘 Ошибка при регистрации пользователя: {e}")
            return


async def add_user_disease_diagnostic(username: str, filename: str, image: bytes, diagnosis: str) -> None:
    """
        Добавляет информацию о диагностике пользователя в базу данных.

        :param username: Имя пользователя
        :param filename: Имя файла изображения
        :param image: Изображение в формате байтов
        :param diagnosis: Текст диагноза
        :return: None
    """
    async with session_maker() as session:
        try:
            async with session.begin():
                new_diagnostic = Diagnostics(user_name=username, filename=filename, image=image, diagnosis=diagnosis)
                session.add(new_diagnostic)
            logger.debug("✅ Данные успешно загружены в базу")
        except Exception as e:
            logger.error(f"🆘 Ошибка при добавлении диагностики: {e}")
            return


async def get_paginated_diagnostics(username: str, page=0, per_page=5):
    """
        Получает список диагностик пользователя с пагинацией.

        :param username: Имя пользователя
        :param page: Номер страницы (по умолчанию 0)
        :param per_page: Количество записей на странице (по умолчанию 5)
        :return: Список словарей с диагностической информацией
    """
    async with session_maker() as session:
        try:
            async with session.begin():
                stmt = (
                    select(Diagnostics)
                    .filter(Diagnostics.user_name == username)
                    .order_by(Diagnostics.id.desc())
                    .limit(per_page)
                    .offset(page * per_page)
                )
                result = await session.execute(stmt)
                diagnostics = result.scalars().all()
                # Преобразуем объекты в словари, чтобы избежать DetachedInstanceError
                diagnostics_data = [
                    {"id": diag.id, "filename": diag.filename, "diagnosis": diag.diagnosis, "date" : diag.created, "file_bin" : diag.image }
                    for diag in diagnostics
                ]
                logger.debug("✅ Данные успешно загружены из базы")
                return diagnostics_data
        except Exception as e:
            logger.error(f"🆘 Ошибка при получении диагностик: {e}")
            return []


async def get_total_diagnostics_count( username):
    """
        Получает общее количество диагностик для указанного пользователя.

        :param username: Имя пользователя
        :return: Количество диагностик (int) или None в случае ошибки
    """
    async with session_maker() as session:
        try:
            async with session.begin():
                result = await session.execute(
                    select(Diagnostics).filter(Diagnostics.user_name == username)
                )
                count_diagnostics = len(result.scalars().all())
                logger.debug("✅ Данные о количестве диагностик успешно загружены из базы")
                return int(count_diagnostics)
        except Exception as e:
            logger.error(f"🆘 Ошибка при получении количества диагностик: {e}")
            return

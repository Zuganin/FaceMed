from sqlalchemy.future import select
from tensorboard.plugins.image.summary_v2 import image

from database.engine import session_maker
from database.models import Users, Diagnostics
from bot.config import logger

async def check_user_registration(username: str) -> bool:
    async with session_maker() as session:
        try:
            stmt = select(Users).where(Users.username == username)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"🆘 Ошибка при проверке пользователя: {e}")
            return False

async def register_user(name: str, surname: str,username: str, age: int, gender: str) -> None:
    # Сохраняем данные в базу данных
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

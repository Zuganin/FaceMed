from sqlalchemy.future import select

from database.engine import session_maker
from database.models import Users
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
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession


from bot.config import DB_URL
from database.models import Base

# Создаем асинхронный движок SQLAlchemy с указанием URL базы данных
engine = create_async_engine(url = DB_URL, echo=True)

# Создаем фабрику сессий, которая будет использовать асинхронный движок
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True)

# Функция для создания базы данных (создает все таблицы на основе моделей)
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция для удаления базы данных (удаляет все таблицы)
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)





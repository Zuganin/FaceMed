from sqlalchemy import Integer, String, MetaData, ForeignKey, LargeBinary, func, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata = MetaData()

class Base(DeclarativeBase):
    # Добавляем поле для отслеживания времени создания записи
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

class Users(Base):
    __tablename__ = "users"


    # Определяем поля таблицы "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    surname: Mapped[str] = mapped_column(String(256), nullable=False)
    username: Mapped[str] = mapped_column(String(256),unique=True, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(256), nullable=True)

class Diagnostics(Base):
    __tablename__ = "diagnostics"

    # Определяем поля таблицы "diagnostics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String(256), ForeignKey("users.username"), nullable=False)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    image: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)


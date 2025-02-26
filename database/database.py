from bot.config import DB_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(url = DB_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://verali_user:verali_password@postgres:5432/verali_db")

# Проверка на пустое значение или только пробелы
if not DATABASE_URL or not DATABASE_URL.strip():
    raise ValueError(
        "DATABASE_URL не установлен или пуст! "
        "Установите переменную DATABASE_URL в Railway: "
        "${{Postgres.DATABASE_URL}} или ${{PostgreSQL.DATABASE_URL}}"
    )

# Удаляем пробелы в начале и конце
DATABASE_URL = DATABASE_URL.strip()

# Railway использует postgres://, но SQLAlchemy требует postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InstagramProfile(Base):
    """Модель для хранения данных Instagram профиля"""
    __tablename__ = "instagram_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    screenshot_path = Column(String, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Инициализация базы данных - создание таблиц"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


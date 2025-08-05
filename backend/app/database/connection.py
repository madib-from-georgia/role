"""
Подключение к базе данных SQLite.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine
import sqlite3
from contextlib import contextmanager
from typing import Generator

from app.config.settings import settings


# Включение внешних ключей для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Включает foreign keys для SQLite."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Создание engine и session
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Для SQLite
    echo=settings.debug  # Логирование SQL запросов в debug режиме
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии базы данных.
    Используется в FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager для получения сессии базы данных.
    Используется в сервисах.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db():
    """Инициализация базы данных."""
    # Импорт всех моделей в правильном порядке для избежания circular imports
    from app.database.models import base  # Сначала базовая модель
    from app.database.models import user   # Базовые модели пользователей
    from app.database.models import token  # Токены пользователей  
    from app.database.models import project  # Проекты
    from app.database.models import text   # Тексты
    from app.database.models import character  # Персонажи
    from app.database.models import checklist  # Чеклисты
    
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)
    
    print("✅ База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных."""
    engine.dispose()
    print("✅ Соединение с базой данных закрыто")


def check_db_connection() -> bool:
    """Проверка соединения с базой данных."""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

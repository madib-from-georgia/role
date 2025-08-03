"""
Конфигурация тестов pytest.
"""

import pytest
import asyncio
from pathlib import Path
import sys
import os

# Добавляем корневую директорию backend в Python path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# Устанавливаем переменные окружения для тестов
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "true"


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Настройки для тестов."""
    from app.config.settings import settings
    
    # Переопределяем настройки для тестов
    original_db_url = settings.database_url
    original_upload_dir = settings.upload_dir
    
    settings.database_url = "sqlite:///:memory:"
    settings.upload_dir = "./test_uploads"
    settings.debug = True
    
    yield settings
    
    # Восстанавливаем оригинальные настройки
    settings.database_url = original_db_url
    settings.upload_dir = original_upload_dir


@pytest.fixture
async def test_db():
    """Тестовая база данных."""
    from app.database.connection import engine, Base
    from app.database.models import user, project, text, character, checklist, token
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Очищаем после тестов
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Фикстура для сессии базы данных."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database.connection import Base
    from app.database.models import user, project, text, character, checklist, token
    
    # Создаем отдельный engine для тестов с правильными настройками SQLite
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},  # Важно для тестов!
        echo=False  # Убираем логи для тестов
    )
    
    # Создаем фабрику сессий для тестов
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Создаем таблицы для каждого теста
    Base.metadata.create_all(bind=test_engine)
    
    # Создаем сессию
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Очищаем таблицы после каждого теста
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_user_data():
    """Образец данных пользователя для тестов."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_project_data():
    """Образец данных проекта для тестов."""
    return {
        "title": "Test Project",
        "description": "Test project description"
    }


@pytest.fixture
def sample_text_data():
    """Образец данных текста для тестов."""
    return {
        "filename": "test.txt",
        "original_format": "txt",
        "content": "Sample text content for testing",
        "file_metadata": {"author": "Test Author", "title": "Test Work"}
    }


@pytest.fixture
def sample_character_data():
    """Образец данных персонажа для тестов."""
    return {
        "name": "Test Character",
        "aliases": ["Главный герой", "ГГ"],
        "importance_score": 0.8,
        "speech_attribution": {"total_words": 1500, "dialogue_count": 25}
    }


@pytest.fixture
def test_client():
    """Тестовый клиент FastAPI."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as client:
        yield client


# Хелперы для тестов
class TestHelpers:
    """Вспомогательные функции для тестов."""
    
    @staticmethod
    def create_test_user_data():
        """Создает тестовые данные пользователя."""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    
    @staticmethod
    def create_test_project_data():
        """Создает тестовые данные проекта."""
        return {
            "title": "Тестовый проект",
            "description": "Описание тестового проекта"
        }
    
    @staticmethod
    def create_test_text_data():
        """Создает тестовые данные текста."""
        return {
            "filename": "test_book.txt",
            "original_format": "txt",
            "content": "Тестовое содержимое книги.",
            "metadata": {"author": "Тестовый автор", "title": "Тестовая книга"}
        }


@pytest.fixture
def test_helpers():
    """Фикстура с хелперами."""
    return TestHelpers

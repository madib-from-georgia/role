"""
Настройки приложения.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения с валидацией."""
    
    # Основные настройки
    app_name: str = "Анализ Персонажей"
    debug: bool = False
    version: str = "1.0.0"
    
    # Авторизация
    auth_enabled: bool = True  # Флаг для включения/отключения авторизации
    
    # База данных
    database_url: str = "sqlite:///./database.db"
    
    # JWT
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Безопасность
    bcrypt_rounds: int = 12
    rate_limit_per_minute: int = 100
    
    # Файлы
    upload_dir: str = "./uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = ["txt", "pdf", "fb2", "epub"]
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # NLP настройки
    nlp_model_path: str = "./models"
    nlp_timeout_seconds: int = 300
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Игнорировать дополнительные поля
    }


# Глобальный экземпляр настроек
settings = Settings()

# Создание необходимых директорий
def create_directories():
    """Создает необходимые директории."""
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(exist_ok=True)
    
    models_path = Path(settings.nlp_model_path)
    models_path.mkdir(exist_ok=True)
    
    logs_path = Path("./logs")
    logs_path.mkdir(exist_ok=True)


# Создание директорий при импорте
create_directories()

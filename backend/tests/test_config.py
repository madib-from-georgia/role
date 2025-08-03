"""
Тесты конфигурации приложения.
"""

import pytest
import os
from pathlib import Path
from app.config.settings import Settings, settings, create_directories


class TestSettings:
    """Тесты настроек приложения."""
    
    def test_settings_instance(self):
        """Проверяет создание экземпляра настроек."""
        assert settings is not None
        assert isinstance(settings, Settings)
    
    def test_default_values(self):
        """Проверяет значения по умолчанию."""
        test_settings = Settings()
        
        assert test_settings.app_name == "Анализ Персонажей"
        assert test_settings.debug is False
        assert test_settings.version == "1.0.0"
        assert test_settings.jwt_algorithm == "HS256"
        assert test_settings.access_token_expire_minutes == 15
        assert test_settings.refresh_token_expire_days == 7
        assert test_settings.bcrypt_rounds == 12
        assert test_settings.rate_limit_per_minute == 100
    
    def test_database_url_format(self):
        """Проверяет формат URL базы данных."""
        assert settings.database_url.startswith("sqlite:///")
    
    def test_file_settings(self):
        """Проверяет настройки файлов."""
        assert settings.max_file_size > 0
        assert isinstance(settings.allowed_extensions, list)
        assert len(settings.allowed_extensions) > 0
        
        # Проверяем ожидаемые форматы
        expected_formats = ["txt", "pdf", "fb2", "epub"]
        for fmt in expected_formats:
            assert fmt in settings.allowed_extensions
    
    def test_cors_origins(self):
        """Проверяет настройки CORS."""
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) > 0
        
        # Проверяем наличие localhost адресов
        localhost_found = any("localhost" in origin for origin in settings.cors_origins)
        assert localhost_found, "Должен быть настроен localhost для разработки"
    
    def test_security_settings(self):
        """Проверяет настройки безопасности."""
        assert len(settings.jwt_secret_key) > 10
        assert settings.bcrypt_rounds >= 10
        assert settings.access_token_expire_minutes > 0
        assert settings.refresh_token_expire_days > 0


class TestEnvironmentVariables:
    """Тесты переменных окружения."""
    
    def test_env_override(self):
        """Проверяет переопределение настроек через env переменные."""
        # Создаем новый экземпляр с переменными окружения
        os.environ["APP_NAME"] = "Test App"
        os.environ["DEBUG"] = "true"
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
        
        test_settings = Settings()
        
        assert test_settings.app_name == "Test App"
        assert test_settings.debug is True
        assert test_settings.access_token_expire_minutes == 30
        
        # Очищаем переменные окружения
        del os.environ["APP_NAME"]
        del os.environ["DEBUG"] 
        del os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
    
    def test_case_insensitive_env(self):
        """Проверяет нечувствительность к регистру env переменных."""
        os.environ["debug"] = "true"  # lowercase
        test_settings = Settings()
        assert test_settings.debug is True
        del os.environ["debug"]
    
    def test_jwt_secret_validation(self):
        """Проверяет валидацию JWT секрета."""
        # Секрет не должен быть пустым
        assert settings.jwt_secret_key != ""
        assert len(settings.jwt_secret_key.strip()) > 0
        
        # В production не должен быть дефолтный ключ
        if not settings.debug:
            assert "change-in-production" not in settings.jwt_secret_key.lower()


class TestDirectoryCreation:
    """Тесты создания директорий."""
    
    def test_create_directories_function(self):
        """Проверяет функцию создания директорий."""
        # Вызываем функцию
        create_directories()
        
        # Проверяем, что директории созданы
        upload_path = Path(settings.upload_dir)
        assert upload_path.exists(), "Директория uploads должна быть создана"
        assert upload_path.is_dir(), "uploads должен быть директорией"
        
        models_path = Path(settings.nlp_model_path)
        assert models_path.exists(), "Директория models должна быть создана"
        assert models_path.is_dir(), "models должен быть директорией"
        
        logs_path = Path("./logs")
        assert logs_path.exists(), "Директория logs должна быть создана"
        assert logs_path.is_dir(), "logs должен быть директорией"
    
    def test_directories_created_on_import(self):
        """Проверяет, что директории создаются при импорте модуля."""
        # Директории должны уже существовать после импорта settings
        upload_path = Path(settings.upload_dir)
        assert upload_path.exists(), "Директория uploads должна существовать после импорта"


class TestSettingsValidation:
    """Тесты валидации настроек."""
    
    def test_numeric_settings_validation(self):
        """Проверяет валидацию числовых настроек."""
        assert isinstance(settings.access_token_expire_minutes, int)
        assert isinstance(settings.refresh_token_expire_days, int)
        assert isinstance(settings.bcrypt_rounds, int)
        assert isinstance(settings.rate_limit_per_minute, int)
        assert isinstance(settings.max_file_size, int)
        
        # Проверяем разумные диапазоны
        assert 1 <= settings.access_token_expire_minutes <= 1440  # 1 минута - 24 часа
        assert 1 <= settings.refresh_token_expire_days <= 365     # 1 день - 1 год
        assert 4 <= settings.bcrypt_rounds <= 20                  # Разумные значения bcrypt
        assert settings.max_file_size > 1024                      # Минимум 1KB
    
    def test_string_settings_not_empty(self):
        """Проверяет, что строковые настройки не пустые."""
        string_settings = [
            "app_name",
            "database_url", 
            "jwt_secret_key",
            "jwt_algorithm",
            "upload_dir",
            "nlp_model_path"
        ]
        
        for setting_name in string_settings:
            value = getattr(settings, setting_name)
            assert isinstance(value, str), f"{setting_name} должен быть строкой"
            assert len(value.strip()) > 0, f"{setting_name} не должен быть пустым"
    
    def test_list_settings_validation(self):
        """Проверяет валидацию списковых настроек."""
        assert isinstance(settings.allowed_extensions, list)
        assert len(settings.allowed_extensions) > 0
        assert all(isinstance(ext, str) for ext in settings.allowed_extensions)
        
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) > 0
        assert all(isinstance(origin, str) for origin in settings.cors_origins)
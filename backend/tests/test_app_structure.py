"""
Тесты для проверки структуры приложения.
"""

import pytest
from pathlib import Path
import importlib.util


class TestAppStructure:
    """Тесты структуры backend приложения."""
    
    def test_main_module_exists(self):
        """Проверяет существование главного модуля."""
        main_path = Path("app/main.py")
        assert main_path.exists(), "Файл app/main.py должен существовать"
    
    def test_config_module_exists(self):
        """Проверяет существование модуля конфигурации."""
        config_path = Path("app/config/settings.py")
        assert config_path.exists(), "Файл app/config/settings.py должен существовать"
    
    def test_database_modules_exist(self):
        """Проверяет существование модулей базы данных."""
        db_files = [
            "app/database/connection.py",
            "app/database/models/user.py",
            "app/database/models/project.py",
            "app/database/models/text.py",
            "app/database/models/character.py",
            "app/database/models/checklist.py",
            "app/database/models/token.py",
        ]
        
        for file_path in db_files:
            assert Path(file_path).exists(), f"Файл {file_path} должен существовать"
    
    def test_router_modules_exist(self):
        """Проверяет существование роутеров."""
        router_files = [
            "app/routers/auth.py",
            "app/routers/projects.py",
            "app/routers/texts.py",
            "app/routers/characters.py",
            "app/routers/checklists.py",
        ]
        
        for file_path in router_files:
            assert Path(file_path).exists(), f"Файл {file_path} должен существовать"
    
    def test_middleware_modules_exist(self):
        """Проверяет существование middleware."""
        middleware_files = [
            "app/middleware/auth_middleware.py",
        ]
        
        for file_path in middleware_files:
            assert Path(file_path).exists(), f"Файл {file_path} должен существовать"
    
    def test_requirements_file_exists(self):
        """Проверяет существование файла зависимостей."""
        requirements_path = Path("requirements.txt")
        assert requirements_path.exists(), "Файл requirements.txt должен существовать"
    
    def test_env_example_exists(self):
        """Проверяет существование примера переменных окружения."""
        env_example_path = Path("env.example")
        assert env_example_path.exists(), "Файл env.example должен существовать"


class TestModuleImports:
    """Тесты импорта модулей."""
    
    def test_can_import_main(self):
        """Проверяет возможность импорта главного модуля."""
        try:
            from app.main import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать app.main: {e}")
    
    def test_can_import_settings(self):
        """Проверяет возможность импорта настроек."""
        try:
            from app.config.settings import settings
            assert settings is not None
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать настройки: {e}")
    
    def test_can_import_database_connection(self):
        """Проверяет возможность импорта подключения к БД."""
        try:
            from app.database.connection import get_db, Base
            assert get_db is not None
            assert Base is not None
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать database.connection: {e}")
    
    def test_can_import_models(self):
        """Проверяет возможность импорта моделей."""
        models = [
            "app.database.models.user",
            "app.database.models.project", 
            "app.database.models.text",
            "app.database.models.character",
            "app.database.models.checklist",
            "app.database.models.token",
        ]
        
        for model_name in models:
            try:
                importlib.import_module(model_name)
            except ImportError as e:
                pytest.fail(f"Не удалось импортировать {model_name}: {e}")
    
    def test_can_import_routers(self):
        """Проверяет возможность импорта роутеров."""
        routers = [
            "app.routers.auth",
            "app.routers.projects",
            "app.routers.texts", 
            "app.routers.characters",
            "app.routers.checklists",
        ]
        
        for router_name in routers:
            try:
                router_module = importlib.import_module(router_name)
                assert hasattr(router_module, 'router'), f"{router_name} должен иметь атрибут 'router'"
            except ImportError as e:
                pytest.fail(f"Не удалось импортировать {router_name}: {e}")


class TestAppConfiguration:
    """Тесты конфигурации приложения."""
    
    def test_settings_has_required_attributes(self):
        """Проверяет наличие обязательных атрибутов в настройках."""
        from app.config.settings import settings
        
        required_attributes = [
            "app_name",
            "database_url",
            "jwt_secret_key",
            "jwt_algorithm",
            "access_token_expire_minutes",
            "bcrypt_rounds",
            "upload_dir",
            "max_file_size",
            "allowed_extensions",
        ]
        
        for attr in required_attributes:
            assert hasattr(settings, attr), f"settings должен иметь атрибут {attr}"
            assert getattr(settings, attr) is not None, f"settings.{attr} не должен быть None"
    
    def test_settings_types(self):
        """Проверяет типы настроек."""
        from app.config.settings import settings
        
        assert isinstance(settings.app_name, str)
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.jwt_secret_key, str)
        assert isinstance(settings.access_token_expire_minutes, int)
        assert isinstance(settings.bcrypt_rounds, int)
        assert isinstance(settings.max_file_size, int)
        assert isinstance(settings.allowed_extensions, list)
        assert isinstance(settings.cors_origins, list)


class TestDatabaseModels:
    """Тесты моделей базы данных."""
    
    def test_models_have_tablename(self):
        """Проверяет наличие __tablename__ у моделей."""
        from app.database.models.user import User
        from app.database.models.project import Project
        from app.database.models.text import Text
        from app.database.models.character import Character
        from app.database.models.checklist import ChecklistResponse
        from app.database.models.token import UserToken
        
        models = [User, Project, Text, Character, ChecklistResponse, UserToken]
        
        for model in models:
            assert hasattr(model, '__tablename__'), f"{model.__name__} должна иметь __tablename__"
            assert isinstance(model.__tablename__, str), f"__tablename__ должен быть строкой"
    
    def test_models_inherit_from_base(self):
        """Проверяет наследование от BaseModel."""
        from app.database.models.base import BaseModel
        from app.database.models.user import User
        from app.database.models.project import Project
        
        assert issubclass(User, BaseModel)
        assert issubclass(Project, BaseModel)
    
    def test_models_have_id_field(self):
        """Проверяет наличие поля id у моделей."""
        from app.database.models.user import User
        from app.database.models.project import Project
        
        assert hasattr(User, 'id')
        assert hasattr(Project, 'id')
    
    def test_user_model_fields(self):
        """Проверяет поля модели User."""
        from app.database.models.user import User
        
        required_fields = ['email', 'username', 'password_hash', 'is_active']
        
        for field in required_fields:
            assert hasattr(User, field), f"User должен иметь поле {field}"
"""
Тесты Pydantic схем.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta

from app.schemas.user import UserCreate, UserUpdate, User
from app.schemas.project import ProjectCreate, ProjectUpdate, Project
from app.schemas.text import TextCreate, TextUpdate, Text
from app.schemas.character import CharacterCreate, CharacterUpdate, Character
from app.schemas.checklist import ChecklistResponseCreate, ChecklistResponseUpdate, ChecklistResponse
from app.schemas.token import TokenCreate, TokenUpdate, TokenResponse


class TestUserSchemas:
    """Тесты схем пользователя."""
    
    def test_user_create_valid(self):
        """Тест валидной схемы создания пользователя."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        user_schema = UserCreate(**user_data)
        
        assert user_schema.email == "test@example.com"
        assert user_schema.username == "testuser"
        assert user_schema.password == "testpassword123"
        assert user_schema.full_name == "Test User"
        assert user_schema.is_active == True  # default value
    
    def test_user_create_invalid_email(self):
        """Тест невалидного email."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="invalid-email",
                username="testuser",
                password="testpassword123"
            )
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_user_create_short_username(self):
        """Тест короткого username."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                username="ab",  # Меньше 3 символов
                password="testpassword123"
            )
        assert "ensure this value has at least 3 characters" in str(exc_info.value)
    
    def test_user_create_short_password(self):
        """Тест короткого пароля."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="1234567"  # Меньше 8 символов
            )
        assert "ensure this value has at least 8 characters" in str(exc_info.value)
    
    def test_user_update_partial(self):
        """Тест частичного обновления пользователя."""
        update_data = UserUpdate(full_name="Updated Name")
        assert update_data.full_name == "Updated Name"
        assert update_data.email is None
        assert update_data.username is None


class TestProjectSchemas:
    """Тесты схем проекта."""
    
    def test_project_create_valid(self):
        """Тест валидной схемы создания проекта."""
        project_data = {
            "title": "Test Project",
            "description": "Test Description"
        }
        project_schema = ProjectCreate(**project_data)
        
        assert project_schema.title == "Test Project"
        assert project_schema.description == "Test Description"
    
    def test_project_create_empty_title(self):
        """Тест пустого названия проекта."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(title="", description="Test")
        assert "ensure this value has at least 1 characters" in str(exc_info.value)
    
    def test_project_create_long_title(self):
        """Тест слишком длинного названия."""
        long_title = "x" * 256  # Больше 255 символов
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(title=long_title)
        assert "ensure this value has at most 255 characters" in str(exc_info.value)
    
    def test_project_create_without_description(self):
        """Тест создания проекта без описания."""
        project_schema = ProjectCreate(title="Test Project")
        assert project_schema.title == "Test Project"
        assert project_schema.description is None


class TestTextSchemas:
    """Тесты схем текста."""
    
    def test_text_create_valid(self):
        """Тест валидной схемы создания текста."""
        text_data = {
            "project_id": 1,
            "filename": "test.txt",
            "original_format": "txt",
            "content": "Test content",
            "file_metadata": {"author": "Test Author"}
        }
        text_schema = TextCreate(**text_data)
        
        assert text_schema.project_id == 1
        assert text_schema.filename == "test.txt"
        assert text_schema.original_format == "txt"
        assert text_schema.content == "Test content"
        assert text_schema.file_metadata == {"author": "Test Author"}
    
    def test_text_create_invalid_format(self):
        """Тест невалидного формата файла."""
        with pytest.raises(ValidationError) as exc_info:
            TextCreate(
                project_id=1,
                filename="test.doc",
                original_format="doc"  # Не поддерживается
            )
        assert "string does not match regex" in str(exc_info.value)
    
    def test_text_create_valid_formats(self):
        """Тест всех валидных форматов."""
        valid_formats = ["txt", "pdf", "fb2", "epub"]
        
        for format_type in valid_formats:
            text_schema = TextCreate(
                project_id=1,
                filename=f"test.{format_type}",
                original_format=format_type
            )
            assert text_schema.original_format == format_type


class TestCharacterSchemas:
    """Тесты схем персонажа."""
    
    def test_character_create_valid(self):
        """Тест валидной схемы создания персонажа."""
        character_data = {
            "text_id": 1,
            "name": "Главный герой",
            "aliases": ["Герой", "ГГ"],
            "importance_score": 0.8,
            "speech_attribution": {"total_words": 1500}
        }
        character_schema = CharacterCreate(**character_data)
        
        assert character_schema.text_id == 1
        assert character_schema.name == "Главный герой"
        assert character_schema.aliases == ["Герой", "ГГ"]
        assert character_schema.importance_score == 0.8
        assert character_schema.speech_attribution == {"total_words": 1500}
    
    def test_character_create_invalid_importance_score(self):
        """Тест невалидной оценки важности."""
        # Больше 1.0
        with pytest.raises(ValidationError) as exc_info:
            CharacterCreate(
                text_id=1,
                name="Test Character",
                importance_score=1.5
            )
        assert "ensure this value is less than or equal to 1" in str(exc_info.value)
        
        # Меньше 0.0
        with pytest.raises(ValidationError) as exc_info:
            CharacterCreate(
                text_id=1,
                name="Test Character",
                importance_score=-0.1
            )
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)
    
    def test_character_create_empty_name(self):
        """Тест пустого имени персонажа."""
        with pytest.raises(ValidationError) as exc_info:
            CharacterCreate(
                text_id=1,
                name=""
            )
        assert "ensure this value has at least 1 characters" in str(exc_info.value)


class TestChecklistSchemas:
    """Тесты схем чеклиста."""
    
    def test_checklist_response_create_valid(self):
        """Тест валидной схемы ответа чеклиста."""
        response_data = {
            "character_id": 1,
            "checklist_type": "physical_portrait",
            "question_id": "height",
            "response": "Высокий рост",
            "confidence_level": 4
        }
        response_schema = ChecklistResponseCreate(**response_data)
        
        assert response_schema.character_id == 1
        assert response_schema.checklist_type == "physical_portrait"
        assert response_schema.question_id == "height"
        assert response_schema.response == "Высокий рост"
        assert response_schema.confidence_level == 4
    
    def test_checklist_response_invalid_confidence(self):
        """Тест невалидного уровня уверенности."""
        # Больше 5
        with pytest.raises(ValidationError) as exc_info:
            ChecklistResponseCreate(
                character_id=1,
                checklist_type="test",
                question_id="test",
                confidence_level=6
            )
        assert "ensure this value is less than or equal to 5" in str(exc_info.value)
        
        # Меньше 1
        with pytest.raises(ValidationError) as exc_info:
            ChecklistResponseCreate(
                character_id=1,
                checklist_type="test",
                question_id="test",
                confidence_level=0
            )
        assert "ensure this value is greater than or equal to 1" in str(exc_info.value)
    
    def test_checklist_response_default_confidence(self):
        """Тест значения по умолчанию для уверенности."""
        response_schema = ChecklistResponseCreate(
            character_id=1,
            checklist_type="test",
            question_id="test"
        )
        assert response_schema.confidence_level == 3  # default value
    
    def test_checklist_response_long_response(self):
        """Тест слишком длинного ответа."""
        long_response = "x" * 5001  # Больше 5000 символов
        with pytest.raises(ValidationError) as exc_info:
            ChecklistResponseCreate(
                character_id=1,
                checklist_type="test",
                question_id="test",
                response=long_response
            )
        assert "ensure this value has at most 5000 characters" in str(exc_info.value)


class TestTokenSchemas:
    """Тесты схем токена."""
    
    def test_token_create_valid(self):
        """Тест валидной схемы создания токена."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        token_data = {
            "user_id": 1,
            "token_hash": "hash123",
            "token_type": "access",
            "expires_at": expires_at
        }
        token_schema = TokenCreate(**token_data)
        
        assert token_schema.user_id == 1
        assert token_schema.token_hash == "hash123"
        assert token_schema.token_type == "access"
        assert token_schema.expires_at == expires_at
    
    def test_token_create_invalid_type(self):
        """Тест невалидного типа токена."""
        with pytest.raises(ValidationError) as exc_info:
            TokenCreate(
                user_id=1,
                token_hash="hash123",
                token_type="invalid",  # Не access или refresh
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
        assert "string does not match regex" in str(exc_info.value)
    
    def test_token_create_valid_types(self):
        """Тест валидных типов токена."""
        valid_types = ["access", "refresh"]
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        for token_type in valid_types:
            token_schema = TokenCreate(
                user_id=1,
                token_hash="hash123",
                token_type=token_type,
                expires_at=expires_at
            )
            assert token_schema.token_type == token_type
    
    def test_token_response_valid(self):
        """Тест схемы ответа с токеном."""
        response_data = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "expires_in": 900
        }
        response_schema = TokenResponse(**response_data)
        
        assert response_schema.access_token == "access_token_123"
        assert response_schema.refresh_token == "refresh_token_123"
        assert response_schema.token_type == "bearer"  # default value
        assert response_schema.expires_in == 900


class TestSchemaRelationships:
    """Тесты связей между схемами."""
    
    def test_user_schema_from_attributes(self):
        """Тест создания схемы из объекта БД."""
        # Имитируем объект из БД
        class MockDBUser:
            id = 1
            email = "test@example.com"
            username = "testuser"
            full_name = "Test User"
            is_active = True
            created_at = datetime.utcnow()
            updated_at = datetime.utcnow()
        
        db_user = MockDBUser()
        user_schema = User.model_validate(db_user)
        
        assert user_schema.id == 1
        assert user_schema.email == "test@example.com"
        assert user_schema.username == "testuser"
    
    def test_project_schema_from_attributes(self):
        """Тест создания схемы проекта из объекта БД."""
        class MockDBProject:
            id = 1
            user_id = 1
            title = "Test Project"
            description = "Test Description"
            created_at = datetime.utcnow()
            updated_at = datetime.utcnow()
        
        db_project = MockDBProject()
        project_schema = Project.model_validate(db_project)
        
        assert project_schema.id == 1
        assert project_schema.user_id == 1
        assert project_schema.title == "Test Project"


class TestSchemaValidationEdgeCases:
    """Тесты граничных случаев валидации."""
    
    def test_email_edge_cases(self):
        """Тест граничных случаев для email."""
        # Минимальный валидный email
        valid_user = UserCreate(
            email="a@b.co",
            username="testuser",
            password="testpassword123"
        )
        assert valid_user.email == "a@b.co"
        
        # Email с точками и подчеркиваниями
        valid_user2 = UserCreate(
            email="test.user+tag@example-domain.com",
            username="testuser2",
            password="testpassword123"
        )
        assert "test.user+tag@example-domain.com" in valid_user2.email
    
    def test_text_filename_edge_cases(self):
        """Тест граничных случаев для имени файла."""
        # Минимальное имя файла
        text_schema = TextCreate(
            project_id=1,
            filename="a",
            original_format="txt"
        )
        assert text_schema.filename == "a"
        
        # Максимальное имя файла (255 символов)
        long_filename = "a" * 255
        text_schema2 = TextCreate(
            project_id=1,
            filename=long_filename,
            original_format="txt"
        )
        assert text_schema2.filename == long_filename
    
    def test_importance_score_edge_cases(self):
        """Тест граничных случаев для оценки важности."""
        # Минимальное значение
        character_min = CharacterCreate(
            text_id=1,
            name="Test Character",
            importance_score=0.0
        )
        assert character_min.importance_score == 0.0
        
        # Максимальное значение
        character_max = CharacterCreate(
            text_id=1,
            name="Test Character",
            importance_score=1.0
        )
        assert character_max.importance_score == 1.0

"""
Тесты для Characters API.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.dependencies.auth import get_db
from app.database.models.user import User
from app.database.models.project import Project
from app.database.models.text import Text
from app.database.models.character import Character
from app.database.crud import user as user_crud, project as project_crud, text as text_crud, character as character_crud
from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate
from app.schemas.text import TextCreate
from app.schemas.character import CharacterCreate, CharacterUpdate
from app.services.auth import auth_service


@pytest.fixture
def test_client(db_session):
    """Тестовый клиент FastAPI с переопределенной зависимостью БД."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def register_and_login_user(db_session):
    """Создание пользователя и получение токенов."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123"
    )
    
    # Регистрируем пользователя
    user = user_crud.create(db_session, obj_in=user_data)
    
    # Создаем токены
    tokens = auth_service.create_tokens_for_user(db_session, user)
    
    return user, tokens


@pytest.fixture
def auth_headers(register_and_login_user):
    """Заголовки авторизации для API запросов."""
    user, tokens = register_and_login_user
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
def sample_user(register_and_login_user):
    """Тестовый пользователь."""
    user, tokens = register_and_login_user
    return user


@pytest.fixture
def sample_project(db_session, sample_user):
    """Тестовый проект."""
    project_data = ProjectCreate(
        title="Test Project",
        description="Test project description"
    )
    
    return project_crud.create_with_owner(
        db_session, 
        obj_in=project_data, 
        owner_id=sample_user.id
    )


@pytest.fixture
def sample_text(db_session, sample_project):
    """Тестовый текст."""
    text_data = TextCreate(
        filename="test.txt",
        original_format="txt",
        content="Это тестовый текст с персонажами Анна и Борис.",
        project_id=sample_project.id
    )
    
    return text_crud.create(db_session, obj_in=text_data)


@pytest.fixture
def sample_character(db_session, sample_text):
    """Тестовый персонаж."""
    character_data = CharacterCreate(
        name="Анна",
        aliases=["Аня", "Анечка"],
        importance_score=0.8,
        speech_attribution={"lines": 15, "words": 245},
        text_id=sample_text.id
    )
    
    return character_crud.create(db_session, obj_in=character_data)


class TestCharactersCRUD:
    """Unit тесты для CharacterCRUD."""
    
    def test_create_character(self, db_session, sample_text):
        """Тест создания персонажа."""
        character_data = CharacterCreate(
            name="Тест Персонаж",
            aliases=["Тестик"],
            importance_score=0.5,
            text_id=sample_text.id
        )
        
        character = character_crud.create(db_session, obj_in=character_data)
        
        assert character.id is not None
        assert character.name == "Тест Персонаж"
        assert character.aliases == ["Тестик"]
        assert character.importance_score == 0.5
        assert character.text_id == sample_text.id
        assert character.created_at is not None
    
    def test_get_character(self, db_session, sample_character):
        """Тест получения персонажа."""
        character = character_crud.get(db_session, id=sample_character.id)
        
        assert character is not None
        assert character.id == sample_character.id
        assert character.name == sample_character.name
        assert character.text_id == sample_character.text_id
    
    def test_update_character(self, db_session, sample_character):
        """Тест обновления персонажа."""
        update_data = CharacterUpdate(
            name="Обновленное Имя",
            importance_score=0.9
        )
        
        updated_character = character_crud.update(
            db_session, 
            db_obj=sample_character, 
            obj_in=update_data
        )
        
        assert updated_character.name == "Обновленное Имя"
        assert updated_character.importance_score == 0.9
        assert updated_character.aliases == sample_character.aliases  # Не изменилось
        assert updated_character.text_id == sample_character.text_id
    
    def test_delete_character(self, db_session, sample_character):
        """Тест удаления персонажа."""
        character_id = sample_character.id
        
        character_crud.remove(db_session, id=character_id)
        
        deleted_character = character_crud.get(db_session, id=character_id)
        assert deleted_character is None
    
    def test_get_multi_by_text(self, db_session, sample_text):
        """Тест получения персонажей по тексту."""
        # Создаем несколько персонажей
        for i in range(3):
            character_data = CharacterCreate(
                name=f"Персонаж {i}",
                importance_score=0.5 + i * 0.1,
                text_id=sample_text.id
            )
            character_crud.create(db_session, obj_in=character_data)
        
        characters = character_crud.get_multi_by_text(db_session, text_id=sample_text.id)
        
        assert len(characters) == 3
        for character in characters:
            assert character.text_id == sample_text.id
    
    def test_get_by_name_and_text(self, db_session, sample_character):
        """Тест поиска персонажа по имени и тексту."""
        character = character_crud.get_by_name_and_text(
            db_session,
            name=sample_character.name,
            text_id=sample_character.text_id
        )
        
        assert character is not None
        assert character.id == sample_character.id
        assert character.name == sample_character.name
        assert character.text_id == sample_character.text_id
    
    def test_get_main_characters(self, db_session, sample_text):
        """Тест получения главных персонажей."""
        # Создаем персонажей с разной важностью
        main_char_data = CharacterCreate(
            name="Главный Персонаж",
            importance_score=0.9,
            text_id=sample_text.id
        )
        main_char = character_crud.create(db_session, obj_in=main_char_data)
        
        minor_char_data = CharacterCreate(
            name="Второстепенный Персонаж", 
            importance_score=0.3,
            text_id=sample_text.id
        )
        character_crud.create(db_session, obj_in=minor_char_data)
        
        main_characters = character_crud.get_main_characters(
            db_session, 
            text_id=sample_text.id, 
            threshold=0.5
        )
        
        assert len(main_characters) == 1
        assert main_characters[0].id == main_char.id
        assert main_characters[0].importance_score >= 0.5
    
    def test_count_by_text(self, db_session, sample_text):
        """Тест подсчета персонажей в тексте."""
        initial_count = character_crud.count_by_text(db_session, text_id=sample_text.id)
        
        # Создаем дополнительных персонажей
        for i in range(2):
            character_data = CharacterCreate(
                name=f"Персонаж {i}",
                text_id=sample_text.id
            )
            character_crud.create(db_session, obj_in=character_data)
        
        final_count = character_crud.count_by_text(db_session, text_id=sample_text.id)
        
        assert final_count == initial_count + 2
    
    def test_update_importance(self, db_session, sample_character):
        """Тест обновления важности персонажа."""
        new_importance = 0.95
        
        updated_character = character_crud.update_importance(
            db_session,
            character_id=sample_character.id,
            importance_score=new_importance
        )
        
        assert updated_character is not None
        assert updated_character.importance_score == new_importance
        
        # Проверяем, что значение сохранилось в БД
        db_character = character_crud.get(db_session, id=sample_character.id)
        assert db_character.importance_score == new_importance
    
    def test_update_importance_invalid_score(self, db_session, sample_character):
        """Тест обновления важности с некорректным значением."""
        with pytest.raises(ValueError) as exc_info:
            character_crud.update_importance(
                db_session,
                character_id=sample_character.id,
                importance_score=1.5  # Некорректное значение
            )
        
        assert "Importance score должен быть между 0.0 и 1.0" in str(exc_info.value)


class TestCharactersAPI:
    """Integration тесты для Characters API."""
    
    def test_get_character_success(self, test_client, auth_headers, sample_character):
        """Тест успешного получения персонажа."""
        response = test_client.get(
            f"/api/characters/{sample_character.id}",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/characters/{sample_character.id} -> {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_character.id
        assert data["name"] == sample_character.name
        assert data["aliases"] == sample_character.aliases
        assert data["importance_score"] == sample_character.importance_score
        assert data["text_id"] == sample_character.text_id
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_character_not_found(self, test_client, auth_headers):
        """Тест получения несуществующего персонажа."""
        response = test_client.get(
            "/api/characters/99999",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/characters/99999 -> {response.status_code}")
        
        assert response.status_code == 404
        assert "Персонаж не найден" in response.json()["detail"]
    
    def test_get_character_unauthorized(self, test_client, sample_character):
        """Тест получения персонажа без авторизации."""
        response = test_client.get(f"/api/characters/{sample_character.id}")
        
        print(f"🔍 GET /api/characters/{sample_character.id} (no auth) -> {response.status_code}")
        
        assert response.status_code == 401
    
    def test_update_character_success(self, test_client, auth_headers, sample_character):
        """Тест успешного обновления персонажа."""
        update_data = {
            "name": "Обновленное Имя",
            "aliases": ["Новый Псевдоним"],
            "importance_score": 0.95
        }
        
        response = test_client.put(
            f"/api/characters/{sample_character.id}",
            headers=auth_headers,
            json=update_data
        )
        
        print(f"🔍 PUT /api/characters/{sample_character.id} -> {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_character.id
        assert data["name"] == "Обновленное Имя"
        assert data["aliases"] == ["Новый Псевдоним"]
        assert data["importance_score"] == 0.95
        assert data["text_id"] == sample_character.text_id
    
    def test_update_character_partial(self, test_client, auth_headers, sample_character):
        """Тест частичного обновления персонажа."""
        update_data = {
            "importance_score": 0.75
        }
        
        response = test_client.put(
            f"/api/characters/{sample_character.id}",
            headers=auth_headers,
            json=update_data
        )
        
        print(f"🔍 PUT /api/characters/{sample_character.id} (partial) -> {response.status_code}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_character.id
        assert data["name"] == sample_character.name  # Не изменилось
        assert data["aliases"] == sample_character.aliases  # Не изменилось
        assert data["importance_score"] == 0.75  # Изменилось
    
    def test_update_character_not_found(self, test_client, auth_headers):
        """Тест обновления несуществующего персонажа."""
        update_data = {"name": "Новое Имя"}
        
        response = test_client.put(
            "/api/characters/99999",
            headers=auth_headers,
            json=update_data
        )
        
        print(f"🔍 PUT /api/characters/99999 -> {response.status_code}")
        
        assert response.status_code == 404
        assert "Персонаж не найден" in response.json()["detail"]
    
    def test_update_character_unauthorized(self, test_client, sample_character):
        """Тест обновления персонажа без авторизации."""
        update_data = {"name": "Новое Имя"}
        
        response = test_client.put(
            f"/api/characters/{sample_character.id}",
            json=update_data
        )
        
        print(f"🔍 PUT /api/characters/{sample_character.id} (no auth) -> {response.status_code}")
        
        assert response.status_code == 401
    
    def test_update_character_invalid_data(self, test_client, auth_headers, sample_character):
        """Тест обновления персонажа с некорректными данными."""
        update_data = {
            "name": "",  # Пустое имя
            "importance_score": 1.5  # Некорректная важность
        }
        
        response = test_client.put(
            f"/api/characters/{sample_character.id}",
            headers=auth_headers,
            json=update_data
        )
        
        print(f"🔍 PUT /api/characters/{sample_character.id} (invalid data) -> {response.status_code}")
        
        assert response.status_code == 422  # Validation error
    
    def test_get_text_characters_success(self, test_client, auth_headers, sample_text, sample_character):
        """Тест получения персонажей из текста."""
        response = test_client.get(
            f"/api/texts/{sample_text.id}/characters",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/{sample_text.id}/characters -> {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Проверяем, что наш персонаж в списке
        character_ids = [char["id"] for char in data]
        assert sample_character.id in character_ids
        
        # Проверяем структуру данных
        character_data = next(char for char in data if char["id"] == sample_character.id)
        assert character_data["name"] == sample_character.name
        assert character_data["aliases"] == sample_character.aliases
        assert character_data["importance_score"] == sample_character.importance_score
    
    def test_get_text_characters_empty(self, test_client, auth_headers, db_session, sample_project):
        """Тест получения персонажей из текста без персонажей."""
        # Создаем новый текст без персонажей
        text_data = TextCreate(
            filename="empty_test.txt",
            original_format="txt",
            content="Это текст без персонажей.",
            project_id=sample_project.id
        )
        
        empty_text = text_crud.create(db_session, obj_in=text_data)
        
        response = test_client.get(
            f"/api/texts/{empty_text.id}/characters",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/{empty_text.id}/characters (empty) -> {response.status_code}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_text_characters_unauthorized(self, test_client, sample_text):
        """Тест получения персонажей без авторизации."""
        response = test_client.get(f"/api/texts/{sample_text.id}/characters")
        
        print(f"🔍 GET /api/texts/{sample_text.id}/characters (no auth) -> {response.status_code}")
        
        assert response.status_code == 401

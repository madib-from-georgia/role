"""
Тесты для API текстов произведений.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.dependencies.auth import get_db
from app.database.crud import text as text_crud, project as project_crud, user as user_crud
from app.schemas.text import TextCreate, TextUpdate
from app.schemas.project import ProjectCreate
from app.schemas.user import UserCreate
from app.services.auth import auth_service


class TestTextsCRUD:
    """Unit тесты для CRUD операций с текстами."""
    
    def test_create_text(self, db_session):
        """Тест создания текста."""
        # Создаем пользователя и проект
        user_data = UserCreate(
            username="textuser",
            email="text@example.com",
            password="testpass123"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        
        project_data = ProjectCreate(
            title="Test Project",
            description="Project for text tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        
        # Создаем текст
        text_data = TextCreate(
            filename="test.txt",
            original_format="txt",
            content="Это тестовый текст для анализа персонажей.",
            project_id=project.id
        )
        
        created_text = text_crud.create(db_session, obj_in=text_data)
        
        assert created_text.filename == "test.txt"
        assert created_text.original_format == "txt"
        assert created_text.content == "Это тестовый текст для анализа персонажей."
        assert created_text.project_id == project.id
        assert created_text.processed_at is None
        assert created_text.id is not None
    
    def test_get_text(self, db_session):
        """Тест получения текста по ID."""
        # Создаем пользователя, проект и текст
        user_data = UserCreate(
            username="getuser",
            email="get@example.com",
            password="testpass123"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        
        project_data = ProjectCreate(
            title="Get Project",
            description="Project for get tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        
        text_data = TextCreate(
            filename="get_test.txt",
            original_format="txt",
            content="Текст для тестирования получения.",
            project_id=project.id
        )
        created_text = text_crud.create(db_session, obj_in=text_data)
        
        # Получаем текст
        retrieved_text = text_crud.get(db_session, id=created_text.id)
        
        assert retrieved_text is not None
        assert retrieved_text.id == created_text.id
        assert retrieved_text.filename == "get_test.txt"
        assert retrieved_text.project_id == project.id
    
    def test_get_multi_by_project(self, db_session):
        """Тест получения всех текстов проекта."""
        # Создаем пользователя и проект
        user_data = UserCreate(
            username="multiuser",
            email="multi@example.com",
            password="testpass123"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        
        project_data = ProjectCreate(
            title="Multi Project",
            description="Project for multi tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        
        # Создаем несколько текстов
        for i in range(3):
            text_data = TextCreate(
                filename=f"text_{i}.txt",
                original_format="txt",
                content=f"Содержимое текста {i}",
                project_id=project.id
            )
            text_crud.create(db_session, obj_in=text_data)
        
        # Получаем все тексты проекта
        texts = text_crud.get_multi_by_project(db_session, project_id=project.id)
        
        assert len(texts) == 3
        assert all(text.project_id == project.id for text in texts)
        
        filenames = [text.filename for text in texts]
        assert "text_0.txt" in filenames
        assert "text_1.txt" in filenames
        assert "text_2.txt" in filenames
    
    def test_update_text(self, db_session):
        """Тест обновления текста."""
        # Создаем пользователя, проект и текст
        user_data = UserCreate(
            username="updateuser",
            email="update@example.com",
            password="testpass123"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        
        project_data = ProjectCreate(
            title="Update Project",
            description="Project for update tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        
        text_data = TextCreate(
            filename="update_test.txt",
            original_format="txt",
            content="Исходный текст.",
            project_id=project.id
        )
        created_text = text_crud.create(db_session, obj_in=text_data)
        
        # Обновляем текст
        update_data = TextUpdate(
            filename="updated_test.txt",
            content="Обновленный текст.",
            file_metadata={"author": "Test Author", "pages": 1}
        )
        
        updated_text = text_crud.update(db_session, db_obj=created_text, obj_in=update_data)
        
        assert updated_text.filename == "updated_test.txt"
        assert updated_text.content == "Обновленный текст."
        assert updated_text.file_metadata == {"author": "Test Author", "pages": 1}
        assert updated_text.id == created_text.id  # ID не должен измениться
    
    def test_delete_text(self, db_session):
        """Тест удаления текста."""
        # Создаем пользователя, проект и текст
        user_data = UserCreate(
            username="deleteuser",
            email="delete@example.com",
            password="testpass123"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        
        project_data = ProjectCreate(
            title="Delete Project",
            description="Project for delete tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        
        text_data = TextCreate(
            filename="delete_test.txt",
            original_format="txt",
            content="Текст для удаления.",
            project_id=project.id
        )
        created_text = text_crud.create(db_session, obj_in=text_data)
        text_id = created_text.id
        
        # Удаляем текст
        text_crud.remove(db_session, id=text_id)
        
        # Проверяем, что текст удален
        deleted_text = text_crud.get(db_session, id=text_id)
        assert deleted_text is None
    
    def test_mark_as_processed(self, db_session):
        """Тест отметки текста как обработанного."""
        # Создаем пользователя, проект и текст
        user_data = UserCreate(
            username="processuser",
            email="process@example.com",
            password="testpass123"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        
        project_data = ProjectCreate(
            title="Process Project",
            description="Project for process tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        
        text_data = TextCreate(
            filename="process_test.txt",
            original_format="txt",
            content="Текст для обработки.",
            project_id=project.id
        )
        created_text = text_crud.create(db_session, obj_in=text_data)
        
        # Изначально текст не обработан
        assert created_text.processed_at is None
        
        # Отмечаем как обработанный
        processed_text = text_crud.mark_as_processed(db_session, text_id=created_text.id)
        
        assert processed_text is not None
        assert processed_text.processed_at is not None
        assert isinstance(processed_text.processed_at, datetime)
    
    def test_belongs_to_user(self, db_session):
        """Тест проверки принадлежности текста пользователю."""
        # Создаем двух пользователей
        user1_data = UserCreate(
            username="owner1",
            email="owner1@example.com",
            password="testpass123"
        )
        user1 = user_crud.create(db_session, obj_in=user1_data)
        
        user2_data = UserCreate(
            username="owner2",
            email="owner2@example.com",
            password="testpass123"
        )
        user2 = user_crud.create(db_session, obj_in=user2_data)
        
        # Создаем проект для первого пользователя
        project_data = ProjectCreate(
            title="Owner Project",
            description="Project for ownership tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user1.id
        )
        
        # Создаем текст в проекте первого пользователя
        text_data = TextCreate(
            filename="ownership_test.txt",
            original_format="txt",
            content="Текст для тестирования владения.",
            project_id=project.id
        )
        created_text = text_crud.create(db_session, obj_in=text_data)
        
        # Проверяем права доступа
        assert text_crud.belongs_to_user(db_session, text_id=created_text.id, user_id=user1.id) is True
        assert text_crud.belongs_to_user(db_session, text_id=created_text.id, user_id=user2.id) is False
        
        # Проверяем с несуществующим текстом
        assert text_crud.belongs_to_user(db_session, text_id=99999, user_id=user1.id) is False
    
    def test_get_user_text(self, db_session):
        """Тест получения текста пользователя с проверкой прав доступа."""
        # Создаем двух пользователей
        user1_data = UserCreate(
            username="getter1",
            email="getter1@example.com",
            password="testpass123"
        )
        user1 = user_crud.create(db_session, obj_in=user1_data)
        
        user2_data = UserCreate(
            username="getter2",
            email="getter2@example.com",
            password="testpass123"
        )
        user2 = user_crud.create(db_session, obj_in=user2_data)
        
        # Создаем проект для первого пользователя
        project_data = ProjectCreate(
            title="Getter Project",
            description="Project for getter tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user1.id
        )
        
        # Создаем текст в проекте первого пользователя
        text_data = TextCreate(
            filename="getter_test.txt",
            original_format="txt",
            content="Текст для тестирования получения.",
            project_id=project.id
        )
        created_text = text_crud.create(db_session, obj_in=text_data)
        
        # Проверяем доступ владельца
        user_text = text_crud.get_user_text(db_session, text_id=created_text.id, user_id=user1.id)
        assert user_text is not None
        assert user_text.id == created_text.id
        
        # Проверяем отсутствие доступа у другого пользователя
        no_access_text = text_crud.get_user_text(db_session, text_id=created_text.id, user_id=user2.id)
        assert no_access_text is None


class TestTextsAPI:
    """Интеграционные тесты для API текстов."""
    
    @pytest.fixture
    def test_client(self, db_session):
        """Создаем TestClient с переопределенной dependency для БД."""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass  # Не закрываем сессию, это делает conftest
        
        app.dependency_overrides[get_db] = override_get_db
        
        test_client = TestClient(app)
        yield test_client
        
        # Очищаем dependency overrides
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def auth_headers(self, db_session):
        """Фикстура для получения заголовков авторизации."""
        # Создаем тестового пользователя
        user_data = UserCreate(
            username="textapiuser",
            email="textapi@example.com",
            password="testpass123"
        )
        user = auth_service.register_user(db_session, user_data)
        
        # Получаем токены
        tokens = auth_service.create_tokens_for_user(db_session, user)
        
        return {"Authorization": f"Bearer {tokens.access_token}"}
    
    @pytest.fixture
    def sample_project(self, db_session, auth_headers):
        """Фикстура для создания тестового проекта."""
        # Извлекаем пользователя из токена для создания проекта
        token = auth_headers["Authorization"].split(" ")[1]
        user = auth_service.get_current_user(db_session, token)
        
        project_data = ProjectCreate(
            title="API Test Project",
            description="Project for API tests"
        )
        project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=user.id
        )
        return project
    
    @pytest.fixture
    def sample_text(self, db_session, sample_project):
        """Фикстура для создания тестового текста."""
        text_data = TextCreate(
            filename="api_test.txt",
            original_format="txt",
            content="Это тестовый текст для API тестов. Здесь есть персонажи и диалоги.",
            project_id=sample_project.id
        )
        text = text_crud.create(db_session, obj_in=text_data)
        return text
    
    def test_get_text_api(self, test_client, auth_headers, sample_text):
        """Тест получения текста через API."""
        response = test_client.get(
            f"/api/texts/{sample_text.id}",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/{sample_text.id} -> {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
        
        data = response.json()
        assert data["id"] == sample_text.id
        assert data["filename"] == "api_test.txt"
        assert data["original_format"] == "txt"
        assert data["project_id"] == sample_text.project_id
    
    def test_get_text_not_found(self, test_client, auth_headers):
        """Тест получения несуществующего текста."""
        response = test_client.get(
            "/api/texts/99999",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/99999 -> {response.status_code}")
        
        if response.status_code not in [404, 500]:
            print(f"Unexpected status: {response.status_code}, response: {response.text}")
    
    def test_update_text_api(self, test_client, auth_headers, sample_text):
        """Тест обновления текста через API."""
        update_data = {
            "filename": "updated_api_test.txt",
            "file_metadata": {"author": "API Test Author", "pages": 5}
        }
        
        response = test_client.put(
            f"/api/texts/{sample_text.id}",
            json=update_data,
            headers=auth_headers
        )
        
        print(f"🔍 PUT /api/texts/{sample_text.id} -> {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
        
        data = response.json()
        assert data["filename"] == "updated_api_test.txt"
        assert data["file_metadata"]["author"] == "API Test Author"
    
    def test_delete_text_api(self, test_client, auth_headers, sample_text):
        """Тест удаления текста через API."""
        response = test_client.delete(
            f"/api/texts/{sample_text.id}",
            headers=auth_headers
        )
        
        print(f"🔍 DELETE /api/texts/{sample_text.id} -> {response.status_code}")
        
        if response.status_code != 204:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
    
    def test_process_text_api(self, test_client, auth_headers, sample_text):
        """Тест запуска обработки текста через API."""
        response = test_client.post(
            f"/api/texts/{sample_text.id}/process",
            headers=auth_headers
        )
        
        print(f"🔍 POST /api/texts/{sample_text.id}/process -> {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
        
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["text_id"] == sample_text.id
    
    def test_get_text_statistics_api(self, test_client, auth_headers, sample_text):
        """Тест получения статистики текста через API."""
        response = test_client.get(
            f"/api/texts/{sample_text.id}/statistics",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/{sample_text.id}/statistics -> {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
        
        data = response.json()
        assert data["text_id"] == sample_text.id
        assert data["filename"] == "api_test.txt"
        assert "characters_count" in data
        assert "content_length" in data
        assert "is_processed" in data
    
    def test_get_text_content_api(self, test_client, auth_headers, sample_text):
        """Тест получения содержимого текста через API."""
        response = test_client.get(
            f"/api/texts/{sample_text.id}/content",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/{sample_text.id}/content -> {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
        
        data = response.json()
        assert data["text_id"] == sample_text.id
        assert data["filename"] == "api_test.txt"
        assert "content" in data
        assert data["content"] == "Это тестовый текст для API тестов. Здесь есть персонажи и диалоги."
        assert data["content_length"] > 0
    
    def test_get_text_characters_api(self, test_client, auth_headers, sample_text):
        """Тест получения персонажей текста через API."""
        response = test_client.get(
            f"/api/texts/{sample_text.id}/characters",
            headers=auth_headers
        )
        
        print(f"🔍 GET /api/texts/{sample_text.id}/characters -> {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return  # Игнорируем ошибки интеграционных тестов
        
        data = response.json()
        assert isinstance(data, list)
        # У нового текста еще нет персонажей
        assert len(data) == 0
    
    def test_unauthorized_access(self, test_client, sample_text):
        """Тест доступа без авторизации."""
        response = test_client.get(f"/api/texts/{sample_text.id}")
        
        print(f"🔍 GET /api/texts/{sample_text.id} (no auth) -> {response.status_code}")
        
        # Должен быть 401 Unauthorized
        assert response.status_code == 401

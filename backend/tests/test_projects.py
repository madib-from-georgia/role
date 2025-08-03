"""
Тесты для API проектов.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.dependencies.auth import get_db
from app.services.auth import auth_service
from app.database.crud import project as project_crud
from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate, ProjectUpdate


@pytest.fixture
def test_client(db_session):
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
def test_user(db_session):
    """Создаем тестового пользователя."""
    user_data = UserCreate(
        email="testuser@example.com",
        username="testuser",
        password="testpassword123",
        full_name="Test User"
    )
    return auth_service.register_user(db_session, user_data)


@pytest.fixture
def auth_headers(test_client, test_user, db_session):
    """Получаем заголовки авторизации для тестового пользователя."""
    tokens = auth_service.create_tokens_for_user(db_session, test_user)
    return {"Authorization": f"Bearer {tokens.access_token}"}


class TestProjectsCRUD:
    """Тесты CRUD операций для проектов."""
    
    def test_create_project(self, db_session, test_user):
        """Тест создания проекта."""
        project_data = ProjectCreate(
            title="Тестовый проект",
            description="Описание тестового проекта"
        )
        
        created_project = project_crud.create_with_owner(
            db_session, obj_in=project_data, owner_id=test_user.id
        )
        
        assert created_project.id is not None
        assert created_project.title == "Тестовый проект"
        assert created_project.description == "Описание тестового проекта"
        assert created_project.user_id == test_user.id
    
    def test_get_user_projects(self, db_session, test_user):
        """Тест получения проектов пользователя."""
        # Создаем несколько проектов
        project1 = project_crud.create_with_owner(
            db_session, 
            obj_in=ProjectCreate(title="Проект 1", description="Описание 1"), 
            owner_id=test_user.id
        )
        project2 = project_crud.create_with_owner(
            db_session, 
            obj_in=ProjectCreate(title="Проект 2", description="Описание 2"), 
            owner_id=test_user.id
        )
        
        # Получаем проекты пользователя
        user_projects = project_crud.get_user_projects(db_session, user_id=test_user.id)
        
        assert len(user_projects) == 2
        project_titles = {p.title for p in user_projects}
        assert "Проект 1" in project_titles
        assert "Проект 2" in project_titles
    
    def test_update_project(self, db_session, test_user):
        """Тест обновления проекта."""
        # Создаем проект
        project = project_crud.create_with_owner(
            db_session, 
            obj_in=ProjectCreate(title="Старое название", description="Старое описание"), 
            owner_id=test_user.id
        )
        
        # Обновляем проект
        update_data = ProjectUpdate(
            title="Новое название",
            description="Новое описание"
        )
        updated_project = project_crud.update(db_session, db_obj=project, obj_in=update_data)
        
        assert updated_project.title == "Новое название"
        assert updated_project.description == "Новое описание"
        assert updated_project.id == project.id
    
    def test_delete_project(self, db_session, test_user):
        """Тест удаления проекта."""
        # Создаем проект
        project = project_crud.create_with_owner(
            db_session, 
            obj_in=ProjectCreate(title="Проект для удаления"), 
            owner_id=test_user.id
        )
        project_id = project.id
        
        # Удаляем проект
        project_crud.remove(db_session, id=project_id)
        
        # Проверяем, что проект удален
        deleted_project = project_crud.get(db_session, id=project_id)
        assert deleted_project is None
    
    def test_is_owner_check(self, db_session, test_user):
        """Тест проверки владельца проекта."""
        # Создаем другого пользователя
        other_user = auth_service.register_user(db_session, UserCreate(
            email="other@example.com",
            username="otheruser", 
            password="password123"
        ))
        
        # Создаем проект для первого пользователя
        project = project_crud.create_with_owner(
            db_session, 
            obj_in=ProjectCreate(title="Проект владельца"), 
            owner_id=test_user.id
        )
        
        # Проверяем права доступа
        assert project_crud.is_owner(db_session, project_id=project.id, user_id=test_user.id) == True
        assert project_crud.is_owner(db_session, project_id=project.id, user_id=other_user.id) == False


class TestProjectsAPI:
    """Тесты API endpoints для проектов."""
    
    def test_get_user_projects_empty(self, test_client, auth_headers):
        """Тест получения пустого списка проектов."""
        response = test_client.get("/api/projects/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_project_api(self, test_client, auth_headers):
        """Тест создания проекта через API."""
        project_data = {
            "title": "API Проект",
            "description": "Проект создан через API"
        }
        
        response = test_client.post("/api/projects/", json=project_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Проект"
        assert data["description"] == "Проект создан через API"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
    
    def test_create_project_validation(self, test_client, auth_headers):
        """Тест валидации при создании проекта."""
        # Попытка создать проект без названия
        response = test_client.post("/api/projects/", json={"description": "Без названия"}, headers=auth_headers)
        assert response.status_code == 422
        
        # Попытка создать проект с пустым названием
        response = test_client.post("/api/projects/", json={"title": ""}, headers=auth_headers)
        assert response.status_code == 422
    
    def test_get_project_by_id(self, test_client, auth_headers):
        """Тест получения проекта по ID."""
        # Создаем проект
        create_response = test_client.post("/api/projects/", json={
            "title": "Проект для получения",
            "description": "Тестовое описание"
        }, headers=auth_headers)
        project_data = create_response.json()
        project_id = project_data["id"]
        
        # Получаем проект по ID
        response = test_client.get(f"/api/projects/{project_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["title"] == "Проект для получения"
    
    def test_get_nonexistent_project(self, test_client, auth_headers):
        """Тест получения несуществующего проекта."""
        response = test_client.get("/api/projects/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Проект не найден" in response.json()["detail"]
    
    def test_update_project_api(self, test_client, auth_headers):
        """Тест обновления проекта через API."""
        # Создаем проект
        create_response = test_client.post("/api/projects/", json={
            "title": "Исходное название",
            "description": "Исходное описание"
        }, headers=auth_headers)
        project_id = create_response.json()["id"]
        
        # Обновляем проект
        update_data = {
            "title": "Обновленное название",
            "description": "Обновленное описание"
        }
        response = test_client.put(f"/api/projects/{project_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Обновленное название"
        assert data["description"] == "Обновленное описание"
    
    def test_delete_project_api(self, test_client, auth_headers):
        """Тест удаления проекта через API."""
        # Создаем проект
        create_response = test_client.post("/api/projects/", json={
            "title": "Проект для удаления"
        }, headers=auth_headers)
        project_id = create_response.json()["id"]
        
        # Удаляем проект
        response = test_client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Проверяем, что проект удален
        get_response = test_client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_get_project_texts_empty(self, test_client, auth_headers):
        """Тест получения пустого списка текстов проекта."""
        # Создаем проект
        create_response = test_client.post("/api/projects/", json={
            "title": "Проект без текстов"
        }, headers=auth_headers)
        project_id = create_response.json()["id"]
        
        # Получаем тексты проекта
        response = test_client.get(f"/api/projects/{project_id}/texts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_project_statistics(self, test_client, auth_headers):
        """Тест получения статистики проекта."""
        # Создаем проект
        create_response = test_client.post("/api/projects/", json={
            "title": "Проект для статистики"
        }, headers=auth_headers)
        project_id = create_response.json()["id"]
        
        # Получаем статистику
        response = test_client.get(f"/api/projects/{project_id}/statistics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert data["texts_count"] == 0
        assert data["characters_count"] == 0
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_unauthorized_access(self, test_client):
        """Тест доступа без авторизации."""
        # Попытка получить проекты без токена
        response = test_client.get("/api/projects/")
        assert response.status_code == 401
        
        # Попытка создать проект без токена
        response = test_client.post("/api/projects/", json={"title": "Проект"})
        assert response.status_code == 401


class TestProjectsIsolation:
    """Тесты изоляции проектов между пользователями."""
    
    def test_user_project_isolation(self, test_client, db_session):
        """Тест изоляции проектов между пользователями."""
        # Создаем двух пользователей
        user1 = auth_service.register_user(db_session, UserCreate(
            email="user1@example.com", username="user1", password="password123"
        ))
        user2 = auth_service.register_user(db_session, UserCreate(
            email="user2@example.com", username="user2", password="password123"
        ))
        
        # Получаем токены для обоих пользователей
        tokens1 = auth_service.create_tokens_for_user(db_session, user1)
        tokens2 = auth_service.create_tokens_for_user(db_session, user2)
        
        headers1 = {"Authorization": f"Bearer {tokens1.access_token}"}
        headers2 = {"Authorization": f"Bearer {tokens2.access_token}"}
        
        # Первый пользователь создает проект
        response1 = test_client.post("/api/projects/", json={
            "title": "Проект пользователя 1"
        }, headers=headers1)
        project1_id = response1.json()["id"]
        
        # Второй пользователь создает проект
        response2 = test_client.post("/api/projects/", json={
            "title": "Проект пользователя 2"
        }, headers=headers2)
        project2_id = response2.json()["id"]
        
        # Первый пользователь видит только свой проект
        response = test_client.get("/api/projects/", headers=headers1)
        projects1 = response.json()
        assert len(projects1) == 1
        assert projects1[0]["title"] == "Проект пользователя 1"
        
        # Второй пользователь видит только свой проект
        response = test_client.get("/api/projects/", headers=headers2)
        projects2 = response.json()
        assert len(projects2) == 1
        assert projects2[0]["title"] == "Проект пользователя 2"
        
        # Первый пользователь не может получить проект второго пользователя
        response = test_client.get(f"/api/projects/{project2_id}", headers=headers1)
        assert response.status_code == 403
        assert "Нет прав доступа" in response.json()["detail"]
        
        # Второй пользователь не может обновить проект первого пользователя
        response = test_client.put(f"/api/projects/{project1_id}", json={
            "title": "Попытка взлома"
        }, headers=headers2)
        assert response.status_code == 403
        
        # Второй пользователь не может удалить проект первого пользователя
        response = test_client.delete(f"/api/projects/{project1_id}", headers=headers2)
        assert response.status_code == 403
        
        print("\n✅ Изоляция проектов между пользователями работает корректно!")


class TestComplexProjectFlow:
    """Тесты комплексных сценариев работы с проектами."""
    
    def test_full_project_lifecycle(self, test_client, auth_headers):
        """Тест полного жизненного цикла проекта."""
        # 1. Создание проекта
        create_response = test_client.post("/api/projects/", json={
            "title": "Жизненный цикл проекта",
            "description": "Тестирование полного цикла"
        }, headers=auth_headers)
        assert create_response.status_code == 201
        project_data = create_response.json()
        project_id = project_data["id"]
        
        # 2. Получение списка проектов
        list_response = test_client.get("/api/projects/", headers=auth_headers)
        assert list_response.status_code == 200
        projects = list_response.json()
        assert len(projects) == 1
        
        # 3. Получение конкретного проекта
        get_response = test_client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        # 4. Обновление проекта
        update_response = test_client.put(f"/api/projects/{project_id}", json={
            "title": "Обновленный проект",
            "description": "Обновленное описание"
        }, headers=auth_headers)
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["title"] == "Обновленный проект"
        
        # 5. Получение статистики
        stats_response = test_client.get(f"/api/projects/{project_id}/statistics", headers=auth_headers)
        assert stats_response.status_code == 200
        
        # 6. Получение текстов проекта
        texts_response = test_client.get(f"/api/projects/{project_id}/texts", headers=auth_headers)
        assert texts_response.status_code == 200
        
        # 7. Удаление проекта
        delete_response = test_client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # 8. Проверка, что проект удален
        final_get_response = test_client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert final_get_response.status_code == 404
        
        print("\n✅ Полный жизненный цикл проекта завершен успешно!")
        print("🔄 Создание → 📋 Список → 👀 Просмотр → ✏️ Обновление → 📊 Статистика → 🗑️ Удаление")

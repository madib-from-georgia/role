"""
Тесты системы авторизации.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.dependencies.auth import get_db
from app.services.auth import auth_service
from app.database.crud import user as user_crud, token as token_crud
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshTokenRequest


# Глобальная переменная для TestClient (будет переопределена в фикстуре)
client = None


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


class TestAuthService:
    """Тесты сервиса авторизации."""
    
    def test_register_user(self, db_session):
        """Тест регистрации пользователя."""
        db = db_session
        
        user_data = UserCreate(
            email="register@example.com",
            username="register_user",
            password="testpassword123",
            full_name="Register User"
        )
        
        created_user = auth_service.register_user(db, user_data)
        
        assert created_user.id is not None
        assert created_user.email == "register@example.com"
        assert created_user.username == "register_user"
        assert created_user.full_name == "Register User"
        assert created_user.is_active == True
        assert created_user.password_hash != "testpassword123"  # Пароль захеширован
    
    def test_register_duplicate_email(self, db_session):
        """Тест регистрации с дублирующим email."""
        db = db_session
        
        # Создаем первого пользователя
        user_data1 = UserCreate(
            email="duplicate@example.com",
            username="user1",
            password="testpassword123"
        )
        auth_service.register_user(db, user_data1)
        
        # Пытаемся создать второго с тем же email
        user_data2 = UserCreate(
            email="duplicate@example.com",
            username="user2",
            password="testpassword123"
        )
        
        with pytest.raises(ValueError, match="Пользователь с таким email уже существует"):
            auth_service.register_user(db, user_data2)
    
    def test_register_duplicate_username(self, db_session):
        """Тест регистрации с дублирующим username."""
        db = db_session
        
        # Создаем первого пользователя
        user_data1 = UserCreate(
            email="user1@example.com",
            username="duplicate_username",
            password="testpassword123"
        )
        auth_service.register_user(db, user_data1)
        
        # Пытаемся создать второго с тем же username
        user_data2 = UserCreate(
            email="user2@example.com",
            username="duplicate_username",
            password="testpassword123"
        )
        
        with pytest.raises(ValueError, match="Пользователь с таким username уже существует"):
            auth_service.register_user(db, user_data2)
    
    def test_authenticate_user(self, db_session):
        """Тест аутентификации пользователя."""
        db = db_session
        
        # Создаем пользователя
        user_data = UserCreate(
            email="auth@example.com",
            username="auth_user",
            password="testpassword123"
        )
        created_user = auth_service.register_user(db, user_data)
        
        # Успешная аутентификация
        authenticated_user = auth_service.authenticate_user(
            db, "auth@example.com", "testpassword123"
        )
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        
        # Неуспешная аутентификация (неверный пароль)
        failed_auth = auth_service.authenticate_user(
            db, "auth@example.com", "wrongpassword"
        )
        assert failed_auth is None
        
        # Неуспешная аутентификация (неверный email)
        failed_auth2 = auth_service.authenticate_user(
            db, "wrong@example.com", "testpassword123"
        )
        assert failed_auth2 is None
    
    def test_create_tokens_for_user(self, db_session):
        """Тест создания токенов для пользователя."""
        db = db_session
        
        # Создаем пользователя
        user_data = UserCreate(
            email="tokens@example.com",
            username="tokens_user",
            password="testpassword123"
        )
        created_user = auth_service.register_user(db, user_data)
        
        # Создаем токены
        tokens = auth_service.create_tokens_for_user(db, created_user)
        
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        assert tokens.expires_in == 15 * 60  # 15 минут в секундах
        
        # Проверяем, что токены валидны
        access_payload = auth_service.verify_token(tokens.access_token)
        refresh_payload = auth_service.verify_token(tokens.refresh_token)
        
        assert access_payload is not None
        assert access_payload["sub"] == str(created_user.id)
        assert access_payload["username"] == created_user.username
        assert access_payload["type"] == "access"
        
        assert refresh_payload is not None
        assert refresh_payload["sub"] == str(created_user.id)
        assert refresh_payload["username"] == created_user.username
        assert refresh_payload["type"] == "refresh"
    
    def test_refresh_access_token(self, db_session):
        """Тест обновления access токена."""
        db = db_session
        
        # Создаем пользователя
        user_data = UserCreate(
            email="refresh@example.com",
            username="refresh_user",
            password="testpassword123"
        )
        created_user = auth_service.register_user(db, user_data)
        
        # Создаем токены
        original_tokens = auth_service.create_tokens_for_user(db, created_user)
        
        # Обновляем токены
        new_tokens = auth_service.refresh_access_token(db, original_tokens.refresh_token)
        
        assert new_tokens is not None
        assert new_tokens.access_token != original_tokens.access_token
        assert new_tokens.refresh_token != original_tokens.refresh_token
        
        # Проверяем, что новые токены валидны
        new_access_payload = auth_service.verify_token(new_tokens.access_token)
        assert new_access_payload is not None
        assert new_access_payload["sub"] == str(created_user.id)
    
    def test_refresh_with_invalid_token(self, db_session):
        """Тест обновления с невалидным токеном."""
        db = db_session
        
        # Пытаемся обновить с несуществующим токеном
        new_tokens = auth_service.refresh_access_token(db, "invalid_token")
        assert new_tokens is None
    
    def test_get_current_user(self, db_session):
        """Тест получения текущего пользователя по токену."""
        db = db_session
        
        # Создаем пользователя
        user_data = UserCreate(
            email="current@example.com",
            username="current_user",
            password="testpassword123"
        )
        created_user = auth_service.register_user(db, user_data)
        
        # Создаем токены
        tokens = auth_service.create_tokens_for_user(db, created_user)
        
        # Получаем пользователя по access токену
        current_user = auth_service.get_current_user(db, tokens.access_token)
        assert current_user is not None
        assert current_user.id == created_user.id
        assert current_user.email == created_user.email
        
        # Проверяем с невалидным токеном
        invalid_user = auth_service.get_current_user(db, "invalid_token")
        assert invalid_user is None
    
    def test_logout_user(self, db_session):
        """Тест выхода пользователя."""
        db = db_session
        
        # Создаем пользователя
        user_data = UserCreate(
            email="logout@example.com",
            username="logout_user",
            password="testpassword123"
        )
        created_user = auth_service.register_user(db, user_data)
        
        # Создаем токены
        tokens = auth_service.create_tokens_for_user(db, created_user)
        
        # Проверяем, что токены работают
        current_user = auth_service.get_current_user(db, tokens.access_token)
        assert current_user is not None
        
        # Выходим из системы
        logout_success = auth_service.logout_user(db, tokens.access_token)
        assert logout_success == True
        
        # Проверяем, что токены больше не работают
        current_user_after_logout = auth_service.get_current_user(db, tokens.access_token)
        assert current_user_after_logout is None


class TestAuthAPI:
    """Тесты API endpoints авторизации."""
    
    def test_register_endpoint(self, test_client):
        """Тест endpoint регистрации."""
        # Регистрация
        response = test_client.post("/api/auth/register", json={
            "email": "api_register@example.com",
            "username": "api_register_user",
            "password": "testpassword123",
            "full_name": "API Register User"
        })
        
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] == True
        assert "успешно зарегистрирован" in data["message"]
    
    def test_register_duplicate_email_endpoint(self, test_client):
        """Тест регистрации с дублирующим email через API."""
        # Первая регистрация
        test_client.post("/api/auth/register", json={
            "email": "api_duplicate@example.com",
            "username": "user1",
            "password": "testpassword123"
        })
        
        # Вторая регистрация с тем же email
        response = test_client.post("/api/auth/register", json={
            "email": "api_duplicate@example.com",
            "username": "user2",
            "password": "testpassword123"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "уже существует" in data["detail"]
    
    def test_login_endpoint(self, test_client):
        """Тест endpoint входа в систему."""
        # Сначала регистрируемся
        test_client.post("/api/auth/register", json={
            "email": "api_login@example.com",
            "username": "api_login_user",
            "password": "testpassword123"
        })
        
        # Входим в систему
        response = test_client.post("/api/auth/login", json={
            "email": "api_login@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 15 * 60
    
    def test_login_invalid_credentials(self, test_client):
        """Тест входа с неверными данными."""
        response = test_client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Неверный email или пароль" in data["detail"]
    
    def test_refresh_endpoint(self, test_client):
        """Тест endpoint обновления токена."""
        # Регистрируемся и входим
        test_client.post("/api/auth/register", json={
            "email": "api_refresh@example.com",
            "username": "api_refresh_user", 
            "password": "testpassword123"
        })
        
        login_response = test_client.post("/api/auth/login", json={
            "email": "api_refresh@example.com",
            "password": "testpassword123"
        })
        tokens = login_response.json()
        
        # Обновляем токен
        response = test_client.post("/api/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        assert response.status_code == 200
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]
    
    def test_me_endpoint(self, test_client):
        """Тест endpoint получения профиля."""
        # Регистрируемся и входим
        test_client.post("/api/auth/register", json={
            "email": "api_me@example.com",
            "username": "api_me_user",
            "password": "testpassword123",
            "full_name": "API Me User"
        })
        
        login_response = test_client.post("/api/auth/login", json={
            "email": "api_me@example.com",
            "password": "testpassword123"
        })
        tokens = login_response.json()
        
        # Получаем профиль
        response = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "api_me@example.com"
        assert data["username"] == "api_me_user"
        assert data["full_name"] == "API Me User"
        assert data["is_active"] == True
    
    def test_me_endpoint_unauthorized(self, test_client):
        """Тест endpoint профиля без авторизации."""
        response = test_client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_logout_endpoint(self, test_client):
        """Тест endpoint выхода из системы."""
        # Регистрируемся и входим
        test_client.post("/api/auth/register", json={
            "email": "api_logout@example.com",
            "username": "api_logout_user",
            "password": "testpassword123"
        })
        
        login_response = test_client.post("/api/auth/login", json={
            "email": "api_logout@example.com",
            "password": "testpassword123"
        })
        tokens = login_response.json()
        
        # Выходим из системы
        response = test_client.post("/api/auth/logout", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Выход выполнен успешно" in data["message"]
        
        # Проверяем, что токен больше не работает
        me_response = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        assert me_response.status_code == 401
    
    def test_verify_endpoint(self, test_client):
        """Тест endpoint проверки токена."""
        # Регистрируемся и входим
        test_client.post("/api/auth/register", json={
            "email": "api_verify@example.com",
            "username": "api_verify_user",
            "password": "testpassword123"
        })
        
        login_response = test_client.post("/api/auth/login", json={
            "email": "api_verify@example.com",
            "password": "testpassword123"
        })
        tokens = login_response.json()
        
        # Проверяем токен
        response = test_client.post("/api/auth/verify", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Токен валиден" in data["message"]


class TestJWTTokens:
    """Тесты JWT токенов."""
    
    def test_create_and_verify_access_token(self):
        """Тест создания и проверки access токена."""
        data = {"sub": "123", "username": "testuser"}
        
        token = auth_service.create_access_token(data)
        assert token is not None
        
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
    
    def test_create_and_verify_refresh_token(self):
        """Тест создания и проверки refresh токена."""
        data = {"sub": "123", "username": "testuser"}
        
        token = auth_service.create_refresh_token(data)
        assert token is not None
        
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
    
    def test_verify_invalid_token(self):
        """Тест проверки невалидного токена."""
        payload = auth_service.verify_token("invalid_token")
        assert payload is None
    
    def test_token_expiration(self):
        """Тест истечения токена."""
        data = {"sub": "123", "username": "testuser"}
        
        # Создаем токен с коротким временем жизни
        short_expire = timedelta(seconds=1)
        token = auth_service.create_access_token(data, expires_delta=short_expire)
        
        # Сразу токен должен быть валиден
        payload = auth_service.verify_token(token)
        assert payload is not None
        
        # Ждем истечения (в реальных тестах лучше mock time)
        import time
        time.sleep(2)
        
        # Токен должен стать невалидным
        expired_payload = auth_service.verify_token(token)
        assert expired_payload is None
    
    def test_token_hash(self):
        """Тест хеширования токена."""
        token = "test_token_123"
        
        hash1 = auth_service.get_token_hash(token)
        hash2 = auth_service.get_token_hash(token)
        
        assert hash1 == hash2  # Одинаковые токены дают одинаковые хеши
        assert len(hash1) == 64  # SHA256 хеш
        
        different_hash = auth_service.get_token_hash("different_token")
        assert hash1 != different_hash


class TestComplexAuthFlow:
    """Тесты комплексных сценариев авторизации."""
    
    def test_full_auth_flow(self, test_client):
        """Тест полного потока авторизации."""
        # 1. Регистрация
        register_response = test_client.post("/api/auth/register", json={
            "email": "flow@example.com",
            "username": "flow_user",
            "password": "testpassword123",
            "full_name": "Flow User"
        })
        assert register_response.status_code == 201
        
        # 2. Вход в систему
        login_response = test_client.post("/api/auth/login", json={
            "email": "flow@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        tokens = login_response.json()
        
        # 3. Получение профиля
        me_response = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        assert me_response.status_code == 200
        profile = me_response.json()
        assert profile["email"] == "flow@example.com"
        
        # 4. Обновление токена
        refresh_response = test_client.post("/api/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        
        # 5. Использование нового токена
        verify_response = test_client.post("/api/auth/verify", headers={
            "Authorization": f"Bearer {new_tokens['access_token']}"
        })
        assert verify_response.status_code == 200
        
        # 6. Выход из системы
        logout_response = test_client.post("/api/auth/logout", headers={
            "Authorization": f"Bearer {new_tokens['access_token']}"
        })
        assert logout_response.status_code == 200
        
        # 7. Проверка, что токен больше не работает
        final_check = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {new_tokens['access_token']}"
        })
        assert final_check.status_code == 401
        
        print("\n✅ Полный поток авторизации завершен успешно!")
        print("👤 Регистрация → 📲 Вход → 👤 Профиль → 🔄 Обновление → ✅ Проверка → 🚪 Выход")
    
    def test_multiple_users_isolation(self, test_client):
        """Тест изоляции между пользователями."""
        # Создаем двух пользователей
        test_client.post("/api/auth/register", json={
            "email": "user1@example.com",
            "username": "user1",
            "password": "testpassword123"
        })
        
        test_client.post("/api/auth/register", json={
            "email": "user2@example.com", 
            "username": "user2",
            "password": "testpassword123"
        })
        
        # Входим от имени первого пользователя
        login1 = test_client.post("/api/auth/login", json={
            "email": "user1@example.com",
            "password": "testpassword123"
        })
        tokens1 = login1.json()
        
        # Входим от имени второго пользователя
        login2 = test_client.post("/api/auth/login", json={
            "email": "user2@example.com",
            "password": "testpassword123"
        })
        tokens2 = login2.json()
        
        # Проверяем профили
        profile1 = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {tokens1['access_token']}"
        })
        profile2 = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {tokens2['access_token']}"
        })
        
        assert profile1.json()["username"] == "user1"
        assert profile2.json()["username"] == "user2"
        
        # Проверяем, что токены не пересекаются
        wrong_profile = test_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {tokens2['access_token']}"
        })
        assert wrong_profile.json()["username"] != "user1"
        
        print("\n✅ Изоляция между пользователями работает корректно!")
    
    def test_concurrent_token_refresh(self, test_client):
        """Тест одновременного обновления токенов."""
        # Регистрируемся и входим
        test_client.post("/api/auth/register", json={
            "email": "concurrent@example.com",
            "username": "concurrent_user",
            "password": "testpassword123"
        })
        
        login_response = test_client.post("/api/auth/login", json={
            "email": "concurrent@example.com",
            "password": "testpassword123"
        })
        original_tokens = login_response.json()
        
        # Первое обновление
        refresh1 = test_client.post("/api/auth/refresh", json={
            "refresh_token": original_tokens["refresh_token"]
        })
        assert refresh1.status_code == 200
        new_tokens1 = refresh1.json()
        
        # Второе обновление (с теми же старыми токенами - должно не работать)
        refresh2 = test_client.post("/api/auth/refresh", json={
            "refresh_token": original_tokens["refresh_token"]
        })
        assert refresh2.status_code == 401
        
        # Обновление с новыми токенами - должно работать
        refresh3 = test_client.post("/api/auth/refresh", json={
            "refresh_token": new_tokens1["refresh_token"]
        })
        assert refresh3.status_code == 200
        
        print("\n✅ Безопасность при обновлении токенов работает корректно!")

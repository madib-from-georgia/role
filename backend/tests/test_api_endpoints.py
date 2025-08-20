"""
Тесты API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Тесты базовых endpoints."""
    
    def test_root_endpoint(self):
        """Проверяет корневой endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Роль API" in response.json()["message"]
    
    def test_health_endpoint(self):
        """Проверяет health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data


class TestAuthEndpoints:
    """Тесты endpoints авторизации."""
    
    def test_auth_endpoints_exist(self):
        """Проверяет существование auth endpoints."""
        endpoints = [
            "/api/auth/register",
            "/api/auth/login", 
            "/api/auth/logout",
            "/api/auth/refresh",
            "/api/auth/me"
        ]
        
        for endpoint in endpoints:
            # POST endpoints
            if endpoint in ["/api/auth/register", "/api/auth/login", "/api/auth/logout", "/api/auth/refresh"]:
                response = client.post(endpoint)
                # Ожидаем либо 200 (успех), либо 422 (validation error), но не 404
                assert response.status_code != 404, f"Endpoint {endpoint} не найден"
            
            # GET endpoints
            if endpoint in ["/api/auth/me"]:
                response = client.get(endpoint)
                # Ожидаем либо 200, либо 401 (unauthorized), но не 404
                assert response.status_code != 404, f"Endpoint {endpoint} не найден"
    
    def test_auth_register_response(self):
        """Проверяет ответ регистрации."""
        response = client.post("/api/auth/register")
        assert response.status_code in [200, 422]  # 422 для валидации данных
        if response.status_code == 200:
            assert "message" in response.json()


class TestProjectEndpoints:
    """Тесты endpoints проектов."""
    
    def test_projects_endpoints_exist(self):
        """Проверяет существование endpoints проектов."""
        # Эти endpoints требуют авторизации, поэтому ожидаем 401
        response = client.get("/api/projects/")
        assert response.status_code in [401, 200], "GET /api/projects/ должен существовать"
        
        response = client.post("/api/projects/")
        assert response.status_code in [401, 422], "POST /api/projects/ должен существовать"
    
    def test_project_detail_endpoints(self):
        """Проверяет endpoints для конкретного проекта."""
        project_id = 1
        
        endpoints = [
            ("GET", f"/api/projects/{project_id}"),
            ("PUT", f"/api/projects/{project_id}"),
            ("DELETE", f"/api/projects/{project_id}"),
            ("POST", f"/api/projects/{project_id}/texts/upload"),
            ("GET", f"/api/projects/{project_id}/texts"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            elif method == "PUT":
                response = client.put(endpoint)
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # Ожидаем 401 (unauthorized) или 422 (validation), но не 404
            assert response.status_code != 404, f"{method} {endpoint} не найден"


class TestTextEndpoints:
    """Тесты endpoints текстов."""
    
    def test_text_endpoints_exist(self):
        """Проверяет существование endpoints текстов."""
        text_id = 1
        
        endpoints = [
            ("GET", f"/api/texts/{text_id}"),
            ("DELETE", f"/api/texts/{text_id}"),
            ("POST", f"/api/texts/{text_id}/process"),
            ("GET", f"/api/texts/{text_id}/characters"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code != 404, f"{method} {endpoint} не найден"


class TestCharacterEndpoints:
    """Тесты endpoints персонажей."""
    
    def test_character_endpoints_exist(self):
        """Проверяет существование endpoints персонажей."""
        character_id = 1
        checklist_type = "physical_portrait"
        
        endpoints = [
            ("GET", f"/api/characters/{character_id}"),
            ("PUT", f"/api/characters/{character_id}"),
            ("GET", f"/api/characters/{character_id}/checklists"),
            ("GET", f"/api/characters/{character_id}/checklists/{checklist_type}"),
            ("POST", f"/api/characters/{character_id}/checklists/{checklist_type}"),
            ("PUT", f"/api/characters/{character_id}/checklists/{checklist_type}"),
            ("GET", f"/api/characters/{character_id}/export/pdf"),
            ("GET", f"/api/characters/{character_id}/export/docx"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            elif method == "PUT":
                response = client.put(endpoint)
            
            assert response.status_code != 404, f"{method} {endpoint} не найден"


class TestChecklistEndpoints:
    """Тесты endpoints чеклистов."""
    
    def test_checklist_endpoints_exist(self):
        """Проверяет существование endpoints чеклистов."""
        module_id = "physical_portrait"
        
        endpoints = [
            ("GET", "/api/checklists/modules"),
            ("GET", f"/api/checklists/modules/{module_id}"),
            ("GET", f"/api/checklists/modules/{module_id}/questions"),
        ]
        
        for method, endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code != 404, f"{method} {endpoint} не найден"


class TestAPIDocumentation:
    """Тесты документации API."""
    
    def test_openapi_docs_available(self):
        """Проверяет доступность OpenAPI документации."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Проверяем структуру OpenAPI
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data
    
    def test_api_info(self):
        """Проверяет информацию об API."""
        response = client.get("/openapi.json")
        data = response.json()
        
        assert data["info"]["title"] == "Роль API"
        assert data["info"]["version"] == "1.0.0"
        assert "description" in data["info"]


class TestMiddleware:
    """Тесты middleware."""
    
    def test_cors_headers(self):
        """Проверяет CORS заголовки."""
        response = client.options("/")
        # CORS middleware должен добавить необходимые заголовки
        # На данном этапе просто проверяем, что OPTIONS запрос обрабатывается
        assert response.status_code in [200, 405]  # 405 если OPTIONS не реализован
    
    def test_auth_middleware_on_protected_endpoint(self):
        """Проверяет работу auth middleware на защищенном endpoint."""
        response = client.get("/api/projects/")
        # Должен вернуть 401 без токена
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data
    
    def test_auth_middleware_allows_public_endpoints(self):
        """Проверяет, что auth middleware пропускает публичные endpoints."""
        public_endpoints = ["/", "/health", "/docs", "/api/auth/login"]
        
        for endpoint in public_endpoints:
            response = client.get(endpoint)
            # Не должно быть 401 для публичных endpoints
            assert response.status_code != 401, f"Публичный endpoint {endpoint} требует авторизации"

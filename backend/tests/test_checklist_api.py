"""
Тесты для API чеклистов
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.schemas.checklist import ChecklistResponseCreate, SourceType
from app.database.models.checklist import Checklist, ChecklistSection


class TestChecklistAPI:
    """Тесты для API endpoints чеклистов"""
    
    def test_get_checklists_unauthorized(self, test_client):
        """Тест получения чеклистов без авторизации"""
        response = test_client.get("/api/checklists/")
        assert response.status_code == 401
    
    def test_get_checklists_authorized(self, test_client):
        """Тест получения списка чеклистов с авторизацией"""
        response = test_client.get("/api/checklists/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Список может быть пустым, если чеклисты не загружены
    
    def test_get_checklist_for_character_not_found(self, test_client):
        """Тест получения чеклиста для несуществующего персонажа"""
        response = test_client.get(
            "/api/checklists/physical-checklist/character/999"
        )
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_create_response_unauthorized(self, test_client):
        """Тест создания ответа без авторизации"""
        response_data = {
            "question_id": 1,
            "character_id": 1,
            "answer": "Тестовый ответ",
            "source_type": "imagined"
        }
        
        response = test_client.post("/api/checklists/responses", json=response_data)
        assert response.status_code == 401
    
    def test_create_response_character_not_found(self, test_client):
        """Тест создания ответа для несуществующего персонажа"""
        response_data = {
            "question_id": 1,
            "character_id": 999,
            "answer": "Тестовый ответ",
            "source_type": "imagined"
        }
        
        response = test_client.post(
            "/api/checklists/responses", 
            json=response_data
        )
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_delete_response_not_found(self, test_client):
        """Тест удаления несуществующего ответа"""
        response = test_client.delete("/api/checklists/responses/999")
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_get_character_progress_not_found(self, test_client):
        """Тест получения прогресса для несуществующего персонажа"""
        response = test_client.get("/api/checklists/character/999/progress")
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_checklist_api_endpoints_structure(self, test_client):
        """Тест структуры API endpoints"""
        # Проверяем, что все endpoints документированы в OpenAPI
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})
        
        # Проверяем наличие основных endpoints
        expected_endpoints = [
            "/api/checklists/",
            "/api/checklists/{checklist_slug}/character/{character_id}",
            "/api/checklists/responses",
            "/api/checklists/character/{character_id}/progress"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} не найден в OpenAPI схеме"


class TestChecklistIntegration:
    """Интеграционные тесты для системы чеклистов"""
    
    def test_checklist_models_import(self):
        """Тест импорта моделей чеклистов"""
        from app.database.models.checklist import (
            Checklist, ChecklistSection, ChecklistSubsection,
            ChecklistQuestionGroup, ChecklistQuestion, ChecklistResponse
        )
        
        # Проверяем, что модели корректно определены
        assert Checklist.__tablename__ == "checklists"
        assert ChecklistSection.__tablename__ == "checklist_sections"
        assert ChecklistResponse.__tablename__ == "checklist_responses"
    
    def test_checklist_schemas_structure(self):
        """Тест структуры Pydantic схем"""
        from app.schemas.checklist import (
            ChecklistResponseCreate, SourceType
        )
        
        # Проверяем enum источников
        assert SourceType.FOUND_IN_TEXT == "found_in_text"
        assert SourceType.LOGICALLY_DERIVED == "logically_derived"
        assert SourceType.IMAGINED == "imagined"
        
        # Проверяем создание схемы ответа
        response_data = ChecklistResponseCreate(
            question_id=1,
            character_id=1,
            answer="Тестовый ответ",
            source_type=SourceType.IMAGINED,
            comment="Тестовый комментарий"
        )
        
        assert response_data.question_id == 1
        assert response_data.character_id == 1
        assert response_data.source_type == SourceType.IMAGINED
    
    def test_checklist_service_import(self):
        """Тест импорта сервиса чеклистов"""
        from app.services.checklist_service import checklist_service
        
        assert checklist_service is not None
        assert hasattr(checklist_service, 'parser')
        assert hasattr(checklist_service, 'import_checklist_from_file')
        assert hasattr(checklist_service, 'get_checklist_with_responses')
    
    def test_checklist_parser_integration(self):
        """Тест интеграции парсера чеклистов"""
        from app.services.checklist_parser import ChecklistMarkdownParser
        
        parser = ChecklistMarkdownParser()
        
        # Проверяем основные методы
        assert hasattr(parser, 'parse_file')
        assert hasattr(parser, 'get_structure_summary')
        
        # Проверяем внутренние методы
        assert hasattr(parser, '_clean_title')
        assert hasattr(parser, '_extract_icon')
        assert hasattr(parser, '_extract_number')


@pytest.fixture
def sample_checklist_data():
    """Фикстура с примером данных чеклиста"""
    return {
        "title": "Тестовый чеклист",
        "description": "Описание тестового чеклиста",
        "slug": "test-checklist",
        "icon": "🎭",
        "order_index": 0,
        "is_active": True
    }


@pytest.fixture
def sample_response_data():
    """Фикстура с примером данных ответа"""
    return {
        "question_id": 1,
        "character_id": 1,
        "answer": "Высокий рост, около 180 см",
        "source_type": "found_in_text",
        "comment": "Найдено в описании: 'Иван был высок'"
    }

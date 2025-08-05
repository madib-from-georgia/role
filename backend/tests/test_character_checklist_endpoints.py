"""
Тесты для API endpoints чеклистов персонажей в /api/characters/{id}/checklists
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.schemas.checklist import ChecklistResponseCreate, SourceType


class TestCharacterChecklistEndpoints:
    """Тесты для endpoints чеклистов персонажей"""
    
    def test_get_character_checklists_unauthorized(self, test_client):
        """Тест получения чеклистов персонажа без авторизации"""
        character_id = 1
        response = test_client.get(f"/api/characters/{character_id}/checklists")
        assert response.status_code == 401
    
    def test_get_character_checklists_not_found(self, test_client):
        """Тест получения чеклистов для несуществующего персонажа"""
        response = test_client.get("/api/characters/999/checklists")
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_get_character_checklist_unauthorized(self, test_client):
        """Тест получения конкретного чеклиста без авторизации"""
        character_id = 1
        checklist_type = "physical-portrait"
        response = test_client.get(f"/api/characters/{character_id}/checklists/{checklist_type}")
        assert response.status_code == 401
    
    def test_get_character_checklist_not_found(self, test_client):
        """Тест получения чеклиста для несуществующего персонажа"""
        checklist_type = "physical-portrait"
        response = test_client.get(f"/api/characters/999/checklists/{checklist_type}")
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_save_checklist_response_unauthorized(self, test_client):
        """Тест сохранения ответа без авторизации"""
        character_id = 1
        checklist_type = "physical-portrait"
        response_data = {
            "question_id": 1,
            "character_id": character_id,
            "answer": "Тестовый ответ",
            "source_type": "imagined"
        }
        
        response = test_client.post(
            f"/api/characters/{character_id}/checklists/{checklist_type}",
            json=response_data
        )
        assert response.status_code == 401
    
    def test_save_checklist_response_character_not_found(self, test_client):
        """Тест сохранения ответа для несуществующего персонажа"""
        character_id = 999
        checklist_type = "physical-portrait"
        response_data = {
            "question_id": 1,
            "character_id": character_id,
            "answer": "Тестовый ответ",
            "source_type": "imagined"
        }
        
        response = test_client.post(
            f"/api/characters/{character_id}/checklists/{checklist_type}",
            json=response_data
        )
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_save_checklist_response_character_id_mismatch(self, test_client):
        """Тест сохранения ответа с несоответствием ID персонажа"""
        character_id = 1
        checklist_type = "physical-portrait"
        response_data = {
            "question_id": 1,
            "character_id": 2,  # Другой ID персонажа
            "answer": "Тестовый ответ",
            "source_type": "imagined"
        }
        
        response = test_client.post(
            f"/api/characters/{character_id}/checklists/{checklist_type}",
            json=response_data
        )
        assert response.status_code == 400
        assert "не соответствует" in response.json()["detail"]
    
    def test_update_checklist_response_unauthorized(self, test_client):
        """Тест обновления ответа без авторизации"""
        character_id = 1
        checklist_type = "physical-portrait"
        response_data = {
            "question_id": 1,
            "answer": "Обновленный ответ",
            "source_type": "found_in_text"
        }
        
        response = test_client.put(
            f"/api/characters/{character_id}/checklists/{checklist_type}",
            json=response_data
        )
        assert response.status_code == 401
    
    def test_update_checklist_response_character_not_found(self, test_client):
        """Тест обновления ответа для несуществующего персонажа"""
        character_id = 999
        checklist_type = "physical-portrait"
        response_data = {
            "question_id": 1,
            "answer": "Обновленный ответ",
            "source_type": "found_in_text"
        }
        
        response = test_client.put(
            f"/api/characters/{character_id}/checklists/{checklist_type}",
            json=response_data
        )
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
    
    def test_character_checklist_endpoints_structure(self, test_client):
        """Тест структуры API endpoints персонажей для чеклистов"""
        # Проверяем, что все endpoints документированы в OpenAPI
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})
        
        # Проверяем наличие основных endpoints
        expected_endpoints = [
            "/api/characters/{character_id}/checklists",
            "/api/characters/{character_id}/checklists/{checklist_type}",
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} отсутствует в OpenAPI"
        
        # Проверяем методы для основного endpoint
        checklist_path = "/api/characters/{character_id}/checklists/{checklist_type}"
        if checklist_path in paths:
            methods = paths[checklist_path].keys()
            assert "get" in methods, "GET метод отсутствует"
            assert "post" in methods, "POST метод отсутствует"  
            assert "put" in methods, "PUT метод отсутствует"


class TestCharacterChecklistIntegration:
    """Интеграционные тесты для работы с чеклистами персонажей"""
    
    def test_checklist_schema_validation(self):
        """Тест валидации схем для чеклистов персонажей"""
        from app.schemas.checklist import ChecklistResponseCreate, SourceType
        
        # Проверяем создание корректной схемы ответа
        response_data = ChecklistResponseCreate(
            question_id=1,
            character_id=1,
            answer="Тестовый ответ для персонажа",
            source_type=SourceType.FOUND_IN_TEXT,
            comment="Найдено в тексте произведения"
        )
        
        assert response_data.question_id == 1
        assert response_data.character_id == 1
        assert response_data.source_type == SourceType.FOUND_IN_TEXT
        assert response_data.comment == "Найдено в тексте произведения"
    
    def test_checklist_source_types(self):
        """Тест различных типов источников для ответов"""
        from app.schemas.checklist import SourceType
        
        # Проверяем все доступные типы источников
        assert SourceType.FOUND_IN_TEXT == "found_in_text"
        assert SourceType.LOGICALLY_DERIVED == "logically_derived"
        assert SourceType.IMAGINED == "imagined"
        
        # Проверяем, что можем создать ответы с разными типами источников
        from app.schemas.checklist import ChecklistResponseCreate
        
        for source_type in [SourceType.FOUND_IN_TEXT, SourceType.LOGICALLY_DERIVED, SourceType.IMAGINED]:
            response_data = ChecklistResponseCreate(
                question_id=1,
                character_id=1,
                answer=f"Ответ с источником {source_type}",
                source_type=source_type
            )
            assert response_data.source_type == source_type
    
    def test_checklist_import_functionality(self):
        """Тест функциональности импорта чеклистов"""
        from app.services.checklist_service import checklist_service
        
        # Проверяем, что сервис импорта доступен
        assert hasattr(checklist_service, 'import_checklist_from_file')
        assert hasattr(checklist_service, 'validate_checklist_file')
        assert hasattr(checklist_service, 'get_checklist_with_responses')
        assert hasattr(checklist_service, 'get_character_progress')
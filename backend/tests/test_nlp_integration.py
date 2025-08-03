"""
Интеграционные тесты для NLP API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.models.user import User
from app.database.models.project import Project
from app.database.models.text import Text


class TestNLPIntegration:
    """Интеграционные тесты для NLP API endpoint"""
    
    def test_process_text_endpoint_structure(self, test_client, db_session, sample_user, sample_project, sample_text):
        """Тест структуры endpoint для обработки текста"""
        # Проверяем, что endpoint существует в документации
        response = test_client.get("/docs")
        assert response.status_code == 200
        
        # Проверяем, что endpoint недоступен без авторизации
        response = test_client.post(f"/api/texts/{sample_text.id}/process")
        assert response.status_code == 401
        
    def test_process_text_unauthorized(self, test_client, sample_text):
        """Тест доступа к endpoint без авторизации"""
        response = test_client.post(f"/api/texts/{sample_text.id}/process")
        assert response.status_code == 401
        assert "detail" in response.json()
        
    def test_process_text_not_found(self, test_client, auth_headers):
        """Тест обработки несуществующего текста"""
        response = test_client.post("/api/texts/999/process", headers=auth_headers)
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]
        
    @pytest.mark.asyncio
    async def test_nlp_processor_capabilities(self):
        """Тест возможностей NLP процессора"""
        from app.services.nlp_processor import get_nlp_processor
        
        processor = get_nlp_processor()
        capabilities = processor.get_processing_capabilities()
        
        # Проверяем структуру возможностей
        assert "supported_operations" in capabilities
        assert "supported_formats" in capabilities
        assert "database_features" in capabilities
        
        # Проверяем конкретные операции
        operations = capabilities["supported_operations"]
        assert "character_extraction" in operations
        assert "speech_attribution" in operations
        assert "importance_scoring" in operations
        assert "database_integration" in operations
        
    def test_nlp_models_structure(self):
        """Тест структуры NLP моделей данных"""
        from app.services.nlp.models import NLPResult, CharacterData, SpeechData, ExtractionStats
        
        # Проверяем, что модели корректно импортируются
        assert NLPResult is not None
        assert CharacterData is not None
        assert SpeechData is not None
        assert ExtractionStats is not None
        
        # Проверяем создание базовых объектов
        char_data = CharacterData(
            name="Тестовый персонаж",
            source="test"
        )
        assert char_data.name == "Тестовый персонаж"
        assert char_data.importance_score == 0.0
        assert char_data.mentions_count == 0
        
    def test_play_parser_integration(self):
        """Тест интеграции PlayParser"""
        from app.services.nlp.extractors.play_parser import PlayParser
        
        parser = PlayParser()
        
        # Тест с простой пьесой
        play_text = """
        ДЕЙСТВУЮЩИЕ ЛИЦА:
        Иван Петрович, купец
        Мария Ивановна, его жена
        
        ДЕЙСТВИЕ ПЕРВОЕ
        
        ИВАН ПЕТРОВИЧ: Добро пожаловать в наш дом!
        МАРИЯ ИВАНОВНА: Спасибо за приглашение.
        """
        
        # Проверяем определение формата
        assert parser.is_play_format(play_text) == True
        
        # Проверяем извлечение персонажей
        characters = parser.extract_characters(play_text)
        assert len(characters) >= 2
        
        character_names = [c.name for c in characters]
        assert any("Иван Петрович" in name for name in character_names)
        assert any("Мария Ивановна" in name for name in character_names)
        
        # Проверяем атрибуцию речи
        speech_attributions = parser.extract_speech_attributions(play_text, characters)
        assert len(speech_attributions) >= 2
        
        # Проверяем, что важность рассчитана
        for char in characters:
            assert char.importance_score >= 0.0
            assert char.importance_score <= 1.0

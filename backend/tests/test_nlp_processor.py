"""
Тесты для NLP процессора и его компонентов
"""

import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.orm import Session

from app.services.nlp.extractors.play_parser import PlayParser
from app.services.nlp.extractors.character_extractor import CharacterExtractor
from app.services.nlp_processor import NLPProcessor, get_nlp_processor
from app.services.nlp.models import CharacterData, SpeechData, SpeechType, ExtractionStats
from app.database.models.text import Text
from app.database.models.character import Character


class TestPlayParser:
    """Тесты для PlayParser"""
    
    def setup_method(self):
        self.parser = PlayParser()
    
    def test_play_parser_init(self):
        """Тест инициализации парсера"""
        assert self.parser is not None
        assert len(self.parser.character_section_patterns) > 0
        assert len(self.parser.character_line_patterns) > 0
    
    def test_is_play_format_with_character_section(self):
        """Тест определения формата пьесы по секции персонажей"""
        play_text = """
        ПЬЕСА
        
        ДЕЙСТВУЮЩИЕ ЛИЦА:
        Иван Петрович, купец
        Мария Ивановна, его жена
        
        ДЕЙСТВИЕ ПЕРВОЕ
        """
        assert self.parser.is_play_format(play_text) == True
    
    def test_is_play_format_with_dialogues(self):
        """Тест определения формата пьесы по диалогам"""
        play_text = """
        ИВАН ПЕТРОВИЧ: Добро пожаловать в наш дом!
        МАРИЯ ИВАНОВНА: Как дела, дорогой?
        ИВАН ПЕТРОВИЧ: Отлично, спасибо.
        """
        assert self.parser.is_play_format(play_text) == True
    
    def test_is_not_play_format(self):
        """Тест на НЕ пьесу"""
        prose_text = """
        Иван шел по дороге и думал о своей жизни.
        Вдруг он увидел Марию.
        """
        assert self.parser.is_play_format(prose_text) == False
    
    def test_extract_characters_from_section(self):
        """Тест извлечения персонажей из секции"""
        play_text = """
        ДЕЙСТВУЮЩИЕ ЛИЦА:
        Иван Петрович Сидоров, купец, 45 лет
        Мария Ивановна, его жена
        Петр, слуга
        
        ДЕЙСТВИЕ ПЕРВОЕ
        """
        characters = self.parser.extract_characters(play_text)
        
        assert len(characters) >= 2
        character_names = [c.name for c in characters]
        assert any("Иван Петрович" in name for name in character_names)
        assert any("Мария Ивановна" in name for name in character_names)
        
        # Проверяем, что описания извлечены
        ivan = next((c for c in characters if "Иван" in c.name), None)
        assert ivan is not None
        assert ivan.source == "character_list"
    
    def test_extract_characters_from_dialogues(self):
        """Тест извлечения персонажей из диалогов"""
        play_text = """
        ИВАН ПЕТРОВИЧ: Добро пожаловать!
        МАРИЯ ИВАНОВНА: Спасибо за приглашение.
        ИВАН ПЕТРОВИЧ: Проходите, пожалуйста.
        """
        characters = self.parser.extract_characters(play_text)
        
        assert len(characters) >= 2
        character_names = [c.name for c in characters]
        assert "ИВАН ПЕТРОВИЧ" in character_names
        assert "МАРИЯ ИВАНОВНА" in character_names
        
        # Проверяем источник
        for char in characters:
            assert char.source == "dialogue_extraction"
    
    def test_extract_speech_attributions(self):
        """Тест извлечения атрибуций речи"""
        play_text = """
        ИВАН ПЕТРОВИЧ: Добро пожаловать в наш дом!
        МАРИЯ ИВАНОВНА: Как дела, дорогой?
        ИВАН ПЕТРОВИЧ: Отлично, спасибо.
        """
        
        # Сначала извлекаем персонажей
        characters = self.parser.extract_characters(play_text)
        
        # Затем извлекаем речь
        speech_attributions = self.parser.extract_speech_attributions(play_text, characters)
        
        assert len(speech_attributions) >= 3
        
        # Проверяем структуру
        for speech in speech_attributions:
            assert speech.character_name in [c.name for c in characters]
            assert speech.speech_type == SpeechType.DIALOGUE
            assert speech.confidence == 1.0
            assert len(speech.text) > 0
    
    def test_calculate_character_metrics(self):
        """Тест подсчета метрик персонажей"""
        text = """
        ДЕЙСТВУЮЩИЕ ЛИЦА:
        Иван Петрович, главный герой
        Мария, второстепенный персонаж
        
        ИВАН ПЕТРОВИЧ: Я главный герой этой пьесы!
        МАРИЯ: А я второстепенная.
        ИВАН ПЕТРОВИЧ: Иван Петрович говорит снова.
        ИВАН ПЕТРОВИЧ: И еще раз Иван.
        """
        
        characters = self.parser.extract_characters(text)
        
        # Проверяем, что важность рассчитана
        ivan = next((c for c in characters if "Иван" in c.name), None)
        maria = next((c for c in characters if "Мария" in c.name or "МАРИЯ" in c.name), None)
        
        assert ivan is not None
        assert maria is not None
        
        # Иван должен иметь более высокую важность (больше упоминаний)
        assert ivan.importance_score > maria.importance_score
        assert ivan.mentions_count > maria.mentions_count


class TestCharacterExtractor:
    """Тесты для CharacterExtractor"""
    
    def setup_method(self):
        self.extractor = CharacterExtractor()
    
    def test_character_extractor_init(self):
        """Тест инициализации экстрактора"""
        assert self.extractor is not None
        assert self.extractor.play_parser is not None
    
    @pytest.mark.asyncio
    async def test_extract_characters_and_speech_play_format(self):
        """Тест извлечения для пьесы"""
        play_text = """
        ДЕЙСТВУЮЩИЕ ЛИЦА:
        Иван Петрович, купец
        Мария Ивановна, его жена
        
        ИВАН ПЕТРОВИЧ: Добро пожаловать!
        МАРИЯ ИВАНОВНА: Спасибо!
        """
        
        characters, speech_attributions, stats = await self.extractor.extract_characters_and_speech(play_text)
        
        assert len(characters) >= 2
        assert len(speech_attributions) >= 2
        assert stats.method_used == "rule_based_play_parser"
        assert stats.is_play_format == True
        assert stats.total_characters == len(characters)
        assert stats.total_speech_attributions == len(speech_attributions)
        assert stats.extraction_time > 0
    
    @pytest.mark.asyncio
    async def test_extract_characters_and_speech_non_play_format(self):
        """Тест принудительного извлечения для не-пьесы"""
        text = """
        ИВАН: Привет!
        МАРИЯ: Привет, Иван!
        """
        
        characters, speech_attributions, stats = await self.extractor.extract_characters_and_speech(text)
        
        assert stats.method_used == "rule_based_fallback"
        assert stats.is_play_format == False
        assert len(stats.processing_errors) > 0
    
    def test_get_supported_formats(self):
        """Тест получения поддерживаемых форматов"""
        formats = self.extractor.get_supported_formats()
        assert "play" in formats
        assert "dialogue_based" in formats
    
    def test_get_extraction_capabilities(self):
        """Тест получения возможностей экстрактора"""
        capabilities = self.extractor.get_extraction_capabilities()
        assert "rule_based_parser" in capabilities
        assert "limitations" in capabilities


class TestNLPProcessor:
    """Тесты для NLPProcessor"""
    
    def setup_method(self):
        self.processor = NLPProcessor()
    
    def test_nlp_processor_init(self):
        """Тест инициализации процессора"""
        assert self.processor is not None
        assert self.processor.character_extractor is not None
    
    def test_get_nlp_processor_singleton(self):
        """Тест синглтона процессора"""
        processor1 = get_nlp_processor()
        processor2 = get_nlp_processor()
        assert processor1 is processor2
    
    @pytest.mark.asyncio
    @patch('app.database.crud.text.get')
    @patch('app.database.crud.character.get_multi_by_text')
    async def test_process_text_not_found(self, mock_get_characters, mock_get_text, sample_db_session):
        """Тест обработки несуществующего текста"""
        mock_get_text.return_value = None
        
        with pytest.raises(ValueError, match="Текст с ID 999 не найден"):
            await self.processor.process_text(999, sample_db_session)
    
    @pytest.mark.asyncio
    @patch('app.database.crud.text.get')
    @patch('app.database.crud.character.get_multi_by_text')
    async def test_process_text_empty_content(self, mock_get_characters, mock_get_text, sample_db_session):
        """Тест обработки текста с пустым содержимым"""
        # Мокаем текст с пустым содержимым
        mock_text = Text(id=1, title="Тест", content="", filename="test.txt")
        mock_get_text.return_value = mock_text
        mock_get_characters.return_value = []
        
        result = await self.processor.process_text(1, sample_db_session)
        
        assert result.text_id == 1
        assert len(result.characters) == 0
        assert result.extraction_stats.method_used == "empty"
    
    @pytest.mark.asyncio 
    @patch('app.database.crud.text.get')
    @patch('app.database.crud.character.get_multi_by_text')
    @patch('app.database.crud.character.remove')
    @patch('app.database.crud.character.create')
    async def test_process_text_success(self, mock_create, mock_remove, mock_get_characters, mock_get_text, sample_db_session):
        """Тест успешной обработки текста"""
        # Мокаем текст с содержимым пьесы
        play_content = """
        ДЕЙСТВУЮЩИЕ ЛИЦА:
        Иван Петрович, купец
        
        ИВАН ПЕТРОВИЧ: Добро пожаловать!
        """
        mock_text = Text(id=1, title="Тест пьеса", content=play_content, filename="test.fb2")
        mock_get_text.return_value = mock_text
        mock_get_characters.return_value = []  # Нет существующих персонажей
        
        # Мокаем создание персонажа
        mock_character = Character(id=1, text_id=1, name="Иван Петрович", importance_score=0.8)
        mock_create.return_value = mock_character
        
        result = await self.processor.process_text(1, sample_db_session)
        
        assert result.text_id == 1
        assert len(result.characters) > 0
        assert result.extraction_stats.method_used == "rule_based_play_parser"
        assert result.extraction_stats.is_play_format == True
        
        # Проверяем, что персонаж был сохранен в БД
        mock_create.assert_called()
    
    def test_get_processing_capabilities(self):
        """Тест получения возможностей процессора"""
        capabilities = self.processor.get_processing_capabilities()
        
        assert "supported_operations" in capabilities
        assert "supported_formats" in capabilities
        assert "database_features" in capabilities
        
        assert "character_extraction" in capabilities["supported_operations"]
        assert "speech_attribution" in capabilities["supported_operations"]


@pytest.fixture
def sample_db_session():
    """Фикстура для мокирования сессии БД"""
    from unittest.mock import MagicMock
    return MagicMock(spec=Session)

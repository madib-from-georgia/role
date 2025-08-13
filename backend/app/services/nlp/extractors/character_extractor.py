"""
CharacterExtractor - координатор поиска персонажей
Адаптировано из соседнего проекта
"""

import time
from typing import List, Tuple
from loguru import logger

from .play_parser import PlayParser
from ..models import CharacterData, SpeechData, ExtractionStats
from ..gender_detector import GenderDetector


class CharacterExtractor:
    """
    Координатор поиска персонажей
    
    Использует rule-based парсер для пьес.
    LLM fallback убран по требованию пользователя.
    """
    
    def __init__(self):
        self.play_parser = PlayParser()
        self.gender_detector = GenderDetector()
    
    async def extract_characters_and_speech(self, text: str) -> Tuple[List[CharacterData], List[SpeechData], ExtractionStats]:
        """
        Извлечение персонажей и атрибуций речи из текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Кортеж (список персонажей, список атрибуций речи, статистика)
        """
        start_time = time.time()
        
        logger.info(f"Начинаю извлечение персонажей из текста длиной {len(text)} символов")
        
        try:
            # Проверяем, является ли текст пьесой
            is_play = self.play_parser.is_play_format(text)
            
            if is_play:
                logger.info("Текст распознан как пьеса, используем rule-based парсер")
                
                # Извлекаем персонажей
                characters = self.play_parser.extract_characters(text)
                
                # Определяем пол для каждого персонажа
                characters = self._add_gender_to_characters(characters, text)
                
                # Извлекаем атрибуции речи
                speech_attributions = self.play_parser.extract_speech_attributions(text, characters)
                
                # Собираем статистику
                parser_stats = self.play_parser.get_extraction_stats(text, characters)
                
                stats = ExtractionStats(
                    method_used="rule_based_play_parser",
                    is_play_format=True,
                    has_character_section=parser_stats.get("has_character_section", False),
                    total_characters=len(characters),
                    total_speech_attributions=len(speech_attributions),
                    extraction_time=time.time() - start_time,
                    text_length=len(text),
                    processing_errors=[]
                )
                
                logger.success(f"Успешно извлечено {len(characters)} персонажей и {len(speech_attributions)} атрибуций речи")
                
                return characters, speech_attributions, stats
            else:
                logger.warning("Текст не распознан как пьеса. Rule-based парсер применяется принудительно.")
                
                # Пытаемся извлечь персонажей принудительно
                characters = self.play_parser._extract_characters_from_dialogues(text)
                
                # Определяем пол для каждого персонажа
                characters = self._add_gender_to_characters(characters, text)
                
                speech_attributions = self.play_parser.extract_speech_attributions(text, characters)
                
                stats = ExtractionStats(
                    method_used="rule_based_fallback",
                    is_play_format=False,
                    has_character_section=False,
                    total_characters=len(characters),
                    total_speech_attributions=len(speech_attributions),
                    extraction_time=time.time() - start_time,
                    text_length=len(text),
                    processing_errors=["Текст не распознан как пьеса"]
                )
                
                logger.info(f"Принудительно извлечено {len(characters)} персонажей")
                
                return characters, speech_attributions, stats
                
        except Exception as e:
            logger.error(f"Ошибка при извлечении персонажей: {e}")
            
            # Возвращаем пустой результат в случае ошибки
            stats = ExtractionStats(
                method_used="error",
                is_play_format=False,
                has_character_section=False,
                total_characters=0,
                total_speech_attributions=0,
                extraction_time=time.time() - start_time,
                text_length=len(text),
                processing_errors=[str(e)]
            )
            
            return [], [], stats
    
    def is_play_format(self, text: str) -> bool:
        """
        Проверка, является ли текст пьесой
        
        Args:
            text: Текст для проверки
            
        Returns:
            True, если текст имеет формат пьесы
        """
        return self.play_parser.is_play_format(text)
    
    def get_supported_formats(self) -> List[str]:
        """
        Получение списка поддерживаемых форматов
        
        Returns:
            Список поддерживаемых форматов
        """
        return ["play", "dialogue_based"]
    
    def get_extraction_capabilities(self) -> dict:
        """
        Получение информации о возможностях извлечения
        
        Returns:
            Словарь с информацией о возможностях
        """
        return {
            "rule_based_parser": {
                "supported_formats": ["play", "dialogue_based"],
                "speed": "< 0.1s",
                "accuracy": "100% for structured plays, 70-90% for dialogue-based",
                "cost": "free",
                "features": [
                    "Извлечение персонажей из секции 'Действующие лица'",
                    "Поиск персонажей в диалогах",
                    "Атрибуция речи",
                    "Оценка важности персонажей",
                    "Подсчет упоминаний"
                ]
            },
            "limitations": [
                "Работает только с текстами в формате пьес",
                "Требует структурированный формат диалогов",
                "Не подходит для прозы и романов"
            ]
        }
    
    def _add_gender_to_characters(self, characters: List[CharacterData], text: str) -> List[CharacterData]:
        """
        Добавляет информацию о поле к персонажам
        
        Args:
            characters: Список персонажей
            text: Исходный текст для контекста
            
        Returns:
            Список персонажей с определенным полом
        """
        logger.info(f"Определяю пол для {len(characters)} персонажей")
        
        for character in characters:
            try:
                # Определяем пол персонажа
                gender = self.gender_detector.detect_gender(
                    name=character.name,
                    description=character.description,
                    context=self._extract_character_context(character.name, text)
                )
                
                # Обновляем пол персонажа
                character.gender = gender
                
                # Получаем уверенность в определении
                confidence = self.gender_detector.get_confidence_score(
                    character.name,
                    character.description
                )
                
                logger.debug(f"Персонаж '{character.name}': пол={gender.value}, уверенность={confidence:.2f}")
                
            except Exception as e:
                logger.warning(f"Ошибка при определении пола для персонажа '{character.name}': {e}")
                # Оставляем значение по умолчанию (UNKNOWN)
        
        return characters
    
    def _extract_character_context(self, character_name: str, text: str) -> str:
        """
        Извлекает контекст упоминания персонажа из текста
        
        Args:
            character_name: Имя персонажа
            text: Исходный текст
            
        Returns:
            Контекст упоминания персонажа
        """
        import re
        
        # Ищем упоминания персонажа в тексте
        pattern = rf'\b{re.escape(character_name)}\b'
        matches = []
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            matches.append(context)
        
        # Возвращаем объединенный контекст (максимум 500 символов)
        full_context = " ... ".join(matches)
        return full_context[:500] if len(full_context) > 500 else full_context

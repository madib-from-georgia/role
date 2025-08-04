"""
Основной NLP процессор для обработки текстов и интеграции с базой данных
"""

import time
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from .nlp.extractors.character_extractor import CharacterExtractor
from .nlp.models import NLPResult, CharacterData, SpeechData, ExtractionStats
from ..database.crud import character as character_crud, text as text_crud
from ..database.models.character import Character
from ..schemas.character import CharacterCreate, CharacterUpdate


class NLPProcessor:
    """
    Основной NLP процессор для анализа литературных текстов
    
    Функции:
    - Извлечение персонажей из текстов
    - Атрибуция речи персонажам
    - Оценка важности персонажей
    - Сохранение результатов в базе данных
    """
    
    def __init__(self):
        self.character_extractor = CharacterExtractor()
        logger.info("NLP Processor инициализирован")
    
    async def process_text(self, text_id: int, db: Session, force_reprocess: bool = False) -> NLPResult:
        """
        Полная обработка текста с сохранением результатов в БД
        
        Args:
            text_id: ID текста для обработки
            db: Сессия базы данных
            force_reprocess: Принудительная переобработка
            
        Returns:
            Результат NLP анализа
        """
        start_time = time.time()
        
        logger.info(f"Начинаю обработку текста ID {text_id}")
        
        # Получаем текст из БД
        text_obj = text_crud.get(db, id=text_id)
        if not text_obj:
            logger.error(f"Текст с ID {text_id} не найден")
            raise ValueError(f"Текст с ID {text_id} не найден")
        
        logger.info(f"Найден текст: {text_obj.filename} (длина: {len(text_obj.content or '')} символов)")
        
        # Проверяем, есть ли уже обработанные персонажи (если не принудительная переобработка)
        if not force_reprocess:
            existing_characters = character_crud.get_multi_by_text(db, text_id=text_id)
            if existing_characters:
                logger.info(f"Найдено {len(existing_characters)} существующих персонажей. Используем кэш.")
                return self._build_result_from_db(text_id, existing_characters, db)
        
        # Извлекаем персонажей и речь из текста
        if not text_obj.content:
            logger.warning("Содержимое текста пустое")
            return self._create_empty_result(text_id)
        
        characters, speech_attributions, extraction_stats = await self.character_extractor.extract_characters_and_speech(
            text_obj.content
        )
        
        # Сохраняем персонажей в БД
        saved_characters = await self._save_characters_to_db(
            text_id, characters, speech_attributions, db
        )
        
        # Создаем результат
        processing_time = time.time() - start_time
        extraction_stats.extraction_time = processing_time
        
        result = NLPResult(
            text_id=text_id,
            characters=characters,
            speech_attributions=speech_attributions,
            extraction_stats=extraction_stats
        )
        
        logger.success(f"Обработка текста ID {text_id} завершена за {processing_time:.2f}с. "
                      f"Найдено {len(characters)} персонажей")
        
        return result
    
    async def _save_characters_to_db(
        self, 
        text_id: int, 
        characters: List[CharacterData], 
        speech_attributions: List[SpeechData],
        db: Session
    ) -> List[Character]:
        """
        Сохранение персонажей в базе данных
        
        Args:
            text_id: ID текста
            characters: Список персонажей
            speech_attributions: Список атрибуций речи
            db: Сессия БД
            
        Returns:
            Список сохраненных персонажей
        """
        logger.info(f"Сохраняю {len(characters)} персонажей в БД")
        
        # Удаляем существующих персонажей для данного текста (если переобрабатываем)
        existing_characters = character_crud.get_multi_by_text(db, text_id=text_id)
        for char in existing_characters:
            character_crud.remove(db, id=char.id)
        
        saved_characters = []
        
        for char_data in characters:
            # Подсчитываем количество речи для этого персонажа
            speech_count = len([s for s in speech_attributions if s.character_name == char_data.name])
            
            # Создаем объект персонажа для БД
            character_create = CharacterCreate(
                text_id=text_id,
                name=char_data.name,
                aliases=char_data.aliases,
                importance_score=char_data.importance_score,
                speech_attribution={
                    "speech_count": speech_count,
                    "source": char_data.source,
                    "mentions_count": char_data.mentions_count,
                    "first_mention_position": char_data.first_mention_position,
                    "description": char_data.description
                }
            )
            
            # Сохраняем в БД
            saved_character = character_crud.create(db, obj_in=character_create)
            saved_characters.append(saved_character)
            
            logger.debug(f"Сохранен персонаж: {char_data.name} (важность: {char_data.importance_score:.2f})")
        
        logger.success(f"Сохранено {len(saved_characters)} персонажей в БД")
        return saved_characters
    
    def _build_result_from_db(self, text_id: int, db_characters: List[Character], db: Session) -> NLPResult:
        """
        Создание результата на основе данных из БД (для кэшированных результатов)
        
        Args:
            text_id: ID текста
            db_characters: Персонажи из БД
            db: Сессия БД
            
        Returns:
            Результат NLP анализа
        """
        logger.debug("Строю результат на основе данных из БД")
        
        characters = []
        for db_char in db_characters:
            speech_attr = db_char.speech_attribution or {}
            
            char_data = CharacterData(
                name=db_char.name,
                aliases=db_char.aliases or [],
                description=speech_attr.get("description"),
                mentions_count=speech_attr.get("mentions_count", 0),
                first_mention_position=speech_attr.get("first_mention_position", 0),
                importance_score=db_char.importance_score or 0.0,
                source=speech_attr.get("source", "database")
            )
            characters.append(char_data)
        
        # Для кэшированных результатов создаем упрощенную статистику
        stats = ExtractionStats(
            method_used="cached_from_database",
            is_play_format=True,  # Предполагаем, что раньше было правильно определено
            has_character_section=True,
            total_characters=len(characters),
            total_speech_attributions=sum(c.speech_attribution.get("speech_count", 0) 
                                        for c in db_characters if c.speech_attribution),
            extraction_time=0.0,  # Кэш = мгновенно
            text_length=0,
            processing_errors=[]
        )
        
        result = NLPResult(
            text_id=text_id,
            characters=characters,
            speech_attributions=[],  # Для кэша не загружаем детальные атрибуции
            extraction_stats=stats
        )
        
        return result
    
    def _create_empty_result(self, text_id: int) -> NLPResult:
        """Создание пустого результата при ошибке"""
        logger.warning("Создаю пустой результат")
        
        stats = ExtractionStats(
            method_used="empty",
            is_play_format=False,
            has_character_section=False,
            total_characters=0,
            total_speech_attributions=0,
            extraction_time=0.0,
            text_length=0,
            processing_errors=["Пустое содержимое текста"]
        )
        
        return NLPResult(
            text_id=text_id,
            characters=[],
            speech_attributions=[],
            extraction_stats=stats
        )
    
    async def get_character_importance_ranking(self, text_id: int, db: Session) -> List[Character]:
        """
        Получение персонажей отсортированных по важности
        
        Args:
            text_id: ID текста
            db: Сессия БД
            
        Returns:
            Список персонажей отсортированных по убыванию важности
        """
        characters = character_crud.get_by_importance(db, text_id=text_id)
        logger.info(f"Получен рейтинг персонажей для текста {text_id}: {len(characters)} персонажей")
        return characters
    
    async def update_character_importance(self, character_id: int, new_score: float, db: Session) -> Optional[Character]:
        """
        Обновление важности персонажа
        
        Args:
            character_id: ID персонажа
            new_score: Новая оценка важности
            db: Сессия БД
            
        Returns:
            Обновленный персонаж или None
        """
        character = character_crud.update_importance(db, character_id=character_id, importance_score=new_score)
        if character:
            logger.info(f"Обновлена важность персонажа {character.name}: {new_score}")
        return character
    
    def get_processing_capabilities(self) -> dict:
        """Получение информации о возможностях процессора"""
        return {
            "supported_operations": [
                "character_extraction",
                "speech_attribution", 
                "importance_scoring",
                "database_integration"
            ],
            "supported_formats": self.character_extractor.get_supported_formats(),
            "extraction_capabilities": self.character_extractor.get_extraction_capabilities(),
            "database_features": [
                "Автоматическое сохранение персонажей",
                "Кэширование результатов",
                "Обновление важности персонажей",
                "Связывание с текстами"
            ]
        }


# Глобальный экземпляр процессора
_nlp_processor_instance = None

def get_nlp_processor() -> NLPProcessor:
    """Получение глобального экземпляра NLP процессора"""
    global _nlp_processor_instance
    if _nlp_processor_instance is None:
        _nlp_processor_instance = NLPProcessor()
    return _nlp_processor_instance

"""
Основной NLP процессор для обработки текстов и интеграции с базой данных
"""

import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from .nlp.extractors.character_extractor import CharacterExtractor
from .nlp.models import NLPResult, CharacterData, SpeechData, ExtractionStats
from ..database.crud import character as character_crud, text as text_crud
from ..database.models.character import Character
from ..schemas.character import CharacterCreate, CharacterUpdate
from ..parsers.content_models import StructuredContent, ContentType, DialogueElement, CharacterListElement


class NLPProcessor:
    """
    Основной NLP процессор для анализа литературных текстов
    
    Функции:
    - Извлечение персонажей из текстов
    - Атрибуция речи персонажам
    - Оценка важности персонажей
    - Сохранение результатов в базе данных
    """
    
    def __init__(self, logs_dir: Optional[str] = None):
        self.character_extractor = CharacterExtractor()
        
        # Настройка путей для логов
        if logs_dir is None:
            # По умолчанию logs рядом с backend
            backend_dir = Path(__file__).parent.parent.parent
            self.logs_dir = backend_dir / "logs"
        else:
            self.logs_dir = Path(logs_dir)
        
        # Создаем базовую директорию логов
        self.logs_dir.mkdir(exist_ok=True)
        
        logger.info(f"NLP Processor инициализирован. Логи сохраняются в: {self.logs_dir}")
    
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
        
        # Сохраняем результаты в JSON
        try:
            await self._save_nlp_results_to_json(text_obj, result)
        except Exception as e:
            logger.error(f"Ошибка при сохранении результатов в JSON: {e}")
        
        logger.success(f"Обработка текста ID {text_id} завершена за {processing_time:.2f}с. "
                      f"Найдено {len(characters)} персонажей")
        
        return result
    
    async def process_structured_content(self, structured_content: StructuredContent, text_id: int, db: Session) -> NLPResult:
        """
        Обработка структурированного контента для извлечения персонажей и речи.
        
        Args:
            structured_content: Структурированный контент
            text_id: ID текста для связывания результатов
            db: Сессия базы данных
            
        Returns:
            Результат NLP анализа
        """
        start_time = time.time()
        
        logger.info(f"Начинаю обработку структурированного контента для текста ID {text_id}")
        
        # Извлекаем персонажей из структурированного контента
        characters = self._extract_characters_from_structured_content(structured_content)
        
        # Извлекаем речевые атрибуции
        speech_attributions = self._extract_speech_from_structured_content(structured_content, characters)
        
        # Создаем статистику
        stats = ExtractionStats(
            method_used="structured_content_parser",
            is_play_format=len(structured_content.get_dialogues()) > 0,
            has_character_section=len(structured_content.get_character_lists()) > 0,
            total_characters=len(characters),
            total_speech_attributions=len(speech_attributions),
            extraction_time=time.time() - start_time,
            text_length=len(structured_content.raw_content),
            processing_errors=[]
        )
        
        # Сохраняем персонажей в БД
        saved_characters = await self._save_characters_to_db(
            text_id, characters, speech_attributions, db
        )
        
        # Создаем результат
        processing_time = time.time() - start_time
        stats.extraction_time = processing_time
        
        result = NLPResult(
            text_id=text_id,
            characters=characters,
            speech_attributions=speech_attributions,
            extraction_stats=stats
        )
        
        # Сохраняем результаты в JSON
        try:
            text_obj = text_crud.get(db, id=text_id)
            if text_obj:
                await self._save_nlp_results_to_json(text_obj, result)
        except Exception as e:
            logger.error(f"Ошибка при сохранении результатов в JSON: {e}")
        
        logger.success(f"Обработка структурированного контента завершена за {processing_time:.2f}с. "
                      f"Найдено {len(characters)} персонажей, {len(speech_attributions)} реплик")
        
        return result
    
    def _extract_characters_from_structured_content(self, content: StructuredContent) -> List[CharacterData]:
        """Извлечение персонажей из структурированного контента"""
        characters = []
        
        # Сначала извлекаем персонажей из списков персонажей
        for char_list in content.get_character_lists():
            if isinstance(char_list, CharacterListElement):
                for char_info in char_list.characters:
                    character = CharacterData(
                        name=char_info['name'],
                        aliases=[],
                        description=char_info.get('description', ''),
                        mentions_count=0,  # Будет пересчитан позже
                        first_mention_position=char_list.position,
                        importance_score=1.0,  # Персонажи из списка считаются важными
                        source="character_list"
                    )
                    characters.append(character)
        
        # Затем извлекаем персонажей из диалогов
        dialogue_speakers = set()
        for dialogue in content.get_dialogues():
            if isinstance(dialogue, DialogueElement) and dialogue.speaker_normalized:
                speaker = dialogue.speaker_normalized
                if speaker not in dialogue_speakers and not any(c.name == speaker for c in characters):
                    character = CharacterData(
                        name=speaker,
                        aliases=[],
                        description=None,
                        mentions_count=0,  # Будет пересчитан позже
                        first_mention_position=dialogue.position,
                        importance_score=0.8,  # Говорящие персонажи важны, но меньше чем из списка
                        source="dialogue_extraction"
                    )
                    characters.append(character)
                    dialogue_speakers.add(speaker)
        
        # Подсчитываем метрики для всех персонажей
        self._calculate_character_metrics_from_content(characters, content)
        
        logger.info(f"Извлечено {len(characters)} персонажей из структурированного контента")
        return characters
    
    def _extract_speech_from_structured_content(self, content: StructuredContent, characters: List[CharacterData]) -> List[SpeechData]:
        """Извлечение речевых атрибуций из структурированного контента"""
        speech_attributions = []
        
        # Создаем мапу персонажей для быстрого поиска
        character_map = {char.name: char for char in characters}
        
        # Извлекаем речь из диалогов
        for dialogue in content.get_dialogues():
            if isinstance(dialogue, DialogueElement) and dialogue.speaker_normalized:
                # Ищем персонажа
                character = character_map.get(dialogue.speaker_normalized)
                if character:
                    from .nlp.models import SpeechType
                    speech_data = SpeechData(
                        character_name=character.name,
                        text=dialogue.content,
                        position=dialogue.position,
                        speech_type=SpeechType.DIALOGUE,
                        confidence=dialogue.confidence,
                        context=None
                    )
                    speech_attributions.append(speech_data)
        
        logger.info(f"Найдено {len(speech_attributions)} речевых атрибуций")
        return speech_attributions
    
    def _calculate_character_metrics_from_content(self, characters: List[CharacterData], content: StructuredContent) -> None:
        """Подсчет метрик персонажей на основе структурированного контента"""
        text = content.raw_content.lower()
        text_length = len(content.raw_content)
        
        for character in characters:
            name_lower = character.name.lower()
            
            # Подсчитываем упоминания в тексте
            mentions = len([elem for elem in content.elements 
                           if name_lower in elem.content.lower()])
            
            # Подсчитываем диалоги персонажа
            dialogue_count = len([d for d in content.get_dialogues() 
                                if isinstance(d, DialogueElement) and 
                                d.speaker_normalized == character.name])
            
            character.mentions_count = mentions
            
            # Рассчитываем важность
            if dialogue_count > 0:
                # Персонаж говорит - высокая важность
                base_score = 0.8 + min(dialogue_count / 10.0, 0.2)
            elif mentions > 0:
                # Персонаж упоминается - средняя важность
                base_score = min(mentions / 20.0, 0.6)
            else:
                base_score = 0.1
            
            # Бонус за источник
            source_bonus = 0.1 if character.source == "character_list" else 0.0
            
            character.importance_score = min(base_score + source_bonus, 1.0)
    
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
        logger.info(f"Сохраняю {len(characters)} персонажей в БД для текста ID {text_id}")
        
        # Логируем имена персонажей для отладки
        character_names = [char.name for char in characters]
        logger.debug(f"Имена персонажей для сохранения: {character_names}")
        
        # Удаляем существующих персонажей для данного текста (если переобрабатываем)
        existing_characters = character_crud.get_multi_by_text(db, text_id=text_id)
        if existing_characters:
            logger.info(f"Удаляю {len(existing_characters)} существующих персонажей")
            for char in existing_characters:
                character_crud.remove(db, id=char.id)
        
        saved_characters = []
        
        for i, char_data in enumerate(characters):
            logger.debug(f"Обрабатываю персонажа {i+1}/{len(characters)}: {char_data.name}")
            
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
    
    async def _save_nlp_results_to_json(self, text_obj, result: NLPResult) -> None:
        """
        Сохранение результатов NLP анализа в JSON файлы
        
        Args:
            text_obj: Объект текста из БД
            result: Результат NLP анализа
        """
        # Создаем имя директории на основе названия файла текста
        safe_filename = self._sanitize_filename(text_obj.filename or f"text_{text_obj.id}")
        book_dir = self.logs_dir / safe_filename
        book_dir.mkdir(exist_ok=True)
        
        # Создаем временную метку для уникальности
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Конвертируем результат в сериализуемый формат
        json_data = {
            "metadata": {
                "text_id": result.text_id,
                "filename": text_obj.filename,
                "processing_time": result.extraction_stats.extraction_time,
                "timestamp": datetime.now().isoformat(),
                "processor_version": "1.0"
            },
            "extraction_stats": {
                "method_used": result.extraction_stats.method_used,
                "is_play_format": result.extraction_stats.is_play_format,
                "has_character_section": result.extraction_stats.has_character_section,
                "total_characters": result.extraction_stats.total_characters,
                "total_speech_attributions": result.extraction_stats.total_speech_attributions,
                "text_length": result.extraction_stats.text_length,
                "processing_errors": result.extraction_stats.processing_errors
            },
            "characters": [
                {
                    "name": char.name,
                    "aliases": char.aliases,
                    "description": char.description,
                    "mentions_count": char.mentions_count,
                    "first_mention_position": char.first_mention_position,
                    "importance_score": char.importance_score,
                    "source": char.source
                }
                for char in result.characters
            ],
            "speech_attributions": [
                {
                    "character_name": speech.character_name,
                    "text": speech.text,
                    "position": speech.position,
                    "speech_type": speech.speech_type.value if hasattr(speech.speech_type, 'value') else str(speech.speech_type),
                    "confidence": speech.confidence,
                    "context": speech.context
                }
                for speech in result.speech_attributions
            ]
        }
        
        # Сохраняем основной результат с временной меткой
        result_file = book_dir / f"nlp_result_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Сохраняем копию как latest
        latest_file = book_dir / "nlp_result_latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Обновляем глобальную latest директорию
        await self._update_latest_directory(book_dir, safe_filename)
        
        logger.info(f"Результаты NLP сохранены в: {result_file}")
        logger.info(f"Latest результат обновлен: {latest_file}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Очистка имени файла для безопасного использования в путях"""
        # Убираем расширение и нормализуем имя
        name = Path(filename).stem
        
        # Заменяем небезопасные символы
        safe_chars = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        safe_chars += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        
        cleaned = ''.join(c if c in safe_chars else '_' for c in name)
        
        # Ограничиваем длину
        if len(cleaned) > 100:
            cleaned = cleaned[:100]
        
        return cleaned or "unknown_text"
    
    async def _update_latest_directory(self, book_dir: Path, book_name: str) -> None:
        """Обновление latest директории"""
        latest_dir = self.logs_dir / "latest"
        latest_dir.mkdir(exist_ok=True)
        
        # Копируем latest файл в общую latest директорию
        source_file = book_dir / "nlp_result_latest.json"
        target_file = latest_dir / f"{book_name}_latest.json"
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            
            # Также создаем общий latest.json (последний обработанный файл)
            latest_global = latest_dir / "latest.json"
            shutil.copy2(source_file, latest_global)
            
            logger.debug(f"Обновлена latest директория: {target_file}")
    
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

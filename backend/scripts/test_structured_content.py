#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы новой системы структурированного контента
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к backend для импортов
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.crud import text as text_crud
from app.services.nlp_processor import get_nlp_processor
from app.parsers import fb2_parser, txt_parser
from loguru import logger

async def test_structured_content_parsing():
    """Тестирование парсинга в структурированный формат"""
    
    logger.info("=== Тест системы структурированного контента ===")
    
    # Тестовый FB2 файл
    fb2_file = Path(__file__).parent.parent.parent / "books" / "fb2" / "15) 1896 - Дядя Ваня.fb2"
    
    if not fb2_file.exists():
        logger.error(f"Тестовый файл не найден: {fb2_file}")
        return
    
    logger.info(f"Тестируем парсинг файла: {fb2_file}")
    
    try:
        # Парсинг в новый структурированный формат
        logger.info("🔄 Парсинг в структурированный формат...")
        structured_content = fb2_parser.parse_to_structured_content(str(fb2_file))
        
        logger.success(f"✅ Парсинг завершен!")
        logger.info(f"📊 Статистика:")
        logger.info(f"   Всего элементов: {len(structured_content.elements)}")
        logger.info(f"   Диалогов: {len(structured_content.get_dialogues())}")
        logger.info(f"   Списков персонажей: {len(structured_content.get_character_lists())}")
        logger.info(f"   Говорящих: {len(structured_content.get_speakers())}")
        
        # Показываем найденных говорящих
        speakers = structured_content.get_speakers()
        if speakers:
            logger.info(f"🎭 Найдены говорящие персонажи:")
            for speaker in speakers[:10]:  # Показываем первых 10
                dialogue_count = structured_content.get_dialogue_count_by_speaker().get(speaker, 0)
                logger.info(f"   • {speaker} ({dialogue_count} реплик)")
        
        # Показываем персонажей из списков
        char_lists = structured_content.get_character_lists()
        if char_lists:
            logger.info(f"📋 Персонажи из списков:")
            for char_list in char_lists:
                logger.info(f"   Секция: {char_list.content}")
                for char in char_list.characters[:5]:  # Показываем первых 5
                    desc = char.get('description', '')
                    logger.info(f"     • {char['name']}{' - ' + desc if desc else ''}")
        
        # Показываем примеры диалогов
        dialogues = structured_content.get_dialogues()
        if dialogues:
            logger.info(f"💬 Примеры диалогов:")
            for dialogue in dialogues[:5]:  # Показываем первые 5
                speaker = dialogue.speaker or "Неизвестно"
                text = dialogue.content[:50] + "..." if len(dialogue.content) > 50 else dialogue.content
                logger.info(f"   {speaker}: {text}")
        
        # Тестируем NLP обработку структурированного контента
        logger.info("\n🧠 Тестируем NLP обработку...")
        
        # Получаем сессию БД
        db: Session = next(get_db())
        
        try:
            # Получаем процессор NLP
            nlp_processor = get_nlp_processor()
            
            # Создаем тестовый текст в БД (если его нет)
            test_text = text_crud.get_by_filename(db, filename=fb2_file.name)
            if not test_text:
                from app.schemas.text import TextCreate
                text_create = TextCreate(
                    filename=fb2_file.name,
                    content=structured_content.raw_content,
                    project_id=1  # Предполагаем, что есть проект с ID 1
                )
                test_text = text_crud.create(db, obj_in=text_create)
                logger.info(f"Создан тестовый текст в БД с ID: {test_text.id}")
            else:
                logger.info(f"Используем существующий текст с ID: {test_text.id}")
            
            # Обрабатываем структурированный контент
            result = await nlp_processor.process_structured_content(
                structured_content, test_text.id, db
            )
            
            logger.success(f"✅ NLP обработка завершена!")
            logger.info(f"📈 Результаты:")
            logger.info(f"   Найдено персонажей: {len(result.characters)}")
            logger.info(f"   Речевых атрибуций: {len(result.speech_attributions)}")
            logger.info(f"   Метод: {result.extraction_stats.method_used}")
            logger.info(f"   Время обработки: {result.extraction_stats.extraction_time:.2f}с")
            
            # Показываем найденных персонажей
            if result.characters:
                logger.info(f"🎭 Найденные персонажи:")
                for char in sorted(result.characters, key=lambda x: x.importance_score, reverse=True)[:10]:
                    logger.info(f"   • {char.name} (важность: {char.importance_score:.2f}, источник: {char.source})")
            
            # Показываем речевые атрибуции
            if result.speech_attributions:
                logger.info(f"💬 Речевые атрибуции:")
                speech_by_char = {}
                for speech in result.speech_attributions:
                    char_name = speech.character_name
                    speech_by_char[char_name] = speech_by_char.get(char_name, 0) + 1
                
                for char_name, count in sorted(speech_by_char.items(), key=lambda x: x[1], reverse=True)[:10]:
                    logger.info(f"   • {char_name}: {count} реплик")
            
            logger.success("🎉 Все тесты прошли успешно!")
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

async def compare_old_vs_new():
    """Сравнение старого и нового подходов"""
    
    logger.info("\n=== Сравнение старого и нового подходов ===")
    
    fb2_file = Path(__file__).parent.parent.parent / "books" / "fb2" / "15) 1896 - Дядя Ваня.fb2"
    
    if not fb2_file.exists():
        logger.warning("Файл для сравнения не найден")
        return
    
    try:
        # Старый подход
        logger.info("🔄 Тестируем старый подход...")
        old_result = fb2_parser.parse_file(str(fb2_file))
        old_content = old_result['content']
        
        # Новый подход
        logger.info("🔄 Тестируем новый подход...")
        new_content = fb2_parser.parse_to_structured_content(str(fb2_file))
        
        logger.info("📊 Сравнение результатов:")
        logger.info(f"   Старый: длина текста {len(old_content)} символов")
        logger.info(f"   Новый: {len(new_content.elements)} элементов, {len(new_content.raw_content)} символов")
        logger.info(f"   Новый: {len(new_content.get_dialogues())} диалогов, {len(new_content.get_character_lists())} списков персонажей")
        
        # Проверяем, есть ли различия в тексте
        text_diff = abs(len(old_content) - len(new_content.raw_content))
        logger.info(f"   Разница в длине текста: {text_diff} символов")
        
        if text_diff < 100:
            logger.success("✅ Тексты практически идентичны")
        else:
            logger.warning("⚠️ Значительная разница в тексте")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при сравнении: {e}")

if __name__ == "__main__":
    asyncio.run(test_structured_content_parsing())
    asyncio.run(compare_old_vs_new())

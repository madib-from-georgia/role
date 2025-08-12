"""
Тестирование системы версионирования чеклистов
"""

import asyncio
import json
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.services.checklist_version_service import checklist_version_service
from app.services.response_migration_service import response_migration_service
from app.database.crud.crud_checklist import checklist as checklist_crud
from loguru import logger


def get_db_sync():
    """Синхронная версия получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_json_v2():
    """Создает тестовый JSON файл версии 2 с изменениями"""
    return json.dumps({
        "external_id": "physical-portrait",
        "version": "2.0",
        "title": "Физический портрет актера (обновленная версия)",
        "description": "Обновленный чеклист для анализа физических характеристик персонажа",
        "sections": [
            {
                "external_id": "general_appearance",
                "title": "Общий внешний вид",
                "description": "Основные физические характеристики",
                "subsections": [
                    {
                        "external_id": "basic_params",
                        "title": "Базовые параметры",
                        "description": "Основные физические параметры персонажа",
                        "question_groups": [
                            {
                                "external_id": "height_weight_group",
                                "title": "Рост и телосложение",
                                "questions": [
                                    {
                                        "external_id": "height_question",
                                        "text": "Какой рост у персонажа? (обновленный вопрос)",
                                        "answer_type": "single_choice",
                                        "source_type": "user_input",
                                        "answers": [
                                            {
                                                "external_id": "height_very_short",
                                                "value_male": "Очень низкий (до 160 см)",
                                                "value_female": "Очень низкая (до 150 см)",
                                                "exported_value_male": "very_short_male",
                                                "exported_value_female": "very_short_female"
                                            },
                                            {
                                                "external_id": "height_short",
                                                "value_male": "Низкий (160-170 см)",
                                                "value_female": "Низкая (150-160 см)",
                                                "exported_value_male": "short_male",
                                                "exported_value_female": "short_female"
                                            },
                                            {
                                                "external_id": "height_medium",
                                                "value_male": "Средний (170-180 см)",
                                                "value_female": "Средняя (160-170 см)",
                                                "exported_value_male": "medium_male",
                                                "exported_value_female": "medium_female"
                                            },
                                            {
                                                "external_id": "height_tall",
                                                "value_male": "Высокий (180-190 см)",
                                                "value_female": "Высокая (170-180 см)",
                                                "exported_value_male": "tall_male",
                                                "exported_value_female": "tall_female"
                                            }
                                        ]
                                    },
                                    {
                                        "external_id": "new_question_build",
                                        "text": "Какое телосложение у персонажа? (новый вопрос)",
                                        "answer_type": "single_choice",
                                        "source_type": "user_input",
                                        "answers": [
                                            {
                                                "external_id": "build_slim",
                                                "value_male": "Худощавое",
                                                "value_female": "Худощавое",
                                                "exported_value_male": "slim_male",
                                                "exported_value_female": "slim_female"
                                            },
                                            {
                                                "external_id": "build_athletic",
                                                "value_male": "Спортивное",
                                                "value_female": "Спортивное",
                                                "exported_value_male": "athletic_male",
                                                "exported_value_female": "athletic_female"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }, ensure_ascii=False, indent=2)


def test_version_service():
    """Тестирует сервис версионирования"""
    logger.info("=== Тестирование системы версионирования ===")
    
    db = next(get_db_sync())
    
    try:
        # 1. Получаем существующий чеклист
        existing_checklist = checklist_crud.get_by_external_id(db, "physical-portrait")
        if not existing_checklist:
            logger.error("Чеклист не найден. Сначала запустите test_import.py")
            return
        
        logger.info(f"Найден чеклист: {existing_checklist.title} (версия {existing_checklist.version})")
        
        # 2. Создаем новую версию JSON
        new_json = create_test_json_v2()
        logger.info("Создан тестовый JSON версии 2.0")
        
        # 3. Проверяем наличие обновлений
        logger.info("\n--- Проверка обновлений ---")
        update_info = checklist_version_service.check_for_updates(
            existing_checklist.id, new_json
        )
        logger.info(f"Результат проверки обновлений: {update_info}")
        
        # 4. Анализируем изменения
        logger.info("\n--- Анализ изменений ---")
        changes = checklist_version_service.analyze_changes(
            existing_checklist.id, new_json
        )
        logger.info(f"Найдено изменений:")
        logger.info(f"- Чеклист: {changes.get('checklist_changes', {})}")
        logger.info(f"- Секции: {len(changes.get('entity_matches', {}).get('sections', []))} совпадений")
        logger.info(f"- Вопросы: {len(changes.get('entity_matches', {}).get('questions', []))} совпадений")
        
        # 5. Анализируем влияние на ответы пользователей
        logger.info("\n--- Анализ влияния на ответы ---")
        impact = response_migration_service.analyze_migration_impact(
            db, existing_checklist.id, changes.get("entity_matches", {})
        )
        logger.info(f"Влияние на ответы: {impact}")
        
        # 6. Тестируем обновление (dry run)
        logger.info("\n--- Тестовое обновление ---")
        result = checklist_version_service.update_checklist(
            existing_checklist.id, new_json, force_update=False, migrate_responses=True
        )
        logger.info(f"Результат обновления: {result}")
        
        # 7. Проверяем обновленный чеклист
        updated_checklist = checklist_crud.get(db, id=existing_checklist.id)
        logger.info(f"Обновленный чеклист: {updated_checklist.title} (версия {updated_checklist.version})")
        
        # 8. Создаем отчет о миграции
        logger.info("\n--- Отчет о миграции ---")
        report = response_migration_service.create_migration_report(
            db, existing_checklist.id, impact, result.get("migration_results")
        )
        logger.info(f"Отчет: {json.dumps(report, ensure_ascii=False, indent=2)}")
        
        logger.success("✅ Тестирование системы версионирования завершено успешно!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def test_entity_matcher():
    """Тестирует EntityMatcher отдельно"""
    logger.info("=== Тестирование EntityMatcher ===")
    
    db = next(get_db_sync())
    
    try:
        from app.services.entity_matcher import EntityMatcher
        
        # Получаем существующий чеклист
        existing_checklist = checklist_crud.get_by_external_id(db, "physical-portrait")
        if not existing_checklist:
            logger.error("Чеклист не найден")
            return
        
        # Создаем новую версию
        new_json = create_test_json_v2()
        
        # Парсим новую версию
        from app.services.checklist_json_parser_new import ChecklistJsonParserNew
        parser = ChecklistJsonParserNew()
        new_data = parser.parse_json_string(new_json)
        
        # Тестируем сопоставление
        matcher = EntityMatcher()
        
        # Сопоставляем вопросы
        old_questions = []
        for section in existing_checklist.sections:
            for subsection in section.subsections:
                for group in subsection.question_groups:
                    old_questions.extend(group.questions)
        
        new_questions = []
        for section_data in new_data["sections"]:
            for subsection_data in section_data["subsections"]:
                for group_data in subsection_data["question_groups"]:
                    new_questions.extend(group_data["questions"])
        
        # Преобразуем словари в объекты для совместимости с EntityMatcher
        class MockQuestion:
            def __init__(self, data):
                self.external_id = data.get("external_id", data.get("id", ""))
                self.text = data.get("text", data.get("title", ""))
                self.answer_type = data.get("answer_type", data.get("answerType", ""))
        
        new_question_objects = [MockQuestion(q) for q in new_questions]
        question_matches = matcher.match_questions(old_questions, new_question_objects)
        
        logger.info(f"Найдено {len(question_matches)} совпадений вопросов:")
        for match in question_matches:
            logger.info(f"- {match.match_type.value}: {match.confidence:.2f}")
            if match.old_entity:
                logger.info(f"  Старый: {match.old_entity.text[:50]}...")
            if match.new_entity:
                logger.info(f"  Новый: {match.new_entity.text[:50]}...")
        
        logger.success("✅ Тестирование EntityMatcher завершено!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования EntityMatcher: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    # Настройка логирования
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    print("Выберите тест:")
    print("1. Полное тестирование системы версионирования")
    print("2. Тестирование EntityMatcher")
    print("3. Оба теста")
    
    choice = input("Введите номер (1-3): ").strip()
    
    if choice == "1":
        test_version_service()
    elif choice == "2":
        test_entity_matcher()
    elif choice == "3":
        test_entity_matcher()
        print("\n" + "="*50 + "\n")
        test_version_service()
    else:
        print("Неверный выбор")
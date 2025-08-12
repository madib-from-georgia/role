"""
Скрипт для удаления всех чеклистов из базы данных
Используется только для разработки!
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import SessionLocal, init_db
from app.database.crud.crud_checklist import checklist
from app.database.crud.crud_checklist_response import checklist_response
from app.database.models.checklist import (
    Checklist, ChecklistSection, ChecklistSubsection,
    ChecklistQuestionGroup, ChecklistQuestion, ChecklistAnswer, ChecklistResponse, ChecklistResponseHistory
)
from loguru import logger


async def clear_all_checklists(force=False):
    """Удаление всех чеклистов из базы данных"""
    
    # Инициализируем базу данных
    await init_db()
    
    db: Session = SessionLocal()
    
    try:
        logger.warning("🚨 ВНИМАНИЕ: Удаление всех чеклистов из базы данных!")
        logger.warning("Это действие необратимо и удалит все данные чеклистов!")
        
        # Подсчитываем количество записей
        checklists_count = db.query(Checklist).count()
        sections_count = db.query(ChecklistSection).count()
        subsections_count = db.query(ChecklistSubsection).count()
        question_groups_count = db.query(ChecklistQuestionGroup).count()
        questions_count = db.query(ChecklistQuestion).count()
        answers_count = db.query(ChecklistAnswer).count()
        responses_count = db.query(ChecklistResponse).count()
        history_count = db.query(ChecklistResponseHistory).count()
        
        logger.info(f"Найдено записей для удаления:")
        logger.info(f"  - Чеклистов: {checklists_count}")
        logger.info(f"  - Секций: {sections_count}")
        logger.info(f"  - Подсекций: {subsections_count}")
        logger.info(f"  - Групп вопросов: {question_groups_count}")
        logger.info(f"  - Вопросов: {questions_count}")
        logger.info(f"  - Вариантов ответов: {answers_count}")
        logger.info(f"  - Ответов пользователей: {responses_count}")
        logger.info(f"  - Истории ответов: {history_count}")
        
        if checklists_count == 0:
            logger.info("База данных уже пуста. Ничего удалять не нужно.")
            return
        
        # Запрашиваем подтверждение только если не force
        if not force:
            confirm = input("\nВы уверены, что хотите удалить ВСЕ чеклисты? (yes/no): ")
            
            if confirm.lower() != 'yes':
                logger.info("Операция отменена пользователем.")
                return
        
        logger.info("Начинаю удаление...")
        
        # Отключаем проверку внешних ключей для SQLite
        db.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Удаляем в правильном порядке (сначала зависимые таблицы)
        
        # 1. Удаляем историю ответов
        deleted_history = db.query(ChecklistResponseHistory).delete(synchronize_session=False)
        logger.info(f"Удалено записей истории: {deleted_history}")
        
        # 2. Удаляем ответы пользователей
        deleted_responses = db.query(ChecklistResponse).delete(synchronize_session=False)
        logger.info(f"Удалено ответов пользователей: {deleted_responses}")
        
        # 3. Удаляем варианты ответов
        deleted_answers = db.query(ChecklistAnswer).delete(synchronize_session=False)
        logger.info(f"Удалено вариантов ответов: {deleted_answers}")
        
        # 4. Удаляем вопросы
        deleted_questions = db.query(ChecklistQuestion).delete(synchronize_session=False)
        logger.info(f"Удалено вопросов: {deleted_questions}")
        
        # 5. Удаляем группы вопросов
        deleted_groups = db.query(ChecklistQuestionGroup).delete(synchronize_session=False)
        logger.info(f"Удалено групп вопросов: {deleted_groups}")
        
        # 6. Удаляем подсекции
        deleted_subsections = db.query(ChecklistSubsection).delete(synchronize_session=False)
        logger.info(f"Удалено подсекций: {deleted_subsections}")
        
        # 7. Удаляем секции
        deleted_sections = db.query(ChecklistSection).delete(synchronize_session=False)
        logger.info(f"Удалено секций: {deleted_sections}")
        
        # 8. Удаляем чеклисты
        deleted_checklists = db.query(Checklist).delete(synchronize_session=False)
        logger.info(f"Удалено чеклистов: {deleted_checklists}")
        
        # Подтверждаем изменения
        db.commit()
        
        # Включаем проверку внешних ключей обратно
        db.execute(text("PRAGMA foreign_keys = ON"))
        
        logger.success("✅ Все чеклисты успешно удалены из базы данных!")
        
        # Проверяем, что все удалено
        remaining_checklists = db.query(Checklist).count()
        remaining_sections = db.query(ChecklistSection).count()
        remaining_questions = db.query(ChecklistQuestion).count()
        remaining_answers = db.query(ChecklistAnswer).count()
        remaining_responses = db.query(ChecklistResponse).count()
        remaining_history = db.query(ChecklistResponseHistory).count()
        
        logger.info(f"Проверка после удаления:")
        logger.info(f"  - Осталось чеклистов: {remaining_checklists}")
        logger.info(f"  - Осталось секций: {remaining_sections}")
        logger.info(f"  - Осталось вопросов: {remaining_questions}")
        logger.info(f"  - Осталось вариантов ответов: {remaining_answers}")
        logger.info(f"  - Осталось ответов пользователей: {remaining_responses}")
        logger.info(f"  - Осталось записей истории: {remaining_history}")
        
    except Exception as e:
        logger.error(f"Ошибка при удалении чеклистов: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def clear_specific_checklist(slug: str, force=False):
    """Удаление конкретного чеклиста по slug"""
    
    await init_db()
    db: Session = SessionLocal()
    
    try:
        # Находим чеклист
        checklist_obj = checklist.get_by_slug(db, slug)
        
        if not checklist_obj:
            logger.error(f"Чеклист с slug '{slug}' не найден")
            return
        
        logger.warning(f"🚨 Удаление чеклиста: {checklist_obj.title}")
        
        # Подсчитываем связанные записи
        sections_count = db.query(ChecklistSection).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).count()
        
        questions_count = db.query(ChecklistQuestion).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).count()
        
        answers_count = db.query(ChecklistAnswer).join(
            ChecklistQuestion
        ).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).count()
        
        responses_count = db.query(ChecklistResponse).join(
            ChecklistQuestion
        ).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).count()
        
        history_count = db.query(ChecklistResponseHistory).join(
            ChecklistResponse
        ).join(
            ChecklistQuestion
        ).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).count()
        
        logger.info(f"Найдено связанных записей:")
        logger.info(f"  - Секций: {sections_count}")
        logger.info(f"  - Вопросов: {questions_count}")
        logger.info(f"  - Вариантов ответов: {answers_count}")
        logger.info(f"  - Ответов пользователей: {responses_count}")
        logger.info(f"  - Истории ответов: {history_count}")
        
        # Запрашиваем подтверждение только если не force
        if not force:
            confirm = input(f"\nУдалить чеклист '{checklist_obj.title}'? (yes/no): ")
            
            if confirm.lower() != 'yes':
                logger.info("Операция отменена пользователем.")
                return
        
        # Удаляем связанные записи
        # 1. Удаляем историю ответов
        deleted_history = db.query(ChecklistResponseHistory).join(
            ChecklistResponse
        ).join(
            ChecklistQuestion
        ).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete(synchronize_session=False)
        
        # 2. Удаляем ответы пользователей
        deleted_responses = db.query(ChecklistResponse).join(
            ChecklistQuestion
        ).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete(synchronize_session=False)
        
        # 3. Удаляем варианты ответов
        deleted_answers = db.query(ChecklistAnswer).join(
            ChecklistQuestion
        ).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete(synchronize_session=False)
        
        # 4. Удаляем вопросы
        deleted_questions = db.query(ChecklistQuestion).join(
            ChecklistQuestionGroup
        ).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete(synchronize_session=False)
        
        deleted_groups = db.query(ChecklistQuestionGroup).join(
            ChecklistSubsection
        ).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete(synchronize_session=False)
        
        deleted_subsections = db.query(ChecklistSubsection).join(
            ChecklistSection
        ).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete(synchronize_session=False)
        
        deleted_sections = db.query(ChecklistSection).filter(
            ChecklistSection.checklist_id == checklist_obj.id
        ).delete()
        
        # Удаляем сам чеклист
        db.delete(checklist_obj)
        
        db.commit()
        
        logger.success(f"✅ Чеклист '{checklist_obj.title}' успешно удален!")
        logger.info(f"Удалено записей:")
        logger.info(f"  - Истории ответов: {deleted_history}")
        logger.info(f"  - Ответов пользователей: {deleted_responses}")
        logger.info(f"  - Вариантов ответов: {deleted_answers}")
        logger.info(f"  - Вопросов: {deleted_questions}")
        logger.info(f"  - Групп: {deleted_groups}")
        logger.info(f"  - Подсекций: {deleted_subsections}")
        logger.info(f"  - Секций: {deleted_sections}")
        
    except Exception as e:
        logger.error(f"Ошибка при удалении чеклиста: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def list_checklists():
    """Показать список всех чеклистов"""
    
    await init_db()
    db: Session = SessionLocal()
    
    try:
        checklists = checklist.get_active_checklists(db)
        
        if not checklists:
            logger.info("В базе данных нет чеклистов.")
            return
        
        logger.info(f"Найдено чеклистов: {len(checklists)}")
        logger.info("Список чеклистов:")
        
        for i, cl in enumerate(checklists, 1):
            logger.info(f"  {i}. {cl.title} (slug: {cl.slug}, ID: {cl.id})")
            
    finally:
        db.close()


async def main():
    """Главная функция"""
    
    if len(sys.argv) < 2:
        logger.info("Аргументы не указаны. Показываю список чеклистов...")
        await list_checklists()
        logger.info("\nИспользование:")
        logger.info("  python clear_checklists.py --list                    # Показать список чеклистов")
        logger.info("  python clear_checklists.py --clear-all              # Удалить все чеклисты")
        logger.info("  python clear_checklists.py --clear-all --force      # Удалить все чеклисты без подтверждения")
        logger.info("  python clear_checklists.py --clear-slug <slug>      # Удалить конкретный чеклист")
        logger.info("  python clear_checklists.py --clear-slug <slug> --force # Удалить конкретный чеклист без подтверждения")
        return
    
    command = sys.argv[1]
    force = "--force" in sys.argv
    
    if command == "--list":
        await list_checklists()
    elif command == "--clear-all":
        await clear_all_checklists(force=force)
    elif command == "--clear-slug":
        if len(sys.argv) < 3:
            logger.error("Необходимо указать slug чеклиста")
            return
        slug = sys.argv[2]
        await clear_specific_checklist(slug, force=force)
    else:
        logger.error(f"Неизвестная команда: {command}")


if __name__ == "__main__":
    asyncio.run(main()) 

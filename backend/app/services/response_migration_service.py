"""
Сервис для миграции ответов пользователей при обновлении чеклистов
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from app.database.crud.crud_checklist_response import checklist_response
from app.database.crud.crud_checklist import checklist_question, checklist_answer
from app.database.models.checklist import ChecklistResponse, ChecklistQuestion, ChecklistAnswer
from app.services.entity_matcher import EntityMatcher, MatchType, EntityMatch
from app.schemas.checklist import ChecklistResponseUpdate


class MigrationStrategy:
    """Стратегии миграции ответов"""
    
    PRESERVE_EXACT = "preserve_exact"           # Сохранить точные совпадения
    MIGRATE_SIMILAR = "migrate_similar"         # Мигрировать похожие
    ARCHIVE_DELETED = "archive_deleted"         # Архивировать удаленные
    PROMPT_USER = "prompt_user"                 # Запросить решение пользователя


class ResponseMigrationService:
    """
    Сервис для миграции ответов пользователей при обновлении чеклистов
    
    Основные функции:
    - Анализ влияния изменений на существующие ответы
    - Автоматическая миграция совместимых ответов
    - Архивирование несовместимых ответов
    - Уведомление пользователей о необходимых действиях
    """
    
    def __init__(self):
        self.entity_matcher = EntityMatcher()
        self.migration_strategies = [
            MigrationStrategy.PRESERVE_EXACT,
            MigrationStrategy.MIGRATE_SIMILAR,
            MigrationStrategy.ARCHIVE_DELETED
        ]
    
    def analyze_migration_impact(
        self, 
        db: Session, 
        checklist_id: int, 
        entity_matches: Dict[str, List[EntityMatch]]
    ) -> Dict[str, Any]:
        """
        Анализирует влияние изменений чеклиста на существующие ответы пользователей
        
        Args:
            db: Сессия базы данных
            checklist_id: ID чеклиста
            entity_matches: Результаты сопоставления сущностей
            
        Returns:
            Анализ влияния на ответы пользователей
        """
        logger.info(f"Анализ влияния миграции для чеклиста {checklist_id}")
        
        # Получаем все ответы пользователей для этого чеклиста
        existing_responses = checklist_response.get_by_character_and_checklist(db, None, checklist_id)
        
        if not existing_responses:
            return {
                "total_responses": 0,
                "affected_responses": 0,
                "migration_plan": {},
                "user_actions_required": []
            }
        
        # Группируем ответы по вопросам
        responses_by_question = {}
        for response in existing_responses:
            question_id = response.question_id
            if question_id not in responses_by_question:
                responses_by_question[question_id] = []
            responses_by_question[question_id].append(response)
        
        # Анализируем влияние на каждый вопрос
        migration_plan = {}
        affected_responses = 0
        user_actions_required = []
        
        question_matches = entity_matches.get("questions", [])
        
        for match in question_matches:
            if match.old_entity:
                old_question_id = match.old_entity.id
                question_responses = responses_by_question.get(old_question_id, [])
                
                if question_responses:
                    plan = self._create_question_migration_plan(match, question_responses)
                    migration_plan[old_question_id] = plan
                    
                    if plan["strategy"] != MigrationStrategy.PRESERVE_EXACT:
                        affected_responses += len(question_responses)
                    
                    if plan["requires_user_action"]:
                        user_actions_required.append({
                            "question_id": old_question_id,
                            "question_text": match.old_entity.text[:100] + "...",
                            "affected_users": len(set(r.character_id for r in question_responses)),
                            "reason": plan["reason"]
                        })
        
        return {
            "total_responses": len(existing_responses),
            "affected_responses": affected_responses,
            "migration_plan": migration_plan,
            "user_actions_required": user_actions_required
        }
    
    def _create_question_migration_plan(
        self, 
        question_match: EntityMatch, 
        responses: List[ChecklistResponse]
    ) -> Dict[str, Any]:
        """
        Создает план миграции для конкретного вопроса
        
        Args:
            question_match: Результат сопоставления вопроса
            responses: Ответы пользователей на этот вопрос
            
        Returns:
            План миграции для вопроса
        """
        plan = {
            "strategy": None,
            "target_question_id": None,
            "requires_user_action": False,
            "reason": "",
            "response_count": len(responses),
            "affected_users": len(set(r.character_id for r in responses))
        }
        
        if question_match.match_type == MatchType.EXACT:
            # Точное совпадение - ответы можно сохранить как есть
            plan.update({
                "strategy": MigrationStrategy.PRESERVE_EXACT,
                "target_question_id": question_match.new_entity.id,
                "requires_user_action": False,
                "reason": "Вопрос не изменился"
            })
        
        elif question_match.match_type == MatchType.SIMILAR:
            # Похожий вопрос - нужно проверить совместимость ответов
            if self._are_answers_compatible(question_match.old_entity, question_match.new_entity):
                plan.update({
                    "strategy": MigrationStrategy.MIGRATE_SIMILAR,
                    "target_question_id": question_match.new_entity.id,
                    "requires_user_action": False,
                    "reason": f"Вопрос изменился, но ответы совместимы (уверенность: {question_match.confidence:.2f})"
                })
            else:
                plan.update({
                    "strategy": MigrationStrategy.PROMPT_USER,
                    "target_question_id": question_match.new_entity.id,
                    "requires_user_action": True,
                    "reason": "Вопрос изменился, ответы могут быть несовместимы"
                })
        
        elif question_match.match_type == MatchType.DELETED:
            # Вопрос удален - архивируем ответы
            plan.update({
                "strategy": MigrationStrategy.ARCHIVE_DELETED,
                "target_question_id": None,
                "requires_user_action": True,
                "reason": "Вопрос удален из чеклиста"
            })
        
        elif question_match.match_type == MatchType.NEW:
            # Новый вопрос - ответов пока нет
            plan.update({
                "strategy": MigrationStrategy.PRESERVE_EXACT,
                "target_question_id": question_match.new_entity.id,
                "requires_user_action": False,
                "reason": "Новый вопрос"
            })
        
        return plan
    
    def _are_answers_compatible(self, old_question: ChecklistQuestion, new_question) -> bool:
        """
        Проверяет совместимость ответов между старым и новым вопросом
        
        Args:
            old_question: Старый вопрос
            new_question: Новый вопрос
            
        Returns:
            True если ответы совместимы
        """
        # Проверяем тип ответа
        if old_question.answer_type != new_question.answer_type:
            return False
        
        # Для точной проверки нужно сравнить доступные ответы
        old_answers = {a.external_id: a for a in old_question.answers}
        new_answers = {a.external_id: a for a in new_question.answers}
        
        # Если все старые ответы есть в новых - совместимо
        return old_answers.keys().issubset(new_answers.keys())
    
    def execute_migration(
        self, 
        db: Session, 
        checklist_id: int, 
        migration_plan: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Выполняет миграцию ответов пользователей
        
        Args:
            db: Сессия базы данных
            checklist_id: ID чеклиста
            migration_plan: План миграции
            dry_run: Режим тестирования без изменений
            
        Returns:
            Результаты миграции
        """
        logger.info(f"Выполнение миграции для чеклиста {checklist_id} (dry_run={dry_run})")
        
        results = {
            "migrated_responses": 0,
            "archived_responses": 0,
            "failed_migrations": 0,
            "errors": []
        }
        
        for old_question_id, plan in migration_plan.items():
            try:
                question_results = self._migrate_question_responses(
                    db, old_question_id, plan, dry_run
                )
                
                results["migrated_responses"] += question_results.get("migrated", 0)
                results["archived_responses"] += question_results.get("archived", 0)
                results["failed_migrations"] += question_results.get("failed", 0)
                
                if question_results.get("errors"):
                    results["errors"].extend(question_results["errors"])
                    
            except Exception as e:
                logger.error(f"Ошибка миграции вопроса {old_question_id}: {str(e)}")
                results["failed_migrations"] += 1
                results["errors"].append(f"Вопрос {old_question_id}: {str(e)}")
        
        if not dry_run:
            db.commit()
            logger.success(f"Миграция завершена: {results}")
        else:
            logger.info(f"Тестовая миграция завершена: {results}")
        
        return results
    
    def _migrate_question_responses(
        self, 
        db: Session, 
        old_question_id: int, 
        plan: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """
        Мигрирует ответы для конкретного вопроса
        
        Args:
            db: Сессия базы данных
            old_question_id: ID старого вопроса
            plan: План миграции для вопроса
            dry_run: Режим тестирования
            
        Returns:
            Результаты миграции вопроса
        """
        results = {
            "migrated": 0,
            "archived": 0,
            "failed": 0,
            "errors": []
        }
        
        # Получаем все ответы на этот вопрос
        responses = db.query(ChecklistResponse).filter(
            ChecklistResponse.question_id == old_question_id,
            ChecklistResponse.is_current == True
        ).all()
        
        strategy = plan["strategy"]
        
        if strategy == MigrationStrategy.PRESERVE_EXACT:
            # Ответы остаются как есть (вопрос не изменился)
            results["migrated"] = len(responses)
        
        elif strategy == MigrationStrategy.MIGRATE_SIMILAR:
            # Мигрируем ответы на новый вопрос
            target_question_id = plan["target_question_id"]
            
            for response in responses:
                try:
                    if not dry_run:
                        # Обновляем question_id в ответе
                        response.question_id = target_question_id
                        response.updated_at = datetime.utcnow()
                        db.add(response)
                    
                    results["migrated"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Ответ {response.id}: {str(e)}")
        
        elif strategy == MigrationStrategy.ARCHIVE_DELETED:
            # Архивируем ответы (помечаем как неактуальные)
            for response in responses:
                try:
                    if not dry_run:
                        response.is_current = False
                        response.updated_at = datetime.utcnow()
                        db.add(response)
                    
                    results["archived"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Ответ {response.id}: {str(e)}")
        
        elif strategy == MigrationStrategy.PROMPT_USER:
            # Требуется действие пользователя - пока архивируем
            for response in responses:
                try:
                    if not dry_run:
                        response.is_current = False
                        response.updated_at = datetime.utcnow()
                        db.add(response)
                    
                    results["archived"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Ответ {response.id}: {str(e)}")
        
        return results
    
    def create_migration_report(
        self, 
        db: Session, 
        checklist_id: int, 
        impact_analysis: Dict[str, Any],
        migration_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создает отчет о миграции
        
        Args:
            db: Сессия базы данных
            checklist_id: ID чеклиста
            impact_analysis: Анализ влияния
            migration_results: Результаты миграции (если выполнялась)
            
        Returns:
            Отчет о миграции
        """
        from app.database.crud.crud_checklist import checklist as checklist_crud
        
        checklist_obj = checklist_crud.get(db, id=checklist_id)
        
        report = {
            "checklist": {
                "id": checklist_id,
                "title": checklist_obj.title if checklist_obj else "Неизвестно",
                "external_id": checklist_obj.external_id if checklist_obj else "Неизвестно"
            },
            "timestamp": datetime.utcnow().isoformat(),
            "impact_analysis": impact_analysis,
            "migration_results": migration_results,
            "recommendations": []
        }
        
        # Добавляем рекомендации
        if impact_analysis["affected_responses"] > 0:
            report["recommendations"].append(
                "Рекомендуется уведомить пользователей об изменениях в чеклисте"
            )
        
        if impact_analysis["user_actions_required"]:
            report["recommendations"].append(
                "Некоторые ответы требуют ручной проверки пользователями"
            )
        
        if migration_results and migration_results["failed_migrations"] > 0:
            report["recommendations"].append(
                "Обратите внимание на ошибки миграции и исправьте их вручную"
            )
        
        return report
    
    def get_user_migration_tasks(
        self, 
        db: Session, 
        character_id: int, 
        checklist_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получает список задач миграции для конкретного пользователя
        
        Args:
            db: Сессия базы данных
            character_id: ID персонажа
            checklist_id: ID чеклиста
            
        Returns:
            Список задач для пользователя
        """
        # Получаем архивированные ответы пользователя
        archived_responses = db.query(ChecklistResponse).filter(
            ChecklistResponse.character_id == character_id,
            ChecklistResponse.is_current == False
        ).all()
        
        tasks = []
        
        for response in archived_responses:
            # Получаем информацию о вопросе
            question = checklist_question.get(db, id=response.question_id)
            if question:
                tasks.append({
                    "response_id": response.id,
                    "question_text": question.text,
                    "old_answer": response.answer.value_male if response.answer else "Неизвестно",
                    "action_required": "review_and_update",
                    "reason": "Вопрос был изменен или удален"
                })
        
        return tasks
    
    def restore_response(
        self, 
        db: Session, 
        response_id: int, 
        new_answer_id: Optional[int] = None
    ) -> bool:
        """
        Восстанавливает архивированный ответ
        
        Args:
            db: Сессия базы данных
            response_id: ID ответа
            new_answer_id: ID нового ответа (если изменился)
            
        Returns:
            True если восстановление успешно
        """
        try:
            response = checklist_response.get(db, id=response_id)
            if not response:
                return False
            
            response.is_current = True
            response.updated_at = datetime.utcnow()
            
            if new_answer_id:
                response.answer_id = new_answer_id
            
            db.add(response)
            db.commit()
            
            logger.info(f"Ответ {response_id} восстановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка восстановления ответа {response_id}: {str(e)}")
            db.rollback()
            return False


# Глобальный экземпляр сервиса
response_migration_service = ResponseMigrationService()
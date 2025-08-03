"""
Упрощенные тесты базы данных и CRUD операций.
"""

import pytest
from datetime import datetime, timedelta

from app.database.crud import user, project, text, character, checklist_response, token
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.text import TextCreate, TextUpdate
from app.schemas.character import CharacterCreate, CharacterUpdate
from app.schemas.checklist import ChecklistResponseCreate, ChecklistResponseUpdate
from app.schemas.token import TokenCreate


class TestSimpleCRUD:
    """Упрощенные тесты CRUD операций."""
    
    def test_user_crud_operations(self, db_session):
        """Тест полного цикла CRUD операций пользователя."""
        db = db_session
        
        # CREATE
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            full_name="Test User"
        )
        created_user = user.create(db, obj_in=user_data)
        
        assert created_user.id is not None
        assert created_user.email == user_data.email
        assert created_user.username == user_data.username
        assert created_user.full_name == user_data.full_name
        assert created_user.is_active == True
        assert created_user.password_hash != user_data.password  # Проверяем хеширование
        
        # READ
        found_user = user.get(db, id=created_user.id)
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email
        
        found_by_email = user.get_by_email(db, email="test@example.com")
        assert found_by_email is not None
        assert found_by_email.id == created_user.id
        
        # AUTHENTICATE
        authenticated_user = user.authenticate(
            db, email="test@example.com", password="testpassword123"
        )
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        
        # UPDATE
        update_data = UserUpdate(full_name="Updated Name")
        updated_user = user.update(db, db_obj=created_user, obj_in=update_data)
        assert updated_user.full_name == "Updated Name"
        
        # DELETE (через деактивацию)
        deactivated_user = user.deactivate(db, db_obj=updated_user)
        assert deactivated_user.is_active == False
    
    def test_project_crud_operations(self, db_session):
        """Тест полного цикла CRUD операций проекта."""
        db = db_session
        
        # Сначала создаем пользователя
        user_data = UserCreate(
            email="project_owner@example.com",
            username="project_owner",
            password="testpassword123"
        )
        created_user = user.create(db, obj_in=user_data)
        
        # CREATE PROJECT
        project_data = ProjectCreate(
            title="Test Project",
            description="Test Description"
        )
        created_project = project.create_with_owner(
            db, obj_in=project_data, owner_id=created_user.id
        )
        
        assert created_project.id is not None
        assert created_project.title == project_data.title
        assert created_project.user_id == created_user.id
        
        # READ PROJECT
        found_project = project.get(db, id=created_project.id)
        assert found_project is not None
        assert found_project.title == "Test Project"
        
        # GET PROJECTS BY OWNER
        user_projects = project.get_multi_by_owner(db, owner_id=created_user.id)
        assert len(user_projects) == 1
        assert user_projects[0].id == created_project.id
        
        # CHECK OWNERSHIP
        assert project.is_owner(db, project_id=created_project.id, user_id=created_user.id) == True
        
        # UPDATE PROJECT
        update_data = ProjectUpdate(title="Updated Project")
        updated_project = project.update(db, db_obj=created_project, obj_in=update_data)
        assert updated_project.title == "Updated Project"
    
    def test_text_crud_operations(self, db_session):
        """Тест полного цикла CRUD операций текста."""
        db = db_session
        
        # Создаем пользователя и проект
        user_data = UserCreate(
            email="text_owner@example.com",
            username="text_owner",
            password="testpassword123"
        )
        created_user = user.create(db, obj_in=user_data)
        
        project_data = ProjectCreate(title="Text Project")
        created_project = project.create_with_owner(
            db, obj_in=project_data, owner_id=created_user.id
        )
        
        # CREATE TEXT
        text_data = TextCreate(
            project_id=created_project.id,
            filename="test.txt",
            original_format="txt",
            content="Test content"
        )
        created_text = text.create(db, obj_in=text_data)
        
        assert created_text.id is not None
        assert created_text.filename == text_data.filename
        assert created_text.project_id == created_project.id
        assert created_text.processed_at is None
        
        # GET TEXTS BY PROJECT
        project_texts = text.get_multi_by_project(db, project_id=created_project.id)
        assert len(project_texts) == 1
        assert project_texts[0].id == created_text.id
        
        # MARK AS PROCESSED
        processed_text = text.mark_as_processed(db, text_id=created_text.id)
        assert processed_text.processed_at is not None
        
        # GET PROCESSED TEXTS
        processed_texts = text.get_processed(db)
        assert len(processed_texts) >= 1
        assert any(t.id == created_text.id for t in processed_texts)
    
    def test_character_crud_operations(self, db_session):
        """Тест полного цикла CRUD операций персонажа."""
        db = db_session
        
        # Создаем базовые сущности
        user_data = UserCreate(
            email="char_owner@example.com",
            username="char_owner",
            password="testpassword123"
        )
        created_user = user.create(db, obj_in=user_data)
        
        project_data = ProjectCreate(title="Character Project")
        created_project = project.create_with_owner(
            db, obj_in=project_data, owner_id=created_user.id
        )
        
        text_data = TextCreate(
            project_id=created_project.id,
            filename="characters.txt",
            original_format="txt"
        )
        created_text = text.create(db, obj_in=text_data)
        
        # CREATE CHARACTER
        character_data = CharacterCreate(
            text_id=created_text.id,
            name="Главный герой",
            aliases=["Герой", "ГГ"],
            importance_score=0.9
        )
        created_character = character.create(db, obj_in=character_data)
        
        assert created_character.id is not None
        assert created_character.name == character_data.name
        assert created_character.importance_score == 0.9
        
        # GET CHARACTERS BY TEXT
        text_characters = character.get_multi_by_text(db, text_id=created_text.id)
        assert len(text_characters) == 1
        assert text_characters[0].id == created_character.id
        
        # CREATE SECONDARY CHARACTER
        secondary_char_data = CharacterCreate(
            text_id=created_text.id,
            name="Второстепенный персонаж",
            importance_score=0.3
        )
        secondary_char = character.create(db, obj_in=secondary_char_data)
        
        # GET MAIN CHARACTERS (важность >= 0.5)
        main_characters = character.get_main_characters(
            db, text_id=created_text.id, threshold=0.5
        )
        assert len(main_characters) == 1
        assert main_characters[0].id == created_character.id
        
        # UPDATE IMPORTANCE
        updated_character = character.update_importance(
            db, character_id=created_character.id, importance_score=0.95
        )
        assert updated_character.importance_score == 0.95
    
    def test_checklist_crud_operations(self, db_session):
        """Тест полного цикла CRUD операций чеклиста."""
        db = db_session
        
        # Создаем базовые сущности
        user_data = UserCreate(
            email="checklist_owner@example.com",
            username="checklist_owner",
            password="testpassword123"
        )
        created_user = user.create(db, obj_in=user_data)
        
        project_data = ProjectCreate(title="Checklist Project")
        created_project = project.create_with_owner(
            db, obj_in=project_data, owner_id=created_user.id
        )
        
        text_data = TextCreate(
            project_id=created_project.id,
            filename="checklist.txt",
            original_format="txt"
        )
        created_text = text.create(db, obj_in=text_data)
        
        character_data = CharacterCreate(
            text_id=created_text.id,
            name="Тестовый персонаж"
        )
        created_character = character.create(db, obj_in=character_data)
        
        # CREATE/UPDATE RESPONSE
        response = checklist_response.create_or_update_response(
            db,
            character_id=created_character.id,
            checklist_type="physical_portrait",
            question_id="height",
            response="Высокий",
            confidence_level=4
        )
        
        assert response.id is not None
        assert response.response == "Высокий"
        assert response.confidence_level == 4
        
        # UPDATE SAME RESPONSE
        updated_response = checklist_response.create_or_update_response(
            db,
            character_id=created_character.id,
            checklist_type="physical_portrait",
            question_id="height",
            response="Очень высокий",
            confidence_level=5
        )
        
        # Должен быть тот же ID, но обновленное содержимое
        assert updated_response.id == response.id
        assert updated_response.response == "Очень высокий"
        assert updated_response.confidence_level == 5
        
        # CREATE ADDITIONAL RESPONSES
        checklist_response.create_or_update_response(
            db,
            character_id=created_character.id,
            checklist_type="physical_portrait",
            question_id="weight",
            response="Средний",
            confidence_level=3
        )
        
        checklist_response.create_or_update_response(
            db,
            character_id=created_character.id,
            checklist_type="physical_portrait",
            question_id="hair_color",
            response="",  # Пустой ответ
            confidence_level=1
        )
        
        # GET COMPLETION STATS
        stats = checklist_response.get_completion_stats(
            db,
            character_id=created_character.id,
            checklist_type="physical_portrait"
        )
        
        assert stats["total"] == 3
        assert stats["filled"] == 2  # Только непустые ответы
        assert stats["empty"] == 1
        assert stats["completion_percent"] > 0
    
    def test_token_crud_operations(self, db_session):
        """Тест полного цикла CRUD операций токена."""
        db = db_session
        
        # Создаем пользователя
        user_data = UserCreate(
            email="token_user@example.com",
            username="token_user",
            password="testpassword123"
        )
        created_user = user.create(db, obj_in=user_data)
        
        # CREATE TOKEN
        token_data = TokenCreate(
            user_id=created_user.id,
            token_hash="test_token_hash",
            token_type="access",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        created_token = token.create(db, obj_in=token_data)
        
        assert created_token.id is not None
        assert created_token.user_id == created_user.id
        assert created_token.is_revoked == False
        
        # VALIDATE TOKEN
        is_valid = token.is_token_valid(db, token_hash="test_token_hash")
        assert is_valid == True
        
        # GET TOKEN INFO
        token_info = token.get_token_info(db, token_hash="test_token_hash")
        assert token_info is not None
        assert token_info["user_id"] == created_user.id
        assert token_info["token_type"] == "access"
        assert token_info["is_valid"] == True
        
        # REVOKE TOKEN
        revoked_token = token.revoke_token(db, token_hash="test_token_hash")
        assert revoked_token.is_revoked == True
        
        # CHECK VALIDATION AFTER REVOKE
        is_valid_after_revoke = token.is_token_valid(db, token_hash="test_token_hash")
        assert is_valid_after_revoke == False


class TestAdvancedOperations:
    """Тесты продвинутых операций."""
    
    def test_complex_data_flow(self, db_session):
        """Тест комплексного потока данных через всю систему."""
        db = db_session
        
        # 1. Создаем пользователя
        user_data = UserCreate(
            email="complex@example.com",
            username="complex_user",
            password="testpassword123",
            full_name="Complex User"
        )
        created_user = user.create(db, obj_in=user_data)
        
        # 2. Создаем проект
        project_data = ProjectCreate(
            title="Анализ Анны Карениной",
            description="Детальный анализ персонажей романа"
        )
        created_project = project.create_with_owner(
            db, obj_in=project_data, owner_id=created_user.id
        )
        
        # 3. Загружаем текст
        text_data = TextCreate(
            project_id=created_project.id,
            filename="anna_karenina.txt",
            original_format="txt",
            content="Все счастливые семьи похожи друг на друга...",
            file_metadata={"author": "Лев Толстой", "year": 1877}
        )
        created_text = text.create(db, obj_in=text_data)
        
        # 4. Создаем персонажей
        anna_data = CharacterCreate(
            text_id=created_text.id,
            name="Анна Каренина",
            aliases=["Анна", "Каренина"],
            importance_score=1.0,
            speech_attribution={"total_words": 12500, "dialogue_scenes": 45}
        )
        anna = character.create(db, obj_in=anna_data)
        
        levin_data = CharacterCreate(
            text_id=created_text.id,
            name="Константин Левин",
            aliases=["Левин", "Костя"],
            importance_score=0.9
        )
        levin = character.create(db, obj_in=levin_data)
        
        # 5. Заполняем чеклисты для Анны
        physical_responses = [
            ("height", "Среднего роста", 4),
            ("hair_color", "Темные волосы", 5),
            ("eyes", "Серые глаза", 5),
            ("age", "Около 28 лет", 3),
        ]
        
        for question_id, response, confidence in physical_responses:
            checklist_response.create_or_update_response(
                db,
                character_id=anna.id,
                checklist_type="physical_portrait",
                question_id=question_id,
                response=response,
                confidence_level=confidence
            )
        
        emotional_responses = [
            ("temperament", "Страстная, импульсивная", 5),
            ("main_emotion", "Внутренний конфликт", 4),
            ("emotional_stability", "Нестабильная", 4),
        ]
        
        for question_id, response, confidence in emotional_responses:
            checklist_response.create_or_update_response(
                db,
                character_id=anna.id,
                checklist_type="emotional_profile",
                question_id=question_id,
                response=response,
                confidence_level=confidence
            )
        
        # 6. Отмечаем текст как обработанный
        text.mark_as_processed(db, text_id=created_text.id)
        
        # 7. Проверяем комплексные запросы
        
        # Получаем всех главных персонажей
        main_characters = character.get_main_characters(
            db, text_id=created_text.id, threshold=0.8
        )
        assert len(main_characters) == 2
        assert anna.id in [c.id for c in main_characters]
        assert levin.id in [c.id for c in main_characters]
        
        # Проверяем статистику заполнения чеклистов
        physical_stats = checklist_response.get_completion_stats(
            db, character_id=anna.id, checklist_type="physical_portrait"
        )
        assert physical_stats["total"] == 4
        assert physical_stats["filled"] == 4
        assert physical_stats["completion_percent"] == 100.0
        
        emotional_stats = checklist_response.get_completion_stats(
            db, character_id=anna.id, checklist_type="emotional_profile"
        )
        assert emotional_stats["total"] == 3
        assert emotional_stats["filled"] == 3
        
        # Получаем ответы по уровню уверенности
        high_confidence_responses = checklist_response.get_responses_by_confidence(
            db, character_id=anna.id, min_confidence=5, max_confidence=5
        )
        assert len(high_confidence_responses) >= 3  # hair_color, eyes, temperament
        
        # Проверяем принадлежность данных
        assert character.belongs_to_text(db, character_id=anna.id, text_id=created_text.id)
        assert text.belongs_to_project(db, text_id=created_text.id, project_id=created_project.id)
        assert project.is_owner(db, project_id=created_project.id, user_id=created_user.id)
        
        # Подсчитываем общую статистику
        total_characters = character.count_by_text(db, text_id=created_text.id)
        total_responses = checklist_response.count_by_character(db, character_id=anna.id)
        
        assert total_characters == 2
        assert total_responses == 7  # 4 physical + 3 emotional
        
        print(f"\n✅ Комплексный тест завершен успешно!")
        print(f"👤 Пользователь: {created_user.username}")
        print(f"📚 Проект: {created_project.title}")
        print(f"📄 Текст: {created_text.filename}")
        print(f"🎭 Персонажей: {total_characters}")
        print(f"📝 Ответов чеклистов для Анны: {total_responses}")
        print(f"📊 Заполненность физического портрета: {physical_stats['completion_percent']}%")
        print(f"📊 Заполненность эмоционального профиля: {emotional_stats['completion_percent']}%")

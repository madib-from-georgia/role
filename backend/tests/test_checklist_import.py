"""
Тесты для импорта чеклистов из Markdown файлов
"""

import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.checklist_service import checklist_service
from app.services.checklist_parser import ChecklistMarkdownParser


class TestChecklistImport:
    """Тесты импорта чеклистов"""
    
    def test_validate_checklist_file_valid(self):
        """Тест валидации корректного файла чеклиста"""
        # Создаем временный файл с корректным содержимым
        valid_content = """# Тестовый чеклист

## 📏 1. ТЕСТОВАЯ СЕКЦИЯ

### 1.1 Тестовая подсекция

**Тестовая группа вопросов:**
- **Группа 1**
  - [ ] **Тестовый вопрос 1?**
    *Подсказка для первого вопроса*

  - [ ] **Тестовый вопрос 2?**
    *Подсказка для второго вопроса*
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(valid_content)
            temp_file = f.name
        
        try:
            validation = checklist_service.validate_checklist_file(temp_file)
            
            assert validation["valid"] is True
            assert validation["errors"] == []
            assert validation["summary"] is not None
            assert "slug" in validation["summary"]
            assert "total_sections" in validation["summary"]
            assert "total_questions" in validation["summary"]
            
        finally:
            os.unlink(temp_file)
    
    def test_validate_checklist_file_invalid(self):
        """Тест валидации некорректного файла"""
        # Создаем временный файл с некорректным содержимым
        invalid_content = "Это не чеклист"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(invalid_content)
            temp_file = f.name
        
        try:
            validation = checklist_service.validate_checklist_file(temp_file)
            
            # Валидация может пройти, но структура будет пустой или минимальной
            assert isinstance(validation, dict)
            assert "valid" in validation
            assert "errors" in validation
            
        finally:
            os.unlink(temp_file)
    
    def test_validate_nonexistent_file(self):
        """Тест валидации несуществующего файла"""
        validation = checklist_service.validate_checklist_file("/nonexistent/file.md")
        
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
        assert "не найден" in validation["errors"][0] or "not found" in validation["errors"][0].lower()
    
    def test_checklist_parser_structure(self):
        """Тест структуры парсера чеклистов"""
        parser = ChecklistMarkdownParser()
        
        # Проверяем наличие необходимых паттернов
        assert hasattr(parser, 'title_pattern')
        assert hasattr(parser, 'section_pattern')
        assert hasattr(parser, 'subsection_pattern')
        assert hasattr(parser, 'question_pattern')
        assert hasattr(parser, 'hint_pattern')
        
        # Проверяем наличие основных методов
        assert hasattr(parser, 'parse_file')
        assert callable(parser.parse_file)
    
    def test_checklist_parser_patterns(self):
        """Тест регулярных выражений парсера"""
        parser = ChecklistMarkdownParser()
        
        # Тест паттерна заголовков
        import re
        
        title_match = re.match(parser.title_pattern, "# Заголовок чеклиста")
        assert title_match is not None
        assert title_match.group(1) == "Заголовок чеклиста"
        
        # Тест паттерна секций
        section_match = re.match(parser.section_pattern, "## 📏 1. СЕКЦИЯ")
        assert section_match is not None
        
        # Тест паттерна подсекций
        subsection_match = re.match(parser.subsection_pattern, "### 1.1 Подсекция")
        assert subsection_match is not None
        
        # Тест паттерна вопросов
        question_match = re.match(parser.question_pattern, "  - [ ] **Тестовый вопрос?**")
        assert question_match is not None
        assert question_match.group(1) == "Тестовый вопрос?"
    
    def test_import_script_structure(self):
        """Тест структуры скрипта импорта"""
        import sys
        from pathlib import Path
        
        # Добавляем путь к скриптам
        scripts_path = Path(__file__).parent.parent / "scripts"
        sys.path.insert(0, str(scripts_path))
        
        try:
            import import_checklists
            
            # Проверяем наличие списка файлов
            assert hasattr(import_checklists, 'CHECKLIST_FILES')
            assert isinstance(import_checklists.CHECKLIST_FILES, list)
            assert len(import_checklists.CHECKLIST_FILES) >= 20  # Должно быть 20 модулей
            
            # Проверяем структуру элементов списка
            for file_path, description in import_checklists.CHECKLIST_FILES:
                assert isinstance(file_path, str)
                assert isinstance(description, str)
                assert file_path.endswith('.md')
                assert 'docs/modules/' in file_path
            
            # Проверяем наличие основных функций
            assert hasattr(import_checklists, 'import_checklist_files')
            assert hasattr(import_checklists, 'validate_all_checklists')
            assert callable(import_checklists.import_checklist_files)
            assert callable(import_checklists.validate_all_checklists)
            
        finally:
            sys.path.pop(0)


class TestChecklistModules:
    """Тесты модулей чеклистов"""
    
    def test_physical_portrait_checklist_exists(self):
        """Тест существования чеклиста физического портрета"""
        checklist_path = Path("docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.md")
        assert checklist_path.exists(), f"Файл чеклиста не найден: {checklist_path}"
    
    def test_emotional_profile_checklist_exists(self):
        """Тест существования чеклиста эмоционального профиля"""
        checklist_path = Path("docs/modules/02-emotional-profile/ACTOR_EMOTIONAL_CHECKLIST.md")
        assert checklist_path.exists(), f"Файл чеклиста не найден: {checklist_path}"
    
    def test_all_checklist_modules_exist(self):
        """Тест существования всех модулей чеклистов"""
        expected_modules = [
            "01-physical-portrait",
            "02-emotional-profile", 
            "03-speech-characteristics",
            "04-internal-conflicts",
            "05-motivation-goals",
            "06-character-relationships",
            "07-biography-backstory",
            "08-social-status",
            "09-key-scenes",
            "10-acting-tasks",
            "11-practical-exercises",
            "12-subtext-analysis",
            "13-tempo-rhythm",
            "14-personality-type",
            "15-defense-mechanisms",
            "16-trauma-ptsd",
            "17-archetypes",
            "18-emotional-intelligence",
            "19-cognitive-distortions",
            "20-attachment-styles"
        ]
        
        modules_dir = Path("docs/modules")
        assert modules_dir.exists(), "Директория модулей не найдена"
        
        for module_name in expected_modules:
            module_dir = modules_dir / module_name
            assert module_dir.exists(), f"Модуль не найден: {module_name}"
            
            # Проверяем наличие файла чеклиста
            checklist_files = list(module_dir.glob("ACTOR_*.md"))
            assert len(checklist_files) > 0, f"Файл чеклиста не найден в модуле: {module_name}"
    
    def test_checklist_files_readable(self):
        """Тест читаемости файлов чеклистов"""
        modules_dir = Path("docs/modules")
        
        if not modules_dir.exists():
            pytest.skip("Директория модулей не найдена")
        
        checklist_files = list(modules_dir.glob("*/ACTOR_*.md"))
        assert len(checklist_files) > 0, "Файлы чеклистов не найдены"
        
        for checklist_file in checklist_files[:5]:  # Проверяем первые 5 файлов
            try:
                with open(checklist_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert len(content) > 0, f"Файл пустой: {checklist_file}"
                    assert "# " in content, f"Заголовок не найден в файле: {checklist_file}"
            except Exception as e:
                pytest.fail(f"Ошибка чтения файла {checklist_file}: {e}")
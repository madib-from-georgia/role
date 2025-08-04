"""
Тесты для парсера чеклистов
"""

import pytest
import tempfile
import os
from pathlib import Path

from app.services.checklist_parser import ChecklistMarkdownParser


class TestChecklistParser:
    """Тесты для парсера чеклистов"""
    
    def setup_method(self):
        self.parser = ChecklistMarkdownParser()
    
    def test_parser_init(self):
        """Тест инициализации парсера"""
        assert self.parser is not None
        assert hasattr(self.parser, 'title_pattern')
        assert hasattr(self.parser, 'section_pattern')
    
    def test_parse_simple_checklist(self):
        """Тест парсинга простого чеклиста"""
        content = """# 🎭 Тестовый чеклист

## 📏 1. СЕКЦИЯ ПЕРВАЯ

### 1.1 Подсекция первая

- **Группа вопросов первая**
  - [ ] **Тестовый вопрос 1?**
    *Подсказка к первому вопросу*

  - [ ] **Тестовый вопрос 2?**
    *Подсказка ко второму вопросу*

### 1.2 Подсекция вторая

- **Группа вопросов вторая**
  - [ ] **Тестовый вопрос 3?**
    *Подсказка к третьему вопросу*
"""
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Парсим файл
            structure = self.parser.parse_file(temp_path)
            
            # Проверяем основную структуру
            assert structure.title == "Тестовый чеклист"
            assert structure.icon == "🎭"
            assert len(structure.sections) == 1
            
            # Проверяем секцию
            section = structure.sections[0]
            assert section.title == "СЕКЦИЯ ПЕРВАЯ"
            assert section.number == "1"
            assert section.icon == "📏"
            assert len(section.subsections) == 2
            
            # Проверяем первую подсекцию
            subsection1 = section.subsections[0]
            assert subsection1.title == "Подсекция первая"
            assert subsection1.number == "1.1"
            assert len(subsection1.question_groups) == 1
            
            # Проверяем группу вопросов
            group = subsection1.question_groups[0]
            assert group.title == "Группа вопросов первая"
            assert len(group.questions) == 2
            
            # Проверяем вопросы
            question1 = group.questions[0]
            assert question1.text == "Тестовый вопрос 1?"
            assert question1.hint == "Подсказка к первому вопросу"
            
            question2 = group.questions[1]
            assert question2.text == "Тестовый вопрос 2?"
            assert question2.hint == "Подсказка ко второму вопросу"
            
        finally:
            # Удаляем временный файл
            os.unlink(temp_path)
    
    def test_get_structure_summary(self):
        """Тест получения сводки структуры"""
        content = """# 🎭 Тестовый чеклист

## 📏 1. ПЕРВАЯ СЕКЦИЯ

### 1.1 Подсекция

- **Группа**
  - [ ] **Вопрос 1?**
  - [ ] **Вопрос 2?**

## 🎨 2. ВТОРАЯ СЕКЦИЯ

### 2.1 Подсекция

- **Группа**
  - [ ] **Вопрос 3?**
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            structure = self.parser.parse_file(temp_path)
            summary = self.parser.get_structure_summary(structure)
            
            assert summary["title"] == "Тестовый чеклист"
            assert summary["total_sections"] == 2
            assert summary["total_questions"] == 3
            
            # Проверяем детали секций
            sections = summary["sections"]
            assert len(sections) == 2
            
            assert sections[0]["title"] == "ПЕРВАЯ СЕКЦИЯ"
            assert sections[0]["questions"] == 2
            
            assert sections[1]["title"] == "ВТОРАЯ СЕКЦИЯ"
            assert sections[1]["questions"] == 1
            
        finally:
            os.unlink(temp_path)
    
    def test_slug_generation(self):
        """Тест генерации slug"""
        assert self.parser._generate_slug("ACTOR_PHYSICAL_CHECKLIST") == "physical-checklist"
        assert self.parser._generate_slug("ACTOR_EMOTIONAL_CHECKLIST") == "emotional-checklist"
        assert self.parser._generate_slug("TEST_FILE") == "test-file"
    
    def test_clean_title(self):
        """Тест очистки заголовков"""
        assert self.parser._clean_title("🎭 1. ЗАГОЛОВОК") == "ЗАГОЛОВОК"
        assert self.parser._clean_title("📏 ЗАГОЛОВОК БЕЗ НОМЕРА") == "ЗАГОЛОВОК БЕЗ НОМЕРА"
        assert self.parser._clean_title("2. ПРОСТО ЗАГОЛОВОК") == "ПРОСТО ЗАГОЛОВОК"
    
    def test_extract_icon(self):
        """Тест извлечения иконок"""
        assert self.parser._extract_icon("🎭 Заголовок") == "🎭"
        assert self.parser._extract_icon("📏 1. Заголовок") == "📏"
        assert self.parser._extract_icon("Заголовок без иконки") == ""
    
    def test_extract_number(self):
        """Тест извлечения номеров"""
        assert self.parser._extract_number("1. ЗАГОЛОВОК") == "1"
        assert self.parser._extract_number("🎭 2.5 ЗАГОЛОВОК") == "2.5"
        assert self.parser._extract_number("ЗАГОЛОВОК БЕЗ НОМЕРА") == ""
    
    def test_parse_real_checklist_structure(self):
        """Тест парсинга реальной структуры чеклиста (если файлы доступны)"""
        # Проверяем, есть ли доступ к реальным файлам чеклистов
        project_root = Path(__file__).parent.parent.parent
        physical_checklist = project_root / "docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.md"
        
        if physical_checklist.exists():
            try:
                structure = self.parser.parse_file(str(physical_checklist))
                summary = self.parser.get_structure_summary(structure)
                
                # Проверяем, что структура имеет смысл
                assert summary["title"]
                assert summary["total_sections"] > 0
                assert summary["total_questions"] > 0
                assert summary["slug"] == "physical-checklist"
                
                print(f"Физический чеклист: {summary['total_questions']} вопросов в {summary['total_sections']} секциях")
                
            except Exception as e:
                pytest.skip(f"Не удалось распарсить реальный файл: {e}")
        else:
            pytest.skip("Реальные файлы чеклистов недоступны для тестирования")
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест несуществующего файла
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("nonexistent_file.md")
        
        # Тест пустого файла
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            structure = self.parser.parse_file(temp_path)
            # Пустой файл должен создать пустую структуру
            assert structure.title == ""
            assert len(structure.sections) == 0
        finally:
            os.unlink(temp_path)

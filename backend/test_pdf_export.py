#!/usr/bin/env python3
"""
Тестовый скрипт для проверки улучшенного PDF экспорта с WeasyPrint.
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent))

from app.services.export_service import export_service
from app.database.models.character import Character
from app.schemas.checklist import ChecklistWithResponses


class MockCharacter:
    """Мок-объект персонажа для тестирования."""
    
    def __init__(self):
        self.id = 1
        self.name = "Гамлет"
        self.aliases = ["Принц Датский", "Принц Гамлет"]
        self.importance_score = 9.5
        self.gender = "male"


class MockResponse:
    """Мок-объект ответа на вопрос."""
    
    def __init__(self, text="Тестовый ответ", source_type="FOUND_IN_TEXT"):
        self.answer_text = text
        self.source_type = MockSourceType(source_type)
        self.confidence_score = 0.85
        self.comment = "Тестовый комментарий"
        self.answer = MockAnswer()


class MockSourceType:
    """Мок-объект типа источника."""
    
    def __init__(self, value):
        self.value = value


class MockAnswer:
    """Мок-объект ответа."""
    
    def __init__(self):
        self.hint = "Совет актеру: обратите внимание на внутренние переживания персонажа"
        self.exercise = "Упражнение: проработайте монолог 'Быть или не быть'"
        self.value_male = "Высокий, статный"
        self.value_female = "Высокая, статная"
        self.exported_value_male = "Я высокий и статный"
        self.exported_value_female = "Я высокая и статная"


class MockQuestion:
    """Мок-объект вопроса."""
    
    def __init__(self, text):
        self.text = text
        self.current_response = MockResponse()


class MockQuestionGroup:
    """Мок-объект группы вопросов."""
    
    def __init__(self, title):
        self.title = title
        self.questions = [
            MockQuestion("Какой рост у персонажа?"),
            MockQuestion("Какое телосложение у персонажа?"),
            MockQuestion("Какие особенности внешности?")
        ]


class MockSubsection:
    """Мок-объект подсекции."""
    
    def __init__(self, title):
        self.title = title
        self.question_groups = [
            MockQuestionGroup("Физические характеристики"),
            MockQuestionGroup("Особенности внешности")
        ]


class MockSection:
    """Мок-объект секции."""
    
    def __init__(self, title):
        self.title = title
        self.subsections = [
            MockSubsection("Общие характеристики"),
            MockSubsection("Детальные характеристики")
        ]


class MockChecklist:
    """Мок-объект чеклиста."""
    
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.sections = [
            MockSection("Физический портрет"),
            MockSection("Эмоциональный профиль")
        ]


async def test_pdf_export():
    """Тестирование экспорта PDF с различными настройками."""
    
    print("🧪 Тестирование улучшенного PDF экспорта...")
    
    # Создаем тестовые данные
    character = MockCharacter()
    checklists = [
        MockChecklist(
            "Модуль 1: Физический портрет",
            "Анализ внешности и физических характеристик персонажа"
        ),
        MockChecklist(
            "Модуль 2: Эмоциональный профиль", 
            "Исследование эмоциональной сферы персонажа"
        )
    ]
    
    # Создаем директорию для тестовых файлов
    test_dir = Path("test_exports")
    test_dir.mkdir(exist_ok=True)
    
    # Тестируем различные форматы и темы
    test_cases = [
        ("detailed", "default", "Детальный отчет (стандартная тема)"),
        ("detailed", "professional", "Детальный отчет (профессиональная тема)"),
        ("detailed", "creative", "Детальный отчет (творческая тема)"),
        ("detailed", "minimal", "Детальный отчет (минималистичная тема)"),
        ("summary", "professional", "Краткий отчет (профессиональная тема)"),
        ("compact", "minimal", "Компактный отчет (минималистичная тема)")
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for format_type, theme, description in test_cases:
        try:
            print(f"📄 Генерация: {description}...")
            
            # Тестируем с WeasyPrint
            pdf_bytes = await export_service.export_character_pdf(
                character=character,
                checklists=checklists,
                format_type=format_type,
                user_id=1,
                use_weasyprint=True,
                theme=theme
            )
            
            # Сохраняем файл
            filename = f"test_{format_type}_{theme}_weasy.pdf"
            filepath = test_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
            
            file_size = len(pdf_bytes) / 1024  # KB
            print(f"✅ Успешно создан: {filename} ({file_size:.1f} KB)")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при создании {description}: {str(e)}")
    
    # Тестируем fallback на ReportLab
    try:
        print(f"📄 Генерация: Fallback на ReportLab...")
        
        pdf_bytes = await export_service.export_character_pdf(
            character=character,
            checklists=checklists,
            format_type="detailed",
            user_id=1,
            use_weasyprint=False
        )
        
        filename = "test_detailed_reportlab.pdf"
        filepath = test_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        file_size = len(pdf_bytes) / 1024  # KB
        print(f"✅ Успешно создан: {filename} ({file_size:.1f} KB)")
        success_count += 1
        total_count += 1
        
    except Exception as e:
        print(f"❌ Ошибка при создании ReportLab PDF: {str(e)}")
        total_count += 1
    
    # Результаты тестирования
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Успешно: {success_count}/{total_count}")
    print(f"❌ Ошибок: {total_count - success_count}/{total_count}")
    
    if success_count > 0:
        print(f"\n📁 Тестовые файлы сохранены в: {test_dir.absolute()}")
        print("🔍 Откройте файлы для проверки качества отчетов")
    
    return success_count == total_count


async def test_themes():
    """Тестирование загрузки тем."""
    
    print("\n🎨 Тестирование системы тем...")
    
    themes = ["professional", "creative", "minimal", "nonexistent"]
    
    for theme in themes:
        try:
            css_content = export_service._load_theme_css(theme)
            if css_content:
                print(f"✅ Тема '{theme}': загружена ({len(css_content)} символов)")
            else:
                print(f"⚠️  Тема '{theme}': не найдена или пуста")
        except Exception as e:
            print(f"❌ Ошибка загрузки темы '{theme}': {str(e)}")


def test_font_detection():
    """Тестирование определения шрифтов."""
    
    print("\n🔤 Тестирование определения шрифтов...")
    
    font_path = export_service._find_cyrillic_font()
    if font_path:
        print(f"✅ Найден шрифт с поддержкой кириллицы: {font_path}")
    else:
        print("⚠️  Шрифт с поддержкой кириллицы не найден")
    
    print(f"🔤 Используемый шрифт по умолчанию: {export_service.default_font}")


async def main():
    """Основная функция тестирования."""
    
    print("🚀 Запуск тестирования улучшенного PDF экспорта\n")
    
    # Проверяем доступность WeasyPrint
    try:
        import weasyprint
        print("✅ WeasyPrint доступен")
    except ImportError:
        print("❌ WeasyPrint недоступен - некоторые тесты будут пропущены")
    
    # Тестируем определение шрифтов
    test_font_detection()
    
    # Тестируем систему тем
    await test_themes()
    
    # Тестируем экспорт PDF
    success = await test_pdf_export()
    
    print(f"\n{'🎉 Все тесты пройдены успешно!' if success else '⚠️  Некоторые тесты завершились с ошибками'}")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
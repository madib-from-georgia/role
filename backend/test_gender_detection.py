#!/usr/bin/env python3
"""
Простой тест для проверки работы определения пола персонажей.
"""

import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.nlp.gender_detector import GenderDetector
from app.services.nlp.models import Gender


def test_gender_detection():
    """Тестирует определение пола персонажей."""
    detector = GenderDetector()
    
    # Тестовые случаи
    test_cases = [
        # (имя, описание, ожидаемый_пол)
        ("Александр", "молодой человек", Gender.MALE),
        ("Мария", "красивая девушка", Gender.FEMALE),
        ("Иван", None, Gender.MALE),
        ("Анна", None, Gender.FEMALE),
        ("Владимир", "он сказал", Gender.MALE),
        ("Екатерина", "она ответила", Gender.FEMALE),
        ("Неизвестный", None, Gender.UNKNOWN),
        ("Король", "правитель страны", Gender.MALE),
        ("Королева", "правительница", Gender.FEMALE),
        ("Дмитрий", "граф, знатный человек", Gender.MALE),
        ("Княгиня", "знатная дама", Gender.FEMALE),
    ]
    
    print("🧪 Тестирование определения пола персонажей...")
    print("=" * 60)
    
    correct = 0
    total = len(test_cases)
    
    for name, description, expected_gender in test_cases:
        detected_gender = detector.detect_gender(name, description)
        confidence = detector.get_confidence_score(name, description)
        
        is_correct = detected_gender == expected_gender
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} {name:15} | {str(detected_gender.value):8} | {confidence:.2f} | {description or 'нет описания'}")
    
    print("=" * 60)
    accuracy = (correct / total) * 100
    print(f"📊 Точность: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy >= 80:
        print("🎉 Тест пройден успешно!")
        return True
    else:
        print("⚠️  Требуется улучшение алгоритма")
        return False


async def test_nlp_integration():
    """Тестирует интеграцию с NLP процессором."""
    from app.services.nlp.extractors.character_extractor import CharacterExtractor
    
    print("\n🔧 Тестирование интеграции с NLP...")
    print("=" * 60)
    
    extractor = CharacterExtractor()
    
    # Тестовый текст пьесы
    test_text = """
    ДЕЙСТВУЮЩИЕ ЛИЦА:
    
    ИВАН ПЕТРОВИЧ - молодой дворянин
    МАРИЯ ИВАНОВНА - его сестра
    ГРАФ АЛЕКСАНДР - старый друг семьи
    
    ДЕЙСТВИЕ ПЕРВОЕ
    
    ИВАН ПЕТРОВИЧ: Сестра, ты готова к балу?
    
    МАРИЯ ИВАНОВНА: Да, брат, я уже одета.
    
    ГРАФ АЛЕКСАНДР: Позвольте проводить вас, сударыня.
    """
    
    try:
        characters, speech, stats = await extractor.extract_characters_and_speech(test_text)
        
        print(f"Найдено персонажей: {len(characters)}")
        print("Персонажи с определенным полом:")
        
        for char in characters:
            gender_str = char.gender.value if hasattr(char, 'gender') and char.gender else "не определен"
            print(f"  - {char.name}: {gender_str}")
        
        # Проверяем, что пол определен правильно
        gender_results = {}
        for char in characters:
            if hasattr(char, 'gender') and char.gender:
                gender_results[char.name] = char.gender.value
        
        expected_genders = {
            "ИВАН ПЕТРОВИЧ": "male",
            "МАРИЯ ИВАНОВНА": "female", 
            "ГРАФ АЛЕКСАНДР": "male"
        }
        
        correct_genders = 0
        for name, expected in expected_genders.items():
            if name in gender_results and gender_results[name] == expected:
                correct_genders += 1
                print(f"✅ {name}: {gender_results[name]} (правильно)")
            else:
                actual = gender_results.get(name, "не определен")
                print(f"❌ {name}: {actual} (ожидался {expected})")
        
        accuracy = (correct_genders / len(expected_genders)) * 100
        print(f"\n📊 Точность интеграции: {correct_genders}/{len(expected_genders)} ({accuracy:.1f}%)")
        
        return accuracy >= 80
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании интеграции: {e}")
        return False


def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестов определения пола персонажей")
    print("=" * 60)
    
    # Тест 1: Базовое определение пола
    test1_passed = test_gender_detection()
    
    # Тест 2: Интеграция с NLP
    test2_passed = asyncio.run(test_nlp_integration())
    
    print("\n" + "=" * 60)
    print("📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"  Базовое определение пола: {'✅ ПРОЙДЕН' if test1_passed else '❌ НЕ ПРОЙДЕН'}")
    print(f"  Интеграция с NLP:        {'✅ ПРОЙДЕН' if test2_passed else '❌ НЕ ПРОЙДЕН'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✨ Функция определения пола персонажей работает корректно")
        return 0
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Требуется дополнительная настройка")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Тестовый скрипт для анализа парсинга EPUB файла "Дядя Ваня"
"""

import sys
import os
sys.path.append('backend')

from backend.app.parsers.epub_parser import EPUBParser
from backend.app.services.nlp.extractors.character_extractor import CharacterExtractor
import asyncio

def test_epub_parsing():
    """Тестирование парсинга EPUB файла"""

    epub_file = "../../books/epub/Чехов Антон. Дядя Ваня - royallib.com.epub"

    if not os.path.exists(epub_file):
        print(f"❌ Файл не найден: {epub_file}")
        return

    print(f"📖 Анализируем файл: {epub_file}")
    print("=" * 80)

    # 1. Парсим EPUB файл
    parser = EPUBParser()

    try:
        result = parser.parse_file(epub_file)
        content = result['content']
        metadata = result['metadata']

        print(f"✅ EPUB файл успешно распарсен")
        print(f"📊 Длина контента: {len(content)} символов")
        lines_count = len(content.split('\n'))
        print(f"📊 Количество строк: {lines_count}")
        print(f"📊 Количество слов: {len(content.split())}")

        # Показываем первые 2000 символов
        print("\n" + "=" * 80)
        print("🔍 ПЕРВЫЕ 2000 СИМВОЛОВ КОНТЕНТА:")
        print("=" * 80)
        print(content[:2000])
        print("..." if len(content) > 2000 else "")

        # Ищем упоминания персонажей вручную
        print("\n" + "=" * 80)
        print("🔍 ПОИСК ПЕРСОНАЖЕЙ В ТЕКСТЕ:")
        print("=" * 80)

        # Известные персонажи из "Дяди Вани"
        expected_characters = [
            "Серебряков", "Александр Владимирович",
            "Елена Андреевна", "Елена",
            "Войницкий", "Иван Петрович", "Ваня",
            "Соня", "София Александровна",
            "Войницкая", "Мария Васильевна",
            "Астров", "Михаил Львович",
            "Телегин", "Илья Ильич", "Вафля",
            "Марина", "Ефим"
        ]

        for char in expected_characters:
            count = content.lower().count(char.lower())
            if count > 0:
                print(f"  ✅ {char}: {count} упоминаний")
            else:
                print(f"  ❌ {char}: не найден")

        # Ищем секцию "Действующие лица"
        print("\n" + "=" * 80)
        print("🔍 ПОИСК СЕКЦИИ 'ДЕЙСТВУЮЩИЕ ЛИЦА':")
        print("=" * 80)

        import re
        patterns = [
            r"(?i)действующие\s+лица",
            r"(?i)ДЕЙСТВУЮЩИЕ\s+ЛИЦА",
            r"(?i)лица",
            r"(?i)персонажи"
        ]

        found_section = False
        for pattern in patterns:
            matches = list(re.finditer(pattern, content))
            if matches:
                found_section = True
                print(f"  ✅ Найден паттерн '{pattern}': {len(matches)} совпадений")
                for i, match in enumerate(matches[:3]):  # Показываем первые 3
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 300)
                    context = content[start:end]
                    print(f"    Контекст {i+1}: ...{context}...")
                    print()

        if not found_section:
            print("  ❌ Секция 'Действующие лица' не найдена")

        # Ищем диалоги в формате "ИМЯ:"
        print("\n" + "=" * 80)
        print("🔍 ПОИСК ДИАЛОГОВ В ФОРМАТЕ 'ИМЯ:':")
        print("=" * 80)

        dialogue_pattern = r'^\s*([А-ЯЁ][А-ЯЁ\s]+):\s*.+$'
        dialogue_matches = re.findall(dialogue_pattern, content, re.MULTILINE)

        if dialogue_matches:
            print(f"  ✅ Найдено {len(dialogue_matches)} диалогов")
            unique_speakers = set(dialogue_matches)
            print(f"  📊 Уникальных говорящих: {len(unique_speakers)}")
            print("  👥 Говорящие:")
            for speaker in sorted(unique_speakers):
                count = dialogue_matches.count(speaker)
                print(f"    - {speaker}: {count} реплик")
        else:
            print("  ❌ Диалоги в формате 'ИМЯ:' не найдены")

        # Теперь тестируем NLP экстрактор
        print("\n" + "=" * 80)
        print("🤖 ТЕСТИРОВАНИЕ NLP ЭКСТРАКТОРА:")
        print("=" * 80)

        async def test_character_extraction():
            extractor = CharacterExtractor()
            characters, speech_data, stats = await extractor.extract_characters_and_speech(content)

            print(f"  📊 Найдено персонажей: {len(characters)}")
            print(f"  📊 Найдено атрибуций речи: {len(speech_data)}")
            print(f"  📊 Метод: {stats.method_used}")
            print(f"  📊 Формат пьесы: {stats.is_play_format}")
            print(f"  📊 Есть секция персонажей: {stats.has_character_section}")

            if characters:
                print("  👥 Найденные персонажи:")
                for char in characters:
                    print(f"    - {char.name} (источник: {char.source}, упоминаний: {char.mentions_count})")
                    if char.description:
                        print(f"      Описание: {char.description}")
            else:
                print("  ❌ Персонажи не найдены!")

            if stats.processing_errors:
                print("  ⚠️ Ошибки обработки:")
                for error in stats.processing_errors:
                    print(f"    - {error}")

        # Запускаем асинхронный тест
        asyncio.run(test_character_extraction())

    except Exception as e:
        print(f"❌ Ошибка при парсинге EPUB: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_epub_parsing()

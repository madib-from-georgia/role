#!/usr/bin/env python3
"""
Быстрый тест функции отладки нормализации
"""

from app.parsers.txt_parser import TxtParser

def test_normalization_debug():
    parser = TxtParser()
    
    print("🧪 БЫСТРЫЙ ТЕСТ ОТЛАДКИ НОРМАЛИЗАЦИИ")
    print("=" * 50)
    
    # Тестируем
    file_path = '../books/txt/groza.txt'
    
    print(f"📖 Тестируем файл: {file_path}")
    print("👀 Смотрите на вывод ниже:")
    print()
    
    try:
        result = parser.parse_to_structured_content(file_path)
        print()
        print("✅ ТЕСТ ПРОШЕЛ УСПЕШНО!")
        print(f"📊 Результат: {len(result.elements)} элементов")
        print()
        print("📁 Проверьте папку: backend/logs/groza/")
        print("📄 Ищите файлы: 01_raw_content_*.txt, 02_normalized_content_*.txt, 03_comparison_*.txt")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_normalization_debug()

# NLP Analysis Logs

Эта директория содержит результаты анализа текстов системой NLP в JSON формате.

## Структура директорий

```
logs/
├── latest/                           # Последние результаты анализа
│   ├── latest.json                  # Самый последний обработанный файл
│   └── {book_name}_latest.json      # Последний результат для каждой книги
└── {book_name}/                     # Результаты для конкретной книги
    ├── nlp_result_latest.json       # Последний результат для этой книги
    └── nlp_result_YYYYMMDD_HHMMSS.json  # Результаты с временными метками
```

## Формат JSON файлов

Каждый JSON файл содержит:

```json
{
  "metadata": {
    "text_id": 123,
    "filename": "example.fb2",
    "processing_time": 1.23,
    "timestamp": "2024-01-15T14:30:00",
    "processor_version": "1.0"
  },
  "extraction_stats": {
    "method_used": "rule_based_play_parser",
    "is_play_format": true,
    "has_character_section": true,
    "total_characters": 8,
    "total_speech_attributions": 45,
    "text_length": 15000,
    "processing_errors": []
  },
  "characters": [
    {
      "name": "Иван Петрович",
      "aliases": ["Ваня"],
      "description": "главный герой",
      "mentions_count": 25,
      "first_mention_position": 150,
      "importance_score": 0.95,
      "source": "character_list"
    }
  ],
  "speech_attributions": [
    {
      "character_name": "Иван Петрович",
      "text": "Текст реплики",
      "position": 1500,
      "speech_type": "dialogue",
      "confidence": 1.0,
      "context": null
    }
  ]
}
```

## Использование

- **latest/latest.json** - содержит результат последнего анализа любого текста
- **latest/{book}_latest.json** - содержит последний результат анализа конкретной книги  
- **{book}/nlp_result_latest.json** - дублирует последний результат в папке книги
- **{book}/nlp_result_YYYYMMDD_HHMMSS.json** - архивные результаты с временными метками

Система автоматически создает эти файлы при каждом запуске NLP анализа текста.

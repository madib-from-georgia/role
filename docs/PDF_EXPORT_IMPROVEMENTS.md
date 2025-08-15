# Улучшения PDF экспорта

## 🎨 Новые возможности

### Улучшенный дизайн PDF отчетов
- **Современная типографика** с поддержкой кириллицы
- **Профессиональные градиенты** и цветовые схемы
- **Визуальные индикаторы** источников информации
- **Прогресс-бары** для отображения завершенности модулей
- **Адаптивная верстка** для печати

### Система тем оформления
- **Professional** - деловой стиль для официальных отчетов
- **Creative** - творческий дизайн с театральными элементами
- **Minimal** - минималистичный стиль для чистого восприятия

### Технические улучшения
- **WeasyPrint** для высококачественного рендеринга HTML в PDF
- **Fallback на ReportLab** при недоступности WeasyPrint
- **Поддержка кастомных шрифтов**
- **Улучшенное логирование** операций экспорта

## 🚀 Как использовать

### Автоматическое использование
После обновления все PDF экспорты автоматически используют новый дизайн:
- Кнопка "Экспорт PDF" в интерфейсе персонажа
- API эндпоинт `/api/export/character`
- Прямые ссылки `/api/characters/{id}/export/pdf`

### Программное использование
```python
from app.services.export_service import export_service

# Экспорт с профессиональной темой
pdf_bytes = await export_service.export_character_pdf(
    character=character,
    checklists=checklists,
    format_type="detailed",
    user_id=user_id,
    use_weasyprint=True,
    theme="professional"
)

# Экспорт с творческой темой
pdf_bytes = await export_service.export_character_pdf(
    character=character,
    checklists=checklists,
    format_type="summary",
    user_id=user_id,
    use_weasyprint=True,
    theme="creative"
)

# Экспорт с кастомными шрифтами
custom_fonts = {
    "MyFont": "/path/to/font.ttf"
}
pdf_bytes = await export_service.export_character_pdf(
    character=character,
    checklists=checklists,
    format_type="compact",
    user_id=user_id,
    use_weasyprint=True,
    theme="minimal",
    custom_fonts=custom_fonts
)
```

## 📁 Структура файлов

```
backend/app/templates/export/
├── character_detailed_weasy.html     # Детальный отчет (WeasyPrint)
├── character_summary_weasy.html      # Краткий отчет (WeasyPrint)
├── character_compact_weasy.html      # Компактный отчет (WeasyPrint)
└── themes/
    ├── professional.css              # Профессиональная тема
    ├── creative.css                  # Творческая тема
    └── minimal.css                   # Минималистичная тема
```

## 🎯 Типы отчетов

### Detailed (Детальный)
- Полная информация по всем модулям
- Все вопросы и ответы
- Советы и упражнения для актеров
- Комментарии и источники

### Summary (Краткий)
- Обзор завершенности модулей
- Прогресс-бары и статистика
- Ключевые показатели
- Компактное представление

### Compact (Компактный)
- Минимальная информация
- Общая статистика
- Ключевые метрики
- Подходит для быстрого обзора

## 🔧 Настройка

### Требования
- WeasyPrint 61.2+ (установлен)
- Системные библиотеки для рендеринга (установлены)
- Python 3.11+ (установлен)

### Проверка работоспособности
```bash
cd backend
python -c "
from app.services.export_service import export_service
print('✅ Export service готов')
import weasyprint
print('✅ WeasyPrint доступен')
"
```

## 🎨 Визуальные улучшения

### Цветовая индикация источников
- 🟢 **Найдено в тексте** - зеленый градиент
- 🟡 **Логически выведено** - оранжевый градиент  
- 🔴 **Придумано** - красный градиент

### Прогресс-бары
- Визуальное отображение завершенности модулей
- Цветовая индикация: высокая/средняя/низкая завершенность
- Процентные показатели

### Типографика
- Современные шрифты с поддержкой кириллицы
- Правильная иерархия заголовков
- Оптимальные отступы и интервалы

## 🚨 Устранение неполадок

### WeasyPrint недоступен
Система автоматически переключится на ReportLab с базовым дизайном.

### Ошибки шрифтов
Проверьте наличие системных шрифтов или используйте кастомные.

### Проблемы с темами
Убедитесь, что файлы тем существуют в папке `themes/`.

---

*Обновлено: 2025-08-15 - Реализация улучшенного PDF экспорта*
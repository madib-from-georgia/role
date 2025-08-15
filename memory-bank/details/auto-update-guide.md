# Автоматическое обновление Memory Bank

## 🔄 Концепция автоматического обновления

Memory Bank должен автоматически обновляться при изменениях в коде проекта, чтобы документация всегда оставалась актуальной.

## 📋 Стратегия обновления

### 1. Git Hooks
Использование pre-commit и post-commit хуков для автоматического обновления документации.

### 2. CI/CD Pipeline
Интеграция с GitHub Actions или другими CI/CD системами для обновления при пуше в основные ветки.

### 3. Скрипты мониторинга
Периодические скрипты, которые сканируют изменения в кодовой базе и обновляют соответствующие разделы документации.

## 🛠️ Реализация автоматического обновления

### Git Hooks Setup

#### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Проверка изменений для обновления Memory Bank..."

# Проверить изменения в API
if git diff --cached --name-only | grep -q "backend/app/routers/"; then
    echo "📝 Обнаружены изменения в API роутерах"
    echo "⚠️  Не забудьте обновить memory-bank/api-endpoints.md"
fi

# Проверить изменения в моделях БД
if git diff --cached --name-only | grep -q "backend/app/database/models/"; then
    echo "📝 Обнаружены изменения в моделях базы данных"
    echo "⚠️  Не забудьте обновить memory-bank/database-schema.md"
fi

# Проверить изменения в компонентах UI
if git diff --cached --name-only | grep -q "frontend/src/components/"; then
    echo "📝 Обнаружены изменения в UI компонентах"
    echo "⚠️  Не забудьте обновить memory-bank/ui-components.md"
fi

# Проверить изменения в чеклистах
if git diff --cached --name-only | grep -q "docs/modules/"; then
    echo "📝 Обнаружены изменения в модулях чеклистов"
    echo "⚠️  Не забудьте обновить memory-bank/modules-system.md"
fi
```

#### Post-commit Hook
```bash
#!/bin/bash
# .git/hooks/post-commit

echo "🔄 Автоматическое обновление Memory Bank..."

# Обновить timestamp в README
sed -i "s/Последнее обновление: .*/Последнее обновление: $(date +%Y-%m-%d)/" memory-bank/README.md

# Обновить changelog если это релизный коммит
if git log -1 --pretty=%B | grep -q "^v[0-9]"; then
    echo "🏷️  Обнаружен релизный коммит, обновление changelog..."
    # Логика обновления changelog
fi

echo "✅ Memory Bank обновлен"
```

### GitHub Actions Workflow

```yaml
# .github/workflows/update-memory-bank.yml
name: Update Memory Bank

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  update-memory-bank:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Check for API changes
      id: api-changes
      run: |
        if git diff --name-only HEAD~1 | grep -q "backend/app/routers/"; then
          echo "api_changed=true" >> $GITHUB_OUTPUT
        fi
    
    - name: Check for DB model changes
      id: db-changes
      run: |
        if git diff --name-only HEAD~1 | grep -q "backend/app/database/models/"; then
          echo "db_changed=true" >> $GITHUB_OUTPUT
        fi
    
    - name: Update API documentation
      if: steps.api-changes.outputs.api_changed == 'true'
      run: |
        echo "⚠️ API изменения обнаружены. Требуется обновление api-endpoints.md"
        # Здесь можно добавить автоматическое сканирование API и обновление документации
    
    - name: Update database schema
      if: steps.db-changes.outputs.db_changed == 'true'
      run: |
        echo "⚠️ Изменения в БД обнаружены. Требуется обновление database-schema.md"
        # Здесь можно добавить автоматическое генерирование схемы БД
    
    - name: Update timestamps
      run: |
        sed -i "s/Последнее обновление: .*/Последнее обновление: $(date +%Y-%m-%d)/" memory-bank/README.md
        
    - name: Commit changes
      if: github.event_name == 'push'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add memory-bank/
        git diff --staged --quiet || git commit -m "docs: auto-update Memory Bank [skip ci]"
        git push
```

### Скрипты мониторинга

#### Скрипт проверки актуальности
```bash
#!/bin/bash
# scripts/check-memory-bank-freshness.sh

echo "🔍 Проверка актуальности Memory Bank..."

# Проверить когда последний раз обновлялись файлы Memory Bank
MEMORY_BANK_LAST_UPDATE=$(find memory-bank/ -name "*.md" -exec stat -c %Y {} \; | sort -n | tail -1)
CODE_LAST_UPDATE=$(find backend/ frontend/ -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs stat -c %Y | sort -n | tail -1)

if [ $CODE_LAST_UPDATE -gt $MEMORY_BANK_LAST_UPDATE ]; then
    echo "⚠️  Memory Bank устарел! Код изменялся после последнего обновления документации."
    echo "📅 Последнее обновление кода: $(date -d @$CODE_LAST_UPDATE)"
    echo "📅 Последнее обновление Memory Bank: $(date -d @$MEMORY_BANK_LAST_UPDATE)"
    exit 1
else
    echo "✅ Memory Bank актуален"
fi
```

#### Скрипт автоматического сканирования API
```bash
#!/bin/bash
# scripts/scan-api-changes.sh

echo "🔍 Сканирование изменений в API..."

# Извлечь все эндпоинты из кода
python3 << 'EOF'
import ast
import os
import re

def extract_endpoints(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Найти все декораторы @app.get, @app.post, etc.
    endpoints = re.findall(r'@\w+\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', content)
    return endpoints

endpoints = []
for root, dirs, files in os.walk('backend/app/routers/'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            endpoints.extend(extract_endpoints(file_path))

print("📋 Найденные эндпоинты:")
for method, path in endpoints:
    print(f"  {method.upper()} {path}")

# Сравнить с документированными эндпоинтами в api-endpoints.md
with open('memory-bank/api-endpoints.md', 'r', encoding='utf-8') as f:
    documented = f.read()

undocumented = []
for method, path in endpoints:
    if f"{method.upper()} `{path}`" not in documented:
        undocumented.append((method, path))

if undocumented:
    print("\n⚠️  Недокументированные эндпоинты:")
    for method, path in undocumented:
        print(f"  {method.upper()} {path}")
else:
    print("\n✅ Все эндпоинты документированы")
EOF
```

## 📊 Мониторинг качества документации

### Метрики актуальности
- **Время с последнего обновления** - как давно обновлялся каждый файл
- **Покрытие кода документацией** - процент задокументированных компонентов
- **Консистентность** - соответствие документации реальному коду

### Автоматические проверки
```bash
# Проверка ссылок в документации
find memory-bank/ -name "*.md" -exec markdown-link-check {} \;

# Проверка орфографии
find memory-bank/ -name "*.md" -exec aspell check {} \;

# Проверка форматирования
find memory-bank/ -name "*.md" -exec markdownlint {} \;
```

## 🔧 Настройка автоматического обновления

### 1. Установка Git Hooks
```bash
# Копировать хуки в .git/hooks/
cp scripts/git-hooks/* .git/hooks/
chmod +x .git/hooks/*
```

### 2. Настройка GitHub Actions
```bash
# Файл уже должен быть в .github/workflows/update-memory-bank.yml
# Настроить секреты в GitHub для автоматических коммитов
```

### 3. Настройка периодических проверок
```bash
# Добавить в crontab для ежедневной проверки
0 9 * * * /path/to/project/scripts/check-memory-bank-freshness.sh
```

### 4. Интеграция с IDE
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check Memory Bank",
      "type": "shell",
      "command": "./scripts/check-memory-bank-freshness.sh",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    },
    {
      "label": "Update Memory Bank",
      "type": "shell",
      "command": "./scripts/update-memory-bank.sh",
      "group": "build"
    }
  ]
}
```

## 📋 Чеклист для разработчиков

### При изменении API
- [ ] Обновить `memory-bank/api-endpoints.md`
- [ ] Запустить `scripts/scan-api-changes.sh`
- [ ] Проверить примеры запросов и ответов

### При изменении моделей БД
- [ ] Обновить `memory-bank/database-schema.md`
- [ ] Обновить ER-диаграмму
- [ ] Документировать новые индексы и ограничения

### При изменении UI компонентов
- [ ] Обновить `memory-bank/ui-components.md`
- [ ] Обновить примеры использования
- [ ] Проверить дизайн-систему

### При добавлении новых модулей
- [ ] Обновить `memory-bank/modules-system.md`
- [ ] Документировать взаимосвязи с другими модулями
- [ ] Обновить общую схему системы

## 🎯 Цели автоматизации

1. **Актуальность** - документация всегда соответствует коду
2. **Консистентность** - единый стиль и структура
3. **Полнота** - все изменения отражены в документации
4. **Эффективность** - минимум ручной работы
5. **Качество** - автоматические проверки и валидация

## 🚀 Будущие улучшения

### Версия 2.0
- **AI-ассистент** для автоматического написания документации
- **Интеграция с Swagger** для автогенерации API документации
- **Визуальные диаграммы** из кода (архитектура, схема БД)
- **Интерактивные примеры** с возможностью тестирования

### Версия 3.0
- **Семантический анализ** изменений в коде
- **Автоматические PR** с обновлениями документации
- **Интеграция с Notion/Confluence** для внешней документации
- **Метрики использования** документации

---

*Автоматическое обновление Memory Bank обеспечивает актуальность и качество документации проекта*
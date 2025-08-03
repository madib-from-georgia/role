# Работа с виртуальным окружением

## Быстрый старт

### Автоматический запуск (рекомендуется)
```bash
# Запуск всего приложения с автоматической настройкой venv
./scripts/start.sh
```

### Ручная настройка venv
```bash
# Активация виртуального окружения
source scripts/activate-venv.sh

# Или напрямую
source .venv/bin/activate

# Проверка, что используется venv
which python3  # Должно показать путь с .venv
which pip      # Должно показать путь с .venv
```

### Установка зависимостей
```bash
# В backend директории с активированным venv
cd backend
pip install -r requirements.txt
```

### Запуск тестов
```bash
# Активировать venv и запустить тесты
cd backend
source ../.venv/bin/activate
python3 -m pytest tests/ -v
```

## Обновленные зависимости

### Замененные библиотеки
- ❌ **PyPDF2** → ✅ **pypdf** (исправлено deprecation warning)
- ✅ **chardet** добавлен для определения кодировки текста

### Текущие зависимости
```
# Web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# File processing
pypdf==3.17.4                # ← ОБНОВЛЕНО
chardet==5.2.0               # ← ДОБАВЛЕНО
python-docx==1.1.0
lxml==4.9.3
beautifulsoup4==4.12.2
zipfile36==0.1.3

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.11.0
flake8==6.1.0
isort==5.12.0
mypy==1.7.1
```

## Проверка состояния

### Проверка активации venv
```bash
echo $VIRTUAL_ENV  # Должно показать путь к .venv
```

### Проверка установленных пакетов
```bash
pip list | grep -E "(pypdf|chardet|fastapi)"
```

### Запуск тестов парсеров
```bash
# Тест всех парсеров (без PyPDF2 warnings)
python3 -m pytest tests/test_parsers.py -v
```

## Полезные команды

### Деактивация venv
```bash
deactivate
```

### Обновление зависимостей
```bash
pip install --upgrade -r requirements.txt
```

### Создание нового venv (если нужно)
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Результат миграции

✅ **Исправлены проблемы:**
- PyPDF2 deprecation warning больше не появляется
- Все пакеты используются из .venv
- PDF парсер работает с современной библиотекой pypdf
- Все тесты проходят (18/18 для парсеров)

✅ **Добавлены улучшения:**
- Автоматическая проверка venv в start.sh
- Вспомогательный скрипт activate-venv.sh
- chardet для лучшего определения кодировки

⚠️ **Остающиеся warnings (не критичные):**
- passlib: 'crypt' deprecated (известная проблема)
- pypdf: ARC4 cryptography warning (внутренняя проблема библиотеки)

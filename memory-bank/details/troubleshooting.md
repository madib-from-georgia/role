# Troubleshooting Guide

## 🚨 Частые проблемы и решения

### 🔧 Проблемы установки и запуска

#### Проблема: "Python не найден" или "python3 command not found"
**Симптомы**:
```bash
bash: python3: command not found
# или
'python3' is not recognized as an internal or external command
```

**Решение**:
```bash
# macOS - установка через Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# Windows - скачать с python.org
# Убедиться что Python добавлен в PATH

# Проверка установки
python3 --version  # должно показать 3.11+
```

#### Проблема: "Node.js версия не поддерживается"
**Симптомы**:
```bash
error: This version of Node.js requires Node.js >= 18.0.0
```

**Решение**:
```bash
# Установка через nvm (рекомендуется)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Или через официальный сайт nodejs.org
# Скачать и установить Node.js 18+

# Проверка
node --version  # должно показать v18+
npm --version
```

#### Проблема: "Виртуальное окружение не активируется"
**Симптомы**:
```bash
# Команда не работает или показывает ошибку
source .venv/bin/activate
```

**Решение**:
```bash
# Пересоздать виртуальное окружение
rm -rf .venv
python3 -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Проверка активации (должно показать путь к .venv)
which python
```

#### Проблема: "Порты заняты"
**Симптомы**:
```bash
Error: listen EADDRINUSE: address already in use :::8000
Error: listen EADDRINUSE: address already in use :::5173
```

**Решение**:
```bash
# Найти процессы на портах
lsof -i :8000
lsof -i :5173

# Убить процессы
kill -9 <PID>

# Или использовать скрипт проекта
./scripts/kill-ports.sh

# Альтернативно - запуск на других портах
cd backend
uvicorn app.main:app --port 8001

cd frontend
npm run dev -- --port 5174
```

### 📦 Проблемы с зависимостями

#### Проблема: "pip install fails" или ошибки установки Python пакетов
**Симптомы**:
```bash
ERROR: Could not build wheels for some-package
error: Microsoft Visual C++ 14.0 is required
```

**Решение**:
```bash
# Обновить pip
python -m pip install --upgrade pip

# Установить build tools (Windows)
# Скачать "Microsoft C++ Build Tools"

# macOS - установить Xcode command line tools
xcode-select --install

# Linux - установить build-essential
sudo apt install build-essential python3-dev

# Очистить кэш pip
pip cache purge

# Переустановить зависимости
pip install -r requirements.txt --no-cache-dir
```

#### Проблема: "npm install fails" или ошибки Node.js пакетов
**Симптомы**:
```bash
npm ERR! code ERESOLVE
npm ERR! peer dep missing
```

**Решение**:
```bash
# Очистить кэш npm
npm cache clean --force

# Удалить node_modules и package-lock.json
rm -rf node_modules package-lock.json

# Переустановить зависимости
npm install

# Если проблемы с peer dependencies
npm install --legacy-peer-deps

# Обновить npm
npm install -g npm@latest
```

### 🗄️ Проблемы с базой данных

#### Проблема: "Database locked" или "database is locked"
**Симптомы**:
```bash
sqlite3.OperationalError: database is locked
```

**Решение**:
```bash
# Найти процессы, использующие базу данных
lsof backend/database.db

# Убить процессы
kill -9 <PID>

# Или перезапустить backend
./scripts/stop.sh
./scripts/start.sh

# В крайнем случае - пересоздать базу
rm backend/database.db
cd backend
python -c "from app.database.connection import create_tables; create_tables()"
python scripts/import_checklists.py
```

#### Проблема: "Table doesn't exist" или ошибки схемы
**Симптомы**:
```bash
sqlite3.OperationalError: no such table: users
```

**Решение**:
```bash
# Проверить существование базы данных
ls -la backend/database.db

# Пересоздать таблицы
cd backend
python -c "from app.database.connection import create_tables; create_tables()"

# Импортировать чеклисты
python scripts/import_checklists.py

# Проверить структуру базы
sqlite3 backend/database.db ".schema"
```

#### Проблема: "Migration failed" или ошибки Alembic
**Симптомы**:
```bash
alembic.util.exc.CommandError: Can't locate revision identified by 'abc123'
```

**Решение**:
```bash
cd backend

# Проверить текущую версию
alembic current

# Посмотреть историю миграций
alembic history

# Сбросить к базовой версии
alembic downgrade base

# Применить все миграции
alembic upgrade head

# В крайнем случае - пересоздать базу
rm database.db alembic/versions/*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 🔐 Проблемы с авторизацией

#### Проблема: "JWT token invalid" или "Token has expired"
**Симптомы**:
```bash
HTTP 401: {"detail": "Could not validate credentials"}
```

**Решение**:
```bash
# Очистить localStorage в браузере
# F12 -> Application -> Local Storage -> Clear All

# Или программно
localStorage.clear()

# Проверить настройки JWT в backend/.env
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Перезапустить backend
cd backend
uvicorn app.main:app --reload
```

#### Проблема: "CORS error" или блокировка запросов
**Симптомы**:
```bash
Access to fetch at 'http://localhost:8000/api/auth/login' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Решение**:
```python
# Проверить настройки CORS в backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Перезапустить backend
```

### 📄 Проблемы с обработкой файлов

#### Проблема: "File upload fails" или ошибки загрузки
**Симптомы**:
```bash
HTTP 413: Request Entity Too Large
HTTP 400: Unsupported file format
```

**Решение**:
```python
# Проверить настройки в backend/.env
MAX_FILE_SIZE=100000000  # 100MB
ALLOWED_EXTENSIONS=txt,pdf,fb2,epub

# Проверить размер файла
ls -lh your-file.pdf

# Для больших файлов - увеличить лимит
# backend/app/main.py
app.add_middleware(
    LimitUploadSizeMiddleware, 
    max_upload_size=200_000_000  # 200MB
)
```

#### Проблема: "PDF parsing fails" или ошибки парсинга
**Симптомы**:
```bash
PdfReadError: EOF marker not found
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Решение**:
```bash
# Проверить файл на повреждения
file your-file.pdf

# Попробовать другой PDF reader
pip install PyPDF4 pdfplumber

# Конвертировать файл в другой формат
# Использовать онлайн конвертеры или Adobe Acrobat

# Проверить логи backend для деталей
tail -f backend/logs/app.log
```

### 🧠 Проблемы с NLP обработкой

#### Проблема: "Character extraction fails" или не находит персонажей
**Симптомы**:
- Обработка завершается, но персонажи не найдены
- Найдены неправильные персонажи

**Решение**:
```bash
# Проверить качество текста
head -n 50 backend/uploads/your-file.txt

# Проверить настройки NLP
# backend/app/services/nlp_processor.py
MIN_CHARACTER_MENTIONS = 3
MIN_IMPORTANCE_SCORE = 0.1

# Запустить обработку в debug режиме
cd backend
python scripts/test_nlp_processing.py your-file.txt

# Проверить логи NLP
python scripts/view_nlp_logs.py
```

#### Проблема: "Speech attribution incorrect" или неправильная атрибуция речи
**Симптомы**:
- Реплики приписаны не тем персонажам
- Пропущены реплики

**Решение**:
```python
# Проверить паттерны речи в коде
# backend/app/services/nlp/extractors/speech_extractor.py

# Настроить паттерны для конкретного формата
SPEECH_PATTERNS = [
    r'^([А-ЯЁ][а-яё]+):\s*(.+)$',  # "Гамлет: Быть или не быть"
    r'^([А-ЯЁ][а-яё]+)\.\s*(.+)$',  # "Гамлет. Быть или не быть"
]

# Тестировать на конкретном тексте
python scripts/test_speech_attribution.py
```

### 🎨 Проблемы с интерфейсом

#### Проблема: "White screen" или пустая страница
**Симптомы**:
- Приложение не загружается
- Белый экран в браузере

**Решение**:
```bash
# Проверить консоль браузера (F12)
# Найти JavaScript ошибки

# Проверить сборку frontend
cd frontend
npm run build

# Проверить dev сервер
npm run dev

# Очистить кэш браузера
# Ctrl+Shift+R (hard refresh)

# Проверить сетевые запросы
# F12 -> Network tab
```

#### Проблема: "API requests fail" или ошибки запросов
**Симптомы**:
```bash
Failed to fetch
Network Error
```

**Решение**:
```typescript
// Проверить базовый URL API
// frontend/src/services/api.ts
const API_BASE_URL = 'http://localhost:8000'

// Проверить статус backend
curl http://localhost:8000/health

// Проверить CORS настройки
// Смотри раздел "Проблемы с авторизацией"

// Добавить обработку ошибок
try {
  const response = await api.get('/endpoint')
} catch (error) {
  console.error('API Error:', error)
}
```

### 📊 Проблемы с производительностью

#### Проблема: "Slow response times" или медленная работа
**Симптомы**:
- Долгая загрузка страниц
- Медленные API запросы

**Решение**:
```bash
# Проверить использование ресурсов
top
htop

# Профилирование backend
cd backend
python -m cProfile -o profile.stats app/main.py

# Анализ профиля
pip install snakeviz
snakeviz profile.stats

# Проверить размер базы данных
ls -lh backend/database.db

# Оптимизировать запросы
sqlite3 backend/database.db "ANALYZE;"
```

#### Проблема: "Memory leaks" или утечки памяти
**Симптомы**:
- Постоянно растущее потребление памяти
- Приложение становится медленным со временем

**Решение**:
```bash
# Мониторинг памяти
pip install memory-profiler
python -m memory_profiler backend/app/main.py

# Проверить кэш
# Очистить кэш результатов NLP
rm -rf backend/cache/*

# Перезапустить приложение
./scripts/stop.sh
./scripts/start.sh
```

## 🔍 Диагностические команды

### Проверка системы
```bash
# Версии
python3 --version
node --version
npm --version
git --version

# Свободное место
df -h

# Память
free -h

# Процессы
ps aux | grep python
ps aux | grep node
```

### Проверка приложения
```bash
# Статус сервисов
curl http://localhost:8000/health
curl http://localhost:5173

# Логи
tail -f backend/logs/app.log
tail -f backend/logs/nlp.log

# База данных
sqlite3 backend/database.db ".tables"
sqlite3 backend/database.db "SELECT COUNT(*) FROM users;"
```

### Сбор информации для отчета об ошибке
```bash
# Создать диагностический отчет
echo "=== System Info ===" > debug_report.txt
uname -a >> debug_report.txt
python3 --version >> debug_report.txt
node --version >> debug_report.txt

echo "=== Disk Space ===" >> debug_report.txt
df -h >> debug_report.txt

echo "=== Memory ===" >> debug_report.txt
free -h >> debug_report.txt

echo "=== Processes ===" >> debug_report.txt
ps aux | grep -E "(python|node)" >> debug_report.txt

echo "=== Recent Logs ===" >> debug_report.txt
tail -n 50 backend/logs/app.log >> debug_report.txt

echo "=== Database Info ===" >> debug_report.txt
ls -la backend/database.db >> debug_report.txt
```

## 🆘 Когда обращаться за помощью

### Создание issue в GitHub
При создании issue включите:

1. **Описание проблемы** - что происходит и что ожидалось
2. **Шаги для воспроизведения** - как повторить проблему
3. **Системная информация** - ОС, версии Python/Node.js
4. **Логи ошибок** - полный текст ошибки
5. **Скриншоты** - если проблема визуальная

### Шаблон issue
```markdown
## Описание проблемы
Краткое описание того, что происходит.

## Шаги для воспроизведения
1. Перейти к '...'
2. Нажать на '...'
3. Прокрутить вниз до '...'
4. Увидеть ошибку

## Ожидаемое поведение
Описание того, что должно происходить.

## Скриншоты
Если применимо, добавьте скриншоты.

## Системная информация
- ОС: [например, macOS 13.0]
- Python: [например, 3.11.0]
- Node.js: [например, 18.12.0]
- Браузер: [например, Chrome 108.0]

## Дополнительный контекст
Любая другая информация о проблеме.
```

## 🔄 Процедуры восстановления

### Полный сброс приложения
```bash
# 1. Остановить все процессы
./scripts/stop.sh

# 2. Удалить базу данных
rm backend/database.db

# 3. Очистить кэш
rm -rf backend/cache/*
rm -rf backend/uploads/*

# 4. Пересоздать виртуальное окружение
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# 5. Переустановить зависимости
cd backend
pip install -r requirements.txt

cd ../frontend
rm -rf node_modules package-lock.json
npm install

# 6. Пересоздать базу данных
cd ../backend
python -c "from app.database.connection import create_tables; create_tables()"
python scripts/import_checklists.py

# 7. Запустить приложение
cd ..
./scripts/start.sh
```

### Восстановление из резервной копии
```bash
# Если есть резервная копия базы данных
cp backup/database.db backend/database.db

# Проверить целостность
sqlite3 backend/database.db "PRAGMA integrity_check;"

# Запустить приложение
./scripts/start.sh
```

---

*Этот гид поможет решить большинство проблем. При возникновении новых проблем - обновляйте документацию!*
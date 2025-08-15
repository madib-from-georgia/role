# Development Workflow

## 🚀 Процесс разработки

### Git Flow
Проект использует упрощенную версию Git Flow с основными ветками:

```
main (production)
├── develop (integration)
│   ├── feature/new-checklist-ui
│   ├── feature/export-improvements
│   └── hotfix/critical-bug-fix
└── release/v1.1.0
```

**Основные ветки**:
- `main` - стабильная production версия
- `develop` - интеграционная ветка для разработки
- `feature/*` - новые функции
- `hotfix/*` - критические исправления
- `release/*` - подготовка к релизу

### Workflow команд

#### Создание новой функции
```bash
# 1. Создание ветки от develop
git checkout develop
git pull origin develop
git checkout -b feature/character-analysis-improvements

# 2. Разработка с коммитами
git add .
git commit -m "feat: add new analysis module"

# 3. Пуш и создание PR
git push origin feature/character-analysis-improvements
# Создать Pull Request в GitHub/GitLab

# 4. После ревью - мерж в develop
git checkout develop
git pull origin develop
git branch -d feature/character-analysis-improvements
```

#### Hotfix процесс
```bash
# 1. Создание hotfix от main
git checkout main
git pull origin main
git checkout -b hotfix/fix-critical-export-bug

# 2. Исправление и коммит
git add .
git commit -m "fix: resolve PDF export crash"

# 3. Мерж в main и develop
git checkout main
git merge hotfix/fix-critical-export-bug
git tag v1.0.1
git push origin main --tags

git checkout develop
git merge hotfix/fix-critical-export-bug
git push origin develop
```

### Соглашения о коммитах

Используется [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Типы коммитов**:
- `feat` - новая функция
- `fix` - исправление бага
- `docs` - изменения в документации
- `style` - форматирование кода
- `refactor` - рефакторинг без изменения функциональности
- `test` - добавление или изменение тестов
- `chore` - изменения в сборке, зависимостях

**Примеры**:
```bash
feat(checklist): add emotional intelligence module
fix(export): resolve PDF generation for large texts
docs(api): update authentication endpoints
refactor(ui): extract reusable button component
test(nlp): add unit tests for character extraction
chore(deps): update React to v18.2.0
```

## 🏗️ Настройка окружения разработки

### Требования к системе
- **Node.js** 18.0.0+
- **Python** 3.11+
- **Git** 2.30+
- **VS Code** (рекомендуется)

### Первоначальная настройка

#### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd role
```

#### 2. Настройка backend
```bash
# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
cd backend
pip install -r requirements.txt

# Настройка базы данных
python -c "from app.database.connection import create_tables; create_tables()"

# Импорт чеклистов
python scripts/import_checklists.py
```

#### 3. Настройка frontend
```bash
cd frontend
npm install

# Проверка типов
npm run type-check

# Линтинг
npm run lint
```

#### 4. Переменные окружения
```bash
# backend/.env
DATABASE_URL=sqlite:///./database.db
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Опционально для AI сервисов
YANDEX_GPT_API_KEY=your-yandex-api-key
OPENAI_API_KEY=your-openai-api-key
```

### VS Code настройка

#### Рекомендуемые расширения
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-eslint"
  ]
}
```

#### Настройки workspace
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/node_modules": true,
    "**/dist": true
  }
}
```

#### Задачи VS Code
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "cd backend && source ../.venv/bin/activate && uvicorn app.main:app --reload",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

## 🧪 Тестирование

### Backend тестирование

#### Структура тестов
```
backend/tests/
├── conftest.py              # Фикстуры pytest
├── test_auth.py            # Тесты авторизации
├── test_projects.py        # Тесты проектов
├── test_characters.py      # Тесты персонажей
├── test_checklists.py      # Тесты чеклистов
├── test_nlp_processor.py   # Тесты NLP
└── test_export.py          # Тесты экспорта
```

#### Запуск тестов
```bash
cd backend

# Все тесты
pytest

# Конкретный файл
pytest tests/test_auth.py

# С покрытием кода
pytest --cov=app --cov-report=html

# Только быстрые тесты
pytest -m "not slow"

# Параллельное выполнение
pytest -n auto
```

#### Пример теста
```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data

def test_login_user():
    # Сначала регистрируем пользователя
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser", 
        "password": "testpass123"
    })
    
    # Затем логинимся
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
```

### Frontend тестирование

#### Структура тестов
```
frontend/src/tests/
├── components/
│   ├── auth/
│   │   ├── LoginForm.test.tsx
│   │   └── RegisterForm.test.tsx
│   ├── checklists/
│   │   ├── ChecklistForm.test.tsx
│   │   └── QuestionCard.test.tsx
│   └── common/
│       ├── Button.test.tsx
│       └── Modal.test.tsx
├── pages/
│   ├── Login.test.tsx
│   └── ProjectDetail.test.tsx
├── services/
│   ├── api.test.ts
│   └── auth.test.ts
├── utils/
│   └── helpers.test.ts
└── mocks/
    ├── handlers.ts
    └── server.ts
```

#### Настройка тестирования
```bash
cd frontend

# Установка зависимостей для тестирования
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom

# Запуск тестов
npm run test

# Тесты в watch режиме
npm run test:watch

# Покрытие кода
npm run test:coverage
```

#### Конфигурация Vitest
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.d.ts',
      ],
    },
  },
})
```

#### Пример теста компонента
```typescript
// src/tests/components/common/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../../../components/common/Button'

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>)
    expect(screen.getByText('Loading')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

## 📦 Сборка и деплой

### Локальная сборка

#### Frontend
```bash
cd frontend

# Сборка для production
npm run build

# Предварительный просмотр сборки
npm run preview

# Анализ размера бандла
npm run build:analyze
```

#### Backend
```bash
cd backend

# Проверка зависимостей
pip check

# Создание requirements.txt
pip freeze > requirements.txt

# Проверка безопасности
pip-audit
```

### Production деплой

#### Подготовка к релизу
```bash
# 1. Создание release ветки
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0

# 2. Обновление версии
# Обновить version в package.json, pyproject.toml
# Обновить CHANGELOG.md

# 3. Финальное тестирование
npm run test
cd backend && pytest

# 4. Мерж в main
git checkout main
git merge release/v1.1.0
git tag v1.1.0
git push origin main --tags

# 5. Мерж обратно в develop
git checkout develop
git merge release/v1.1.0
git push origin develop
```

#### Автоматический деплой (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Install Node dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Run Python tests
        run: |
          cd backend
          pytest
          
      - name: Run Node tests
        run: |
          cd frontend
          npm run test
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build frontend
        run: |
          cd frontend
          npm ci
          npm run build
          
      - name: Deploy to server
        run: |
          # Деплой на сервер через SSH
          echo "Deploying to production server..."
```

## 🔧 Инструменты разработки

### Линтинг и форматирование

#### Python (Backend)
```bash
# Установка инструментов
pip install black isort pylint mypy

# Форматирование кода
black backend/
isort backend/

# Линтинг
pylint backend/app/

# Проверка типов
mypy backend/app/
```

#### TypeScript (Frontend)
```bash
# Установка инструментов
npm install --save-dev eslint prettier @typescript-eslint/parser

# Форматирование
npx prettier --write "src/**/*.{ts,tsx}"

# Линтинг
npx eslint "src/**/*.{ts,tsx}"

# Проверка типов
npx tsc --noEmit
```

### Pre-commit hooks
```bash
# Установка pre-commit
pip install pre-commit

# Настройка hooks
pre-commit install

# Ручной запуск
pre-commit run --all-files
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0-alpha.4
    hooks:
      - id: prettier
        files: \.(js|ts|tsx|json|css|md)$
```

### Отладка

#### Backend отладка
```python
# Использование debugger
import pdb; pdb.set_trace()

# Или с ipdb для лучшего интерфейса
import ipdb; ipdb.set_trace()

# Логирование
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

#### Frontend отладка
```typescript
// React Developer Tools
// Установить расширение для браузера

// Отладка в VS Code
// Настроить launch.json для отладки

// Console debugging
console.log('Debug info:', data)
console.table(arrayData)
console.group('Group name')
console.groupEnd()
```

## 📊 Мониторинг и профилирование

### Performance мониторинг

#### Backend
```python
# Профилирование с cProfile
python -m cProfile -o profile.stats script.py

# Анализ с snakeviz
pip install snakeviz
snakeviz profile.stats

# Memory profiling
pip install memory-profiler
@profile
def my_function():
    # код функции
    pass
```

#### Frontend
```typescript
// React Profiler
import { Profiler } from 'react'

function onRenderCallback(id, phase, actualDuration) {
  console.log('Component:', id, 'Phase:', phase, 'Duration:', actualDuration)
}

<Profiler id="App" onRender={onRenderCallback}>
  <App />
</Profiler>

// Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
getFCP(console.log)
getLCP(console.log)
getTTFB(console.log)
```

### Логирование

#### Структурированные логи
```python
# backend/app/utils/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 🚨 Troubleshooting

### Частые проблемы

#### "Module not found" ошибки
```bash
# Python
pip install -r requirements.txt
# Проверить PYTHONPATH

# Node.js
npm install
# Очистить кэш: npm cache clean --force
# Удалить node_modules и переустановить
```

#### Проблемы с базой данных
```bash
# Пересоздать базу данных
rm backend/database.db
cd backend
python -c "from app.database.connection import create_tables; create_tables()"
python scripts/import_checklists.py
```

#### Проблемы с портами
```bash
# Найти процесс на порту
lsof -i :8000
lsof -i :5173

# Убить процесс
kill -9 <PID>

# Или использовать скрипт
./scripts/kill-ports.sh
```

---

*Workflow настроен для эффективной разработки, тестирования и деплоя высококачественного кода*
# Анализ Персонажей — Веб-приложение для актеров

Веб-приложение для детального анализа персонажей художественных произведений с использованием современных психологических теорий и театральной методологии Станиславского.

## 🎯 Описание проекта

**Анализ Персонажей** — это профессиональный инструмент для актеров, позволяющий создавать глубокие, научно обоснованные характеристики персонажей через систему структурированных опросников.

### Ключевые возможности

- 📚 **Поддержка множества форматов**: TXT, PDF, FB2, EPUB
- 🧠 **20 модулей анализа**: 13 базовых + 7 психологических
- 📝 **Система опросников**: Структурированные чеклисты для каждого модуля
- 🤖 **Автоматический анализ**: Поиск персонажей и атрибуция речи
- 📄 **Экспорт результатов**: Полные отчеты в PDF формате
- 🎭 **Научная обоснованность**: Базируется на проверенных психологических теориях

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                    Yandex Cloud                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   React App     │  │   FastAPI       │                  │
│  │   (Frontend)    │◄─┤   (Backend)     │                  │
│  │   Port 5173     │  │   Port 8000     │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                              │                              │
│                       ┌─────────────────┐                  │
│                       │   SQLite DB     │                  │
│                       │   (database.db) │                  │
│                       └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Технический стек

#### Frontend
- **React 18** с TypeScript
- **Vite** для сборки и dev-сервера  
- **Custom CSS** для стилизации
- **React Query** для управления состоянием
- **React Hook Form** для работы с формами

#### Backend
- **Python 3.11+** с FastAPI
- **SQLAlchemy** для работы с базой данных
- **Pydantic** для валидации данных
- **Python-multipart** для загрузки файлов

#### База данных
- **SQLite** для локального хранения данных
- **Файловая система** для хранения загруженных произведений

#### ML/NLP сервисы
- **Готовый модуль анализа** (интеграция из существующего проекта)
- **Библиотеки парсинга**: pdf-parse, epub-parser, fb2-parser

## 📊 Модели данных

### Основные сущности

```sql
-- Пользователи системы
users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Проекты пользователя
projects (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Загруженные произведения
texts (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  filename VARCHAR(255) NOT NULL,
  original_format VARCHAR(10) NOT NULL,
  content TEXT,
  metadata JSON,
  processed_at TIMESTAMP
);

-- Найденные персонажи
characters (
  id SERIAL PRIMARY KEY,
  text_id INTEGER REFERENCES texts(id),
  name VARCHAR(255) NOT NULL,
  aliases JSON,
  importance_score FLOAT,
  speech_attribution JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Результаты заполнения чеклистов
character_checklist_responses (
  id SERIAL PRIMARY KEY,
  character_id INTEGER REFERENCES characters(id),
  checklist_type VARCHAR(50) NOT NULL,
  question_id VARCHAR(100) NOT NULL,
  response TEXT,
  confidence_level INTEGER DEFAULT 3,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- JWT токены для авторизации
user_tokens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(255) NOT NULL,
  token_type VARCHAR(20) DEFAULT 'access',  -- access, refresh
  expires_at TIMESTAMP NOT NULL,
  is_revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧠 Система модулей анализа

### Базовые модули (1-13)

1. **Физический портрет** - внешность, движения, голос
2. **Эмоциональный профиль** - базовые эмоции, триггеры, регуляция
3. **Речевые характеристики** - лексика, синтаксис, стиль
4. **Внутренние конфликты** - психологические противоречия
5. **Мотивация и цели** - сверхзадача по Станиславскому
6. **Отношения с персонажами** - динамика взаимодействий
7. **Предыстория и биография** - жизненная история
8. **Социальный статус** - положение в обществе
9. **Ключевые сцены** - поворотные моменты
10. **Актерские задачи** - конкретные задания
11. **Практические упражнения** - этюды для вживания
12. **Анализ подтекста** - скрытые смыслы
13. **Темпо-ритм** - ритмические характеристики

### Психологические модули (14-20)

14. **Психотип личности** - MBTI, Big Five, типология Юнга
15. **Защитные механизмы** - по теории Анны Фрейд
16. **Травмы и ПТСР** - травматические события и симптомы
17. **Архетипы** - по К. Г. Юнгу
18. **Эмоциональный интеллект** - модели Майера-Саловея, Гоулмана
19. **Когнитивные искажения** - паттерны мышления из КПТ
20. **Стили привязанности** - теория Боулби

## 🚀 Установка и запуск

### Локальная разработка

#### Требования к системе
- **Python 3.11+**
- **Node.js 18+**
- **curl** (для проверки запуска сервисов)

#### Быстрый старт

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd role
```

2. **Настройка переменных окружения** (опционально)
```bash
# backend/.env
DATABASE_URL=sqlite:///./database.db
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100000000
ALLOWED_EXTENSIONS=txt,pdf,fb2,epub

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_PER_MINUTE=100

# CORS (для production)
FRONTEND_URL=https://your-domain.com
```

3. **Запуск приложения одной командой**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

Скрипт автоматически:
- ✅ Проверит наличие Python3 и Node.js
- ✅ Создаст виртуальное окружение `.venv`
- ✅ Активирует venv и проверит корректность
- ✅ Установит все зависимости backend и frontend
- ✅ Запустит оба сервиса
- ✅ Проверит корректность запуска

> 📝 **Виртуальное окружение**: Все Python пакеты устанавливаются в изолированное окружение `.venv`. Подробнее см. [VENV_SETUP.md](docs/VENV_SETUP.md)

4. **Доступ к приложению**
После успешного запуска будут доступны:
- 🌐 **Веб-интерфейс**: http://localhost:5173
- 📚 **API документация**: http://localhost:8000/docs  
- 🔧 **API эндпоинт**: http://localhost:8000

5. **Остановка приложения**
```bash
# Способ 1: Мягкая остановка (если start.sh запущен)
# Нажмите Ctrl+C в терминале где запущен start.sh

# Способ 2: Принудительная остановка всех процессов
chmod +x scripts/stop.sh
./scripts/stop.sh
```

> **Примечание**: Скрипт `stop.sh` принудительно завершает все процессы на портах 8000, 5173-5175 и останавливает процессы `uvicorn` и `vite`

#### Ручная установка (для разработки)

<details>
<summary>Развернуть инструкции ручной установки</summary>

```bash
# 1. Backend setup
python3 -m venv .venv
source .venv/bin/activate
cd backend
pip install -r requirements.txt
python -c "from app.database.migrations import create_tables; create_tables()"

# 2. Frontend setup  
cd ../frontend
npm install

# 3. Ручной запуск (2 терминала)
# Terminal 1 - Backend
cd backend
source ../.venv/bin/activate
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend  
npx vite --host 0.0.0.0 --port 5173
```
</details>

#### Первый запуск
- Перейдите на http://localhost:5173
- Зарегистрируйтесь через форму регистрации
- Создайте свой первый проект
- Загрузите произведение и начните анализ

#### Диагностика проблем

<details>
<summary>🔍 Если приложение не запускается</summary>

**1. Проверьте версии:**
```bash
python3 --version  # Должно быть >= 3.11
node --version     # Должно быть >= 18
```

**2. Проверьте свободные порты:**
```bash
lsof -i :8000      # Backend порт
lsof -i :5173      # Frontend порт
```

**3. Принудительная очистка:**
```bash
./scripts/stop.sh           # Остановить все процессы
rm -rf .venv                # Удалить виртуальное окружение
rm -rf frontend/node_modules # Удалить node_modules
./scripts/start.sh          # Запустить заново
```

**4. Проверьте логи:**
```bash
# Backend логи
curl http://localhost:8000/docs

# Frontend логи  
curl http://localhost:5173
```

**5. Ручной запуск для отладки:**
- Используйте ручную установку (см. выше)
- Запускайте backend и frontend в отдельных терминалах
- Смотрите ошибки в консоли

</details>

### Развертывание в Yandex Cloud

#### Предварительные требования

- Аккаунт в Yandex Cloud
- Установленный Yandex CLI
- Домен (для покупки в любом регистраторе)

#### Шаги развертывания

1. **Создание виртуальной машины**
```bash
yc compute instance create \
  --name role-app \
  --zone ru-central1-a \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --create-boot-disk image-folder-id=standard-images,image-family=ubuntu-22-04-lts,size=50GB \
  --cores 2 \
  --memory 4GB \
  --ssh-key ~/.ssh/id_rsa.pub
```

2. **Настройка сервера**
```bash
# Подключение к серверу
ssh yc-user@51.250.4.162

# Установка зависимостей
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv nodejs npm nginx -y

# Установка PM2 для управления процессами
sudo npm install -g pm2
```

3. **Деплой приложения**
```bash
# Клонирование проекта
git clone <repository-url> /home/yc-user/role
cd /home/yc-user/role

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend build
cd ../frontend
npm install
npm run build

# PM2 конфигурация
cd /home/yc-user/role
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

4. **Настройка Nginx**
```nginx
# /etc/nginx/sites-available/role
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        root /home/yc-user/role/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

5. **SSL сертификат (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## 📁 Структура проекта

```
role/
├── README.md                    # Этот файл
├── package.json                 # Root package.json
├── .gitignore                   # Git ignore rules
├── ecosystem.config.js          # PM2 configuration
│
├── frontend/                    # React приложение
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── CharacterAnalysis.tsx
│   │   │   ├── ChecklistForm.tsx
│   │   │   ├── AuthGuard.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── ProjectList.tsx
│   │   │   ├── CreateProject.tsx
│   │   │   ├── ProjectDetail.tsx
│   │   │   └── CharacterDetail.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── storage.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useLocalStorage.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── types/
│   │   │   ├── index.ts
│   │   │   └── auth.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts

│
├── backend/                     # Python FastAPI сервер
│   ├── app/
│   │   ├── main.py             # Главный файл FastAPI
│   │   ├── database/
│   │   │   ├── connection.py   # SQLite подключение
│   │   │   ├── migrations.py   # Создание таблиц
│   │   │   └── models/
│   │   │       ├── user.py
│   │   │       ├── token.py
│   │   │       ├── project.py
│   │   │       ├── text.py
│   │   │       ├── character.py
│   │   │       └── checklist.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── texts.py
│   │   │   ├── characters.py
│   │   │   └── checklists.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── jwt_service.py
│   │   │   ├── file_parser.py
│   │   │   ├── character_extractor.py
│   │   │   └── export_service.py
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py
│   │   │   └── cors_middleware.py
│   │   ├── parsers/
│   │   │   ├── txt_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── fb2_parser.py
│   │   │   └── epub_parser.py
│   │   └── utils/
│   │       ├── password_utils.py
│   │       ├── security.py
│   │       ├── text_processing.py
│   │       └── file_utils.py
│   ├── uploads/                # Загруженные файлы
│   ├── database.db            # SQLite база данных
│   ├── requirements.txt
│   └── .env
│
├── shared/                     # Общие типы
│   └── types.ts
│
├── docs/                       # Документация
│   ├── ARCHITECTURE.md
│   ├── MEMORY_BANK.md
│   └── modules/               # Чеклисты модулей
│       ├── 01-physical-portrait/
│       ├── 02-emotional-profile/
│       └── ...
│
└── scripts/                   # Скрипты развертывания
    ├── start.sh
    ├── stop.sh
    └── deploy.sh
```

## 🔧 API Endpoints

### Авторизация
```
POST   /api/auth/register         # Регистрация пользователя
POST   /api/auth/login           # Вход в систему
POST   /api/auth/logout          # Выход из системы
POST   /api/auth/refresh         # Обновление токена
GET    /api/auth/me              # Информация о текущем пользователе
PUT    /api/auth/me              # Обновление профиля
```

### Проекты (требует авторизации)
```
GET    /api/projects              # Список проектов пользователя
POST   /api/projects              # Создать проект
GET    /api/projects/{id}         # Получить проект
PUT    /api/projects/{id}         # Обновить проект
DELETE /api/projects/{id}         # Удалить проект
```

### Тексты (требует авторизации)
```
POST   /api/projects/{id}/texts/upload    # Загрузить файл
GET    /api/projects/{id}/texts           # Список текстов проекта
GET    /api/texts/{id}                    # Получить текст
DELETE /api/texts/{id}                    # Удалить текст
POST   /api/texts/{id}/process            # Обработать текст
```

### Персонажи (требует авторизации)
```
GET    /api/texts/{id}/characters         # Персонажи в тексте
GET    /api/characters/{id}               # Данные персонажа
PUT    /api/characters/{id}               # Обновить персонажа
```

### Чеклисты (требует авторизации)
```
GET    /api/characters/{id}/checklists               # Все чеклисты персонажа
GET    /api/characters/{id}/checklists/{type}        # Конкретный чеклист
POST   /api/characters/{id}/checklists/{type}        # Сохранить ответы
PUT    /api/characters/{id}/checklists/{type}        # Обновить ответы
```

### Экспорт (требует авторизации)
```
GET    /api/characters/{id}/export/pdf     # Экспорт в PDF
GET    /api/characters/{id}/export/docx    # Экспорт в DOCX
```

> **Примечание**: Все API endpoints, кроме авторизации, требуют валидный JWT токен в заголовке `Authorization: Bearer <token>`

## 🛠️ NPM Скрипты

### Основные команды
```bash
npm run start          # Запуск приложения (frontend + backend)
npm run stop           # Остановка приложения
npm run dev            # Алиас для npm run start
npm run build          # Сборка frontend для production
npm run kill-ports     # Остановка процессов на портах 5173 и 8000
```

### Управление чеклистами
```bash
npm run list-checklists        # Показать список всех чеклистов в БД
npm run import-checklists      # Импорт чеклистов из Markdown файлов
npm run clear-checklists       # Показать список чеклистов (без аргументов)
npm run clear-checklists-force # Удалить все чеклисты без подтверждения
```

### Утилиты
```bash
npm run show-user-projects     # Показать проекты пользователей
npm run logs                   # Просмотр NLP логов
npm run lint:md:fix           # Исправить форматирование Markdown файлов
```

### Прямые команды Python
```bash
# Показать список чеклистов
cd backend && python scripts/clear_checklists.py --list

# Удалить все чеклисты (с подтверждением)
cd backend && python scripts/clear_checklists.py --clear-all

# Удалить все чеклисты (без подтверждения)
cd backend && python scripts/clear_checklists.py --clear-all --force

# Удалить конкретный чеклист по slug
cd backend && python scripts/clear_checklists.py --clear-slug physical-checklist

# Валидация чеклистов без импорта
cd backend && python scripts/import_checklists.py --validate-only
```

## 🎨 Пользовательский интерфейс

### Основные страницы

1. **Авторизация** - регистрация и вход в систему
2. **Список проектов** - обзор всех проектов пользователя
3. **Создание проекта** - форма создания нового проекта
4. **Детали проекта** - загрузка файлов, список персонажей
5. **Страница персонажа** - система опросников по модулям
6. **Результаты анализа** - просмотр и экспорт данных
7. **Профиль пользователя** - настройки аккаунта

### Система опросников

Каждый из 20 модулей представлен в виде интерактивного опросника:

- **Структурированные вопросы** с различными типами ответов
- **Градация достоверности** для каждого ответа
- **Автосохранение** прогресса заполнения
- **Навигация между модулями** с индикацией прогресса
- **Валидация данных** и подсказки для пользователя

## 📊 Мониторинг и аналитика

### Метрики производительности

- Время обработки файлов
- Скорость заполнения опросников
- Использование ресурсов сервера
- Размер базы данных

### Логирование

- Действия пользователей
- Ошибки системы
- Производительность API
- Статистика использования модулей

## 🔒 Безопасность

### Система аутентификации

#### JWT Токены
- **Access Token**: срок действия 15 минут
- **Refresh Token**: срок действия 7 дней
- **Automatic Refresh**: обновление токенов на лету
- **Token Revocation**: отзыв скомпрометированных токенов

#### Хеширование паролей
- **bcrypt**: с солью и коэффициентом 12
- **Валидация**: минимум 8 символов, цифры, буквы
- **Защита от брутфорса**: лимит попыток входа

#### Middleware безопасности
- **CORS**: настроенный для production домена
- **Rate Limiting**: 100 запросов в минуту на IP
- **Request Validation**: Pydantic схемы для всех данных

### Защита данных

#### Изоляция пользователей
- **Row Level Security**: каждый пользователь видит только свои данные
- **Foreign Key Constraints**: строгая целостность данных
- **Cascade Deletion**: удаление пользователя удаляет все связанные данные

#### Файловая безопасность
- **Валидация типов файлов**: проверка MIME-типов
- **Ограничение размера**: максимум 100 МБ на файл
- **Вирусное сканирование**: проверка загружаемых файлов
- **Песочница**: изолированная обработка файлов

#### Сетевая безопасность
- **HTTPS**: принудительное шифрование (Let's Encrypt)
- **Secure Headers**: CSP, HSTS, X-Frame-Options
- **IP Whitelist**: ограничение доступа к админ-панели

### Мониторинг безопасности

#### Логирование
- **Аудит входов**: все попытки аутентификации
- **API Calls**: логирование всех запросов с пользователем
- **Error Tracking**: мониторинг подозрительной активности
- **Rate Limit Violations**: отслеживание превышений лимитов

#### Резервное копирование
- **Автоматические бэкапы**: каждые 6 часов
- **Шифрование бэкапов**: AES-256 encryption
- **Удаленное хранение**: Yandex Object Storage
- **Тестирование восстановления**: еженедельные проверки

## 🚀 Планы развития

### Версия 1.0 ✅
- [x] Авторизация пользователей
- [x] Управление проектами  
- [x] Загрузка и обработка произведений
- [x] 20 модулей анализа персонажей
- [x] Система опросников/чеклистов
- [x] Экспорт результатов в PDF

### Версия 2.0
- [ ] Коллаборативная работа над проектами
- [ ] Интеграция с AI сервисами для автоматического заполнения
- [ ] Мобильное приложение (React Native)
- [ ] Расширенная аналитика и дашборды
- [ ] Система уведомлений
- [ ] Интеграция с календарем репетиций

### Версия 3.0
- [ ] Библиотека готовых анализов классических персонажей
- [ ] Интеграция с театральными CRM системами
- [ ] Машинное обучение для предсказания характеристик
- [ ] Голосовой анализ персонажей (voice AI)
- [ ] VR/AR визуализация персонажей

## 📞 Поддержка

### Документация
- [Архитектура системы](docs/ARCHITECTURE.md)
- [Мемори банк проекта](docs/MEMORY_BANK.md)
- [Руководство пользователя](docs/USER_GUIDE.md)


---

*Создано с ❤️ для театрального сообщества*

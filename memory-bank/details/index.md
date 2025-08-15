# Memory Bank Index

> 🔍 **Быстрый поиск по банку знаний проекта** - найдите нужную информацию за секунды

## 🎯 Быстрые ссылки

### Для новых разработчиков
- [Обзор проекта](project-overview.md) - что это за проект и зачем он нужен
- [Техническая архитектура](technical-architecture.md) - как устроена система
- [Процесс разработки](development-workflow.md) - как настроить окружение и начать работу

### Для решения проблем
- [Troubleshooting](troubleshooting.md) - решение типичных проблем
- [API Endpoints](api-endpoints.md) - документация по API
- [База данных](database-schema.md) - схема и запросы

### Для понимания бизнес-логики
- [Система модулей](modules-system.md) - 20 модулей анализа персонажей
- [UI компоненты](ui-components.md) - дизайн-система и интерфейс
- [История изменений](changelog.md) - что было добавлено и когда

## 📚 Тематический указатель

### 🏗️ Архитектура и технологии

#### Backend
- **FastAPI** → [technical-architecture.md#backend](technical-architecture.md#backend-python)
- **SQLAlchemy** → [database-schema.md](database-schema.md)
- **JWT авторизация** → [api-endpoints.md#авторизация](api-endpoints.md#авторизация-apiauth)
- **NLP обработка** → [modules-system.md#nlp-модуль](modules-system.md#nlp-модуль-критически-важный)

#### Frontend
- **React 18** → [technical-architecture.md#frontend](technical-architecture.md#frontend-react)
- **TypeScript** → [ui-components.md](ui-components.md)
- **Компоненты** → [ui-components.md#атомарные-компоненты](ui-components.md#атомарные-компоненты)
- **Дизайн-система** → [ui-components.md#дизайн-философия](ui-components.md#дизайн-философия)

#### База данных
- **Схема таблиц** → [database-schema.md#er-диаграмма](database-schema.md#er-диаграмма)
- **Миграции** → [database-schema.md#миграции-и-версионирование](database-schema.md#миграции-и-версионирование)
- **Оптимизация** → [database-schema.md#производительность](database-schema.md#производительность)

### 🧠 Система анализа персонажей

#### Модули анализа
- **Базовые модули (1-13)** → [modules-system.md#базовые-модули](modules-system.md#базовые-модули-1-13)
- **Психологические модули (14-20)** → [modules-system.md#психологические-модули](modules-system.md#психологические-модули-14-20)
- **Взаимосвязи модулей** → [modules-system.md#взаимосвязи-модулей](modules-system.md#взаимосвязи-модулей)

#### Конкретные модули
- **Физический портрет** → [modules-system.md#1-физический-портрет](modules-system.md#1-физический-портрет-персонажа)
- **Эмоциональный профиль** → [modules-system.md#2-эмоциональный-профиль](modules-system.md#2-эмоциональный-профиль-персонажа)
- **Речевые характеристики** → [modules-system.md#3-речевые-характеристики](modules-system.md#3-речевые-характеристики)
- **Психотип личности** → [modules-system.md#14-психотип-личности](modules-system.md#14-психотип-личности)
- **Защитные механизмы** → [modules-system.md#15-защитные-механизмы](modules-system.md#15-защитные-механизмы-психики)

### 🔧 Разработка и деплой

#### Настройка окружения
- **Требования к системе** → [development-workflow.md#требования-к-системе](development-workflow.md#требования-к-системе)
- **Первоначальная настройка** → [development-workflow.md#первоначальная-настройка](development-workflow.md#первоначальная-настройка)
- **VS Code настройка** → [development-workflow.md#vs-code-настройка](development-workflow.md#vs-code-настройка)

#### Git и версионирование
- **Git Flow** → [development-workflow.md#git-flow](development-workflow.md#git-flow)
- **Соглашения о коммитах** → [development-workflow.md#соглашения-о-коммитах](development-workflow.md#соглашения-о-коммитах)
- **Процесс релиза** → [development-workflow.md#подготовка-к-релизу](development-workflow.md#подготовка-к-релизу)

#### Тестирование
- **Backend тесты** → [development-workflow.md#backend-тестирование](development-workflow.md#backend-тестирование)
- **Frontend тесты** → [development-workflow.md#frontend-тестирование](development-workflow.md#frontend-тестирование)
- **Покрытие кода** → [development-workflow.md#запуск-тестов](development-workflow.md#запуск-тестов)

### 🌐 API и интеграции

#### Эндпоинты
- **Авторизация** → [api-endpoints.md#авторизация](api-endpoints.md#авторизация-apiauth)
- **Проекты** → [api-endpoints.md#проекты](api-endpoints.md#проекты-apiprojects)
- **Персонажи** → [api-endpoints.md#персонажи](api-endpoints.md#персонажи-apicharacters)
- **Чеклисты** → [api-endpoints.md#чеклисты](api-endpoints.md#чеклисты-apichecklists)
- **Экспорт** → [api-endpoints.md#экспорт](api-endpoints.md#экспорт-apiexport)

#### Безопасность
- **JWT токены** → [api-endpoints.md#типы-токенов](api-endpoints.md#типы-токенов)
- **CORS** → [api-endpoints.md#cors](api-endpoints.md#cors)
- **Rate Limiting** → [api-endpoints.md#rate-limiting](api-endpoints.md#rate-limiting)

### 🎨 Пользовательский интерфейс

#### Компоненты
- **Атомарные** → [ui-components.md#атомарные-компоненты](ui-components.md#атомарные-компоненты)
- **Молекулярные** → [ui-components.md#молекулярные-компоненты](ui-components.md#молекулярные-компоненты)
- **Организменные** → [ui-components.md#организменные-компоненты](ui-components.md#организменные-компоненты)
- **Специализированные** → [ui-components.md#специализированные-компоненты](ui-components.md#специализированные-компоненты)

#### Дизайн
- **Цветовая палитра** → [ui-components.md#цветовая-палитра](ui-components.md#цветовая-палитра)
- **Типографика** → [ui-components.md#типографика](ui-components.md#типографика)
- **Адаптивность** → [ui-components.md#адаптивность](ui-components.md#адаптивность)
- **Доступность** → [ui-components.md#доступность-a11y](ui-components.md#доступность-a11y)

## 🚨 Решение проблем

### Частые ошибки
- **"Python не найден"** → [troubleshooting.md#python-не-найден](troubleshooting.md#проблема-python-не-найден-или-python3-command-not-found)
- **"Порты заняты"** → [troubleshooting.md#порты-заняты](troubleshooting.md#проблема-порты-заняты)
- **"Database locked"** → [troubleshooting.md#database-locked](troubleshooting.md#проблема-database-locked-или-database-is-locked)
- **"CORS error"** → [troubleshooting.md#cors-error](troubleshooting.md#проблема-cors-error-или-блокировка-запросов)

### Диагностика
- **Проверка системы** → [troubleshooting.md#проверка-системы](troubleshooting.md#проверка-системы)
- **Проверка приложения** → [troubleshooting.md#проверка-приложения](troubleshooting.md#проверка-приложения)
- **Сбор информации** → [troubleshooting.md#сбор-информации](troubleshooting.md#сбор-информации-для-отчета-об-ошибке)

### Восстановление
- **Полный сброс** → [troubleshooting.md#полный-сброс](troubleshooting.md#полный-сброс-приложения)
- **Восстановление БД** → [troubleshooting.md#восстановление-из-резервной-копии](troubleshooting.md#восстановление-из-резервной-копии)

## 📋 Чеклисты для разработчиков

### Новый разработчик
- [ ] Прочитать [project-overview.md](project-overview.md)
- [ ] Изучить [technical-architecture.md](technical-architecture.md)
- [ ] Настроить окружение по [development-workflow.md](development-workflow.md)
- [ ] Запустить приложение локально
- [ ] Создать тестового пользователя
- [ ] Загрузить тестовое произведение
- [ ] Заполнить один чеклист

### Перед коммитом
- [ ] Запустить тесты: `npm run test` и `pytest`
- [ ] Проверить линтинг: `npm run lint` и `pylint`
- [ ] Проверить типы: `npm run type-check` и `mypy`
- [ ] Обновить документацию при необходимости
- [ ] Следовать [соглашениям о коммитах](development-workflow.md#соглашения-о-коммитах)

### Перед релизом
- [ ] Обновить [changelog.md](changelog.md)
- [ ] Обновить версию в `package.json` и `pyproject.toml`
- [ ] Запустить полное тестирование
- [ ] Проверить сборку frontend: `npm run build`
- [ ] Создать release ветку
- [ ] Протестировать на staging окружении

## 🔍 Поиск по ключевым словам

### A-E
- **API** → [api-endpoints.md](api-endpoints.md)
- **Авторизация** → [api-endpoints.md#авторизация](api-endpoints.md#авторизация-apiauth)
- **Архитектура** → [technical-architecture.md](technical-architecture.md)
- **База данных** → [database-schema.md](database-schema.md)
- **Безопасность** → [api-endpoints.md#безопасность](api-endpoints.md#безопасность)
- **Версионирование** → [development-workflow.md#git-flow](development-workflow.md#git-flow)
- **Деплой** → [development-workflow.md#production-деплой](development-workflow.md#production-деплой)
- **Дизайн** → [ui-components.md](ui-components.md)
- **Ошибки** → [troubleshooting.md](troubleshooting.md)

### F-N
- **FastAPI** → [technical-architecture.md#backend-python](technical-architecture.md#backend-python)
- **Frontend** → [technical-architecture.md#frontend-react](technical-architecture.md#frontend-react)
- **Git** → [development-workflow.md#git-flow](development-workflow.md#git-flow)
- **JWT** → [api-endpoints.md#типы-токенов](api-endpoints.md#типы-токенов)
- **Компоненты** → [ui-components.md](ui-components.md)
- **Миграции** → [database-schema.md#миграции-и-версионирование](database-schema.md#миграции-и-версионирование)
- **Модули** → [modules-system.md](modules-system.md)
- **NLP** → [modules-system.md#nlp-модуль](modules-system.md#nlp-модуль-критически-важный)

### O-Z
- **Персонажи** → [modules-system.md](modules-system.md)
- **Производительность** → [troubleshooting.md#проблемы-с-производительностью](troubleshooting.md#проблемы-с-производительностью)
- **React** → [technical-architecture.md#frontend-react](technical-architecture.md#frontend-react)
- **SQLite** → [database-schema.md](database-schema.md)
- **Тестирование** → [development-workflow.md#тестирование](development-workflow.md#тестирование)
- **TypeScript** → [ui-components.md](ui-components.md)
- **Установка** → [development-workflow.md#настройка-окружения-разработки](development-workflow.md#настройка-окружения-разработки)
- **Чеклисты** → [modules-system.md#структура-модуля](modules-system.md#структура-модуля)
- **Экспорт** → [api-endpoints.md#экспорт](api-endpoints.md#экспорт-apiexport)

## 📊 Статистика Memory Bank

- **Всего документов**: 12
- **Общий объем**: ~4000 строк документации
- **Покрытие тем**: 100% критических аспектов проекта
- **Последнее обновление**: 2025-08-15
- **Версия Memory Bank**: 1.0.0

## 🔄 Обновление индекса

Этот индекс обновляется автоматически при изменениях в документации. Если вы не нашли нужную информацию:

1. Используйте поиск по файлам в VS Code (`Ctrl+Shift+F`)
2. Проверьте [troubleshooting.md](troubleshooting.md) для решения проблем
3. Обратитесь к команде разработки
4. Создайте issue для улучшения документации

---

*Индекс создан для быстрого поиска информации в Memory Bank проекта "Анализ Персонажей"*
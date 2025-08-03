# Makefile для backend приложения "Анализ Персонажей"

# Переменные
PYTHON = python3
PIP = pip
PYTEST = pytest
VENV = .venv
APP_MODULE = app.main:app

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help install install-dev venv clean test test-cov lint format run dev db-init db-reset check all

# Помощь
help:
	@echo "$(GREEN)Команды для разработки backend приложения:$(NC)"
	@echo ""
	@echo "$(YELLOW)Установка и настройка:$(NC)"
	@echo "  install      - Установить зависимости"
	@echo "  install-dev  - Установить зависимости для разработки"
	@echo "  venv         - Создать виртуальное окружение"
	@echo ""
	@echo "$(YELLOW)Разработка:$(NC)"
	@echo "  run          - Запустить приложение"
	@echo "  dev          - Запустить в режиме разработки"
	@echo "  test         - Запустить тесты"
	@echo "  test-cov     - Запустить тесты с покрытием"
	@echo "  lint         - Проверить код линтерами"
	@echo "  format       - Форматировать код"
	@echo ""
	@echo "$(YELLOW)База данных:$(NC)"
	@echo "  db-init      - Инициализировать базу данных"
	@echo "  db-reset     - Сбросить базу данных"
	@echo ""
	@echo "$(YELLOW)Утилиты:$(NC)"
	@echo "  clean        - Очистить временные файлы"
	@echo "  check        - Проверить всё (тесты + линтеры)"
	@echo "  all          - Полная настройка проекта"

# Создание виртуального окружения
venv:
	@echo "$(GREEN)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Активируйте окружение: source $(VENV)/bin/activate$(NC)"

# Установка зависимостей
install:
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt

# Установка зависимостей для разработки
install-dev: install
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	$(PIP) install pytest-asyncio pytest-cov black flake8 isort mypy

# Запуск приложения
run:
	@echo "$(GREEN)Запуск приложения...$(NC)"
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port 8000

# Запуск в режиме разработки
dev:
	@echo "$(GREEN)Запуск в режиме разработки...$(NC)"
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port 8000 --reload

# Инициализация базы данных
db-init:
	@echo "$(GREEN)Инициализация базы данных...$(NC)"
	$(PYTHON) -c "import asyncio; from app.database.connection import init_db; asyncio.run(init_db())"

# Сброс базы данных
db-reset:
	@echo "$(YELLOW)Сброс базы данных...$(NC)"
	rm -f database.db
	$(MAKE) db-init

# Запуск тестов
test:
	@echo "$(GREEN)Запуск тестов...$(NC)"
	$(PYTEST)

# Запуск тестов с покрытием
test-cov:
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	$(PYTEST) --cov=app --cov-report=term-missing --cov-report=html

# Линтеры
lint:
	@echo "$(GREEN)Проверка кода линтерами...$(NC)"
	flake8 app tests --max-line-length=100 --ignore=E203,W503
	mypy app --ignore-missing-imports
	@echo "$(GREEN)Линтеры пройдены!$(NC)"

# Форматирование кода
format:
	@echo "$(GREEN)Форматирование кода...$(NC)"
	black app tests --line-length=100
	isort app tests --profile black
	@echo "$(GREEN)Код отформатирован!$(NC)"

# Очистка временных файлов
clean:
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf uploads/ test_uploads/ logs/
	@echo "$(GREEN)Очистка завершена!$(NC)"

# Полная проверка
check: lint test
	@echo "$(GREEN)Все проверки пройдены!$(NC)"

# Полная настройка проекта
all: install-dev db-init test
	@echo "$(GREEN)Проект полностью настроен и готов к работе!$(NC)"

# Проверка статуса приложения
status:
	@echo "$(GREEN)Проверка статуса приложения...$(NC)"
	curl -s http://localhost:8000/health | jq . || echo "$(RED)Приложение не запущено$(NC)"

# Просмотр логов
logs:
	@echo "$(GREEN)Последние логи приложения:$(NC)"
	tail -f logs/*.log 2>/dev/null || echo "$(YELLOW)Логи не найдены$(NC)"

# Установка pre-commit hooks
pre-commit:
	@echo "$(GREEN)Настройка pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks установлены!$(NC)"

# Обновление зависимостей
update:
	@echo "$(GREEN)Обновление зависимостей...$(NC)"
	$(PIP) install --upgrade -r requirements.txt

# Создание миграции (заготовка для будущего)
migration:
	@echo "$(YELLOW)Создание миграции базы данных...$(NC)"
	@echo "TODO: Реализовать создание миграций с Alembic"

# Применение миграций (заготовка для будущего)
migrate:
	@echo "$(GREEN)Применение миграций...$(NC)"
	@echo "TODO: Реализовать применение миграций с Alembic"

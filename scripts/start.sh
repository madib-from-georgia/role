#!/bin/bash

# Скрипт для запуска приложения Role
# Запускает бэкенд и фронтенд одновременно

set -e

echo "🚀 Запуск приложения Role..."

# Проверяем, что мы в правильной директории
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Функция для остановки процессов при завершении скрипта
cleanup() {
    echo ""
    echo "🛑 Остановка приложения..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Устанавливаем обработчик сигналов
trap cleanup SIGINT SIGTERM

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.11+"
    exit 1
fi

# Проверяем Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Установите Node.js 18+"
    exit 1
fi

# Проверяем виртуальное окружение Python
if [ ! -d ".venv" ]; then
    echo "📦 Создание виртуального окружения Python..."
    python3 -m venv .venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source .venv/bin/activate

# Проверяем, что используем Python из venv
PYTHON_PATH=$(which python3)
if [[ "$PYTHON_PATH" != *".venv"* ]]; then
    echo "❌ Виртуальное окружение не активировано корректно"
    echo "Python path: $PYTHON_PATH"
    exit 1
fi

echo "✅ Используется Python из venv: $PYTHON_PATH"

# Устанавливаем зависимости Python
echo "📦 Установка зависимостей Python..."
cd backend
pip install -r requirements.txt


# Запускаем бэкенд
echo "🔧 Запуск бэкенда..."
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Устанавливаем зависимости Node.js
echo "📦 Установка зависимостей Node.js..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# Запускаем фронтенд
echo "🔧 Запуск фронтенда..."
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

cd ..

# Ждем запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Проверяем, что сервисы запустились
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo "❌ Бэкенд не запустился"
    cleanup
    exit 1
fi

if ! curl -s http://localhost:5173 > /dev/null; then
    echo "❌ Фронтенд не запустился"
    cleanup
    exit 1
fi

echo ""
echo "✅ Приложение успешно запущено!"
echo ""
echo "🌐 Веб-интерфейс:     http://localhost:5173"
echo "📚 API документация:  http://localhost:8000/docs"
echo "🔧 API эндпоинт:      http://localhost:8000"
echo ""
echo "Нажмите Ctrl+C для остановки приложения"

# Ждем сигнала завершения
wait

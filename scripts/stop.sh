#!/bin/bash

# Скрипт для остановки приложения Role

echo "🛑 Остановка приложения Role..."

# Останавливаем процессы по портам
echo "🔧 Остановка бэкенда (порт 8000)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Бэкенд уже остановлен"

echo "🔧 Остановка фронтенда (порт 5173)..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "Фронтенд уже остановлен"

echo "🔧 Остановка фронтенда (порт 5174)..."
lsof -ti:5174 | xargs kill -9 2>/dev/null || echo "Фронтенд на порту 5174 уже остановлен"

echo "🔧 Остановка фронтенда (порт 5175)..."
lsof -ti:5175 | xargs kill -9 2>/dev/null || echo "Фронтенд на порту 5175 уже остановлен"

# Останавливаем процессы uvicorn и vite
echo "🔧 Остановка процессов uvicorn..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null || echo "Процессы uvicorn уже остановлены"

echo "🔧 Остановка процессов vite..."
pkill -f "vite.*--host" 2>/dev/null || echo "Процессы vite уже остановлены"

echo "✅ Приложение остановлено!"

#!/bin/bash

# Markdown to JSON Converter Script
# Удобная обертка для запуска TypeScript конвертера

# Проверяем наличие TypeScript
if ! command -v npx &> /dev/null; then
    echo "❌ Ошибка: npx не найден. Установите Node.js и npm"
    exit 1
fi

# Проверяем наличие ts-node
if ! npx ts-node --version &> /dev/null; then
    echo "📦 Устанавливаем ts-node..."
    npm install -g ts-node typescript
fi

# Запускаем конвертер (путь относительно корня проекта)
npx ts-node scripts/md-to-json-converter.ts "$@" 

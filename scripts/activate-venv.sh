#!/bin/bash

# Скрипт для активации виртуального окружения
# Использование: source scripts/activate-venv.sh

# Проверяем, что мы в корне проекта
if [ ! -d ".venv" ]; then
    echo "❌ Виртуальное окружение .venv не найдено!"
    echo "Запустите этот скрипт из корня проекта"
    exit 1
fi

# Активируем виртуальное окружение
echo "🔄 Активирую виртуальное окружение..."
source .venv/bin/activate

# Проверяем активацию
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Виртуальное окружение активировано: $VIRTUAL_ENV"
    echo "🐍 Python: $(which python3)"
    echo "📦 Pip: $(which pip)"
    echo ""
    echo "Для деактивации используйте: deactivate"
else
    echo "❌ Ошибка активации виртуального окружения"
    exit 1
fi

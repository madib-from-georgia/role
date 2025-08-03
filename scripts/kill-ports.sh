#!/bin/bash

echo "Остановка процессов, занимающих порты приложения..."

# Убиваем процессы на портах 8000, 5173 и 3000
for port in 8000 5173 3000; do
    echo "Проверка порта $port..."
    if lsof -ti:$port > /dev/null; then
        echo "Убиваем процессы на порту $port"
        lsof -ti:$port | xargs kill -9
    else
        echo "Порт $port свободен"
    fi
done

echo "Все порты освобождены!"

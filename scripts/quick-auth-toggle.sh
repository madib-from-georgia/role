#!/bin/bash

# Быстрый переключатель авторизации
# Переключает между включенной и отключенной авторизацией

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Пути к файлам
BACKEND_CONFIG="backend/app/config/settings.py"
FRONTEND_CONFIG="frontend/src/config.ts"

# Проверяем текущее состояние
if grep -q "auth_enabled: bool = True" "$BACKEND_CONFIG"; then
    echo -e "${YELLOW}Авторизация включена. Отключаю...${NC}"
    ./scripts/toggle-auth.sh disable
    echo -e "${GREEN}✅ Авторизация отключена!${NC}"
    echo -e "${YELLOW}Перезапустите сервисы:${NC}"
    echo "  Backend:  cd backend && python -m uvicorn app.main:app --reload --port 8000"
    echo "  Frontend: cd frontend && npm run dev"
else
    echo -e "${YELLOW}Авторизация отключена. Включаю...${NC}"
    ./scripts/toggle-auth.sh enable
    echo -e "${GREEN}✅ Авторизация включена!${NC}"
    echo -e "${YELLOW}Перезапустите сервисы:${NC}"
    echo "  Backend:  cd backend && python -m uvicorn app.main:app --reload --port 8000"
    echo "  Frontend: cd frontend && npm run dev"
fi

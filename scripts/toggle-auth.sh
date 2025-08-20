#!/bin/bash

# Скрипт для включения/выключения авторизации в проекте "Роль"
# Автор: AI Assistant
# Версия: 1.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Пути к файлам конфигурации
BACKEND_CONFIG="backend/app/config/settings.py"
FRONTEND_CONFIG="frontend/src/config.ts"

# Функция для вывода цветного текста
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Управление авторизацией${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Функция для проверки существования файлов
check_files() {
    if [[ ! -f "$BACKEND_CONFIG" ]]; then
        print_error "Файл $BACKEND_CONFIG не найден!"
        exit 1
    fi
    
    if [[ ! -f "$FRONTEND_CONFIG" ]]; then
        print_error "Файл $FRONTEND_CONFIG не найден!"
        exit 1
    fi
}

# Функция для показа текущего состояния
show_status() {
    print_header
    
    # Проверяем backend
    if grep -q "auth_enabled: bool = True" "$BACKEND_CONFIG"; then
        BACKEND_STATUS="ВКЛЮЧЕНА"
        BACKEND_COLOR=$GREEN
    else
        BACKEND_STATUS="ОТКЛЮЧЕНА"
        BACKEND_COLOR=$RED
    fi
    
    # Проверяем frontend
    if grep -q "authEnabled: true" "$FRONTEND_CONFIG"; then
        FRONTEND_STATUS="ВКЛЮЧЕНА"
        FRONTEND_COLOR=$GREEN
    else
        FRONTEND_STATUS="ОТКЛЮЧЕНА"
        FRONTEND_COLOR=$RED
    fi
    
    echo -e "Текущее состояние авторизации:"
    echo -e "  Backend:  ${BACKEND_COLOR}$BACKEND_STATUS${NC}"
    echo -e "  Frontend: ${FRONTEND_COLOR}$FRONTEND_STATUS${NC}"
    echo ""
}

# Функция для включения авторизации
enable_auth() {
    print_status "Включаю авторизацию..."
    
    # Backend
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's/auth_enabled: bool = False/auth_enabled: bool = True/' "$BACKEND_CONFIG"
    else
        # Linux
        sed -i 's/auth_enabled: bool = False/auth_enabled: bool = True/' "$BACKEND_CONFIG"
    fi
    
    # Frontend
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's/authEnabled: false/authEnabled: true/' "$FRONTEND_CONFIG"
    else
        # Linux
        sed -i 's/authEnabled: false/authEnabled: true/' "$FRONTEND_CONFIG"
    fi
    
    print_status "Авторизация включена!"
    print_warning "Не забудьте перезапустить backend и frontend!"
}

# Функция для отключения авторизации
disable_auth() {
    print_status "Отключаю авторизацию..."
    
    # Backend
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's/auth_enabled: bool = True/auth_enabled: bool = False/' "$BACKEND_CONFIG"
    else
        # Linux
        sed -i 's/auth_enabled: bool = True/auth_enabled: bool = False/' "$BACKEND_CONFIG"
    fi
    
    # Frontend
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's/authEnabled: true/authEnabled: false/' "$FRONTEND_CONFIG"
    else
        # Linux
        sed -i 's/authEnabled: true/authEnabled: false/' "$FRONTEND_CONFIG"
    fi
    
    print_status "Авторизация отключена!"
    print_warning "Не забудьте перезапустить backend и frontend!"
}

# Функция для перезапуска сервисов
restart_services() {
    print_status "Перезапускаю сервисы..."
    
    # Останавливаем backend если запущен
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        print_status "Останавливаю backend..."
        pkill -f "uvicorn.*main:app" || true
        sleep 2
    fi
    
    # Останавливаем frontend если запущен
    if pgrep -f "vite" > /dev/null; then
        print_status "Останавливаю frontend..."
        pkill -f "vite" || true
        sleep 2
    fi
    
    print_status "Сервисы остановлены. Запустите их заново:"
    echo ""
    echo -e "  ${BLUE}Backend:${NC}"
    echo -e "    cd backend && python -m uvicorn app.main:app --reload --port 8000"
    echo ""
    echo -e "  ${BLUE}Frontend:${NC}"
    echo -e "    cd frontend && npm run dev"
    echo ""
}

# Функция для показа справки
show_help() {
    print_header
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "Команды:"
    echo "  status     - Показать текущее состояние авторизации"
    echo "  enable     - Включить авторизацию"
    echo "  disable    - Отключить авторизацию"
    echo "  restart    - Перезапустить сервисы (остановить backend/frontend)"
    echo "  help       - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 status          # Показать состояние"
    echo "  $0 enable          # Включить авторизацию"
    echo "  $0 disable         # Отключить авторизацию"
    echo "  $0 restart         # Перезапустить сервисы"
    echo ""
    echo "Примечание: После изменения конфигурации необходимо перезапустить сервисы"
}

# Основная логика
main() {
    case "${1:-status}" in
        "status")
            check_files
            show_status
            ;;
        "enable")
            check_files
            enable_auth
            show_status
            ;;
        "disable")
            check_files
            disable_auth
            show_status
            ;;
        "restart")
            restart_services
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Неизвестная команда: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Запуск скрипта
main "$@"

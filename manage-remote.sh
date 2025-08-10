#!/bin/bash

# Скрипт удаленного управления приложением Role на Yandex Cloud
# Запускается с локальной машины, выполняет команды на удаленном сервере

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Конфигурация (ИЗМЕНИТЕ ЭТИ ЗНАЧЕНИЯ)
SERVER_IP="51.250.4.162"                    # IP адрес сервера
SERVER_USER="yc-user"            # Пользователь на сервере
SSH_KEY=""                      # Путь к SSH ключу (опционально)

# Функция показа помощи
show_help() {
    echo -e "${BLUE}Скрипт удаленного управления приложением Role${NC}"
    echo ""
    echo "Использование: $0 --server IP [--key PATH] [--user USER] КОМАНДА"
    echo ""
    echo "Параметры подключения:"
    echo "  --server IP       IP адрес сервера (обязательно)"
    echo "  --user USER       Пользователь на сервере (по умолчанию: yc-user)"
    echo "  --key PATH        Путь к SSH ключу"
    echo ""
    echo "Команды:"
    echo "  status            Показать статус приложения"
    echo "  start             Запустить приложение"
    echo "  stop              Остановить приложение"
    echo "  restart           Перезапустить приложение"
    echo "  logs [LINES]      Показать логи (по умолчанию 50 строк)"
    echo "  logs-live         Показать логи в реальном времени"
    echo "  monitor           Открыть монитор PM2"
    echo "  backup            Создать резервную копию"
    echo "  health            Проверить здоровье приложения"
    echo "  info              Показать информацию о системе"
    echo "  nginx ACTION      Управление Nginx (status|restart|reload)"
    echo "  cleanup           Очистить логи и временные файлы"
    echo "  shell             Открыть SSH сессию"
    echo ""
    echo "Примеры:"
    echo "  $0 --server 1.2.3.4 status"
    echo "  $0 --server 1.2.3.4 --key ~/.ssh/id_rsa logs 100"
    echo "  $0 --server 1.2.3.4 nginx restart"
}

# Обработка параметров командной строки
COMMAND=""
COMMAND_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --server)
            SERVER_IP="$2"
            shift 2
            ;;
        --user)
            SERVER_USER="$2"
            shift 2
            ;;
        --key)
            SSH_KEY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [ -z "$COMMAND" ]; then
                COMMAND="$1"
            else
                COMMAND_ARGS="$COMMAND_ARGS $1"
            fi
            shift
            ;;
    esac
done

# Проверка обязательных параметров
if [ -z "$SERVER_IP" ]; then
    error "Не указан IP адрес сервера. Используйте --server IP"
fi

if [ -z "$COMMAND" ]; then
    show_help
    exit 1
fi

# Формирование SSH команды
SSH_CMD="ssh"
if [ ! -z "$SSH_KEY" ]; then
    if [ ! -f "$SSH_KEY" ]; then
        error "SSH ключ не найден: $SSH_KEY"
    fi
    SSH_CMD="ssh -i $SSH_KEY"
fi

SSH_TARGET="$SERVER_USER@$SERVER_IP"

# Проверка подключения к серверу
check_connection() {
    if ! $SSH_CMD -o ConnectTimeout=10 $SSH_TARGET "echo 'OK'" >/dev/null 2>&1; then
        error "Не удается подключиться к серверу $SSH_TARGET"
    fi
}

# Выполнение команд на сервере
case $COMMAND in
    status)
        log "📊 Получение статуса приложения с сервера $SERVER_IP..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
echo -e "\033[0;34m📊 Статус приложения Role\033[0m"
echo ""

# PM2 статус
echo -e "\033[1;33m🔧 PM2 Процессы:\033[0m"
if command -v pm2 &> /dev/null; then
    pm2 list
else
    echo "PM2 не установлен"
fi
echo ""

# Nginx статус
echo -e "\033[1;33m🌐 Nginx:\033[0m"
if sudo systemctl is-active --quiet nginx; then
    echo -e "\033[0;32m✅ Nginx запущен\033[0m"
else
    echo -e "\033[0;31m❌ Nginx остановлен\033[0m"
fi

# Проверка портов
echo -e "\033[1;33m🔌 Порты:\033[0m"
if ss -tlnp 2>/dev/null | grep -q ":8000"; then
    echo -e "\033[0;32m✅ Backend (8000) активен\033[0m"
else
    echo -e "\033[0;31m❌ Backend (8000) неактивен\033[0m"
fi

if ss -tlnp 2>/dev/null | grep -q ":80"; then
    echo -e "\033[0;32m✅ Nginx (80) активен\033[0m"
else
    echo -e "\033[0;31m❌ Nginx (80) неактивен\033[0m"
fi

# Использование диска
echo ""
echo -e "\033[1;33m💾 Использование диска:\033[0m"
df -h / | tail -1 | awk '{print "Использовано: " $3 " из " $2 " (" $5 ")"}'

# Использование памяти
echo -e "\033[1;33m🧠 Использование памяти:\033[0m"
free -h | grep "Mem:" | awk '{print "Использовано: " $3 " из " $2}'
EOF
        ;;
        
    start)
        log "🚀 Запуск приложения на сервере $SERVER_IP..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
if pm2 list | grep -q "role-backend.*online"; then
    echo -e "\033[1;33mПриложение уже запущено\033[0m"
    exit 0
fi

cd /home/yc-user/role
pm2 start ecosystem.config.js

if ! sudo systemctl is-active --quiet nginx; then
    sudo systemctl start nginx
fi

echo -e "\033[0;32m✅ Приложение запущено\033[0m"
EOF
        ;;
        
    stop)
        log "🛑 Остановка приложения на сервере $SERVER_IP..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
pm2 stop role-backend || echo "Не удалось остановить через PM2"
echo -e "\033[0;32m✅ Приложение остановлено\033[0m"
EOF
        ;;
        
    restart)
        log "🔄 Перезапуск приложения на сервере $SERVER_IP..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
pm2 restart role-backend || exit 1
sudo systemctl reload nginx
echo -e "\033[0;32m✅ Приложение перезапущено\033[0m"
EOF
        ;;
        
    logs)
        LINES=${COMMAND_ARGS:-50}
        log "📋 Получение логов приложения ($LINES строк)..."
        check_connection
        $SSH_CMD $SSH_TARGET "pm2 logs role-backend --lines $LINES"
        ;;
        
    logs-live)
        log "📋 Подключение к логам в реальном времени..."
        log "Нажмите Ctrl+C для выхода"
        check_connection
        $SSH_CMD $SSH_TARGET "pm2 logs role-backend"
        ;;
        
    monitor)
        log "📊 Открытие монитора PM2..."
        log "Нажмите 'q' для выхода из монитора"
        check_connection
        $SSH_CMD -t $SSH_TARGET "pm2 monit"
        ;;
        
    backup)
        log "💾 Создание резервной копии на сервере $SERVER_IP..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
if [ -f "/opt/backup-role.sh" ]; then
    /opt/backup-role.sh
    echo -e "\033[0;32m✅ Резервная копия создана\033[0m"
else
    echo -e "\033[0;31m❌ Скрипт резервного копирования не найден\033[0m"
    exit 1
fi
EOF
        ;;
        
    health)
        log "🏥 Проверка здоровья приложения на сервере $SERVER_IP..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
echo -e "\033[0;34m🏥 Проверка здоровья приложения\033[0m"
echo ""

# Проверка PM2
if pm2 list | grep -q "role-backend.*online"; then
    echo -e "\033[0;32m✅ PM2: Приложение запущено\033[0m"
else
    echo -e "\033[0;31m❌ PM2: Приложение не запущено\033[0m"
    exit 1
fi

# Проверка API
if curl -s http://localhost:8000/docs > /dev/null; then
    echo -e "\033[0;32m✅ API: Доступно\033[0m"
else
    echo -e "\033[0;31m❌ API: Недоступно\033[0m"
    exit 1
fi

# Проверка веб-интерфейса через Nginx
if curl -s http://localhost/ > /dev/null; then
    echo -e "\033[0;32m✅ Web: Доступно\033[0m"
else
    echo -e "\033[0;31m❌ Web: Недоступно\033[0m"
    exit 1
fi

# Проверка базы данных
if [ -f "/home/yc-user/role/backend/database.db" ]; then
    echo -e "\033[0;32m✅ Database: Файл существует\033[0m"
else
    echo -e "\033[0;31m❌ Database: Файл не найден\033[0m"
    exit 1
fi

echo ""
echo -e "\033[0;32m🎉 Все сервисы работают нормально!\033[0m"
EOF
        ;;
        
    info)
        log "ℹ️  Получение информации о системе..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
echo -e "\033[0;34mℹ️  Информация о системе\033[0m"
echo ""

# Версия ОС
echo -e "\033[1;33m🖥️  Операционная система:\033[0m"
lsb_release -d | cut -f2

# Версии ПО
echo -e "\033[1;33m🐍 Python:\033[0m"
python3 --version 2>/dev/null || echo "Не установлен"

echo -e "\033[1;33m📦 Node.js:\033[0m"
node --version 2>/dev/null || echo "Не установлен"

echo -e "\033[1;33m🔧 PM2:\033[0m"
pm2 --version 2>/dev/null || echo "Не установлен"

echo -e "\033[1;33m🌐 Nginx:\033[0m"
nginx -v 2>&1 | cut -d' ' -f3 || echo "Не установлен"

# Информация о приложении
if [ -d "/home/yc-user/role" ]; then
    echo ""
    echo -e "\033[1;33m📁 Приложение:\033[0m"
    echo "Директория: /home/yc-user/role"
    
    cd /home/yc-user/role
    if [ -d ".git" ]; then
        echo "Текущий коммит: $(git rev-parse --short HEAD)"
        echo "Ветка: $(git branch --show-current)"
        echo "Последний коммит: $(git log --format='%s' -n 1)"
    fi
fi

# Uptime
echo ""
echo -e "\033[1;33m⏰ Uptime системы:\033[0m"
uptime -p
EOF
        ;;
        
    nginx)
        ACTION=${COMMAND_ARGS// /}
        case $ACTION in
            status)
                log "🌐 Получение статуса Nginx..."
                check_connection
                $SSH_CMD $SSH_TARGET "sudo systemctl status nginx --no-pager"
                ;;
            restart)
                log "🔄 Перезапуск Nginx..."
                check_connection
                $SSH_CMD $SSH_TARGET "sudo nginx -t && sudo systemctl restart nginx && echo '✅ Nginx перезапущен'"
                ;;
            reload)
                log "🔄 Перезагрузка конфигурации Nginx..."
                check_connection
                $SSH_CMD $SSH_TARGET "sudo nginx -t && sudo systemctl reload nginx && echo '✅ Конфигурация Nginx перезагружена'"
                ;;
            *)
                error "Неизвестное действие для nginx: $ACTION. Используйте: status, restart, reload"
                ;;
        esac
        ;;
        
    cleanup)
        log "🧹 Очистка логов и временных файлов..."
        check_connection
        $SSH_CMD $SSH_TARGET << 'EOF'
# Очистка логов PM2
pm2 flush

# Очистка системных логов (старше 7 дней)
sudo journalctl --vacuum-time=7d

# Очистка старых резервных копий (старше 30 дней)
if [ -d "/opt/backups" ]; then
    find /opt/backups -name "*.db" -mtime +30 -delete
    find /opt/backups -name "*.tar.gz" -mtime +30 -delete
fi

echo -e "\033[0;32m✅ Очистка завершена\033[0m"
EOF
        ;;
        
    shell)
        log "🐚 Открытие SSH сессии на сервере $SERVER_IP..."
        check_connection
        $SSH_CMD -t $SSH_TARGET
        ;;
        
    *)
        error "Неизвестная команда: $COMMAND. Используйте '$0 --help' для справки."
        ;;
esac

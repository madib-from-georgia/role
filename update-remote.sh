#!/bin/bash

# Скрипт удаленного обновления приложения Role на Yandex Cloud
# Запускается с локальной машины, выполняет обновление на удаленном сервере

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Конфигурация (ИЗМЕНИТЕ ЭТИ ЗНАЧЕНИЯ)
SERVER_IP="51.250.4.162"                    # IP адрес сервера
SERVER_USER="yc-user"            # Пользователь на сервере
SSH_KEY=""                      # Путь к SSH ключу (опционально)
BRANCH="main"                   # Ветка для обновления
SKIP_BACKUP=false               # Пропустить резервную копию
FORCE_UPDATE=false              # Принудительное обновление

# Параметры командной строки
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
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        -h|--help)
            echo "Использование: $0 [опции]"
            echo "Опции:"
            echo "  --server IP       IP адрес сервера"
            echo "  --user USER       Пользователь на сервере (по умолчанию: yc-user)"
            echo "  --key PATH        Путь к SSH ключу"
            echo "  --branch BRANCH   Ветка для обновления (по умолчанию: main)"
            echo "  --skip-backup     Пропустить создание резервной копии"
            echo "  --force           Принудительное обновление (игнорировать изменения)"
            echo "  -h, --help        Показать эту справку"
            echo ""
            echo "Пример:"
            echo "  $0 --server 1.2.3.4"
            echo "  $0 --server 1.2.3.4 --branch develop --force"
            exit 0
            ;;
        *)
            error "Неизвестный параметр: $1"
            ;;
    esac
done

# Проверка обязательных параметров
if [ -z "$SERVER_IP" ]; then
    error "Не указан IP адрес сервера. Используйте --server IP"
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

log "🔄 Начинаем удаленное обновление приложения Role"
log "📡 Сервер: $SSH_TARGET"
log "🌿 Ветка: $BRANCH"

if [ "$SKIP_BACKUP" = true ]; then
    warn "Резервная копия будет пропущена"
fi

if [ "$FORCE_UPDATE" = true ]; then
    warn "Принудительное обновление: локальные изменения будут перезаписаны"
fi

# Проверка подключения к серверу
log "🔍 Проверка подключения к серверу..."
if ! $SSH_CMD -o ConnectTimeout=10 $SSH_TARGET "echo 'Подключение успешно'" 2>/dev/null; then
    error "Не удается подключиться к серверу $SSH_TARGET"
fi

log "✅ Подключение к серверу установлено"

# Создание скрипта обновления на сервере
log "📝 Создание скрипта обновления на сервере..."

UPDATE_SCRIPT=$(cat << 'EOF'
#!/bin/bash

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Параметры передаются как аргументы
BRANCH="$1"
SKIP_BACKUP="$2"
FORCE_UPDATE="$3"
APP_DIR="/home/yc-user/role"
BACKUP_DIR="/home/yc-user/backups"

log "🔄 Начинаем обновление на сервере"

# Проверка существования директории приложения
if [ ! -d "$APP_DIR" ]; then
    error "Директория приложения $APP_DIR не найдена"
fi

# Проверка PM2
if ! command -v pm2 &> /dev/null; then
    error "PM2 не найден"
fi

cd $APP_DIR

# Проверка Git репозитория
if [ ! -d ".git" ]; then
    error "Директория не является Git репозиторием"
fi

# Создание резервной копии (если не пропущено)
if [ "$SKIP_BACKUP" != "true" ]; then
    log "💾 Создание резервной копии..."
    
    BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
    mkdir -p $BACKUP_DIR
    
    # Резервная копия базы данных
    if [ -f "backend/database.db" ]; then
        cp backend/database.db $BACKUP_DIR/database_pre_update_$BACKUP_DATE.db
        log "✅ Резервная копия базы данных создана"
    fi
    
    # Резервная копия загруженных файлов
    if [ -d "backend/uploads" ]; then
        tar -czf $BACKUP_DIR/uploads_pre_update_$BACKUP_DATE.tar.gz -C backend uploads/
        log "✅ Резервная копия файлов создана"
    fi
    
    # Резервная копия конфигурации
    if [ -f "backend/.env" ]; then
        cp backend/.env $BACKUP_DIR/env_pre_update_$BACKUP_DATE
        log "✅ Резервная копия конфигурации создана"
    fi
else
    warn "Создание резервной копии пропущено"
fi

# Остановка приложения
log "🛑 Остановка приложения..."
pm2 stop role-backend || warn "Не удалось остановить приложение через PM2"

# Сохранение текущих изменений (если есть)
if [ "$FORCE_UPDATE" != "true" ]; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
        warn "Обнаружены локальные изменения в репозитории"
        git status --porcelain
        
        log "📦 Сохранение локальных изменений в stash..."
        git stash push -m "Auto-stash before update $(date)"
    fi
else
    warn "Принудительное обновление: локальные изменения будут перезаписаны"
    git reset --hard HEAD
    git clean -fd
fi

# Получение обновлений из репозитория
log "📥 Получение обновлений из репозитория..."
git fetch origin

# Проверка, есть ли обновления
CURRENT_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$BRANCH)

if [ "$CURRENT_COMMIT" = "$REMOTE_COMMIT" ]; then
    log "✅ Приложение уже обновлено до последней версии"
    pm2 start role-backend
    exit 0
fi

log "🔄 Обновление до ветки $BRANCH..."
git checkout $BRANCH
git pull origin $BRANCH

# Активация виртуального окружения
log "🐍 Активация виртуального окружения..."
source .venv/bin/activate

# Обновление зависимостей Python
log "📦 Обновление зависимостей Python..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Выполнение миграций базы данных (если есть)
if [ -f "alembic.ini" ]; then
    log "🗄️ Выполнение миграций базы данных..."
    # Установка PYTHONPATH для корректной работы Alembic
    # Используем абсолютный путь к backend директории
    export PYTHONPATH="$APP_DIR/backend:$PYTHONPATH"
    if python -m alembic upgrade head 2>/dev/null; then
        log "✅ Миграции выполнены успешно"
    else
        warn "⚠️ Миграции пропущены (возможны проблемы с PYTHONPATH)"
    fi
else
    warn "⚠️ Файл alembic.ini не найден, миграции пропущены"
fi

cd ..

# Проверка изменений в package.json фронтенда
FRONTEND_UPDATED=false
if git diff --name-only $CURRENT_COMMIT $REMOTE_COMMIT | grep -q "frontend/package.json"; then
    FRONTEND_UPDATED=true
    log "📦 Обнаружены изменения в зависимостях фронтенда"
fi

# Обновление и сборка фронтенда
log "🔨 Сборка фронтенда..."
cd frontend

if [ "$FRONTEND_UPDATED" = true ]; then
    log "📦 Обновление зависимостей Node.js..."
    npm install
fi

npm run build
cd ..

# Проверка изменений в конфигурации PM2
if [ -f "ecosystem.config.js" ]; then
    if git diff --name-only $CURRENT_COMMIT $REMOTE_COMMIT | grep -q "ecosystem.config.js"; then
        log "⚙️ Обнаружены изменения в конфигурации PM2"
        pm2 delete role-backend || true
        pm2 start ecosystem.config.js
    fi
fi

# Запуск приложения
log "🚀 Запуск приложения..."
pm2 start role-backend

# Ожидание запуска
log "⏳ Ожидание запуска приложения..."
sleep 10

# Проверка работы приложения
log "🔍 Проверка работы приложения..."

# Проверка PM2
if ! pm2 list | grep -q "role-backend.*online"; then
    error "Приложение не запустилось"
fi

# Проверка доступности API
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/docs > /dev/null; then
        log "✅ API доступно"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            warn "API недоступно, попытка $RETRY_COUNT/$MAX_RETRIES. Ожидание..."
            sleep 5
        else
            error "API недоступно после $MAX_RETRIES попыток"
        fi
    fi
done

# Перезагрузка Nginx
log "🔄 Перезагрузка Nginx..."
sudo nginx -t && sudo systemctl reload nginx

# Очистка старых логов PM2
log "🧹 Очистка старых логов..."
pm2 flush

# Информация об обновлении
NEW_COMMIT=$(git rev-parse HEAD)
COMMIT_MESSAGE=$(git log --format="%s" -n 1 $NEW_COMMIT)

log "✅ Обновление завершено успешно!"
echo ""
echo "📊 Информация об обновлении:"
echo "  Предыдущий коммит: ${CURRENT_COMMIT:0:8}"
echo "  Новый коммит:      ${NEW_COMMIT:0:8}"
echo "  Сообщение коммита: $COMMIT_MESSAGE"
echo ""

# Показать последние логи
echo "📋 Последние логи приложения:"
pm2 logs role-backend --lines 10 --nostream
EOF
)

# Отправка и выполнение скрипта на сервере
log "📤 Отправка скрипта на сервер и выполнение..."
echo "$UPDATE_SCRIPT" | $SSH_CMD $SSH_TARGET "cat > /tmp/update-script.sh && chmod +x /tmp/update-script.sh && /tmp/update-script.sh '$BRANCH' '$SKIP_BACKUP' '$FORCE_UPDATE'"

# Проверка результата
if [ $? -eq 0 ]; then
    log "✅ Удаленное обновление завершено успешно!"
    echo ""
    echo -e "${BLUE}🌐 Приложение обновлено и доступно${NC}"
    echo ""
    echo -e "${YELLOW}📋 Для проверки статуса на сервере:${NC}"
    echo -e "${YELLOW}  $SSH_CMD $SSH_TARGET${NC}"
    echo -e "${YELLOW}  pm2 status${NC}"
    echo -e "${YELLOW}  pm2 logs role-backend${NC}"
else
    error "Обновление завершилось с ошибкой"
fi

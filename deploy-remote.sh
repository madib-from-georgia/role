#!/bin/bash

# Скрипт удаленного развертывания приложения Role на Yandex Cloud
# Запускается с локальной машины, выполняет развертывание на удаленном сервере

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
REPO_URL="https://github.com/madib-from-georgia/role.git"                     # URL Git репозитория
DOMAIN=""                       # Домен или IP для Nginx
BRANCH="main"                   # Ветка для развертывания

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
        --repo)
            REPO_URL="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Использование: $0 [опции]"
            echo "Опции:"
            echo "  --server IP     IP адрес сервера"
            echo "  --user USER     Пользователь на сервере (по умолчанию: yc-user)"
            echo "  --key PATH      Путь к SSH ключу"
            echo "  --repo URL      URL Git репозитория"
            echo "  --domain DOMAIN Домен или IP для Nginx"
            echo "  --branch BRANCH Ветка для развертывания (по умолчанию: main)"
            echo "  -h, --help      Показать эту справку"
            echo ""
            echo "Пример:"
            echo "  $0 --server 1.2.3.4 --repo https://github.com/user/role.git --domain example.com"
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

if [ -z "$REPO_URL" ]; then
    error "Не указан URL репозитория. Используйте --repo URL"
fi

if [ -z "$DOMAIN" ]; then
    DOMAIN="$SERVER_IP"
    warn "Домен не указан, используется IP сервера: $DOMAIN"
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

log "🚀 Начинаем удаленное развертывание приложения Role"
log "📡 Сервер: $SSH_TARGET"
log "🌐 Домен: $DOMAIN"
log "📦 Репозиторий: $REPO_URL"
log "🌿 Ветка: $BRANCH"

# Проверка подключения к серверу
log "🔍 Проверка подключения к серверу..."
if ! $SSH_CMD -o ConnectTimeout=10 $SSH_TARGET "echo 'Подключение успешно'" 2>/dev/null; then
    error "Не удается подключиться к серверу $SSH_TARGET"
fi

log "✅ Подключение к серверу установлено"

# Создание скрипта развертывания на сервере
log "📝 Создание скрипта развертывания на сервере..."

DEPLOY_SCRIPT=$(cat << 'EOF'
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

# Параметры передаются как переменные окружения
REPO_URL="$1"
DOMAIN="$2"
BRANCH="$3"
APP_DIR="/home/yc-user/role"
PYTHON_VERSION="3.11"

log "🚀 Начинаем развертывание на сервере"

# Обновление системы
log "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11
log "🐍 Установка Python ${PYTHON_VERSION}..."
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev python3-pip

# Установка Node.js 18
log "📦 Установка Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Установка дополнительных пакетов
log "🔧 Установка дополнительных пакетов..."
sudo apt install -y git nginx certbot python3-certbot-nginx curl build-essential htop

# Установка системных пакетов для WeasyPrint
log "📄 Установка системных пакетов для WeasyPrint..."
sudo apt install -y python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Установка PM2
log "🌐 Установка PM2..."
if ! sudo npm install -g pm2; then
    error "Не удалось установить PM2"
fi

# Проверка установки PM2
if ! command -v pm2 &> /dev/null; then
    error "PM2 не установлен"
fi

# Клонирование репозитория
log "📁 Клонирование репозитория..."
if [ -d "$APP_DIR" ]; then
    warn "Директория $APP_DIR уже существует. Удаляем..."
    rm -rf $APP_DIR
fi

git clone $REPO_URL $APP_DIR

# Переход в директорию проекта
cd $APP_DIR
git checkout $BRANCH

# Создание виртуального окружения Python
log "🐍 Настройка Python окружения..."
python${PYTHON_VERSION} -m venv .venv
source .venv/bin/activate

# Установка зависимостей Python
log "📦 Установка зависимостей Python..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Настройка конфигурации
log "⚙️ Настройка конфигурации..."
if [ ! -f .env ]; then
    cp .env.example .env
    sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env
fi

# Создание директорий
mkdir -p uploads cache

# Инициализация базы данных
log "🗄️ Инициализация базы данных..."
cd $APP_DIR

# Создаем пустую базу данных SQLite
log "📝 Создание пустой базы данных SQLite..."
cd backend
touch database.db
log "✅ Файл базы данных создан"

# Выполнение миграций Alembic
log "🔄 Выполнение миграций базы данных..."
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
source $APP_DIR/.venv/bin/activate

# Проверяем наличие миграций
if [ -d "$APP_DIR/backend/alembic/versions" ] && [ "$(ls -A $APP_DIR/backend/alembic/versions)" ]; then
    log "📋 Найдены миграции Alembic, выполняем..."
    cd $APP_DIR/backend
    if alembic upgrade head; then
        log "✅ Миграции базы данных выполнены успешно"
    else
        error "❌ Ошибка выполнения миграций Alembic"
    fi
else
    warn "⚠️ Миграции Alembic не найдены, пропускаем"
fi

# Создание тестового пользователя
log "👤 Создание тестового пользователя..."
cd $APP_DIR/backend
if python scripts/create_mock_user.py; then
    log "✅ Тестовый пользователь создан успешно (dev_user/dev_password_123, email: dev@example.com)"
else
    warn "⚠️ Не удалось создать тестового пользователя - можно будет создать через API"
fi

# Импорт чеклистов
log "📋 Импорт чеклистов..."
cd $APP_DIR/backend
if python scripts/import_checklists.py; then
    log "✅ Чеклисты успешно импортированы"
else
    warn "⚠️ Не удалось импортировать чеклисты - можно будет импортировать вручную"
fi

cd $APP_DIR

# Установка зависимостей Node.js и сборка фронтенда
log "📦 Установка зависимостей Node.js и сборка фронтенда..."
cd frontend
npm install
npm run build
cd ..

# Проверка наличия сборки фронтенда
if [ ! -d "frontend/dist" ]; then
    error "Директория сборки фронтенда не найдена"
fi

if [ ! -f "frontend/dist/index.html" ]; then
    error "Файл index.html не найден в сборке фронтенда"
fi

# Исправление прав доступа к файлам фронтенда и директориям
log "🔧 Настройка прав доступа к файлам фронтенда..."
sudo chmod 755 /home/yc-user /home/yc-user/role /home/yc-user/role/frontend
sudo chown -R yc-user:www-data frontend/dist
sudo chmod -R 755 frontend/dist

# Создание конфигурации PM2
log "🔧 Создание конфигурации PM2..."
cat > ecosystem.config.js << EOFPM2
module.exports = {
  apps: [
    {
      name: 'role-backend',
      cwd: '$APP_DIR/backend',
      script: '$APP_DIR/.venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      env: {
        ENVIRONMENT: 'production',
        PYTHONPATH: '$APP_DIR'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '/var/log/pm2/role-backend-error.log',
      out_file: '/var/log/pm2/role-backend-out.log',
      log_file: '/var/log/pm2/role-backend.log'
    }
  ]
};
EOFPM2

# Создание директории для логов PM2
sudo mkdir -p /var/log/pm2
sudo chown yc-user:yc-user /var/log/pm2

# Запуск приложения через PM2
log "🚀 Запуск приложения..."
if ! pm2 start ecosystem.config.js; then
    error "Не удалось запустить приложение через PM2"
fi

if ! pm2 save; then
    error "Не удалось сохранить конфигурацию PM2"
fi

# Настройка автозапуска PM2 (без интерактивного режима)
log "🔧 Настройка автозапуска PM2..."
set +e  # Отключаем режим завершения при ошибках
PM2_STARTUP_CMD=$(pm2 startup systemd -u yc-user --hp /home/yc-user --no-daemon 2>/dev/null)
if [ -n "$PM2_STARTUP_CMD" ] && [[ "$PM2_STARTUP_CMD" == *"sudo"* ]]; then
    log "Выполнение команды автозапуска PM2..."
    # Выполняем команду от root без интерактивного режима
    echo "$PM2_STARTUP_CMD" | sudo bash
    if [ $? -ne 0 ]; then
        warn "Не удалось настроить автозапуск PM2"
    fi
else
    warn "Команда автозапуска PM2 не получена или не содержит sudo"
fi
set -e  # Включаем режим завершения при ошибках обратно

# Проверка статуса приложения
log "🔍 Проверка статуса приложения..."
if ! pm2 list | grep -q "role-backend.*online"; then
    warn "Приложение не запущено"
fi

# Настройка Nginx
log "🌐 Настройка Nginx..."
# Копирование шаблона конфигурации Nginx
cp nginx.conf.template /tmp/nginx-role-app.conf

# Замена переменных в конфигурации
sed -i "s|{{DOMAIN}}|$DOMAIN|g" /tmp/nginx-role-app.conf
sed -i "s|{{APP_DIR}}|$APP_DIR|g" /tmp/nginx-role-app.conf

# Проверка наличия директории sites-available
if [ ! -d "/etc/nginx/sites-available" ]; then
    error "Директория /etc/nginx/sites-available не найдена"
fi

# Копирование конфигурации Nginx с проверкой ошибок
if ! sudo cp /tmp/nginx-role-app.conf /etc/nginx/sites-available/role-app; then
    error "Не удалось скопировать конфигурацию Nginx"
fi

# Активация конфигурации Nginx
if ! sudo ln -sf /etc/nginx/sites-available/role-app /etc/nginx/sites-enabled/; then
    error "Не удалось активировать конфигурацию Nginx"
fi

if ! sudo rm -f /etc/nginx/sites-enabled/default; then
    warn "Не удалось удалить стандартную конфигурацию Nginx"
fi

# Проверка конфигурации Nginx и перезапуск
if sudo nginx -t; then
    log "✅ Конфигурация Nginx проверена успешно"
    if ! sudo systemctl restart nginx; then
        error "Не удалось перезапустить Nginx"
    fi
    log "✅ Nginx перезапущен успешно"
else
    error "Ошибка в конфигурации Nginx"
fi

# Настройка файрвола
log "🔥 Настройка файрвола..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Создание скрипта резервного копирования
log "💾 Создание скрипта резервного копирования..."
sudo tee /opt/backup-role.sh > /dev/null << 'EOFBACKUP'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

if [ -f "/home/yc-user/role/backend/database.db" ]; then
    cp /home/yc-user/role/backend/database.db $BACKUP_DIR/database_$DATE.db
fi

if [ -d "/home/yc-user/role/backend/uploads" ]; then
    tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /home/yc-user/role/backend uploads/
fi

find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOFBACKUP

sudo chmod +x /opt/backup-role.sh

# Настройка cron для резервного копирования
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-role.sh >> /var/log/backup.log 2>&1") | crontab -

# Ожидание запуска сервисов
log "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка работы
log "🔍 Проверка работы сервисов..."
if ! pm2 list | grep -q "role-backend.*online"; then
    error "Backend не запустился"
fi

if ! curl -s http://localhost:8000/docs > /dev/null; then
    warn "API может быть недоступно"
fi

log "✅ Развертывание завершено успешно!"
echo ""
echo "🌐 Веб-интерфейс:     http://$DOMAIN/"
echo "📚 API документация:  http://$DOMAIN/docs"
echo "🔧 API эндпоинт:      http://$DOMAIN/api/"
EOF
)

# Отправка и выполнение скрипта на сервере
log "📤 Отправка скрипта на сервер и выполнение..."
echo "$DEPLOY_SCRIPT" | $SSH_CMD $SSH_TARGET "cat > /tmp/deploy-script.sh && chmod +x /tmp/deploy-script.sh && /tmp/deploy-script.sh '$REPO_URL' '$DOMAIN' '$BRANCH'"

# Проверка результата
if [ $? -eq 0 ]; then
    log "✅ Удаленное развертывание завершено успешно!"
    echo ""
    echo -e "${BLUE}🌐 Приложение доступно по адресу: http://$DOMAIN${NC}"
    echo -e "${BLUE}📚 API документация: http://$DOMAIN/docs${NC}"
    echo ""
    echo -e "${YELLOW}📋 Для управления приложением на сервере:${NC}"
    echo -e "${YELLOW}  $SSH_CMD $SSH_TARGET${NC}"
    echo -e "${YELLOW}  pm2 status${NC}"
    echo -e "${YELLOW}  pm2 logs role-backend${NC}"
    echo ""

    # Предложение настройки SSL
    if [[ "$DOMAIN" != "$SERVER_IP" ]]; then
        echo -e "${YELLOW}💡 Для настройки SSL сертификата выполните на сервере:${NC}"
        echo -e "${YELLOW}   sudo certbot --nginx -d $DOMAIN${NC}"
    fi
else
    error "Развертывание завершилось с ошибкой"
fi

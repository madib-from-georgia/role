# Инструкция по развертыванию приложения Role на Yandex Cloud

## Обзор приложения

**Role** - это веб-приложение для анализа персонажей художественных произведений, состоящее из:
- **Backend**: FastAPI приложение на Python 3.9+
- **Frontend**: React приложение на Vite
- **База данных**: SQLite (можно заменить на PostgreSQL для продакшена)

## Требования к виртуальной машине

### Минимальные характеристики:
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Диск**: 20 GB SSD
- **ОС**: Ubuntu 22.04 LTS

### Рекомендуемые характеристики:
- **CPU**: 4 vCPU
- **RAM**: 8 GB
- **Диск**: 40 GB SSD
- **ОС**: Ubuntu 22.04 LTS

## Шаг 1: Создание виртуальной машины в Yandex Cloud

1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Выберите каталог или создайте новый
3. Перейдите в раздел "Compute Cloud" → "Виртуальные машины"
4. Нажмите "Создать ВМ"

### Настройки ВМ:
- **Имя**: `role-app-server`
- **Зона доступности**: `ru-central1-a`
- **Платформа**: Intel Ice Lake
- **Конфигурация**: 2-4 vCPU, 4-8 GB RAM
- **Образ**: Ubuntu 22.04 LTS
- **Диск**: 20-40 GB SSD
- **Сеть**: default-net
- **Публичный IP**: Да
- **SSH-ключ**: Добавьте свой публичный SSH-ключ

## Шаг 2: Подключение к серверу

```bash
ssh yc-user@<PUBLIC_IP_ADDRESS>
```

## Шаг 3: Установка необходимого ПО

### Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### Установка Python 3.11
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### Установка Node.js 18+
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Установка дополнительных пакетов
```bash
sudo apt install -y git nginx certbot python3-certbot-nginx curl build-essential
```

### Установка PM2 для управления процессами
```bash
sudo npm install -g pm2
```

## Шаг 4: Клонирование и настройка проекта

### Клонирование репозитория
```bash
cd /opt
sudo git clone <YOUR_REPOSITORY_URL> role
sudo chown -R yc-user:yc-user /home/yc-user/role
cd /home/yc-user/role
```

### Создание виртуального окружения Python
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Установка зависимостей Python
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Установка зависимостей Node.js
```bash
cd frontend
npm install
npm run build
cd ..
```

## Шаг 5: Настройка окружения

### Создание файла конфигурации backend
```bash
cd backend
cp .env.example .env
```

Отредактируйте файл `.env`:
```bash
nano .env
```

Содержимое файла `.env`:
```env
# Application Configuration
PORT=8000
ENVIRONMENT=production
DATABASE_URL=sqlite:///./database.db
UPLOAD_DIR=./uploads
CACHE_DIR=./cache

# Для продакшена рекомендуется использовать PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost/role_db
```

### Инициализация базы данных
```bash
# Если используете Alembic для миграций
python -m alembic upgrade head

# Или создайте тестового пользователя
python scripts/create_test_user.py
```

## Шаг 6: Настройка PM2 для автозапуска

### Создание конфигурации PM2
```bash
cd /home/yc-user/role
nano ecosystem.config.js
```

Содержимое файла `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'role-backend',
      cwd: '/home/yc-user/role/backend',
      script: '/home/yc-user/role/.venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      env: {
        ENVIRONMENT: 'production'
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
```

### Создание директории для логов
```bash
sudo mkdir -p /var/log/pm2
sudo chown yc-user:yc-user /var/log/pm2
```

### Запуск приложения через PM2
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

Выполните команду, которую выведет `pm2 startup`.

## Шаг 7: Настройка Nginx

### Создание конфигурации Nginx
```bash
sudo nano /etc/nginx/sites-available/role
```

Содержимое файла:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Замените на ваш домен или IP

    # Статические файлы фронтенда
    location / {
        root /home/yc-user/role/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Кэширование статических файлов
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API бэкенда
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличиваем таймауты для загрузки файлов
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Увеличиваем максимальный размер загружаемых файлов
        client_max_body_size 100M;
    }

    # Документация API
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # OpenAPI схема
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Активация конфигурации
```bash
sudo ln -s /etc/nginx/sites-available/role /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Шаг 8: Настройка SSL (опционально)

Если у вас есть домен:

```bash
sudo certbot --nginx -d your-domain.com
```

## Шаг 9: Настройка файрвола

```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## Шаг 10: Проверка работы

### Проверка статуса сервисов
```bash
# Проверка PM2
pm2 status

# Проверка Nginx
sudo systemctl status nginx

# Проверка логов
pm2 logs role-backend
```

### Тестирование приложения
- Веб-интерфейс: `http://your-server-ip/`
- API документация: `http://your-server-ip/docs`

## Управление приложением

### Основные команды PM2
```bash
# Перезапуск приложения
pm2 restart role-backend

# Остановка приложения
pm2 stop role-backend

# Просмотр логов
pm2 logs role-backend

# Мониторинг
pm2 monit
```

### Обновление приложения
```bash
cd /home/yc-user/role
git pull origin main

# Обновление backend
source .venv/bin/activate
cd backend
pip install -r requirements.txt
cd ..

# Обновление frontend
cd frontend
npm install
npm run build
cd ..

# Перезапуск приложения
pm2 restart role-backend
```

## Мониторинг и логи

### Настройка ротации логов
```bash
sudo nano /etc/logrotate.d/role
```

Содержимое:
```
/var/log/pm2/*.log {
    daily
    missingok
    rotate 14
    compress
    notifempty
    create 0640 yc-user yc-user
    postrotate
        pm2 reloadLogs
    endscript
}
```

### Мониторинг ресурсов
```bash
# Использование диска
df -h

# Использование памяти
free -h

# Процессы
htop

# PM2 мониторинг
pm2 monit
```

## Резервное копирование

### Создание скрипта резервного копирования
```bash
nano /opt/backup-role.sh
```

Содержимое:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Резервная копия базы данных
cp /home/yc-user/role/backend/database.db $BACKUP_DIR/database_$DATE.db

# Резервная копия загруженных файлов
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /home/yc-user/role/backend uploads/

# Удаление старых резервных копий (старше 30 дней)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /opt/backup-role.sh

# Добавление в crontab для ежедневного резервного копирования
crontab -e
```

Добавьте строку:
```
0 2 * * * /opt/backup-role.sh >> /var/log/backup.log 2>&1
```

## Безопасность

### Дополнительные меры безопасности
1. **Изменение SSH порта**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Измените Port 22 на другой порт
   sudo systemctl restart ssh
   ```

2. **Настройка fail2ban**:
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

3. **Регулярные обновления**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## Устранение неполадок

### Частые проблемы

1. **Приложение не запускается**:
   ```bash
   pm2 logs role-backend
   ```

2. **Ошибки Nginx**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Проблемы с базой данных**:
   ```bash
   cd /home/yc-user/role/backend
   source ../.venv/bin/activate
   python scripts/reset_database.py
   ```

4. **Нехватка места на диске**:
   ```bash
   # Очистка логов PM2
   pm2 flush
   
   # Очистка системных логов
   sudo journalctl --vacuum-time=7d
   ```

## Автоматизированное развертывание

Для упрощения процесса развертывания и управления приложением созданы специальные скрипты:

### Скрипты автоматизации

1. **[`deploy-initial.sh`](deploy-initial.sh)** - Скрипт первоначального развертывания
2. **[`deploy-update.sh`](deploy-update.sh)** - Скрипт обновления приложения
3. **[`manage-app.sh`](manage-app.sh)** - Скрипт управления приложением

### Использование скриптов

#### Первоначальное развертывание

```bash
# Скачайте скрипт на сервер
wget https://raw.githubusercontent.com/your-username/role/main/deploy-initial.sh
chmod +x deploy-initial.sh

# Отредактируйте конфигурацию в скрипте
nano deploy-initial.sh
# Измените REPO_URL и DOMAIN на ваши значения

# Запустите развертывание
./deploy-initial.sh
```

#### Обновление приложения

```bash
# Обычное обновление
./deploy-update.sh

# Обновление с пропуском резервной копии
./deploy-update.sh --skip-backup

# Принудительное обновление (игнорировать локальные изменения)
./deploy-update.sh --force

# Обновление до определенной ветки
./deploy-update.sh --branch develop
```

#### Управление приложением

```bash
# Проверка статуса всех сервисов
./manage-app.sh status

# Перезапуск приложения
./manage-app.sh restart

# Просмотр логов
./manage-app.sh logs

# Мониторинг в реальном времени
./manage-app.sh monitor

# Проверка здоровья приложения
./manage-app.sh health

# Создание резервной копии
./manage-app.sh backup

# Очистка логов и временных файлов
./manage-app.sh cleanup

# Полный список команд
./manage-app.sh --help
```

### Преимущества автоматизированного подхода

- **Безопасность**: Автоматическое создание резервных копий перед обновлением
- **Надежность**: Проверка работоспособности на каждом этапе
- **Удобство**: Простые команды для всех операций
- **Мониторинг**: Встроенные инструменты для отслеживания состояния
- **Откат**: Возможность быстрого восстановления из резервной копии

## Заключение

После выполнения всех шагов ваше приложение Role будет доступно по адресу вашего сервера. Приложение будет автоматически запускаться при перезагрузке сервера благодаря PM2.

Для продакшена рекомендуется:
- Использовать PostgreSQL вместо SQLite
- Настроить мониторинг (например, Grafana + Prometheus)
- Настроить автоматические резервные копии
- Использовать CDN для статических файлов
- Настроить SSL-сертификаты

**Важно**: Замените `<YOUR_REPOSITORY_URL>` и `your-domain.com` на актуальные значения для вашего проекта.

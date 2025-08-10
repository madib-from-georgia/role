# Удаленное развертывание приложения Role на Yandex Cloud

## Обзор

Эти скрипты позволяют развертывать и управлять приложением Role на виртуальной машине Yandex Cloud **с локальной машины** через SSH.

## Скрипты удаленного управления

### 1. [`deploy-remote.sh`](deploy-remote.sh) - Первоначальное развертывание
Полностью автоматизированное развертывание приложения на чистой Ubuntu 22.04 ВМ.

### 2. [`update-remote.sh`](update-remote.sh) - Обновление приложения
Безопасное обновление приложения с резервным копированием.

### 3. [`manage-remote.sh`](manage-remote.sh) - Управление приложением
Удаленное управление всеми аспектами работы приложения.

## Предварительные требования

### На локальной машине:
- SSH клиент
- Bash (Linux/macOS) или Git Bash (Windows)
- Доступ к интернету

### На виртуальной машине:
- Ubuntu 22.04 LTS
- SSH доступ с правами sudo
- Публичный IP адрес

## Быстрый старт

### 1. Создание ВМ в Yandex Cloud

1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте ВМ с параметрами:
   - **ОС**: Ubuntu 22.04 LTS
   - **CPU**: 2-4 vCPU
   - **RAM**: 4-8 GB
   - **Диск**: 20-40 GB SSD
   - **Публичный IP**: Да
   - **SSH-ключ**: Добавьте свой публичный ключ

### 2. Первоначальное развертывание

```bash
./deploy-remote.sh \
  --server 51.250.4.162 \
  --repo https://github.com/madib-from-georgia/role
```

**Параметры:**
- `--server IP` - IP адрес сервера (обязательно)
- `--repo URL` - URL Git репозитория (обязательно)
- `--domain DOMAIN` - Домен или IP для Nginx (опционально, по умолчанию IP сервера)
- `--user USER` - Пользователь на сервере (по умолчанию: yc-user)
- `--key PATH` - Путь к SSH ключу (опционально)
- `--branch BRANCH` - Ветка для развертывания (по умолчанию: main)

### 3. Проверка статуса

```bash
./manage-remote.sh --server 51.250.4.162 status
```

## Подробное использование

### Развертывание приложения

#### Базовое развертывание
```bash
./deploy-remote.sh --server 51.250.4.162 --repo https://github.com/madib-from-georgia/role
```

#### С указанием домена и SSH ключа
```bash
./deploy-remote.sh \
  --server 51.250.4.162 \
  --key ~/.ssh/role-key \
  --repo https://github.com/madib-from-georgia/role \
  --domain example.com \
  --branch main
```

### Обновление приложения

#### Обычное обновление
```bash
./update-remote.sh --server 51.250.4.162
```

#### Обновление с дополнительными параметрами
```bash
./update-remote.sh \
  --server 51.250.4.162 \
  --key ~/.ssh/role-key \
  --branch develop \
  --force
```

**Параметры обновления:**
- `--skip-backup` - Пропустить создание резервной копии
- `--force` - Принудительное обновление (игнорировать локальные изменения)
- `--branch BRANCH` - Обновиться до указанной ветки

### Управление приложением

#### Основные команды
```bash
# Статус приложения
./manage-remote.sh --server 51.250.4.162 status

# Запуск приложения
./manage-remote.sh --server 51.250.4.162 start

# Остановка приложения
./manage-remote.sh --server 51.250.4.162 stop

# Перезапуск приложения
./manage-remote.sh --server 51.250.4.162 restart
```

#### Логи и мониторинг
```bash
# Просмотр логов (последние 50 строк)
./manage-remote.sh --server 51.250.4.162 logs

# Просмотр логов (100 строк)
./manage-remote.sh --server 51.250.4.162 logs 100

# Логи в реальном времени
./manage-remote.sh --server 51.250.4.162 logs-live

# Монитор PM2
./manage-remote.sh --server 51.250.4.162 monitor
```

#### Обслуживание
```bash
# Проверка здоровья приложения
./manage-remote.sh --server 51.250.4.162 health

# Создание резервной копии
./manage-remote.sh --server 51.250.4.162 backup

# Очистка логов и временных файлов
./manage-remote.sh --server 51.250.4.162 cleanup

# Информация о системе
./manage-remote.sh --server 51.250.4.162 info
```

#### Управление Nginx
```bash
# Статус Nginx
./manage-remote.sh --server 51.250.4.162 nginx status

# Перезапуск Nginx
./manage-remote.sh --server 51.250.4.162 nginx restart

# Перезагрузка конфигурации Nginx
./manage-remote.sh --server 51.250.4.162 nginx reload
```

#### SSH сессия
```bash
# Открыть SSH сессию на сервере
./manage-remote.sh --server 51.250.4.162 shell
```

## Настройка SSH

### Использование SSH ключей

1. **Создание SSH ключа** (если нет):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/role-key
   ```

2. **Добавление публичного ключа в Yandex Cloud**:
   - Скопируйте содержимое `~/.ssh/role-key.pub`
   - Добавьте в настройки ВМ при создании

3. **Использование ключа в скриптах**:
   ```bash
   ./deploy-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key --repo URL
   ```

### Настройка SSH config

Создайте файл `~/.ssh/config`:
```
Host yandex-role
    HostName 51.250.4.162
    User yc-user
    IdentityFile ~/.ssh/role-key
    ServerAliveInterval 60
```

Тогда можно использовать:
```bash
./manage-remote.sh --server yandex-role status
```

## Настройка SSL

После развертывания настройте SSL сертификат:

```bash
# Подключитесь к серверу
./manage-remote.sh --server 51.250.4.162 shell

# На сервере выполните
sudo certbot --nginx -d your-domain.com
```

## Мониторинг и логи

### Структура логов на сервере
- **PM2 логи**: `/var/log/pm2/role-backend-*.log`
- **Nginx логи**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **Резервные копии**: `/opt/backups/`

### Автоматическое резервное копирование
Скрипт автоматически настраивает ежедневное резервное копирование в 2:00 AM.

## Устранение неполадок

### Проблемы с подключением
```bash
# Проверка подключения
ssh yc-user@51.250.4.162 "echo 'OK'"

# Проверка с ключом
ssh -i ~/.ssh/role-key yc-user@51.250.4.162 "echo 'OK'"
```

### Проблемы с развертыванием
```bash
# Проверка статуса после развертывания
./manage-remote.sh --server 51.250.4.162 health

# Просмотр логов
./manage-remote.sh --server 51.250.4.162 logs 100
```

### Проблемы с обновлением
```bash
# Принудительное обновление
./update-remote.sh --server 51.250.4.162 --force

# Откат к предыдущей версии (на сервере)
./manage-remote.sh --server 51.250.4.162 shell
cd /home/yc-user/role
git log --oneline -10  # Найти нужный коммит
git checkout COMMIT_HASH
./manage-remote.sh --server 51.250.4.162 restart
```

### Восстановление из резервной копии
```bash
# Подключение к серверу
./manage-remote.sh --server 51.250.4.162 shell

# На сервере
ls /opt/backups/  # Посмотреть доступные резервные копии
cp /opt/backups/database_YYYYMMDD_HHMMSS.db /home/yc-user/role/backend/database.db
./manage-remote.sh --server 51.250.4.162 restart
```

## Примеры использования

### Полный цикл развертывания
```bash
# 1. Развертывание
./deploy-remote.sh \
  --server 51.250.4.162 \
  --key ~/.ssh/role-key \
  --repo https://github.com/madib-from-georgia/role \
  --domain example.com

# 2. Проверка статуса
./manage-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key status

# 3. Настройка SSL (на сервере)
./manage-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key shell
sudo certbot --nginx -d example.com
exit

# 4. Проверка здоровья
./manage-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key health
```

### Регулярное обслуживание
```bash
# Еженедельное обновление
./update-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key

# Ежемесячная очистка
./manage-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key cleanup

# Проверка здоровья
./manage-remote.sh --server 51.250.4.162 --key ~/.ssh/role-key health
```

## Безопасность

### Рекомендации по безопасности
1. **Используйте SSH ключи** вместо паролей
2. **Ограничьте доступ** к SSH ключам (chmod 600)
3. **Регулярно обновляйте** систему и приложение
4. **Мониторьте логи** на предмет подозрительной активности
5. **Создавайте резервные копии** перед важными изменениями

### Настройка файрвола
Скрипт автоматически настраивает UFW, но вы можете дополнительно ограничить доступ:

```bash
./manage-remote.sh --server 51.250.4.162 shell

# На сервере
sudo ufw status
sudo ufw allow from YOUR_IP_ADDRESS to any port 22  # Ограничить SSH
sudo ufw delete allow ssh  # Удалить общее правило SSH
```

## Производительность

### Мониторинг ресурсов
```bash
# Информация о системе
./manage-remote.sh --server 51.250.4.162 info

# Мониторинг PM2
./manage-remote.sh --server 51.250.4.162 monitor
```

### Оптимизация
- **Увеличьте ресурсы ВМ** при высокой нагрузке
- **Настройте CDN** для статических файлов
- **Используйте PostgreSQL** вместо SQLite для продакшена
- **Настройте кэширование** в Nginx

## Заключение

Эти скрипты обеспечивают полный цикл управления приложением Role на Yandex Cloud:

✅ **Автоматизированное развертывание** - от чистой ВМ до работающего приложения  
✅ **Безопасные обновления** - с резервным копированием и проверками  
✅ **Удобное управление** - все операции с локальной машины  
✅ **Мониторинг и логи** - полный контроль над состоянием приложения  
✅ **Восстановление** - быстрый откат при проблемах  

**Важно**: Замените примеры IP адресов, доменов и путей к ключам на ваши реальные значения.

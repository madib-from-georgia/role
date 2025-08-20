# 📧 Руководство по настройке отправки email

## Пошаговая инструкция для настройки функции "Забыли пароль?"

### 1. Создание файла конфигурации

Создайте файл `.env` в папке `backend/`:

```bash
cd backend
touch .env
```

### 2. Настройка Yandex Mail (рекомендуется для России)

[YANDEX_EMAIL_SETUP.md](YANDEX_EMAIL_SETUP.md)

### 3. Альтернативные почтовые сервисы

#### Gmail (для пользователей за пределами России)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=ваш-email@gmail.com
SMTP_PASSWORD=пароль-приложения-16-символов
EMAIL_FROM=ваш-email@gmail.com
EMAIL_FROM_NAME=Роль
```

**Для Gmail нужно:**
1. Включить двухфакторную аутентификацию
2. Создать пароль приложения в настройках безопасности
3. Использовать этот пароль вместо основного

#### Mail.ru
```env
SMTP_SERVER=smtp.mail.ru
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=ваш-email@mail.ru
SMTP_PASSWORD=ваш-пароль
EMAIL_FROM=ваш-email@mail.ru
EMAIL_FROM_NAME=Роль
```

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=ваш-email@outlook.com
SMTP_PASSWORD=ваш-пароль
EMAIL_FROM=ваш-email@outlook.com
EMAIL_FROM_NAME=Роль
```

### 4. Проверка настроек

#### Шаг 4.1: Перезапустите backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Шаг 4.2: Проверьте в логах
При запуске вы должны увидеть:
```
✅ Email сервис настроен: ваш-email@gmail.com
```

Если видите:
```
⚠️ Email настройки не настроены. Пропускаем отправку email.
```
Значит, настройки неверные.

#### Шаг 4.3: Тестирование
Запустите тестовый скрипт:
```bash
python test_forgot_password.py
```

### 5. Тестирование через интерфейс

1. Откройте http://localhost:5173
2. Нажмите "Войти"
3. Нажмите "Забыли пароль?"
4. Введите существующий email
5. Проверьте почту (включая папку "Спам")

### 6. Возможные проблемы и решения

#### Проблема: "Authentication failed"
**Решение:**
- Убедитесь, что используете пароль приложения, а не обычный пароль
- Проверьте, что двухфакторная аутентификация включена

#### Проблема: "Connection refused"
**Решение:**
- Проверьте SMTP_SERVER и SMTP_PORT
- Убедитесь, что интернет-соединение работает

#### Проблема: Письма не приходят
**Решение:**
- Проверьте папку "Спам"
- Убедитесь, что EMAIL_FROM совпадает с SMTP_USERNAME
- Проверьте логи backend на ошибки

#### Проблема: "SSL/TLS error"
**Решение:**
- Убедитесь, что SMTP_USE_TLS=true
- Для Gmail используйте порт 587

### 7. Безопасность

⚠️ **ВАЖНО:**
- Никогда не коммитьте файл `.env` в git
- Файл `.env` уже добавлен в `.gitignore`
- Используйте пароли приложений, а не основные пароли
- Регулярно обновляйте пароли приложений

### 8. Пример полного файла .env

```env
# Основные настройки приложения
APP_NAME=Роль
DEBUG=false
VERSION=1.0.0

# База данных
DATABASE_URL=sqlite:///./database.db

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email настройки (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=Роль

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### 9. Проверка работы

После настройки функция "Забыли пароль?" будет работать следующим образом:

1. **Пользователь запрашивает сброс** → система создает токен
2. **Отправляется красивое письмо** с кнопкой "Сбросить пароль"
3. **Пользователь переходит по ссылке** → открывается форма нового пароля
4. **После смены пароля** → все сессии завершаются, отправляется уведомление

### 10. Поддержка

Если возникли проблемы:
1. Проверьте логи backend
2. Убедитесь, что все переменные в `.env` заполнены
3. Протестируйте с помощью `test_forgot_password.py`
4. Проверьте настройки почтового провайдера

---

**Готово!** 🎉 Функция "Забыли пароль?" настроена и готова к использованию.

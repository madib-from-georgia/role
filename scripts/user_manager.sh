#!/bin/bash

# Скрипт для управления пользователями системы "Роль"
# Автор: System Administrator
# Версия: 1.0

# Проверяем поддержку цветов в терминале
if [[ -t 1 ]] && [[ "${TERM:-}" != "dumb" ]] && command -v tput >/dev/null 2>&1 && tput colors >/dev/null 2>&1 && [[ $(tput colors) -ge 8 ]]; then
    # Цвета для вывода
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    NC='\033[0m' # No Color
else
    # Отключаем цвета если терминал их не поддерживает
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    NC=''
fi

# Путь к базе данных
DB_PATH="./backend/database.db"
BACKEND_DIR="./backend"

# Функция для вывода заголовка
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ СИСТЕМЫ    ${NC}"
    echo -e "${BLUE}              \"РОЛЬ\"                   ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

# Функция для проверки зависимостей
check_dependencies() {
    # Проверяем наличие sqlite3
    if ! command -v sqlite3 &> /dev/null; then
        echo -e "${RED}Ошибка: sqlite3 не установлен${NC}"
        echo -e "${YELLOW}Установите sqlite3:${NC}"
        echo "  Ubuntu/Debian: sudo apt-get install sqlite3"
        echo "  CentOS/RHEL: sudo yum install sqlite"
        echo "  macOS: brew install sqlite3"
        return 1
    fi
    
    # Проверяем наличие базы данных
    if [[ ! -f "$DB_PATH" ]]; then
        echo -e "${RED}Ошибка: База данных не найдена по пути: $DB_PATH${NC}"
        echo -e "${YELLOW}Убедитесь, что:${NC}"
        echo "1. Вы запускаете скрипт из корневой директории проекта"
        echo "2. Backend приложение было запущено хотя бы один раз"
        echo "3. Миграции базы данных выполнены"
        return 1
    fi
    
    return 0
}

# Функция для вывода меню
show_menu() {
    echo -e "${YELLOW}Выберите действие:${NC}"
    echo "1. Показать всех пользователей"
    echo "2. Добавить пользователя"
    echo "3. Удалить пользователя"
    echo "4. Изменить статус пользователя (активировать/деактивировать)"
    echo "5. Показать проекты пользователя"
    echo "6. Выход"
    echo
    echo -n "Введите номер действия [1-6]: "
}

# Функция для показа всех пользователей
show_all_users() {
    echo -e "${GREEN}=== СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ===${NC}"
    echo
    
    local query="SELECT id, email, username, full_name, is_active, created_at FROM users ORDER BY created_at DESC;"
    
    # Выполняем запрос и форматируем вывод
    echo -e "${BLUE}Пользователи системы \"Роль\":${NC}"
    echo "-------------------------------------------------------------------------------------"
    printf "%-5s %-25s %-15s %-20s %-8s %-19s\n" "ID" "EMAIL" "USERNAME" "FULL_NAME" "ACTIVE" "CREATED"
    echo "-------------------------------------------------------------------------------------"
    
    sqlite3 -separator $'\t' "$DB_PATH" "$query" | while IFS=$'\t' read -r id email username full_name is_active created_at; do
        # Форматируем дату
        formatted_date=$(echo "$created_at" | cut -d'T' -f1)
        
        # Форматируем статус
        if [[ "$is_active" == "1" ]]; then
            status="${GREEN}Да${NC}"
        else
            status="${RED}Нет${NC}"
        fi
        
        # Обрезаем длинные поля
        email_short=$(echo "$email" | cut -c1-24)
        username_short=$(echo "$username" | cut -c1-14)
        full_name_short=$(echo "$full_name" | cut -c1-19)
        
        printf "%-5s %-25s %-15s %-20s %-8s %-19s\n" "$id" "$email_short" "$username_short" "$full_name_short" "$status" "$formatted_date"
    done
    
    echo "-------------------------------------------------------------------------------------"
    
    # Подсчитываем количество пользователей
    local total_users=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users;")
    local active_users=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE is_active = 1;")
    local inactive_users=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE is_active = 0;")
    
    echo -e "${GREEN}Всего пользователей: $total_users${NC}"
    echo -e "${GREEN}Активных: $active_users${NC}"
    echo -e "${RED}Неактивных: $inactive_users${NC}"
    echo
}

# Функция для добавления пользователя
add_user() {
    echo -e "${GREEN}=== ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ===${NC}"
    echo
    
    # Запрашиваем email
    while true; do
        echo -n "Введите email пользователя: "
        read email
        
        # Проверяем, что email не пустой
        if [[ -z "$email" ]]; then
            echo -e "${RED}Ошибка: Email не может быть пустым${NC}"
            continue
        fi
        
        # Проверяем формат email
        if [[ ! "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            echo -e "${RED}Ошибка: Некорректный формат email${NC}"
            continue
        fi
        
        # Проверяем, что пользователь с таким email не существует
        local existing_user=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE email = '$email';")
        if [[ "$existing_user" -gt 0 ]]; then
            echo -e "${RED}Ошибка: Пользователь с email '$email' уже существует${NC}"
            continue
        fi
        
        break
    done
    
    # Запрашиваем username
    while true; do
        echo -n "Введите username пользователя: "
        read username
        
        # Проверяем, что username не пустой
        if [[ -z "$username" ]]; then
            echo -e "${RED}Ошибка: Username не может быть пустым${NC}"
            continue
        fi
        
        # Проверяем корректность username
        if [[ ! "$username" =~ ^[a-zA-Z0-9_-]+$ ]]; then
            echo -e "${RED}Ошибка: Username может содержать только буквы, цифры, дефисы и подчеркивания${NC}"
            continue
        fi
        
        # Проверяем, что пользователь с таким username не существует
        local existing_user=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE username = '$username';")
        if [[ "$existing_user" -gt 0 ]]; then
            echo -e "${RED}Ошибка: Пользователь с username '$username' уже существует${NC}"
            continue
        fi
        
        break
    done
    
    # Запрашиваем полное имя (опционально)
    echo -n "Введите полное имя пользователя (необязательно): "
    read full_name
    
    # Запрашиваем пароль
    while true; do
        echo -n "Введите пароль для пользователя: "
        read -s password
        echo
        
        if [[ -z "$password" ]]; then
            echo -e "${RED}Ошибка: Пароль не может быть пустым${NC}"
            continue
        fi
        
        if [[ ${#password} -lt 6 ]]; then
            echo -e "${RED}Ошибка: Пароль должен содержать минимум 6 символов${NC}"
            continue
        fi
        
        echo -n "Подтвердите пароль: "
        read -s password_confirm
        echo
        
        if [[ "$password" != "$password_confirm" ]]; then
            echo -e "${RED}Ошибка: Пароли не совпадают${NC}"
            continue
        fi
        
        break
    done
    
    # Генерируем хеш пароля с помощью Python
    echo -e "${YELLOW}Создание пользователя '$username'...${NC}"
    
    # Создаем временный Python скрипт для хеширования пароля
    local temp_script=$(mktemp)
    cat > "$temp_script" << EOF
import bcrypt
import sys
import sqlite3
from datetime import datetime

password = sys.argv[1]
email = sys.argv[2]
username = sys.argv[3]
full_name = sys.argv[4] if sys.argv[4] != 'NULL' else None

# Хешируем пароль
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

# Подключаемся к базе данных
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()

# Вставляем пользователя
try:
    cursor.execute("""
        INSERT INTO users (email, username, password_hash, full_name, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """, (email, username, password_hash, full_name, datetime.utcnow(), datetime.utcnow()))
    
    conn.commit()
    user_id = cursor.lastrowid
    print(f"SUCCESS:{user_id}")
    
except Exception as e:
    print(f"ERROR:{str(e)}")
    
finally:
    conn.close()
EOF
    
    # Проверяем наличие Python и bcrypt
    if ! python3 -c "import bcrypt" 2>/dev/null; then
        echo -e "${RED}Ошибка: Модуль bcrypt не установлен${NC}"
        echo -e "${YELLOW}Установите bcrypt: pip install bcrypt${NC}"
        rm "$temp_script"
        return 1
    fi
    
    # Выполняем скрипт
    local full_name_param="$full_name"
    if [[ -z "$full_name" ]]; then
        full_name_param="NULL"
    fi
    
    local result=$(python3 "$temp_script" "$password" "$email" "$username" "$full_name_param")
    rm "$temp_script"
    
    if [[ "$result" == SUCCESS:* ]]; then
        local user_id=${result#SUCCESS:}
        echo -e "${GREEN}Пользователь '$username' успешно создан с ID: $user_id${NC}"
        
        # Показываем информацию о созданном пользователе
        echo
        echo -e "${BLUE}Информация о пользователе:${NC}"
        sqlite3 -header -column "$DB_PATH" "SELECT id, email, username, full_name, is_active, created_at FROM users WHERE id = $user_id;"
        
    else
        local error_msg=${result#ERROR:}
        echo -e "${RED}Ошибка при создании пользователя: $error_msg${NC}"
        return 1
    fi
    
    echo
}

# Функция для удаления пользователя
delete_user() {
    echo -e "${GREEN}=== УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ===${NC}"
    echo
    
    # Запрашиваем идентификатор пользователя
    while true; do
        echo -n "Введите ID или email пользователя для удаления: "
        read user_identifier
        
        # Проверяем, что идентификатор не пустой
        if [[ -z "$user_identifier" ]]; then
            echo -e "${RED}Ошибка: Идентификатор не может быть пустым${NC}"
            continue
        fi
        
        # Ищем пользователя по ID или email
        local user_info
        if [[ "$user_identifier" =~ ^[0-9]+$ ]]; then
            # Поиск по ID
            user_info=$(sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, email, username, full_name FROM users WHERE id = $user_identifier;")
        else
            # Поиск по email
            user_info=$(sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, email, username, full_name FROM users WHERE email = '$user_identifier';")
        fi
        
        if [[ -z "$user_info" ]]; then
            echo -e "${RED}Ошибка: Пользователь не найден${NC}"
            continue
        fi
        
        # Разбираем информацию о пользователе
        IFS=$'\t' read -r user_id user_email user_username user_full_name <<< "$user_info"
        break
    done
    
    # Показываем информацию о пользователе
    echo -e "${BLUE}Информация о пользователе:${NC}"
    echo "ID: $user_id"
    echo "Email: $user_email"
    echo "Username: $user_username"
    echo "Полное имя: $user_full_name"
    echo
    
    # Показываем количество проектов пользователя
    local projects_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM projects WHERE user_id = $user_id;")
    echo -e "${YELLOW}У пользователя $projects_count проект(ов)${NC}"
    
    if [[ "$projects_count" -gt 0 ]]; then
        echo -e "${RED}ВНИМАНИЕ: При удалении пользователя будут удалены все его проекты и связанные данные!${NC}"
    fi
    echo
    
    # Запрашиваем подтверждение
    while true; do
        echo -e "${YELLOW}Вы действительно хотите удалить пользователя '$user_username' (ID: $user_id)? [y/n]: ${NC}"
        read confirm
        case $confirm in
            [Yy]* ) break;;
            [Nn]* ) echo -e "${YELLOW}Отмена удаления${NC}"; return 0;;
            * ) echo -e "${YELLOW}Пожалуйста, введите y или n${NC}";;
        esac
    done
    
    # Удаляем пользователя
    echo -e "${YELLOW}Удаление пользователя '$user_username'...${NC}"
    
    # Создаем временный SQL скрипт для удаления
    local temp_sql=$(mktemp)
    cat > "$temp_sql" << EOF
BEGIN TRANSACTION;

-- Удаляем связанные данные (каскадное удаление через внешние ключи должно работать автоматически)
-- Но на всякий случай удаляем явно

-- Удаляем токены пользователя
DELETE FROM user_tokens WHERE user_id = $user_id;

-- Удаляем проекты пользователя (это также удалит связанные тексты, персонажей и ответы)
DELETE FROM projects WHERE user_id = $user_id;

-- Удаляем самого пользователя
DELETE FROM users WHERE id = $user_id;

COMMIT;
EOF
    
    if sqlite3 "$DB_PATH" < "$temp_sql"; then
        echo -e "${GREEN}Пользователь '$user_username' успешно удален${NC}"
    else
        echo -e "${RED}Ошибка при удалении пользователя '$user_username'${NC}"
        rm "$temp_sql"
        return 1
    fi
    
    rm "$temp_sql"
    echo
}

# Функция для изменения статуса пользователя
toggle_user_status() {
    echo -e "${GREEN}=== ИЗМЕНЕНИЕ СТАТУСА ПОЛЬЗОВАТЕЛЯ ===${NC}"
    echo
    
    # Запрашиваем идентификатор пользователя
    while true; do
        echo -n "Введите ID или email пользователя: "
        read user_identifier
        
        if [[ -z "$user_identifier" ]]; then
            echo -e "${RED}Ошибка: Идентификатор не может быть пустым${NC}"
            continue
        fi
        
        # Ищем пользователя
        local user_info
        if [[ "$user_identifier" =~ ^[0-9]+$ ]]; then
            user_info=$(sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, email, username, full_name, is_active FROM users WHERE id = $user_identifier;")
        else
            user_info=$(sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, email, username, full_name, is_active FROM users WHERE email = '$user_identifier';")
        fi
        
        if [[ -z "$user_info" ]]; then
            echo -e "${RED}Ошибка: Пользователь не найден${NC}"
            continue
        fi
        
        IFS=$'\t' read -r user_id user_email user_username user_full_name is_active <<< "$user_info"
        break
    done
    
    # Показываем текущий статус
    echo -e "${BLUE}Информация о пользователе:${NC}"
    echo "ID: $user_id"
    echo "Email: $user_email"
    echo "Username: $user_username"
    echo "Полное имя: $user_full_name"
    
    if [[ "$is_active" == "1" ]]; then
        echo -e "Текущий статус: ${GREEN}Активен${NC}"
        new_status=0
        action="деактивировать"
    else
        echo -e "Текущий статус: ${RED}Неактивен${NC}"
        new_status=1
        action="активировать"
    fi
    echo
    
    # Запрашиваем подтверждение
    while true; do
        echo -e "${YELLOW}Вы хотите $action пользователя '$user_username'? [y/n]: ${NC}"
        read confirm
        case $confirm in
            [Yy]* ) break;;
            [Nn]* ) echo -e "${YELLOW}Отмена изменения статуса${NC}"; return 0;;
            * ) echo -e "${YELLOW}Пожалуйста, введите y или n${NC}";;
        esac
    done
    
    # Изменяем статус
    if sqlite3 "$DB_PATH" "UPDATE users SET is_active = $new_status, updated_at = datetime('now') WHERE id = $user_id;"; then
        if [[ "$new_status" == "1" ]]; then
            echo -e "${GREEN}Пользователь '$user_username' активирован${NC}"
        else
            echo -e "${YELLOW}Пользователь '$user_username' деактивирован${NC}"
        fi
    else
        echo -e "${RED}Ошибка при изменении статуса пользователя${NC}"
        return 1
    fi
    
    echo
}

# Функция для показа проектов пользователя
show_user_projects() {
    echo -e "${GREEN}=== ПРОЕКТЫ ПОЛЬЗОВАТЕЛЯ ===${NC}"
    echo
    
    # Запрашиваем идентификатор пользователя
    while true; do
        echo -n "Введите ID или email пользователя: "
        read user_identifier
        
        if [[ -z "$user_identifier" ]]; then
            echo -e "${RED}Ошибка: Идентификатор не может быть пустым${NC}"
            continue
        fi
        
        # Ищем пользователя
        local user_info
        if [[ "$user_identifier" =~ ^[0-9]+$ ]]; then
            user_info=$(sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, email, username FROM users WHERE id = $user_identifier;")
        else
            user_info=$(sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, email, username FROM users WHERE email = '$user_identifier';")
        fi
        
        if [[ -z "$user_info" ]]; then
            echo -e "${RED}Ошибка: Пользователь не найден${NC}"
            continue
        fi
        
        IFS=$'\t' read -r user_id user_email user_username <<< "$user_info"
        break
    done
    
    echo -e "${BLUE}Проекты пользователя '$user_username' (ID: $user_id):${NC}"
    echo "----------------------------------------------------------------"
    printf "%-5s %-30s %-15s %-15s\n" "ID" "НАЗВАНИЕ" "СОЗДАН" "ОБНОВЛЕН"
    echo "----------------------------------------------------------------"
    
    # Получаем проекты пользователя
    sqlite3 -separator $'\t' "$DB_PATH" "SELECT id, title, created_at, updated_at FROM projects WHERE user_id = $user_id ORDER BY updated_at DESC;" | while IFS=$'\t' read -r project_id project_name created_at updated_at; do
        # Форматируем даты
        created_date=$(echo "$created_at" | cut -d'T' -f1)
        updated_date=$(echo "$updated_at" | cut -d'T' -f1)
        
        # Обрезаем длинное название
        project_name_short=$(echo "$project_name" | cut -c1-29)
        
        printf "%-5s %-30s %-15s %-15s\n" "$project_id" "$project_name_short" "$created_date" "$updated_date"
    done
    
    echo "----------------------------------------------------------------"
    
    # Подсчитываем статистику
    local total_projects=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM projects WHERE user_id = $user_id;")
    local total_texts=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM texts WHERE project_id IN (SELECT id FROM projects WHERE user_id = $user_id);")
    local total_characters=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM characters WHERE text_id IN (SELECT id FROM texts WHERE project_id IN (SELECT id FROM projects WHERE user_id = $user_id));")
    
    echo -e "${GREEN}Всего проектов: $total_projects${NC}"
    echo -e "${GREEN}Всего текстов: $total_texts${NC}"
    echo -e "${GREEN}Всего персонажей: $total_characters${NC}"
    echo
}

# Функция для паузы
pause() {
    echo
    echo -n "Нажмите Enter для продолжения..."
    read
}

# Главная функция
main() {
    # Проверяем зависимости
    if ! check_dependencies; then
        exit 1
    fi
    
    while true; do
        clear
        print_header
        show_menu
        
        read choice
        echo
        
        case $choice in
            1)
                show_all_users
                pause
                ;;
            2)
                add_user
                pause
                ;;
            3)
                delete_user
                pause
                ;;
            4)
                toggle_user_status
                pause
                ;;
            5)
                show_user_projects
                pause
                ;;
            6)
                echo -e "${GREEN}Выход из программы${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Неверный выбор. Пожалуйста, введите число от 1 до 6${NC}"
                pause
                ;;
        esac
    done
}

# Проверяем, что скрипт запущен в интерактивном режиме
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

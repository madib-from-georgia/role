# WeasyPrint Setup для macOS

WeasyPrint требует системные библиотеки для работы на macOS. По умолчанию приложение работает без WeasyPrint, используя только ReportLab для PDF генерации.

## Опциональная установка WeasyPrint

Если вы хотите использовать WeasyPrint для HTML to PDF конверсии, выполните следующие шаги:

### 1. Установите системные зависимости через Homebrew

```bash
# Установите Homebrew если еще не установлен
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установите необходимые системные библиотеки
brew install cairo pango gdk-pixbuf libffi
```

### 2. Установите WeasyPrint

```bash
pip install weasyprint==61.2
```

### 3. Раскомментируйте WeasyPrint в requirements.txt

Откройте `backend/requirements.txt` и раскомментируйте строку:
```
weasyprint==61.2  # HTML to PDF
```

## Проверка установки

```python
try:
    import weasyprint
    print("WeasyPrint успешно установлен!")
except ImportError as e:
    print(f"WeasyPrint недоступен: {e}")
```

## Альтернативы

Приложение полностью функционально без WeasyPrint:
- PDF генерация через **ReportLab** (встроено)
- DOCX генерация через **python-docx** (встроено)
- HTML шаблоны для preview (встроено)

## Troubleshooting

### Ошибка: "cannot load library 'gobject-2.0-0'"

Эта ошибка означает, что системные библиотеки не установлены. Выполните шаг 1 выше.

### Ошибка при установке через pip

```bash
# Попробуйте установить с системными флагами
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig"
pip install weasyprint
```

### Для Linux (Ubuntu/Debian)

```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
pip install weasyprint
```

### Для Windows

WeasyPrint обычно работает без дополнительных настроек на Windows:
```bash
pip install weasyprint
```

## Документация

- [WeasyPrint Installation Guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)
- [WeasyPrint Troubleshooting](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting)

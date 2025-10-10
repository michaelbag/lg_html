# Генератор этикеток с DataMatrix кодами

Автоматическая генерация этикеток с DataMatrix/QR кодами из CSV данных с наложением на PDF/JPG шаблоны.

## 🎯 Возможности

- ✅ Генерация DataMatrix кодов из CSV данных
- ✅ Наложение кодов на PDF или JPG шаблоны
- ✅ Гибкая настройка позиции и размера кодов
- ✅ Добавление текста под DataMatrix в высоком разрешении
- ✅ Поддержка EAC логотипов
- ✅ Экспорт в PDF и HTML
- ✅ Прозрачный фон для PNG этикеток
- ✅ Конфигурация через JSON/INI файлы

## 📦 Установка

### Требования
- Python 3.11+
- pip

### Зависимости

```bash
pip install Pillow reportlab pylibdmtx PyPDF2 qrcode[pil]
```

Или используйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## 🚀 Использование

### Базовый запуск

```bash
python main.py data.csv ./output
```

### С конфигурационным файлом

```bash
python main.py --config config.ini data.csv ./output
```

### С параметрами командной строки

```bash
python main.py data.csv ./output \
  --width 30 \
  --height 20 \
  --template ./makets/template.pdf \
  --dm-size 20 \
  --dm-position bottom-right \
  --dm-margin 5
```

## ⚙️ Конфигурация

### Формат CSV

CSV файл должен содержать 3 колонки (разделитель: TAB):

```
[DataMatrix данные]	[Штрихкод]	[Название продукта]
```

Пример:
```
0108809687640804215!O3HX91EE1192...	08809687640804	PLARECETA Cream
```

### Конфигурационный файл (config.ini)

```ini
[settings]
width = 30              # Ширина этикетки (мм)
height = 20             # Высота этикетки (мм)
margin = 1              # Отступы (мм)
dpi = 300               # Разрешение для PNG/JPG
delimiter =             # Разделитель CSV (tab)
dm_scale = 1.3          # Масштаб DataMatrix (1.0 = 100%)
eac_image = eac.png     # Путь к EAC логотипу
eac_height = 4          # Высота EAC (мм)
no_pdf = false          # Создавать PDF

# Параметры шаблона
template = ./makets/template.pdf
dm_position = bottom-right  # bottom-right, bottom-left, top-right, top-left
dm_size = 20                # Размер большей стороны DM (мм)
dm_margin = 5               # Отступ от края (мм)

# Параметры отображения
no_eac = true               # Скрыть EAC логотип
no_product_name = true      # Скрыть название продукта
text_below_dm = true        # Текст под DataMatrix
transparent_bg = true       # Прозрачный фон
```

### JSON конфигурация

```json
{
    "width": 30,
    "height": 20,
    "margin": 1,
    "dpi": 300,
    "template": "./makets/template.pdf",
    "dm_size": 20,
    "dm_margin": 5,
    "no_eac": true,
    "text_below_dm": true,
    "transparent_bg": true
}
```

## 📊 Параметры командной строки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--width` | Ширина страницы (мм) | 30 |
| `--height` | Высота страницы (мм) | 20 |
| `--margin` | Отступ от краев (мм) | 2 |
| `--dpi` | DPI для изображений | 300 |
| `--delimiter` | Разделитель CSV | `\t` (tab) |
| `--dm-scale` | Масштаб DataMatrix | 1.0 |
| `--eac-image` | Путь к EAC изображению | eac.png |
| `--eac-height` | Высота EAC (мм) | 5 |
| `--template` | Путь к шаблону (PDF/JPG) | - |
| `--dm-position` | Позиция DM на шаблоне | bottom-right |
| `--dm-size` | Размер большей стороны DM (мм) | 15 |
| `--dm-margin` | Отступ DM от края (мм) | 2 |
| `--no-pdf` | Не создавать PDF | false |
| `--no-eac` | Не отображать EAC | false |
| `--no-product-name` | Не отображать название | false |
| `--text-below-dm` | Текст под DataMatrix | false |
| `--transparent-bg` | Прозрачный фон | false |

## 📁 Структура проекта

```
lg_html/
├── main.py              # Основной скрипт
├── config.ini           # Конфигурация (INI)
├── config.json          # Конфигурация (JSON) - игнорируется git
├── data.csv             # CSV с данными
├── eac.png              # Логотип EAC
├── makets/              # PDF/JPG шаблоны (игнорируется git)
├── output/              # Выходные файлы (игнорируется git)
├── venv/                # Виртуальное окружение
├── .gitignore
└── README.md
```

## 🎨 Примеры использования

### Генерация простых этикеток

```bash
python main.py data.csv ./output --width 30 --height 20
```

### Наложение на PDF шаблон

```bash
python main.py data.csv ./output \
  --template ./makets/template.pdf \
  --dm-position bottom-right \
  --dm-size 20 \
  --dm-margin 5
```

### Только DataMatrix + текст (прозрачный фон)

```bash
python main.py data.csv ./output \
  --no-eac \
  --no-product-name \
  --text-below-dm \
  --transparent-bg
```

## 🔧 Особенности

### Высокое качество текста в PDF

Скрипт автоматически создает изображения в разрешении **1200 DPI** при вставке в PDF для обеспечения максимальной читаемости текста.

### Предотвращение наложения текста

При работе с PDF шаблонами каждая страница загружается заново, что предотвращает наложение текста с предыдущих страниц.

### Резервные варианты

- Если `pylibdmtx` недоступен, используется QR код
- Если шрифт не найден, используется стандартный шрифт PIL

## 🐛 Устранение неполадок

### Текст под DataMatrix нечитаемый

Убедитесь, что используется последняя версия с поддержкой высокого разрешения (1200 DPI).

### Текст накладывается на предыдущие страницы

Обновите код - исправление включено в последнюю версию.

### Ошибка импорта pylibdmtx

```bash
# macOS
brew install libdmtx
pip install pylibdmtx

# Linux
sudo apt-get install libdmtx0a
pip install pylibdmtx

# Windows
# Скачайте libdmtx с официального сайта
pip install pylibdmtx
```

## 📝 Лицензия

MIT License

## 👤 Автор

Разработано для автоматизации генерации этикеток с маркировкой.

## 🤝 Вклад

Приветствуются pull requests и issue reports!

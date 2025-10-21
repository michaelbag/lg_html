# Генератор этикеток в PDF

Генерация этикеток с DataMatrix (в т.ч. GS1 DataMatrix) в многостраничные PDF с использованием шаблонов.

- `main.py` — базовый генератор
- `gen2.py` — продвинутый генератор с шаблонами и конфигами (актуальная версия: v2.12)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/michaelbag/lg_html.git
cd lg_html
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Структура проекта

```
lg_html/
├── gen2.py               # Улучшенный генератор с шаблонами (v2.12)
├── main.py               # Оригинальный генератор
├── conf/                 # JSON-конфиги (см. CONFIG_EXAMPLES.md)
├── input_data/           # CSV с данными (разделитель — табуляция)
├── input_templates/      # PDF шаблоны
├── output/               # Результаты PDF
├── temp/                 # Временные файлы (авто)
├── CONFIG_EXAMPLES.md    # Документация по конфигам
├── requirements.txt
└── README.md
```

## Использование main.py

Оригинальный скрипт для генерации простых этикеток:

```bash
python main.py <csv_file> <output_pdf> [опции]
```

### Основные параметры:
- `csv_file` - путь к CSV файлу с данными
- `output_pdf` - путь к выходному PDF файлу
- `--dm-size` - размер DataMatrix кода в мм
- `--dm-x`, `--dm-y` - координаты DataMatrix
- `--dpi` - DPI для генерации (по умолчанию: 300)

### Пример:
```bash
python main.py data.csv.example output.pdf --dm-size 15 --dm-x 10 --dm-y 5
```

## Использование gen2.py

Улучшенный скрипт с поддержкой шаблонов, конфигураций и автоматической организацией файлов.

### Структура папок

Скрипт автоматически создает и использует папки:

- **`input_data/`** - CSV файлы с данными (разделитель - табуляция)
- **`input_templates/`** - PDF шаблоны для этикеток
- **`temp/`** - временные файлы (создаются и удаляются автоматически)
- **`output/`** - готовые PDF файлы с этикетками
- **`conf/`** - конфигурационные файлы JSON с настройками параметров

### Быстрый старт

1. Поместите CSV файл в папку `input_data/`
2. Поместите PDF шаблон в папку `input_templates/`
3. Запустите скрипт:

```bash
# С конфигурационным файлом (рекомендуется)
python gen2.py -c single_template.json

# Или с параметрами командной строки
python gen2.py -t single -dx 10 -dy 5 -ds 15 -dc 0
```

Показать доступные примеры конфигураций:
```bash
python gen2.py --show-configs
```

### Конфигурационные файлы

Для упрощения использования создайте JSON файл в папке `conf/` с настройками (см. также CONFIG_EXAMPLES.md):

```json
{
    "description": "Конфигурация для single шаблона",
    "template_type": "single",
    "csv_file": "input_data/data.csv",
    "template_pdf": "input_templates/maket.pdf",
    "output_pdf": "output/out.pdf",
    "dm_x": 10,
    "dm_y": 5,
    "dm_size": 15,
    "datamatrix_column": 0,
    "text_column": 2,
    "text_start": 0,
    "text_length": 10,
    "text_font_size": 14,
    "text_offset_x": 20,
    "text_offset_y": 0,
    "text_color": "black",
    "dpi": 300
}
```

Затем используйте:
```bash
python gen2.py -c имя_конфигурации.json
```

### Основные параметры

#### Обязательные:
- `-t, --template-type` - тип шаблона: `single` или `multiple`
- `-dx, --dm-x` - X координата DataMatrix (слева сверху) в мм
- `-dy, --dm-y` - Y координата DataMatrix (слева сверху) в мм
- `-ds, --dm-size` - размер DataMatrix кода в мм

#### Пути к файлам (можно указывать в конфиге):
- `csv_file` — путь к CSV (если не указан, ищется в `input_data/`)
- `template_pdf` — путь к PDF шаблону (если не указан, ищется в `input_templates/`)
- `output_pdf` — путь к выходному PDF (если не указан, создается в `output/`)
Примечание: аргументы командной строки имеют приоритет над значениями в конфиге.

#### Для множественного шаблона:
- `-lh, --labels-horizontal` - количество этикеток по горизонтали
- `-lv, --labels-vertical` - количество этикеток по вертикали
- `-lw, --label-width` - ширина отдельной этикетки в мм
- `-lh2, --label-height` - высота отдельной этикетки в мм
- `-lml, --label-margin-left` - отступ слева от края страницы в мм
- `-lmt, --label-margin-top` - отступ сверху от края страницы в мм
- `-lsh, --label-spacing-horizontal` - расстояние между этикетками по горизонтали в мм
- `-lsv, --label-spacing-vertical` - расстояние между этикетками по вертикали в мм

#### Параметры CSV:
- `-dc, --datamatrix-column` - номер столбца CSV для DataMatrix (начиная с 0)

#### Текстовые поля:
- `-tc, --text-column` - номер столбца CSV для текста
- `-ts, --text-start` - начальная позиция для извлечения текста
- `-tl, --text-length` - длина извлекаемого текста
- `-tfs, --text-font-size` - размер шрифта для текста в пунктах
- `-tox, --text-offset-x` - смещение текста по X относительно DataMatrix в мм
- `-toy, --text-offset-y` - смещение текста по Y относительно DataMatrix в мм
- `-tcl, --text-color` - цвет текста

#### Дополнительные:
- `-d, --dpi` - DPI для генерации изображений (по умолчанию: 300)
- `-c, --config` - путь к файлу конфигурации JSON
- `--show-configs` - показать доступные примеры конфигураций и выйти
- `-v, --version` - показать версию программы

### Примеры использования

#### 1. С конфигурационным файлом
```bash
# Использование готовой конфигурации
python gen2.py -c single_template.json
python gen2.py -c multiple_template.json
python gen2.py -c simple_multiple.json
```

#### 2. Автоматический поиск файлов
```bash
# Все файлы берутся автоматически из папок
python gen2.py -t single -dx 10 -dy 5 -ds 15 -dc 0
```

#### 3. Один шаблон на одну этикетку
```bash
python gen2.py data.csv maket.pdf output.pdf \
    -t single \
    -dx 10 \
    -dy 5 \
    -ds 15 \
    -dc 0
```

#### 4. Множественный шаблон (3x6)
```bash
python gen2.py -t multiple -lh 3 -lv 6 -dx 5 -dy 3 -ds 12 -dc 0
```

#### 5. С текстовыми полями
```bash
python gen2.py -t single -dx 10 -dy 5 -ds 15 -dc 0 \
    -tc 2 -ts 0 -tl 10 -tfs 14 -tox 20 -toy 0
```

#### 6. Полная команда с множественным шаблоном
```bash
python gen2.py data_copy.csv multi_maket.pdf out_multi_maket.pdf \
    -t multiple -lh 3 -lv 6 -lw 55 -lh2 37 -lml 22 -lmt 30 \
    -lsh 5 -lsv 3 -dx 38 -dy 15 -ds 17 -tc 0 -ts 32 -tl 10 \
    -tfs 7 -tox 1 -toy 18 -tcl black
```

## Формат CSV файла

CSV файл должен использовать разделитель табуляция. Парсинг устойчив к кавычкам в полях. Пример:

```
0108809687640804215!	PLARECETA 1234567890	Дополнительная информация
0108809687640804215!	PLARECETA 1234567891	Дополнительная информация
0108809687640804215!	PLARECETA 1234567892	Дополнительная информация
```

## Типы шаблонов

### Single (один шаблон на этикетку)
- Каждая этикетка создается на отдельной странице
- Используется один PDF шаблон для всех этикеток
- Подходит для больших этикеток

### Multiple (несколько этикеток на шаблоне)
- Несколько этикеток размещаются на одной странице
- Автоматическое создание новых страниц при превышении лимита
- Заполнение по строкам и столбцам
- Подходит для маленьких этикеток

## Особенности

1. Поддержка GS1 DataMatrix (AI/FNC1), ISO/IEC 16022
2. Прозрачный фон кодов для наложения на шаблон
3. Точное позиционирование (мм), масштабирование, 300 DPI
4. Многостраничный вывод, сетки для multiple-шаблонов
5. Извлечение фрагментов текста из CSV

## Зависимости

- `pylibdmtx` - для генерации DataMatrix кодов
- `qrcode` - альтернативная библиотека для кодов (если pylibdmtx недоступна)
- `reportlab` - для работы с PDF
- `PyPDF2` - для работы с PDF шаблонами
- `Pillow` - для обработки изображений

## Версии

- `gen2.py v2.12` — актуальная: поддержка путей в конфиге, `--show-configs`, устойчивый CSV-парсинг, фиксы слияния PDF, отображение прогресса
- `main.py` — базовая версия

## Автор

**Michael BAG**  
📧 E-mail: mk@p7net.ru  
💬 Telegram: https://t.me/michaelbag

## Лицензия

Проект распространяется свободно для использования и модификации.
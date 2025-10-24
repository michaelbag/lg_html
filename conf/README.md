# Папка conf

Эта папка предназначена для хранения конфигурационных файлов JSON с настройками генерации этикеток.

## Поддерживаемые форматы:

- **JSON файлы** (.json) - конфигурации с настройками параметров

## Примеры конфигураций:

См. файлы в корневой папке проекта:
- `config_csv_example.json` - пример для CSV файлов
- `config_excel_example.json` - пример для Excel файлов
- `config_v1.0.json` - базовая конфигурация

## Структура конфигурации:

```json
{
    "description": "Описание конфигурации",
    "template_type": "single",
    "csv_file": "input_data/data.csv",
    "template_pdf": "input_templates/template.pdf",
    "output_pdf": "output/result.pdf",
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

## Использование:

1. Создайте JSON файл с настройками в этой папке
2. Запустите генератор: `python gen2.py -c имя_конфигурации.json`
3. Или используйте генератор конфигураций: `python generate_config.py data.csv template.pdf output.pdf --type single`

#!/usr/bin/env python3
"""
Генератор конфигурационных файлов для генератора этикеток v2.16
Поддерживает создание конфигураций для CSV и Excel файлов
"""

import json
import argparse
import os
import sys
from pathlib import Path

def create_single_template_config(data_file, template_pdf, output_pdf, **kwargs):
    """Создание конфигурации для single шаблона"""
    config = {
        "_comment": "Конфигурация для single шаблона - один шаблон на этикетку",
        "description": "Single template configuration",
        
        "_template_type_comment": "Тип шаблона: 'single' (один шаблон на этикетку) или 'multiple' (несколько этикеток на шаблоне)",
        "template_type": "single",
        
        "_data_file_comment": "Путь к файлу с данными (CSV или Excel .xlsx). Может быть относительным или абсолютным",
        "data_file": data_file,
        
        "_template_pdf_comment": "Путь к PDF шаблону. Может быть относительным или абсолютным",
        "template_pdf": template_pdf,
        
        "_output_pdf_comment": "Путь к выходному PDF файлу. Может быть относительным или абсолютным",
        "output_pdf": output_pdf,
        
        "_datamatrix_comment": "Параметры DataMatrix кода",
        "dm_x": kwargs.get('dm_x', 10),
        "dm_y": kwargs.get('dm_y', 5),
        "dm_size": kwargs.get('dm_size', 15),
        "datamatrix_column": kwargs.get('datamatrix_column', 0),
        
        "_text_comment": "Параметры текста на этикетке",
        "text_column": kwargs.get('text_column', None),
        "text_start": kwargs.get('text_start', 0),
        "text_length": kwargs.get('text_length', None),
        "text_font_size": kwargs.get('text_font_size', 12),
        "text_offset_x": kwargs.get('text_offset_x', 5),
        "text_offset_y": kwargs.get('text_offset_y', 0),
        "text_color": kwargs.get('text_color', 'black'),
        
        "_excel_comment": "Параметры Excel файла (если используется)",
        "excel_sheet": kwargs.get('excel_sheet', 0),
        
        "_quality_comment": "Параметры качества",
        "dpi": kwargs.get('dpi', 300)
    }
    
    # Удаляем None значения
    config = {k: v for k, v in config.items() if v is not None}
    return config

def create_multiple_template_config(data_file, template_pdf, output_pdf, **kwargs):
    """Создание конфигурации для multiple шаблона"""
    config = {
        "_comment": "Конфигурация для multiple шаблона - несколько этикеток на странице",
        "description": "Multiple template configuration",
        
        "_template_type_comment": "Тип шаблона: 'single' (один шаблон на этикетку) или 'multiple' (несколько этикеток на шаблоне)",
        "template_type": "multiple",
        
        "_data_file_comment": "Путь к файлу с данными (CSV или Excel .xlsx). Может быть относительным или абсолютным",
        "data_file": data_file,
        
        "_template_pdf_comment": "Путь к PDF шаблону. Может быть относительным или абсолютным",
        "template_pdf": template_pdf,
        
        "_output_pdf_comment": "Путь к выходному PDF файлу. Может быть относительным или абсолютным",
        "output_pdf": output_pdf,
        
        "_labels_comment": "Параметры размещения этикеток на странице",
        "labels_horizontal": kwargs.get('labels_horizontal', 2),
        "labels_vertical": kwargs.get('labels_vertical', 3),
        "label_width": kwargs.get('label_width', 100),
        "label_height": kwargs.get('label_height', 50),
        "label_margin_left": kwargs.get('label_margin_left', 10),
        "label_margin_top": kwargs.get('label_margin_top', 15),
        "label_spacing_horizontal": kwargs.get('label_spacing_horizontal', 5),
        "label_spacing_vertical": kwargs.get('label_spacing_vertical', 3),
        
        "_datamatrix_comment": "Параметры DataMatrix кода",
        "dm_x": kwargs.get('dm_x', 20),
        "dm_y": kwargs.get('dm_y', 10),
        "dm_size": kwargs.get('dm_size', 15),
        "datamatrix_column": kwargs.get('datamatrix_column', 0),
        
        "_text_comment": "Параметры текста на этикетке",
        "text_column": kwargs.get('text_column', None),
        "text_start": kwargs.get('text_start', 0),
        "text_length": kwargs.get('text_length', None),
        "text_font_size": kwargs.get('text_font_size', 12),
        "text_offset_x": kwargs.get('text_offset_x', 25),
        "text_offset_y": kwargs.get('text_offset_y', 5),
        "text_color": kwargs.get('text_color', 'black'),
        
        "_excel_comment": "Параметры Excel файла (если используется)",
        "excel_sheet": kwargs.get('excel_sheet', 0),
        
        "_quality_comment": "Параметры качества",
        "dpi": kwargs.get('dpi', 300)
    }
    
    # Удаляем None значения
    config = {k: v for k, v in config.items() if v is not None}
    return config

def detect_file_type(file_path):
    """Определение типа файла данных"""
    if not file_path:
        return "unknown"
    
    file_path = str(file_path).lower()
    if file_path.endswith(('.xlsx', '.xls')):
        return "excel"
    elif file_path.endswith('.csv'):
        return "csv"
    else:
        return "unknown"

def main():
    parser = argparse.ArgumentParser(
        description="Генератор конфигурационных файлов для генератора этикеток v2.16",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

1. Создание конфигурации для CSV файла (single):
   python generate_config.py data.csv template.pdf output.pdf --type single

2. Создание конфигурации для Excel файла (multiple):
   python generate_config.py data.xlsx template.pdf output.pdf --type multiple --excel-sheet "Sheet1"

3. Создание конфигурации с настройками:
   python generate_config.py data.csv template.pdf output.pdf --type single --dm-x 15 --dm-y 10 --dm-size 20
        """
    )
    
    # Обязательные параметры
    parser.add_argument('data_file', help='Путь к файлу с данными (CSV или Excel)')
    parser.add_argument('template_pdf', help='Путь к PDF шаблону')
    parser.add_argument('output_pdf', help='Путь к выходному PDF файлу')
    
    # Тип шаблона
    parser.add_argument('--type', choices=['single', 'multiple'], required=True,
                       help='Тип шаблона: single (один на этикетку) или multiple (несколько на странице)')
    
    # Параметры DataMatrix
    parser.add_argument('--dm-x', type=float, default=10, help='Позиция DataMatrix по X (мм)')
    parser.add_argument('--dm-y', type=float, default=5, help='Позиция DataMatrix по Y (мм)')
    parser.add_argument('--dm-size', type=float, default=15, help='Размер DataMatrix (мм)')
    parser.add_argument('--datamatrix-column', type=int, default=0, help='Номер столбца с DataMatrix данными')
    
    # Параметры текста
    parser.add_argument('--text-column', type=int, help='Номер столбца с текстом (опционально)')
    parser.add_argument('--text-start', type=int, default=0, help='Начальная позиция текста')
    parser.add_argument('--text-length', type=int, help='Длина текста (опционально)')
    parser.add_argument('--text-font-size', type=int, default=12, help='Размер шрифта текста')
    parser.add_argument('--text-offset-x', type=float, default=5, help='Смещение текста по X (мм)')
    parser.add_argument('--text-offset-y', type=float, default=0, help='Смещение текста по Y (мм)')
    parser.add_argument('--text-color', default='black', help='Цвет текста')
    
    # Параметры для multiple шаблона
    parser.add_argument('--labels-horizontal', type=int, default=2, help='Количество этикеток по горизонтали')
    parser.add_argument('--labels-vertical', type=int, default=3, help='Количество этикеток по вертикали')
    parser.add_argument('--label-width', type=float, default=100, help='Ширина этикетки (мм)')
    parser.add_argument('--label-height', type=float, default=50, help='Высота этикетки (мм)')
    parser.add_argument('--label-margin-left', type=float, default=10, help='Отступ слева (мм)')
    parser.add_argument('--label-margin-top', type=float, default=15, help='Отступ сверху (мм)')
    parser.add_argument('--label-spacing-horizontal', type=float, default=5, help='Расстояние по горизонтали (мм)')
    parser.add_argument('--label-spacing-vertical', type=float, default=3, help='Расстояние по вертикали (мм)')
    
    # Параметры Excel
    parser.add_argument('--excel-sheet', default=0, help='Номер или имя листа Excel (по умолчанию: 0)')
    
    # Качество
    parser.add_argument('--dpi', type=int, default=300, help='DPI для генерации (по умолчанию: 300)')
    
    # Выходной файл
    parser.add_argument('-o', '--output', help='Путь к выходному JSON файлу (по умолчанию: config.json)')
    
    args = parser.parse_args()
    
    # Определяем тип файла данных
    file_type = detect_file_type(args.data_file)
    print(f"Обнаружен тип файла данных: {file_type}")
    
    if file_type == "excel":
        print("✓ Excel файл обнаружен - будет использована поддержка Excel")
        print(f"  Лист Excel: {args.excel_sheet}")
    elif file_type == "csv":
        print("✓ CSV файл обнаружен")
    else:
        print("⚠️  Неизвестный тип файла - предполагается CSV")
    
    # Создаем конфигурацию
    kwargs = {
        'dm_x': args.dm_x,
        'dm_y': args.dm_y,
        'dm_size': args.dm_size,
        'datamatrix_column': args.datamatrix_column,
        'text_column': args.text_column,
        'text_start': args.text_start,
        'text_length': args.text_length,
        'text_font_size': args.text_font_size,
        'text_offset_x': args.text_offset_x,
        'text_offset_y': args.text_offset_y,
        'text_color': args.text_color,
        'excel_sheet': args.excel_sheet,
        'dpi': args.dpi
    }
    
    if args.type == 'multiple':
        kwargs.update({
            'labels_horizontal': args.labels_horizontal,
            'labels_vertical': args.labels_vertical,
            'label_width': args.label_width,
            'label_height': args.label_height,
            'label_margin_left': args.label_margin_left,
            'label_margin_top': args.label_margin_top,
            'label_spacing_horizontal': args.label_spacing_horizontal,
            'label_spacing_vertical': args.label_spacing_vertical
        })
        config = create_multiple_template_config(args.data_file, args.template_pdf, args.output_pdf, **kwargs)
    else:
        config = create_single_template_config(args.data_file, args.template_pdf, args.output_pdf, **kwargs)
    
    # Определяем выходной файл
    output_file = args.output or 'config.json'
    
    # Сохраняем конфигурацию
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ Конфигурация создана: {output_file}")
        print(f"✓ Тип шаблона: {args.type}")
        print(f"✓ Файл данных: {args.data_file}")
        print(f"✓ Шаблон PDF: {args.template_pdf}")
        print(f"✓ Выходной PDF: {args.output_pdf}")
        
        if file_type == "excel":
            print(f"✓ Лист Excel: {args.excel_sheet}")
        
        print(f"\nДля использования конфигурации выполните:")
        print(f"  python gen2.py -c {output_file}")
        
    except Exception as e:
        print(f"✗ Ошибка при сохранении конфигурации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

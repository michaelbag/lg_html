#!/usr/bin/env python3
"""
Генератор конфигурационных файлов для генератора этикеток v2.17
Версия скрипта: 1.1
Версия проекта: 2.17
Поддерживает создание конфигураций для CSV и Excel файлов

Copyright (C) 2025 Michael Bag

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

Автор: Michael Bag
Версия: 1.1
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

def get_user_input(prompt, default=None, input_type=str, choices=None):
    """Получение ввода от пользователя с проверкой типа и выбора"""
    while True:
        if default is not None:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        try:
            user_input = input(full_prompt).strip()
            
            # Если ввод пустой и есть значение по умолчанию
            if not user_input and default is not None:
                return default
            
            # Если ввод пустой и нет значения по умолчанию
            if not user_input:
                print("❌ Поле не может быть пустым. Попробуйте снова.")
                continue
            
            # Проверка выбора из списка
            if choices and user_input not in choices:
                print(f"❌ Выберите один из вариантов: {', '.join(choices)}")
                continue
            
            # Преобразование типа
            if input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input
                
        except ValueError:
            print(f"❌ Введите корректное значение типа {input_type.__name__}")
        except KeyboardInterrupt:
            print("\n\n❌ Отменено пользователем")
            sys.exit(1)


def select_data_file():
    """Выбор файла данных из папки input_data с поддержкой подкаталогов"""
    data_dir = Path("input_data")
    
    if not data_dir.exists():
        print("❌ Папка input_data не найдена")
        return get_user_input("Путь к файлу с данными (CSV или Excel)")
    
    # Ищем файлы данных рекурсивно во всех подкаталогах
    data_files = []
    for ext in ['*.csv', '*.xlsx', '*.xls']:
        data_files.extend(data_dir.rglob(ext))
    
    if not data_files:
        print("❌ В папке input_data не найдено файлов данных")
        return get_user_input("Путь к файлу с данными (CSV или Excel)")
    
    # Сортируем файлы: сначала по папке, потом по имени
    data_files.sort(key=lambda x: (x.parent.name, x.name))
    
    print("\n📁 Доступные файлы данных:")
    print("-" * 50)
    
    current_folder = None
    for i, file_path in enumerate(data_files, 1):
        file_size = file_path.stat().st_size
        size_str = f"{file_size:,} байт" if file_size < 1024 else f"{file_size/1024:.1f} КБ"
        
        # Показываем название папки, если она изменилась
        folder_name = file_path.parent.name
        if folder_name != current_folder:
            if current_folder is not None:
                print()  # Пустая строка между папками
            print(f"📂 {folder_name}/")
            current_folder = folder_name
        
        # Показываем файл с отступом
        relative_path = file_path.relative_to(data_dir)
        print(f"   {i:2d}. {file_path.name} ({size_str})")
    
    print(f"\n{len(data_files) + 1:2d}. Ввести путь вручную")
    
    while True:
        try:
            choice = input(f"\nВыберите файл данных (1-{len(data_files) + 1}): ").strip()
            
            if not choice:
                print("❌ Выберите номер файла")
                continue
            
            choice_num = int(choice)
            
            if choice_num == len(data_files) + 1:
                return get_user_input("Путь к файлу с данными (CSV или Excel)")
            elif 1 <= choice_num <= len(data_files):
                selected_file = data_files[choice_num - 1]
                print(f"✅ Выбран файл: {selected_file}")
                return str(selected_file)
            else:
                print(f"❌ Выберите номер от 1 до {len(data_files) + 1}")
                
        except ValueError:
            print("❌ Введите корректный номер")
        except KeyboardInterrupt:
            print("\n\n❌ Отмена операции")
            sys.exit(0)


def select_template_file():
    """Выбор PDF шаблона из папки input_templates с поддержкой подкаталогов"""
    template_dir = Path("input_templates")
    
    if not template_dir.exists():
        print("❌ Папка input_templates не найдена")
        return get_user_input("Путь к PDF шаблону")
    
    # Ищем PDF файлы рекурсивно во всех подкаталогах
    template_files = list(template_dir.rglob("*.pdf"))
    
    if not template_files:
        print("❌ В папке input_templates не найдено PDF файлов")
        return get_user_input("Путь к PDF шаблону")
    
    # Сортируем файлы: сначала по папке, потом по имени
    template_files.sort(key=lambda x: (x.parent.name, x.name))
    
    print("\n📄 Доступные PDF шаблоны:")
    print("-" * 50)
    
    current_folder = None
    for i, file_path in enumerate(template_files, 1):
        file_size = file_path.stat().st_size
        size_str = f"{file_size:,} байт" if file_size < 1024 else f"{file_size/1024:.1f} КБ"
        
        # Показываем название папки, если она изменилась
        folder_name = file_path.parent.name
        if folder_name != current_folder:
            if current_folder is not None:
                print()  # Пустая строка между папками
            print(f"📂 {folder_name}/")
            current_folder = folder_name
        
        # Показываем файл с отступом
        relative_path = file_path.relative_to(template_dir)
        print(f"   {i:2d}. {file_path.name} ({size_str})")
    
    print(f"\n{len(template_files) + 1:2d}. Ввести путь вручную")
    
    while True:
        try:
            choice = input(f"\nВыберите PDF шаблон (1-{len(template_files) + 1}): ").strip()
            
            if not choice:
                print("❌ Выберите номер файла")
                continue
            
            choice_num = int(choice)
            
            if choice_num == len(template_files) + 1:
                return get_user_input("Путь к PDF шаблону")
            elif 1 <= choice_num <= len(template_files):
                selected_file = template_files[choice_num - 1]
                print(f"✅ Выбран шаблон: {selected_file}")
                return str(selected_file)
            else:
                print(f"❌ Выберите номер от 1 до {len(template_files) + 1}")
                
        except ValueError:
            print("❌ Введите корректный номер")
        except KeyboardInterrupt:
            print("\n\n❌ Отмена операции")
            sys.exit(0)


def interactive_mode():
    """Интерактивный режим создания конфигурации"""
    print("=" * 60)
    print("🔧 ИНТЕРАКТИВНЫЙ РЕЖИМ СОЗДАНИЯ КОНФИГУРАЦИИ")
    print("=" * 60)
    print()
    
    # Основные параметры
    print("📁 ОСНОВНЫЕ ПАРАМЕТРЫ")
    print("-" * 30)
    
    # Выбор файла данных
    print("Выбор файла с данными:")
    data_file = select_data_file()
    
    # Выбор PDF шаблона
    print("\nВыбор PDF шаблона:")
    template_pdf = select_template_file()
    
    # Генерируем имя выходного файла на основе шаблона
    template_path = Path(template_pdf)
    template_name = template_path.stem  # имя файла без расширения
    output_filename = f"{template_name}_result.pdf"
    output_default = f"output/{output_filename}"
    
    output_pdf = get_user_input(
        "Путь к выходному PDF файлу",
        default=output_default
    )
    
    template_type = get_user_input(
        "Тип шаблона (single - один на этикетку, multiple - несколько на странице)",
        default="single",
        choices=["single", "multiple"]
    )
    
    print()
    print("📊 ПАРАМЕТРЫ DATAMATRIX")
    print("-" * 30)
    
    dm_x = get_user_input(
        "Позиция DataMatrix по X (мм) - расстояние от левого края",
        default=10.0,
        input_type=float
    )
    
    dm_y = get_user_input(
        "Позиция DataMatrix по Y (мм) - расстояние от верхнего края",
        default=5.0,
        input_type=float
    )
    
    dm_size = get_user_input(
        "Размер DataMatrix (мм)",
        default=15.0,
        input_type=float
    )
    
    datamatrix_column = get_user_input(
        "Номер столбца с DataMatrix данными (начиная с 0)",
        default=0,
        input_type=int
    )
    
    print()
    print("📝 ПАРАМЕТРЫ ТЕКСТА")
    print("-" * 30)
    
    use_text = get_user_input(
        "Добавить текст на этикетку? (y/n)",
        default="n",
        choices=["y", "n", "yes", "no"]
    ).lower() in ["y", "yes"]
    
    text_column = None
    text_start = 0
    text_length = None
    text_font_size = 12
    text_offset_x = 5.0
    text_offset_y = 0.0
    text_color = "black"
    
    if use_text:
        text_column = get_user_input(
            "Номер столбца с текстом (начиная с 0)",
            input_type=int
        )
        
        text_start = get_user_input(
            "Начальная позиция для извлечения текста",
            default=0,
            input_type=int
        )
        
        text_length = get_user_input(
            "Длина извлекаемого текста (оставьте пустым для всей строки)",
            input_type=int
        )
        
        text_font_size = get_user_input(
            "Размер шрифта текста",
            default=12,
            input_type=int
        )
        
        text_offset_x = get_user_input(
            "Смещение текста по X относительно DataMatrix (мм)",
            default=5.0,
            input_type=float
        )
        
        text_offset_y = get_user_input(
            "Смещение текста по Y относительно DataMatrix (мм)",
            default=0.0,
            input_type=float
        )
        
        text_color = get_user_input(
            "Цвет текста",
            default="black"
        )
    
    # Параметры для multiple шаблона
    labels_horizontal = 2
    labels_vertical = 3
    label_width = 100.0
    label_height = 50.0
    label_margin_left = 10.0
    label_margin_top = 15.0
    label_spacing_horizontal = 5.0
    label_spacing_vertical = 3.0
    
    if template_type == "multiple":
        print()
        print("📐 ПАРАМЕТРЫ MULTIPLE ШАБЛОНА")
        print("-" * 30)
        
        labels_horizontal = get_user_input(
            "Количество этикеток по горизонтали",
            default=2,
            input_type=int
        )
        
        labels_vertical = get_user_input(
            "Количество этикеток по вертикали",
            default=3,
            input_type=int
        )
        
        label_width = get_user_input(
            "Ширина отдельной этикетки (мм)",
            default=100.0,
            input_type=float
        )
        
        label_height = get_user_input(
            "Высота отдельной этикетки (мм)",
            default=50.0,
            input_type=float
        )
        
        label_margin_left = get_user_input(
            "Отступ слева от края страницы (мм)",
            default=10.0,
            input_type=float
        )
        
        label_margin_top = get_user_input(
            "Отступ сверху от края страницы (мм)",
            default=15.0,
            input_type=float
        )
        
        label_spacing_horizontal = get_user_input(
            "Расстояние между этикетками по горизонтали (мм)",
            default=5.0,
            input_type=float
        )
        
        label_spacing_vertical = get_user_input(
            "Расстояние между этикетками по вертикали (мм)",
            default=3.0,
            input_type=float
        )
    
    # Параметры Excel
    excel_sheet = 0
    file_type = detect_file_type(data_file)
    if file_type == "excel":
        print()
        print("📊 ПАРАМЕТРЫ EXCEL")
        print("-" * 30)
        
        excel_sheet = get_user_input(
            "Номер или имя листа Excel (0 для первого листа)",
            default=0
        )
    
    print()
    print("⚙️ ПАРАМЕТРЫ КАЧЕСТВА")
    print("-" * 30)
    
    dpi = get_user_input(
        "DPI для генерации изображений",
        default=300,
        input_type=int
    )
    
    print()
    print("💾 СОХРАНЕНИЕ КОНФИГУРАЦИИ")
    print("-" * 30)
    
    # Генерируем имя файла конфигурации на основе шаблона
    config_filename = f"{template_name}_conf.json"
    config_default = f"conf/{config_filename}"
    
    output_file = get_user_input(
        "Путь к выходному JSON файлу",
        default=config_default
    )
    
    # Создаем конфигурацию
    kwargs = {
        'dm_x': dm_x,
        'dm_y': dm_y,
        'dm_size': dm_size,
        'datamatrix_column': datamatrix_column,
        'text_column': text_column,
        'text_start': text_start,
        'text_length': text_length,
        'text_font_size': text_font_size,
        'text_offset_x': text_offset_x,
        'text_offset_y': text_offset_y,
        'text_color': text_color,
        'excel_sheet': excel_sheet,
        'dpi': dpi
    }
    
    if template_type == 'multiple':
        kwargs.update({
            'labels_horizontal': labels_horizontal,
            'labels_vertical': labels_vertical,
            'label_width': label_width,
            'label_height': label_height,
            'label_margin_left': label_margin_left,
            'label_margin_top': label_margin_top,
            'label_spacing_horizontal': label_spacing_horizontal,
            'label_spacing_vertical': label_spacing_vertical
        })
        config = create_multiple_template_config(data_file, template_pdf, output_pdf, **kwargs)
    else:
        config = create_single_template_config(data_file, template_pdf, output_pdf, **kwargs)
    
    # Сохраняем конфигурацию
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print()
        print("✅ КОНФИГУРАЦИЯ УСПЕШНО СОЗДАНА!")
        print("=" * 50)
        print(f"📄 Файл: {output_file}")
        print(f"📊 Тип шаблона: {template_type}")
        print(f"📁 Файл данных: {data_file}")
        print(f"📄 Шаблон PDF: {template_pdf}")
        print(f"📄 Выходной PDF: {output_pdf}")
        
        if file_type == "excel":
            print(f"📊 Лист Excel: {excel_sheet}")
        
        print()
        print("🚀 ДЛЯ ИСПОЛЬЗОВАНИЯ КОНФИГУРАЦИИ:")
        print(f"   python gen2.py -c {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении конфигурации: {e}")
        sys.exit(1)

def main():
    # Информация о версии и авторе
    __version__ = "1.1"
    __author__ = "Michael BAG"
    __author_email__ = "mk@p7net.ru"
    __author_telegram__ = "https://t.me/michaelbag"
    __description__ = "Генератор конфигурационных файлов для генератора этикеток"
    
    parser = argparse.ArgumentParser(
        description=f"{__description__} v{__version__} (проект v2.17)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Примеры использования:

1. 🔧 ИНТЕРАКТИВНЫЙ РЕЖИМ (рекомендуется для новичков):
   python generate_config.py -i

2. Создание конфигурации для CSV файла (single):
   python generate_config.py data.csv template.pdf output.pdf -t single

3. Создание конфигурации для Excel файла (multiple):
   python generate_config.py data.xlsx template.pdf output.pdf -t multiple -es "Sheet1"

4. Создание конфигурации с настройками (короткие параметры):
   python generate_config.py data.csv template.pdf output.pdf -t single -dx 15 -dy 10 -ds 20

5. Создание конфигурации с текстом и multiple шаблоном:
   python generate_config.py data.csv template.pdf output.pdf -t multiple -lh 3 -lv 4 -tc 2 -tfs 14

6. Создание конфигурации с полными параметрами:
   python generate_config.py data.csv template.pdf output.pdf --type single --dm-x 15 --dm-y 10 --dm-size 20

Автор: {__author__}
E-mail: {__author_email__}
Telegram: {__author_telegram__}
Версия: {__version__}
        """
    )
    
    # Обязательные параметры (необязательны в интерактивном режиме)
    parser.add_argument('data_file', nargs='?', help='Путь к файлу с данными (CSV или Excel)')
    parser.add_argument('template_pdf', nargs='?', help='Путь к PDF шаблону')
    parser.add_argument('output_pdf', nargs='?', help='Путь к выходному PDF файлу')
    
    # Тип шаблона
    parser.add_argument('--type', '-t', choices=['single', 'multiple'],
                       help='Тип шаблона: single (один на этикетку) или multiple (несколько на странице)')
    
    # Параметры DataMatrix
    parser.add_argument('--dm-x', '-dx', type=float, default=10, help='Позиция DataMatrix по X (мм)')
    parser.add_argument('--dm-y', '-dy', type=float, default=5, help='Позиция DataMatrix по Y (мм)')
    parser.add_argument('--dm-size', '-ds', type=float, default=15, help='Размер DataMatrix (мм)')
    parser.add_argument('--datamatrix-column', '-dc', type=int, default=0, help='Номер столбца с DataMatrix данными')
    
    # Параметры текста
    parser.add_argument('--text-column', '-tc', type=int, help='Номер столбца с текстом (опционально)')
    parser.add_argument('--text-start', '-ts', type=int, default=0, help='Начальная позиция текста')
    parser.add_argument('--text-length', '-tl', type=int, help='Длина текста (опционально)')
    parser.add_argument('--text-font-size', '-tfs', type=int, default=12, help='Размер шрифта текста')
    parser.add_argument('--text-offset-x', '-tox', type=float, default=5, help='Смещение текста по X (мм)')
    parser.add_argument('--text-offset-y', '-toy', type=float, default=0, help='Смещение текста по Y (мм)')
    parser.add_argument('--text-color', '-tcl', default='black', help='Цвет текста')
    
    # Параметры для multiple шаблона
    parser.add_argument('--labels-horizontal', '-lh', type=int, default=2, help='Количество этикеток по горизонтали')
    parser.add_argument('--labels-vertical', '-lv', type=int, default=3, help='Количество этикеток по вертикали')
    parser.add_argument('--label-width', '-lw', type=float, default=100, help='Ширина этикетки (мм)')
    parser.add_argument('--label-height', '-lh2', type=float, default=50, help='Высота этикетки (мм)')
    parser.add_argument('--label-margin-left', '-lml', type=float, default=10, help='Отступ слева (мм)')
    parser.add_argument('--label-margin-top', '-lmt', type=float, default=15, help='Отступ сверху (мм)')
    parser.add_argument('--label-spacing-horizontal', '-lsh', type=float, default=5, help='Расстояние по горизонтали (мм)')
    parser.add_argument('--label-spacing-vertical', '-lsv', type=float, default=3, help='Расстояние по вертикали (мм)')
    
    # Параметры Excel
    parser.add_argument('--excel-sheet', '-es', default=0, help='Номер или имя листа Excel (по умолчанию: 0)')
    
    # Качество
    parser.add_argument('--dpi', '-d', type=int, default=300, help='DPI для генерации (по умолчанию: 300)')
    
    # Выходной файл
    parser.add_argument('-o', '--output', help='Путь к выходному JSON файлу (по умолчанию: config.json)')
    
    # Интерактивный режим
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='Запустить интерактивный режим создания конфигурации')
    
    args = parser.parse_args()
    
    # Если запрошен интерактивный режим
    if args.interactive:
        interactive_mode()
        return
    
    # Проверяем обязательные параметры для неинтерактивного режима
    if not args.data_file or not args.template_pdf or not args.output_pdf or not args.type:
        print("❌ Ошибка: В неинтерактивном режиме требуются все обязательные параметры:")
        print("   - data_file (путь к файлу с данными)")
        print("   - template_pdf (путь к PDF шаблону)")
        print("   - output_pdf (путь к выходному PDF файлу)")
        print("   - --type или -t (тип шаблона: single или multiple)")
        print()
        print("💡 Для интерактивного режима используйте: python generate_config.py -i")
        sys.exit(1)
    
    # Выводим информацию о версии и авторе
    print("=" * 60)
    print(f"{__description__} v{__version__}")
    print(f"Автор: {__author__}")
    print(f"Версия проекта: 2.17")
    print("=" * 60)
    print()
    
    # Определяем тип файла данных
    file_type = detect_file_type(args.data_file)
    print(f"Обнаружен тип файла данных: {file_type}")
    
    if file_type == "excel":
        print("⚠️  ВНИМАНИЕ: Excel файл обнаружен")
        print("   Поддержка Excel находится в режиме ТЕСТИРОВАНИЯ и РАЗРАБОТКИ")
        print("   НЕ РЕКОМЕНДУЕТСЯ для производственного использования")
        print("   Требуется дополнить коды специальным символом <gs>")
        print("   Для работы используйте CSV файлы")
        print(f"  Лист Excel: {args.excel_sheet}")
    elif file_type == "csv":
        print("✓ CSV файл обнаружен - рекомендуется для работы")
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

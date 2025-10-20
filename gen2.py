#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор этикеток в многостраничный PDF документ с применением шаблона
Версия 2.9

Поддерживает:
- CSV файлы с разделителем табуляция
- PDF шаблоны (один шаблон на этикетку или несколько этикеток на шаблоне)
- Позиционирование DataMatrix кода по координатам
- Многостраничный PDF документ
- JSON конфигурационные файлы с подробными описаниями параметров

Примеры конфигураций:
- conf/single_template.json - для single шаблона (один шаблон на этикетку)
- conf/multiple_template.json - для multiple шаблона (несколько этикеток на странице)
- conf/complete_example.json - полный пример со всеми параметрами
- conf/c251020_single.json - пример пользовательской конфигурации

Автор: Michael Bag
Версия: 2.9
"""

import argparse
import csv
import os
import sys
import json
import copy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime

# Информация о версии
__version__ = "2.9"
__author__ = "Michael Bag"
__description__ = "Генератор этикеток в многостраничный PDF с шаблонами"

# Попытка импорта библиотек для DataMatrix и PDF
try:
    from pylibdmtx import pylibdmtx
    DATAMATRIX_AVAILABLE = True
    print("Используется pylibdmtx для генерации DataMatrix кодов")
except ImportError:
    try:
        import qrcode
        DATAMATRIX_AVAILABLE = False
        QRCODE_AVAILABLE = True
        print("Внимание: pylibdmtx не установлен, используется QR код вместо DataMatrix")
    except ImportError:
        DATAMATRIX_AVAILABLE = False
        QRCODE_AVAILABLE = False
        print("Ошибка: Не установлены библиотеки для генерации кодов. Установите: pip install pylibdmtx или pip install qrcode[pil]")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import mm
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Внимание: reportlab не установлен, генерация PDF недоступна. Установите: pip install reportlab")

try:
    import PyPDF2
    PDF_TEMPLATE_AVAILABLE = True
except ImportError:
    PDF_TEMPLATE_AVAILABLE = False
    print("Внимание: PyPDF2 не установлен, для работы с PDF шаблонами установите: pip install PyPDF2")


def generate_data_matrix(data, size_pixels):
    """Генерация DataMatrix кода в указанном размере"""
    try:
        if DATAMATRIX_AVAILABLE:
            # Генерируем DataMatrix
            encoded = pylibdmtx.encode(data.encode('utf-8'))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
            
            # Масштабируем до нужного размера с сохранением пропорций
            img.thumbnail(size_pixels, Image.LANCZOS)
            return img
            
        elif QRCODE_AVAILABLE:
            # Создаем QR код как альтернативу
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.thumbnail(size_pixels, Image.LANCZOS)
            return img
            
    except Exception as e:
        print(f"Ошибка при генерации DataMatrix: {e}")
        return None


def extract_text_fragment(text, start_pos, length=None):
    """Извлечение фрагмента текста с заданной позиции и длины"""
    if not text:
        return ""
    
    if start_pos >= len(text):
        return ""
    
    if length is None:
        return text[start_pos:]
    else:
        end_pos = start_pos + length
        return text[start_pos:end_pos]


def setup_directories():
    """Создание необходимых директорий"""
    directories = ['input_data', 'input_templates', 'temp', 'output', 'conf']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Директория {directory}: {'создана' if not Path(directory).exists() else 'существует'}")

def show_config_examples():
    """Отображение информации о доступных примерах конфигураций"""
    print("\n" + "="*60)
    print("ДОСТУПНЫЕ ПРИМЕРЫ КОНФИГУРАЦИЙ:")
    print("="*60)
    
    config_examples = [
        {
            "file": "conf/single_template.json",
            "description": "Для single шаблона (один шаблон на этикетку)",
            "usage": "python gen2.py -c single_template.json"
        },
        {
            "file": "conf/multiple_template.json", 
            "description": "Для multiple шаблона (несколько этикеток на странице)",
            "usage": "python gen2.py -c multiple_template.json"
        },
        {
            "file": "conf/complete_example.json",
            "description": "Полный пример со всеми параметрами и описаниями",
            "usage": "python gen2.py -c complete_example.json"
        },
        {
            "file": "conf/c251020_single.json",
            "description": "Пример пользовательской конфигурации",
            "usage": "python gen2.py -c c251020_single.json"
        }
    ]
    
    for i, config in enumerate(config_examples, 1):
        print(f"\n{i}. {config['file']}")
        print(f"   Описание: {config['description']}")
        print(f"   Использование: {config['usage']}")
        
        # Проверяем существование файла
        if Path(config['file']).exists():
            print(f"   Статус: ✓ Файл существует")
        else:
            print(f"   Статус: ✗ Файл не найден")
    
    print("\n" + "="*60)
    print("ВСЕ КОНФИГУРАЦИОННЫЕ ФАЙЛЫ СОДЕРЖАТ ПОДРОБНЫЕ ОПИСАНИЯ ПАРАМЕТРОВ")
    print("="*60)


def find_input_file(filename, directory='input_data', file_type=None):
    """Поиск файла в указанной директории"""
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return None
    
    # Если filename не указан, ищем первый подходящий файл
    if not filename:
        if file_type == 'csv':
            # Ищем CSV файлы
            for file in directory_path.glob("*.csv"):
                if file.is_file():
                    print(f"Найден CSV файл: {file}")
                    return str(file)
        elif file_type == 'pdf':
            # Ищем PDF файлы
            for file in directory_path.glob("*.pdf"):
                if file.is_file():
                    print(f"Найден PDF файл: {file}")
                    return str(file)
        else:
            # Ищем любые файлы
            for file in directory_path.iterdir():
                if file.is_file():
                    print(f"Найден файл: {file}")
                    return str(file)
        return None
    
    # Если указан полный путь, используем его
    if os.path.isabs(filename) or '/' in filename or '\\' in filename:
        return filename if os.path.exists(filename) else None
    
    # Ищем в указанной директории
    file_path = Path(directory) / filename
    if file_path.exists():
        return str(file_path)
    
    # Ищем файлы с похожими именами
    for file in directory_path.glob(f"*{filename}*"):
        if file.is_file():
            print(f"Найден файл: {file}")
            return str(file)
    
    return None


def load_config(config_file):
    """Загрузка конфигурации из JSON файла"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Загружена конфигурация: {config.get('description', 'Без описания')}")
        return config
        
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации не найден: {config_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка: Неверный формат JSON в файле конфигурации: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
        return None


def find_config_file(config_file):
    """Поиск файла конфигурации"""
    if not config_file:
        return None
    
    # Если указан полный путь, используем его
    if os.path.isabs(config_file) or '/' in config_file or '\\' in config_file:
        return config_file if os.path.exists(config_file) else None
    
    # Ищем в папке conf
    conf_path = Path('conf') / config_file
    if conf_path.exists():
        return str(conf_path)
    
    # Ищем файлы с похожими именами
    conf_dir = Path('conf')
    if conf_dir.exists():
        for file in conf_dir.glob(f"*{config_file}*"):
            if file.is_file() and file.suffix == '.json':
                print(f"Найден файл конфигурации: {file}")
                return str(file)
    
    return None


def get_output_filename(output_pdf, template_type, labels_per_page=None):
    """Генерация имени выходного файла"""
    if output_pdf:
        # Если указан полный путь, используем его
        if os.path.isabs(output_pdf) or '/' in output_pdf or '\\' in output_pdf:
            return output_pdf
        # Иначе помещаем в папку output
        return str(Path('output') / output_pdf)
    
    # Генерируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if template_type == "single":
        filename = f"labels_single_{timestamp}.pdf"
    else:
        if labels_per_page:
            h, v = labels_per_page
            filename = f"labels_multiple_{h}x{v}_{timestamp}.pdf"
        else:
            filename = f"labels_multiple_{timestamp}.pdf"
    
    return str(Path('output') / filename)


def read_csv_data(csv_file, datamatrix_column, text_column=None, text_start=0, text_length=None):
    """Чтение данных из CSV файла с разделителем табуляция"""
    data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for i, row in enumerate(reader):
                if len(row) > datamatrix_column:
                    datamatrix_data = row[datamatrix_column].strip()
                    if datamatrix_data:
                        # Извлекаем текст если указан столбец
                        text_data = ""
                        if text_column is not None and len(row) > text_column:
                            text_data = extract_text_fragment(row[text_column].strip(), text_start, text_length)
                        
                        data.append({
                            'row_number': i + 1,
                            'datamatrix_data': datamatrix_data,
                            'text_data': text_data,
                            'full_row': row
                        })
                else:
                    print(f"Пропуск строки {i+1}: недостаточно столбцов (найдено {len(row)}, требуется {datamatrix_column+1})")
        
        print(f"Прочитано {len(data)} строк с данными для DataMatrix из CSV файла")
        if text_column is not None:
            print(f"Извлечение текста из столбца {text_column}, позиция {text_start}, длина {text_length or 'до конца'}")
        return data
        
    except Exception as e:
        print(f"Ошибка при чтении CSV файла: {e}")
        return []


def get_template_info(template_path):
    """Получение информации о PDF шаблоне"""
    if not PDF_TEMPLATE_AVAILABLE:
        print("Ошибка: PyPDF2 не установлен")
        return None
    
    try:
        template_pdf = PyPDF2.PdfReader(template_path)
        first_page = template_pdf.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)
        
        return {
            'page_width': page_width,
            'page_height': page_height,
            'total_pages': len(template_pdf.pages)
        }
        
    except Exception as e:
        print(f"Ошибка при чтении PDF шаблона: {e}")
        return None


def create_datamatrix_image(datamatrix_data, size_mm, dpi=300):
    """Создание изображения DataMatrix кода в указанном размере в мм"""
    # Конвертируем мм в пиксели
    mm_to_px = dpi / 25.4
    size_px = int(size_mm * mm_to_px)
    
    # Генерируем DataMatrix
    dm_img = generate_data_matrix(datamatrix_data, (size_px, size_px))
    
    if dm_img:
        # Конвертируем в RGBA для поддержки прозрачности
        if dm_img.mode != 'RGBA':
            dm_img = dm_img.convert('RGBA')
        
        # Удаляем белый фон
        dm_img = remove_white_background(dm_img)
        
        return dm_img
    
    return None


def remove_white_background(image):
    """Удаление белого фона с изображения"""
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        data = image.getdata()
        new_data = []
        
        for item in data:
            # Если пиксель белый (или близкий к белому), делаем его прозрачным
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0))  # Прозрачный
            else:
                new_data.append(item)
        
        image.putdata(new_data)
        return image
        
    except Exception as e:
        print(f"Ошибка при удалении белого фона: {e}")
        return image


def generate_multi_page_pdf(csv_data, template_path, template_type, labels_per_page, 
                           dm_x_mm, dm_y_mm, dm_size_mm, output_pdf, dpi=300,
                           label_width_mm=None, label_height_mm=None,
                           label_margin_left_mm=0, label_margin_top_mm=0,
                           label_spacing_horizontal_mm=0, label_spacing_vertical_mm=0,
                           text_font_size=12, text_offset_x_mm=0, text_offset_y_mm=0, text_color='black'):
    """Генерация многостраничного PDF с этикетками"""
    
    if not PDF_AVAILABLE or not PDF_TEMPLATE_AVAILABLE:
        print("Ошибка: Необходимые библиотеки для PDF не установлены")
        return False
    
    try:
        # Получаем информацию о шаблоне
        template_info = get_template_info(template_path)
        if not template_info:
            return False
        
        page_width = template_info['page_width']
        page_height = template_info['page_height']
        
        # Конвертируем координаты из мм в точки (1 mm = 2.83465 points)
        mm_to_pt = 2.83465
        dm_x_pt = dm_x_mm * mm_to_pt
        dm_y_pt = dm_y_mm * mm_to_pt
        dm_size_pt = dm_size_mm * mm_to_pt
        
        # Читаем шаблон
        template_pdf = PyPDF2.PdfReader(template_path)
        
        # Создаем новый PDF
        output = PyPDF2.PdfWriter()
        
        if template_type == "single":
            # Один шаблон на одну этикетку
            for i, data_item in enumerate(csv_data):
                # Создаем DataMatrix изображение
                dm_img = create_datamatrix_image(data_item['datamatrix_data'], dm_size_mm, dpi)
                
                if dm_img:
                    # Создаем временный файл для DataMatrix
                    temp_dm_path = f"temp/temp_dm_{i}.png"
                    dm_img.save(temp_dm_path, 'PNG', dpi=(dpi, dpi))
                    
                    # Создаем PDF страницу с DataMatrix и текстом
                    packet = BytesIO()
                    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    
                    # Добавляем DataMatrix на страницу
                    dm_reader = ImageReader(temp_dm_path)
                    c.drawImage(dm_reader, dm_x_pt, dm_y_pt, 
                               width=dm_size_pt, height=dm_size_pt, mask='auto')
                    
                    # Добавляем текст если есть
                    if data_item.get('text_data'):
                        # Вычисляем позицию текста относительно DataMatrix
                        text_x = dm_x_pt + text_offset_x_mm * mm_to_pt
                        text_y = dm_y_pt + text_offset_y_mm * mm_to_pt
                        
                        # Устанавливаем шрифт и цвет
                        c.setFont("Helvetica", text_font_size)
                        c.setFillColor(text_color)
                        
                        # Добавляем текст
                        c.drawString(text_x, text_y, data_item['text_data'])
                        
                        print(f"Добавлен текст: '{data_item['text_data']}' на позицию ({text_x/mm_to_pt:.1f}, {text_y/mm_to_pt:.1f}) мм")
                    
                    c.save()
                    packet.seek(0)
                    new_pdf = PyPDF2.PdfReader(packet)
                    
                    # Объединяем с шаблоном
                    template_page = template_pdf.pages[0]
                    # Создаем копию страницы шаблона для избежания наложения datamatrix
                    template_page = copy.deepcopy(template_page)
                    template_page.merge_page(new_pdf.pages[0])
                    output.add_page(template_page)
                    
                    # Удаляем временный файл
                    try:
                        os.remove(temp_dm_path)
                    except:
                        pass
                    
                    print(f"Создана страница {i+1} с DataMatrix: {data_item['datamatrix_data'][:20]}...")
                else:
                    print(f"Ошибка создания DataMatrix для строки {data_item['row_number']}")
        
        elif template_type == "multiple":
            # Шаблон с несколькими этикетками
            labels_horizontal, labels_vertical = labels_per_page
            labels_per_page_total = labels_horizontal * labels_vertical
            
            # Вычисляем размеры одной этикетки на шаблоне
            if label_width_mm is not None and label_height_mm is not None:
                # Используем заданные размеры этикеток
                label_width = label_width_mm * mm_to_pt
                label_height = label_height_mm * mm_to_pt
                print(f"Используются заданные размеры этикеток: {label_width_mm}×{label_height_mm} мм")
            else:
                # Автоматически вычисляем размеры на основе размера страницы
                label_width = page_width / labels_horizontal
                label_height = page_height / labels_vertical
                print(f"Автоматически вычислены размеры этикеток: {label_width/mm_to_pt:.1f}×{label_height/mm_to_pt:.1f} мм")
            
            # Вычисляем отступы и расстояния
            margin_left_pt = label_margin_left_mm * mm_to_pt
            margin_top_pt = label_margin_top_mm * mm_to_pt
            spacing_horizontal_pt = label_spacing_horizontal_mm * mm_to_pt
            spacing_vertical_pt = label_spacing_vertical_mm * mm_to_pt
            
            # Вычисляем смещение DataMatrix для каждой этикетки
            dm_offset_x = dm_x_mm * mm_to_pt
            dm_offset_y = dm_y_mm * mm_to_pt
            
            print(f"Отступы: слева={label_margin_left_mm}мм, сверху={label_margin_top_mm}мм")
            print(f"Расстояния: горизонтально={label_spacing_horizontal_mm}мм, вертикально={label_spacing_vertical_mm}мм")
            
            current_page = 0
            current_page_data = []  # Список DataMatrix для текущей страницы
            
            for i, data_item in enumerate(csv_data):
                # Вычисляем позицию этикетки на текущей странице
                position_on_page = i % labels_per_page_total
                label_row = position_on_page // labels_horizontal
                label_col = position_on_page % labels_horizontal
                
                # Вычисляем координаты этикетки с учетом отступов и расстояний
                label_x = margin_left_pt + label_col * (label_width + spacing_horizontal_pt)
                label_y = page_height - margin_top_pt - (label_row + 1) * label_height - label_row * spacing_vertical_pt
                
                # Вычисляем координаты DataMatrix для этой этикетки
                dm_x_final = label_x + dm_offset_x
                dm_y_final = label_y + dm_offset_y
                
                # Создаем DataMatrix изображение
                dm_img = create_datamatrix_image(data_item['datamatrix_data'], dm_size_mm, dpi)
                
                if dm_img:
                    # Создаем временный файл для DataMatrix
                    temp_dm_path = f"temp/temp_dm_{i}.png"
                    dm_img.save(temp_dm_path, 'PNG', dpi=(dpi, dpi))
                    
                    # Добавляем данные в список текущей страницы
                    current_page_data.append({
                        'path': temp_dm_path,
                        'x': dm_x_final,
                        'y': dm_y_final,
                        'row': label_row,
                        'col': label_col,
                        'data': data_item['datamatrix_data'],
                        'text_data': data_item.get('text_data', '')
                    })
                    
                    print(f"Подготовлен DataMatrix на позицию ({label_col+1},{label_row+1}) страницы {current_page+1}: {data_item['datamatrix_data'][:20]}...")
                else:
                    print(f"Ошибка создания DataMatrix для строки {data_item['row_number']}")
                
                # Если страница заполнена или это последний элемент, создаем страницу
                if len(current_page_data) == labels_per_page_total or i == len(csv_data) - 1:
                    # Создаем копию страницы шаблона для избежания наложения datamatrix
                    template_page = template_pdf.pages[current_page % len(template_pdf.pages)]
                    # Создаем глубокую копию страницы шаблона
                    template_page = copy.deepcopy(template_page)
                    
                    # Создаем PDF страницу с DataMatrix
                    packet = BytesIO()
                    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    
                    # Добавляем все DataMatrix и текст на страницу
                    for dm_data in current_page_data:
                        dm_reader = ImageReader(dm_data['path'])
                        c.drawImage(dm_reader, dm_data['x'], dm_data['y'], 
                                   width=dm_size_pt, height=dm_size_pt, mask='auto')
                        
                        # Добавляем текст если есть
                        if dm_data.get('text_data'):
                            # Вычисляем позицию текста относительно DataMatrix
                            text_x = dm_data['x'] + text_offset_x_mm * mm_to_pt
                            text_y = dm_data['y'] + text_offset_y_mm * mm_to_pt
                            
                            # Устанавливаем шрифт и цвет
                            c.setFont("Helvetica", text_font_size)
                            c.setFillColor(text_color)
                            
                            # Добавляем текст
                            c.drawString(text_x, text_y, dm_data['text_data'])
                        
                        # Удаляем временный файл
                        try:
                            os.remove(dm_data['path'])
                        except:
                            pass
                    
                    c.save()
                    packet.seek(0)
                    new_pdf = PyPDF2.PdfReader(packet)
                    
                    # Объединяем с шаблоном
                    template_page.merge_page(new_pdf.pages[0])
                    output.add_page(template_page)
                    
                    print(f"Создана страница {current_page+1} с {len(current_page_data)} этикетками")
                    
                    # Подготавливаемся к следующей странице
                    current_page += 1
                    current_page_data = []
        
        # Сохраняем результат
        with open(output_pdf, "wb") as output_file:
            output.write(output_file)
        
        print(f"Многостраничный PDF создан: {output_pdf}")
        print(f"Всего страниц: {len(output.pages)}")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании многостраничного PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description=f'{__description__} v{__version__}',
        epilog=f'Автор: {__author__} | Версия: {__version__}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Обязательные параметры
    parser.add_argument('csv_file', nargs='?', help='Путь к CSV файлу с данными (разделитель - табуляция). Если не указан, ищется в папке input_data')
    parser.add_argument('template_pdf', nargs='?', help='Путь к PDF шаблону. Если не указан, ищется в папке input_templates')
    parser.add_argument('output_pdf', nargs='?', help='Путь к выходному PDF файлу. Если не указан, создается в папке output')
    
    # Параметры шаблона
    parser.add_argument('-t', '--template-type', choices=['single', 'multiple'], required=False,
                       help='Тип шаблона: single (один шаблон на этикетку) или multiple (несколько этикеток на шаблоне)')
    
    # Параметры для множественного шаблона
    parser.add_argument('-lh', '--labels-horizontal', type=int, default=1,
                       help='Количество этикеток по горизонтали (для template-type=multiple)')
    parser.add_argument('-lv', '--labels-vertical', type=int, default=1,
                       help='Количество этикеток по вертикали (для template-type=multiple)')
    
    # Параметры размеров и отступов для множественного шаблона
    parser.add_argument('-lw', '--label-width', type=float, default=None,
                       help='Ширина отдельной этикетки в мм (для template-type=multiple)')
    parser.add_argument('-lh2', '--label-height', type=float, default=None,
                       help='Высота отдельной этикетки в мм (для template-type=multiple)')
    parser.add_argument('-lml', '--label-margin-left', type=float, default=0,
                       help='Отступ слева от края страницы до первой этикетки в мм')
    parser.add_argument('-lmt', '--label-margin-top', type=float, default=0,
                       help='Отступ сверху от края страницы до первой этикетки в мм')
    parser.add_argument('-lsh', '--label-spacing-horizontal', type=float, default=0,
                       help='Расстояние между этикетками по горизонтали в мм')
    parser.add_argument('-lsv', '--label-spacing-vertical', type=float, default=0,
                       help='Расстояние между этикетками по вертикали в мм')
    
    # Параметры позиционирования DataMatrix
    parser.add_argument('-dx', '--dm-x', type=float, required=False,
                       help='X координата DataMatrix (слева сверху) в мм')
    parser.add_argument('-dy', '--dm-y', type=float, required=False,
                       help='Y координата DataMatrix (слева сверху) в мм')
    parser.add_argument('-ds', '--dm-size', type=float, required=False,
                       help='Размер DataMatrix кода в мм')
    
    # Параметры CSV
    parser.add_argument('-dc', '--datamatrix-column', type=int, default=0,
                       help='Номер столбца CSV файла для DataMatrix (начиная с 0)')
    
    # Параметры текстового поля
    parser.add_argument('-tc', '--text-column', type=int, default=None,
                       help='Номер столбца CSV файла для текста (начиная с 0)')
    parser.add_argument('-ts', '--text-start', type=int, default=0,
                       help='Начальная позиция для извлечения текста (начиная с 0)')
    parser.add_argument('-tl', '--text-length', type=int, default=None,
                       help='Длина извлекаемого текста (если не указано, берется до конца строки)')
    parser.add_argument('-tfs', '--text-font-size', type=int, default=12,
                       help='Размер шрифта для текста в пунктах')
    parser.add_argument('-tox', '--text-offset-x', type=float, default=0,
                       help='Смещение текста по X относительно DataMatrix в мм')
    parser.add_argument('-toy', '--text-offset-y', type=float, default=0,
                       help='Смещение текста по Y относительно DataMatrix в мм')
    parser.add_argument('-tcl', '--text-color', default='black',
                       help='Цвет текста (по умолчанию: black)')
    
    # Дополнительные параметры
    parser.add_argument('-d', '--dpi', type=int, default=300,
                       help='DPI для генерации изображений (по умолчанию: 300)')
    parser.add_argument('-c', '--config', type=str, default=None,
                       help='Путь к файлу конфигурации JSON. Если указан, параметры загружаются из файла')
    parser.add_argument('--show-configs', action='store_true',
                       help='Показать доступные примеры конфигураций и выйти')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Выводим информацию о версии
    print(f"{__description__} v{__version__}")
    print(f"Автор: {__author__}")
    print("-" * 50)
    
    # Обрабатываем аргумент --show-configs
    if args.show_configs:
        show_config_examples()
        sys.exit(0)
    
    # Создаем необходимые директории
    setup_directories()
    
    # Загружаем конфигурацию если указана
    config = None
    if args.config:
        config_file = find_config_file(args.config)
        if config_file:
            config = load_config(config_file)
            if not config:
                sys.exit(1)
        else:
            print(f"Ошибка: Файл конфигурации не найден: {args.config}")
            sys.exit(1)
    
    # Применяем конфигурацию к аргументам
    if config:
        # Сначала сохраняем значения аргументов командной строки
        original_csv_file = args.csv_file
        original_template_pdf = args.template_pdf
        original_output_pdf = args.output_pdf
        
        # Обновляем аргументы значениями из конфигурации
        for key, value in config.items():
            if hasattr(args, key) and key != 'description':
                setattr(args, key, value)
                print(f"Параметр {key}: {value}")
        
        # Восстанавливаем аргументы командной строки если они были указаны
        if original_csv_file is not None:
            args.csv_file = original_csv_file
            print(f"CSV файл из командной строки: {args.csv_file}")
        
        if original_template_pdf is not None:
            args.template_pdf = original_template_pdf
            print(f"PDF шаблон из командной строки: {args.template_pdf}")
        
        if original_output_pdf is not None:
            args.output_pdf = original_output_pdf
            print(f"Выходной PDF из командной строки: {args.output_pdf}")
        
    
    # Проверяем обязательные параметры
    if not args.template_type:
        print("Ошибка: Не указан тип шаблона (-t/--template-type). Укажите параметр или используйте конфигурационный файл (-c/--config)")
        sys.exit(1)
    
    if args.dm_x is None or args.dm_y is None or args.dm_size is None:
        print("Ошибка: Не указаны координаты DataMatrix (-dx, -dy, -ds). Укажите параметры или используйте конфигурационный файл (-c/--config)")
        sys.exit(1)
    
    # Определяем пути к файлам
    csv_file = find_input_file(args.csv_file, 'input_data', 'csv')
    template_pdf = find_input_file(args.template_pdf, 'input_templates', 'pdf')
    
    # Проверяем существование файлов
    if not csv_file:
        print(f"Ошибка: CSV файл не найден: {args.csv_file}")
        print("Поместите CSV файл в папку input_data или укажите полный путь")
        sys.exit(1)
    
    if not template_pdf:
        print(f"Ошибка: PDF шаблон не найден: {args.template_pdf}")
        print("Поместите PDF шаблон в папку input_templates или укажите полный путь")
        sys.exit(1)
    
    print(f"Используется CSV файл: {csv_file}")
    print(f"Используется шаблон: {template_pdf}")
    
    # Проверяем доступность библиотек
    if not PDF_AVAILABLE:
        print("Ошибка: reportlab не установлен. Установите: pip install reportlab")
        sys.exit(1)
    
    if not PDF_TEMPLATE_AVAILABLE:
        print("Ошибка: PyPDF2 не установлен. Установите: pip install PyPDF2")
        sys.exit(1)
    
    if not DATAMATRIX_AVAILABLE and not QRCODE_AVAILABLE:
        print("Ошибка: Не установлены библиотеки для генерации кодов. Установите: pip install pylibdmtx или pip install qrcode[pil]")
        sys.exit(1)
    
    # Читаем данные из CSV
    csv_data = read_csv_data(csv_file, args.datamatrix_column, 
                           args.text_column, args.text_start, args.text_length)
    if not csv_data:
        print("Ошибка: Не удалось прочитать данные из CSV файла")
        sys.exit(1)
    
    # Подготавливаем параметры для множественного шаблона
    labels_per_page = None
    if args.template_type == "multiple":
        labels_per_page = (args.labels_horizontal, args.labels_vertical)
        print(f"Шаблон с {args.labels_horizontal}x{args.labels_vertical} этикетками на странице")
    
    # Определяем имя выходного файла
    output_pdf = get_output_filename(args.output_pdf, args.template_type, labels_per_page)
    print(f"Выходной файл: {output_pdf}")
    
    # Генерируем многостраничный PDF
    success = generate_multi_page_pdf(
        csv_data, template_pdf, args.template_type, labels_per_page,
        args.dm_x, args.dm_y, args.dm_size, output_pdf, args.dpi,
        args.label_width, args.label_height,
        args.label_margin_left, args.label_margin_top,
        args.label_spacing_horizontal, args.label_spacing_vertical,
        args.text_font_size, args.text_offset_x, args.text_offset_y, args.text_color
    )
    
    if success:
        print(f"Успешно создан многостраничный PDF: {output_pdf}")
        print(f"Обработано {len(csv_data)} записей из CSV файла")
    else:
        print("Ошибка при создании PDF файла")
        sys.exit(1)


if __name__ == "__main__":
    main()

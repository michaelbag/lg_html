#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор этикеток в многостраничный PDF документ с применением шаблона
Версия 2.0

Поддерживает:
- CSV файлы с разделителем табуляция
- PDF шаблоны (один шаблон на этикетку или несколько этикеток на шаблоне)
- Позиционирование DataMatrix кода по координатам
- Многостраничный PDF документ

Автор: Michael Bag
Версия: 2.0
"""

import argparse
import csv
import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Информация о версии
__version__ = "2.0"
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


def read_csv_data(csv_file, datamatrix_column):
    """Чтение данных из CSV файла с разделителем табуляция"""
    data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for i, row in enumerate(reader):
                if len(row) > datamatrix_column:
                    datamatrix_data = row[datamatrix_column].strip()
                    if datamatrix_data:
                        data.append({
                            'row_number': i + 1,
                            'datamatrix_data': datamatrix_data,
                            'full_row': row
                        })
                else:
                    print(f"Пропуск строки {i+1}: недостаточно столбцов (найдено {len(row)}, требуется {datamatrix_column+1})")
        
        print(f"Прочитано {len(data)} строк с данными для DataMatrix из CSV файла")
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
                           label_spacing_horizontal_mm=0, label_spacing_vertical_mm=0):
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
                    temp_dm_path = f"temp_dm_{i}.png"
                    dm_img.save(temp_dm_path, 'PNG', dpi=(dpi, dpi))
                    
                    # Создаем PDF страницу с DataMatrix
                    packet = BytesIO()
                    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    
                    # Добавляем DataMatrix на страницу
                    dm_reader = ImageReader(temp_dm_path)
                    c.drawImage(dm_reader, dm_x_pt, dm_y_pt, 
                               width=dm_size_pt, height=dm_size_pt, mask='auto')
                    
                    c.save()
                    packet.seek(0)
                    new_pdf = PyPDF2.PdfReader(packet)
                    
                    # Объединяем с шаблоном
                    template_page = template_pdf.pages[0]
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
                    temp_dm_path = f"temp_dm_{i}.png"
                    dm_img.save(temp_dm_path, 'PNG', dpi=(dpi, dpi))
                    
                    # Добавляем данные в список текущей страницы
                    current_page_data.append({
                        'path': temp_dm_path,
                        'x': dm_x_final,
                        'y': dm_y_final,
                        'row': label_row,
                        'col': label_col,
                        'data': data_item['datamatrix_data']
                    })
                    
                    print(f"Подготовлен DataMatrix на позицию ({label_col+1},{label_row+1}) страницы {current_page+1}: {data_item['datamatrix_data'][:20]}...")
                else:
                    print(f"Ошибка создания DataMatrix для строки {data_item['row_number']}")
                
                # Если страница заполнена или это последний элемент, создаем страницу
                if len(current_page_data) == labels_per_page_total or i == len(csv_data) - 1:
                    # Создаем новую страницу с шаблоном
                    template_page = template_pdf.pages[current_page % len(template_pdf.pages)]
                    
                    # Создаем PDF страницу с DataMatrix
                    packet = BytesIO()
                    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    
                    # Добавляем все DataMatrix на страницу
                    for dm_data in current_page_data:
                        dm_reader = ImageReader(dm_data['path'])
                        c.drawImage(dm_reader, dm_data['x'], dm_data['y'], 
                                   width=dm_size_pt, height=dm_size_pt, mask='auto')
                        
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
    parser.add_argument('csv_file', help='Путь к CSV файлу с данными (разделитель - табуляция)')
    parser.add_argument('template_pdf', help='Путь к PDF шаблону')
    parser.add_argument('output_pdf', help='Путь к выходному PDF файлу')
    
    # Параметры шаблона
    parser.add_argument('--template-type', choices=['single', 'multiple'], required=True,
                       help='Тип шаблона: single (один шаблон на этикетку) или multiple (несколько этикеток на шаблоне)')
    
    # Параметры для множественного шаблона
    parser.add_argument('--labels-horizontal', type=int, default=1,
                       help='Количество этикеток по горизонтали (для template-type=multiple)')
    parser.add_argument('--labels-vertical', type=int, default=1,
                       help='Количество этикеток по вертикали (для template-type=multiple)')
    
    # Параметры размеров и отступов для множественного шаблона
    parser.add_argument('--label-width', type=float, default=None,
                       help='Ширина отдельной этикетки в мм (для template-type=multiple)')
    parser.add_argument('--label-height', type=float, default=None,
                       help='Высота отдельной этикетки в мм (для template-type=multiple)')
    parser.add_argument('--label-margin-left', type=float, default=0,
                       help='Отступ слева от края страницы до первой этикетки в мм')
    parser.add_argument('--label-margin-top', type=float, default=0,
                       help='Отступ сверху от края страницы до первой этикетки в мм')
    parser.add_argument('--label-spacing-horizontal', type=float, default=0,
                       help='Расстояние между этикетками по горизонтали в мм')
    parser.add_argument('--label-spacing-vertical', type=float, default=0,
                       help='Расстояние между этикетками по вертикали в мм')
    
    # Параметры позиционирования DataMatrix
    parser.add_argument('--dm-x', type=float, required=True,
                       help='X координата DataMatrix (слева сверху) в мм')
    parser.add_argument('--dm-y', type=float, required=True,
                       help='Y координата DataMatrix (слева сверху) в мм')
    parser.add_argument('--dm-size', type=float, required=True,
                       help='Размер DataMatrix кода в мм')
    
    # Параметры CSV
    parser.add_argument('--datamatrix-column', type=int, default=0,
                       help='Номер столбца CSV файла для DataMatrix (начиная с 0)')
    
    # Дополнительные параметры
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI для генерации изображений (по умолчанию: 300)')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Выводим информацию о версии
    print(f"{__description__} v{__version__}")
    print(f"Автор: {__author__}")
    print("-" * 50)
    
    # Проверяем существование файлов
    if not os.path.exists(args.csv_file):
        print(f"Ошибка: CSV файл не найден: {args.csv_file}")
        sys.exit(1)
    
    if not os.path.exists(args.template_pdf):
        print(f"Ошибка: PDF шаблон не найден: {args.template_pdf}")
        sys.exit(1)
    
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
    csv_data = read_csv_data(args.csv_file, args.datamatrix_column)
    if not csv_data:
        print("Ошибка: Не удалось прочитать данные из CSV файла")
        sys.exit(1)
    
    # Подготавливаем параметры для множественного шаблона
    labels_per_page = None
    if args.template_type == "multiple":
        labels_per_page = (args.labels_horizontal, args.labels_vertical)
        print(f"Шаблон с {args.labels_horizontal}x{args.labels_vertical} этикетками на странице")
    
    # Создаем выходную директорию если нужно
    output_dir = os.path.dirname(args.output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Генерируем многостраничный PDF
    success = generate_multi_page_pdf(
        csv_data, args.template_pdf, args.template_type, labels_per_page,
        args.dm_x, args.dm_y, args.dm_size, args.output_pdf, args.dpi,
        args.label_width, args.label_height,
        args.label_margin_left, args.label_margin_top,
        args.label_spacing_horizontal, args.label_spacing_vertical
    )
    
    if success:
        print(f"Успешно создан многостраничный PDF: {args.output_pdf}")
        print(f"Обработано {len(csv_data)} записей из CSV файла")
    else:
        print("Ошибка при создании PDF файла")
        sys.exit(1)


if __name__ == "__main__":
    main()

import argparse
import csv
import os
import sys
import json
import configparser
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Информация о версии
__version__ = "1.0.0"
__author__ = "Michael Bag"
__description__ = "Генератор этикеток с DataMatrix/QR кодами для печати"

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
    from io import BytesIO
    PDF_TEMPLATE_AVAILABLE = True
except ImportError:
    PDF_TEMPLATE_AVAILABLE = False
    print("Внимание: PyPDF2 не установлен, для работы с PDF шаблонами установите: pip install PyPDF2")

def load_config(config_file):
    """Загрузка настроек из файла"""
    config = {}
    
    if not os.path.exists(config_file):
        print(f"Файл конфигурации не найден: {config_file}")
        return config
    
    try:
        # Пробуем загрузить как JSON
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.lower().endswith('.json'):
                config = json.load(f)
            else:
                # Пробуем как INI
                parser = configparser.ConfigParser()
                parser.read(config_file, encoding='utf-8')
                
                if 'settings' in parser:
                    for key, value in parser['settings'].items():
                        # Преобразуем типы данных
                        if value.lower() in ('true', 'yes', '1'):
                            config[key] = True
                        elif value.lower() in ('false', 'no', '0'):
                            config[key] = False
                        elif value.isdigit():
                            config[key] = int(value)
                        elif value.replace('.', '').isdigit():
                            config[key] = float(value)
                        else:
                            config[key] = value
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
    
    return config

def merge_args_with_config(args, config):
    """Объединение аргументов командной строки с настройками из файла"""
    # Создаем копию аргументов
    merged = vars(args).copy()
    
    # Маппинг имен параметров между командной строкой и конфигом
    param_mapping = {
        'width': 'width',
        'height': 'height',
        'margin': 'margin',
        'dpi': 'dpi',
        'delimiter': 'delimiter',
        'text_spacing': 'text_spacing',
        'dm_scale': 'dm_scale',
        'eac_image': 'eac_image',
        'eac_height': 'eac_height',
        'no_pdf': 'no_pdf',
        'template': 'template',
        'dm_position': 'dm_position',
        'dm_size': 'dm_size',
        'dm_margin': 'dm_margin',
        'no_eac': 'no_eac',
        'no_product_name': 'no_product_name',
        'text_below_dm': 'text_below_dm',
        'transparent_bg': 'transparent_bg'
    }
    
    # Обновляем значения из конфига, если они не заданы в командной строке
    for config_key, arg_key in param_mapping.items():
        if config_key in config and getattr(args, arg_key) is None:
            # Для булевых значений проверяем, если они явно не заданы
            if isinstance(getattr(args, arg_key), bool) and not getattr(args, arg_key):
                merged[arg_key] = config[config_key]
            elif not isinstance(getattr(args, arg_key), bool):
                merged[arg_key] = config[config_key]
    
    return argparse.Namespace(**merged)

def generate_data_matrix_direct(data, size_pixels):
    """Генерация DataMatrix кода прямо в нужном размере с сохранением пропорций"""
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

def wrap_text(text, max_width, draw, font, max_lines=2):
    """Перенос текста по словам с ограничением по количеству строк"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                # Если достигли максимального количества строк, обрезаем
                if len(lines) >= max_lines:
                    # Обрезаем последнюю строку если нужно
                    if lines:
                        last_line = lines[-1]
                        while last_line and draw.textbbox((0, 0), last_line + "...", font=font)[2] > max_width:
                            last_line = last_line[:-1]
                        lines[-1] = last_line + "..." if last_line else "..."
                    break
            current_line = [word]
    
    if current_line and len(lines) < max_lines:
        lines.append(' '.join(current_line))
    
    return lines

def load_eac_image(eac_path, max_height_px):
    """Загрузка и масштабирование EAC изображения"""
    try:
        if not os.path.exists(eac_path):
            print(f"Предупреждение: Файл EAC не найден: {eac_path}")
            return None
        
        eac_img = Image.open(eac_path)
        
        # Масштабируем по высоте с сохранением пропорций
        original_width, original_height = eac_img.size
        scale_factor = max_height_px / original_height
        new_width = int(original_width * scale_factor)
        new_height = max_height_px
        
        eac_img = eac_img.resize((new_width, new_height), Image.LANCZOS)
        return eac_img
        
    except Exception as e:
        print(f"Ошибка при загрузке EAC изображения: {e}")
        return None

def create_label_page(text_line1, text_line2, data_matrix_data, page_width, page_height, margin, 
                     eac_img=None, dm_scale=1.0, show_eac=True, show_product_name=True, 
                     text_below_dm=False, transparent_bg=False):
    """Создание одной этикетки на странице"""
    # Создаем изображение для страницы (белый фон или прозрачный)
    if transparent_bg:
        img = Image.new('RGBA', (page_width, page_height), (0, 0, 0, 0))  # Прозрачный фон
    else:
        img = Image.new('RGB', (page_width, page_height), 'white')  # Белый фон
    
    draw = ImageDraw.Draw(img)
    
    # Вычисляем доступные области
    text_area_width = page_width // 2 - margin * 2
    qr_area_width = page_width // 2 - margin
    qr_area_height = page_height - 2 * margin
    
    # Генерируем DataMatrix прямо в нужном размере
    dm_img = None
    if data_matrix_data:
        # Вычисляем размер DataMatrix с учетом масштаба
        base_size = min(qr_area_width, qr_area_height)
        dm_size = (int(base_size * dm_scale), int(base_size * dm_scale))
        
        dm_img = generate_data_matrix_direct(data_matrix_data, dm_size)
        
        if dm_img:
            # Конвертируем DataMatrix в RGBA если нужно
            if transparent_bg and dm_img.mode != 'RGBA':
                dm_img = dm_img.convert('RGBA')
            
            # Позиционируем DataMatrix справа по центру
            dm_x = page_width - dm_img.width - margin
            dm_y = (page_height - dm_img.height) // 2
            img.paste(dm_img, (dm_x, dm_y), dm_img if dm_img.mode == 'RGBA' else None)
    
    # Позиция для текста
    text_x = margin
    text_y = margin
    
    # Добавляем EAC изображение слева над текстом если есть и не отключено
    if eac_img and show_eac:
        # Конвертируем EAC в RGBA если нужно
        if transparent_bg and eac_img.mode != 'RGBA':
            eac_img = eac_img.convert('RGBA')
        
        eac_x = margin
        eac_y = margin
        img.paste(eac_img, (eac_x, eac_y), eac_img if eac_img.mode == 'RGBA' else None)
        text_y += eac_img.height + 5  # Отступ между EAC и текстом
    
    # Настройки шрифта для текста
    try:
        # Пробуем использовать стандартные шрифты
        font_size = 20
        font = ImageFont.truetype("Arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
    
    # Цвет текста (черный для белого фона, черный для прозрачного)
    text_color = 'black'
    
    # Текст слева (если не отключено и не перемещено под DataMatrix)
    if not text_below_dm:
        # Первая строка текста (с переносом и ограничением в 2 строки)
        if font and show_product_name and text_line1:
            lines = wrap_text(text_line1, text_area_width, draw, font, max_lines=2)
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                draw.text((text_x, text_y), line, fill=text_color, font=font)
                text_y += line_height + 2
            
            # Добавляем отступ между первой и второй строкой
            text_y += 10
        
        # Вторая строка текста (последние 8 символов после удаления "=")
        if font and text_line2:
            draw.text((text_x, text_y), text_line2, fill=text_color, font=font)
    
    # Текст под DataMatrix (если включена опция)
    if text_below_dm and dm_img and text_line2:
        if font:
            # Вычисляем позицию текста под DataMatrix
            text_below_x = page_width - dm_img.width - margin
            text_below_y = dm_img.height + margin + 5  # Отступ под DataMatrix
            
            # Проверяем, помещается ли текст
            bbox = draw.textbbox((0, 0), text_line2, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Если текст шире DataMatrix, центрируем его относительно DataMatrix
            if text_width > dm_img.width:
                text_below_x = page_width - text_width - margin
            
            draw.text((text_below_x, text_below_y), text_line2, fill=text_color, font=font)
    
    # Резервный вариант без шрифта (если шрифт не загрузился)
    if not font:
        # Текст слева
        if not text_below_dm:
            if show_product_name and text_line1:
                # Обрезаем текст если слишком длинный
                if len(text_line1) > 20:
                    text_line1 = text_line1[:20] + "..."
                draw.text((text_x, text_y), text_line1, fill=text_color)
                text_y += 60
            
            if text_line2:
                draw.text((text_x, text_y), text_line2, fill=text_color)
        
        # Текст под DataMatrix
        if text_below_dm and dm_img and text_line2:
            text_below_x = page_width - dm_img.width - margin
            text_below_y = dm_img.height + margin + 5
            draw.text((text_below_x, text_below_y), text_line2, fill=text_color)
    
    return img

def generate_html_page(image_paths, output_html, page_width, page_height, margin):
    """Генерация HTML файла для печати"""
    css_style = f"""
    <style>
        @page {{
            size: {page_width}mm {page_height}mm;
            margin: {margin}mm;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        .page {{
            width: {page_width}mm;
            height: {page_height}mm;
            page-break-after: always;
            position: relative;
        }}
        .label {{
            width: 100%;
            height: 100%;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
        }}
    </style>
    """
    
    html_content = ["<!DOCTYPE html>", "<html>", "<head>"]
    html_content.append("<meta charset='UTF-8'>")
    html_content.append("<title>Этикетки для печати</title>")
    html_content.append(css_style)
    html_content.append("</head>")
    html_content.append("<body>")
    
    for img_path in image_paths:
        html_content.append("<div class='page'>")
        html_content.append(f"<img class='label' src='{img_path}' alt='Этикетка'>")
        html_content.append("</div>")
    
    html_content.append("</body>")
    html_content.append("</html>")
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))

def generate_pdf_with_image_template(image_paths, output_pdf, template_path, dm_position, dm_size_mm, dm_margin_mm):
    """Генерация PDF с использованием изображения как шаблона с пропорциональным масштабированием"""
    try:
        # Загружаем изображение шаблона
        template_img = Image.open(template_path)
        img_width_px, img_height_px = template_img.size
        
        # Конвертируем пиксели в мм (предполагаем 300 DPI)
        mm_to_px = 300 / 25.4
        page_width_mm = img_width_px / mm_to_px
        page_height_mm = img_height_px / mm_to_px
        
        c = canvas.Canvas(output_pdf, pagesize=(page_width_mm * mm, page_height_mm * mm))
        
        for i, image_path in enumerate(image_paths):
            if i > 0:
                c.showPage()
            
            # Добавляем шаблон на страницу
            template_reader = ImageReader(template_path)
            c.drawImage(template_reader, 0, 0, width=page_width_mm * mm, height=page_height_mm * mm)
            
            # Добавляем DataMatrix на шаблон с пропорциональным масштабированием
            dm_img = Image.open(image_path)
            dm_width_px, dm_height_px = dm_img.size
            
            # Вычисляем пропорциональный размер
            dm_ratio = dm_width_px / dm_height_px
            
            # Используем указанный размер как максимальную сторону
            if dm_ratio >= 1:  # Шире чем высота
                dm_width_final_mm = dm_size_mm
                dm_height_final_mm = dm_size_mm / dm_ratio
            else:  # Выше чем ширина
                dm_height_final_mm = dm_size_mm
                dm_width_final_mm = dm_size_mm * dm_ratio
            
            # Вычисляем позицию DataMatrix
            if dm_position == "bottom-right":
                x = page_width_mm * mm - dm_width_final_mm * mm - dm_margin_mm * mm
                y = dm_margin_mm * mm
            elif dm_position == "bottom-left":
                x = dm_margin_mm * mm
                y = dm_margin_mm * mm
            elif dm_position == "top-right":
                x = page_width_mm * mm - dm_width_final_mm * mm - dm_margin_mm * mm
                y = page_height_mm * mm - dm_height_final_mm * mm - dm_margin_mm * mm
            elif dm_position == "top-left":
                x = dm_margin_mm * mm
                y = page_height_mm * mm - dm_height_final_mm * mm - dm_margin_mm * mm
            else:
                # По умолчанию - правый нижний угол
                x = page_width_mm * mm - dm_width_final_mm * mm - dm_margin_mm * mm
                y = dm_margin_mm * mm
            
            # Создаем временное изображение без белого фона для PDF
            if image_path.endswith('.png'):
                # Для PNG используем оригинальное изображение с прозрачностью
                dm_reader = ImageReader(image_path)
                c.drawImage(dm_reader, x, y, width=dm_width_final_mm * mm, height=dm_height_final_mm * mm, mask='auto')
            else:
                # Для JPEG создаем изображение без белого фона
                dm_img_clean = remove_white_background(dm_img)
                if dm_img_clean:
                    # Сохраняем временное изображение
                    temp_path = f"temp_dm_{i}.png"
                    dm_img_clean.save(temp_path, 'PNG')
                    dm_reader = ImageReader(temp_path)
                    c.drawImage(dm_reader, x, y, width=dm_width_final_mm * mm, height=dm_height_final_mm * mm, mask='auto')
                    # Удаляем временный файл
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                else:
                    # Резервный вариант
                    dm_reader = ImageReader(image_path)
                    c.drawImage(dm_reader, x, y, width=dm_width_final_mm * mm, height=dm_height_final_mm * mm)
            
            print(f"DataMatrix на странице {i+1}: размер {dm_width_final_mm:.1f}x{dm_height_final_mm:.1f} мм, позиция ({x/mm:.1f}, {y/mm:.1f}) мм")
        
        c.save()
        return True
        
    except Exception as e:
        print(f"Ошибка при создании PDF с шаблоном-изображением: {e}")
        return False

def generate_pdf_with_pdf_template(image_paths, output_pdf, template_path, dm_position, dm_size_mm, dm_margin_mm):
    """Генерация PDF с использованием PDF как шаблона с пропорциональным масштабированием"""
    if not PDF_TEMPLATE_AVAILABLE:
        print("Ошибка: PyPDF2 не установлен, для работы с PDF шаблонами установите: pip install PyPDF2")
        return False
    
    try:
        # Читаем PDF шаблон
        template_pdf = PyPDF2.PdfReader(template_path)
        first_page = template_pdf.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)
        
        # Создаем новый PDF
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        for i, image_path in enumerate(image_paths):
            if i > 0:
                c.showPage()
            
            # Загружаем DataMatrix изображение для определения пропорций
            dm_img = Image.open(image_path)
            dm_width_px, dm_height_px = dm_img.size
            
            # Вычисляем пропорциональный размер
            dm_ratio = dm_width_px / dm_height_px
            
            # Конвертируем размер из мм в точки (1 mm = 2.83465 points)
            mm_to_pt = 2.83465
            
            if dm_ratio >= 1:  # Шире чем высота
                dm_width_final_pt = dm_size_mm * mm_to_pt
                dm_height_final_pt = (dm_size_mm * mm_to_pt) / dm_ratio
            else:  # Выше чем ширина
                dm_height_final_pt = dm_size_mm * mm_to_pt
                dm_width_final_pt = (dm_size_mm * mm_to_pt) * dm_ratio
            
            # Конвертируем отступы в точки
            dm_margin_pt = dm_margin_mm * mm_to_pt
            
            # Вычисляем позицию DataMatrix
            if dm_position == "bottom-right":
                x = page_width - dm_width_final_pt - dm_margin_pt
                y = dm_margin_pt
            elif dm_position == "bottom-left":
                x = dm_margin_pt
                y = dm_margin_pt
            elif dm_position == "top-right":
                x = page_width - dm_width_final_pt - dm_margin_pt
                y = page_height - dm_height_final_pt - dm_margin_pt
            elif dm_position == "top-left":
                x = dm_margin_pt
                y = page_height - dm_height_final_pt - dm_margin_pt
            else:
                x = page_width - dm_width_final_pt - dm_margin_pt
                y = dm_margin_pt
            
            # ИСПРАВЛЕНИЕ: Создаем изображение в высоком разрешении для PDF
            # Целевой DPI для PDF - 1200 (в 4 раза выше стандартного) для максимального качества текста
            high_res_dpi = 1200
            mm_to_px_high = high_res_dpi / 25.4
            
            # Размер в пикселях для высокого разрешения
            high_res_width = int(dm_size_mm * mm_to_px_high)
            high_res_height = int(high_res_width / dm_ratio if dm_ratio >= 1 else high_res_width * dm_ratio)
            
            # Масштабируем изображение до высокого разрешения с лучшим качеством
            dm_img_highres = dm_img.resize((high_res_width, high_res_height), Image.Resampling.LANCZOS)
            
            # Создаем временное изображение без белого фона для PDF
            temp_path = f"temp_dm_highres_{i}.png"
            if image_path.endswith('.png'):
                # Для PNG сохраняем масштабированное изображение с прозрачностью
                dm_img_highres.save(temp_path, 'PNG', dpi=(high_res_dpi, high_res_dpi))
            else:
                # Для JPEG создаем изображение без белого фона
                dm_img_clean = remove_white_background(dm_img_highres)
                if dm_img_clean:
                    dm_img_clean.save(temp_path, 'PNG', dpi=(high_res_dpi, high_res_dpi))
                else:
                    dm_img_highres.save(temp_path, 'PNG', dpi=(high_res_dpi, high_res_dpi))
            
            # Вставляем изображение высокого разрешения в PDF
            dm_reader = ImageReader(temp_path)
            c.drawImage(dm_reader, x, y, width=dm_width_final_pt, height=dm_height_final_pt, mask='auto')
            
            # Удаляем временный файл
            try:
                os.remove(temp_path)
            except:
                pass
            
            print(f"DataMatrix на странице {i+1}: размер {dm_width_final_pt/mm_to_pt:.1f}x{dm_height_final_pt/mm_to_pt:.1f} мм, позиция ({x/mm_to_pt:.1f}, {y/mm_to_pt:.1f}) мм, разрешение: {high_res_width}x{high_res_height}px")
        
        c.save()
        
        # Объединяем шаблон с DataMatrix
        packet.seek(0)
        new_pdf = PyPDF2.PdfReader(packet)
        
        output = PyPDF2.PdfWriter()
        
        for i in range(len(new_pdf.pages)):
            # ИСПРАВЛЕНИЕ: Читаем шаблон заново для каждой страницы, чтобы избежать наложения
            # Это критически важно, так как PyPDF2 работает по ссылкам
            template_pdf_fresh = PyPDF2.PdfReader(template_path)
            template_page_idx = i % len(template_pdf_fresh.pages)
            template_page = template_pdf_fresh.pages[template_page_idx]
            
            # Объединяем чистую копию шаблона с DataMatrix
            template_page.merge_page(new_pdf.pages[i])
            output.add_page(template_page)
        
        # Сохраняем результат
        with open(output_pdf, "wb") as output_file:
            output.write(output_file)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при создании PDF с PDF шаблоном: {e}")
        return False

def generate_pdf_simple(image_paths, output_pdf, page_width_mm, page_height_mm, margin_mm):
    """Генерация простого PDF без шаблона"""
    if not PDF_AVAILABLE:
        print("Ошибка: reportlab не установлен, генерация PDF недоступна")
        return False
    
    try:
        c = canvas.Canvas(output_pdf, pagesize=(page_width_mm * mm, page_height_mm * mm))
        
        for i, image_path in enumerate(image_paths):
            if i > 0:
                c.showPage()
            
            img_reader = ImageReader(image_path)
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            available_width = page_width_mm * mm - 2 * margin_mm * mm
            available_height = page_height_mm * mm - 2 * margin_mm * mm
            
            width_ratio = available_width / img_width
            height_ratio = available_height / img_height
            scale = min(width_ratio, height_ratio)
            
            new_width = img_width * scale
            new_height = img_height * scale
            
            x = (page_width_mm * mm - new_width) / 2
            y = (page_height_mm * mm - new_height) / 2
            
            c.drawImage(img_reader, x, y, new_width, new_height)
        
        c.save()
        return True
        
    except Exception as e:
        print(f"Ошибка при создании простого PDF: {e}")
        return False
    
def remove_white_background(image):
    """Удаление белого фона с изображения"""
    try:
        # Конвертируем в RGBA если нужно
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Получаем данные пикселей
        data = image.getdata()
        
        # Создаем новый список пикселей с прозрачностью для белых пикселей
        new_data = []
        for item in data:
            # Если пиксель белый (или близкий к белому), делаем его прозрачным
            if item[0] > 200 and item[1] > 200 and item[2] > 200:  # Порог для белого цвета
                new_data.append((255, 255, 255, 0))  # Прозрачный
            else:
                new_data.append(item)  # Оставляем как есть
        
        # Применяем новые данные
        image.putdata(new_data)
        return image
        
    except Exception as e:
        print(f"Ошибка при удалении белого фона: {e}")
        return None   

def main():
    parser = argparse.ArgumentParser(
        description=f'{__description__} v{__version__}',
        epilog=f'Автор: {__author__} | Версия: {__version__}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('csv_file', help='Путь к CSV файлу')
    parser.add_argument('output_dir', help='Папка для сохранения результатов')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    # Основные параметры с значениями по умолчанию None для возможности переопределения из конфига
    parser.add_argument('--width', type=int, default=None, help='Ширина страницы в мм')
    parser.add_argument('--height', type=int, default=None, help='Высота страницы в мм')
    parser.add_argument('--margin', type=int, default=None, help='Отступ от краев в мм')
    parser.add_argument('--dpi', type=int, default=None, help='DPI для изображений')
    parser.add_argument('--delimiter', default=None, help='Разделитель в CSV файле')
    parser.add_argument('--text-spacing', type=int, default=None, help='Отступ между строками текста в пикселях')
    parser.add_argument('--dm-scale', type=float, default=None, help='Масштаб DataMatrix (1.0 = 100%%, 1.5 = 150%%)')
    parser.add_argument('--eac-image', default=None, help='Путь к файлу EAC изображения')
    parser.add_argument('--eac-height', type=int, default=None, help='Максимальная высота EAC изображения в мм')
    parser.add_argument('--no-pdf', action='store_true', default=None, help='Не создавать PDF файл')
    
    # Параметры для работы с шаблонами
    parser.add_argument('--template', default=None, help='Путь к файлу шаблона (PDF или JPG)')
    parser.add_argument('--dm-position', default=None, 
                       choices=['bottom-right', 'bottom-left', 'top-right', 'top-left'],
                       help='Позиция DataMatrix на шаблоне')
    parser.add_argument('--dm-size', type=float, default=None, help='Размер большей стороны DataMatrix на шаблоне в мм')
    parser.add_argument('--dm-margin', type=float, default=None, help='Отступ DataMatrix от краев шаблона в мм')
    
    # Параметры для управления отображением
    parser.add_argument('--no-eac', action='store_true', default=None, help='Не отображать EAC изображение')
    parser.add_argument('--no-product-name', action='store_true', default=None, help='Не отображать наименование продукта (первая строка)')
    parser.add_argument('--text-below-dm', action='store_true', default=None, help='Размещать вторую строку под DataMatrix вместо левой стороны')
    parser.add_argument('--transparent-bg', action='store_true', default=None, help='Использовать прозрачный фон')
    
    # Новый параметр для файла конфигурации
    parser.add_argument('--config', help='Путь к файлу конфигурации (JSON или INI)')
    
    args = parser.parse_args()
    
    # Выводим информацию о версии при запуске
    print(f"{__description__} v{__version__}")
    print(f"Автор: {__author__}")
    print("-" * 50)
    
    # Загружаем конфигурацию если указан файл
    if args.config:
        config = load_config(args.config)
        if config:
            print(f"Загружена конфигурация из: {args.config}")
            args = merge_args_with_config(args, config)
    
    # Устанавливаем значения по умолчанию для параметров, которые остались None
    defaults = {
        'width': 30,
        'height': 20,
        'margin': 2,
        'dpi': 300,
        'delimiter': '\t',
        'text_spacing': 10,
        'dm_scale': 1.0,
        'eac_image': 'eac.png',
        'eac_height': 5,
        'no_pdf': False,
        'template': None,
        'dm_position': 'bottom-right',
        'dm_size': 15,
        'dm_margin': 2,
        'no_eac': False,
        'no_product_name': False,
        'text_below_dm': False,
        'transparent_bg': False
    }
    
    # Применяем значения по умолчанию
    for key, default_value in defaults.items():
        if getattr(args, key) is None:
            setattr(args, key, default_value)
    
    # Автоматически включаем прозрачный фон если отключены EAC и наименование
    if args.no_eac and args.no_product_name and not args.text_below_dm:
        args.transparent_bg = True
        print("Автоматически включен прозрачный фон (отключены EAC и наименование)")
    
    # Создаем выходную директорию если не существует
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Конвертируем мм в пиксели (для изображений)
    mm_to_px = args.dpi / 25.4
    page_width_px = int(args.width * mm_to_px)
    page_height_px = int(args.height * mm_to_px)
    margin_px = int(args.margin * mm_to_px)
    eac_max_height_px = int(args.eac_height * mm_to_px)
    
    # Загружаем EAC изображение (только если не отключено)
    eac_img = None
    if not args.no_eac:
        eac_img = load_eac_image(args.eac_image, eac_max_height_px)
        if eac_img:
            print(f"EAC изображение загружено: {args.eac_image}")
        else:
            print(f"EAC изображение не найдено или не загружено: {args.eac_image}")
    else:
        print("EAC изображение отключено")
    
    # Читаем CSV файл с указанным разделителем
    try:
        with open(args.csv_file, 'r', encoding='utf-8') as f:
            # Используем csv.reader с указанным разделителем
            reader = csv.reader(f, delimiter=args.delimiter)
            rows = list(reader)
        print(f"Прочитано {len(rows)} строк из CSV файла с разделителем '{args.delimiter}'")
    except Exception as e:
        print(f"Ошибка при чтении CSV файла: {e}")
        sys.exit(1)
    
    generated_images = []
    
    # Обрабатываем каждую строку CSV
    for i, row in enumerate(rows):
        if len(row) < 3:
            print(f"Пропуск строки {i+1}: недостаточно столбцов (найдено {len(row)}, требуется 3)")
            continue
        
        col1 = row[0].strip() if row[0] else ''  # DataMatrix данные
        col3 = row[2].strip() if len(row) > 2 and row[2] else ''  # Текст для первой строки
        
        if not col1:
            print(f"Пропуск строки {i+1}: пустой первый столбец")
            continue
        
        # Создаем текст для второй строки (удаляем "=" и берем последние 8 символов)
        cleaned_col1 = col1.rstrip('=')  # Удаляем символы "=" с конца
        text_line2 = cleaned_col1[-8:] if len(cleaned_col1) >= 8 else cleaned_col1
        
        # Создаем этикетку с новыми параметрами отображения
        label_img = create_label_page(
            col3, text_line2, col1,  # Передаем данные для DataMatrix напрямую
            page_width_px, page_height_px, margin_px, eac_img, args.dm_scale,
            show_eac=not args.no_eac,
            show_product_name=not args.no_product_name,
            text_below_dm=args.text_below_dm,
            transparent_bg=args.transparent_bg
        )
        
        # Сохраняем этикетку
        label_filename = f"label_{i+1:03d}.jpg"
        if args.transparent_bg:
            label_filename = f"label_{i+1:03d}.png"  # PNG для прозрачности

        label_path = Path(args.output_dir) / label_filename
        if args.transparent_bg:
            label_img.save(label_path, 'PNG', dpi=(args.dpi, args.dpi))
        else:
            label_img.save(label_path, 'JPEG', quality=95, dpi=(args.dpi, args.dpi))
        
        generated_images.append(str(label_path))
        
        # Формируем информационное сообщение о настройках
        settings_info = []
        if args.no_eac:
            settings_info.append("без EAC")
        if args.no_product_name:
            settings_info.append("без наименования")
        if args.text_below_dm:
            settings_info.append("текст под DM")
        if args.transparent_bg:
            settings_info.append("прозрачный фон")
        
        settings_str = f" ({', '.join(settings_info)})" if settings_info else ""
        print(f"Создана этикетка {i+1}: {label_filename} (масштаб DataMatrix: {args.dm_scale}{settings_str})")
    
    # Генерируем HTML файл
    if generated_images:
        html_path = Path(args.output_dir) / "labels.html"
        relative_image_paths = [Path(p).name for p in generated_images]
        generate_html_page(
            relative_image_paths, str(html_path), 
            args.width, args.height, args.margin
        )
        print(f"HTML файл создан: {html_path}")
        
        # Генерируем PDF файл если не отключено
        if not args.no_pdf and PDF_AVAILABLE:
            if args.template:
                # PDF с шаблоном
                pdf_path = Path(args.output_dir) / "labels_with_template.pdf"
                
                if args.template.lower().endswith('.pdf'):
                    if PDF_TEMPLATE_AVAILABLE:
                        success = generate_pdf_with_pdf_template(
                            generated_images, str(pdf_path), 
                            args.template, args.dm_position, 
                            args.dm_size, args.dm_margin
                        )
                    else:
                        print("Ошибка: PyPDF2 не установлен, используйте JPG шаблоны или установите: pip install PyPDF2")
                        success = False
                else:
                    success = generate_pdf_with_image_template(
                        generated_images, str(pdf_path), 
                        args.template, args.dm_position, 
                        args.dm_size, args.dm_margin
                    )
                
                if success:
                    print(f"PDF файл с шаблоном создан: {pdf_path}")
                    print(f"DataMatrix позиция: {args.dm_position}, размер большей стороны: {args.dm_size}мм, отступ: {args.dm_margin}мм")
                else:
                    print("Ошибка при создании PDF файла с шаблоном")
            else:
                # Простой PDF
                pdf_path = Path(args.output_dir) / "labels.pdf"
                if generate_pdf_simple(generated_images, str(pdf_path), args.width, args.height, args.margin):
                    print(f"PDF файл создан: {pdf_path}")
                else:
                    print("Ошибка при создании PDF файла")
        elif args.no_pdf:
            print("Создание PDF файла отключено")
        elif not PDF_AVAILABLE:
            print("Генерация PDF недоступна (установите reportlab: pip install reportlab)")
        
        print(f"Всего создано этикеток: {len(generated_images)}")
    else:
        print("Не создано ни одной этикетки")

if __name__ == "__main__":
    main()
    
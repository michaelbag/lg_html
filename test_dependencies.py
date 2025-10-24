#!/usr/bin/env python3
"""
Тест зависимостей для генератора этикеток v2.16
Проверяет все необходимые модули для работы с CSV, Excel, PDF и DataMatrix
"""

import sys
import importlib

def test_module(module_name, description=""):
    """Тестирует импорт модуля"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - {description} (Ошибка: {e})")
        return False

def main():
    print("=" * 60)
    print("Тест зависимостей для генератора этикеток v2.16")
    print("=" * 60)
    print()
    
    # Список модулей для проверки
    modules = [
        ("PIL", "Обработка изображений"),
        ("qrcode", "QR коды"),
        ("pylibdmtx", "DataMatrix коды"),
        ("reportlab", "PDF генерация"),
        ("PyPDF2", "PDF обработка"),
        ("pandas", "Excel поддержка"),
        ("openpyxl", "Excel файлы"),
        ("csv", "CSV обработка (встроенный)"),
        ("json", "JSON конфигурация (встроенный)"),
        ("argparse", "Аргументы командной строки (встроенный)"),
    ]
    
    success_count = 0
    total_count = len(modules)
    
    for module, description in modules:
        if test_module(module, description):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Результат: {success_count}/{total_count} модулей доступны")
    
    if success_count == total_count:
        print("✓ Все зависимости установлены корректно!")
        print("✓ Генератор готов к работе с CSV и Excel файлами")
        return 0
    else:
        print("✗ Некоторые зависимости отсутствуют")
        print("  Установите недостающие модули:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

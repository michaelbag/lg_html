#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования скрипта gen2.py для генерации этикеток

Этот скрипт демонстрирует различные способы использования gen2.py
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Выполнение команды с выводом описания"""
    print(f"\n{'='*60}")
    print(f"Выполнение: {description}")
    print(f"Команда: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка выполнения команды: {e}")
        return False

def main():
    print("Примеры использования gen2.py")
    print("=" * 50)
    
    # Проверяем наличие необходимых файлов
    required_files = ['gen2.py', 'data.csv.example']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Ошибка: Файл {file} не найден")
            return
    
    # Создаем тестовую директорию
    test_dir = Path("test_gen2_output")
    test_dir.mkdir(exist_ok=True)
    
    # Пример 1: Один шаблон на одну этикетку
    print("\nПример 1: Один шаблон на одну этикетку")
    cmd1 = [
        sys.executable, 'gen2.py',
        'data.csv.example',  # CSV файл
        'makets/maket01.pdf',  # PDF шаблон
        str(test_dir / 'output_single.pdf'),  # Выходной PDF
        '--template-type', 'single',
        '--dm-x', '10',  # X координата DataMatrix в мм
        '--dm-y', '5',   # Y координата DataMatrix в мм
        '--dm-size', '15',  # Размер DataMatrix в мм
        '--datamatrix-column', '0'  # Столбец с данными для DataMatrix
    ]
    
    success1 = run_command(cmd1, "Генерация PDF с одним шаблоном на этикетку")
    
    # Пример 2: Шаблон с несколькими этикетками (2x2)
    print("\nПример 2: Шаблон с несколькими этикетками (2x2)")
    cmd2 = [
        sys.executable, 'gen2.py',
        'data.csv.example',
        'makets/maket01.pdf',
        str(test_dir / 'output_multiple_2x2.pdf'),
        '--template-type', 'multiple',
        '--labels-horizontal', '2',
        '--labels-vertical', '2',
        '--dm-x', '5',
        '--dm-y', '3',
        '--dm-size', '12',
        '--datamatrix-column', '0'
    ]
    
    success2 = run_command(cmd2, "Генерация PDF с шаблоном 2x2")
    
    # Пример 3: Шаблон с несколькими этикетками (3x1)
    print("\nПример 3: Шаблон с несколькими этикетками (3x1)")
    cmd3 = [
        sys.executable, 'gen2.py',
        'data.csv.example',
        'makets/maket01.pdf',
        str(test_dir / 'output_multiple_3x1.pdf'),
        '--template-type', 'multiple',
        '--labels-horizontal', '3',
        '--labels-vertical', '1',
        '--dm-x', '8',
        '--dm-y', '2',
        '--dm-size', '10',
        '--datamatrix-column', '0',
        '--dpi', '600'  # Высокое разрешение
    ]
    
    success3 = run_command(cmd3, "Генерация PDF с шаблоном 3x1 (высокое разрешение)")
    
    # Пример 4: Использование другого столбца для DataMatrix
    print("\nПример 4: Использование второго столбца для DataMatrix")
    cmd4 = [
        sys.executable, 'gen2.py',
        'data.csv.example',
        'makets/maket01.pdf',
        str(test_dir / 'output_column1.pdf'),
        '--template-type', 'single',
        '--dm-x', '15',
        '--dm-y', '8',
        '--dm-size', '18',
        '--datamatrix-column', '1'  # Второй столбец
    ]
    
    success4 = run_command(cmd4, "Генерация PDF с данными из второго столбца")
    
    # Пример 5: Множественный шаблон с заданными размерами и отступами
    print("\nПример 5: Множественный шаблон с заданными размерами и отступами")
    cmd5 = [
        sys.executable, 'gen2.py',
        'data.csv.example',
        'makets/multi_maket.pdf',
        str(test_dir / 'output_custom_sizes.pdf'),
        '--template-type', 'multiple',
        '--labels-horizontal', '3',
        '--labels-vertical', '6',
        '--label-width', '50',
        '--label-height', '30',
        '--label-margin-left', '10',
        '--label-margin-top', '15',
        '--label-spacing-horizontal', '5',
        '--label-spacing-vertical', '3',
        '--dm-x', '5',
        '--dm-y', '3',
        '--dm-size', '12',
        '--datamatrix-column', '0'
    ]
    
    success5 = run_command(cmd5, "Генерация PDF с заданными размерами этикеток")
    
    # Выводим результаты
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    results = [
        ("Один шаблон на этикетку", success1),
        ("Шаблон 2x2", success2),
        ("Шаблон 3x1", success3),
        ("Второй столбец", success4),
        ("Заданные размеры этикеток", success5)
    ]
    
    for test_name, success in results:
        status = "✓ УСПЕШНО" if success else "✗ ОШИБКА"
        print(f"{test_name:25} : {status}")
    
    # Проверяем созданные файлы
    print(f"\nСозданные файлы в директории {test_dir}:")
    for file in test_dir.glob("*.pdf"):
        size = file.stat().st_size
        print(f"  {file.name} ({size:,} байт)")
    
    print(f"\nТестирование завершено. Проверьте файлы в директории: {test_dir}")

if __name__ == "__main__":
    main()

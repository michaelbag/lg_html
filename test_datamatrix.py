#!/usr/bin/env python3
"""
Скрипт диагностики DataMatrix на Windows
Проверяет все возможные варианты установки и работы с DataMatrix
"""

import sys
import platform
import subprocess
import importlib.util

def print_header():
    print("=" * 60)
    print("🔍 ДИАГНОСТИКА DATAMATRIX НА WINDOWS")
    print("=" * 60)
    print(f"ОС: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.machine()}")
    print(f"Python: {sys.version}")
    print("-" * 60)

def check_python_version():
    """Проверка версии Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - подходит")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - требуется Python 3.8+")
        return False

def check_pip():
    """Проверка pip"""
    print("\n📦 Проверка pip...")
    try:
        import pip
        print(f"✅ pip {pip.__version__} установлен")
        return True
    except ImportError:
        print("❌ pip не найден")
        return False

def check_conda():
    """Проверка conda"""
    print("\n🐍 Проверка conda...")
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ conda не найден")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ conda не найден")
        return False

def check_pylibdmtx():
    """Проверка pylibdmtx"""
    print("\n🔢 Проверка pylibdmtx...")
    try:
        import pylibdmtx
        print("✅ pylibdmtx импортирован успешно")
        
        # Тест генерации
        try:
            encoded = pylibdmtx.encode(b'test_data')
            print("✅ DataMatrix генерация работает")
            return True
        except Exception as e:
            print(f"❌ Ошибка генерации DataMatrix: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ pylibdmtx не установлен: {e}")
        return False

def check_qrcode():
    """Проверка qrcode (fallback)"""
    print("\n📱 Проверка qrcode (fallback)...")
    try:
        import qrcode
        print("✅ qrcode установлен")
        
        # Тест генерации
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data('test')
            qr.make(fit=True)
            print("✅ QR код генерация работает")
            return True
        except Exception as e:
            print(f"❌ Ошибка генерации QR: {e}")
            return False
            
    except ImportError:
        print("❌ qrcode не установлен")
        return False

def check_other_dependencies():
    """Проверка других зависимостей"""
    print("\n📚 Проверка других зависимостей...")
    
    dependencies = [
        ('PIL', 'Pillow'),
        ('reportlab', 'reportlab'),
        ('PyPDF2', 'PyPDF2')
    ]
    
    results = {}
    for module, name in dependencies:
        try:
            importlib.import_module(module)
            print(f"✅ {name} установлен")
            results[name] = True
        except ImportError:
            print(f"❌ {name} не установлен")
            results[name] = False
    
    return results

def suggest_solutions():
    """Предложения по решению проблем"""
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("-" * 40)
    
    print("\n🥇 ЛУЧШИЙ ВАРИАНТ - Anaconda/Miniconda:")
    print("1. Скачайте Anaconda с https://anaconda.com/download")
    print("2. Создайте окружение: conda create -n labelgen python=3.9")
    print("3. Активируйте: conda activate labelgen")
    print("4. Установите: conda install -c conda-forge pylibdmtx")
    
    print("\n🥈 АЛЬТЕРНАТИВА - pip + Visual Studio Build Tools:")
    print("1. Установите Visual Studio Build Tools")
    print("2. pip install pylibdmtx")
    
    print("\n🥉 ПРОСТОЙ ВАРИАНТ - только QR коды:")
    print("1. pip install -r requirements-minimal.txt")
    print("2. Скрипт автоматически переключится на QR коды")
    
    print("\n📋 Подробные инструкции:")
    print("- INSTALL_WINDOWS.md - общая установка")
    print("- DATAMATRIX_WINDOWS.md - специально для DataMatrix")

def test_main_script():
    """Тест основного скрипта"""
    print("\n🧪 Тест основного скрипта...")
    try:
        # Создаем тестовый CSV
        with open('test_diagnostic.csv', 'w', encoding='utf-8') as f:
            f.write("01046000000000121=ABC1234567890\tИгнорируется\tТестовый продукт\n")
        
        # Запускаем скрипт
        result = subprocess.run([
            sys.executable, 'main.py', 'test_diagnostic.csv', 'test_output'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Основной скрипт работает")
            if "pylibdmtx" in result.stdout:
                print("✅ Используется DataMatrix")
            elif "QR код" in result.stdout:
                print("⚠️ Используется QR код (fallback)")
        else:
            print(f"❌ Ошибка в основном скрипте: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут при тестировании скрипта")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
    finally:
        # Очистка
        import os
        try:
            os.remove('test_diagnostic.csv')
            import shutil
            shutil.rmtree('test_output', ignore_errors=True)
        except:
            pass

def main():
    print_header()
    
    # Проверки
    python_ok = check_python_version()
    pip_ok = check_pip()
    conda_ok = check_conda()
    pylibdmtx_ok = check_pylibdmtx()
    qrcode_ok = check_qrcode()
    other_deps = check_other_dependencies()
    
    # Тест основного скрипта
    test_main_script()
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ДИАГНОСТИКИ:")
    print("=" * 60)
    
    if pylibdmtx_ok:
        print("🎉 ОТЛИЧНО! DataMatrix полностью работает")
    elif qrcode_ok:
        print("✅ ХОРОШО! QR коды работают (DataMatrix недоступен)")
    else:
        print("❌ ПРОБЛЕМА! Нужна установка зависимостей")
    
    if not any(other_deps.values()):
        print("⚠️ ВНИМАНИЕ! Отсутствуют другие зависимости")
    
    # Рекомендации
    suggest_solutions()
    
    print("\n" + "=" * 60)
    print("Диагностика завершена!")
    print("=" * 60)

if __name__ == "__main__":
    main()

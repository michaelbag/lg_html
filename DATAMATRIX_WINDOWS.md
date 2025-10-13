# Установка DataMatrix на Windows 10/11

## Обзор проблемы

`pylibdmtx` - это Python обертка для библиотеки `libdmtx`, которая требует системные зависимости. На Windows это создает дополнительные сложности.

## Методы установки

### 🥇 Метод 1: Через Anaconda/Miniconda (РЕКОМЕНДУЕТСЯ)

**Преимущества:**
- ✅ Автоматически устанавливает все системные зависимости
- ✅ Предкомпилированные пакеты
- ✅ Не требует Visual Studio Build Tools
- ✅ Работает "из коробки"

**Установка:**
```cmd
# 1. Установите Anaconda или Miniconda
# Скачайте с https://anaconda.com/download

# 2. Создайте виртуальное окружение
conda create -n labelgen python=3.9
conda activate labelgen

# 3. Установите все зависимости
conda install -c conda-forge pillow reportlab pypdf2 qrcode
conda install -c conda-forge pylibdmtx

# 4. Проверьте установку
python -c "from pylibdmtx import pylibdmtx; print('DataMatrix работает!')"
```

### 🥈 Метод 2: Через pip + Visual Studio Build Tools

**Требования:**
- Visual Studio Build Tools 2019 или новее
- Windows SDK

**Установка:**
```cmd
# 1. Установите Visual Studio Build Tools
# Скачайте с https://visualstudio.microsoft.com/downloads/
# Выберите "C++ build tools"

# 2. Установите зависимости
pip install --upgrade pip setuptools wheel
pip install pylibdmtx

# 3. Если ошибка, попробуйте:
pip install --only-binary=all pylibdmtx
```

### 🥉 Метод 3: Предкомпилированные wheel файлы

**Для Python 3.8-3.11:**
```cmd
# Скачайте wheel файл с https://www.lfd.uci.edu/~gohlke/pythonlibs/#pylibdmtx
# Выберите подходящую версию для вашего Python

# Установите wheel
pip install pylibdmtx-0.1.9-cp39-cp39-win_amd64.whl
```

### 🔄 Метод 4: Fallback на QR коды

**Если DataMatrix не работает:**
```cmd
# Установите только QR коды
pip install -r requirements-minimal.txt

# Скрипт автоматически переключится на QR коды
```

## Пошаговая диагностика

### Шаг 1: Проверка Python
```cmd
python --version
# Должно быть Python 3.8 или новее
```

### Шаг 2: Проверка pip
```cmd
pip --version
pip install --upgrade pip
```

### Шаг 3: Тест установки pylibdmtx
```cmd
python -c "
try:
    from pylibdmtx import pylibdmtx
    print('✅ pylibdmtx установлен успешно')
    
    # Тест генерации
    encoded = pylibdmtx.encode(b'test')
    print('✅ DataMatrix генерация работает')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
except Exception as e:
    print(f'❌ Ошибка генерации: {e}')
"
```

### Шаг 4: Тест в скрипте
```cmd
python main.py --version
# Должно показать: "Используется pylibdmtx для генерации DataMatrix кодов"
```

## Решение проблем

### Ошибка: "Microsoft Visual C++ 14.0 is required"

**Решение:**
```cmd
# Установите Visual Studio Build Tools
# Или используйте conda:
conda install -c conda-forge pylibdmtx
```

### Ошибка: "libdmtx not found"

**Решение:**
```cmd
# Установите системные библиотеки через conda
conda install -c conda-forge libdmtx

# Или используйте предкомпилированные wheel
pip install pylibdmtx --only-binary=all
```

### Ошибка: "No module named 'pylibdmtx'"

**Решение:**
```cmd
# Проверьте виртуальное окружение
conda activate labelgen  # или ваше окружение

# Переустановите
pip uninstall pylibdmtx
pip install pylibdmtx
```

### Ошибка при компиляции

**Решение:**
```cmd
# Установите все необходимые инструменты
conda install -c conda-forge gcc_win-64 gxx_win-64

# Или используйте conda для установки
conda install -c conda-forge pylibdmtx
```

## Альтернативные решения

### 1. Использование Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libdmtx0a libdmtx-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### 2. Использование WSL2
```bash
# В WSL2 (Ubuntu)
sudo apt-get update
sudo apt-get install libdmtx0a libdmtx-dev
pip install pylibdmtx
```

### 3. Использование альтернативных библиотек

**qrcode (всегда работает):**
```python
import qrcode
# Автоматический fallback в скрипте
```

**python-barcode:**
```cmd
pip install python-barcode[images]
```

## Проверка работоспособности

### Полный тест скрипта
```cmd
# Создайте тестовый CSV
echo 01046000000000121=ABC1234567890,Игнорируется,Тестовый продукт > test.csv

# Запустите скрипт
python main.py test.csv output_test

# Проверьте результат
dir output_test
```

### Ожидаемый вывод при успешной установке DataMatrix:
```
Генератор этикеток с DataMatrix/QR кодами для печати v1.0.0
Автор: Michael Bag
--------------------------------------------------
Используется pylibdmtx для генерации DataMatrix кодов
EAC изображение не найдено или не загружено: eac.png
Прочитано 1 строк из CSV файла с разделителем '	'
Создана этикетка 1: label_001.jpg (масштаб DataMatrix: 1.0)
HTML файл создан: output_test/labels.html
PDF файл создан: output_test/labels.pdf
Всего создано этикеток: 1
```

### Ожидаемый вывод при fallback на QR:
```
Генератор этикеток с DataMatrix/QR кодами для печати v1.0.0
Автор: Michael Bag
--------------------------------------------------
Внимание: pylibdmtx не установлен, используется QR код вместо DataMatrix
```

## Рекомендации

1. **Для разработки:** Используйте Anaconda/Miniconda
2. **Для продакшена:** Используйте Docker или предкомпилированные wheel
3. **Для простоты:** Используйте QR коды (всегда работают)
4. **Для максимальной совместимости:** Создайте несколько вариантов установки

## Заключение

DataMatrix на Windows требует дополнительных настроек, но при правильной установке работает отлично. Рекомендуется использовать conda для простоты или иметь fallback на QR коды для максимальной совместимости.

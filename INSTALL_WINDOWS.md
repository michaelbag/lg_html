# Установка на Windows 10/11

## Быстрая установка

### 1. Установка Python
```cmd
# Скачайте Python с https://python.org
# Убедитесь что отмечена опция "Add Python to PATH"
```

### 2. Установка зависимостей
```cmd
# Откройте командную строку (cmd) или PowerShell
pip install -r requirements.txt
```

### 3. Установка системных библиотек для DataMatrix

#### Вариант A: Через conda (рекомендуется)
```cmd
# Установите Anaconda или Miniconda
conda install -c conda-forge pylibdmtx
```

#### Вариант B: Через pip (может не работать)
```cmd
pip install pylibdmtx
```

#### Вариант C: Только QR коды (если DataMatrix не работает)
```cmd
pip install -r requirements-minimal.txt
```

## Проверка установки

### Быстрая проверка
```cmd
python main.py --version
```

### Полная диагностика DataMatrix
```cmd
python test_datamatrix.py
```

Этот скрипт проверит:
- ✅ Версию Python
- ✅ Наличие pip и conda
- ✅ Установку pylibdmtx
- ✅ Работу DataMatrix генерации
- ✅ Fallback на QR коды
- ✅ Все остальные зависимости

### Ожидаемый вывод при успешной установке:
```
Генератор этикеток с DataMatrix/QR кодами для печати v1.0.0
Автор: Michael Bag
```

## Тестирование

```cmd
# Создайте тестовый CSV файл
echo 01046000000000121=ABC1234567890,Игнорируется,Тестовый продукт > test.csv

# Запустите генератор
python main.py test.csv output_test
```

## Решение проблем

### Ошибка "Microsoft Visual C++ 14.0 is required"
```cmd
# Установите Visual Studio Build Tools
# Или используйте conda вместо pip
conda install -c conda-forge pylibdmtx
```

### Ошибка "libdmtx not found"
```cmd
# DataMatrix недоступен, но QR коды работают
# Скрипт автоматически переключится на QR коды
```

### Проблемы с шрифтами
- Скрипт автоматически найдет Arial в `C:/Windows/Fonts/`
- Если Arial не найден, будет использован системный шрифт по умолчанию

### Проблемы с путями
- Используйте прямые слеши `/` или двойные обратные `\\`
- Избегайте пробелов в путях к файлам

## Примеры использования

### Базовое использование
```cmd
python main.py data.csv output_folder
```

### С конфигурацией
```cmd
python main.py data.csv output_folder --config config.json
```

### Только QR коды (без DataMatrix)
```cmd
python main.py data.csv output_folder --no-pdf
```

## Альтернативные способы установки

### 1. Через Anaconda (рекомендуется для Windows)
```cmd
# Создайте виртуальное окружение
conda create -n labelgen python=3.9
conda activate labelgen

# Установите зависимости
conda install -c conda-forge pillow reportlab pypdf2 qrcode
conda install -c conda-forge pylibdmtx  # Для DataMatrix
```

### 2. Через Chocolatey
```cmd
# Установите Chocolatey, затем:
choco install python
pip install -r requirements.txt
```

### 3. Через Scoop
```cmd
# Установите Scoop, затем:
scoop install python
pip install -r requirements.txt
```

## Производительность на Windows

- **SSD рекомендуется** для быстрой работы с изображениями
- **8GB RAM минимум** для больших объемов данных
- **Антивирус** может замедлять работу - добавьте папку проекта в исключения

## Поддержка Windows-специфичных функций

- ✅ **Длинные пути** (>260 символов) - поддерживаются
- ✅ **Unicode имена файлов** - поддерживаются
- ✅ **Различные разделители** в CSV - поддерживаются
- ✅ **Сетевые пути** (UNC) - поддерживаются

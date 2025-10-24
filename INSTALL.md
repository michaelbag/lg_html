# Установка зависимостей для генератора этикеток

## Быстрая установка

```bash
# Установка всех зависимостей
pip install -r requirements.txt
```

## Минимальная установка

```bash
# Только базовые функции (изображения + QR коды)
pip install -r requirements-minimal.txt
```

## Установка по компонентам

### 1. Основные зависимости
```bash
pip install Pillow>=9.0.0
```

### 2. DataMatrix коды (рекомендуется)
```bash
pip install pylibdmtx>=0.1.9
```

### 3. QR коды (альтернатива)
```bash
pip install qrcode[pil]>=7.3.1
```

### 4. PDF генерация
```bash
pip install reportlab>=4.0.0
```

### 5. PDF шаблоны
```bash
pip install PyPDF2>=3.0.0
```

### 6. Excel поддержка (новое в v2.16)
```bash
pip install pandas>=2.0.0 openpyxl>=3.1.0
```

## Системные зависимости для pylibdmtx

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libdmtx0a libdmtx-dev
```

### macOS
```bash
brew install libdmtx
```

### Windows 10/11
- **Рекомендуется:** `conda install -c conda-forge pylibdmtx`
- **Альтернатива:** `pip install pylibdmtx` (может требовать Visual Studio Build Tools)
- **Fallback:** Используйте только QR коды с `requirements-minimal.txt`

> 📋 **Подробные инструкции для Windows:** см. [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

## Проверка установки

```bash
python -c "
try:
    from pylibdmtx import pylibdmtx
    print('✓ pylibdmtx установлен')
except ImportError:
    print('✗ pylibdmtx не установлен')

try:
    import qrcode
    print('✓ qrcode установлен')
except ImportError:
    print('✗ qrcode не установлен')

try:
    from reportlab.pdfgen import canvas
    print('✓ reportlab установлен')
except ImportError:
    print('✗ reportlab не установлен')

try:
    import PyPDF2
    print('✓ PyPDF2 установлен')
except ImportError:
    print('✗ PyPDF2 не установлен')

try:
    import pandas
    print('✓ pandas установлен (Excel поддержка)')
except ImportError:
    print('✗ pandas не установлен (Excel поддержка недоступна)')

try:
    import openpyxl
    print('✓ openpyxl установлен (Excel поддержка)')
except ImportError:
    print('✗ openpyxl не установлен (Excel поддержка недоступна)')
"
```

## Решение проблем

### Ошибка "libdmtx not found"
- Установите системные зависимости (см. выше)
- На macOS: `brew install libdmtx`
- На Ubuntu: `sudo apt-get install libdmtx-dev`

### Ошибка с шрифтами
- Скрипт автоматически использует системные шрифты
- Для кастомных шрифтов поместите .ttf файлы в папку со скриптом

### Проблемы с PDF
- Убедитесь что установлен reportlab
- Проверьте права на запись в выходную папку

### Проблемы с Excel файлами
- Убедитесь что установлены pandas и openpyxl
- Проверьте что Excel файл не поврежден
- Для больших Excel файлов может потребоваться больше памяти

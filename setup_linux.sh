#!/bin/bash
# Скрипт инициализации проекта lg_html для Linux
# Автор: Michael BAG
# Версия: 1.0

set -e  # Выход при ошибке

echo "========================================"
echo "Инициализация проекта lg_html для Linux"
echo "========================================"
echo

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден в системе!"
    echo "Установите Python 3.7+ используя пакетный менеджер вашего дистрибутива:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo "✓ Python найден"
python3 --version

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "ОШИБКА: pip3 не найден!"
    echo "Установите pip3:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    echo "  Fedora: sudo dnf install python3-pip"
    exit 1
fi

echo "✓ pip3 найден"

# Создание виртуального окружения
echo
echo "Создание виртуального окружения..."
python3 -m venv venv
echo "✓ Виртуальное окружение создано"

# Активация виртуального окружения
echo
echo "Активация виртуального окружения..."
source venv/bin/activate
echo "✓ Виртуальное окружение активировано"

# Обновление pip
echo
echo "Обновление pip..."
python -m pip install --upgrade pip || echo "ПРЕДУПРЕЖДЕНИЕ: Не удалось обновить pip, продолжаем..."

# Установка системных зависимостей для pylibdmtx
echo
echo "Установка системных зависимостей..."
if command -v apt-get &> /dev/null; then
    echo "Обнаружен apt, устанавливаем системные зависимости..."
    sudo apt-get update
    sudo apt-get install -y libdmtx-dev libdmtx0a
elif command -v yum &> /dev/null; then
    echo "Обнаружен yum, устанавливаем системные зависимости..."
    sudo yum install -y libdmtx-devel
elif command -v dnf &> /dev/null; then
    echo "Обнаружен dnf, устанавливаем системные зависимости..."
    sudo dnf install -y libdmtx-devel
else
    echo "ПРЕДУПРЕЖДЕНИЕ: Неизвестный пакетный менеджер, пропускаем установку системных зависимостей"
    echo "Установите libdmtx вручную для работы с DataMatrix кодами"
fi

# Установка зависимостей Python
echo
echo "Установка зависимостей Python..."
pip install -r requirements.txt
echo "✓ Зависимости установлены"

# Создание необходимых папок
echo
echo "Создание структуры папок..."
mkdir -p input_data input_templates output temp conf
echo "✓ Структура папок создана"

# Проверка установки
echo
echo "Проверка установки..."
python -c "import pylibdmtx, qrcode, reportlab, PyPDF2, PIL; print('✓ Все модули импортированы успешно')" || echo "ПРЕДУПРЕЖДЕНИЕ: Некоторые модули не импортированы корректно"

echo
echo "========================================"
echo "Инициализация завершена успешно!"
echo "========================================"
echo
echo "Для активации виртуального окружения в будущем используйте:"
echo "  source venv/bin/activate"
echo
echo "Для запуска генератора используйте:"
echo "  python gen2.py --help"
echo
echo "Документация доступна в README.md"
echo

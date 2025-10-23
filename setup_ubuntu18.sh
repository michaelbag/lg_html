#!/bin/bash
# Скрипт инициализации проекта lg_html для Ubuntu Server 18.04
# Автор: Michael BAG
# Версия: 1.0

set -e  # Выход при ошибке

echo "========================================"
echo "Инициализация проекта lg_html для Ubuntu Server 18.04"
echo "========================================"
echo

# Проверка версии Ubuntu
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$VERSION_ID" != "18.04" ]]; then
        echo "ПРЕДУПРЕЖДЕНИЕ: Этот скрипт предназначен для Ubuntu 18.04, но обнаружена версия: $VERSION_ID"
        echo "Продолжаем выполнение..."
    fi
fi

# Обновление системы
echo "Обновление системы..."
sudo apt-get update
sudo apt-get upgrade -y
echo "✓ Система обновлена"

# Установка Python 3.7+ (Ubuntu 18.04 поставляется с Python 3.6, нужен более новый)
echo
echo "Проверка версии Python..."
python3_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python3_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Установка Python 3.8 из deadsnakes PPA..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils
    sudo apt-get install -y python3.8-pip || {
        # Если pip3.8 недоступен, устанавливаем через get-pip
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        sudo python3.8 get-pip.py
        rm get-pip.py
    }
    # Создаем символическую ссылку
    sudo ln -sf /usr/bin/python3.8 /usr/bin/python3
    sudo ln -sf /usr/bin/pip3.8 /usr/bin/pip3
else
    echo "✓ Python $python3_version найден"
    # Установка дополнительных пакетов для Python
    sudo apt-get install -y python3-venv python3-dev python3-pip
fi

echo "✓ Python настроен"
python3 --version

# Установка системных зависимостей
echo
echo "Установка системных зависимостей..."
sudo apt-get install -y \
    libdmtx-dev \
    libdmtx0a \
    build-essential \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev

echo "✓ Системные зависимости установлены"

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
python -m pip install --upgrade pip
echo "✓ pip обновлен"

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

# Создание скрипта активации
echo
echo "Создание скрипта активации..."
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Скрипт активации виртуального окружения для lg_html
source venv/bin/activate
echo "Виртуальное окружение активировано"
echo "Для запуска генератора используйте: python gen2.py --help"
EOF
chmod +x activate_env.sh
echo "✓ Скрипт активации создан (activate_env.sh)"

echo
echo "========================================"
echo "Инициализация завершена успешно!"
echo "========================================"
echo
echo "Для активации виртуального окружения используйте:"
echo "  source venv/bin/activate"
echo "  или"
echo "  ./activate_env.sh"
echo
echo "Для запуска генератора используйте:"
echo "  python gen2.py --help"
echo
echo "Документация доступна в README.md"
echo

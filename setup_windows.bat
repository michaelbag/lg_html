@echo off
REM Скрипт инициализации проекта lg_html для Windows
REM Автор: Michael BAG
REM Версия: 1.0

echo ========================================
echo Инициализация проекта lg_html для Windows
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден в системе!
    echo Пожалуйста, установите Python 3.7+ с https://python.org
    echo Убедитесь, что Python добавлен в PATH
    pause
    exit /b 1
)

echo ✓ Python найден
python --version

REM Проверка наличия pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: pip не найден!
    echo Попробуйте переустановить Python с опцией "Add Python to PATH"
    pause
    exit /b 1
)

echo ✓ pip найден

REM Создание виртуального окружения
echo.
echo Создание виртуального окружения...
python -m venv venv
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось создать виртуальное окружение
    pause
    exit /b 1
)

echo ✓ Виртуальное окружение создано

REM Активация виртуального окружения
echo.
echo Активация виртуального окружения...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

echo ✓ Виртуальное окружение активировано

REM Обновление pip
echo.
echo Обновление pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: Не удалось обновить pip, продолжаем...
)

REM Установка зависимостей
echo.
echo Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости
    echo Попробуйте установить их вручную:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Зависимости установлены

REM Создание необходимых папок
echo.
echo Создание структуры папок...
if not exist "input_data" mkdir input_data
if not exist "input_templates" mkdir input_templates
if not exist "output" mkdir output
if not exist "temp" mkdir temp
if not exist "conf" mkdir conf

echo ✓ Структура папок создана

REM Проверка установки
echo.
echo Проверка установки...
python -c "import pylibdmtx, qrcode, reportlab, PyPDF2, PIL; print('✓ Все модули импортированы успешно')"
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: Некоторые модули не импортированы корректно
    echo Проверьте установку зависимостей вручную
)

echo.
echo ========================================
echo Инициализация завершена успешно!
echo ========================================
echo.
echo Для активации виртуального окружения в будущем используйте:
echo   venv\Scripts\activate.bat
echo.
echo Для запуска генератора используйте:
echo   python gen2.py --help
echo.
echo Документация доступна в README.md
echo.
pause

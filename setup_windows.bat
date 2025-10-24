@echo off
REM lg_html project initialization script for Windows
REM Author: Michael BAG
REM Version: 1.0

echo ========================================
echo lg_html Project Initialization for Windows
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in system!
    echo Please install Python 3.7+ from https://python.org
    echo Make sure Python is added to PATH
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Check for pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found!
    echo Try reinstalling Python with "Add Python to PATH" option
    pause
    exit /b 1
)

echo ✓ pip found

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated

REM Update pip
echo.
echo Updating pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to update pip, continuing...
)

REM Detect system architecture
echo.
echo Detecting system architecture...
for /f "tokens=2 delims==" %%i in ('wmic os get osarchitecture /value ^| find "="') do set ARCH=%%i
echo ✓ Architecture: %ARCH%

REM Install dependencies with architecture-specific handling
echo.
echo Installing dependencies...

REM Handle Pillow installation for different architectures
if "%ARCH%"=="64-bit" (
    echo ✓ Detected 64-bit architecture, installing x86_64-compatible packages...
    pip install --no-cache-dir --force-reinstall Pillow
) else if "%ARCH%"=="32-bit" (
    echo ✓ Detected 32-bit architecture, installing x86-compatible packages...
    pip install --no-cache-dir --force-reinstall Pillow
) else (
    echo ⚠️  Unknown architecture (%ARCH%), using default package installation...
    pip install Pillow
)

REM Install other dependencies
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Try installing them manually:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Dependencies installed

REM Create necessary folders
echo.
echo Creating folder structure...
if not exist "input_data" mkdir input_data
if not exist "input_templates" mkdir input_templates
if not exist "output" mkdir output
if not exist "temp" mkdir temp
if not exist "conf" mkdir conf

echo ✓ Folder structure created

REM Check installation
echo.
echo Checking installation...
python test_dependencies.py

echo.
echo ========================================
echo Initialization completed successfully!
echo ========================================
echo.
echo To activate virtual environment in the future, use:
echo   venv\Scripts\activate.bat
echo.
echo To run the generator, use:
echo   python gen2.py --help
echo.
echo Documentation is available in README.md
echo.
pause

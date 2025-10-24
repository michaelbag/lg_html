#!/bin/bash
# lg_html project initialization script for macOS
# Author: Michael BAG
# Version: 1.0
# Supports both Intel and Apple Silicon (M1/M2/M3) Macs

set -e  # Exit on error

echo "========================================"
echo "lg_html Project Initialization for macOS"
echo "========================================"
echo

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found in system!"
    echo "Install Python 3.7+ using one of these methods:"
    echo "  1. Homebrew: brew install python3"
    echo "  2. Official installer: https://python.org/downloads/"
    echo "  3. pyenv: brew install pyenv && pyenv install 3.11"
    exit 1
fi

echo "✓ Python found"
python3 --version

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found!"
    echo "Install pip3:"
    echo "  brew install python3"
    echo "  or download from: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

echo "✓ pip3 found"

# Detect Mac architecture
echo
echo "Detecting Mac architecture..."
ARCH=$(uname -m)
OS_VERSION=$(sw_vers -productVersion)
echo "✓ Architecture: $ARCH"
echo "✓ macOS Version: $OS_VERSION"

# Check for Homebrew (recommended for system dependencies)
if command -v brew &> /dev/null; then
    echo "✓ Homebrew found"
    BREW_AVAILABLE=true
else
    echo "⚠️  Homebrew not found (optional but recommended)"
    echo "   Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    BREW_AVAILABLE=false
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Update pip
echo
echo "Updating pip..."
python -m pip install --upgrade pip || echo "WARNING: Failed to update pip, continuing..."

# Install system dependencies for pylibdmtx (if Homebrew is available)
if [ "$BREW_AVAILABLE" = true ]; then
    echo
    echo "Installing system dependencies via Homebrew..."
    if ! brew list libdmtx &> /dev/null; then
        echo "Installing libdmtx for DataMatrix support..."
        brew install libdmtx
    else
        echo "✓ libdmtx already installed"
    fi
else
    echo
    echo "⚠️  Skipping system dependencies installation (Homebrew not available)"
    echo "   Install libdmtx manually for DataMatrix code support:"
    echo "   brew install libdmtx"
fi

# Install Python dependencies with architecture-specific handling
echo
echo "Installing Python dependencies..."

# Handle Pillow installation for different Mac architectures
if [[ "$ARCH" == "arm64" ]]; then
    echo "✓ Detected Apple Silicon (M1/M2/M3), installing ARM64-compatible packages..."
    echo "  This ensures compatibility with Apple Silicon Macs"
    pip install --no-cache-dir --force-reinstall Pillow
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "✓ Detected Intel Mac, installing x86_64-compatible packages..."
    pip install --no-cache-dir --force-reinstall Pillow
else
    echo "⚠️  Unknown architecture ($ARCH), using default package installation..."
    pip install Pillow
fi

# Install other dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary folders
echo
echo "Creating folder structure..."
mkdir -p input_data input_templates output temp conf
echo "✓ Folder structure created"

# Check installation
echo
echo "Checking installation..."
python test_dependencies.py

echo
echo "========================================"
echo "Initialization completed successfully!"
echo "========================================"
echo
echo "Architecture-specific notes:"
if [[ "$ARCH" == "arm64" ]]; then
    echo "✓ Optimized for Apple Silicon (M1/M2/M3)"
    echo "✓ All packages installed with ARM64 compatibility"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "✓ Optimized for Intel Macs"
    echo "✓ All packages installed with x86_64 compatibility"
fi
echo
echo "To activate virtual environment in the future, use:"
echo "  source venv/bin/activate"
echo
echo "To run the generator, use:"
echo "  python gen2.py --help"
echo
echo "To use the interactive config generator:"
echo "  python generate_config.py -i"
echo
echo "Documentation is available in README.md"
echo

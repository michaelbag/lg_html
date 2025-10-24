#!/bin/bash
# lg_html project initialization script for Linux
# Author: Michael BAG
# Version: 1.0

set -e  # Exit on error

echo "========================================"
echo "lg_html Project Initialization for Linux"
echo "========================================"
echo

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found in system!"
    echo "Install Python 3.7+ using your distribution's package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo "✓ Python found"
python3 --version

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found!"
    echo "Install pip3:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    echo "  Fedora: sudo dnf install python3-pip"
    exit 1
fi

echo "✓ pip3 found"

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

# Install system dependencies for pylibdmtx
echo
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    echo "Detected apt, installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y libdmtx-dev libdmtx0a
elif command -v yum &> /dev/null; then
    echo "Detected yum, installing system dependencies..."
    sudo yum install -y libdmtx-devel
elif command -v dnf &> /dev/null; then
    echo "Detected dnf, installing system dependencies..."
    sudo dnf install -y libdmtx-devel
else
    echo "WARNING: Unknown package manager, skipping system dependencies installation"
    echo "Install libdmtx manually for DataMatrix code support"
fi

# Detect system architecture
echo
echo "Detecting system architecture..."
ARCH=$(uname -m)
OS=$(uname -s)
echo "✓ Architecture: $ARCH"
echo "✓ Operating System: $OS"

# Install Python dependencies with architecture-specific handling
echo
echo "Installing Python dependencies..."

# Handle Pillow installation for different architectures
if [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]]; then
    echo "✓ Detected ARM64 architecture, installing ARM64-compatible packages..."
    pip install --no-cache-dir --force-reinstall Pillow
elif [[ "$ARCH" == "x86_64" || "$ARCH" == "amd64" ]]; then
    echo "✓ Detected x86_64 architecture, installing x86_64-compatible packages..."
    pip install --no-cache-dir --force-reinstall Pillow
else
    echo "⚠️  Unknown architecture ($ARCH), using default package installation..."
    pip install Pillow
fi

# Install other dependencies
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
echo "To activate virtual environment in the future, use:"
echo "  source venv/bin/activate"
echo
echo "To run the generator, use:"
echo "  python gen2.py --help"
echo
echo "Documentation is available in README.md"
echo

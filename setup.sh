#!/bin/bash
# Universal lg_html project initialization script
# Author: Michael BAG
# Version: 1.0
# Automatically detects OS and runs appropriate setup script

set -e  # Exit on error

echo "========================================"
echo "lg_html Universal Project Initialization"
echo "========================================"
echo

# Detect operating system
OS=$(uname -s)
ARCH=$(uname -m)

echo "✓ Detected OS: $OS"
echo "✓ Detected Architecture: $ARCH"
echo

# Run appropriate setup script
case "$OS" in
    "Darwin")
        echo "🍎 macOS detected, running macOS setup..."
        if [ -f "setup_macos.sh" ]; then
            chmod +x setup_macos.sh
            ./setup_macos.sh
        else
            echo "❌ setup_macos.sh not found!"
            echo "Please ensure all setup scripts are present."
            exit 1
        fi
        ;;
    "Linux")
        echo "🐧 Linux detected, running Linux setup..."
        if [ -f "setup_linux.sh" ]; then
            chmod +x setup_linux.sh
            ./setup_linux.sh
        else
            echo "❌ setup_linux.sh not found!"
            echo "Please ensure all setup scripts are present."
            exit 1
        fi
        ;;
    "CYGWIN"*|"MINGW"*|"MSYS"*)
        echo "🪟 Windows detected, running Windows setup..."
        if [ -f "setup_windows.bat" ]; then
            ./setup_windows.bat
        else
            echo "❌ setup_windows.bat not found!"
            echo "Please ensure all setup scripts are present."
            exit 1
        fi
        ;;
    *)
        echo "❌ Unsupported operating system: $OS"
        echo "Supported systems: macOS, Linux, Windows"
        echo "Please run the appropriate setup script manually:"
        echo "  macOS: ./setup_macos.sh"
        echo "  Linux: ./setup_linux.sh"
        echo "  Windows: setup_windows.bat"
        exit 1
        ;;
esac

echo
echo "🎉 Setup completed successfully!"
echo "Your lg_html project is ready to use."

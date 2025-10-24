#!/bin/bash
# lg_html project initialization script for Ubuntu Server 20.04
# Author: Michael BAG
# Version: 1.0

set -e  # Exit on error

echo "========================================"
echo "lg_html Project Initialization for Ubuntu Server 20.04"
echo "========================================"
echo

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$VERSION_ID" != "20.04" ]]; then
        echo "WARNING: This script is designed for Ubuntu 20.04, but detected version: $VERSION_ID"
        echo "Continuing execution..."
    fi
fi

# Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y
echo "✓ System updated"

# Check for Python 3.8+ (Ubuntu 20.04 comes with Python 3.8)
echo
echo "Checking Python version..."
python3_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python3_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Installing Python 3.8+..."
    sudo apt-get install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils python3.8-pip
    # Create symbolic link if needed
    if [ ! -f /usr/bin/python3 ]; then
        sudo ln -sf /usr/bin/python3.8 /usr/bin/python3
    fi
    if [ ! -f /usr/bin/pip3 ]; then
        sudo ln -sf /usr/bin/pip3.8 /usr/bin/pip3
    fi
else
    echo "✓ Python $python3_version found"
    # Install additional Python packages
    sudo apt-get install -y python3-venv python3-dev python3-pip
fi

echo "✓ Python configured"
python3 --version

# Install system dependencies
echo
echo "Installing system dependencies..."
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
    liblzma-dev \
    pkg-config

echo "✓ System dependencies installed"

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
python -m pip install --upgrade pip
echo "✓ pip updated"

# Install Python dependencies
echo
echo "Installing Python dependencies..."
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

# Create activation script
echo
echo "Creating activation script..."
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Virtual environment activation script for lg_html
source venv/bin/activate
echo "Virtual environment activated"
echo "To run the generator, use: python gen2.py --help"
EOF
chmod +x activate_env.sh
echo "✓ Activation script created (activate_env.sh)"

# Create systemd service (optional)
echo
echo "Creating systemd service (optional)..."
cat > lg_html.service << EOF
[Unit]
Description=LG HTML Label Generator Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python gen2.py --help
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
echo "✓ Systemd service created (lg_html.service)"
echo "  To install the service, run:"
echo "    sudo cp lg_html.service /etc/systemd/system/"
echo "    sudo systemctl daemon-reload"
echo "    sudo systemctl enable lg_html.service"

echo
echo "========================================"
echo "Initialization completed successfully!"
echo "========================================"
echo
echo "To activate virtual environment, use:"
echo "  source venv/bin/activate"
echo "  or"
echo "  ./activate_env.sh"
echo
echo "To run the generator, use:"
echo "  python gen2.py --help"
echo
echo "Documentation is available in README.md"
echo

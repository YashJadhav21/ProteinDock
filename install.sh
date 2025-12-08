#!/bin/bash
# Download AutoDock Vina for Linux if not present
VINA_DIR="backend/vina_bin"
VINA_URL="https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64"

mkdir -p $VINA_DIR

if [ ! -f "$VINA_DIR/vina" ]; then
    echo "Downloading AutoDock Vina for Linux..."
    curl -L $VINA_URL -o $VINA_DIR/vina
    chmod +x $VINA_DIR/vina
    echo "✅ AutoDock Vina downloaded successfully"
else
    echo "✅ AutoDock Vina already present"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node dependencies
echo "Installing Node dependencies..."
cd backend
npm install

echo "✅ All dependencies installed"

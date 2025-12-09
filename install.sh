#!/bin/bash
# AutoDock Vina Installation for Railway (Linux)
echo "🔧 Setting up AutoDock Vina for Linux..."

VINA_DIR="backend/vina_bin"

# Create directory
mkdir -p $VINA_DIR

# Remove Windows executable if present
rm -f $VINA_DIR/vina.exe

# Check if we have the versioned Linux binary and rename it
if [ -f "$VINA_DIR/vina_1.2.7_linux_x86_64" ]; then
    echo "✅ Found existing AutoDock Vina Linux binary"
    mv $VINA_DIR/vina_1.2.7_linux_x86_64 $VINA_DIR/vina
    chmod +x $VINA_DIR/vina
    echo "✅ Renamed to vina and made executable"
elif [ ! -f "$VINA_DIR/vina" ]; then
    # Download if not present
    echo "📥 Downloading AutoDock Vina v1.2.5 for Linux..."
    VINA_URL="https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64"
    curl -L $VINA_URL -o $VINA_DIR/vina
    chmod +x $VINA_DIR/vina
    echo "✅ Downloaded and made executable"
else
    echo "✅ AutoDock Vina already present"
    chmod +x $VINA_DIR/vina
fi

# Verify file size
FILE_SIZE=$(stat -c%s "$VINA_DIR/vina" 2>/dev/null || stat -f%z "$VINA_DIR/vina" 2>/dev/null)
if [ "$FILE_SIZE" -gt 100000 ]; then
    echo "✅ Binary size verified: $FILE_SIZE bytes"
else
    echo "❌ Error: Binary file too small ($FILE_SIZE bytes)"
    exit 1
fi

# Test Vina binary
echo "🔍 Testing AutoDock Vina..."
if $VINA_DIR/vina --version 2>&1 | grep -q "AutoDock Vina"; then
    echo "✅ AutoDock Vina is working!"
    $VINA_DIR/vina --version 2>&1 | head -n 1
else
    echo "⚠️  Warning: Vina binary may not be compatible with this system"
fi

# Python packages installed via nixpacks.toml
echo "✅ Python packages installed via nixpacks"

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
cd backend
npm install --production

echo ""
echo "✅ All dependencies installed successfully!"
echo "🎯 AutoDock Vina: $(pwd)/vina_bin/vina"
echo ""




#!/bin/bash
set -e

echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "🐍 Checking for Python 2.7..."
# Check if Python 2.7 is already available (Render may have it pre-installed)
if command -v python2.7 &> /dev/null; then
    echo "✅ Python 2.7 found: $(python2.7 --version)"
elif command -v python2 &> /dev/null; then
    echo "✅ Python 2 found: $(python2 --version)"
    # Create symlink if python2 exists but not python2.7
    ln -s $(which python2) /tmp/python2.7 || true
else
    echo "⚠️  Python 2 not found - MGLTools will use BioPython + OpenBabel fallback"
    echo "    This is less accurate but functional for receptor preparation"
fi

echo "✅ MGLTools scripts bundled in repository (backend/mgltools/)"

echo "🔧 Setting up AutoDock Vina..."
cd backend/vina_bin

if [ ! -f "vina" ]; then
    if [ -f "vina_1.2.7_linux_x86_64" ]; then
        mv vina_1.2.7_linux_x86_64 vina
    else
        curl -L https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.7/vina_1.2.7_linux_x86_64 -o vina
    fi
fi

chmod +x vina
cd ../..

echo "📦 Installing Node.js dependencies..."
cd backend && npm install --production && cd ..

echo "✅ Build complete!"

#!/bin/bash
set -e

echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "🐍 Installing Python 2.7 for MGLTools..."
# Render uses Ubuntu - install python2.7
sudo apt-get update -qq
sudo apt-get install -y python2.7 python2.7-dev

# Verify Python 2.7 is installed
if command -v python2.7 &> /dev/null; then
    echo "✅ Python 2.7 installed: $(python2.7 --version)"
else
    echo "⚠️  Python 2.7 installation failed, will use BioPython fallback"
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

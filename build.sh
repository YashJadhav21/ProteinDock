#!/bin/bash
set -e

echo "📦 Installing pip..."
curl -sS https://bootstrap.pypa.io/get-pip.py | python3 - --break-system-packages

echo "📦 Installing Python dependencies..."
python3 -m pip install --break-system-packages --no-cache-dir biopython numpy rdkit-pypi meeko openbabel-wheel

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
cd backend && npm install --production

echo "✅ Build complete!"

#!/bin/bash
set -e

echo "📦 Installing pip..."
curl -sS https://bootstrap.pypa.io/get-pip.py | python3 - --break-system-packages

echo "📦 Finding GCC library path..."
GCC_LIB=$(find /nix/store -name "libstdc++.so.6" 2>/dev/null | head -n1 | xargs dirname)
echo "Found at: $GCC_LIB"

echo "📦 Installing Python dependencies with library path..."
LD_LIBRARY_PATH="$GCC_LIB:$LD_LIBRARY_PATH" python3 -m pip install --break-system-packages --no-cache-dir biopython numpy rdkit-pypi meeko openbabel-wheel

echo "📦 Testing RDKit import..."
LD_LIBRARY_PATH="$GCC_LIB:$LD_LIBRARY_PATH" python3 -c "from rdkit import Chem; print('✅ RDKit works!')"

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

echo "💾 Saving library path to env file..."
echo "export LD_LIBRARY_PATH=\"$GCC_LIB:\$LD_LIBRARY_PATH\"" > ../lib_path.sh

echo "✅ Build complete!"

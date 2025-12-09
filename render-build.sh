#!/bin/bash
set -e

echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "🧬 Setting up MGLTools (AutoDockTools)..."
cd backend

# Download MGLTools if not present
if [ ! -d "mgltools/MGLToolsPckgs" ]; then
    echo "Downloading MGLTools..."
    wget -q http://mgltools.scripps.edu/downloads/downloads/tars/releases/REL1.5.7/mgltools_x86_64Linux2_1.5.7.tar.gz -O mgltools.tar.gz
    
    echo "Extracting MGLTools..."
    tar -xzf mgltools.tar.gz
    
    echo "Setting up MGLTools directories..."
    mkdir -p mgltools
    mv mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs mgltools/
    
    echo "Cleaning up..."
    rm -rf mgltools_x86_64Linux2_1.5.7
    rm mgltools.tar.gz
    
    echo "✅ MGLTools setup complete!"
else
    echo "✅ MGLTools already installed"
fi

cd ..

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

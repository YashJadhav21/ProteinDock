#!/bin/bash
# Load library path from build
if [ -f lib_path.sh ]; then
    source lib_path.sh
    echo "✅ Loaded library path from build: $LD_LIBRARY_PATH"
else
    echo "⚠️ lib_path.sh not found, searching..."
    GCC_LIBS=$(find /nix/store -type d -path "*/gcc-*/lib" 2>/dev/null | tr '\n' ':')
    export LD_LIBRARY_PATH="${GCC_LIBS}${LD_LIBRARY_PATH}"
fi

echo "🔧 LD_LIBRARY_PATH = $LD_LIBRARY_PATH"

# Start the server
cd backend && node server.js

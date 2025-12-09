#!/bin/bash
# Find GCC library path and set LD_LIBRARY_PATH
GCC_LIB_PATH=$(find /nix/store -type f -name "libstdc++.so.6" 2>/dev/null | head -n1 | xargs dirname)

if [ -n "$GCC_LIB_PATH" ]; then
    echo "✅ Found libstdc++.so.6 at: $GCC_LIB_PATH"
    export LD_LIBRARY_PATH="$GCC_LIB_PATH:$LD_LIBRARY_PATH"
else
    echo "⚠️ Could not find libstdc++.so.6"
fi

# Start the server
cd backend && node server.js

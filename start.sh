#!/bin/bash
# Set LD_LIBRARY_PATH to include all gcc lib directories from Nix store
export LD_LIBRARY_PATH=$(find /nix/store -name "libstdc++.so.6" -exec dirname {} \; 2>/dev/null | tr '\n' ':')$LD_LIBRARY_PATH

echo "🔧 LD_LIBRARY_PATH set to: $LD_LIBRARY_PATH"

# Verify library is accessible
if ldconfig -p 2>/dev/null | grep -q libstdc++.so.6 || find /nix/store -name "libstdc++.so.6" 2>/dev/null | head -n1; then
    echo "✅ libstdc++.so.6 is accessible"
else
    echo "⚠️ Warning: libstdc++.so.6 may not be accessible"
fi

# Start the server
cd backend && node server.js

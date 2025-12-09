#!/bin/bash
# Find and export the gcc library path
GCC_LIB=$(find /nix/store -name "libstdc++.so.6" 2>/dev/null | head -n 1 | xargs dirname)
if [ -n "$GCC_LIB" ]; then
    export LD_LIBRARY_PATH="$GCC_LIB:$LD_LIBRARY_PATH"
    echo "✅ Found libstdc++.so.6 in $GCC_LIB"
else
    echo "⚠️ Could not find libstdc++.so.6"
fi

# Execute the command passed as arguments
exec "$@"

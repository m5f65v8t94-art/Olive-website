#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/backend"

echo "=========================================================="
echo "🌱 Starting Olive Youth Mental-Wellbeing Support App (Liv)"
echo "=========================================================="

# Check if arch is x86_64 or arm64
if command -v python3 >/dev/null 2>&1; then
    arch -x86_64 python3 run_backend.py 2>/dev/null || python3 run_backend.py
else
    echo "Python 3 is required but not found."
    exit 1
fi

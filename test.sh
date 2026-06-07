#!/usr/bin/env bash
set -euo pipefail

FACTORIO="${FACTORIO:-/home/reimar/.local/share/Steam/steamapps/common/Factorio/bin/x64/factorio}"
MOD_DIR="$(cd "$(dirname "$0")" && pwd)"
SAVE="${1:-}"

echo "=== Factorio Mod Test: orbs ==="
echo "Mod directory: $MOD_DIR"

# Test 1: Data stage validation (--create a throwaway map)
echo ""
echo "--- Test 1: Data stage (prototype loading) ---"
TMPMAP=$(mktemp /tmp/factorio-test-XXXXXX.zip)
trap "rm -f $TMPMAP" EXIT

if output=$("$FACTORIO" --create "$TMPMAP" 2>&1); then
    echo "PASS: Data stage loaded successfully"
else
    echo "FAIL: Data stage error"
    echo "$output"
    exit 1
fi

# Test 2: Check for prototype warnings
if echo "$output" | grep -i "warning" | grep -v "Checksum" | head -20 | grep -q .; then
    echo ""
    echo "Warnings detected:"
    echo "$output" | grep -i "warning" | grep -v "Checksum" | head -20
fi

# Test 3: Load and run a save game (if provided)
if [[ -n "$SAVE" ]]; then
    echo ""
    echo "--- Test 2: Runtime (benchmark $SAVE for 60 ticks) ---"
    if output=$("$FACTORIO" --benchmark "$SAVE" --benchmark-ticks 60 --benchmark-sanitize 2>&1); then
        echo "PASS: Save loaded and ran 60 ticks"
        echo "$output" | tail -3
    else
        echo "FAIL: Runtime error"
        echo "$output"
        exit 1
    fi
else
    echo ""
    echo "(Skipping runtime test - pass a save file as argument to test runtime)"
    echo "  Example: ./test.sh ~/.factorio/saves/ORBS.zip"
fi

echo ""
echo "=== All tests passed ==="

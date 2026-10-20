#!/usr/bin/env bash
set -euo pipefail

FACTORIO="${FACTORIO:-/home/reimar/.local/share/Steam/steamapps/common/Factorio/bin/x64/factorio}"
MOD_DIR="$(cd "$(dirname "$0")" && pwd)"
SPRITES=0
if [[ "${1:-}" == "--sprites" ]]; then SPRITES=1; shift; fi
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
    echo "  Add --sprites first to also load every sprite in a real (windowed) start"
fi

# Test 4: Sprite loading (graphical start; --create above never opens images)
if [[ "$SPRITES" == 1 ]]; then
    echo ""
    echo "--- Test 3: Sprites (graphical start to the main menu) ---"
    # steam_appid.txt in the working directory stops the Steam API from
    # relaunching the game through Steam (needs Steam running).
    RUNDIR=$(mktemp -d /tmp/factorio-sprites-XXXXXX)
    LOG="$RUNDIR/log.txt"
    echo 427520 > "$RUNDIR/steam_appid.txt"
    (cd "$RUNDIR" && exec "$FACTORIO" > "$LOG" 2>&1) &
    PID=$!
    for _ in $(seq 300); do
        grep -qE "Factorio initialised|Error" "$LOG" 2>/dev/null && break
        kill -0 $PID 2>/dev/null || break
        sleep 1
    done
    kill $PID 2>/dev/null || true
    wait $PID 2>/dev/null || true
    if grep -q "Factorio initialised" "$LOG" && ! grep -q "Error" "$LOG"; then
        echo "PASS: All sprites loaded"
        rm -rf "$RUNDIR"
    else
        echo "FAIL: Sprite loading error (full log: $LOG)"
        grep -B2 -A10 "Error" "$LOG" | head -40
        exit 1
    fi
fi

echo ""
echo "=== All tests passed ==="

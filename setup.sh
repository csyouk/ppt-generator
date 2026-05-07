#!/usr/bin/env bash
set -e

echo "========================================="
echo " ppt-builder bootstrap"
echo "========================================="

# uv 설치 확인
if ! command -v uv >/dev/null 2>&1; then
    echo "[INFO] uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    export PATH="$HOME/.cargo/bin:$PATH"

    if ! command -v uv >/dev/null 2>&1; then
        echo "[ERROR] uv installation failed"
        exit 1
    fi
fi

echo "[INFO] Creating virtual environment..."
uv venv

echo "[INFO] Installing dependencies..."
uv sync

echo "[INFO] Installing Playwright Chromium..."
source .venv/bin/activate

python -m playwright install chromium

echo ""
echo "========================================="
echo " Setup complete"
echo "========================================="
echo ""
echo "Activate venv:"
echo "  source .venv/bin/activate"
echo ""
echo "Run build:"
echo "  python src/build.py"

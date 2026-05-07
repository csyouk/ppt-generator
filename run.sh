#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

source .venv/bin/activate

INPUT=${1:-example.md}

python -m src.build \
  -i "$INPUT" \
  --output output.pptx
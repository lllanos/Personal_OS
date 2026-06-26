#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_DIR="$ROOT_DIR/installer"

cd "$INSTALLER_DIR"

if [[ ! -d ".venv" ]]; then
  echo "🍃 Creating Python virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "🌱 Installing dependencies..."
pip install -r requirements.txt

if [[ ! -f "config.yaml" ]]; then
  echo "🪨 Creating local config.yaml from config.example.yaml..."
  cp config.example.yaml config.yaml
fi

echo "🍃 Validating local configuration..."
python validate_config.py

echo "◯ Previewing PersonalOS structure..."
python dry_run.py

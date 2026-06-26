#!/usr/bin/env bash
set -euo pipefail

# PersonalOS Installer Runner
# Usage from WSL:
#   export NOTION_TOKEN="ntn_YOUR_ROTATED_TOKEN"
#   export NOTION_PARENT_PAGE_ID="38bd46f8cef78097b8fad9b290a97c21"
#   bash run_installer.sh

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

echo "◯ Running PersonalOS installer..."
python install.py

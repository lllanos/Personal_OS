# ◯ PersonalOS

PersonalOS is a calm personal operating system concept designed to reduce cognitive load, restore harmony, and help people move through the day one clear step at a time.

This repository starts with a Notion installer prototype, but PersonalOS is not limited to Notion. Notion is the first storage and prototyping layer.

## Core idea

PersonalOS does not try to maximize productivity. It helps people recover clarity, rhythm, and balance.

> Less noise. One next step. More harmony.

## Early principles

- One visible screen.
- One visible mission.
- Zen and nature-inspired language.
- No pressure, no guilt, no aggressive urgency.
- The user returns to a refuge, not a dashboard.
- The system helps reduce mental load.
- Rituals guide transitions instead of forcing task management.

## Current milestone

`v0.1.0 Seed` creates the first Notion-based PersonalOS structure:

- 🍃 Refugio
- 🌅 Ritual del Amanecer
- 🎯 Ritual del Foco
- ☕ Ritual de Pausa
- 🌙 Ritual del Cierre
- 👤 Personas
- 🎯 Misiones
- 🌱 Hábitos

## Quick start

```bash
cd ~/projects
git clone https://github.com/lllanos/Personal_OS.git
cd Personal_OS

export NOTION_TOKEN="ntn_YOUR_ROTATED_TOKEN"
export NOTION_PARENT_PAGE_ID="38bd46f8cef78097b8fad9b290a97c21"

bash dry_run.sh
bash run_installer.sh
```

## Repository structure

```text
installer/     Notion installer and setup files
docs/          Lightweight documentation placeholders
assets/        Visual identity placeholders
examples/      Example configuration files
tests/         Future validation tests
```

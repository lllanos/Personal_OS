# PersonalOS Installer

Installer v0.1.0 creates the first Notion prototype of PersonalOS.

## Requirements

- Python 3.10+
- A Notion integration token
- A Notion parent page shared with the integration

## Quick start from WSL

```bash
cd ~/projects
git clone https://github.com/lllanos/Personal_OS.git
cd Personal_OS/installer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
```

Edit `config.yaml` and replace:

```yaml
notion:
  token: "ntn_REPLACE_WITH_ROTATED_TOKEN"
  parent_page_id: "38bd46f8cef78097b8fad9b290a97c21"
```

Then run:

```bash
python install.py
```

## Safer token usage

Instead of writing the token in `config.yaml`, you can export it:

```bash
export NOTION_TOKEN="ntn_YOUR_ROTATED_TOKEN"
export NOTION_PARENT_PAGE_ID="38bd46f8cef78097b8fad9b290a97c21"
python install.py
```

## Output

The installer creates:

- ◯ PersonalOS
- 🍃 Refugio
- 👤 Personas
- 🎯 Misiones
- 🌱 Hábitos

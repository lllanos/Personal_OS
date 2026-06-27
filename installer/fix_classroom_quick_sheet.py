#!/usr/bin/env python3
"""Add an editable quick sheet to the guided Google Classroom page.

The user should be able to paste/write the Classroom link and minimal context
without leaving the guided page or opening the backing database.

Run from installer directory:

    python fix_classroom_quick_sheet.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import yaml
from notion_client import Client
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID_RE = re.compile(r"([a-fA-F0-9]{32}|[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})")


def normalize_page_id(value: str) -> str:
    match = PAGE_ID_RE.search(value or "")
    if not match:
        return value
    return match.group(1).replace("-", "")


def rt(text: str):
    return [{"type": "text", "text": {"content": text}}]


def heading(text: str, level: int = 2):
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rt(text)}}


def paragraph(text: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def callout(text: str, icon: str = "✍️"):
    return {"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": icon}, "rich_text": rt(text)}}


def todo(text: str):
    return {"object": "block", "type": "to_do", "to_do": {"rich_text": rt(text), "checked": False}}


def load_config():
    path = Path("config.yaml") if Path("config.yaml").exists() else Path("config.example.yaml")
    if not path.exists():
        console.print("[red]No config.yaml or config.example.yaml found.[/red]")
        sys.exit(1)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_mapping():
    path = Path(".personalos/notion_mappings_v2.json")
    if not path.exists():
        console.print("[red]No existe .personalos/notion_mappings_v2.json.[/red]")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def save_mapping(mapping):
    Path(".personalos/notion_mappings_v2.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_token(config):
    token = os.getenv("NOTION_TOKEN") or config.get("notion", {}).get("token")
    if not token or "REPLACE" in token:
        console.print("[red]Missing valid NOTION_TOKEN. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    return token


def obj(mapping, key):
    value = mapping.get("objects", {}).get(key)
    if not value:
        console.print(f"[red]Mapping incompleto: falta {key}.[/red]")
        sys.exit(1)
    return value


def main():
    console.print(Panel("Agregando ficha rápida editable Classroom", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    objects = mapping.setdefault("objects", {})

    if objects.get("guided_google_classroom_quick_sheet"):
        console.print("[yellow]La ficha rápida Classroom ya fue agregada. No se duplica.[/yellow]")
        return 0

    guided = obj(mapping, "guided_google_classroom")
    notion = Client(auth=resolve_token(config))

    blocks = [
        divider(),
        heading("Ficha rápida Classroom", 2),
        callout("Escribí o pegá acá lo mínimo necesario. No hace falta abrir el registro si todavía estás orientándote.", "✍️"),
        heading("Acceso", 3),
        paragraph("Link de Classroom: pegar acá"),
        paragraph("Cuenta / usuario: escribir acá si hace falta"),
        todo("El link principal quedó escrito en esta página."),
        heading("Clase o materia", 3),
        paragraph("Materia o clase: escribir acá"),
        paragraph("Docente: escribir acá si lo sabés"),
        todo("La clase o materia principal quedó identificada."),
        heading("Próxima entrega", 3),
        paragraph("Entrega / tarea / examen: escribir acá"),
        paragraph("Fecha: escribir acá"),
        paragraph("Notas: escribir acá"),
        todo("La próxima entrega quedó identificada o se marcó como no visible."),
        heading("Cierre de esta ficha", 3),
        todo("Tengo una próxima acción clara."),
        todo("Puedo continuar sin abrir la base si no la necesito."),
        callout("La base Registro Classroom queda disponible como respaldo, pero esta ficha es el camino principal.", "🌿"),
    ]

    notion.blocks.children.append(block_id=normalize_page_id(guided["id"]), children=blocks)
    objects["guided_google_classroom_quick_sheet"] = {"status": "added"}
    save_mapping(mapping)
    console.print("[green]✓ Ficha rápida Classroom agregada correctamente.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

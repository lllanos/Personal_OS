#!/usr/bin/env python3
"""Add a visual form-like table to the guided Google Classroom page.

Notion does not provide native page-body form inputs through the API, but a
simple two-column table gives a clear visual cue: field on the left, value on
the right. This keeps the user inside the guided page and avoids opening the
backing database while orienting.

Run from installer directory:

    python fix_classroom_visual_form_table.py
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

FIELDS = [
    ("Link de Classroom", "pegar link aquí"),
    ("Cuenta / usuario", "escribir aquí si hace falta"),
    ("Materia o clase", "escribir aquí"),
    ("Docente", "escribir aquí si lo sabés"),
    ("Entrega / tarea / examen", "escribir aquí"),
    ("Fecha", "escribir aquí"),
    ("Notas", "escribir aquí"),
    ("Próxima acción", "escribir el siguiente paso"),
]


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


def callout(text: str, icon: str = "📝"):
    return {"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": icon}, "rich_text": rt(text)}}


def table_row(left: str, right: str):
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [rt(left), rt(right)],
        },
    }


def table_block():
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": 2,
            "has_column_header": True,
            "has_row_header": False,
            "children": [
                table_row("Campo", "Completar"),
                *[table_row(field, placeholder) for field, placeholder in FIELDS],
            ],
        },
    }


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
    console.print(Panel("Agregando tabla visual tipo formulario Classroom", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    objects = mapping.setdefault("objects", {})

    if objects.get("guided_google_classroom_visual_form_table"):
        console.print("[yellow]La tabla visual Classroom ya fue agregada. No se duplica.[/yellow]")
        return 0

    guided = obj(mapping, "guided_google_classroom")
    notion = Client(auth=resolve_token(config))

    blocks = [
        divider(),
        heading("Ficha rápida visual", 2),
        callout("Completá la columna derecha. Es una ficha simple, no una planilla de trabajo.", "📝"),
        table_block(),
        heading("Para cerrar esta ficha", 3),
        todo("Completé al menos Link o fuente principal."),
        todo("Completé Materia o clase."),
        todo("Completé Próxima acción."),
        paragraph("Cuando esos tres puntos estén claros, podés avanzar sin abrir el Registro Classroom."),
    ]

    notion.blocks.children.append(block_id=normalize_page_id(guided["id"]), children=blocks)
    objects["guided_google_classroom_visual_form_table"] = {"status": "added"}
    save_mapping(mapping)
    console.print("[green]✓ Tabla visual tipo formulario agregada correctamente.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

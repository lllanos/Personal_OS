#!/usr/bin/env python3
"""Append cross-step navigation to an existing PersonalOS Notion install.

This script upgrades an already-created PersonalOS learning flow without
reinstalling the whole workspace. It reads .personalos/notion_mappings_v2.json
created by installer/install.py and appends navigation links to:

- Paso 1 — Confirmar fuente de aprendizaje
- Paso 2 — Registrar materia o curso
- Paso 3 — Registrar primera tarea o entrega

Run from the installer directory:

    python fix_learning_navigation.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from notion_client import Client
from notion_client.errors import APIResponseError
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID_RE = re.compile(
    r"([a-fA-F0-9]{32}|[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
)


def rt(text: str, link: str | None = None) -> list[dict[str, Any]]:
    item: dict[str, Any] = {"type": "text", "text": {"content": text}}
    if link:
        item["text"]["link"] = {"url": link}
    return [item]


def heading(text: str, level: int = 2) -> dict[str, Any]:
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rt(text)}}


def paragraph_link(label: str, url: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(label, url)}}


def paragraph(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def callout(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🧭"},
            "rich_text": rt(text),
        },
    }


def normalize_page_id(value: str) -> str:
    match = PAGE_ID_RE.search(value or "")
    if not match:
        return value
    return match.group(1).replace("-", "")


def load_config() -> dict[str, Any]:
    path = Path("config.yaml") if Path("config.yaml").exists() else Path("config.example.yaml")
    if not path.exists():
        console.print("[red]No config.yaml or config.example.yaml found.[/red]")
        sys.exit(1)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_mapping() -> dict[str, Any]:
    path = Path(".personalos/notion_mappings_v2.json")
    if not path.exists():
        console.print("[red]No existe .personalos/notion_mappings_v2.json.[/red]")
        console.print("[yellow]Ejecutá primero python install.py para crear PersonalOS en Notion.[/yellow]")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_token(config: dict[str, Any]) -> str:
    token = os.getenv("NOTION_TOKEN") or config.get("notion", {}).get("token")
    if not token or "REPLACE" in token:
        console.print("[red]Missing valid NOTION_TOKEN. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    return token


def obj(mapping: dict[str, Any], key: str) -> dict[str, str]:
    objects = mapping.get("objects", {})
    value = objects.get(key)
    if not value:
        console.print(f"[red]Mapping incompleto: falta {key}.[/red]")
        sys.exit(1)
    return value


def append(notion: Client, page_id: str, blocks: list[dict[str, Any]]) -> None:
    try:
        notion.blocks.children.append(block_id=normalize_page_id(page_id), children=blocks)
    except APIResponseError as exc:
        console.print(f"[red]No pude actualizar página {page_id}[/red]")
        console.print(f"[yellow]{exc}[/yellow]")
        raise


def main() -> int:
    console.print(Panel("Agregando navegación entre pasos de aprendizaje", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    notion = Client(auth=resolve_token(config))

    step1 = obj(mapping, "learning_step_1")
    step2 = obj(mapping, "learning_step_2")
    step3 = obj(mapping, "learning_step_3")
    setup = obj(mapping, "learning_setup")
    refugio = obj(mapping, "refugio")
    bitacora = obj(mapping, "bitacora")

    append(
        notion,
        step1["id"],
        [
            divider(),
            heading("Navegación", 2),
            callout("Cuando confirmes la fuente, continuá con la estructura mínima del aprendizaje."),
            paragraph_link("🎒 Ir al Paso 2 — Registrar materia o curso", step2["url"]),
            paragraph_link("🏠 Volver a Configurar aprendizaje", setup["url"]),
            paragraph_link("🍃 Volver al Refugio", refugio["url"]),
        ],
    )

    append(
        notion,
        step2["id"],
        [
            divider(),
            heading("Navegación", 2),
            paragraph_link("👣 Volver al Paso 1 — Confirmar fuente de aprendizaje", step1["url"]),
            paragraph_link("✅ Ir al Paso 3 — Registrar primera tarea o entrega", step3["url"]),
            paragraph_link("🏠 Volver a Configurar aprendizaje", setup["url"]),
            paragraph_link("🍃 Volver al Refugio", refugio["url"]),
        ],
    )

    append(
        notion,
        step3["id"],
        [
            divider(),
            heading("Navegación", 2),
            callout("Al finalizar, ya existe una acción concreta para mostrar en Hoy / Ahora o No olvidar."),
            paragraph_link("🎒 Volver al Paso 2 — Registrar materia o curso", step2["url"]),
            paragraph_link("🍃 Finalizar y volver al Refugio", refugio["url"]),
            paragraph_link("📖 Registrar reflexión en Bitácora", bitacora["url"]),
            paragraph_link("🏠 Volver a Configurar aprendizaje", setup["url"]),
        ],
    )

    console.print("[green]✓ Navegación agregada correctamente.[/green]")
    console.print("Ahora podés recorrer: Paso 1 → Paso 2 → Paso 3 → Refugio / Bitácora")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

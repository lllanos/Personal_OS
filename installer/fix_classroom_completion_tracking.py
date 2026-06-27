#!/usr/bin/env python3
"""Add completion tracking to the guided Google Classroom page.

The guided page should not only explain what to do; it should make completion
visible. This script appends a clear checklist and tracking section to the
existing guided_google_classroom page.

Run from installer directory:

    python fix_classroom_completion_tracking.py
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


def rt(text: str, link: str | None = None):
    item = {"type": "text", "text": {"content": text}}
    if link:
        item["text"]["link"] = {"url": link}
    return [item]


def heading(text: str, level: int = 2):
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rt(text)}}


def paragraph(text: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def link_paragraph(label: str, url: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(label, url)}}


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def callout(text: str, icon: str = "✅"):
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


def append(notion, page_id, blocks):
    notion.blocks.children.append(block_id=normalize_page_id(page_id), children=blocks)


def main():
    console.print(Panel("Agregando seguimiento de finalización Classroom", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    objects = mapping.setdefault("objects", {})

    if objects.get("guided_google_classroom_completion_tracking"):
        console.print("[yellow]El seguimiento de Classroom ya fue agregado. No se duplica.[/yellow]")
        return 0

    guided = obj(mapping, "guided_google_classroom")
    classroom_db = objects.get("capture_google_classroom")
    step2 = obj(mapping, "learning_step_2")
    step3 = obj(mapping, "learning_step_3")
    refugio = obj(mapping, "refugio")

    notion = Client(auth=resolve_token(config))

    blocks = [
        divider(),
        heading("Seguimiento para finalizar", 2),
        callout("Marcá estos puntos para saber cuándo Classroom quedó suficientemente configurado. No hace falta perfección; hace falta claridad.", "✅"),
        heading("Acceso", 3),
        todo("Confirmé si puede entrar a Classroom."),
        todo("Registré o tengo pendiente registrar el link principal."),
        heading("Clase o materia", 3),
        todo("Elegí una sola clase o materia para empezar."),
        todo("Anoté el nombre de la clase o materia."),
        todo("Anoté el docente si lo conozco."),
        heading("Próxima entrega", 3),
        todo("Revisé si hay una tarea, entrega o examen próximo."),
        todo("Si hay fecha, la registré o dejé claro que está pendiente."),
        heading("Cierre", 3),
        todo("Hay una próxima acción concreta."),
        todo("Puedo continuar al Paso 2 o Paso 3 sin volver a pensar desde cero."),
        heading("Estado recomendado", 2),
        paragraph("Cuando estén marcados al menos Acceso + Clase/materia + Próxima acción, este bloque puede considerarse listo para avanzar."),
    ]

    if classroom_db:
        blocks.extend([
            callout("El registro estructurado sigue disponible como respaldo interno.", "🧾"),
            link_paragraph("🧾 Abrir Registro Classroom", classroom_db["url"]),
        ])

    blocks.extend([
        divider(),
        heading("Avanzar", 2),
        link_paragraph("🎒 Continuar al Paso 2 — Registrar materia o curso", step2["url"]),
        link_paragraph("✅ Continuar al Paso 3 — Registrar primera tarea o entrega", step3["url"]),
        link_paragraph("🍃 Volver al Refugio", refugio["url"]),
    ])

    append(notion, guided["id"], blocks)
    objects["guided_google_classroom_completion_tracking"] = {"status": "added"}
    save_mapping(mapping)
    console.print("[green]✓ Seguimiento de finalización agregado correctamente.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

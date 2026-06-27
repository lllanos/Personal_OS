#!/usr/bin/env python3
"""Create a guided Google Classroom configuration page.

This upgrade keeps the database as internal structure but gives the user a
friendlier page-first experience.

Run from installer directory:

    python fix_classroom_guided_page.py
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


def title_prop(text: str):
    return {"title": rt(text)}


def heading(text: str, level: int = 2):
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rt(text)}}


def paragraph(text: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def link_paragraph(label: str, url: str):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(label, url)}}


def bulleted(text: str):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text)}}


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def callout(text: str, icon: str = "🌿"):
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


def create_guided_page(notion, classroom_page, classroom_db, step1, step2, step3, setup, refugio):
    children = [
        heading("Configurar Classroom paso a paso", 1),
        callout("No hace falta completar todo ahora. La idea es dejar una primera referencia clara y una próxima acción.", "🌿"),
        heading("Paso 1 — Acceso", 2),
        paragraph("¿Ya podés entrar a Classroom?"),
        todo("Sí, puedo entrar."),
        todo("No puedo entrar todavía."),
        todo("No sé, tengo que confirmarlo."),
        paragraph("Link de Classroom: pegalo en el Registro Classroom cuando lo tengas."),
        heading("Paso 2 — Clase o materia", 2),
        paragraph("Elegí una sola clase o materia para empezar. Una alcanza."),
        bulleted("Nombre de la materia o clase."),
        bulleted("Docente, si lo sabés."),
        bulleted("Link o referencia principal."),
        heading("Paso 3 — Próxima entrega", 2),
        paragraph("Buscá si hay una tarea, entrega o examen próximo."),
        todo("Hay una entrega próxima."),
        todo("No hay entrega visible."),
        todo("Todavía no revisé."),
        heading("Paso 4 — Registrar", 2),
        callout("Cuando tengas datos, cargalos en el registro. La base queda como respaldo interno, no como pantalla principal.", "🧾"),
    ]
    if classroom_db:
        children.append(link_paragraph("🧾 Abrir Registro Classroom", classroom_db["url"]))
    children.extend([
        divider(),
        heading("Continuar", 2),
        link_paragraph("🎒 Ir al Paso 2 — Registrar materia o curso", step2["url"]),
        link_paragraph("✅ Ir al Paso 3 — Registrar primera tarea o entrega", step3["url"]),
        link_paragraph("👣 Volver al Paso 1 — Confirmar fuente", step1["url"]),
        link_paragraph("🏠 Volver a Configurar aprendizaje", setup["url"]),
        link_paragraph("🍃 Volver al Refugio", refugio["url"]),
    ])
    return notion.pages.create(
        parent={"page_id": normalize_page_id(classroom_page["id"])},
        icon={"type": "emoji", "emoji": "🌿"},
        properties={"title": title_prop("Configurar Classroom paso a paso")},
        children=children,
    )


def main():
    console.print(Panel("Creando página guiada de Classroom", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    objects = mapping.setdefault("objects", {})
    notion = Client(auth=resolve_token(config))

    if "guided_google_classroom" in objects:
        console.print("[yellow]Ya existe guided_google_classroom en el mapping. No se crea duplicado.[/yellow]")
        return 0

    classroom_page = obj(mapping, "source_google_classroom")
    step1 = obj(mapping, "learning_step_1")
    step2 = obj(mapping, "learning_step_2")
    step3 = obj(mapping, "learning_step_3")
    setup = obj(mapping, "learning_setup")
    refugio = obj(mapping, "refugio")
    classroom_db = objects.get("capture_google_classroom")

    guided = create_guided_page(notion, classroom_page, classroom_db, step1, step2, step3, setup, refugio)
    objects["guided_google_classroom"] = {"id": guided.get("id"), "url": guided.get("url")}

    append(notion, classroom_page["id"], [
        divider(),
        heading("Configuración guiada", 2),
        callout("Para una experiencia más cómoda, empezá por la página guiada. El registro queda como respaldo.", "🌿"),
        link_paragraph("🌿 Configurar Classroom paso a paso", guided["url"]),
    ])

    save_mapping(mapping)
    console.print("[green]✓ Página guiada de Classroom creada correctamente.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

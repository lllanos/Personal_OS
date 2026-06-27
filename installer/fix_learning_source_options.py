#!/usr/bin/env python3
"""Create actionable source option pages under Paso 1.

This script upgrades an already-created PersonalOS learning flow without
reinstalling the whole workspace. It reads .personalos/notion_mappings_v2.json
created by installer/install.py, creates one page per learning source option
under Paso 1, and appends links to those option pages.

Run from the installer directory:

    python fix_learning_source_options.py
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

SOURCE_OPTIONS = [
    {
        "key": "source_google_classroom",
        "title": "Google Classroom",
        "icon": "🏫",
        "goal": "Dejar listo el acceso principal a Classroom y saber qué revisar primero.",
        "checks": [
            "Confirmar que la persona puede entrar a Google Classroom.",
            "Guardar el link principal de Classroom o de la clase.",
            "Identificar materias o clases activas.",
            "Revisar tareas pendientes y próximas entregas.",
            "Registrar una primera tarea o entrega en PersonalOS.",
        ],
        "fields": ["Link de Classroom", "Materia o clase", "Docente", "Próxima entrega", "Notas"],
    },
    {
        "key": "source_campus_moodle",
        "title": "Campus universitario / Moodle",
        "icon": "🎓",
        "goal": "Registrar el campus o aula virtual donde vive el material de estudio.",
        "checks": [
            "Confirmar URL del campus.",
            "Identificar materia, comisión o curso.",
            "Ubicar calendario, entregas o evaluaciones.",
            "Guardar material principal o sección de archivos.",
            "Registrar próxima acción concreta.",
        ],
        "fields": ["URL del campus", "Materia/curso", "Usuario o referencia", "Fechas importantes", "Notas"],
    },
    {
        "key": "source_google_drive",
        "title": "Google Drive",
        "icon": "📁",
        "goal": "Ubicar carpeta o archivo principal para que el material no quede perdido.",
        "checks": [
            "Guardar link a carpeta principal.",
            "Identificar archivos importantes.",
            "Ordenar por materia, curso o fecha.",
            "Marcar documentos que requieren acción.",
            "Registrar primera tarea asociada a un archivo.",
        ],
        "fields": ["Link de carpeta", "Archivos clave", "Materia/curso", "Acción pendiente", "Notas"],
    },
    {
        "key": "source_whatsapp",
        "title": "WhatsApp o grupo de alumnos",
        "icon": "💬",
        "goal": "Convertir mensajes dispersos en tareas, fechas o documentos visibles.",
        "checks": [
            "Identificar grupo o conversación principal.",
            "Buscar mensajes con fechas, entregas o archivos.",
            "Guardar capturas o links relevantes si aplica.",
            "Pasar la información importante a PersonalOS.",
            "Definir próxima acción.",
        ],
        "fields": ["Grupo/conversación", "Mensaje importante", "Fecha", "Archivo/link", "Próxima acción"],
    },
    {
        "key": "source_email",
        "title": "Email",
        "icon": "✉️",
        "goal": "Usar el correo como fuente controlada, no como memoria infinita.",
        "checks": [
            "Identificar remitente o asunto clave.",
            "Guardar búsqueda o correo importante.",
            "Detectar fechas, adjuntos o instrucciones.",
            "Registrar tarea o entrega si corresponde.",
            "Definir próxima acción.",
        ],
        "fields": ["Remitente", "Asunto", "Fecha", "Adjunto/link", "Próxima acción"],
    },
    {
        "key": "source_pdfs_apuntes",
        "title": "PDFs, carpeta local o apuntes físicos",
        "icon": "📄",
        "goal": "Transformar material suelto en una referencia clara y accionable.",
        "checks": [
            "Identificar dónde está el material.",
            "Nombrar el documento o apunte principal.",
            "Relacionarlo con materia, curso o tema.",
            "Detectar si hay tarea, lectura o entrega asociada.",
            "Registrar próxima acción.",
        ],
        "fields": ["Ubicación", "Documento/apunte", "Materia/tema", "Fecha", "Próxima acción"],
    },
]


def rt(text: str, link: str | None = None) -> list[dict[str, Any]]:
    item: dict[str, Any] = {"type": "text", "text": {"content": text}}
    if link:
        item["text"]["link"] = {"url": link}
    return [item]


def title_prop(text: str) -> dict[str, Any]:
    return {"title": rt(text)}


def heading(text: str, level: int = 2) -> dict[str, Any]:
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rt(text)}}


def paragraph(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def paragraph_link(label: str, url: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(label, url)}}


def bulleted(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text)}}


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def callout(text: str, icon: str = "🧭") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {"icon": {"type": "emoji", "emoji": icon}, "rich_text": rt(text)},
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


def save_mapping(mapping: dict[str, Any]) -> None:
    Path(".personalos/notion_mappings_v2.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def resolve_token(config: dict[str, Any]) -> str:
    token = os.getenv("NOTION_TOKEN") or config.get("notion", {}).get("token")
    if not token or "REPLACE" in token:
        console.print("[red]Missing valid NOTION_TOKEN. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    return token


def obj(mapping: dict[str, Any], key: str) -> dict[str, str]:
    value = mapping.get("objects", {}).get(key)
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


def create_option_page(notion: Client, parent_id: str, option: dict[str, Any], step1_url: str, step2_url: str, setup_url: str) -> dict[str, Any]:
    children = [
        heading(option["title"], 1),
        callout(option["goal"], option["icon"]),
        heading("Checklist", 2),
        *[bulleted(item) for item in option["checks"]],
        heading("Datos a registrar", 2),
        *[bulleted(field) for field in option["fields"]],
        divider(),
        heading("Navegación", 2),
        paragraph_link("👣 Volver al Paso 1 — Confirmar fuente de aprendizaje", step1_url),
        paragraph_link("🎒 Continuar al Paso 2 — Registrar materia o curso", step2_url),
        paragraph_link("🏠 Volver a Configurar aprendizaje", setup_url),
    ]
    return notion.pages.create(
        parent={"page_id": normalize_page_id(parent_id)},
        icon={"type": "emoji", "emoji": option["icon"]},
        properties={"title": title_prop(option["title"])},
        children=children,
    )


def main() -> int:
    console.print(Panel("Creando opciones accionables de fuente de aprendizaje", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    notion = Client(auth=resolve_token(config))

    objects = mapping.setdefault("objects", {})
    step1 = obj(mapping, "learning_step_1")
    step2 = obj(mapping, "learning_step_2")
    setup = obj(mapping, "learning_setup")

    option_links: list[tuple[str, str]] = []
    for option in SOURCE_OPTIONS:
        if option["key"] in objects:
            option_links.append((option["icon"] + " " + option["title"], objects[option["key"]]["url"]))
            console.print(f"[dim]Ya existe: {option['title']}[/dim]")
            continue

        page = create_option_page(notion, step1["id"], option, step1["url"], step2["url"], setup["url"])
        objects[option["key"]] = {"id": page.get("id"), "url": page.get("url")}
        option_links.append((option["icon"] + " " + option["title"], page.get("url")))
        console.print(f"[green]Creado:[/green] {option['title']}")

    append(
        notion,
        step1["id"],
        [
            divider(),
            heading("Elegí una fuente para configurar", 2),
            callout("Estas opciones ya no son solo una lista: cada una abre una guía concreta."),
            *[paragraph_link(label, url) for label, url in option_links],
        ],
    )

    save_mapping(mapping)
    console.print("[green]✓ Opciones de fuente agregadas correctamente.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

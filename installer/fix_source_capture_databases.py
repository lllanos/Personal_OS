#!/usr/bin/env python3
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

PAGE_ID_RE = re.compile(
    r"([a-fA-F0-9]{32}|[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
)

CAPTURE_CONFIG = {
    "source_google_classroom": {
        "database_key": "capture_google_classroom",
        "database_name": "Registro Classroom",
        "title_property": "Clase / materia",
        "seed_title": "Primera clase / materia",
        "helper": "Cargá acá el Classroom o clase principal. Después continuá al Paso 2 para registrar la materia o curso.",
        "properties": {
            "Clase / materia": {"title": {}},
            "Link de Classroom": {"url": {}},
            "Docente": {"rich_text": {}},
            "Próxima entrega": {"date": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Pendiente", "color": "yellow"},
                        {"name": "Configurado", "color": "green"},
                        {"name": "Revisar", "color": "orange"},
                    ]
                }
            },
            "Notas": {"rich_text": {}},
        },
    },
    "source_campus_moodle": {
        "database_key": "capture_campus_moodle",
        "database_name": "Registro Campus / Moodle",
        "title_property": "Materia / curso",
        "seed_title": "Primera materia / curso",
        "helper": "Cargá el campus, materia o aula virtual principal.",
        "properties": {
            "Materia / curso": {"title": {}},
            "URL del campus": {"url": {}},
            "Institución": {"rich_text": {}},
            "Próxima fecha": {"date": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Pendiente", "color": "yellow"},
                        {"name": "Configurado", "color": "green"},
                        {"name": "Revisar", "color": "orange"},
                    ]
                }
            },
            "Notas": {"rich_text": {}},
        },
    },
    "source_google_drive": {
        "database_key": "capture_google_drive",
        "database_name": "Registro Google Drive",
        "title_property": "Carpeta / archivo",
        "seed_title": "Carpeta principal",
        "helper": "Cargá la carpeta o archivo principal y qué acción queda pendiente sobre ese material.",
        "properties": {
            "Carpeta / archivo": {"title": {}},
            "Link": {"url": {}},
            "Materia / tema": {"rich_text": {}},
            "Acción pendiente": {"rich_text": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Pendiente", "color": "yellow"},
                        {"name": "Ordenado", "color": "green"},
                        {"name": "Revisar", "color": "orange"},
                    ]
                }
            },
            "Notas": {"rich_text": {}},
        },
    },
    "source_whatsapp": {
        "database_key": "capture_whatsapp",
        "database_name": "Registro WhatsApp / Grupo",
        "title_property": "Grupo / conversación",
        "seed_title": "Grupo principal",
        "helper": "Usá este registro para transformar mensajes importantes en acciones visibles.",
        "properties": {
            "Grupo / conversación": {"title": {}},
            "Tema": {"rich_text": {}},
            "Fecha importante": {"date": {}},
            "Acción pendiente": {"rich_text": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Pendiente", "color": "yellow"},
                        {"name": "Pasado a PersonalOS", "color": "green"},
                        {"name": "Revisar", "color": "orange"},
                    ]
                }
            },
            "Notas": {"rich_text": {}},
        },
    },
    "source_email": {
        "database_key": "capture_email",
        "database_name": "Registro Email",
        "title_property": "Asunto / referencia",
        "seed_title": "Primer email importante",
        "helper": "Cargá correos que tengan fechas, adjuntos, instrucciones o acciones pendientes.",
        "properties": {
            "Asunto / referencia": {"title": {}},
            "Remitente": {"rich_text": {}},
            "Fecha importante": {"date": {}},
            "Adjunto / link": {"url": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Pendiente", "color": "yellow"},
                        {"name": "Registrado", "color": "green"},
                        {"name": "Revisar", "color": "orange"},
                    ]
                }
            },
            "Notas": {"rich_text": {}},
        },
    },
    "source_pdfs_apuntes": {
        "database_key": "capture_pdfs_apuntes",
        "database_name": "Registro PDFs / Apuntes",
        "title_property": "Documento / apunte",
        "seed_title": "Primer documento / apunte",
        "helper": "Cargá dónde está el material y qué acción queda asociada a ese documento o apunte.",
        "properties": {
            "Documento / apunte": {"title": {}},
            "Ubicación": {"rich_text": {}},
            "Materia / tema": {"rich_text": {}},
            "Fecha relacionada": {"date": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Pendiente", "color": "yellow"},
                        {"name": "Ordenado", "color": "green"},
                        {"name": "Revisar", "color": "orange"},
                    ]
                }
            },
            "Notas": {"rich_text": {}},
        },
    },
}


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


def callout(text: str):
    return {
        "object": "block",
        "type": "callout",
        "callout": {"icon": {"type": "emoji", "emoji": "✍️"}, "rich_text": rt(text)},
    }


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
        console.print("[yellow]Ejecutá primero python install.py para crear PersonalOS en Notion.[/yellow]")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def save_mapping(mapping):
    Path(".personalos/notion_mappings_v2.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def resolve_token(config):
    token = os.getenv("NOTION_TOKEN") or config.get("notion", {}).get("token")
    if not token or "REPLACE" in token:
        console.print("[red]Missing valid NOTION_TOKEN. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    return token


def create_database(notion, parent_id, name, properties):
    return notion.databases.create(
        parent={"page_id": normalize_page_id(parent_id)},
        icon={"type": "emoji", "emoji": "🧾"},
        title=rt(name),
        properties=properties,
    )


def create_seed_row(notion, database_id, title_property, seed_title):
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            title_property: {"title": rt(seed_title)},
            "Estado": {"select": {"name": "Pendiente"}},
        },
    )


def append_capture_section(notion, page_id, db_url, helper):
    notion.blocks.children.append(
        block_id=normalize_page_id(page_id),
        children=[
            divider(),
            heading("Cargar información", 2),
            callout(helper),
            link_paragraph("🧾 Abrir registro de carga", db_url),
            paragraph("También podés cargar los datos directamente en la base que aparece en esta página."),
        ],
    )


def main():
    console.print(Panel("Creando registros de captura para fuentes de aprendizaje", title="◯ PersonalOS"))

    config = load_config()
    mapping = load_mapping()
    objects = mapping.setdefault("objects", {})
    notion = Client(auth=resolve_token(config))

    for source_key, capture in CAPTURE_CONFIG.items():
        source = objects.get(source_key)
        if not source:
            console.print(f"[yellow]Saltando {source_key}: no existe página fuente en mapping.[/yellow]")
            continue

        db_key = capture["database_key"]
        if db_key in objects:
            console.print(f"[dim]Ya existe: {capture['database_name']}[/dim]")
            continue

        db = create_database(notion, source["id"], capture["database_name"], capture["properties"])
        create_seed_row(notion, db["id"], capture["title_property"], capture["seed_title"])
        append_capture_section(notion, source["id"], db["url"], capture["helper"])

        objects[db_key] = {"id": db.get("id"), "url": db.get("url")}
        console.print(f"[green]Creado:[/green] {capture['database_name']}")

    save_mapping(mapping)
    console.print("[green]✓ Registros de captura creados correctamente.[/green]")


if __name__ == "__main__":
    main()

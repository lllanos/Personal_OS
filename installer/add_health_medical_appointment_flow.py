#!/usr/bin/env python3
"""Add Health / Medical Appointment guided flow to an existing PersonalOS install.

This script applies the lessons learned from Education:
- page-first experience
- visual quick sheet
- completion tracking
- clear navigation
- internal database only as backing structure

Run from installer directory:

    python add_health_medical_appointment_flow.py
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


def callout(text: str, icon: str = "🩺"):
    return {"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": icon}, "rich_text": rt(text)}}


def todo(text: str):
    return {"object": "block", "type": "to_do", "to_do": {"rich_text": rt(text), "checked": False}}


def table_row(left: str, right: str):
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {"cells": [rt(left), rt(right)]},
    }


def table_block(rows: list[tuple[str, str]]):
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": 2,
            "has_column_header": True,
            "has_row_header": False,
            "children": [table_row("Campo", "Completar"), *[table_row(k, v) for k, v in rows]],
        },
    }


def select_prop(options: list[tuple[str, str]]):
    return {"select": {"options": [{"name": name, "color": color} for name, color in options]}}


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


def create_page(notion, parent_id: str, title: str, icon: str, children: list[dict]):
    return notion.pages.create(
        parent={"page_id": normalize_page_id(parent_id)},
        icon={"type": "emoji", "emoji": icon},
        properties={"title": title_prop(title)},
        children=children,
    )


def create_database(notion, parent_id: str):
    return notion.databases.create(
        parent={"page_id": normalize_page_id(parent_id)},
        icon={"type": "emoji", "emoji": "🧾"},
        title=rt("Registro Turnos médicos"),
        properties={
            "Turno / tema": {"title": {}},
            "Persona": {"rich_text": {}},
            "Especialidad": {"rich_text": {}},
            "Médico / institución": {"rich_text": {}},
            "Fecha": {"date": {}},
            "Estado": select_prop([
                ("Pendiente", "yellow"),
                ("Pedido", "orange"),
                ("Confirmado", "green"),
                ("Realizado", "blue"),
                ("Esperando resultado", "purple"),
                ("Requiere acción", "red"),
                ("Cerrado", "gray"),
            ]),
            "Próxima acción": {"rich_text": {}},
            "Qué llevar": {"rich_text": {}},
            "Notas": {"rich_text": {}},
        },
    )


def create_seed_row(notion, db_id: str):
    notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Turno / tema": {"title": rt("Primer turno médico")},
            "Estado": {"select": {"name": "Pendiente"}},
            "Próxima acción": {"rich_text": rt("Definir si hay que pedir turno o confirmar fecha.")},
        },
    )


def append(notion, page_id: str, blocks: list[dict]):
    notion.blocks.children.append(block_id=normalize_page_id(page_id), children=blocks)


def main():
    console.print(Panel("Agregando módulo Salud / Turno médico", title="◯ PersonalOS"))
    config = load_config()
    mapping = load_mapping()
    objects = mapping.setdefault("objects", {})
    notion = Client(auth=resolve_token(config))

    if objects.get("health_home"):
        console.print("[yellow]El módulo Salud ya existe en el mapping. No se duplica.[/yellow]")
        return 0

    root = obj(mapping, "root")
    refugio = obj(mapping, "refugio")
    bitacora = obj(mapping, "bitacora")

    health_home = create_page(notion, root["id"], "Salud", "🩺", [
        heading("Salud", 1),
        callout("Un lugar para no perder turnos, estudios, medicación, documentos y próximas acciones de salud.", "🩺"),
        heading("¿Qué necesitás organizar?", 2),
        bulleted("Turno médico"),
        bulleted("Medicación"),
        bulleted("Estudio / análisis"),
        bulleted("Control periódico"),
        bulleted("Síntoma / seguimiento"),
        bulleted("Documento médico"),
        divider(),
        callout("Por ahora empezamos con Turno médico para validar el flujo sin convertirlo en planilla.", "🌿"),
    ])
    objects["health_home"] = {"id": health_home.get("id"), "url": health_home.get("url")}

    appointment_flow = create_page(notion, health_home["id"], "Turno médico", "📅", [
        heading("Turno médico", 1),
        callout("No hace falta cargar todo perfecto. La meta es que el turno no se pierda y que quede clara la próxima acción.", "📅"),
        heading("Ficha rápida visual", 2),
        table_block([
            ("Persona", "escribir aquí"),
            ("Especialidad / motivo", "escribir aquí"),
            ("Médico / institución", "escribir aquí"),
            ("Fecha / pendiente", "escribir aquí"),
            ("Lugar / modalidad", "escribir aquí"),
            ("Qué llevar", "escribir aquí"),
            ("Documento / estudio relacionado", "escribir aquí"),
            ("Próxima acción", "escribir el siguiente paso"),
            ("Notas", "escribir aquí"),
        ]),
        heading("Qué llevar / preparar", 2),
        todo("DNI / credencial / obra social, si aplica."),
        todo("Estudios anteriores o documentos relacionados."),
        todo("Lista de medicación actual, si aplica."),
        todo("Preguntas para el médico."),
        heading("Seguimiento para finalizar", 2),
        callout("Cuando estos puntos estén claros, el turno está suficientemente organizado para avanzar.", "✅"),
        todo("Sé para quién es."),
        todo("Sé el motivo o especialidad."),
        todo("Hay fecha o está claro que falta pedirla."),
        todo("Sé qué llevar o revisar antes."),
        todo("Hay una próxima acción concreta."),
        divider(),
        heading("Estado sugerido", 2),
        bulleted("Pendiente: todavía falta pedir o confirmar."),
        bulleted("Confirmado: ya tiene fecha/lugar."),
        bulleted("Realizado: el turno ya ocurrió."),
        bulleted("Esperando resultado: falta informe, indicación o devolución."),
        bulleted("Requiere acción: hay que hacer algo después del turno."),
    ])
    objects["health_appointment_flow"] = {"id": appointment_flow.get("id"), "url": appointment_flow.get("url")}

    db = create_database(notion, appointment_flow["id"])
    objects["health_appointment_db"] = {"id": db.get("id"), "url": db.get("url")}
    create_seed_row(notion, db["id"])

    append(notion, appointment_flow["id"], [
        divider(),
        heading("Registro interno", 2),
        callout("La base existe como respaldo estructurado. La ficha visual de arriba es el camino principal.", "🧾"),
        link_paragraph("🧾 Abrir Registro Turnos médicos", db["url"]),
        divider(),
        heading("Navegación", 2),
        link_paragraph("🩺 Volver a Salud", health_home["url"]),
        link_paragraph("🍃 Volver al Refugio", refugio["url"]),
        link_paragraph("📖 Registrar reflexión en Bitácora", bitacora["url"]),
    ])

    append(notion, health_home["id"], [
        heading("Flujos disponibles", 2),
        link_paragraph("📅 Turno médico", appointment_flow["url"]),
        divider(),
        heading("Navegación", 2),
        link_paragraph("🍃 Volver al Refugio", refugio["url"]),
    ])

    append(notion, root["id"], [
        divider(),
        heading("Nuevo dominio", 2),
        link_paragraph("🩺 Salud", health_home["url"]),
    ])

    append(notion, refugio["id"], [
        divider(),
        heading("Otro dominio disponible", 2),
        link_paragraph("🩺 Salud", health_home["url"]),
    ])

    save_mapping(mapping)
    console.print("[green]✓ Módulo Salud / Turno médico agregado correctamente.[/green]")
    console.print("Abrí Salud desde PersonalOS o Refugio para probar el nuevo flujo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""PersonalOS Notion Installer v0.1.1 Seed.

This installer intentionally keeps Notion payloads conservative.
Notion accepts only a restricted subset of emojis for page/database icons, so
all icons sent to the API pass through a small safe registry.
"""

from __future__ import annotations

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

from components import (
    closing_ritual_components,
    focus_ritual_components,
    morning_ritual_components,
    pause_ritual_components,
    refuge_components,
    rt,
)

console = Console()

# Notion-safe icon registry.
# Avoid symbolic glyphs such as "◯" as page/database icons; Notion rejects them.
ICONS: dict[str, str] = {
    "root": "🌱",
    "refuge": "🌱",
    "people": "👤",
    "missions": "🎯",
    "habits": "🌱",
    "morning": "🌅",
    "focus": "🎯",
    "pause": "☕",
    "closing": "🌙",
    "fallback": "🌱",
}

PAGE_ID_RE = re.compile(
    r"([a-fA-F0-9]{32}|[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
)


def title_prop(text: str) -> dict[str, Any]:
    return {"title": rt(text)}


def rich_text_prop(text: str) -> dict[str, Any]:
    return {"rich_text": rt(text)}


def select_prop(options: list[tuple[str, str]]) -> dict[str, Any]:
    return {"select": {"options": [{"name": name, "color": color} for name, color in options]}}


def safe_icon(icon_key: str) -> str:
    return ICONS.get(icon_key, ICONS["fallback"])


def normalize_page_id(value: str) -> str:
    """Accept a plain Notion page id or a full Notion URL and return a page id."""
    match = PAGE_ID_RE.search(value or "")
    if not match:
        return value
    return match.group(1).replace("-", "")


def load_config() -> dict[str, Any]:
    config_path = Path("config.yaml")
    if not config_path.exists():
        config_path = Path("config.example.yaml")
    if not config_path.exists():
        console.print("[red]No config.yaml or config.example.yaml found.[/red]")
        sys.exit(1)
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def resolve_settings(config: dict[str, Any]) -> tuple[str, str]:
    token = os.getenv("NOTION_TOKEN") or config.get("notion", {}).get("token")
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID") or config.get("notion", {}).get("parent_page_id")
    if not token or "REPLACE" in token:
        console.print("[red]Missing NOTION_TOKEN. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    if not parent_page_id:
        console.print("[red]Missing NOTION_PARENT_PAGE_ID. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    return token, normalize_page_id(parent_page_id)


class PersonalOSInstaller:
    def __init__(self, notion: Client, parent_page_id: str, config: dict[str, Any]) -> None:
        self.notion = notion
        self.parent_page_id = parent_page_id
        self.config = config
        self.people_ids: dict[str, str] = {}

    def create_page(self, parent_id: str, name: str, icon_key: str, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        try:
            return self.notion.pages.create(
                parent={"page_id": parent_id},
                icon={"type": "emoji", "emoji": safe_icon(icon_key)},
                properties={"title": title_prop(name)},
                children=children or [],
            )
        except APIResponseError as exc:
            console.print(f"[red]Notion rejected page creation for:[/red] {name}")
            console.print(f"[yellow]Icon key:[/yellow] {icon_key} -> {safe_icon(icon_key)}")
            console.print(f"[yellow]Message:[/yellow] {exc}")
            raise

    def create_database(self, parent_id: str, name: str, icon_key: str, properties: dict[str, Any]) -> dict[str, Any]:
        try:
            return self.notion.databases.create(
                parent={"page_id": parent_id},
                icon={"type": "emoji", "emoji": safe_icon(icon_key)},
                title=rt(name),
                properties=properties,
            )
        except APIResponseError as exc:
            console.print(f"[red]Notion rejected database creation for:[/red] {name}")
            console.print(f"[yellow]Icon key:[/yellow] {icon_key} -> {safe_icon(icon_key)}")
            console.print(f"[yellow]Message:[/yellow] {exc}")
            raise

    def create_db_item(self, database_id: str, properties: dict[str, Any], children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return self.notion.pages.create(parent={"database_id": database_id}, properties=properties, children=children or [])

    def run(self) -> None:
        console.print(Panel("🍃 Preparando tu Refugio...", title="◯ PersonalOS Installer", subtitle="v0.1.1 Seed"))
        root = self.create_root()
        people_db = self.create_people_db(root["id"])
        missions_db = self.create_missions_db(root["id"], people_db["id"])
        habits_db = self.create_habits_db(root["id"], people_db["id"])
        self.seed_people(people_db["id"])
        self.seed_missions(missions_db["id"])
        self.seed_habits(habits_db["id"])
        refuge = self.create_refuge(root["id"], missions_db["id"], habits_db["id"], people_db["id"])
        rituals = self.create_rituals(root["id"])
        console.print("\n[green]☀ Tu Refugio está listo.[/green]")
        console.print(f"Raíz: {root['url']}")
        console.print(f"Refugio: {refuge['url']}")
        for name, page in rituals.items():
            console.print(f"{name}: {page['url']}")
        console.print(f"Personas: {people_db['url']}")
        console.print(f"Misiones: {missions_db['url']}")
        console.print(f"Hábitos: {habits_db['url']}")

    def create_root(self) -> dict[str, Any]:
        console.print("🍃 Creando raíz PersonalOS...")
        return self.create_page(
            self.parent_page_id,
            self.config.get("personalos", {}).get("title", "◯ PersonalOS"),
            "root",
            [
                {"object": "block", "type": "heading_1", "heading_1": {"rich_text": rt("◯ PersonalOS")}},
                {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt("Un refugio digital para recuperar armonía, claridad y dirección.")}},
                {"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": safe_icon("refuge")}, "rich_text": rt("Hoy no hace falta resolver todo. Solo caminar el siguiente paso.")}},
            ],
        )

    def create_people_db(self, root_id: str) -> dict[str, Any]:
        console.print("👤 Creando Personas...")
        return self.create_database(
            root_id,
            "👤 Personas",
            "people",
            {
                "Nombre": {"title": {}},
                "Rol": select_prop([("Hija", "pink"), ("Hijo Mayor", "blue"), ("Hijo Menor", "green"), ("Madre", "purple"), ("Luis", "gray"), ("Familia", "orange")]),
                "Activo": {"checkbox": {}},
                "Tema": select_prop([("Zen", "green"), ("Bosque", "green"), ("Mar", "blue"), ("Montaña", "gray"), ("Minimal", "default")]),
                "Estación": select_prop([("Primavera", "green"), ("Verano", "yellow"), ("Otoño", "orange"), ("Invierno", "blue")]),
            },
        )

    def create_missions_db(self, root_id: str, people_db_id: str) -> dict[str, Any]:
        console.print("🪨 Preparando el Camino...")
        return self.create_database(
            root_id,
            "🎯 Misiones",
            "missions",
            {
                "Misión": {"title": {}},
                "Persona": {"relation": {"database_id": people_db_id, "single_property": {}}},
                "Estado": select_prop([("Pendiente", "gray"), ("En camino", "yellow"), ("Pausa", "blue"), ("Completada", "green")]),
                "Momento": select_prop([("Amanecer", "yellow"), ("Foco", "green"), ("Pausa", "blue"), ("Cierre", "purple")]),
                "Dominio": select_prop([("Educación", "blue"), ("Hogar", "green"), ("Salud", "red"), ("Familia", "orange"), ("Personal", "purple")]),
                "Tiempo": {"number": {"format": "number"}},
                "Balance": select_prop([("Sereno", "green"), ("Cargado", "yellow"), ("Necesita pausa", "blue"), ("En movimiento", "orange")]),
                "Siguiente paso": {"rich_text": {}},
                "Después": {"rich_text": {}},
            },
        )

    def create_habits_db(self, root_id: str, people_db_id: str) -> dict[str, Any]:
        console.print("🌱 Plantando hábitos...")
        return self.create_database(
            root_id,
            "🌱 Hábitos",
            "habits",
            {
                "Hábito": {"title": {}},
                "Persona": {"relation": {"database_id": people_db_id, "single_property": {}}},
                "Estado": select_prop([("Activo", "green"), ("Pausado", "yellow"), ("Descanso", "blue")]),
                "Frecuencia": select_prop([("Diario", "green"), ("Lunes a viernes", "blue"), ("Semanal", "yellow"), ("Cuando haga falta", "gray")]),
                "Hoy": {"checkbox": {}},
            },
        )

    def seed_people(self, people_db_id: str) -> None:
        season = self.config.get("personalos", {}).get("season", "Otoño")
        theme = self.config.get("personalos", {}).get("theme", "zen").capitalize()
        for person in self.config.get("people", []):
            page = self.create_db_item(
                people_db_id,
                {
                    "Nombre": title_prop(person["name"]),
                    "Rol": {"select": {"name": person["role"]}},
                    "Activo": {"checkbox": True},
                    "Tema": {"select": {"name": theme}},
                    "Estación": {"select": {"name": season}},
                },
            )
            self.people_ids[person["role"]] = page["id"]

    def seed_missions(self, missions_db_id: str) -> None:
        primary_role = self.config.get("personalos", {}).get("primary_person", "Hija")
        person_id = self.people_ids.get(primary_role) or next(iter(self.people_ids.values()))
        seeds = [
            ("Abrir Classroom", "En camino", "Amanecer", "Educación", 3, "Sereno", "Abrir Classroom.", "Leer la consigna."),
            ("Leer la consigna", "Pendiente", "Foco", "Educación", 5, "Sereno", "Leer solo la consigna, sin resolver todavía.", "Subrayar qué hay que entregar."),
        ]
        for mission, status, moment, domain, minutes, balance, next_step, after in seeds:
            self.create_db_item(
                missions_db_id,
                {
                    "Misión": title_prop(mission),
                    "Persona": {"relation": [{"id": person_id}]},
                    "Estado": {"select": {"name": status}},
                    "Momento": {"select": {"name": moment}},
                    "Dominio": {"select": {"name": domain}},
                    "Tiempo": {"number": minutes},
                    "Balance": {"select": {"name": balance}},
                    "Siguiente paso": rich_text_prop(next_step),
                    "Después": rich_text_prop(after),
                },
            )

    def seed_habits(self, habits_db_id: str) -> None:
        primary_role = self.config.get("personalos", {}).get("primary_person", "Hija")
        person_id = self.people_ids.get(primary_role) or next(iter(self.people_ids.values()))
        for habit in ["💧 Tomar agua", "🎒 Preparar mochila", "🌙 Preparar descanso"]:
            self.create_db_item(
                habits_db_id,
                {
                    "Hábito": title_prop(habit),
                    "Persona": {"relation": [{"id": person_id}]},
                    "Estado": {"select": {"name": "Activo"}},
                    "Frecuencia": {"select": {"name": "Diario"}},
                    "Hoy": {"checkbox": False},
                },
            )

    def create_refuge(self, root_id: str, missions_db_id: str, habits_db_id: str, people_db_id: str) -> dict[str, Any]:
        console.print("🍃 Creando Refugio desde componentes...")
        return self.create_page(root_id, "🍃 Refugio", "refuge", refuge_components(missions_db_id, habits_db_id, people_db_id))

    def create_rituals(self, root_id: str) -> dict[str, dict[str, Any]]:
        console.print("🌅 Creando rituales iniciales...")
        return {
            "Ritual del Amanecer": self.create_page(root_id, "🌅 Ritual del Amanecer", "morning", morning_ritual_components()),
            "Ritual del Foco": self.create_page(root_id, "🎯 Ritual del Foco", "focus", focus_ritual_components()),
            "Ritual de Pausa": self.create_page(root_id, "☕ Ritual de Pausa", "pause", pause_ritual_components()),
            "Ritual del Cierre": self.create_page(root_id, "🌙 Ritual del Cierre", "closing", closing_ritual_components()),
        }


def main() -> None:
    config = load_config()
    token, parent_page_id = resolve_settings(config)
    installer = PersonalOSInstaller(Client(auth=token), parent_page_id, config)
    installer.run()


if __name__ == "__main__":
    main()

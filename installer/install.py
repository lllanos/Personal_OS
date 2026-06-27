#!/usr/bin/env python3
"""PersonalOS Notion Installer v2.0 Seed.

PersonalOS v2 is not a documentation installer.
It creates an evaluable Notion experience: Refugio, Camino, Jardin, Bitacora,
Companion selection, and the first Resource setup.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from notion_client import Client
from notion_client.errors import APIResponseError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

INSTALLER_VERSION = "2.0.0-seed"
SCHEMA_VERSION = "2.0"

ICONS: dict[str, str] = {
    "root": "🌱",
    "refugio": "🍃",
    "camino": "🧭",
    "paso": "👣",
    "jardin": "🌿",
    "bitacora": "📖",
    "persona": "👤",
    "resource": "📚",
    "aurora": "🌸",
    "samwise": "🌿",
    "mellon": "🍃",
    "fallback": "🌱",
}

PAGE_ID_RE = re.compile(
    r"([a-fA-F0-9]{32}|[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
)

PROFILE_OPTIONS = {
    "1": "Adulto",
    "2": "Adolescente",
    "3": "Niño",
    "4": "Otra persona",
}

COMPANION_OPTIONS = {
    "1": "Aurora",
    "2": "Samwise",
}

CLASSROOM_OPTIONS = {
    "1": "Navegador",
    "2": "Aplicación",
    "3": "Más tarde",
}


@dataclass
class FirstExperience:
    profile: str
    display_name: str
    companion: str
    classroom_mode: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_icon(icon_key: str) -> str:
    return ICONS.get(icon_key, ICONS["fallback"])


def normalize_page_id(value: str) -> str:
    match = PAGE_ID_RE.search(value or "")
    if not match:
        return value
    return match.group(1).replace("-", "")


def rt(text: str, link: str | None = None) -> list[dict[str, Any]]:
    item: dict[str, Any] = {"type": "text", "text": {"content": text}}
    if link:
        item["text"]["link"] = {"url": link}
    return [item]


def title_prop(text: str) -> dict[str, Any]:
    return {"title": rt(text)}


def rich_text_prop(text: str) -> dict[str, Any]:
    return {"rich_text": rt(text)}


def select_prop(options: list[tuple[str, str]]) -> dict[str, Any]:
    return {"select": {"options": [{"name": name, "color": color} for name, color in options]}}


def paragraph(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def heading(text: str, level: int = 2) -> dict[str, Any]:
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rt(text)}}


def callout(text: str, icon_key: str = "refugio") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": safe_icon(icon_key)},
            "rich_text": rt(text),
        },
    }


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def link_paragraph(label: str, url: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(label, url)}}


def load_config() -> dict[str, Any]:
    config_path = Path("config.yaml")
    if not config_path.exists():
        config_path = Path("config.example.yaml")
    if not config_path.exists():
        console.print("[red]No config.yaml or config.example.yaml found.[/red]")
        sys.exit(1)
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def resolve_settings(config: dict[str, Any]) -> tuple[str, str]:
    notion_cfg = config.get("notion", {})
    token = os.getenv("NOTION_TOKEN") or notion_cfg.get("token")
    parent_page_id = (
        os.getenv("NOTION_PARENT_PAGE_ID")
        or notion_cfg.get("parent_page_id")
        or notion_cfg.get("parent_page")
    )
    if not token or "REPLACE" in token:
        console.print("[red]Missing NOTION_TOKEN. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    if not parent_page_id:
        console.print("[red]Missing NOTION_PARENT_PAGE_ID / parent_page. Export it or set it in config.yaml.[/red]")
        sys.exit(1)
    return token, normalize_page_id(parent_page_id)


def choose_from(title: str, options: dict[str, str]) -> str:
    console.print(f"\n[bold]{title}[/bold]")
    for key, value in options.items():
        console.print(f"  {key}. {value}")
    choice = Prompt.ask("Elegí una opción", choices=list(options.keys()), default="1")
    return options[choice]


def run_first_experience() -> FirstExperience:
    console.print(
        Panel(
            "Bienvenido.\n\nHoy vamos a preparar tu Refugio.\nNo hace falta resolver toda la vida hoy.\nSolo dar el primer paso.",
            title="🍃 PersonalOS v2",
            subtitle="First Experience",
        )
    )

    profile = choose_from("¿Para quién estamos preparando este Refugio?", PROFILE_OPTIONS)
    display_name = Prompt.ask("\n¿Cómo querés que te llame?").strip() or "Persona"

    console.print("\nCada persona prefiere ser acompañada de una manera distinta.")
    console.print("[dim]Aurora: presencia serena. Samwise: compañero de camino.[/dim]")
    companion = choose_from("¿Cómo preferís que te acompañe?", COMPANION_OPTIONS)

    classroom_mode = choose_from("¿Cómo preferís abrir Classroom cuando haga falta?", CLASSROOM_OPTIONS)

    console.print("\n[green]Perfecto.[/green]")
    console.print("Ya tengo lo necesario. El resto lo iremos descubriendo juntos.\n")
    Prompt.ask("Mellon. Presioná ENTER para preparar tu Refugio", default="")

    return FirstExperience(
        profile=profile,
        display_name=display_name,
        companion=companion,
        classroom_mode=classroom_mode,
    )


class PersonalOSV2Installer:
    def __init__(self, notion: Client, parent_page_id: str, config: dict[str, Any], fx: FirstExperience) -> None:
        self.notion = notion
        self.parent_page_id = parent_page_id
        self.config = config
        self.fx = fx
        self.mapping: dict[str, Any] = {
            "installer_version": INSTALLER_VERSION,
            "schema_version": SCHEMA_VERSION,
            "created_at": now_iso(),
            "first_experience": asdict(fx),
            "objects": {},
        }

    def save_mapping(self) -> None:
        target_dir = Path(".personalos")
        target_dir.mkdir(exist_ok=True)
        path = target_dir / "notion_mappings_v2.json"
        path.write_text(json.dumps(self.mapping, ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"[dim]Mapping local guardado en {path}[/dim]")

    def remember(self, key: str, obj: dict[str, Any]) -> dict[str, Any]:
        self.mapping["objects"][key] = {
            "id": obj.get("id"),
            "url": obj.get("url"),
            "created_at": now_iso(),
        }
        return obj

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
            console.print(f"[yellow]Message:[/yellow] {exc}")
            raise

    def create_db_item(self, database_id: str, properties: dict[str, Any], children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return self.notion.pages.create(parent={"database_id": database_id}, properties=properties, children=children or [])

    def append_blocks(self, page_id: str, blocks: list[dict[str, Any]]) -> None:
        if not blocks:
            return
        self.notion.blocks.children.append(block_id=page_id, children=blocks)

    def companion_welcome(self) -> str:
        if self.fx.companion == "Samwise":
            return f"Qué bueno verte, {self.fx.display_name}. Todavía queda camino, pero hoy alcanza con un paso."
        return f"Bienvenido, {self.fx.display_name}. Hoy alcanza con un solo paso."

    def companion_closing(self) -> str:
        if self.fx.companion == "Samwise":
            return "Si el camino pesa, lo hacemos más liviano. Un paso sigue siendo camino."
        return "No hace falta resolver todo. El Refugio va a seguir acá cuando lo necesites."

    def run(self) -> None:
        console.print("🌱 Preparando tu Refugio...")
        root = self.remember("root", self.create_root())

        console.print("🌿 Plantando Mi Jardín...")
        jardin = self.remember("jardin", self.create_jardin(root["id"]))
        persona_db = self.remember("persona_db", self.create_persona_db(jardin["id"]))
        resources_db = self.remember("resources_db", self.create_resources_db(jardin["id"]))
        companion_page = self.remember("companion", self.create_companion_page(jardin["id"]))

        console.print("🧭 Trazando el primer Camino...")
        camino = self.remember("camino", self.create_camino(root["id"]))

        console.print("📖 Preparando la Bitácora...")
        bitacora = self.remember("bitacora", self.create_bitacora(root["id"]))

        console.print("📚 Configurando Classroom como primer Recurso...")
        self.seed_persona(persona_db["id"])
        self.seed_classroom(resources_db["id"])

        console.print("🍃 Abriendo el Refugio...")
        refugio = self.remember("refugio", self.create_refugio(root["id"], camino["url"], jardin["url"], bitacora["url"]))

        self.append_root_navigation(root["id"], refugio["url"], camino["url"], jardin["url"], bitacora["url"], companion_page["url"])
        self.save_mapping()

        console.print("\n[green]Mellon.[/green]")
        console.print("Tu Refugio está listo.\n")
        console.print(f"PersonalOS: {root['url']}")
        console.print(f"Refugio: {refugio['url']}")
        console.print(f"Camino: {camino['url']}")
        console.print(f"Mi Jardín: {jardin['url']}")
        console.print(f"Bitácora: {bitacora['url']}")

    def create_root(self) -> dict[str, Any]:
        return self.create_page(
            self.parent_page_id,
            "PersonalOS",
            "root",
            [
                heading("PersonalOS", 1),
                paragraph("Un Refugio digital para recuperar calma, claridad y dirección."),
                callout(self.companion_welcome(), "refugio"),
                paragraph(f"Companion elegido: {self.fx.companion}"),
                paragraph(f"Perfil inicial: {self.fx.profile}"),
                divider(),
                paragraph("Este espacio fue creado para evaluar PersonalOS v2 como experiencia viva, no como documentación técnica."),
            ],
        )

    def append_root_navigation(self, root_id: str, refugio_url: str, camino_url: str, jardin_url: str, bitacora_url: str, companion_url: str) -> None:
        self.append_blocks(
            root_id,
            [
                heading("Entrar", 2),
                link_paragraph("🍃 Refugio", refugio_url),
                link_paragraph("🧭 Camino", camino_url),
                link_paragraph("🌿 Mi Jardín", jardin_url),
                link_paragraph("📖 Bitácora", bitacora_url),
                link_paragraph(f"🤝 Companion: {self.fx.companion}", companion_url),
            ],
        )

    def create_refugio(self, root_id: str, camino_url: str, jardin_url: str, bitacora_url: str) -> dict[str, Any]:
        return self.create_page(
            root_id,
            "Refugio",
            "refugio",
            [
                heading(f"Bienvenido, {self.fx.display_name}.", 1),
                callout(self.companion_welcome(), "refugio"),
                heading("Tu Camino", 2),
                paragraph("Hoy no hace falta ver todo. Solo el siguiente paso."),
                link_paragraph("🧭 Ir al Camino", camino_url),
                heading("Tu siguiente paso", 2),
                callout("Abrir Classroom. Si todavía no está listo, PersonalOS ya preparó el recurso en Mi Jardín.", "paso"),
                heading("Cuando termines", 2),
                link_paragraph("📖 Dejar una pequeña reflexión", bitacora_url),
                heading("Cuidar el espacio", 2),
                link_paragraph("🌿 Ir a Mi Jardín", jardin_url),
                divider(),
                paragraph(self.companion_closing()),
            ],
        )

    def create_camino(self, root_id: str) -> dict[str, Any]:
        resource_hint = "Classroom se abrirá desde navegador." if self.fx.classroom_mode == "Navegador" else "Classroom quedó preparado según tu preferencia."
        if self.fx.classroom_mode == "Más tarde":
            resource_hint = "Classroom quedó pendiente para configurar más tarde."
        return self.create_page(
            root_id,
            "Camino",
            "camino",
            [
                heading("Camino inicial", 1),
                paragraph("Preparar el primer estudio."),
                callout("Un solo paso visible. Nada más.", "camino"),
                heading("Paso actual", 2),
                paragraph("Abrir Classroom."),
                callout(resource_hint, "resource"),
                paragraph("Cuando termines, volvé al Refugio o dejá una reflexión en la Bitácora."),
            ],
        )

    def create_jardin(self, root_id: str) -> dict[str, Any]:
        return self.create_page(
            root_id,
            "Mi Jardín",
            "jardin",
            [
                heading("Mi Jardín", 1),
                paragraph("Acá crecen las personas, recursos y preferencias del Refugio."),
                callout("Por ahora solo necesitamos lo esencial: Persona, Companion y Classroom.", "jardin"),
            ],
        )

    def create_companion_page(self, jardin_id: str) -> dict[str, Any]:
        if self.fx.companion == "Samwise":
            title = "Samwise"
            icon = "samwise"
            description = "Compañero de camino. Cercano, simple y constante."
            phrase = "Un paso más también cuenta."
        else:
            title = "Aurora"
            icon = "aurora"
            description = "Presencia serena. Calma, suave y contemplativa."
            phrase = "Hoy alcanza con algo pequeño."
        return self.create_page(
            jardin_id,
            title,
            icon,
            [
                heading(title, 1),
                paragraph(description),
                callout(phrase, icon),
                paragraph("El Companion cambia la voz de PersonalOS, no sus principios."),
            ],
        )

    def create_bitacora(self, root_id: str) -> dict[str, Any]:
        return self.create_page(
            root_id,
            "Bitácora",
            "bitacora",
            [
                heading("Bitácora", 1),
                paragraph("No es un historial. Es memoria con significado."),
                callout("Después del primer paso, podés registrar cómo fue. También podés no responder.", "bitacora"),
                heading("Primera reflexión", 2),
                paragraph("¿Cómo fue este paso?"),
                paragraph("Más claro / Más tranquilo / Igual / Prefiero no responder"),
                paragraph("Notas libres:"),
            ],
        )

    def create_persona_db(self, jardin_id: str) -> dict[str, Any]:
        return self.create_database(
            jardin_id,
            "Persona",
            "persona",
            {
                "Nombre": {"title": {}},
                "Perfil": select_prop([("Adulto", "blue"), ("Adolescente", "green"), ("Niño", "yellow"), ("Otra persona", "gray")]),
                "Companion": select_prop([("Aurora", "pink"), ("Samwise", "green")]),
                "Estado": select_prop([("Activo", "green"), ("Descansando", "blue")]),
            },
        )

    def create_resources_db(self, jardin_id: str) -> dict[str, Any]:
        return self.create_database(
            jardin_id,
            "Recursos",
            "resource",
            {
                "Recurso": {"title": {}},
                "Tipo": select_prop([("Educación", "blue"), ("Documento", "gray"), ("Aplicación", "green"), ("Sitio web", "purple")]),
                "Estado": select_prop([("Descubierto", "gray"), ("Configurado", "green"), ("Más tarde", "yellow")]),
                "Modo": select_prop([("Navegador", "blue"), ("Aplicación", "green"), ("Más tarde", "yellow")]),
                "URL": {"url": {}},
                "Notas": {"rich_text": {}},
            },
        )

    def seed_persona(self, persona_db_id: str) -> None:
        page = self.create_db_item(
            persona_db_id,
            {
                "Nombre": title_prop(self.fx.display_name),
                "Perfil": {"select": {"name": self.fx.profile}},
                "Companion": {"select": {"name": self.fx.companion}},
                "Estado": {"select": {"name": "Activo"}},
            },
        )
        self.remember("persona", page)

    def seed_classroom(self, resources_db_id: str) -> None:
        status = "Más tarde" if self.fx.classroom_mode == "Más tarde" else "Configurado"
        url = "https://classroom.google.com" if self.fx.classroom_mode == "Navegador" else None
        props: dict[str, Any] = {
            "Recurso": title_prop("Classroom"),
            "Tipo": {"select": {"name": "Educación"}},
            "Estado": {"select": {"name": status}},
            "Modo": {"select": {"name": self.fx.classroom_mode}},
            "Notas": rich_text_prop("Primer recurso de PersonalOS v2. Se configura una sola vez."),
        }
        if url:
            props["URL"] = {"url": url}
        page = self.create_db_item(resources_db_id, props)
        self.remember("resource_classroom", page)


def main() -> None:
    config = load_config()
    token, parent_page_id = resolve_settings(config)
    first_experience = run_first_experience()
    installer = PersonalOSV2Installer(Client(auth=token), parent_page_id, config, first_experience)
    installer.run()


if __name__ == "__main__":
    main()

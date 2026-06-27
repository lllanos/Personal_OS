#!/usr/bin/env python3
"""PersonalOS Notion Installer v2.1 Seed.

PersonalOS v2 creates an evaluable Notion experience.
This version adds safer test modes, avoids confusing duplicate roots,
and improves the Education / Classroom onboarding.
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
from rich.prompt import Confirm, Prompt

console = Console()

INSTALLER_VERSION = "2.1.0-seed"
SCHEMA_VERSION = "2.1"
CANONICAL_REPOSITORY = "lllanos/Personal_OS"

ICONS: dict[str, str] = {
    "root": "🌱",
    "refugio": "🍃",
    "camino": "🧭",
    "paso": "👣",
    "jardin": "🌿",
    "bitacora": "📖",
    "persona": "👤",
    "resource": "📚",
    "educacion": "🎒",
    "classroom": "🏫",
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

INSTALL_MODE_OPTIONS = {
    "1": "Instalación limpia de prueba: archivar PersonalOS anteriores y crear uno nuevo",
    "2": "Copia nueva: crear PersonalOS con nombre único sin archivar anteriores",
    "3": "Upgrade local: mantener Notion como está y solo usar mapping local si existe",
}

LEARNING_CONTEXT_OPTIONS = {
    "1": "Colegio primario",
    "2": "Colegio secundario",
    "3": "Carrera universitaria / terciaria",
    "4": "Curso online",
    "5": "Capacitación laboral",
    "6": "Estudio personal",
    "7": "Otro",
}

CLASSROOM_USAGE_OPTIONS = {
    "1": "Sí, usa Google Classroom",
    "2": "No usa Google Classroom",
    "3": "No sé todavía",
}

CLASSROOM_OPEN_OPTIONS = {
    "1": "Navegador",
    "2": "Aplicación",
    "3": "Más tarde",
}


@dataclass
class FirstExperience:
    install_mode: str
    profile: str
    display_name: str
    companion: str
    learning_context: str
    classroom_usage: str
    classroom_open_mode: str
    classroom_url: str | None
    classroom_notes: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_label() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M")


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


def bulleted(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text)}}


def numbered(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": rt(text)}}


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


def choose_from(title: str, options: dict[str, str], default: str = "1") -> str:
    console.print(f"\n[bold]{title}[/bold]")
    for key, value in options.items():
        console.print(f"  {key}. {value}")
    choice = Prompt.ask("Elegí una opción", choices=list(options.keys()), default=default)
    return options[choice]


def ask_optional_url(prompt: str) -> str | None:
    value = Prompt.ask(prompt, default="").strip()
    return value or None


def run_first_experience() -> FirstExperience:
    console.print(
        Panel(
            "Bienvenido.\n\nHoy vamos a preparar tu Refugio.\nNo hace falta resolver toda la vida hoy.\nSolo dar el primer paso.",
            title="🍃 PersonalOS v2.1",
            subtitle="First Experience",
        )
    )

    install_mode = choose_from("¿Cómo querés instalar esta prueba?", INSTALL_MODE_OPTIONS, default="1")
    profile = choose_from("¿Para quién estamos preparando este Refugio?", PROFILE_OPTIONS)
    display_name = Prompt.ask("\n¿Cómo querés que te llame?").strip() or "Persona"

    console.print("\nCada persona prefiere ser acompañada de una manera distinta.")
    console.print("[dim]Aurora: presencia serena. Samwise: compañero de camino.[/dim]")
    companion = choose_from("¿Cómo preferís que te acompañe?", COMPANION_OPTIONS)

    learning_context = choose_from("¿Qué tipo de aprendizaje querés organizar primero?", LEARNING_CONTEXT_OPTIONS)
    classroom_usage = choose_from("¿Este aprendizaje usa Google Classroom?", CLASSROOM_USAGE_OPTIONS)

    classroom_open_mode = "Más tarde"
    classroom_url = None
    classroom_notes = ""

    if classroom_usage == "Sí, usa Google Classroom":
        classroom_open_mode = choose_from("¿Cómo preferís abrir Classroom cuando haga falta?", CLASSROOM_OPEN_OPTIONS)
        classroom_url = ask_optional_url("Pegá el link de Classroom si ya lo tenés. Si no, ENTER")
        classroom_notes = Prompt.ask(
            "¿Qué necesitás recordar sobre este Classroom?",
            default="Revisar materias, tareas pendientes y próximas entregas.",
        ).strip()
    elif classroom_usage == "No sé todavía":
        classroom_notes = "Confirmar si la institución usa Google Classroom u otra plataforma."
    else:
        classroom_notes = "No usa Classroom. PersonalOS organizará este aprendizaje por materias, tareas, documentos y fechas."

    console.print("\n[green]Perfecto.[/green]")
    console.print("Ya tengo lo necesario. El resto lo iremos descubriendo juntos.\n")
    Prompt.ask("Mellon. Presioná ENTER para preparar tu Refugio", default="")

    return FirstExperience(
        install_mode=install_mode,
        profile=profile,
        display_name=display_name,
        companion=companion,
        learning_context=learning_context,
        classroom_usage=classroom_usage,
        classroom_open_mode=classroom_open_mode,
        classroom_url=classroom_url,
        classroom_notes=classroom_notes,
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
            "repository": CANONICAL_REPOSITORY,
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

    def plain_title(self, page: dict[str, Any]) -> str:
        title = page.get("properties", {}).get("title", {}).get("title", [])
        return "".join(part.get("plain_text", "") for part in title).strip()

    def is_direct_child_of_parent(self, page: dict[str, Any]) -> bool:
        parent = page.get("parent", {})
        return parent.get("type") == "page_id" and normalize_page_id(parent.get("page_id", "")) == self.parent_page_id

    def archive_existing_roots(self) -> int:
        if not self.fx.install_mode.startswith("Instalación limpia"):
            return 0

        console.print("🧹 Buscando PersonalOS anteriores bajo la página padre...")
        archived = 0
        try:
            response = self.notion.search(
                query="PersonalOS",
                filter={"value": "page", "property": "object"},
                page_size=50,
            )
        except APIResponseError as exc:
            console.print(f"[yellow]No pude buscar páginas previas en Notion:[/yellow] {exc}")
            return 0

        for page in response.get("results", []):
            title = self.plain_title(page)
            if not self.is_direct_child_of_parent(page):
                continue
            if title == "PersonalOS" or title.startswith("PersonalOS —"):
                try:
                    self.notion.pages.update(page_id=page["id"], archived=True)
                    archived += 1
                    console.print(f"  Archivado: {title}")
                except APIResponseError as exc:
                    console.print(f"[yellow]No pude archivar {title}:[/yellow] {exc}")
        return archived

    def root_title(self) -> str:
        if self.fx.install_mode.startswith("Copia nueva"):
            return f"PersonalOS — {self.fx.display_name} — {timestamp_label()}"
        return "PersonalOS"

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
        if blocks:
            self.notion.blocks.children.append(block_id=page_id, children=blocks)

    def companion_welcome(self) -> str:
        if self.fx.companion == "Samwise":
            return f"Qué bueno verte, {self.fx.display_name}. Todavía queda camino, pero hoy alcanza con un paso."
        return f"Bienvenido, {self.fx.display_name}. Hoy alcanza con un solo paso."

    def companion_closing(self) -> str:
        if self.fx.companion == "Samwise":
            return "Si el camino pesa, lo hacemos más liviano. Un paso sigue siendo camino."
        return "No hace falta resolver todo. El Refugio va a seguir acá cuando lo necesites."

    def classroom_next_step(self) -> str:
        if self.fx.classroom_usage == "Sí, usa Google Classroom":
            return "Dejar Classroom listo: confirmar acceso, copiar link si existe y revisar próximas tareas."
        if self.fx.classroom_usage == "No sé todavía":
            return "Confirmar si el aprendizaje usa Classroom, campus, Drive, WhatsApp, PDFs u otra fuente."
        return "Organizar el aprendizaje sin Classroom: materias, tareas, documentos, fechas y próxima acción."

    def run(self) -> None:
        archived = self.archive_existing_roots()
        if archived:
            console.print(f"[green]{archived} PersonalOS anterior(es) archivado(s).[/green]")

        console.print("🌱 Preparando tu Refugio...")
        root = self.remember("root", self.create_root())

        console.print("🌿 Plantando Mi Jardín...")
        jardin = self.remember("jardin", self.create_jardin(root["id"]))
        persona_db = self.remember("persona_db", self.create_persona_db(jardin["id"]))
        resources_db = self.remember("resources_db", self.create_resources_db(jardin["id"]))
        companion_page = self.remember("companion", self.create_companion_page(jardin["id"]))
        classroom_setup = self.remember("classroom_setup", self.create_classroom_setup_page(jardin["id"]))

        console.print("🧭 Trazando el primer Camino...")
        camino = self.remember("camino", self.create_camino(root["id"], classroom_setup["url"]))

        console.print("📖 Preparando la Bitácora...")
        bitacora = self.remember("bitacora", self.create_bitacora(root["id"]))

        console.print("📚 Configurando el primer Recurso de aprendizaje...")
        self.seed_persona(persona_db["id"])
        self.seed_classroom(resources_db["id"], classroom_setup["url"])

        console.print("🍃 Abriendo el Refugio...")
        refugio = self.remember("refugio", self.create_refugio(root["id"], camino["url"], jardin["url"], bitacora["url"], classroom_setup["url"]))

        self.append_root_navigation(root["id"], refugio["url"], camino["url"], jardin["url"], bitacora["url"], companion_page["url"], classroom_setup["url"])
        self.save_mapping()

        console.print("\n[green]Mellon.[/green]")
        console.print("Tu Refugio está listo.\n")
        console.print(f"PersonalOS: {root['url']}")
        console.print(f"Refugio: {refugio['url']}")
        console.print(f"Camino: {camino['url']}")
        console.print(f"Mi Jardín: {jardin['url']}")
        console.print(f"Classroom Setup: {classroom_setup['url']}")
        console.print(f"Bitácora: {bitacora['url']}")

    def create_root(self) -> dict[str, Any]:
        return self.create_page(
            self.parent_page_id,
            self.root_title(),
            "root",
            [
                heading("PersonalOS", 1),
                paragraph("Un Refugio digital para recuperar calma, claridad y dirección."),
                callout(self.companion_welcome(), "refugio"),
                paragraph(f"Modo de instalación: {self.fx.install_mode}"),
                paragraph(f"Companion elegido: {self.fx.companion}"),
                paragraph(f"Perfil inicial: {self.fx.profile}"),
                paragraph(f"Primer contexto de aprendizaje: {self.fx.learning_context}"),
                divider(),
                paragraph("Este espacio fue creado para evaluar PersonalOS v2 como experiencia viva, no como documentación técnica."),
            ],
        )

    def append_root_navigation(self, root_id: str, refugio_url: str, camino_url: str, jardin_url: str, bitacora_url: str, companion_url: str, classroom_setup_url: str) -> None:
        self.append_blocks(
            root_id,
            [
                heading("Entrar", 2),
                link_paragraph("🍃 Refugio", refugio_url),
                link_paragraph("🧭 Camino", camino_url),
                link_paragraph("🌿 Mi Jardín", jardin_url),
                link_paragraph("🏫 Configurar aprendizaje / Classroom", classroom_setup_url),
                link_paragraph("📖 Bitácora", bitacora_url),
                link_paragraph(f"🤝 Companion: {self.fx.companion}", companion_url),
            ],
        )

    def create_refugio(self, root_id: str, camino_url: str, jardin_url: str, bitacora_url: str, classroom_setup_url: str) -> dict[str, Any]:
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
                callout(self.classroom_next_step(), "paso"),
                link_paragraph("🏫 Abrir configuración de aprendizaje / Classroom", classroom_setup_url),
                heading("Cuando termines", 2),
                link_paragraph("📖 Dejar una pequeña reflexión", bitacora_url),
                heading("Cuidar el espacio", 2),
                link_paragraph("🌿 Ir a Mi Jardín", jardin_url),
                divider(),
                paragraph(self.companion_closing()),
            ],
        )

    def create_camino(self, root_id: str, classroom_setup_url: str) -> dict[str, Any]:
        return self.create_page(
            root_id,
            "Camino",
            "camino",
            [
                heading("Camino inicial", 1),
                paragraph(f"Preparar el primer aprendizaje: {self.fx.learning_context}."),
                callout("Un solo paso visible. Nada más.", "camino"),
                heading("Paso actual", 2),
                paragraph(self.classroom_next_step()),
                callout(self.fx.classroom_notes, "resource"),
                link_paragraph("🏫 Configurar aprendizaje / Classroom", classroom_setup_url),
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
                callout("Por ahora solo necesitamos lo esencial: Persona, Companion y primer aprendizaje.", "jardin"),
            ],
        )

    def create_classroom_setup_page(self, jardin_id: str) -> dict[str, Any]:
        children = [
            heading("Configurar aprendizaje / Classroom", 1),
            paragraph(f"Contexto detectado: {self.fx.learning_context}"),
            paragraph(f"Uso de Classroom: {self.fx.classroom_usage}"),
            paragraph(f"Modo preferido: {self.fx.classroom_open_mode}"),
            callout(self.fx.classroom_notes, "classroom"),
            heading("Qué significa dejarlo listo", 2),
            numbered("Confirmar dónde vive la información: Classroom, campus, Drive, WhatsApp, PDFs o apuntes."),
            numbered("Guardar el link o referencia principal."),
            numbered("Registrar materias, cursos o espacios de aprendizaje."),
            numbered("Registrar la próxima tarea o entrega visible."),
            numbered("Definir una próxima acción concreta."),
            heading("Datos actuales", 2),
            bulleted(f"Persona: {self.fx.display_name}"),
            bulleted(f"Tipo de aprendizaje: {self.fx.learning_context}"),
            bulleted(f"Classroom: {self.fx.classroom_usage}"),
        ]
        if self.fx.classroom_url:
            children.append(link_paragraph("Abrir Classroom / plataforma", self.fx.classroom_url))
        else:
            children.append(paragraph("Link pendiente: todavía no se registró un enlace."))
        children.extend(
            [
                heading("Próxima acción sugerida", 2),
                callout(self.classroom_next_step(), "paso"),
            ]
        )
        return self.create_page(jardin_id, "Configurar aprendizaje / Classroom", "classroom", children)

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
                "Aprendizaje inicial": {"rich_text": {}},
            },
        )

    def create_resources_db(self, jardin_id: str) -> dict[str, Any]:
        return self.create_database(
            jardin_id,
            "Recursos",
            "resource",
            {
                "Recurso": {"title": {}},
                "Tipo": select_prop([("Educación", "blue"), ("Documento", "gray"), ("Aplicación", "green"), ("Sitio web", "purple"), ("Campus", "orange")]),
                "Estado": select_prop([("Descubierto", "gray"), ("Configurado", "green"), ("Pendiente", "yellow"), ("No aplica", "gray")]),
                "Modo": select_prop([("Navegador", "blue"), ("Aplicación", "green"), ("Más tarde", "yellow"), ("No aplica", "gray")]),
                "Contexto": select_prop([("Colegio primario", "yellow"), ("Colegio secundario", "green"), ("Carrera universitaria / terciaria", "blue"), ("Curso online", "purple"), ("Capacitación laboral", "orange"), ("Estudio personal", "gray"), ("Otro", "gray")]),
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
                "Aprendizaje inicial": rich_text_prop(self.fx.learning_context),
            },
        )
        self.remember("persona", page)

    def seed_classroom(self, resources_db_id: str, setup_url: str) -> None:
        if self.fx.classroom_usage == "Sí, usa Google Classroom":
            status = "Pendiente" if self.fx.classroom_open_mode == "Más tarde" else "Configurado"
            resource_name = "Google Classroom"
            resource_type = "Educación"
            mode = self.fx.classroom_open_mode
            url = self.fx.classroom_url or "https://classroom.google.com"
        elif self.fx.classroom_usage == "No sé todavía":
            status = "Pendiente"
            resource_name = "Plataforma de aprendizaje por confirmar"
            resource_type = "Educación"
            mode = "Más tarde"
            url = setup_url
        else:
            status = "No aplica"
            resource_name = "Aprendizaje sin Classroom"
            resource_type = "Educación"
            mode = "No aplica"
            url = setup_url

        props: dict[str, Any] = {
            "Recurso": title_prop(resource_name),
            "Tipo": {"select": {"name": resource_type}},
            "Estado": {"select": {"name": status}},
            "Modo": {"select": {"name": mode}},
            "Contexto": {"select": {"name": self.fx.learning_context}},
            "Notas": rich_text_prop(self.fx.classroom_notes),
        }
        if url:
            props["URL"] = {"url": url}
        page = self.create_db_item(resources_db_id, props)
        self.remember("resource_learning", page)


def main() -> None:
    config = load_config()
    token, parent_page_id = resolve_settings(config)
    first_experience = run_first_experience()
    installer = PersonalOSV2Installer(Client(auth=token), parent_page_id, config, first_experience)
    installer.run()


if __name__ == "__main__":
    main()

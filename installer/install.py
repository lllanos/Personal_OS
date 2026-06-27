#!/usr/bin/env python3
"""PersonalOS Notion Installer v2.2 Seed.

Creates an evaluable Notion experience and a real clickable learning flow.
This version fixes the dead-end next step by creating actionable pages:
Paso 1, Paso 2 and Paso 3.
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

INSTALLER_VERSION = "2.2.0-seed"
SCHEMA_VERSION = "2.2"
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
            title="🍃 PersonalOS v2.2",
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
    console.print("Ya tengo lo necesario para crear un camino de aprendizaje con pasos concretos.\n")
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

    def first_action_label(self) -> str:
        return "Abrir Paso 1 — Confirmar fuente de aprendizaje"

    def classroom_next_step(self) -> str:
        if self.fx.classroom_usage == "Sí, usa Google Classroom":
            return "Paso 1: confirmar acceso y fuente. Después registrar materia/curso y primera tarea."
        if self.fx.classroom_usage == "No sé todavía":
            return "Paso 1: elegir la fuente real del aprendizaje: Classroom, campus, Drive, WhatsApp, PDFs u otra."
        return "Paso 1: organizar este aprendizaje sin Classroom, desde materias/cursos, documentos, fechas y tareas."

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
        learning_setup = self.remember("learning_setup", self.create_learning_setup_page(jardin["id"]))

        console.print("👣 Creando pasos accionables de aprendizaje...")
        step1 = self.remember("learning_step_1", self.create_learning_source_step(learning_setup["id"]))
        step2 = self.remember("learning_step_2", self.create_learning_structure_step(learning_setup["id"]))
        step3 = self.remember("learning_step_3", self.create_first_task_step(learning_setup["id"]))
        self.append_learning_navigation(learning_setup["id"], step1["url"], step2["url"], step3["url"])

        console.print("🧭 Trazando el primer Camino...")
        camino = self.remember("camino", self.create_camino(root["id"], learning_setup["url"], step1["url"]))

        console.print("📖 Preparando la Bitácora...")
        bitacora = self.remember("bitacora", self.create_bitacora(root["id"]))

        console.print("📚 Configurando el primer Recurso de aprendizaje...")
        self.seed_persona(persona_db["id"])
        self.seed_learning_resource(resources_db["id"], learning_setup["url"], step1["url"])

        console.print("🍃 Abriendo el Refugio...")
        refugio = self.remember("refugio", self.create_refugio(root["id"], camino["url"], jardin["url"], bitacora["url"], learning_setup["url"], step1["url"]))

        self.append_root_navigation(root["id"], refugio["url"], camino["url"], jardin["url"], bitacora["url"], companion_page["url"], learning_setup["url"], step1["url"])
        self.save_mapping()

        console.print("\n[green]Mellon.[/green]")
        console.print("Tu Refugio está listo.\n")
        console.print(f"PersonalOS: {root['url']}")
        console.print(f"Refugio: {refugio['url']}")
        console.print(f"Camino: {camino['url']}")
        console.print(f"Mi Jardín: {jardin['url']}")
        console.print(f"Aprendizaje: {learning_setup['url']}")
        console.print(f"Siguiente paso: {step1['url']}")
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

    def append_root_navigation(self, root_id: str, refugio_url: str, camino_url: str, jardin_url: str, bitacora_url: str, companion_url: str, learning_setup_url: str, step1_url: str) -> None:
        self.append_blocks(
            root_id,
            [
                heading("Entrar", 2),
                link_paragraph("🍃 Refugio", refugio_url),
                link_paragraph("🧭 Camino", camino_url),
                link_paragraph("👣 Siguiente paso", step1_url),
                link_paragraph("🎒 Configurar aprendizaje", learning_setup_url),
                link_paragraph("🌿 Mi Jardín", jardin_url),
                link_paragraph("📖 Bitácora", bitacora_url),
                link_paragraph(f"🤝 Companion: {self.fx.companion}", companion_url),
            ],
        )

    def create_refugio(self, root_id: str, camino_url: str, jardin_url: str, bitacora_url: str, learning_setup_url: str, step1_url: str) -> dict[str, Any]:
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
                link_paragraph("👣 Abrir Paso 1 — Confirmar fuente de aprendizaje", step1_url),
                link_paragraph("🎒 Ver configuración de aprendizaje", learning_setup_url),
                heading("Cuando termines", 2),
                link_paragraph("📖 Dejar una pequeña reflexión", bitacora_url),
                heading("Cuidar el espacio", 2),
                link_paragraph("🌿 Ir a Mi Jardín", jardin_url),
                divider(),
                paragraph(self.companion_closing()),
            ],
        )

    def create_camino(self, root_id: str, learning_setup_url: str, step1_url: str) -> dict[str, Any]:
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
                link_paragraph("👣 Abrir Paso 1 — Confirmar fuente de aprendizaje", step1_url),
                link_paragraph("🎒 Ver configuración de aprendizaje", learning_setup_url),
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

    def create_learning_setup_page(self, jardin_id: str) -> dict[str, Any]:
        children = [
            heading("Configurar aprendizaje", 1),
            paragraph(f"Contexto detectado: {self.fx.learning_context}"),
            paragraph(f"Uso de Classroom: {self.fx.classroom_usage}"),
            paragraph(f"Modo preferido: {self.fx.classroom_open_mode}"),
            callout(self.fx.classroom_notes, "classroom"),
            heading("Camino guiado", 2),
            paragraph("Este espacio no termina en una frase. Abajo están los pasos concretos para avanzar."),
        ]
        return self.create_page(jardin_id, "Configurar aprendizaje", "educacion", children)

    def append_learning_navigation(self, learning_setup_id: str, step1_url: str, step2_url: str, step3_url: str) -> None:
        blocks = [
            heading("Pasos", 2),
            link_paragraph("👣 Paso 1 — Confirmar fuente de aprendizaje", step1_url),
            link_paragraph("🎒 Paso 2 — Registrar materia o curso", step2_url),
            link_paragraph("✅ Paso 3 — Registrar primera tarea o entrega", step3_url),
            divider(),
            heading("Qué significa dejarlo listo", 2),
            numbered("Confirmar dónde vive la información: Classroom, campus, Drive, WhatsApp, PDFs o apuntes."),
            numbered("Guardar el link o referencia principal."),
            numbered("Registrar materias, cursos o espacios de aprendizaje."),
            numbered("Registrar la próxima tarea o entrega visible."),
            numbered("Definir una próxima acción concreta."),
        ]
        self.append_blocks(learning_setup_id, blocks)

    def create_learning_source_step(self, setup_id: str) -> dict[str, Any]:
        children = [
            heading("Paso 1 — Confirmar fuente de aprendizaje", 1),
            callout("Elegí dónde vive realmente la información. No importa si todavía no está perfecto.", "paso"),
            heading("Opciones posibles", 2),
            bulleted("Google Classroom"),
            bulleted("Campus universitario / Moodle"),
            bulleted("Google Drive"),
            bulleted("WhatsApp o grupo de alumnos"),
            bulleted("Email"),
            bulleted("PDFs, carpeta local o apuntes físicos"),
            heading("Resultado esperado", 2),
            paragraph("Dejar escrita una fuente principal y, si existe, un link o referencia."),
            heading("Después", 2),
            paragraph("Cuando tengas la fuente principal, avanzá al Paso 2 para registrar la materia o curso."),
        ]
        if self.fx.classroom_url:
            children.append(link_paragraph("Abrir link registrado", self.fx.classroom_url))
        return self.create_page(setup_id, "Paso 1 — Confirmar fuente de aprendizaje", "paso", children)

    def create_learning_structure_step(self, setup_id: str) -> dict[str, Any]:
        return self.create_page(
            setup_id,
            "Paso 2 — Registrar materia o curso",
            "educacion",
            [
                heading("Paso 2 — Registrar materia o curso", 1),
                callout("Ahora convertimos la fuente en estructura mínima: materia, curso o espacio de aprendizaje.", "educacion"),
                heading("Datos mínimos", 2),
                bulleted("Nombre de la materia, curso o capacitación."),
                bulleted("Persona relacionada."),
                bulleted("Fuente o plataforma."),
                bulleted("Link principal, si existe."),
                bulleted("Estado: activo, pendiente o pausado."),
                heading("Resultado esperado", 2),
                paragraph("Que el aprendizaje ya no dependa de recordar dónde estaba cada cosa."),
                heading("Después", 2),
                paragraph("Avanzá al Paso 3 para registrar la primera tarea, entrega, examen o próxima acción."),
            ],
        )

    def create_first_task_step(self, setup_id: str) -> dict[str, Any]:
        return self.create_page(
            setup_id,
            "Paso 3 — Registrar primera tarea o entrega",
            "paso",
            [
                heading("Paso 3 — Registrar primera tarea o entrega", 1),
                callout("Un aprendizaje empieza a funcionar cuando tiene una próxima acción visible.", "paso"),
                heading("Cargá una primera acción", 2),
                bulleted("Revisar plataforma."),
                bulleted("Anotar próxima entrega."),
                bulleted("Buscar PDF o apunte."),
                bulleted("Preguntar al docente o compañero."),
                bulleted("Agendar examen o fecha importante."),
                heading("Campos mínimos", 2),
                bulleted("Qué hay que hacer."),
                bulleted("Para quién es."),
                bulleted("Fecha, si existe."),
                bulleted("Fuente o link."),
                bulleted("Próxima acción."),
                heading("Resultado esperado", 2),
                paragraph("Al terminar este paso, PersonalOS ya tiene algo concreto que mostrar en Hoy / Ahora o No olvidar."),
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

    def seed_learning_resource(self, resources_db_id: str, setup_url: str, step1_url: str) -> None:
        if self.fx.classroom_usage == "Sí, usa Google Classroom":
            status = "Pendiente" if self.fx.classroom_open_mode == "Más tarde" else "Configurado"
            resource_name = "Google Classroom"
            resource_type = "Educación"
            mode = self.fx.classroom_open_mode
            url = self.fx.classroom_url or "https://classroom.google.com"
        elif self.fx.classroom_usage == "No sé todavía":
            status = "Pendiente"
            resource_name = "Fuente de aprendizaje por confirmar"
            resource_type = "Educación"
            mode = "Más tarde"
            url = step1_url
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

"""Reusable Notion block components for PersonalOS.

The installer should render experiences from components rather than hard-coded pages.
"""

from __future__ import annotations

from typing import Any


def rt(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": text}}]


def heading(text: str, level: int = 2) -> dict[str, Any]:
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": rt(text)}}


def paragraph(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def callout(text: str, emoji: str = "🍃") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {"icon": {"type": "emoji", "emoji": emoji}, "rich_text": rt(text)},
    }


def todo(text: str, checked: bool = False) -> dict[str, Any]:
    return {"object": "block", "type": "to_do", "to_do": {"rich_text": rt(text), "checked": checked}}


def link_to_database(database_id: str) -> dict[str, Any]:
    return {"object": "block", "type": "link_to_page", "link_to_page": {"type": "database_id", "database_id": database_id}}


def welcome_component() -> list[dict[str, Any]]:
    return [
        heading("◯ PersonalOS", 1),
        paragraph("🌅 Buenos días."),
        paragraph("Hoy no hace falta resolver todo. Solo caminar el siguiente paso."),
        divider(),
    ]


def next_step_component(title: str, minutes: int) -> list[dict[str, Any]]:
    return [
        heading("🍃 Siguiente paso", 2),
        paragraph(title),
        paragraph(f"⏱ {minutes} minutos"),
        callout("Vamos", "▶️"),
        divider(),
    ]


def balance_component(status: str = "Sereno") -> list[dict[str, Any]]:
    return [
        heading("⚖ Balance", 2),
        paragraph(status),
        divider(),
    ]


def after_component(text: str) -> list[dict[str, Any]]:
    return [
        heading("⏭ Después", 2),
        paragraph(text),
        divider(),
    ]


def path_component(state: str = "🪨  🪨  ○  ○  ○") -> list[dict[str, Any]]:
    return [
        heading("🌱 Camino", 2),
        paragraph(state),
        divider(),
    ]


def closing_component() -> list[dict[str, Any]]:
    return [
        heading("🌙 Cierre", 2),
        paragraph("Cuando termines, dejamos preparado mañana."),
        divider(),
    ]


def refuge_components(missions_db_id: str, habits_db_id: str, people_db_id: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    blocks.extend(welcome_component())
    blocks.extend(next_step_component("Abrir Classroom", 3))
    blocks.extend(balance_component("Sereno"))
    blocks.extend(after_component("Leer la consigna"))
    blocks.extend(path_component())
    blocks.extend(closing_component())
    blocks.extend([
        link_to_database(missions_db_id),
        link_to_database(habits_db_id),
        link_to_database(people_db_id),
    ])
    return blocks


def morning_ritual_components() -> list[dict[str, Any]]:
    return [
        heading("🌅 Ritual del Amanecer", 1),
        paragraph("Antes de empezar, volvemos al cuerpo y al presente."),
        divider(),
        callout("Respirá un momento. No hace falta resolver todo ahora.", "🍃"),
        todo("Tomar agua"),
        todo("Mirar el primer paso del día"),
        todo("Elegir caminar despacio"),
        divider(),
        paragraph("Cuando estés listo, volvé al Refugio."),
    ]


def focus_ritual_components() -> list[dict[str, Any]]:
    return [
        heading("🎯 Ritual del Foco", 1),
        paragraph("Una sola misión. Un solo paso. Sin ruido alrededor."),
        divider(),
        callout("Guardá lo que distrae. Prepará el espacio. Empezamos pequeño.", "🕯️"),
        todo("Preparar el lugar"),
        todo("Abrir solo lo necesario"),
        todo("Hacer el siguiente paso"),
        divider(),
        paragraph("Si cuesta, reducimos la misión. El camino sigue."),
    ]


def pause_ritual_components() -> list[dict[str, Any]]:
    return [
        heading("☕ Ritual de Pausa", 1),
        paragraph("Descansar también es parte del camino."),
        divider(),
        callout("Pausa breve. Agua. Respiración. Volvemos cuando haya aire.", "🍵"),
        todo("Levantarse un minuto"),
        todo("Tomar agua"),
        todo("Respirar sin pantalla"),
        divider(),
        paragraph("No estás frenando. Estás recuperando balance."),
    ]


def closing_ritual_components() -> list[dict[str, Any]]:
    return [
        heading("🌙 Ritual del Cierre", 1),
        paragraph("El día no necesita quedar perfecto. Solo preparado para continuar."),
        divider(),
        callout("Dejemos una piedra lista para mañana.", "🪨"),
        todo("Preparar mochila o elementos necesarios"),
        todo("Anotar el primer paso de mañana"),
        todo("Cerrar el día sin culpa"),
        divider(),
        paragraph("Mañana seguimos caminando."),
    ]

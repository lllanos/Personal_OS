#!/usr/bin/env python3
"""Local configuration validator for PersonalOS Installer.

The first experience now asks for the initial person interactively, so people in
config.yaml is optional. The only hard requirements are Notion credentials and a
valid parent page id.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID_RE = re.compile(r"^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$")


def load_config() -> dict[str, Any]:
    path = Path("config.yaml") if Path("config.yaml").exists() else Path("config.example.yaml")
    if not path.exists():
        raise FileNotFoundError("Missing config.yaml or config.example.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def main() -> int:
    console.print(Panel("🍃 Validando configuración local...", title="◯ PersonalOS"))
    try:
        config = load_config()
    except Exception as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        return 1

    token = os.getenv("NOTION_TOKEN") or config.get("notion", {}).get("token", "")
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID") or config.get("notion", {}).get("parent_page_id", "")
    people = config.get("people", [])
    primary_person = config.get("personalos", {}).get("primary_person")

    errors: list[str] = []
    warnings: list[str] = []

    if not token:
        errors.append("NOTION_TOKEN no está definido.")
    elif "REPLACE" in token:
        errors.append("El token todavía contiene REPLACE. Usá un token rotado real.")
    elif not token.startswith("ntn_"):
        warnings.append("El token no empieza con ntn_. Verificá que sea un token interno de Notion válido.")

    if not parent_page_id:
        errors.append("NOTION_PARENT_PAGE_ID no está definido.")
    elif not PAGE_ID_RE.match(parent_page_id):
        errors.append("El parent_page_id no parece un ID válido de Notion.")

    if not people:
        warnings.append("No hay personas definidas en config.yaml. Está bien: el First Experience las pedirá en pantalla.")
    else:
        roles = {person.get("role") for person in people}
        if primary_person and primary_person not in roles:
            warnings.append(f"primary_person={primary_person!r} no existe dentro de people.role. Se ignorará para el First Experience.")

    if errors:
        console.print("[red]Validación fallida:[/red]")
        for error in errors:
            console.print(f"  ✗ {error}")
        return 1

    for warning in warnings:
        console.print(f"[yellow]⚠ {warning}[/yellow]")

    console.print("[green]✓ Configuración válida. Podés ejecutar el instalador.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

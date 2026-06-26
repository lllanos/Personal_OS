#!/usr/bin/env python3
"""PersonalOS dry-run preview.

This command does not call Notion. It only shows what the installer intends to create.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def load_config() -> dict[str, Any]:
    path = Path("config.yaml") if Path("config.yaml").exists() else Path("config.example.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    config = load_config()
    personalos = config.get("personalos", {})
    people = config.get("people", [])

    console.print(Panel("Vista previa local. No se crea nada en Notion.", title="◯ PersonalOS Dry Run"))

    console.print("\n[bold]Estructura a crear[/bold]")
    console.print("◯ PersonalOS")
    console.print("├── 🍃 Refugio")
    console.print("├── 👤 Personas")
    console.print("├── 🎯 Misiones")
    console.print("└── 🌱 Hábitos")

    table = Table(title="Personas iniciales")
    table.add_column("Nombre")
    table.add_column("Rol")
    table.add_column("Tema")
    table.add_column("Estación")

    theme = str(personalos.get("theme", "zen")).capitalize()
    season = personalos.get("season", "Otoño")

    for person in people:
        table.add_row(person.get("name", ""), person.get("role", ""), theme, season)

    console.print(table)

    missions = Table(title="Misiones semilla")
    missions.add_column("Misión")
    missions.add_column("Momento")
    missions.add_column("Tiempo")
    missions.add_column("Balance")
    missions.add_row("Abrir Classroom", "Amanecer", "3 min", "Sereno")
    missions.add_row("Leer la consigna", "Foco", "5 min", "Sereno")
    console.print(missions)

    habits = Table(title="Hábitos semilla")
    habits.add_column("Hábito")
    habits.add_column("Frecuencia")
    habits.add_row("💧 Tomar agua", "Diario")
    habits.add_row("🎒 Preparar mochila", "Diario")
    habits.add_row("🌙 Preparar descanso", "Diario")
    console.print(habits)

    console.print("\n[green]✓ Dry-run completo. Si esto se ve correcto, ejecutá bash run_installer.sh.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

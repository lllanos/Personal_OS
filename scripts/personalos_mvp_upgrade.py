from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERSONALOS_DIR = ROOT / ".personalos"
ENROLL_DIR = PERSONALOS_DIR / "enroll"
BACKUP_DIR = PERSONALOS_DIR / "backups"
CANONICAL_REPOSITORY = "lllanos/Personal_OS"
PRODUCT_NAME = "PersonalOS"


FILES = {
    "docs/personalos/PERSONALOS_MVP.md": """# PersonalOS — MVP Inicial

Documento base del MVP inicial de PersonalOS.

Ver también:

- templates/personalos/personalos-page.md
- docs/personalos/ENROLL_INICIAL.md
- docs/personalos/REPOSITORY_CONTEXT.md
""",
    "templates/personalos/README.md": """# PersonalOS Template

Plantilla inicial del MVP de PersonalOS.

Principio central:

> Una sola página para vivir el sistema. Bases internas para sostenerlo.

Repositorio canónico:

```text
lllanos/Personal_OS
```
""",
    "templates/personalos/personalos-page.md": """# PersonalOS — Centro de Control

## Hoy / Ahora

## No olvidar

## Personas

## Dominios de vida

## Educación / Aprendizaje

## Bloqueados

## Captura rápida
""",
    "templates/personalos/databases/personas.md": """# Base: Personas
""",
    "templates/personalos/databases/dominios.md": """# Base: Dominios
""",
    "templates/personalos/databases/elementos.md": """# Base: Elementos
""",
    "templates/personalos/databases/tareas.md": """# Base: Tareas
""",
    "templates/personalos/databases/documentos.md": """# Base: Documentos
""",
    "templates/personalos/databases/decisiones.md": """# Base: Decisiones
""",
    "templates/personalos/views/hoy-ahora.md": """# Vista: Hoy / Ahora
""",
    "templates/personalos/views/no-olvidar.md": """# Vista: No olvidar
""",
    "templates/personalos/views/por-persona.md": """# Vista: Por persona
""",
    "templates/personalos/views/por-dominio.md": """# Vista: Por dominio
""",
    "templates/personalos/views/bloqueados.md": """# Vista: Bloqueados
""",
    "docs/personalos/ENROLL_INICIAL.md": """# PersonalOS — Enroll Inicial

1. ¿A quién querés organizar?
2. ¿Qué área querés organizar primero?
3. ¿Qué elemento concreto existe dentro de esa área?
4. ¿Hay alguna tarea, fecha, documento o decisión asociada?
5. ¿Cuál es la próxima acción?
""",
    "docs/personalos/REPOSITORY_CONTEXT.md": """# PersonalOS — Repository Context

## Canonical repository

```text
lllanos/Personal_OS
```

Use this repository full name for future commits, documentation updates, scripts, upgrade instructions, and implementation work related to PersonalOS.
""",
}


def write_file_upgrade(path: Path, content: str, timestamp: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(content, encoding="utf-8")
        return "CREATED: " + str(path.relative_to(ROOT))

    current = path.read_text(encoding="utf-8", errors="ignore")
    if current == content:
        return "UNCHANGED: " + str(path.relative_to(ROOT))

    upgrade_path = path.with_name(path.name + ".upgrade-" + timestamp)
    upgrade_path.write_text(content, encoding="utf-8")
    return "EXISTS: " + str(path.relative_to(ROOT)) + " | UPGRADE COPY: " + str(upgrade_path.relative_to(ROOT))


def create_enroll_state(timestamp: str) -> None:
    ENROLL_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        "system": PRODUCT_NAME,
        "repository": CANONICAL_REPOSITORY,
        "mode": "mvp-initial-enroll",
        "created_at": timestamp,
        "status": "ready",
        "recommended_first_module": "Educación / Aprendizaje",
        "questions": [
            "¿A quién querés organizar?",
            "¿Qué área querés organizar primero?",
            "¿Qué elemento concreto existe dentro de esa área?",
            "¿Hay alguna tarea, fecha, documento o decisión asociada?",
            "¿Cuál es la próxima acción?"
        ],
        "principle": "Una sola página para vivir el sistema. Bases internas para sostenerlo."
    }
    (ENROLL_DIR / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="PersonalOS MVP safe upgrade installer")
    parser.add_argument("--enroll", action="store_true", help="Prepare initial user enroll state")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be prepared")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    PERSONALOS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    report = []
    report.append("# PersonalOS MVP Upgrade Report")
    report.append("")
    report.append("- Repository: " + CANONICAL_REPOSITORY)
    report.append("- Timestamp: " + timestamp)
    report.append("- Root: " + str(ROOT))
    report.append("- Dry run: " + str(args.dry_run))
    report.append("- Enroll: " + str(args.enroll))
    report.append("")

    if args.dry_run:
        for rel in FILES:
            report.append("WOULD CHECK: " + rel)
    else:
        for rel, content in FILES.items():
            report.append(write_file_upgrade(ROOT / rel, content, timestamp))

        if args.enroll:
            create_enroll_state(timestamp)
            report.append("ENROLL READY: .personalos/enroll/state.json")

    report_path = PERSONALOS_DIR / ("upgrade_report_" + timestamp + ".md")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))
    print("")
    print("Report: " + str(report_path.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

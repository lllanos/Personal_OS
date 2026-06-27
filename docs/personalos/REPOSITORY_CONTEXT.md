# PersonalOS — Repository Context

## Canonical repository

The canonical GitHub repository for PersonalOS is:

```text
lllanos/Personal_OS
```

Use this repository full name for future commits, documentation updates, scripts, upgrade instructions, and implementation work related to PersonalOS.

## Naming convention

- Product / system name: **PersonalOS**
- GitHub repository name: **Personal_OS**
- Repository full name: **lllanos/Personal_OS**

## Current working branch

Default branch:

```text
main
```

## Operational note

When updating the repository, prefer safe upgrade behavior over destructive replacement:

1. Detect existing files and structures.
2. Preserve current user-created content.
3. Add missing structures.
4. Create upgrade copies or backups when content differs.
5. Restart or prepare the enroll process only after the upgrade state is ready.

## Current MVP direction

The current PersonalOS MVP direction is:

> One visible page for daily use. Internal structures for context, tracking, relationships, and safe expansion.

Initial visible sections:

- Hoy / Ahora
- No olvidar
- Personas
- Dominios de vida
- Educación / Aprendizaje
- Bloqueados
- Captura rápida

Initial internal structures:

- Personas
- Dominios
- Elementos
- Tareas
- Documentos
- Decisiones

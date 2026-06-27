---
id: PERSONALOS_V2_PRODUCT_SPRINT
title: PersonalOS v2 Product Sprint
version: 0.1 Seed
status: active
layer: product
related:
  - PERSONALOS_MASTER_PLAN
  - PERSONALOS_1101
  - PERSONALOS_1106
---

# PersonalOS v2 Product Sprint

## Decision

PersonalOS v2 will prioritize the evaluable product experience in Notion.

Notion will not mirror the architecture documentation.
Notion will represent the living product experience.

GitHub remains the laboratory for architecture, domain, events, runtime, and governance.

## Goal

Create a PersonalOS v2 Notion experience that can be used, tested, and evaluated by real people.

The goal is not to show everything PersonalOS can become.
The goal is to make the first experience understandable, calm, and useful.

## Product principles

1. Notion is the house, not the blueprint.
2. The first user experience matters more than architectural completeness.
3. The installer should create an experience, not documentation.
4. One initial person only.
5. One visible path.
6. One primary step.
7. One simple resource setup.
8. One optional reflection.
9. No guilt language.
10. No technical language.

## PersonalOS v2 scope

### 1. First Experience

The installer should ask:

```text
¿Para quién estamos preparando este Refugio?
- Adulto
- Adolescente
- Niño
- Otra persona

¿Cómo querés que te llame?

¿Cómo preferís que te acompañe?
- Aurora
- Samwise
```

Then it creates the personalized Refugio.

### 2. Companion Selection

Aurora and Samwise do not change features.
They change language, rhythm, and tone.

- Aurora: serene presence.
- Samwise: companion of the road.

### 3. Refugio

The Refugio is the entry point.

It should show:

- welcome message;
- one current Camino;
- one primary Paso;
- access to Mi Jardín;
- access to Bitácora.

### 4. Camino

The first Camino should be simple and evaluable.

Initial Camino:

```text
Preparar el primer paso
```

Initial Paso:

```text
Abrir Classroom
```

### 5. Resource Setup

If Classroom is not configured, ask:

```text
¿Cómo preferís abrir Classroom?
- Navegador
- Aplicación
- Más tarde
```

The answer should be remembered.

### 6. Mi Jardín

Mi Jardín v2 contains only:

- Persona;
- Companion;
- Recursos.

No advanced configuration.

### 7. Bitácora mínima

After the first step, offer a lightweight reflection:

```text
¿Cómo fue este paso?
- Más claro
- Más tranquilo
- Igual
- Prefiero no responder
```

## Out of scope for v2

- Architecture pages in Notion.
- Full Aurora Core implementation.
- Full event sourcing.
- Mobile app.
- Multi-person family workspace.
- Advanced AI.
- Full Legacy Engine.
- Full Living Graph.

## Installer direction

`install.py` should evolve into a v2 experience generator.

Minimum changes:

- interactive onboarding;
- personalized root title;
- one initial person;
- companion-aware content;
- simple resources database;
- classroom setup fields;
- clean titles;
- safe icons;
- foundation for idempotency.

## Success criteria

PersonalOS v2 succeeds if a first tester can answer:

- What is my Refugio?
- What is my next step?
- Where do I configure Classroom?
- Who is accompanying me?
- Where do I leave a small reflection?

Without needing documentation.

## Final rule

Do not show the blueprint to the person.

Let them enter the Refugio.

---
id: PERSONALOS_101
title: Day Engine Specification
version: 0.1 Seed
status: draft
layer: engineering
related:
  - PERSONALOS_100
  - PERSONALOS_002
  - PERSONALOS_003
  - PERSONALOS_102
---

# PERSONALOS_101 — Day Engine

## Mission

The Day Engine builds the experience of **Today**.

It does not schedule an agenda. It prepares a day that feels understandable, calm and actionable.

## Responsibility

Given a person and the current context, produce a complete `TodayContext`.

## Inputs

- PersonState
- Current date
- Current moment
- Active journeys
- Energy
- Balance
- Pending reflections
- Ritual calendar

## Output

```text
TodayContext
├── greeting
├── moment
├── balance
├── energy
├── ritual
├── next_step
├── after_step
├── reflection_prompt
└── closing_focus
```

## Decision pipeline

```mermaid
graph TD
 A[Load PersonState] --> B[Detect Moment]
 B --> C[Evaluate Energy]
 C --> D[Evaluate Balance]
 D --> E[Select Ritual]
 E --> F[Request Flow Engine]
 F --> G[Build TodayContext]
```

## Design rules

- Only one primary step.
- Maximum one secondary step.
- Never expose backlog by default.
- Prefer clarity over completeness.
- Preserve emotional calm.

## Failure handling

If no step is appropriate:

- suggest a pause;
- invite reflection;
- recommend restoring energy;
- never fabricate urgency.

## Adapter contract

Every interface (Notion, Android, iOS, Web) renders the same TodayContext without changing its meaning.

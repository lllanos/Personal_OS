---
id: PERSONALOS_1103
title: PersonalOS Event Model
version: 0.1 Seed
status: draft
layer: architecture
related:
  - PERSONALOS_MASTER_PLAN
  - PERSONALOS_1101
  - PERSONALOS_1102
  - PERSONALOS_1104
---

# PERSONALOS_1103 — Event Model

## Purpose

This document defines the first domain event model for PersonalOS.

PersonalOS should be event-oriented because a life-centered system is better represented by meaningful moments than by raw CRUD updates.

## Event principle

An event means something happened that may matter to the person's path, memory, balance, or future experience.

Not every technical action is a domain event.

## Event contract

All domain events should share a common envelope.

```text
DomainEvent
├── event_id
├── event_type
├── occurred_at
├── actor_id
├── persona_id
├── aggregate_type
├── aggregate_id
├── source
├── correlation_id
├── causation_id
├── payload
└── metadata
```

## Event naming rule

Events must be named in past tense.

Examples:

- RefugioCreated
- CompanionChosen
- PasoCompleted
- ReflectionCaptured

Avoid command-style names such as:

- CreateRefugio
- ChooseCompanion
- CompletePaso

## Event categories

### Identity events

- PersonaCreated
- PersonaNamed
- ProfileSelected
- LanguageSelected
- CompanionChosen
- CompanionChanged

### Refugio events

- RefugioCreated
- RefugioEntered
- ReturnedToRefugio
- RefugioStateChanged
- RoomEntered

### Camino events

- CaminoCreated
- CaminoStarted
- CaminoPaused
- CaminoResumed
- CaminoCompleted
- CaminoIntegrated

### Paso events

- PasoCreated
- PasoAvailable
- PasoStarted
- PasoCompleted
- PasoSkipped
- PasoBlocked
- PasoReflected
- PasoIntegrated

### Jardin events

- JardinCreated
- PersonAddedToJardin
- RitualAdded
- PreferenceChanged

### Resource events

- ResourceDiscovered
- ResourceSetupRequested
- ResourceConfigured
- ResourceOpened
- ResourceUnavailable
- CapabilityUnlocked

### Reflection and wisdom events

- ReflectionPrompted
- ReflectionCaptured
- InsightProposed
- InsightAccepted
- InsightRejected
- WisdomUpdated

### Legacy events

- MilestoneMarked
- LegacyCapsuleCreated
- LegacyCapsuleShared
- LifeChapterCreated

### Balance events

- BalanceChecked
- BalanceChanged
- EnergyChanged
- PauseSuggested

### Seasonal events

- SeasonChanged
- LifeStageChanged

## Minimal MVP event set

For Notion v0.2, only a minimal set is required.

```text
PersonaCreated
ProfileSelected
PersonaNamed
CompanionChosen
RefugioCreated
ResourceDiscovered
ResourceConfigured
PasoStarted
PasoCompleted
ReflectionCaptured
ReturnedToRefugio
```

## Example event: PersonaNamed

```json
{
  "event_type": "PersonaNamed",
  "aggregate_type": "Persona",
  "payload": {
    "display_name": "Luis"
  }
}
```

## Example event: ResourceConfigured

```json
{
  "event_type": "ResourceConfigured",
  "aggregate_type": "Recurso",
  "payload": {
    "resource_name": "Classroom",
    "preferred_open_mode": "browser",
    "capabilities": ["open"]
  }
}
```

## Example event: PasoCompleted

```json
{
  "event_type": "PasoCompleted",
  "aggregate_type": "Paso",
  "payload": {
    "paso_title": "Abrir Classroom",
    "completion_context": "first_experience"
  }
}
```

## Event usage

Events are used to:

- reconstruct meaningful history;
- feed the Living Graph;
- update projections;
- support future synchronization;
- explain why Aurora made a decision;
- preserve memory without storing every click.

## Event storage rule

The first implementation may persist events in simple storage.

A full event-sourcing system is not required for MVP.

However, events should be designed as if they may later support event sourcing.

## Projections

Events may feed projections such as:

- current Refugio state;
- current Camino state;
- current Paso;
- configured resources;
- recent meaningful activity;
- Bitacora;
- Legacy timeline.

## Privacy rule

Events belong to the person.

Events must not become surveillance logs.

Avoid recording unnecessary technical details, clicks, or passive behavior unless they directly support the person's experience and are explainable.

## Anti-patterns

Do not create domain events for:

- every page view;
- every mouse click;
- every UI render;
- every background sync;
- every adapter-specific call.

These may be technical logs, but they are not PersonalOS domain events.

## Summary

PersonalOS events represent meaningful moments.

They are the raw material for memory, reflection, wisdom, continuity, and legacy.

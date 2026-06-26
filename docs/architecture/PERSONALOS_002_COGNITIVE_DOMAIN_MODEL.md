---
id: PERSONALOS_002
title: Cognitive Domain Model
version: 0.1 Seed
status: foundational
layer: architecture
related:
  - PERSONALOS_000
  - PERSONALOS_001
  - PERSONALOS_003
  - PERSONALOS_101
  - PERSONALOS_103
---

# PERSONALOS_002 — Cognitive Domain Model

## Principle

PersonalOS does not model tasks first.
It models human movement through intention, context, clarity, steps, reflection, wisdom, and legacy.

## Domain overview

```mermaid
graph TD
  PERSON[Person] --> TODAY[Today]
  PERSON --> JOURNEYS[Journeys]
  TODAY --> MOMENT[Moment]
  TODAY --> BALANCE[Balance]
  TODAY --> ENERGY[Energy]
  JOURNEYS --> STEPS[Steps]
  STEPS --> CONTEXT[Context]
  STEPS --> RESOURCES[Resources]
  TODAY --> REFLECTION[Reflection]
  REFLECTION --> WISDOM[Wisdom]
  WISDOM --> LEGACY[Legacy]
```

## Person

A person is not a user record.
A person is a living center of intention, energy, memory, values, and growth.

## Today

The day is the base unit of the experience.
PersonalOS does not ask the person to live inside weeks or project plans.
It starts with today.

## Moment

The day is divided into human moments, such as dawn, focus, pause, afternoon, and closing.

## Journey

A journey is a meaningful path.
It replaces the traditional idea of a project.

## Step

A step is the smallest meaningful unit of movement.

A step must be small enough to start without planning.
If a step creates anxiety, it is still too large.

## Context

Context is everything needed to start:

- domain
- material
- resource
- due date
- place
- time
- emotional state
- next action

## Resources

Resources should wait for the person.
The person should not have to search for them every time.

## Reflection

Reflection is intentionally small.
One question per day is enough.

## Wisdom

Wisdom stores discovered patterns about a person.
It must never be used to compare or classify the person against others.

## Legacy

Legacy is memory with meaning.
It preserves reflections, learnings, values, and lived experience.

## Daily decision loop

```mermaid
graph TD
  NEWDAY[New day] --> ENERGY[Evaluate energy]
  ENERGY --> BALANCE[Evaluate balance]
  BALANCE --> MOMENT[Evaluate moment]
  MOMENT --> JOURNEY[Find active journey]
  JOURNEY --> STEP[Find possible step]
  STEP --> FRICTION[Reduce friction]
  FRICTION --> SHOW[Show one step]
  SHOW --> WAIT[Wait]
  WAIT --> LEARN[Learn]
  LEARN --> REFLECT[Store reflection]
  REFLECT --> TOMORROW[Prepare tomorrow]
```

## Core rules

### The One Step Rule

At any moment PersonalOS should answer one question:

> What is the next step?

### The Ready Rule

When a step appears, it should be ready to start.

### The Return Rule

Every person has the right to return without guilt.

## Summary

PersonalOS does not manage tasks.
It accompanies a person's path.

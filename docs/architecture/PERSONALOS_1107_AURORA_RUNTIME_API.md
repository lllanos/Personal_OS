---
id: PERSONALOS_1107
title: Aurora Runtime API
version: 0.1 Seed
status: draft
layer: architecture
related:
  - PERSONALOS_MASTER_PLAN
  - PERSONALOS_1101
  - PERSONALOS_1102
  - PERSONALOS_1103
  - PERSONALOS_1104
  - PERSONALOS_1105
  - PERSONALOS_1106
---

# PERSONALOS_1107 — Aurora Runtime API

## Purpose

Define the platform-neutral runtime contract between Aurora Core and every adapter.

## Principles

- Aurora Core owns decisions.
- Adapters request and render.
- Communication is state and event based.
- APIs express domain language, never platform language.

## Main Runtime Services

- Identity Service
- Experience Service
- Journey Service
- Resource Service
- Balance Service
- Reflection Service
- Wisdom Service
- Legacy Service
- Event Service

## Core Requests

### EnterRefugio
Returns the current PersonalOSState.

### NextPaso
Returns one recommended next step.

### OpenResource
Requests execution of a capability through a configured resource.

### CaptureReflection
Stores an optional reflection and emits ReflectionCaptured.

### UpdatePreference
Updates a domain preference through Identity Engine.

## Runtime Responses

Every response returns:

- current_state
- optional_events
- optional_projection_updates
- optional_messages

## PersonalOSState

Minimum runtime projection:

- Persona
- Current Refugio
- Current Room
- Active Camino
- Primary Paso
- Companion
- Balance
- Resource Requests
- Reflection Prompt

## Event Flow

Adapter -> Aurora Runtime -> Domain Event -> Engine Updates -> Projection -> Adapter

## Error Contract

Runtime returns domain-friendly outcomes.

Technical details remain internal and may be logged separately.

## Versioning

Runtime contracts evolve independently of adapters.

Adapters negotiate supported API versions without changing domain semantics.

## MVP Runtime

For Notion v0.2 the runtime only needs:

- EnterRefugio
- NextPaso
- OpenResource
- CaptureReflection
- UpdatePreference

Everything else remains internal until Aurora Core matures.

## Final Principle

Aurora Runtime is the conversation layer of PersonalOS.

Every adapter speaks with Aurora through this API, allowing the experience to remain consistent regardless of the platform.

---
name: m365-agent-factory
description: Scaffold for the M365 Agent Factory control-plane workflow.
---

# Status: NOT IMPLEMENTED

This file defines the planned skill boundary only. It does not yet perform intake, architecture, specification generation, approval, or orchestration.

## Purpose

Own objective capture, requirements extraction, minimal clarification, architecture selection, specification drafting, approval gating, and implementation orchestration for M365 Copilot agents.

## Boundaries

The skill coordinates other capabilities; Microsoft tools perform platform work. It must not invent environment facts or begin implementation before approval. It does not implement an agent runtime or platform API wrapper.

## Inputs and outputs (planned)

- Inputs: ordinary-language business objective, supplied context, answers/assumptions, target environment when known.
- Outputs: persisted objective and clarifications, architecture decision, approved specification/hash, dependency-ordered build manifest, state and routing records.

## Dependencies (planned, unverified)

Verified host skill loading; Microsoft Copilot Studio, Power Automate, Dataverse, evaluation and ALM capabilities as selected by architecture; project artifact templates and deterministic helpers.

## References

See `references/` for planned architecture, clarification, capability, specification, and routing contracts.

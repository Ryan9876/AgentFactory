# Architecture decision workflow

## Interface and gate

Input: a resolved objective record, supplied context, and any user-accepted assumptions. Output: a persisted decision for every component category in `templates/architecture-decision.md`. Each decision records the selection, rationale, dependency, and evidence status. Architecture precedes specification drafting. If a consequential unknown prevents a sound choice, mark the architecture `CLARIFICATION_REQUIRED`, name the blocker, and do not draft the specification.

Architecture is a proposal until the user accepts it through the project approval workflow. A capability listed in the registry is not proof that it is installed, authenticated, permitted, compatible, or connected to the target environment.

## Decision procedure

For each component category:

1. Identify the requirement it serves and the supplied evidence or unresolved dependency.
2. Apply the simplest suitable option in the preference order below.
3. Record the choice and why it meets the requirement. Record a reason for `Not required` or `None selected` too.
4. Mark capability evidence `verified`, `available`, `not_required`, `not_yet_verified`, or `blocked`. Use `verified` only after a concrete check in the relevant host/environment. State what remains to be checked.
5. Record consequential alternatives and blockers; do not turn unknown live-system facts into architecture assumptions.

## Harness

Use **Standard Copilot Studio** by default. Select a newer GHCP-style harness only when explicitly requested or when it provides a material architectural advantage, the required tooling exists, and maturity/compatibility is acceptable. Record the evidence and reason for any exception. Do not claim host support based only on documentation or a catalog entry.

## Component distinctions and selection

- **Knowledge** holds searchable factual/reference content. Identify the authoritative source and its access model; record exact location as a dependency if not supplied.
- **Skill** provides reusable procedural knowledge or multi-step task guidance. Add one only when the procedure is meaningful and reusable; do not label reference content as a skill.
- **Tool/action** performs external actions, accesses live-system data, executes deterministic computation, or calls an API. Identify the capability intent and leave provider/operation unresolved until evidence supports it.
- **Power Automate** is preferred for deterministic multi-step behavior with branching, approvals, multiple connectors, retries/recovery, asynchronous work, or workflow state. A simple action may use a native connector/tool when it reliably meets the requirement.
- **Dataverse/state** is not automatic. Use Dataverse when requirements need structured durable application data, relationships, ownership/security semantics, durable workflow state, or solution-managed structured data, and no suitable authoritative system already owns the state. Name the state owner; if unknown, record a blocker/dependency instead of assuming Dataverse.
- **Additional agents** require a meaningful boundary in responsibility, security, permissions, data domain, independent lifecycle, tool surface, or evaluation ownership. Do not create them merely to organize prompts.
- **External integrations** identify only sources/services actually stated or required. Do not invent vendors, systems, URLs, connector names, operations, schemas, or credentials.
- **Custom development** is considered only after the preference order has been evaluated and a concrete gap recorded.

Apply this preference order, choosing the earliest reliable fit rather than forcing an unsuitable option:

```text
native Copilot Studio capability
→ knowledge
→ built-in connector/tool
→ Power Automate
→ Dataverse
→ existing MCP/API
→ custom connector
→ custom code
```

## Record and continue

Use `templates/architecture-decision.md`. Once consequential choices are resolved or explicitly accepted as documented assumptions, set the architecture disposition to `DECIDED` or `DECIDED_WITH_UNRESOLVED_DEPENDENCIES` as appropriate. Do not move to specification until the required architecture choices are recorded. Dependencies that can be safely verified during preflight remain explicit and must be resolved before affected implementation begins.

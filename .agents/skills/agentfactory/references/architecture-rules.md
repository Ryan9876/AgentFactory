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

Select the least-complex viable supported architecture after requirements, licensing, hosting, and automation constraints are known. Declarative agents are preferred for suitable internal M365 knowledge/expertise scenarios; use Standard Copilot Studio for structured conversations or Power Platform-heavy scenarios, adding Power Automate and Dataverse only when justified. Custom engines are exception-only. GitHub Copilot harness is disallowed under current constraints; embedded Work IQ in Copilot Studio is disallowed. Host-composed Work IQ is distinct from conditional direct Work IQ MCP. Documentation or catalog discovery does not prove host support, authentication, or tenant execution.

## Path of least resistance and buildability

Record native capability considered, simplest viable level (Use → Configure → Integrate → Automate → Extend → Build), demonstrated reason earlier levels are insufficient, security/data impact, selected authoring surface, runtime qualification plan, restoration plan when applicable, and reassessment stop conditions. Classify before implementation as `CLOUD_BUILDABLE`, `CLOUD_BUILDABLE_WITH_MANUAL_DEPLOY`, `PORTAL_STEP_REQUIRED`, or `BLOCKED`. Authoring/UI/tool-host failure alone never authorizes a more complex architecture; localize the failing layer and try another supported surface first.

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

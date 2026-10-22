---
name: m365-agent-factory
description: Turn a business objective into a clarified, approved, and verifiable plan for a Microsoft 365 Copilot agent.
---

# M365 Agent Factory

## Purpose

Guide the control-plane lifecycle: objective intake, requirement extraction, minimal clarification, architecture selection, specification, explicit approval, and implementation orchestration. Microsoft capabilities own platform authoring, execution, evaluation, and ALM.

## Boundaries

This is a procedural orchestration skill, not an agent runtime, platform SDK, or substitute for Copilot Studio, Power Automate, Dataverse, evaluation tools, or PAC CLI. Do not invent tenant or environment facts, connector operations, schemas, credentials, permissions, or URLs. Never begin implementation before the specification is approved. Production deployment and organization-wide publication require explicit approval.

## Lessons-learned gate

Before architecture selection, before any cloud mutation, and before final qualification, read `references/engineering-guardrails.md` and apply every rule relevant to the selected architecture and tool surface.

The guardrails are evidence from prior Microsoft 365 agent delivery, not a mandate to reproduce Work Radar's architecture. Apply universal architecture, diagnosis, evidence, security, restoration, path-of-least-resistance, and user-presence rules broadly. Apply PAC, Copilot Studio, browser, semantic, persistence, reconciliation, and diagnostic rules only when those concerns exist in the approved design.

If new evidence invalidates the current implementation path, stop the affected work, record the evidence, reassess the supported native alternatives, and change path rather than continuing a disproven approach.

## Intake procedure

1. Inspect all supplied conversation and project context before asking anything. Reuse answers and facts already present; do not ask the user to repeat them.
2. Record the objective and source material in the project's `.agent-factory/objective.md` using `templates/objective.md`.
3. Separate facts, assumptions, and unknowns. Label each assumption and explain its source or safe-default basis. Never present an assumption as a user-provided fact.
4. For each unknown, record whether its answer could materially change required behavior, architecture, authoritative data, identity/authentication, permissions, consequential actions, user experience, evaluation, or deployment.
5. Ask only about unknowns with material impact that must be resolved now. Prefer one grouped clarification round. For each question, explain the decision it affects and offer safe recommended defaults when available. Defaults are proposals, not accepted answers.
6. Defer details that can be safely established during architecture or preflight. Record the deferral and the stage that must resolve it instead of asking prematurely.
7. Do not draft architecture while a consequential unknown blocks a sound architecture decision. Do not draft the implementation specification before architecture is recorded. If a second clarification round is needed, limit it to genuinely blocking unknowns revealed by the first answers.
8. Persist answers and update the intake disposition. Proceed to architecture only when no blocking consequential unknown remains or the user explicitly accepts a documented assumption.

## Build orchestration and resume

1. Do not preflight or build until architecture and specification are approved. Record approval only after an explicit user decision; the approved specification digest is computed from the exact `.agent-factory/spec.md` bytes.
2. Use repository helper `../../../scripts/build_state.py` to store the digest, enforce V1 state transitions, verify integrity, dependency-order manifest tasks, and persist state. Do not implement these gates informally in prose.
3. Before initial build, resume, and final verification, verify the stored hash. On mismatch, persist `SPEC_CHANGED`, block affected work, and require an updated specification plus explicit reapproval and a new digest.
4. Generate manifest tasks only from an approved specification and accepted architecture. Map every requirement to a registered capability intent; record dependencies, selected provider, output artifact, status, and evidence.
5. A task is `COMPLETE` only with implementation evidence and `VERIFIED` only with verification evidence. Do not mark or reuse work as verified based solely on a prior status.
6. On resume, inspect existing platform artifacts and record inspection evidence. Reuse a completed task only when its artifact and verification evidence remain valid. Restart an inspected incomplete task; block a task whose artifact was not inspected or whose prior side-effect outcome is unknown. Continue independent dependency-ready work when safe.
7. Persist state and manifest progress after each transition. Never include credentials, secret values, or authentication material in project state, manifest evidence, fixtures, or logs.

## Inputs

- Ordinary-language business objective.
- Conversation, repository, and project context already supplied.
- Clarification responses and explicitly accepted assumptions.
- Environment or capability evidence when available.

## Outputs

- Persisted objective, context inventory, explicit facts, assumptions, unknowns, questions, and responses.
- Intake disposition: `CLARIFICATION_REQUIRED` or ready for architecture (`ARCHITECTING`).
- Later lifecycle artifacts are governed by the specification and approval gates.

## Dependencies

- Skill host capable of loading repository skills (host discovery is environment-specific).
- Project control-plane templates and persisted `.agent-factory/` directory.
- Microsoft platform capabilities only when selected by an approved architecture; resolve their availability just in time.

## Implementation status

Implemented as procedural skill guidance, reference policy, objective template, and static golden intake records. Runtime behavior depends on the compatible skill host and has not been exercised through GitHub Copilot CLI in this environment.

## References

- `references/clarification-policy.md`
- `references/architecture-rules.md`
- `references/capability-registry.md`
- `references/specification-contract.md`
- `references/build-routing.md`
- `references/engineering-guardrails.md`
- `../../../scripts/build_state.py` (state and manifest contract)

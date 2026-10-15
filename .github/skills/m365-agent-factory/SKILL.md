---
name: m365-agent-factory
description: Turn a business objective into a clarified, approved, and verifiable plan for a Microsoft 365 Copilot agent.
---

# M365 Agent Factory

## Purpose

Guide the control-plane lifecycle: objective intake, requirement extraction, minimal clarification, architecture selection, specification, explicit approval, and implementation orchestration. Microsoft capabilities own platform authoring, execution, evaluation, and ALM.

## Boundaries

This is a procedural orchestration skill, not an agent runtime, platform SDK, or substitute for Copilot Studio, Power Automate, Dataverse, evaluation tools, or PAC CLI. Do not invent tenant or environment facts, connector operations, schemas, credentials, permissions, or URLs. Never begin implementation before the specification is approved. Production deployment and organization-wide publication require explicit approval.

## Intake procedure

1. Inspect all supplied conversation and project context before asking anything. Reuse answers and facts already present; do not ask the user to repeat them.
2. Record the objective and source material in the project's `.agent-factory/objective.md` using `templates/objective.md`.
3. Separate facts, assumptions, and unknowns. Label each assumption and explain its source or safe-default basis. Never present an assumption as a user-provided fact.
4. For each unknown, record whether its answer could materially change required behavior, architecture, authoritative data, identity/authentication, permissions, consequential actions, user experience, evaluation, or deployment.
5. Ask only about unknowns with material impact that must be resolved now. Prefer one grouped clarification round. For each question, explain the decision it affects and offer safe recommended defaults when available. Defaults are proposals, not accepted answers.
6. Defer details that can be safely established during architecture or preflight. Record the deferral and the stage that must resolve it instead of asking prematurely.
7. Do not draft architecture while a consequential unknown blocks a sound architecture decision. Do not draft the implementation specification before architecture is recorded. If a second clarification round is needed, limit it to genuinely blocking unknowns revealed by the first answers.
8. Persist answers and update the intake disposition. Proceed to architecture only when no blocking consequential unknown remains or the user explicitly accepts a documented assumption.

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

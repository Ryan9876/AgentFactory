# M365 Agent Factory — V1 product and build specification

Status: authoritative bootstrap baseline; implementation is not started. This document is the source for the implementation plan. Mandatory requirements use stable unique `REQ-NNN` identifiers.

## 1. Product objective and boundary

M365 Agent Factory is a low-effort system for designing and developing useful Microsoft 365 Copilot agents with Copilot Studio and Power Platform. It is a thin orchestration/control-plane skill pack. Microsoft tooling performs platform authoring, workflow execution, data management, evaluation, and ALM where supported.

V1 custom skills are `m365-agent-factory`, `power-platform-resilience`, and `agent-spec-verifier`. V1 excludes a custom graphical UI, custom runtime, custom Copilot Studio schema, custom Power Automate API wrapper, Dataverse SDK abstraction, autonomous tenant governance, fully autonomous Production deployment, autonomous organization-wide publication, generalized Power Apps generation, generalized CI/CD, arbitrary custom connector creation, and duplication of Microsoft evaluation methodology.

## 2. Users and outcomes

Primary users are makers, solution architects, and developers who need to turn a business objective into a reviewable, implementable, evaluated, and packageable M365 Copilot agent. The business outcome is reduced effort and rework while retaining explicit human approval, traceability, and release evidence.

Channels, exact success thresholds, and tenant-specific policies are project-specific and must be supplied or decided during clarification/approval. The Factory must not invent quality thresholds.

## 3. Requirements

### Objective intake

- **REQ-001 (mandatory):** Accept an objective expressed in ordinary language.
- **REQ-002 (mandatory):** Separate supplied facts, assumptions, and unknowns in persisted project context.
- **REQ-003 (mandatory):** Inspect all supplied conversation and project context before asking clarification questions.
- **REQ-004 (mandatory):** Ask only questions whose answers could materially change architecture, security, cost, user experience, acceptance, or release safety.
- **REQ-005 (mandatory):** Prefer one grouped clarification round and offer safe recommended defaults when the user can reasonably choose them.

### Architecture

- **REQ-006 (mandatory):** Produce and record an architecture decision before drafting implementation specification.
- **REQ-007 (mandatory):** Justify each proposed platform component and prefer the lowest-complexity suitable architecture.
- **REQ-008 (mandatory):** Explicitly decide whether knowledge, skills, tools/actions, Power Automate, Dataverse, additional agents, MCP/API integration, custom connectors, or custom code are needed.
- **REQ-009 (mandatory):** Use Standard Copilot Studio as the default harness. Choose a newer GHCP-style harness only by explicit request or material architectural advantage, with required tooling and acceptable maturity/compatibility; record the decision.
- **REQ-010 (mandatory):** Apply the knowledge/skill/tool distinctions, Power Automate and Dataverse criteria, additional-agent boundary, and custom-development preference hierarchy in `architecture-rules.md`.

### Specification

- **REQ-011 (mandatory):** Generate a project specification before implementation with the applicable fields listed below.
- **REQ-012 (mandatory):** Give each mandatory functional or nonfunctional requirement a stable unique `REQ-NNN` identifier and preserve IDs through implementation and verification.
- **REQ-013 (mandatory):** Record known assumptions, dependencies, unresolved blockers, acceptance criteria, release gates, and evaluation plan explicitly.

The generated specification includes, where applicable: Objective; Business outcome; Users; Channels; Success criteria; In scope; Out of scope; User scenarios; Agent responsibilities; Architecture; Instructions; Knowledge; Skills; Tools/actions; Power Automate flows; Dataverse components; External systems; Identity/authentication; Permissions; Confirmation rules; Failure handling; Escalation; Observability; ALM/deployment; Functional requirements; Resilience requirements; Evaluation plan; Acceptance criteria; Release gates; Known assumptions; Known dependencies; Unresolved blockers.

### Approval and integrity

- **REQ-014 (mandatory):** Do not start implementation until the user approves the specification.
- **REQ-015 (mandatory):** At approval, calculate SHA-256 of `.agent-factory/spec.md` and persist it as `approved_spec_sha256` in `state.json`.
- **REQ-016 (mandatory):** Recalculate and compare the spec hash before initial build, build resume, and final verification. A mismatch sets `SPEC_CHANGED`, blocks progress, and requires reapproval.

### Preflight

- **REQ-017 (mandatory):** Confirm the target environment before implementation; default to Development.
- **REQ-018 (mandatory):** Check/load only external capabilities required by the approved architecture.
- **REQ-019 (mandatory):** If a required capability, access, permission, policy, or input is missing, record an explicit blocking state and dependency.
- **REQ-020 (mandatory):** Never invent tenant/environment IDs, schemas, credentials, URLs, connector operations, or other live-system facts.

### Build and resume

- **REQ-021 (mandatory):** Generate a dependency-ordered build manifest from the approved specification.
- **REQ-022 (mandatory):** Delegate platform implementation to the responsible Microsoft capability, passing only relevant requirements and context.
- **REQ-023 (mandatory):** Update manifest status and requirement traceability as implementation/evidence completes.
- **REQ-024 (mandatory):** Persist enough state to inspect existing artifacts and resume interrupted work at the first incomplete component, reusing completed verified work.

The generated agent's control-plane state directory is:

```text
.agent-factory/
├── objective.md
├── clarifications.md
├── architecture.md
├── spec.md
├── build-manifest.md
├── state.json
├── traceability.csv
├── acceptance-report.md
└── evals/
```

This stores Factory state and does not replace Copilot Studio project files, Power Automate artifacts, Dataverse solutions, or other Microsoft-owned platform artifacts.

V1 state values are exactly:

```text
OBJECTIVE_CAPTURED
CLARIFICATION_REQUIRED
ARCHITECTING
SPEC_DRAFTED
AWAITING_APPROVAL
APPROVED
PREFLIGHT
BUILDING
VERIFYING
ITERATING
READY_TO_PACKAGE
BLOCKED
COMPLETE
SPEC_CHANGED
```

### Resilience

- **REQ-025 (mandatory):** Apply and document identity/authentication, least privilege, and user-context versus service-context decisions.
- **REQ-026 (mandatory):** Define consequential side effects and confirmation requirements before execution.
- **REQ-027 (mandatory):** Define retries, retry safety, idempotency, duplicate prevention, partial failure, compensation/recovery, timeouts, and unavailable-dependency behavior where applicable.
- **REQ-028 (mandatory):** Define missing-permission behavior, user-facing errors, in-entitlement alternatives, and safe stop behavior. Do not recommend requesting elevated access or changing tenant policy under the existing-entitlements-only program rule.
- **REQ-029 (mandatory):** Define connection references, environment variables, secret handling, logging/correlation, and observable DLP/policy dependencies where applicable.

### Evaluation and verification

- **REQ-030 (mandatory):** Plan evaluation for happy paths, realistic variants, ambiguity, missing inputs, grounding, tool selection, failures, permissions, side effects, out-of-scope requests, and applicable safety/trust scenarios.
- **REQ-031 (mandatory):** Use thresholds provided/approved for the project; do not invent quality thresholds.
- **REQ-032 (mandatory):** Verify in this order: spec integrity → requirement coverage → platform validation → functional verification → evaluation → resilience review → verdict.
- **REQ-033 (mandatory):** Use only verdicts `SHIP`, `ITERATE`, and `BLOCK`.
- **REQ-034 (mandatory):** Permit `SHIP` only when every mandatory requirement has both implementation evidence and verification evidence.
- **REQ-035 (mandatory):** Find the smallest owning component for a defect, route its fix to the responsible platform skill/tool, retest the affected component, and rerun required release tests before final acceptance.
- **REQ-036 (mandatory):** Never weaken an approved requirement merely to make a test pass; route proposed requirement changes through spec change and reapproval.

### Packaging and release boundary

- **REQ-037 (mandatory):** Produce an acceptance report containing agent, environment, approved spec hash, architecture, built components, evaluation result, requirement coverage, known limitations, manual deployment steps, remaining admin approvals, and release verdict.
- **REQ-038 (mandatory):** Keep Production deployment and organization-wide M365 publication behind explicit approval; V1 does not perform either autonomously.

## 4. Architecture baseline

Apply `docs/architecture.md` and `.github/skills/m365-agent-factory/references/architecture-rules.md`. Microsoft-provided agent, flow, data, evaluation, and ALM capabilities are reused. The capability registry is mutable and records evidence/compatibility; the design does not pin to an unverified command.

## 5. Deterministic helper contracts

Helpers are planned only; do not interpret these interfaces as implemented behavior.

### `scripts/spec_hash.py`

Future CLI accepts a project root (default current directory), reads `.agent-factory/spec.md` as bytes, and emits the lowercase SHA-256 digest. It uses Python standard library only. Approval persists `{"approved_spec_sha256":"..."}`. Before build, resume, and final verification, the digest is recomputed; a mismatch is `SPEC_CHANGED` and requires reapproval. Planned tests cover known digest, missing file, byte-for-byte sensitivity, and stable output.

### `scripts/traceability_check.py`

Future CLI reads requirements from the approved specification and `traceability.csv`, accepts a release/final mode, and reports actionable errors with nonzero exit status on invalid coverage. CSV columns, in order:

```text
requirement_id,requirement_summary,mandatory,implementation_artifact,implementation_evidence,verification_id,verification_evidence,status
```

IDs follow `REQ-NNN`. The checker must fail if a mandatory requirement is missing, an unknown requirement appears, implementation evidence is absent, or (at release) verification evidence is absent. Planned tests cover each failure, optional requirements, and complete coverage. Python standard library only.

## 6. Acceptance scenarios

1. **Knowledge-only:** “Build an HR policy agent using SharePoint policy documents.” Expected: Standard Copilot Studio and SharePoint knowledge; no Power Automate, Dataverse, or child agent absent another requirement.
2. **IT ticketing:** “Help service-desk users troubleshoot incidents from internal documentation and open an engineering ticket when escalation is required.” Expected: knowledge, procedural troubleshooting skill when justified, ticket action/tool or flow, side-effect policy, and no unnecessary Dataverse.
3. **Approval workflow:** “Collect a request, determine the required approver, obtain approval, record the outcome, and notify the requester.” Expected: agent and Power Automate; persistent state source; Dataverse only if no other authoritative system owns the state; recovery/error behavior and explicit acceptance tests.
4. **Ambiguous objective:** “Build a refund agent.” Expected: consequential clarification and no invented commerce/payment integration.
5. **Interrupted build:** Read persisted state, inspect existing artifacts, reuse completed verified work, and resume at the first incomplete component.
6. **Spec drift:** Change the approved spec. Expected: `SPEC_CHANGED`; `BLOCK` until reapproved.

## 7. V1 non-goals

No custom graphical Agent Factory UI; custom runtime; custom Copilot Studio schema implementation; custom Power Automate API wrapper; custom Dataverse SDK abstraction; autonomous tenant governance changes; fully autonomous Production deployment; autonomous organization-wide Copilot publication; generalized Power Apps generation; generalized CI/CD platform; arbitrary custom connector creation; or duplicated Microsoft evaluation methodology.

## 8. Release gates

V1 acceptance requires all mandatory requirements to have implementation and verification evidence, successful applicable platform validation and approved evaluations, resilience review, acceptance report, and `SHIP`. A real Development-environment pilot and verification of tool installation/host compatibility are dependencies before declaring operational readiness. Production and tenant-wide publication remain separately approved actions.

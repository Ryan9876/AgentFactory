# Qualification Labs — consolidated status

**Checkpoint:** 2026-10-23
**Branch at checkpoint:** `codex/labs-bc-auth-checkpoint`
**Scope:** Original four-lab evidence consolidation and local Lab C fixture-contract audit. No tenant resource or existing agent was changed. No merge or push occurred.

This summary separates platform support, current-environment constraints, and runtime evidence. The qualification index in [`config/qualification-labs.yaml`](../../config/qualification-labs.yaml) is the machine-readable state source. Durable supporting records are kept in [`evidence/`](evidence/); project-local `.agent-factory/` state is not part of this repository baseline.

## Verified capabilities and local evidence

| Lab | Verified within the stated boundary |
|---|---|
| A — Copilot Studio MCP | Fresh MCP authentication, Development selection, live catalog, connection listing, and workflow listing succeeded. Agent inventory was blocked by missing `prvReadbot`; lifecycle mutation was not attempted. |
| B — Declarative agent lifecycle | Read-only target preflight established that the approved Production target is blocked for WIQD provisioning by the known disabled sideload policy. No qualifying Development/Test target was identified in available local surfaces. Azure subscription readiness and downstream uniqueness/cleanup gates remain unresolved. See [Lab B evidence](declarative-agent-lab-b.md) and [preflight record](evidence/lab-b-preflight.json). |
| C — Host-composed Work IQ | The local fixture contract is `SOURCE_QUALIFIED` for definition and fail-closed preconditions only. The complete candidate corpus/tool scope is unavailable; no fixture was run and runtime context transfer remains `NOT_TESTED`. See [Lab C evidence](host-composed-work-iq-lab-c.md) and [fixture record](evidence/lab-c-fixture-contract.json). |
| D — Direct Work IQ MCP | The fixed program premise blocks the route under current tenant/security prerequisites. No direct authentication, schema, retrieval, or evaluation operation was qualified. |

## Fixed constraints and unresolved gates

| Lab | Constraint or missing evidence | Disposition |
|---|---|---|
| A | Missing `prvReadbot` blocks the tested Development agent-inventory route. Do not bypass or reopen it. | `COMPLETE`; `CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT`; lifecycle remains `NOT_TESTED`. |
| B | Current Production target has disabled custom-app upload/sideload; no qualifying Development/Test target was identified. Azure readiness, effective target correlation, complete title inventory, and complete cleanup-absence proof remain unresolved. | `PREFLIGHT_BLOCKED`; target `UNQUALIFIED`; `CREATE_ALLOWED=NO`. |
| C | Complete effective knowledge and tool-retrieval scope is not available through the inspected supported read-only sources. This is an evidence-completeness gap, not a demonstrated permission denial. | `RUNTIME_NOT_TESTED`; fixtures remain designed, not run. |
| D | The program premise records fixed tenant enablement, delegated permission/consent, service-principal, and Copilot Credits/spending constraints. Individual current states were not reverified. | `ASSESSMENT_COMPLETE`; `CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT`; direct operations remain `NOT_TESTED`. |

No lab created a resource in this checkpoint, so cloud cleanup was unnecessary. The Lab B approval applies only to the frozen bytes recorded as the single active specification in the qualification index; its target gate still prohibits creation. Labs A and D remain unchanged.

## Local evidence-contract result

The Lab C tracked fixture record and repository test preserve the distinction between `SOURCE_QUALIFIED` local fixture preconditions and `RUNTIME_NOT_TESTED` context transfer. The positive fixture requires an attributable host citation and complete-corpus exclusion; the unsupported fixture requires absence checks in host context and the full agent corpus; the boundary fixture expects non-disclosure and no action. The recorded inspection had zero prompts and source-content queries, no declared-tool invocation, and no agent or tenant mutation.

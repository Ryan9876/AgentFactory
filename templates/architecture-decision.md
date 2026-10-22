# Architecture decision record

- Decision ID:
- Status: `DRAFT` | `CLARIFICATION_REQUIRED` | `DECIDED_WITH_UNRESOLVED_DEPENDENCIES` | `DECIDED`
- Objective record:
- Accepted by user: `yes` | `no` (record decision date/evidence below)
- Specification status: not drafted until architecture is decided
- Agent type/runtime:
- Authoring/build tool:
- Buildability: `CLOUD_BUILDABLE` | `CLOUD_BUILDABLE_WITH_MANUAL_DEPLOY` | `PORTAL_STEP_REQUIRED` | `BLOCKED`
- Work IQ mode: `not_required` | `host_composed` | `direct_mcp_conditional` | `embedded_disallowed`
- Simplest viable path: `Use` | `Configure` | `Integrate` | `Automate` | `Extend` | `Build`
- Native capability considered / demonstrated gap at earlier levels:
- Security/data boundaries and implementation surface:
- Runtime qualification plan (source validation is not runtime qualification):
- Rollback/restoration plan (when applicable):
- Stop/reassessment conditions:
- User acceptance / date:

For each row, state the selection (including `Not required` / `None selected`), rationale, dependency, and evidence status. Evidence status is one of `verified`, `available`, `not_required`, `not_yet_verified`, or `blocked`. Use `verified` only after a concrete check in the relevant host/environment.

| Component | Selection | Rationale / requirement served | Dependency or evidence needed | Evidence status |
| --- | --- | --- | --- | --- |
| Harness | Select least-complex viable supported architecture |  |  | not_yet_verified |
| Knowledge |  |  |  | not_required |
| Skills |  |  |  | not_required |
| Tools/actions |  |  |  | not_required |
| Power Automate |  |  |  | not_required |
| Dataverse/state owner |  |  |  | not_required |
| Additional agents |  |  |  | not_required |
| External integrations |  |  |  | not_required |
| Custom development |  |  |  | not_required |

## Alternatives considered

| Alternative | Reason selected or rejected |
| --- | --- |

## Assumptions

| Assumption | Basis | Accepted by user? |
| --- | --- | --- |

## Unresolved blockers and dependencies

| Item | Blocks which decision/task | Owner or verification stage |
| --- | --- | --- |

## Decision rationale

<!-- Explain why this is the lowest-complexity architecture that meets the objective. -->

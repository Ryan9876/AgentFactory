---
name: power-platform-resilience
description: Review approved M365 agent designs for identity, side-effect safety, failure recovery, configuration, and operational evidence.
---

# Power Platform resilience

## Purpose

Provide cross-cutting policy/reference guidance for resilient and safe Copilot Studio and Power Platform designs. Review against the approved architecture and specification, and identify requirements, dependencies, and gaps for the owning platform capability.

## Boundaries

This is a policy/reference skill. It does not execute platform changes, configure connectors, run flows, grant permissions, or replace Microsoft validation. Do not invent tenant policy, roles, connection names, environment variables, secret values, or platform behavior. Record unavailable facts as dependencies and route implementation or validation to the responsible Microsoft capability.

## Inputs

- Approved architecture and specification.
- Action inventory and user/service identity decisions.
- Verified environment, connector, permission, and policy evidence where available.
- Applicable project resilience and acceptance requirements.

## Outputs

- Per-action identity and permission review.
- Side-effect, confirmation, retry/idempotency, failure/recovery, and escalation criteria.
- Configuration, secret-handling, observability, and policy-dependency findings.
- Applicability rationale, unresolved dependencies, and remediation owner.

## Review procedure

1. Review every knowledge source, tool/action, flow, state store, external system, and release operation in the approved design.
2. Apply `references/identity-and-permissions.md` to each action and data boundary.
3. Apply `references/side-effect-safety.md` before any externally visible or consequential action.
4. Apply `references/resilience-rules.md` to failure modes and runtime operations; mark non-applicable items with a reason.
5. Compare scenarios against `tests/fixtures/resilience/scenario-coverage.csv` and record evidence gaps.
6. Route each finding to the smallest owning component. Do not weaken an approved requirement to clear a finding.

## Dependencies

Approved project artifacts and evidence from selected Microsoft platform capabilities. Actual configuration, permission, DLP/policy visibility, and tenant behavior require environment-specific validation when the project reaches preflight or verification.

## Implementation status

Implemented as review policy, reference guidance, and a static golden-scenario coverage matrix. It has not executed or validated changes in a live Power Platform environment.

## References

- `references/identity-and-permissions.md`
- `references/side-effect-safety.md`
- `references/resilience-rules.md`

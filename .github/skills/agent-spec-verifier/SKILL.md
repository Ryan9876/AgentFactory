---
name: agent-spec-verifier
description: Verify a Microsoft 365 agent implementation against its approved specification and report a release verdict.
---

# Agent specification verifier

## Purpose

Verify the approved spec, requirement evidence, platform validation, functional behavior, evaluation, and resilience in the required order. Route failures to the smallest owning component and issue one evidence-based final verdict.

## Boundaries

This is a verification/control-plane skill. It does not author or execute Copilot Studio agents, flows, Dataverse changes, or Microsoft evaluations. Microsoft capabilities produce platform and evaluation evidence. Do not treat a skill/tool listing, a status label, or an uninspected artifact as verification evidence. Do not weaken an approved requirement to pass a check. Production deployment and organization-wide publication remain explicit approval boundaries.

## Inputs

- Approved `.agent-factory/spec.md` and `state.json` digest.
- `.agent-factory/traceability.csv` and implementation artifacts/evidence.
- Platform-validation, functional-test, evaluation, and resilience-review evidence from responsible capabilities.
- Explicitly approved project evaluation thresholds.

## Outputs

- Ordered gate results and findings.
- Requirement coverage and smallest owning component for each gap.
- Remediation routing and required retests.
- Acceptance report and exactly one verdict: `SHIP`, `ITERATE`, or `BLOCK`.

## Verification procedure

1. From the Agent Factory repository root, invoke `python3 -m scripts.agent_spec_verifier --project-root <agent-project-root> --evidence-file <evidence-json>`. The evidence JSON contains inspectable results from the responsible platform capabilities; the helper checks the hash and mandatory requirement evidence before accepting later gate results.
2. Follow `references/verification-protocol.md` without reordering gates. A failed/blocked gate stops later checks until the issue is resolved and verification is rerun.
3. Apply `references/traceability-rules.md`; a mandatory requirement needs both implementation and verification evidence for release.
4. Apply `references/verdict-rules.md`. `SHIP` requires every gate to pass and no unresolved blockers.
5. For each finding, identify the smallest owning component and route remediation to its Microsoft capability. Retest the affected component and rerun required release tests.
6. Populate `templates/acceptance-report.md` with evidence references, limitations, manual steps, remaining approvals, and the returned verdict.

## Dependencies

Approved project artifacts; deterministic specification integrity and traceability helpers; platform and evaluation evidence from the currently available registered Microsoft capabilities; resilience review guidance.

## Implementation status

Implemented as verifier policy and a deterministic local gate module. It consumes evidence records; it does not run Microsoft platform validation or evaluation. Execution through GitHub Copilot CLI and a live Development environment remains unverified. If the local helper cannot run, record that dependency as blocked; do not represent platform evidence as verified.

## References

- `references/verification-protocol.md`
- `references/traceability-rules.md`
- `references/verdict-rules.md`
- `../../../scripts/agent_spec_verifier.py`

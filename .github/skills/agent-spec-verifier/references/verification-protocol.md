# Verification protocol

Run release gates in this exact order:

```text
spec integrity
→ requirement coverage
→ platform validation
→ functional verification
→ evaluation
→ resilience review
→ verdict
```

Stop at the first failed or blocked gate. Later gates are `NOT_RUN` until the issue is resolved and verification is rerun. The project state records `ITERATING` for remediable gaps, `BLOCKED` for unmet prerequisites/unsafe conditions, `SPEC_CHANGED` for digest drift, or `READY_TO_PACKAGE` only after all gates pass without unresolved blockers.

## Gate evidence

1. **Spec integrity:** Compare the exact current `.agent-factory/spec.md` bytes to `approved_spec_sha256`. A mismatch sets `SPEC_CHANGED`, yields `BLOCK`, and prevents all later checks until the changed spec is explicitly reapproved with a new digest.
2. **Requirement coverage:** Run the deterministic traceability validator in release mode. Every mandatory requirement must have a known unique ID, implementation artifact/evidence, verification ID/evidence. A status word alone is not evidence.
3. **Platform validation:** Consume inspectable validation evidence from the responsible Microsoft capability. Tool presence or successful local syntax validation is not platform validation.
4. **Functional verification:** Consume evidence that approved user scenarios and acceptance criteria were exercised against the implementation.
5. **Evaluation:** Consume Microsoft evaluation results for applicable happy paths, realistic variants, ambiguity, missing inputs, grounding, tool selection, failures, permissions, side effects, out-of-scope requests, and applicable safety/trust scenarios. Thresholds must be explicitly approved and the source recorded. If thresholds are missing, the gate is blocked; do not invent them.
6. **Resilience review:** Consume evidence for identity, least privilege, side effects, confirmations, retry safety, idempotency, duplicates, partial failure, recovery, timeouts, unavailable dependencies, permissions, configuration, secrets, observability, DLP/policy visibility, and escalation where applicable. Unsafe behavior blocks release.

From the Agent Factory repository root, run `python3 -m scripts.agent_spec_verifier --project-root <agent-project-root> --evidence-file <evidence-json>`. The JSON object accepts evidence records with `status` (`pass`, `fail`, or `blocked`) and an inspectable `evidence` reference for platform, functional, evaluation, and resilience gates. Evaluation also requires `thresholds_approved: true` and `thresholds_source`; resilience may set `unsafe: true`. It verifies integrity and traceability locally; it does not run the Microsoft checks represented by those evidence records.

## Blocker accounting and remediation

Inspect the specification's `Unresolved blockers` section and persisted state blockers. Any unresolved blocker prevents `SHIP`. Route each finding to its smallest owning component and responsible Microsoft capability. Retest the changed component and rerun required release checks; never weaken an approved requirement to obtain a pass.

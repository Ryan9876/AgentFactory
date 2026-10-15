# V1 workflow

The state values are exact contract values. A project may move among them as work proceeds, while `SPEC_CHANGED` requires approval again and `BLOCKED` records a dependency or decision that prevents safe progress.

```text
OBJECTIVE_CAPTURED
→ CLARIFICATION_REQUIRED (when a consequential unknown remains)
→ ARCHITECTING
→ SPEC_DRAFTED
→ AWAITING_APPROVAL
→ APPROVED
→ PREFLIGHT
→ BUILDING
→ VERIFYING
→ ITERATING (when evidence shows a fix is needed; then verify again)
→ READY_TO_PACKAGE
→ COMPLETE
```

`BLOCKED` can be entered when required information, permission, capability, or environment is unavailable. A changed approved specification enters `SPEC_CHANGED` and blocks build/resume/final verification until reapproval. Persist the current state and artifact pointers in `.agent-factory/state.json` so interrupted work can resume.

## Stage contract

1. Capture an ordinary-language objective. Separate explicit facts, assumptions, and unknowns; use supplied context first.
2. Ask a grouped clarification round only for consequential unknowns. Offer safe defaults where possible.
3. Decide architecture before writing the build specification. Justify each component and prefer the least complex suitable option.
4. Draft the specification with stable `REQ-NNN` IDs for mandatory requirements. Record assumptions, dependencies, blockers, evaluations, and acceptance criteria.
5. Obtain explicit approval. Hash `spec.md` with SHA-256 and store the approved digest.
6. Preflight the Development target and only the capabilities the design needs. Do not invent IDs, schemas, URLs, credentials, or connector operations.
7. Build from a dependency-ordered manifest by routing focused requirements to the responsible Microsoft capability. Persist progress and evidence.
8. Verify in order: spec integrity, requirement coverage, platform validation, functional verification, evaluation, resilience review, verdict.
9. Route fixes to the smallest owning component, retest it, and rerun release tests. Package only after `SHIP`.

Production deployment and organization-wide M365 publication require explicit approval in V1.

# Agent specification generation and approval contract

## Generation input and gate

Draft a specification only after the objective intake gate is clear and the architecture decision is recorded. Inputs are the persisted objective/context, clarification answers and accepted assumptions, architecture decision, and applicable project requirements. Use `templates/agent-spec.md` and write the project copy to `.agent-factory/spec.md`.

If a consequential unknown prevents a safe requirement or architecture decision, keep the state at `CLARIFICATION_REQUIRED` or `BLOCKED`, record the blocker, and do not present the draft as ready for approval.

## Draft contents

Include every applicable field listed in the template. For requirements, preserve existing stable IDs or assign each mandatory requirement a unique `REQ-NNN` identifier. Do not renumber an existing requirement because its wording changed; route such changes through spec change and approval. Link each requirement to observable acceptance evidence.

Always account for assumptions, known dependencies, unresolved blockers, evaluation thresholds, and release gates. When no blockers remain, explicitly record `None identified` after checking; do not leave the section blank or silently imply resolution. Leave unavailable facts as unresolved dependencies rather than inventing them.

Success criteria and evaluation thresholds must come from supplied project requirements or explicit user approval. If none are supplied, state `Not supplied; approval required before evaluation thresholds are set`. Do not invent a numeric or qualitative pass threshold.

## Approval transition

Generation ends at `AWAITING_APPROVAL`. The draft must never be marked `APPROVED` by generation, validation, or the skill's own judgment. Obtain an explicit human approval of the content. Record approver and time, compute SHA-256 of the exact `.agent-factory/spec.md` bytes with `scripts/spec_hash.py`, and store the result as `approved_spec_sha256` in `state.json`.

The helper accepts `--project-root` and emits the digest; `--approved-hash` compares a current digest and emits `SPEC_CHANGED` on mismatch. Check the approved hash before initial build, resume, and final verification. Any mismatch sets `SPEC_CHANGED`, blocks implementation/verification, and requires a changed draft plus explicit reapproval and a new digest.

Approval is a separate explicit state transition. After explicit approval and a matching digest, the project may enter `APPROVED`; specification generation alone must not do so.

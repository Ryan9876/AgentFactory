# Build manifest

- Generated from approved spec hash:
- Target environment: Development by default; confirm and record the actual target before preflight.
- Architecture decision:

Tasks are dependency ordered. Requirement IDs must exist in the approved specification. The owning capability is a stable capability intent resolved through the current registry; record the selected provider and its evidence. Keep platform artifacts in Microsoft-owned project/solution locations.

| Task ID | Dependencies | Requirement IDs | Owning capability | Provider | Configuration surface and rejected-route evidence | Output artifact | Status | Implementation evidence | Verification evidence | Artifact inspection evidence |
|---|---|---|---|---|---|---|---|---|---|

Statuses are `PENDING`, `READY`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`, or `VERIFIED`. `COMPLETE` means implementation evidence exists but the task is not yet verified. Only `VERIFIED` tasks with current artifact inspection evidence can be reused as completed work or satisfy a dependent task. Record a concrete blocking reason rather than guessing.

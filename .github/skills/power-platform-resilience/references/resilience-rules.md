# Resilience review rules

Review each selected knowledge, action, flow, state, integration, and release component. Define applicable controls from project requirements and supported platform behavior. When a control does not apply, record why. Do not invent numeric retry counts, timeout durations, service guarantees, or quality thresholds; obtain them from authoritative platform limits or explicit project approval.

## Retry and duplicate safety

- Classify failures as transient, permanent, permission/configuration, or unknown using available evidence.
- Retry only failures that are safe to retry. A retry policy must state its scope, stop condition, and how the user or operator learns that work remains incomplete.
- Before retrying a write or other side effect, establish whether the operation is idempotent. Use a supported idempotency key or equivalent deduplication strategy when available; do not invent provider support.
- Prevent duplicate execution across repeated turns, flow replays, timeouts, or user resubmissions. Persist a correlation/request identity or use platform-native deduplication where supported. If safe deduplication is unavailable, stop for confirmation or manual recovery.
- Do not blindly replay an operation when its first outcome is unknown. Inspect authoritative state first where possible.

## Partial failure and recovery

- Identify the sequence of externally visible steps and the state after each step.
- Explain which completed steps remain committed when a later step fails.
- Define compensation only where the action is safe, supported, and authorized; otherwise provide a recovery path and owner.
- Preserve enough state and correlation evidence to resume or reconcile interrupted work without duplicating side effects.
- Do not report overall success when a required step failed or its result is unknown.

## Timeouts and unavailable dependencies

- State which operation can time out, how its outcome is determined, and whether cancellation actually stops downstream work.
- For an unavailable dependency, fail safely, preserve recoverable inputs/state, and provide a clear retry or escalation path.
- Avoid unbounded waits. Use platform-supported limits or explicit project requirements; do not invent durations.
- Make dependency failures distinguishable from invalid input, authorization failure, and successful empty results.

## Permissions and user-facing failures

- Missing, expired, revoked, or insufficient permission must not be bypassed. Stop the affected action and explain what can safely continue.
- Give a concise user-facing error without exposing tokens, secret values, internal stack traces, or unnecessary sensitive data.
- Tell the user/operator what action failed, whether any partial work occurred, and the safe next step.
- Escalate unresolved security, policy, data integrity, or consequential-action failures to the named owner. If no owner is known, record it as a dependency and blocker.

## Configuration and secrets

- Define connection references and environment variables as solution configuration where the platform design supports them.
- Separate environment-specific configuration from flow/agent logic and identify the responsible owner and validation stage.
- Store secrets only in an approved secret store or supported secure connection mechanism. Never place credentials in prompts, source, logs, Agent Factory state, fixtures, or version control.
- Specify rotation/expiry handling where relevant; do not record secret values.
- Treat DLP/policy dependencies as verified only when observable through an authoritative check. If a policy is hidden or not inspectable, record that limitation and the required administrator validation.

## Logging and correlation

- Define correlation across an agent turn, action/flow run, external operation, and recovery attempt when supported.
- Record operational outcome, timing, failure category, and safe identifiers needed for diagnosis.
- Minimize logged personal, confidential, or business-sensitive content. Never log credentials or secret material.
- State who can access operational records and how a support owner uses them; do not claim telemetry exists until verified.

## Evidence

Map each applicable concern to scenario and verification evidence using `tests/fixtures/resilience/scenario-coverage.csv`. A policy statement is not evidence that a platform setting or runtime behavior has been validated.

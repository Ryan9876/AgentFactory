# Side-effect safety review

Treat externally visible, consequential, or difficult-to-reverse actions as side effects. Examples include creating or updating records, submitting tickets/requests, sending notifications, approving/rejecting, issuing transactions, and deployment/publication.

## Before execution

- Classify each action by consequence and reversibility; name its target and the initiating authority.
- State what the user must review before confirmation: action, target/recipient, material values, consequences, and any irreversible boundary.
- Require an explicit affirmative confirmation before a consequential action when the specification requires it. Do not infer consent from a request for information or from silence.
- Define cancellation behavior and distinguish “cancelled before submission” from “outcome unknown after submission.”
- Apply the approved identity and least-privilege policy. Do not change identity to make an action succeed.

## Retry and duplicate prevention

- Decide whether the action is safe to repeat before enabling automatic retries.
- Use supported idempotency or deduplication mechanisms where available, and identify evidence for that support. Do not invent provider semantics.
- Prevent repeated user turns, flow replays, and ambiguous timeouts from creating duplicate side effects.
- If the first outcome is unknown, inspect authoritative state before replay. If it cannot be determined safely, stop and escalate.

## Partial outcomes and recovery

- Make clear whether each step completed, failed, or has an unknown result.
- Define authorized compensation when safe; otherwise name the manual recovery owner and preserve correlation details.
- Never claim success for an incomplete multi-step action. Never conceal partial completion from the user or operator.

## Release actions

Production deployment and organization-wide M365 publication remain explicit approval boundaries. Do not execute them autonomously. Development operations must still target an environment positively identified for development and use disposable or approved artifacts.

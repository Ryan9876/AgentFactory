# Work Radar V1 lessons retained for AgentFactory V2

Captured from the Work Radar V1 lessons-learned review on 2026-10-21.

This document is the durable human-facing summary. The enforceable AgentFactory rules derived from it live in `.agents/skills/agentfactory/references/engineering-guardrails.md`, the canonical Codex skill location.

## Why this matters

Work Radar V1 took longer than necessary because multiple issues that looked like agent-design problems were actually defects or limitations in authoring surfaces, browser automation, PAC authentication/session behavior, cloud component lifecycle, or incomplete runtime qualification.

The central lesson is:

**Use the simplest supported Microsoft-native capability first, prove it in the real runtime, and extend only after a specific limitation has been demonstrated.**

Implementation order remains:

**Use → Configure → Integrate → Automate → Extend → Build.**

## Lessons that apply broadly

### Diagnose the layer before redesigning the product

Do not react to a browser, authoring UI, authentication, environment, connector, or runtime failure by changing the agent architecture until the failing layer is localized.

A supported alternative surface is preferable to a custom workaround when the underlying platform/runtime remains sound.

### Static correctness is not runtime qualification

YAML parsing, local tests, PAC acceptance, Dataverse presence, source synchronization, and authoring UI rendering are useful evidence but do not prove runtime semantics.

Treat these as separate states:

- `DESIGNED`
- `IMPLEMENTED`
- `CLOUD_SYNCHRONIZED`
- `RUNTIME_QUALIFIED`

### Treat user-presence boundaries as workflow constraints

MFA, terms acceptance, admin approval, tenant policy changes, and PAC authentication that only works reliably in the user's normal Terminal are not reasons to redesign the product.

AgentFactory should stop cleanly, provide the exact required action, and resume afterward.

### Every temporary cloud experiment needs restoration first

Before a temporary mutation, know the exact component identity, original state, backup, expected restoration hash, blast radius, and zero-write test path where feasible.

Temporary diagnostics should default inactive, zero-write, and non-published.

### Evidence is part of engineering, not post-build documentation

Preserve component IDs, hashes, command exit codes, tested runtime, failure reason, next gate, and what was explicitly not changed.

Freeze qualified components and prefer additive changes around them.

### Stop when new evidence changes the optimal path

`STOP → REASSESS → CHANGE PATH` is a successful engineering outcome when an assumption is disproven or a simpler supported route is discovered.

## Copilot Studio / PAC lessons

Apply these only when a future architecture actually selects Copilot Studio/PAC.

- A modern Copilot Studio UI failure does not prove the Standard agent is broken.
- Use another supported Standard/classic surface when appropriate before redesigning the agent.
- Do not infer harness identity from telemetry, billing, or capacity field names.
- Never invent a Copilot Studio component GUID and assume PAC push will create the cloud component.
- Track component identity/state/hash separately from filenames.
- Require a fresh pre-push pull and a post-push pull/verification for cloud mutations.
- Capture explicit CLI exit status; do not infer success from timestamps or side effects.
- If managed-host PAC authentication is proven unreliable, use a user-presence boundary instead of repeating auth troubleshooting.

## Browser automation lessons

Apply only when browser automation is necessary.

For Power Platform/Copilot Studio work, the proven fallback sequence was:

1. Playwright CLI once.
2. On the known managed-host launch failure, switch to Playwright MCP.
3. Use the user's normal browser for targeted comparison or interactive/user-presence steps.

Chrome DevTools MCP and TinyFish should not be default choices for this corporate Power Platform workflow unless new evidence shows the situation has changed.

## Generative semantic-boundary lessons

Apply only when a future agent has model-derived semantics feeding deterministic behavior.

- Preserve semantic evidence as typed structured data at the point it is first known.
- Do not reconstruct important state later by parsing generated prose.
- Keep source metadata separate from user-action semantics.
- Distinguish explicit negative, absent evidence, failed reasoning, and invalid output.
- Internal semantic fields must not accidentally prompt the user unless prompting is part of the approved behavior.
- Use deterministic policy rules when the business semantics are explicit; do not introduce weighted scoring without a demonstrated need.

## Persistence/idempotency lessons

Apply only when a future agent persists/reconciles records.

Prove identity and idempotency before adding intelligence. Preserve first-detection immutability where the requirements need it.

Keep qualified reconciliation flows narrow; prefer bounded sidecar/extension flows to continuously widening a stable core.

## Security lessons

Every project should record the allowed/forbidden data planes and connectors, identity model, publication boundary, and diagnostic redaction expectations.

Never weaken security merely because a tool is inconvenient. Do not change tenant-wide roles/DLP, disable secure-output protections, or route corporate data through an unapproved external plane simply to make development easier.

## Qualification lessons

Define positive, negative, boundary, non-applicable, and repeatability fixtures where relevant.

Test both `MUST` and `MUST NOT` behavior. A single successful generative run is insufficient when repeatability matters.

## Work Radar details that are not universal defaults

Do not copy these into unrelated agent architectures unless their requirements independently justify them:

- Work Radar's priority bands or semantic field names;
- Calendar → Inbox → Teams implementation order;
- its specific Microsoft List schema;
- its exact reconciliation/lifecycle behavior;
- its product-specific runtime prompts and fixtures.

The value of Work Radar is the engineering method and failure evidence, not a template every future agent must resemble.

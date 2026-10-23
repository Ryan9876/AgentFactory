# AgentFactory engineering guardrails from Work Radar V1

Source: lessons learned from the Work Radar V1 build, captured 2026-10-21.

These rules exist to prevent future AgentFactory builds from repeating known platform, tooling, qualification, security, and delivery failures. Apply the universal rules to every build. Apply Copilot Studio-, PAC-, browser-, semantic-, persistence-, and diagnostic-specific rules only when those surfaces are actually selected by the approved architecture.

The governing principle is:

**Use → Configure → Integrate → Automate → Extend → Build.**

Do not add custom infrastructure until a supported Microsoft-native capability has been tried or a specific limitation has been demonstrated.

## 1. Universal architecture and diagnosis rules

1. Treat every proposed architecture as provisional until the required runtime behavior is qualified in the real target runtime.
2. Static correctness is not runtime qualification. Parsing, local tests, PAC acceptance, Dataverse presence, or authoring-UI display do not prove runtime behavior.
3. Separate platform/tooling diagnosis from product implementation. Localize a failure before editing agent logic.
4. Use this failure taxonomy where applicable: `TOOL_HOST`, `AUTH`, `BROWSER_SESSION`, `ENVIRONMENT_DISCOVERY`, `POWER_PLATFORM_ENVIRONMENT`, `AGENT_LIST`, `AGENT_LOAD`, `COPILOT_STUDIO_AUTHORING_UI`, `TEST_PANEL`, `AGENT_CONFIGURATION`, `TOPIC_RUNTIME`, `FLOW_RUNTIME`, `TOOL_INVOCATION`, `CONNECTOR`, `DATA`.
5. A malfunctioning authoring surface is not evidence that the agent architecture is wrong. Look for another supported native surface before extending or rebuilding.
6. When new evidence changes the optimal path, `STOP`, `REASSESS`, and `CHANGE PATH`. Continuing an invalidated plan is a failure mode; changing course is not.
7. Freeze known-good qualified components. Prefer additive, bounded changes around them over reopening stable components.
8. Distinguish at least `DESIGNED`, `IMPLEMENTED`, `CLOUD_SYNCHRONIZED`, and `RUNTIME_QUALIFIED`. Do not collapse these into a single done state.
9. Distinguish `BLOCKED`, `FAILED`, and `NOT_TESTED/UNQUALIFIED`. They imply different next actions.
10. Store harness/runtime identity explicitly. Do not infer architecture from telemetry, billing, capacity, or UI field names.

## 2. User-presence and authority boundaries

Classify operations before execution:

- `SAFE_AUTOMATION`
- `USER_PRESENCE_REQUIRED`
- `ADMIN_REQUIRED`
- `ARCHITECTURE_DECISION_REQUIRED`

Typical `USER_PRESENCE_REQUIRED` boundaries include MFA, terms acknowledgments, interactive PAC authentication when managed-host persistence fails, and other interactive consent steps.

Typical `ADMIN_REQUIRED` boundaries include tenant policy changes, admin consent, role/DLP changes, and organization-wide publication when policy requires it.

AgentFactory must stop cleanly at a boundary, provide the exact user/admin action or command, preserve state, and resume after the boundary is satisfied.

## 3. Browser/tool-host rules

For Power Platform/Copilot Studio browser automation, use a predeclared fallback rather than ad-hoc tool experimentation.

Keep browser identity and generic regression separate: regular Chrome Stable with the dedicated visible profile `AgentFactory` is the persistent Microsoft identity and interactive-authentication surface. Discover its profile directory from Chrome metadata; do not assume or persist a directory identifier. Do not use this authenticated profile for generic automation or regression. Use Chrome for Testing with a disposable isolated profile for deterministic browser regression. Existing browser sign-in does not prove unattended authentication or runtime qualification.

Preferred sequence when browser automation is truly necessary:

1. Playwright CLI — one attempt.
2. If the known managed-host browser launch failure occurs, record the tool host as environment-blocked and switch immediately to Playwright MCP.
3. Use the user's normal browser only for targeted comparison or a user-presence action.

Avoid Chrome DevTools MCP and TinyFish by default for this corporate Power Platform workflow unless a future build records new evidence that they are the better supported path.

Do not spend project time repeatedly debugging a known tool-host limitation unless browser automation itself is the deliverable.

When automation and platform behavior disagree, use this diagnostic branch:

- normal browser works, automation fails → likely automation/session/profile problem;
- normal browser fails the same way → likely platform/environment/tenant problem.

A browser page is not authoritative cloud component state. Corroborate with supported cloud/PAC source, component identity, hashes, and runtime tests.

## 3.1 Structured configuration before browser automation

For every agent construction or configuration operation, AgentFactory MUST use the highest-priority supported deterministic surface capable of that exact operation: native capability, MCP, CLI, API/SDK, supported code/configuration editor, declarative/source representation, or import/export/package mechanism. This preserves Use → Configure → Integrate → Automate → Extend → Build and the registry's MCP → CLI → API/SDK preference while placing supported editors and structured source ahead of browser UI.

Playwright, browser-use, Chrome automation, Computer Use, browser clicking, and UI field entry MUST NOT configure an operation that a supported structured/editor surface can perform. If browser automation is proposed while any such route is known to work, or its availability has not been checked, STOP → REASSESS → CHANGE PATH. “Easier to click” and “the browser is already open/authenticated” are not evidence.

Browser automation is allowed only for the bounded operation after operation-specific evidence records that every higher-priority structured route is unavailable or insufficient and explains why. Localize a failed MCP/CLI/API/editor route, then check the remaining supported routes; one failure alone does not authorize browser fallback. Return adjacent configuration to structured surfaces immediately. Verify saved state through an authoritative supported surface when possible. Browser clicks and source edits alone do not establish RUNTIME_QUALIFIED.

Keep browser authentication, MFA, consent, account selection, visual/runtime observation, and genuinely portal-only operations available when needed. Authentication can use Chrome while configuration continues through MCP/CLI/API/editor. Preserve the dedicated Chrome Stable AgentFactory identity profile and Chrome for Testing disposable regression profile split.

## 4. PAC and cloud synchronization rules

PAC behavior can differ by execution host. Do not assume authentication/session persistence that works in the user's normal Terminal will work in a managed Codex host.

If managed-host PAC authentication is unreliable, formalize a user-presence boundary instead of repeatedly debugging it:

- Codex authors and validates source, computes hashes, inspects diffs, and prepares exact commands.
- The user runs the required PAC command in the normal Terminal.
- Codex inspects the resulting workspace/cloud state and continues verification.

For every cloud mutation, the default sequence is:

`PULL → VALIDATE → EDIT → VALIDATE → FRESH PULL → BOUNDED DIFF → PUSH → PULL → VERIFY`

Required rules:

1. No PAC push without a fresh pre-push pull.
2. No qualification without an explicit command exit code.
3. Capture command output, exit code, timestamp, and log path when practical.
4. Never infer success from file timestamps or side effects alone.
5. A post-push pull/cloud inspection is required to establish synchronization evidence.

## 5. Copilot Studio component lifecycle rules

Do not assume source editing can create arbitrary new Copilot Studio components merely because it can edit existing ones.

1. Never invent a component GUID/identity unless a supported creation path explicitly requires or permits it.
2. Create new topics/components through a supported creation UI/API/tooling mechanism first; then use source synchronization where supported.
3. Component identity is more important than filename. For each mutable component record: `logical_name`, `component_id`, `component_type`, `expected_state`, `expected_hash`, and `qualification_status`.
4. For Standard-harness agents, if the modern Agents page fails independently of the runtime, use another supported Standard/classic authoring or testing surface rather than redesigning the agent.
5. Do not interpret UI telemetry/capacity fields as proof of harness identity.

## 6. Temporary cloud experiment rules

Never mutate first and plan cleanup later.

Before any temporary cloud experiment require:

- `BACKUP_READY = PASS`
- `RESTORE_HASH_KNOWN = PASS`
- `COMPONENT_ID_KNOWN = PASS`
- `ORIGINAL_STATE_KNOWN = PASS`
- `BLAST_RADIUS_BOUNDED = PASS`
- `ZERO_WRITE_TEST_PATH = PASS`

Diagnostics should default to `INACTIVE`, `ZERO_WRITE`, and `NON_PUBLISHED`.

Enable a diagnostic only for the qualification window, disable it immediately afterward, restore the original bytes/state, synchronize the restoration, and verify the original hash. Restoration is itself a qualification gate.

A borrowed inactive component is an emergency qualification technique, not a preferred product architecture. Prefer a supported purpose-built diagnostic component when one exists.

## 7. Generative-to-deterministic boundary rules

When deterministic downstream behavior depends on a semantic fact, preserve the fact as structured data when it is first known.

Use:

`generative reasoning → typed contract → deterministic validation → deterministic automation`

Do not parse generated prose downstream to reconstruct state that could have been emitted structurally.

General rules:

1. Keep source metadata separate from user-action semantics.
2. Keep existence of a signal separate from whether it applies to the user/action.
3. Do not derive task semantics from convenient source metadata unless the approved requirements say to do so.
4. Internal semantic parameters must not auto-prompt the user unless prompting is explicitly part of the requirement.
5. Distinguish explicit negative, absent evidence, failed reasoning, and invalid output. Do not silently coerce all missing values to false.
6. Prefer deterministic policy rules over weighted scoring when the business semantics can be stated explicitly.
7. For time-sensitive classifications, persist stable evidence and calculate the next reevaluation boundary rather than rescanning everything unnecessarily.

These rules are conditional: apply them only to builds with generative classification or generative-to-deterministic handoff.

## 8. Persistence, identity, and flow scope rules

Before adding more intelligence to a persistent workflow, prove:

- `IDENTITY`
- `IDEMPOTENCY`
- `FIRST_DETECTION_IMMUTABILITY` where applicable

Once a reconciliation/core flow is proven safe and idempotent, keep it narrow. Prefer a stable core plus small bounded extension flows/sidecars over a single flow that accumulates unrelated create/update/enrich/reprioritize/repair responsibilities.

## 9. Security contract

Every project must establish security boundaries before implementation, including where applicable:

- allowed data planes;
- forbidden data planes;
- allowed connectors;
- forbidden connectors;
- publication scope;
- identity model;
- diagnostic redaction rules.

Tooling inconvenience is never a sufficient reason to weaken security. Do not disable secure-output protections, expose corporate data to an unapproved external plane, add a custom API only for observability, or change tenant roles/DLP for convenience without an explicit approved architecture/security decision.

## 10. Qualification and test rules

For every material generative or behavioral contract, define a fixture matrix before runtime qualification:

- positive fixtures;
- negative fixtures;
- boundary fixtures;
- non-applicable fixtures;
- repeatability fixtures.

Every capability must define both `MUST` and `MUST NOT` behavior and test both.

For model-derived behavior, a single successful run is not enough. Important fixtures must be rerun in fresh contexts when repeatability matters. Record `SEMANTIC_REPEATABILITY = PASS` only after that evidence exists.

Runtime qualification must verify the actual selected target runtime, not a surrogate authoring or source-validation surface.

## 11. Evidence and frozen-component rules

Evidence is a first-class project artifact. For each milestone preserve:

- objective;
- environment;
- exact tested component;
- result/state;
- component IDs/hashes where relevant;
- command exit evidence where relevant;
- failure reason;
- next gate;
- what was explicitly not changed.

For critical cloud-synchronized/generated artifacts, record hashes. Once a component is qualified, inventory and freeze it; reopen it only when a later approved requirement actually needs a change.

Recommended frozen-component fields:

`component`, `component_id`, `expected_hash`, `status`, `qualification_date`, `allowed_change_scope`.

## 12. Anti-regression rules

Future AgentFactory builds must enforce these unless a newer verified platform fact explicitly supersedes them:

1. No Production publish without explicit user approval.
2. No tenant-wide setting or DLP change for convenience.
3. No new external service when a supported Microsoft-native capability satisfies the requirement.
4. No new Copilot Studio component identity invented without a supported creation path.
5. No PAC push without a fresh pull.
6. No qualification without explicit exit-code evidence for material external CLI operations.
7. No generative classifier considered qualified without runtime fixtures where the classifier matters to acceptance.
8. No internal semantic parameter may auto-prompt unless prompting is an approved requirement.
9. No temporary diagnostic may remain active after testing.
10. No cloud experiment without an exact restoration path.
11. No downstream prose parsing when structured evidence can be preserved upstream.
12. No architecture redesign solely because one Microsoft authoring surface is malfunctioning.
13. No repeated debugging of a known tool-host limitation when a proven fallback exists.
14. No silent promotion of observed behavior into approved product semantics.
15. No widening of a qualified core workflow without a demonstrated requirement.

## 13. Required decision record additions

Before implementing a feature, the architecture/feature decision should capture:

- Goal — user outcome being achieved.
- Native capability — Microsoft-native capability that already addresses it.
- Simplest path — Use / Configure / Integrate / Automate / Extend / Build.
- Why earlier levels are insufficient — demonstrated limitations only.
- Security impact — data boundaries and identities affected.
- Runtime qualification plan — how behavior will be proven in the actual target runtime.
- Rollback/restoration — how temporary cloud changes are undone.
- Stop conditions — evidence that would cause the plan to change.

## 14. Applicability rule

Do not overfit future agents to Work Radar.

- The architecture/diagnosis, evidence, security, restoration, user-presence, and path-of-least-resistance rules are broadly applicable.
- PAC and Copilot Studio component rules apply only when those tools/surfaces are selected.
- Semantic, priority, persistence, and reconciliation rules apply only when the future agent has those concerns.
- Work Radar's specific priority bands, field names, Calendar/Inbox/Teams sequence, and product behavior are examples, not universal AgentFactory requirements.

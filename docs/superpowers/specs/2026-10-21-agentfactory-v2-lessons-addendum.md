# AgentFactory V2 — Work Radar lessons addendum

Status: approved addition requested on 2026-10-21 before V2 implementation begins.

This addendum extends `2026-10-21-agentfactory-v2-design.md`. It does not replace the V2 architecture. Its purpose is to preserve the repeatable engineering lessons from Work Radar V1 without forcing Work Radar-specific product semantics onto future agents.

## Principle

AgentFactory must preserve this implementation order:

**Use → Configure → Integrate → Automate → Extend → Build.**

A custom extension is justified only by a demonstrated limitation of an earlier supported path, not by tooling inconvenience or an unqualified assumption.

AgentFactory is also **autonomy-first**: Codex is expected to perform as much of the work itself as the available supported tools allow. User effort is the final fallback, not the default integration mechanism.

## Requirements

- **LL-001 — Path of least resistance:** Before implementation, record the Microsoft-native capability considered, the simplest viable path, and the demonstrated reason earlier levels are insufficient.
- **LL-002 — Failure localization:** Before changing product architecture because something failed, classify the failing layer/tool surface. Platform, browser, authentication, environment, authoring UI, runtime, connector, and data failures must not be conflated.
- **LL-003 — Runtime qualification:** Distinguish `DESIGNED`, `IMPLEMENTED`, `CLOUD_SYNCHRONIZED`, and `RUNTIME_QUALIFIED`. Static/source validation cannot substitute for target-runtime evidence.
- **LL-004 — User-presence boundaries:** Classify operations as `SAFE_AUTOMATION`, `USER_PRESENCE_REQUIRED`, `ADMIN_REQUIRED`, or `ARCHITECTURE_DECISION_REQUIRED` where applicable, and stop cleanly at interactive/admin boundaries.
- **LL-005 — Cloud mutation evidence:** Material external CLI operations must capture output and explicit exit status. PAC cloud mutation uses fresh pre-push pull, bounded diff, push, post-push pull, and verification when PAC is the selected surface.
- **LL-006 — Component identity:** Do not invent Copilot Studio component identities unless a supported creation path explicitly permits it. Track cloud component identity/state/hash separately from filenames.
- **LL-007 — Temporary experiment restoration:** No temporary cloud experiment begins without known backup, original state, component identity, restoration hash/path, bounded blast radius, and a zero-write test path where feasible. Diagnostics default inactive/non-published.
- **LL-008 — Security contract:** Each project records allowed/forbidden data planes and connectors, identity model, publication boundary, and diagnostic redaction expectations as applicable. Tooling inconvenience is not a reason to weaken security.
- **LL-009 — Structured semantic boundaries:** When a deterministic downstream system depends on model-derived facts, use a typed structured contract and deterministic validation rather than parsing generated prose. Apply only when a generative-to-deterministic boundary exists.
- **LL-010 — Identity/idempotency first:** Persistent/reconciliation workflows prove stable identity and idempotency before adding intelligence; first-detection immutability is required when the product semantics need it.
- **LL-011 — Qualification fixtures:** Material behavioral/generative contracts define positive, negative, boundary, non-applicable, and repeatability fixtures as appropriate. Every capability specifies both `MUST` and `MUST NOT` behavior.
- **LL-012 — Evidence and freeze:** Evidence is a first-class artifact. Qualified critical components are inventoried/hashed when useful and treated as frozen until a later approved requirement justifies reopening them.
- **LL-013 — Tool-host fallbacks:** Known host/tool limitations become explicit workflow constraints with one bounded attempt and a proven fallback rather than repeated troubleshooting. Power Platform browser automation should not default to Chrome DevTools MCP or TinyFish based on Work Radar evidence unless new evidence supersedes that rule.
- **LL-014 — Stop/reassess/change path:** When new evidence disproves an assumption or reveals a simpler supported route, stop affected work, reassess, and change path. Continuing the obsolete plan is not required for procedural consistency.
- **LL-015 — Applicability/no overfitting:** Work Radar-specific priority bands, field names, data-source sequence, and product semantics are examples only. PAC, Copilot Studio, browser, semantic, persistence, and diagnostic rules apply only when those concerns exist in the selected architecture.
- **LL-016 — Autonomy-first execution ownership:** Codex owns execution by default. If repository edits, shell/CLI, PAC, MCP, SDK/API, browser automation, supported portal automation, or another available tool can safely perform an approved step, Codex should perform it rather than instructing the user to do it manually. Do not hand work to the user merely because another execution surface is inconvenient.
- **LL-017 — Fallback exhaustion before handoff:** If the preferred execution path fails, Codex must localize the failure and try the next-best safe supported path when one exists. The fallback search can include alternate CLI/PAC commands, MCP, SDK/API, repository/source operations, browser automation, another supported Microsoft authoring/testing surface, or a different supported implementation path. Handoff occurs only after reasonable supported automation paths are exhausted or a genuine `USER_PRESENCE_REQUIRED`, `ADMIN_REQUIRED`, security, destructive-action, or explicit-approval boundary is reached. Do not bypass MFA, consent, tenant governance, or other security controls in the name of autonomy.
- **LL-018 — Minimal copy/paste user handoff:** When user action is genuinely unavoidable, request only the smallest irreducibly human action. All instructions to the user must be placed in one consistent fenced copy/paste block, and that block must contain only the exact command(s) or UI action(s) the user should perform—no explanatory prose, alternatives, expected-output discussion, or unrelated steps. Context/explanation may be given outside the block, but instructions themselves must not be duplicated outside it.

## Active policy location

The operational rules derived from these requirements live in:

`.github/skills/m365-agent-factory/references/engineering-guardrails.md`

During the V2 skill-layout migration this file moves with the main skill to:

`.agents/skills/agentfactory/references/engineering-guardrails.md`

The main AgentFactory skill must load the guardrails before architecture selection, before cloud mutation, and before final qualification.

## Verification

The repository must retain an automated contract test proving that:

- the main AgentFactory skill references the guardrails;
- the core anti-regression rules remain present;
- autonomy-first execution and fallback exhaustion remain mandatory;
- unavoidable user handoffs use the minimal copy/paste instruction contract;
- the guardrails explicitly prevent Work Radar-specific details from becoming universal architecture defaults.

# AgentFactory V2 — Lessons Learned Implementation Addendum

> **For agentic workers:** Apply this addendum together with `docs/superpowers/plans/2026-10-21-agentfactory-v2-final.md`. It modifies existing task acceptance criteria; it does not create a separate product lane.

**Goal:** Make Work Radar V1 lessons and the approved autonomy-first execution policy enforceable in AgentFactory V2 so future builds do not repeat known architecture, PAC, browser, component-lifecycle, qualification, security, evidence, restoration, or unnecessary user-handoff failures.

**Spec:** `docs/superpowers/specs/2026-10-21-agentfactory-v2-lessons-addendum.md`

## Changes to the existing V2 plan

### Task 1 — Repair root guidance and establish V2 policy

Add to Task 1 acceptance:

- Root/current-policy docs reference the lessons-derived guardrail as a mandatory engineering input, without copying the entire historical file into `AGENTS.md`.
- Current docs state that runtime qualification is distinct from source/static validation.
- Current docs state that platform/tooling failure must be localized before architecture changes.
- Current docs state that Codex owns execution by default and the user is the final fallback, not the normal integration surface.
- Current docs state that user instructions, when unavoidable, use the standard copy/paste-only handoff format.

### Task 2 — Move custom skills to canonical `.agents/skills`

The skill migration must also move:

- `.github/skills/m365-agent-factory/references/engineering-guardrails.md`
  → `.agents/skills/agentfactory/references/engineering-guardrails.md`

Update `tests/test_lessons_guardrails.py` to the canonical `.agents/skills/agentfactory/...` paths in the same commit. Do not leave two authoritative copies.

### Task 3 — Machine-readable constraints

Do not hard-code all Work Radar lessons into `constraints.yaml`. Only stable organization-level constraints belong there.

Add or reserve machine-readable policy values only where they affect architecture globally, such as:

- Production/org publication approvals;
- forbidden/disallowed harnesses;
- approved data/security boundaries where organization-wide;
- autonomy-first execution ownership;
- user handoff only after fallback exhaustion;
- optional browser/tool-host defaults only if they remain valid in the target Codex environment.

Tool-host observations that might change with a new environment belong in capability/readiness evidence, not immutable constraints.

### Task 4 — V2 architecture routing

Extend architecture decision/template/tests with:

- native capability considered;
- simplest path level (`Use`, `Configure`, `Integrate`, `Automate`, `Extend`, `Build`);
- demonstrated reason earlier levels are insufficient;
- buildability;
- autonomous execution surfaces available to Codex;
- ordered fallback surfaces if the first path fails;
- user-presence/admin boundaries only after fallback exhaustion;
- runtime qualification plan;
- rollback/restoration plan when cloud mutation is expected;
- stop conditions that trigger reassessment.

Tests must prove that:

- an authoring/UI/tool-host failure alone does not authorize migration to a more complex architecture;
- a failed execution surface causes fallback to another supported surface rather than immediate user handoff;
- `USER_PRESENCE_REQUIRED` is reserved for intrinsically interactive/privileged boundaries or exhausted supported automation paths.

### Task 5 — Capability registry V2

Represent evidence dimensions so the registry can distinguish:

- documented/discovered;
- installed/available in the Codex host;
- authenticated;
- cloud synchronized;
- runtime qualified;
- blocked by tool host;
- blocked by user-presence/admin boundary.

For capabilities with multiple execution surfaces, record supported fallback surfaces so AgentFactory can move from one path to another without requiring the user to choose manually.

Seed relevant historical evidence from the Work Radar lessons as historical/observed evidence, not as permanent proof for the new Codex Cloud environment.

### Task 6 — Codex Cloud bootstrap/tooling

Bootstrap/readiness must not assume browser or PAC authentication behavior from another host.

Add readiness output for relevant tool-host states, including:

- PAC installed;
- PAC auth usable in this host vs alternate supported automation path vs genuine `USER_PRESENCE_REQUIRED`;
- browser automation available vs `TOOL_HOST_BLOCKED` if browser testing is selected;
- MCP/SDK/API alternatives where they can perform the same approved operation;
- explicit fallback recommendation rather than repeated repair loops or immediate user handoff.

Do not install Chrome DevTools MCP or TinyFish by default for Power Platform browser automation.

### Task 7 — Readiness and evidence model

Add a standard evidence/qualification model supporting at least:

- `DESIGNED`
- `IMPLEMENTED`
- `CLOUD_SYNCHRONIZED`
- `RUNTIME_QUALIFIED`
- `BLOCKED`
- `FAILED`
- `RESTORED` when a temporary experiment exists.

Readiness/evidence output must not treat `BLOCKED`, `FAILED`, and `NOT_TESTED` as interchangeable.

For blocked execution, readiness must capture:

- failed surface;
- reason;
- fallback surfaces attempted;
- remaining supported alternatives;
- whether a true user/admin boundary has been reached.

### Task 8 — Disposable declarative first build

The declarative first build does not need PAC/Copilot-Studio-specific mutation rules unless that build path actually selects those tools.

It must still demonstrate the universal lessons:

1. record path-of-least-resistance decision;
2. define security/publication boundary;
3. define MUST and MUST NOT fixtures;
4. distinguish implementation from runtime qualification;
5. preserve evidence;
6. execute autonomously through the best supported surface available;
7. if WIQD fails, try the next-best supported path such as Agents Toolkit when suitable before asking the user to perform implementation work;
8. hand off only an irreducibly human auth/consent/admin step, using the standard copy/paste block format.

### Task 9 — Whole-system acceptance

Whole-system verification must include `tests/test_lessons_guardrails.py` and confirm:

- the guardrail survived skill migration;
- the main AgentFactory skill loads/references it;
- the architecture template exposes qualification/restoration/stop-condition fields;
- the capability/readiness model distinguishes documented, synchronized, and runtime-qualified evidence;
- autonomy-first execution and fallback exhaustion are present as mandatory policy;
- the system does not ask the user to perform work another supported Codex-accessible surface can complete;
- unavoidable user instructions use one fenced copy/paste block containing only the exact actions;
- Work Radar-specific semantics are not universal defaults.

## Additional future-project artifacts

When a future project selects Copilot Studio/PAC or temporary cloud mutation, AgentFactory should generate project-local evidence artifacts rather than adding project state to the AgentFactory repository itself. Appropriate project-local artifacts include:

- component inventory (`logical_name`, ID, type, state, hash, qualification status);
- cloud-sync command evidence with explicit exit codes;
- execution-surface/fallback-attempt evidence;
- temporary experiment restoration record;
- frozen-component registry;
- runtime fixture matrix and repeatability evidence;
- security/data-plane contract.

These artifacts belong under the generated project's `.agent-factory/` state/evidence tree, not in the shared AgentFactory control-plane repository.

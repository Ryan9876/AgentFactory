# M365 Agent Factory V1 implementation plan

Source of truth: [the V1 specification](../../specs/m365-agent-factory-spec.md). This plan is executable without the originating conversation. It describes future work; none of the tasks below is implemented by the bootstrap commit. Preserve requirement IDs and update the specification first through approval if scope changes.

## Working rules

- Work in small commits. Do not start a build before explicit approval of the generated project specification and persisted SHA-256.
- Use Microsoft capabilities for platform operations. Verify the actual host, tools, commands, versions, and permissions before depending on them.
- Keep project control-plane records under `.agent-factory/`; platform artifacts stay in their Microsoft-owned locations/solutions.
- Use Python standard library for deterministic helpers. Write tests before helper implementation (TDD).
- Each implementation commit includes changed files, tests/commands, expected outcomes, and updated traceability where requirements are addressed.
- Never fabricate environment facts or lower approved requirements to pass tests.

## Task 1 — Repository and dependency baseline

**Files:** `README.md`, `.gitignore`, `docs/installation.md`, and any baseline project configuration discovered as necessary.

**Work:** Inspect repository history, status, available Python/test tooling, and skill-host documentation. Record decisions and versions; add only justified dependencies. Confirm `.github/skills/` discovery compatibility for the selected host. Protect credentials and local caches.

**Tests/verification:** `git status --short`; inspect tracked file list; run selected tool version commands; confirm no credentials are tracked. Expected: reproducible baseline and an explicit, evidence-backed host/dependency decision.

**Commit:** `chore: establish implementation baseline`.

## Task 2 — Agent Factory data and artifact contracts

**Files:** `templates/agent-spec.md`, `templates/architecture-decision.md`, `templates/build-manifest.md`, `templates/traceability.csv`, `templates/state.json`, `templates/acceptance-report.md`; contract tests in `tests/`.

**Interfaces:** State uses only the 14 V1 state names in the spec. Traceability uses the exact eight-column CSV contract. Manifest tasks include stable task ID, dependency IDs, requirement IDs, owning capability, status, and evidence. State records current state, project/target identifiers where verified, approved digest, manifest progress, timestamps, and blocker references without secrets.

**Tests:** Validate template parseability, required fields, allowed states, CSV header, and links among requirement/task/evidence records. Expected: templates are usable and contain no live tenant values.

**Commit:** `docs: define Agent Factory artifact contracts`.

## Task 3 — Deterministic specification hash helper

**Files:** `scripts/spec_hash.py`, `tests/test_helpers.py` (or focused module), CLI usage docs.

**Interface:** Accept optional project root; read `<root>/.agent-factory/spec.md` as bytes; print lowercase SHA-256 to stdout; clear diagnostic/nonzero exit for missing/unreadable file. No non-standard dependencies.

**Tests (write first):** Known fixture digest, changed-byte digest, stable output, missing file, explicit root. Expected: all tests pass and stdout contains only the digest on success.

**Verification:** Run focused test command and helper on a temporary fixture. Expected: output matches independently computed `sha256sum`/standard-library digest.

**Commit:** `feat: add approved spec hash helper`.

## Task 4 — Deterministic requirement traceability helper

**Files:** `scripts/traceability_check.py`, focused tests.

**Interface:** Accept spec path, CSV path, and final/release mode; parse mandatory `REQ-NNN` requirements and exact CSV header; provide actionable diagnostics and nonzero status on failure. Standard library only.

**Tests (write first):** Missing mandatory row; unknown ID; absent implementation artifact/evidence; absent verification ID/evidence only in release mode; complete rows; malformed/duplicate IDs; optional row behavior. Expected: fail cases fail deterministically, valid coverage succeeds.

**Verification:** Run focused suite and CLI fixtures. Expected: release mode enforces all implementation and verification evidence for every mandatory requirement.

**Commit:** `feat: validate requirement traceability`.

## Task 5 — `m365-agent-factory` intake and clarification

**Files:** `.github/skills/m365-agent-factory/SKILL.md`, `references/clarification-policy.md`, intake fixtures/tests.

**Interface:** Input objective plus available user/project context; output objective record separating facts, assumptions, unknowns, and consequential questions; grouped clarification prompt with safe defaults when appropriate. Do not draft architecture/spec until consequential unknowns are resolved or explicitly accepted as assumptions.

**Tests:** Ordinary objective; supplied context avoids repeat questions; only consequential ambiguity asks; grouped round and safe defaults; refund scenario does not invent integrations. Expected: deterministic reviewable intake records satisfy REQ-001, REQ-002, REQ-003, REQ-004, and REQ-005.

**Commit:** `feat: implement objective intake and clarification`.

## Task 6 — Architecture decision engine

**Files:** `.github/skills/m365-agent-factory/references/architecture-rules.md`, architecture logic/tests and decision template.

**Interface:** Resolved objective record → decisions for harness, knowledge, skills, tools/actions, flows, Dataverse/state, agents, external integrations, custom development; each decision includes rationale and evidence/dependency status.

**Tests:** Six golden scenarios as they become available; specifically knowledge-only avoids flow/data/child agent, approval uses flow and authoritative state, harness defaults Standard. Expected: no unsupported platform assumption is presented as verified.

**Commit:** `feat: add architecture decision workflow`.

## Task 7 — Specification generation contract

**Files:** `templates/agent-spec.md`, skill references, specification validation tests.

**Interface:** Objective/context + approved architecture → draft spec with applicable required sections, unique stable `REQ-NNN` IDs, assumptions/dependencies/blockers, acceptance criteria, thresholds and release gates. Approval is a separate explicit transition.

**Tests:** Required section presence, unique IDs, no missing unresolved-blocker accounting, no quality threshold invention. Expected: traceable draft reaches `AWAITING_APPROVAL`, never `APPROVED` by generation alone.

**Commit:** `feat: generate traceable agent specifications`.

## Task 8 — `power-platform-resilience`

**Files:** `.github/skills/power-platform-resilience/SKILL.md` and references for resilience, identity/permissions, side-effect safety; policy tests/examples.

**Interface:** Approved architecture/spec → review guidance for identity, least privilege, context, confirmation, retries and retry safety, idempotency, duplicates, partial failure, recovery, timeout, dependency/permission failure, errors, configuration, secrets, logging/correlation, observable DLP/policy, escalation.

**Tests:** Scenario coverage matrix and no secrets in generated artifacts. Expected: policy guidance is cross-cutting and does not claim to execute platform changes.

**Commit:** `feat: define Power Platform resilience guidance`.

## Task 9 — Capability registry and platform routing

**Files:** `.github/skills/m365-agent-factory/references/capability-registry.md`, `references/build-routing.md`, registry schema/data and checks if justified.

**Interface:** Registry entry records capability family, operation scope, provider, install/discovery path, compatibility evidence/date, prerequisites, limitations, and unavailable behavior. Router maps manifest task and requirement IDs to the smallest suitable Microsoft capability and passes focused context.

**Tests/verification:** Schema validation, unknown capability blocks clearly, conditional GHCP harness decision, route matrix for Copilot Studio/Power Automate/Dataverse/evaluation/ALM. Verify actual plugin/skill and CLI compatibility from primary documentation/tooling before marking available.

**Commit:** `feat: route builds through verified capabilities`.

## Task 10 — Build manifest, state, approval, and resume

**Files:** manifest/state modules, templates, skill workflow and tests.

**Interface:** Approved spec + hash + architecture → dependency-ordered tasks; transitions persist state/evidence. Before initial build/resume, recalculate hash; mismatch → `SPEC_CHANGED`, block until reapproval. Resume inspects platform artifacts and restarts at first incomplete component.

**Tests:** Invalid transition; approval stores digest; drift before build/resume; completed verified task reuse; interrupted task restart; no secret persistence. Expected: resume is idempotent and honest about uninspected artifacts.

**Commit:** `feat: persist build plan and resume interrupted work`.

## Task 11 — `agent-spec-verifier`

**Files:** `.github/skills/agent-spec-verifier/SKILL.md`, verification/traceability/verdict references, verification tests.

**Interface:** Approved spec/hash, artifacts, traceability, platform/eval evidence → ordered checks: integrity → coverage → platform → functional → evaluation → resilience → verdict. Allowed verdicts only `SHIP`, `ITERATE`, `BLOCK`; SHIP requires implementation and verification evidence for all mandatory requirements.

**Tests:** Each failed gate; missing mandatory evidence; drift; all-pass SHIP; unresolved blocker. Expected: verdict is evidence-based and ordered.

**Commit:** `feat: verify implementations against approved specs`.

## Task 12 — Remediation loop

**Files:** remediation routing module/skill references and tests.

**Interface:** Verification finding → smallest owning component, responsible platform capability, focused requirement context, affected retests, required release reruns. Requirement change proposal enters spec-change/reapproval path.

**Tests:** Correct owner routing; component retest plus required release suite; no requirement weakening. Expected: unresolved or unrouteable findings remain `BLOCK`.

**Commit:** `feat: route verification findings to remediation`.

## Task 13 — Golden scenario tests

**Files:** `tests/scenarios/*.md`, automated scenario harness/fixtures.

**Work:** Encode knowledge-only, IT ticketing, approval workflow, ambiguous refund objective, interrupted build, and spec drift from the specification. Assertions check decisions, no invented live facts, state transitions, requirement traceability, and verdict.

**Verification:** Run full local suite; report per-scenario outcomes. Expected: all approved scenario expectations pass without tenant access.

**Commit:** `test: cover V1 Agent Factory scenarios`.

## Task 14 — Real Development-environment pilot

**Files:** pilot run artifacts under a clearly excluded/local or approved project directory; sanitized pilot report under `docs/` only if safe and approved by repository policy.

**Work:** Verify approved environment, licensing, tool paths, access, DLP and admin constraints; run a low-risk representative agent through approval, build, evaluation, verification, and package. Use supported Microsoft tooling and record versions/evidence without credentials.

**Verification:** Confirm platform validation/evaluation evidence and acceptance report; production/publishing remains a separate approval boundary. Expected: pilot dependencies are proven rather than assumed.

**Commit:** `docs: record sanitized Development pilot evidence`.

## Task 15 — V1 acceptance and documentation

**Files:** README and `docs/` pages, capability registry, acceptance report template, final traceability evidence.

**Work:** Close mandatory REQs with evidence; verify clean installation/discovery instructions; document supported and conditional capabilities, limitations, manual deployment/admin approvals; ensure no credential material is committed.

**Verification:** Full local test/lint checks selected by baseline; release-mode traceability check; hash integrity check; platform/evaluation evidence review; `SHIP` only if every mandatory gate passes.

**Commit:** `chore: accept M365 Agent Factory v1`.

## Commit boundaries

Each numbered task ends in its own reviewable commit after the listed checks. Do not combine Microsoft environment setup with code tasks. Keep the real pilot and any Production/publication action behind their documented human approval boundaries.

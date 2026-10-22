# AgentFactory V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor AgentFactory into a Codex-first Microsoft 365 agent factory that selects the least-complex viable architecture, enforces the organization’s licensing/Work IQ constraints, uses Microsoft-supported tooling, and is ready for a disposable declarative-agent first build.

**Architecture:** Preserve V1’s approval, traceability, resume, resilience, and verification control plane. Replace the V1 “Standard Copilot Studio by default” rule with capability routing across declarative agents, Standard Copilot Studio, Power Automate/Dataverse, and an exception-only custom-engine path. Keep mutable Microsoft platform knowledge out of custom skills; use Microsoft Learn MCP/plugin plus current Microsoft CLIs, while machine-readable constraints and a V2 capability registry drive architecture and preflight.

**Tech Stack:** Python 3.9+, PyYAML 6.x, Bash, Node.js 24+, .NET 10+, Work IQ Dev Tools (`@microsoft/wiqd`), Microsoft 365 Agents Toolkit CLI (`@microsoft/m365agentstoolkit-cli`), Power Platform CLI (`Microsoft.PowerApps.CLI.Tool`), Codex skills/plugins/MCP.

**Spec:** `docs/superpowers/specs/2026-10-21-agentfactory-v2-design.md`

## Global Constraints

- Implementation preference: **Use → Configure → Integrate → Automate → Extend → Build.**
- Canonical project skills live in `.agents/skills/`.
- GitHub Copilot harness agents are disallowed because Copilot Credit funding is unavailable.
- Copilot Studio embedded Work IQ is disallowed while it requires the GitHub Copilot harness/Copilot Credits.
- Work IQ in Microsoft 365 Copilot and host-composed use with specialized agents are available patterns.
- Direct Work IQ MCP is optional/conditional and is not a first-build dependency.
- Declarative agents are preferred when suitable; Standard Copilot Studio remains allowed for structured/Power Platform-heavy scenarios.
- Custom-engine agents are exception-only.
- Development is the default target; Production mutation and organization-wide publication require explicit approval.
- Current Microsoft platform facts must be verified from first-party documentation/tool discovery.
- Never invent tenant IDs, environment IDs, schemas, credentials, URLs, connector operations, permissions, or verification results.

## Review Focus

- Knowledge-only internal agents must route to declarative/WIQD instead of silently retaining the V1 Standard-Copilot-Studio default; covered by Task 4 tests.
- A requirement that truly depends on GHCP must become `BLOCKED` or be redesigned; covered by Tasks 3-4.
- Direct Work IQ MCP must remain `CONDITIONAL` when billing/auth/tenant execution are unverified; host-composed Work IQ stays independently available; covered by Tasks 3 and 5.
- Documentation/tool discovery must never count as authentication or tenant execution evidence; covered by Task 5 registry tests.
- Cloud setup must fail clearly when Node <24 or .NET <10; covered by Task 6 bootstrap tests.

---

## Task 1: Repair root guidance and establish V2 as current policy

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/supported-platforms.md`
- Modify: `docs/workflow.md`
- Create: `tests/test_v2_policy.py`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-10-21-agentfactory-v2-design.md`
- Produces: concise repo-level instructions; detailed procedures remain in skills/config/docs.

- [ ] **Step 1: Write failing V2 policy tests**

Assert that:
- `AGENTS.md` contains no literal shell/heredoc construction;
- `AGENTS.md` points to the V2 design and `config/constraints.yaml`;
- Development is default; Production/org-wide publication require explicit approval;
- current architecture docs state “least-complex viable architecture” and do not declare Standard Copilot Studio as the universal default;
- supported-platform docs explicitly mark GHCP and Copilot-Studio-embedded Work IQ as disallowed.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_v2_policy -v`
Expected: FAIL against current malformed/stale V1 guidance.

- [ ] **Step 3: Replace root guidance and update current-facing docs**

Keep `docs/v1-acceptance.md` and V1 historical evidence intact.

- [ ] **Step 4: Verify**

Run: `python3 -m unittest tests.test_v2_policy -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `docs: make AgentFactory V2 the current policy`

---

## Task 2: Move custom skills to canonical Codex layout

**Files:**
- Replace symlink: `.agents/skills`
- Move: `.github/skills/m365-agent-factory/` → `.agents/skills/agentfactory/`
- Move: `.github/skills/agent-spec-verifier/` → `.agents/skills/agent-spec-verifier/`
- Move: `.github/skills/power-platform-resilience/` → `.agents/skills/power-platform-resilience/`
- Modify: moved skill references/relative paths
- Modify: tests that hard-code `.github/skills/...`
- Create: `tests/test_skill_layout.py`

**Interfaces:**
- Produces canonical skill IDs: `agentfactory`, `agent-spec-verifier`, `power-platform-resilience`.

- [ ] **Step 1: Write failing layout tests**

Assert:
- `.agents/skills` is a real directory, not a symlink;
- the three canonical skill folders exist and contain `SKILL.md`;
- main skill frontmatter name is `agentfactory`;
- no active tests/references point to `.github/skills/m365-agent-factory`.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_skill_layout -v`
Expected: FAIL on current symlink/V1 naming.

- [ ] **Step 3: Perform `git mv` migration and repair relative references**

Preserve history; do not keep duplicate custom skill sources in both locations.

- [ ] **Step 4: Update existing contract tests to canonical paths**

Do not weaken behavioral assertions.

- [ ] **Step 5: Verify**

Run: `python3 -m unittest discover -s tests -v`
Expected: no failures caused by stale skill paths.

- [ ] **Step 6: Commit**

Commit: `refactor: make .agents skills canonical`

---

## Task 3: Add machine-readable constraints

**Files:**
- Create: `requirements.txt`
- Create: `config/constraints.yaml`
- Create: `scripts/config_loader.py`
- Create: `tests/test_constraints_config.py`
- Modify: `.agents/skills/agentfactory/SKILL.md`

**Interfaces:**
- `load_yaml(path: pathlib.Path) -> dict[str, object]`
- `validate_constraints(data: dict[str, object]) -> list[str]`

- [ ] **Step 1: Add dependency and failing tests**

`requirements.txt` contains only `PyYAML>=6.0,<7`.

Tests pin these values:
- `organization.purpose: internal_m365_agents`
- `licensing.github_copilot_harness: disallowed`
- `licensing.usage_based_copilot_credits_for_agent_builds: unavailable`
- `work_iq.m365_copilot: available`
- `work_iq.host_composition_with_agents: available`
- `work_iq.copilot_studio_embedded: disallowed`
- `work_iq.direct_mcp_api: conditional`
- declarative preferred; Standard allowed; GHCP disallowed; custom engine exception-only;
- Production and organization publication require explicit approval.

Also test missing/malformed top-level sections return actionable validation errors.

- [ ] **Step 2: Verify failure**

Run: `python3 -m pip install -r requirements.txt && python3 -m unittest tests.test_constraints_config -v`
Expected: FAIL before config/loader implementation.

- [ ] **Step 3: Implement loader/validator and constraints YAML**

Use `yaml.safe_load`; reject non-mapping roots. Store no secrets or tenant IDs.

- [ ] **Step 4: Update `agentfactory` skill to read constraints before architecture selection**

Treat the file as hard architecture input, not advisory prose.

- [ ] **Step 5: Verify and commit**

Run: `python3 -m unittest tests.test_constraints_config tests.test_v2_policy -v`
Expected: PASS.

Commit: `feat: add AgentFactory architecture constraints`

---

## Task 4: Replace harness-first decisions with V2 routing

**Files:**
- Modify: `.agents/skills/agentfactory/references/architecture-rules.md`
- Modify: `templates/architecture-decision.md`
- Modify: `tests/test_architecture_contracts.py`
- Modify: `tests/fixtures/architecture/knowledge-only.json`
- Modify: `tests/fixtures/architecture/it-ticketing.json`
- Modify: `tests/fixtures/architecture/approval-workflow.json`
- Modify: `tests/fixtures/architecture/ambiguous-refund.json`
- Create: `tests/fixtures/architecture/ghcp-required.json`

**Interfaces:**
- Required architecture fields: `agent_type_runtime`, `authoring_tool`, `buildability`, `work_iq_mode`, plus knowledge/skills/tools/actions/Power Automate/Dataverse/additional agents/external integrations/custom development.
- `buildability`: `CLOUD_BUILDABLE`, `CLOUD_BUILDABLE_WITH_MANUAL_DEPLOY`, `PORTAL_STEP_REQUIRED`, `BLOCKED`.

- [ ] **Step 1: Rewrite architecture tests first**

Prove:
- knowledge-only internal M365 → declarative agent, WIQD primary, no Power Automate/Dataverse;
- approval workflow → Standard Copilot Studio + Power Automate;
- ambiguous refund → clarification required, no invented integration;
- GHCP-required → `BLOCKED` or explicit redesign;
- host-composed Work IQ is independent of direct Work IQ MCP;
- buildability is decided before specification.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_architecture_contracts -v`
Expected: FAIL on V1 default-harness assumptions.

- [ ] **Step 3: Update rules/template/fixtures**

Routing order: declarative → Standard/Power Platform when requirements justify it → custom engine only with a demonstrated requirement. Never select GHCP under current constraints.

- [ ] **Step 4: Verify**

Run: `python3 -m unittest tests.test_architecture_contracts tests.test_golden_scenarios -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `feat: route AgentFactory across supported agent types`

---

## Task 5: Replace V1 registry with multidimensional capability registry

**Files:**
- Create: `config/capability-registry.yaml`
- Modify: `.agents/skills/agentfactory/references/capability-registry.md`
- Modify: `.agents/skills/agentfactory/references/build-routing.md`
- Modify: `.agents/skills/agentfactory/references/capability-routes.csv`
- Remove after migration: `.agents/skills/agentfactory/references/capability-registry.json`
- Modify: `tests/test_capability_registry.py`

**Interfaces:**
- Reuse `load_yaml()`.
- Provider evidence fields: `microsoft_support_status`, `preview_status`, `organization_policy_status`, `licensing_status`, `codex_cloud_tool_status`, `authentication_status`, `tenant_execution_status`, `last_verified_at`, `evidence`, `limitations`, `fallback`.

- [ ] **Step 1: Rewrite registry tests first**

Require capabilities/providers for:
- Microsoft Learn MCP/plugin;
- declarative create/validate/package/provision via WIQD with Agents Toolkit fallback;
- Standard Copilot Studio author/manage/test via PAC;
- PAC MCP as optional interface, not auth evidence;
- Power Automate and Dataverse;
- agent evaluation;
- `workiq.retrieve` as preview + conditional licensing/auth/tenant execution;
- custom-engine path as exception-only;
- GHCP absent from allowed routes or explicitly policy-blocked.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_capability_registry -v`
Expected: FAIL against V1 JSON/two-status model.

- [ ] **Step 3: Build V2 YAML registry and update routing CSV/contract**

Use dated first-party URLs plus preserved V1 live evidence. A documentation hit may set Microsoft support status, but must not set authentication or tenant execution to PASS.

- [ ] **Step 4: Verify**

Run: `python3 -m unittest tests.test_capability_registry -v`
Expected: PASS.

- [ ] **Step 5: Full suite and commit**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

Commit: `feat: add multidimensional capability registry`

---

## Task 6: Add deterministic Codex Cloud bootstrap and first-party Microsoft docs plugin

**Files:**
- Create: `scripts/bootstrap_codex_cloud.sh`
- Create: `tests/test_bootstrap_contract.py`
- Modify: `docs/installation.md`

**Interfaces:**
- Exit nonzero with actionable text when Node major <24 or .NET major <10.
- Idempotent on repeat runs.

- [ ] **Step 1: Write failing bootstrap contract tests**

Assert the script:
- uses `set -euo pipefail`;
- installs `requirements.txt`;
- validates Node >=24 and .NET >=10 before Microsoft CLI installation;
- installs/updates `@microsoft/wiqd@latest` and `@microsoft/m365agentstoolkit-cli@latest`;
- installs/updates `Microsoft.PowerApps.CLI.Tool` and exposes `$HOME/.dotnet/tools`;
- verifies `wiqd --help`, `atk -h`, `pac help`;
- when `codex` is available, prefers the MicrosoftDocs Codex plugin path: `codex plugin marketplace add MicrosoftDocs/mcp`, then installs `microsoft-docs@microsoftdocs-local` if not already installed;
- verifies `codex mcp list` contains the Microsoft Learn endpoint from the plugin; if plugin installation is unavailable on the active Codex surface, falls back to `codex mcp add microsoft-learn --url https://learn.microsoft.com/api/mcp`;
- does not configure Work IQ MCP by default;
- does not run interactive M365 authentication during bootstrap.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_bootstrap_contract -v`
Expected: FAIL before script exists.

- [ ] **Step 3: Implement bootstrap script**

Use current first-party install surfaces. Do not install GitHub Copilot CLI or GHCP tooling.

- [ ] **Step 4: Verify shell and tests**

Run: `python3 -m unittest tests.test_bootstrap_contract -v`
Run: `bash -n scripts/bootstrap_codex_cloud.sh`
Expected: PASS.

- [ ] **Step 5: Document auth boundary and commit**

Document that M365/PAC/WIQD authentication is separate from bootstrap and credentials are never committed.

Commit: `feat: bootstrap AgentFactory Codex cloud tooling`

---

## Task 7: Add first-build readiness checker

**Files:**
- Create: `scripts/readiness_check.py`
- Create: `tests/test_readiness_check.py`
- Modify: `docs/installation.md`

**Interfaces:**
- `run_checks(command_runner=...) -> list[CheckResult]`
- `CheckResult`: `name`, `status`, `detail`, `required`
- Status: `PASS`, `FAIL`, `CONDITIONAL`, `BLOCKED`
- CLI supports `--json`.

- [ ] **Step 1: Write failing unit tests with a fake command runner**

Cover:
- repository/skill layout;
- Python dependency import;
- Node 24+ and .NET 10+;
- `wiqd`, `atk`, `pac` help;
- Microsoft Learn plugin/MCP presence when Codex CLI exists;
- M365/Development auth as a required live preflight, not guessed from installation;
- Work IQ MCP may be `CONDITIONAL`/`BLOCKED` without blocking the first declarative build;
- unsupported runtime versions produce clear required failures.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_readiness_check -v`
Expected: FAIL before implementation.

- [ ] **Step 3: Implement checker**

No tenant mutations. Read-only checks may report a required failure with the exact next step.

- [ ] **Step 4: Verify**

Run: `python3 -m unittest tests.test_readiness_check -v`
Run: `python3 scripts/readiness_check.py --json`
Expected: unit tests PASS; local output reports actual host state honestly.

- [ ] **Step 5: Commit**

Commit: `feat: add first-build readiness checks`

---

## Task 8: Define disposable first-build golden path

**Files:**
- Create: `tests/fixtures/first-build/objective.md`
- Create: `tests/fixtures/first-build/expected-architecture.json`
- Create: `docs/first-build.md`
- Modify: `tests/test_golden_scenarios.py`

**Interfaces:**
- First build: low-risk internal declarative knowledge agent for Microsoft 365 Copilot; no external mutation, Dataverse, Power Automate, GHCP, embedded Work IQ, or direct Work IQ MCP dependency.
- Primary authoring route: WIQD. Fallback: Agents Toolkit when WIQD provisioning prerequisites (including Azure subscription/access) are unavailable and the fallback still satisfies the approved objective.

- [ ] **Step 1: Add failing first-build routing test**

Assert declarative/WIQD primary, ATK fallback, direct Work IQ MCP `not_required`, and GHCP `disallowed`.

- [ ] **Step 2: Verify failure**

Run: `python3 -m unittest tests.test_golden_scenarios -v`
Expected: FAIL until fixture exists.

- [ ] **Step 3: Add fixture and operator runbook**

`docs/first-build.md` separates:
1. offline readiness;
2. live M365/Development authentication;
3. WIQD prerequisite check (`wiqd doctor`) and Azure-access decision;
4. WIQD or ATK route selection;
5. disposable agent creation;
6. static/deep validation;
7. Development-only provision/sideload;
8. functional test in Microsoft 365 Copilot;
9. cleanup/retention decision;
10. no organization-wide share/publish without explicit approval.

- [ ] **Step 4: Verify and commit**

Run: `python3 -m unittest tests.test_golden_scenarios -v`
Expected: PASS.

Commit: `docs: define AgentFactory V2 first build`

---

## Task 9: Final verification and Codex Cloud handoff

**Files:**
- Modify only if verification reveals defects.

**Interfaces:**
- Produces repo ready for a fresh Codex Cloud environment named `AgentFactory`.

- [ ] **Step 1: Full test suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 2: Integrity checks**

Run: `python3 scripts/traceability_check.py --spec docs/specs/m365-agent-factory-spec.md --traceability docs/acceptance-traceability.csv --release`
Expected: historical V1 acceptance remains valid; V2 implementation does not silently rewrite V1 evidence.

Run: `python3 -m compileall scripts tests`
Expected: PASS.

Run: `git diff --check`
Expected: PASS.

- [ ] **Step 3: V2 readiness output**

Run: `python3 scripts/readiness_check.py --json`
Expected: accurate local status; unperformed tenant/auth checks remain explicit.

- [ ] **Step 4: Whole-branch review**

Review for accidental GHCP routing, hidden Work IQ billing dependency, stale `.github/skills` references, invented tenant claims, unsupported Microsoft command assumptions, and V1-history corruption.

- [ ] **Step 5: Codex Cloud handoff**

After merge/branch selection:
1. Create fresh Codex Cloud environment `AgentFactory` with `Ryan9876/AgentFactory` as its only default repo.
2. Use `scripts/bootstrap_codex_cloud.sh` as setup/bootstrap.
3. Run `python3 scripts/readiness_check.py --json` inside the environment.
4. Complete supported Microsoft account authentication outside repository secrets.
5. Re-run readiness until required checks pass.
6. Execute `docs/first-build.md` and capture evidence before using the Factory for a real organizational agent.

Final commit if review fixes are needed: `chore: finalize AgentFactory V2 readiness`

# AgentFactory V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor AgentFactory into a Codex-first Microsoft 365 agent factory that selects the least-complex viable architecture, enforces the organization’s licensing/Work IQ constraints, uses first-party Microsoft tooling, and is ready for a disposable declarative-agent first build.

**Architecture:** Preserve V1’s approval, traceability, resume, resilience, and verification control plane, but move architecture selection from “Standard Copilot Studio by default” to capability routing across declarative agents, Standard Copilot Studio, Power Automate/Dataverse, and an exception-only custom-engine path. Keep mutable Microsoft knowledge/tool syntax outside custom skills; use Microsoft Learn MCP and current Microsoft CLIs, while machine-readable constraints and a V2 capability registry drive routing and preflight.

**Tech Stack:** Python 3.9+, PyYAML 6.x, Bash, Node.js 24+, .NET 10+, Work IQ Dev Tools (`@microsoft/wiqd`), Microsoft 365 Agents Toolkit CLI (`@microsoft/m365agentstoolkit-cli`), Power Platform CLI (`Microsoft.PowerApps.CLI.Tool`), Codex skills/MCP configuration.

**Spec:** `docs/superpowers/specs/2026-10-21-agentfactory-v2-design.md`

## Global Constraints

- Implementation preference order: **Use → Configure → Integrate → Automate → Extend → Build.**
- Repository target host: Codex; canonical project skills live under `.agents/skills/`.
- GitHub Copilot harness agents are disallowed because Copilot Credit funding is unavailable.
- Copilot Studio embedded Work IQ is disallowed while it requires the GitHub Copilot harness/Copilot Credits.
- Work IQ in Microsoft 365 Copilot and host-composed use with specialized agents are available patterns.
- Direct Work IQ MCP is optional/conditional and must not be required for the first build.
- Declarative agents are preferred when they satisfy the objective; Standard Copilot Studio is allowed for structured/Power Platform-heavy scenarios.
- Custom-engine agents are exception-only.
- Development is the default target; Production mutation and organization-wide publication require explicit approval.
- Current Microsoft platform facts must be verified against first-party documentation/tool discovery rather than copied into long-lived custom skills.
- Never invent tenant IDs, environment IDs, schemas, credentials, URLs, connector operations, permissions, or verification results.

## Review Focus

- A knowledge-only internal agent must route to a declarative agent instead of silently preserving the V1 Standard-Copilot-Studio default; covered in Task 4 routing tests.
- Any request that materially requires the GitHub Copilot harness must become `BLOCKED` or be redesigned, never routed to a credit-dependent path; covered in Tasks 3 and 4.
- Direct Work IQ MCP must remain `CONDITIONAL` when billing/auth/tenant execution are unverified, while host-composed Work IQ remains usable; covered in Tasks 3 and 5.
- Tool discovery/documentation must not be promoted to proof of authentication or successful tenant execution; covered in Task 5 registry-schema tests.
- Cloud setup must fail clearly when Node <24 or .NET <10 rather than partially installing an unusable toolchain; covered in Task 6 bootstrap tests.

---

## File Structure

### Canonical custom skills

- `.agents/skills/agentfactory/` — objective intake, constraints, architecture selection, specification/approval lifecycle, capability routing, build/resume orchestration.
- `.agents/skills/agent-spec-verifier/` — verification/evidence/remediation verdict logic.
- `.agents/skills/power-platform-resilience/` — security, side effects, recovery, permissions, observability, DLP review.

### Machine-readable policy

- `config/constraints.yaml` — organization/licensing/Work IQ/deployment architecture constraints.
- `config/capability-registry.yaml` — V2 capability/provider evidence with independent support/licensing/auth/tenant-execution dimensions.
- `scripts/config_loader.py` — safe YAML loading and required-field validation.
- `scripts/readiness_check.py` — local/cloud first-build readiness checks with machine-readable output.

### Cloud bootstrap

- `scripts/bootstrap_codex_cloud.sh` — validates runtime floors; installs repo Python deps, WIQD, Agents Toolkit, PAC CLI; configures Microsoft Learn MCP where Codex CLI is available.
- `requirements.txt` — `PyYAML>=6.0,<7` only.

### Updated contracts/tests

- `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/supported-platforms.md`, `docs/workflow.md` — V2 policy/current-state docs.
- `templates/architecture-decision.md` — runtime, authoring tool, buildability, Work IQ mode, dependencies/evidence.
- `tests/test_v2_policy.py`, `tests/test_skill_layout.py`, `tests/test_constraints_config.py`, `tests/test_readiness_check.py` — new V2 contracts.
- Existing architecture, registry, golden-scenario, intake, build-state, verifier, resilience and traceability tests are updated rather than replaced.

---

### Task 1: Repair root guidance and make V2 the current architecture

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/supported-platforms.md`
- Modify: `docs/workflow.md`
- Create: `tests/test_v2_policy.py`

**Interfaces:**
- Consumes: approved V2 design at `docs/superpowers/specs/2026-10-21-agentfactory-v2-design.md`.
- Produces: concise repository-level policy; deeper procedures remain in skills/config/docs.

- [ ] **Step 1: Write failing policy tests**

Create `tests/test_v2_policy.py` with assertions that:
- `AGENTS.md` contains no `cat > AGENTS.md`, heredoc marker, or shell-construction wrapper;
- `AGENTS.md` references the V2 design, `config/constraints.yaml`, and current first-party Microsoft documentation;
- root guidance states Development by default and explicit approval for Production/org-wide publication;
- current architecture docs state “least-complex viable architecture” and do not state that Standard Copilot Studio is the universal/default harness;
- supported-platform docs explicitly mark GitHub Copilot harness and Copilot-Studio-embedded Work IQ as disallowed under current constraints.

- [ ] **Step 2: Run the policy tests and verify failure**

Run: `python3 -m unittest tests.test_v2_policy -v`
Expected: FAIL against the current malformed/stale V1 guidance.

- [ ] **Step 3: Replace `AGENTS.md` with concise V2 guidance and update current docs**

Keep V1 acceptance/history documents intact. Update current-facing docs only; link to V1 acceptance rather than rewriting historical evidence.

- [ ] **Step 4: Run policy tests**

Run: `python3 -m unittest tests.test_v2_policy -v`
Expected: PASS.

- [ ] **Step 5: Run full tests and commit**

Run: `python3 -m unittest discover -s tests -v`
Expected: existing failures are allowed only where later V2 tasks intentionally update stale V1 path/routing assertions; record them before commit.

Commit: `docs: make AgentFactory V2 the current policy`

---

### Task 2: Move custom skills to the canonical Codex layout

**Files:**
- Remove symlink: `.agents/skills`
- Move: `.github/skills/m365-agent-factory/` → `.agents/skills/agentfactory/`
- Move: `.github/skills/agent-spec-verifier/` → `.agents/skills/agent-spec-verifier/`
- Move: `.github/skills/power-platform-resilience/` → `.agents/skills/power-platform-resilience/`
- Modify: `.agents/skills/agentfactory/SKILL.md`
- Modify: all moved references containing old relative paths or old skill name
- Modify: tests with `.github/skills/...` constants
- Create: `tests/test_skill_layout.py`

**Interfaces:**
- Produces canonical skill IDs: `agentfactory`, `agent-spec-verifier`, `power-platform-resilience`.
- Later tasks must reference `.agents/skills/agentfactory/references/...` only.

- [ ] **Step 1: Write failing layout tests**

Assertions:
- `.agents/skills` is a real directory, not a symlink;
- exactly the three custom V2 skill folders above contain `SKILL.md`;
- the main skill frontmatter name is `agentfactory`;
- no tracked test/reference path points to `.github/skills/m365-agent-factory`;
- `.github/skills` no longer owns the custom skill sources.

- [ ] **Step 2: Run layout tests and verify failure**

Run: `python3 -m unittest tests.test_skill_layout -v`
Expected: FAIL because `.agents/skills` is currently a symlink and the main skill is V1-named.

- [ ] **Step 3: Perform git moves and repair relative references**

Use `git mv` so history is retained. Do not duplicate the custom skills in both locations.

- [ ] **Step 4: Update existing tests to canonical paths without weakening their behavioral assertions**

At minimum update architecture, capability-registry, intake, resilience, specification, golden-scenario and acceptance-readiness path constants as required.

- [ ] **Step 5: Run all skill/layout/contract tests**

Run: `python3 -m unittest discover -s tests -v`
Expected: no failures caused by old skill paths/names.

- [ ] **Step 6: Commit**

Commit: `refactor: make .agents skills canonical`

---

### Task 3: Add machine-readable organizational constraints

**Files:**
- Create: `requirements.txt`
- Create: `config/constraints.yaml`
- Create: `scripts/config_loader.py`
- Create: `tests/test_constraints_config.py`
- Modify: `.agents/skills/agentfactory/SKILL.md`

**Interfaces:**
- `load_yaml(path: pathlib.Path) -> dict[str, object]`
- `validate_constraints(data: dict[str, object]) -> list[str]` returns zero errors for valid config; each string is a user-actionable schema/policy error.

- [ ] **Step 1: Add dependency and failing schema tests**

`requirements.txt` contains only `PyYAML>=6.0,<7`.

Tests assert exact required values:
- `organization.purpose == "internal_m365_agents"`
- `licensing.github_copilot_harness == "disallowed"`
- `licensing.usage_based_copilot_credits_for_agent_builds == "unavailable"`
- `work_iq.m365_copilot == "available"`
- `work_iq.host_composition_with_agents == "available"`
- `work_iq.copilot_studio_embedded == "disallowed"`
- `work_iq.direct_mcp_api == "conditional"`
- declarative agent preferred, Standard allowed, GHCP disallowed, custom engine exception-only;
- Production and organization publication require explicit approval.

Also test malformed/missing top-level sections return validation errors.

- [ ] **Step 2: Install test dependency and confirm failing tests**

Run: `python3 -m pip install -r requirements.txt && python3 -m unittest tests.test_constraints_config -v`
Expected: FAIL because config/loader do not exist.

- [ ] **Step 3: Implement YAML loader, validator, and `config/constraints.yaml`**

Use `yaml.safe_load`; reject a non-mapping root. Keep secrets/tenant identifiers out of this file.

- [ ] **Step 4: Make `agentfactory` load/apply constraints before architecture selection**

Skill guidance must treat these values as hard architecture inputs, not advisory prose.

- [ ] **Step 5: Run tests and commit**

Run: `python3 -m unittest tests.test_constraints_config tests.test_v2_policy -v`
Expected: PASS.

Commit: `feat: add AgentFactory architecture constraints`

---

### Task 4: Replace harness-first architecture decisions with V2 routing

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
- Architecture decision fields must include: `agent_type_runtime`, `authoring_tool`, `buildability`, `work_iq_mode`, plus existing knowledge/skills/tools/actions/Power Automate/Dataverse/additional-agents/external-integration/custom-development decisions.
- `buildability` allowed values: `CLOUD_BUILDABLE`, `CLOUD_BUILDABLE_WITH_MANUAL_DEPLOY`, `PORTAL_STEP_REQUIRED`, `BLOCKED`.

- [ ] **Step 1: Rewrite architecture contract tests first**

Tests must prove:
- knowledge-only internal M365 scenario → declarative agent, WIQD primary, no Power Automate/Dataverse;
- approval workflow → Standard Copilot Studio + Power Automate, with authoritative state owner unresolved unless supplied;
- ambiguous refund → clarification required, no invented integration;
- GHCP-required fixture → `BLOCKED` or explicit redesign because the constraint is disallowed;
- host-composed Work IQ can be selected independently of direct Work IQ MCP;
- architecture precedes specification and records buildability.

- [ ] **Step 2: Run architecture tests and verify failure**

Run: `python3 -m unittest tests.test_architecture_contracts -v`
Expected: FAIL on V1 harness/default assumptions.

- [ ] **Step 3: Update architecture rules/template/fixtures to V2**

Routing priority: declarative → Standard Copilot Studio/Power Platform when needed → custom engine only with a demonstrated requirement. Never route to GHCP under current constraints.

- [ ] **Step 4: Run architecture and golden-scenario tests**

Run: `python3 -m unittest tests.test_architecture_contracts tests.test_golden_scenarios -v`
Expected: PASS after any V1 golden expectations are updated to the approved V2 design rather than weakened.

- [ ] **Step 5: Commit**

Commit: `feat: route AgentFactory across supported agent types`

---

### Task 5: Replace the stale registry with capability registry V2

**Files:**
- Create: `config/capability-registry.yaml`
- Modify: `.agents/skills/agentfactory/references/capability-registry.md`
- Modify: `.agents/skills/agentfactory/references/build-routing.md`
- Modify: `.agents/skills/agentfactory/references/capability-routes.csv`
- Remove after migration: `.agents/skills/agentfactory/references/capability-registry.json`
- Modify: `tests/test_capability_registry.py`

**Interfaces:**
- Reuse `load_yaml()` from `scripts/config_loader.py`.
- Every provider record includes: `microsoft_support_status`, `preview_status`, `organization_policy_status`, `licensing_status`, `codex_cloud_tool_status`, `authentication_status`, `tenant_execution_status`, `last_verified_at`, `evidence`, `limitations`, `fallback`.

- [ ] **Step 1: Replace registry tests before registry data**

Tests must assert independent evidence dimensions and known capabilities for:
- Microsoft Learn MCP/current docs;
- declarative agent create/validate/package/provision via WIQD, with Agents Toolkit fallback;
- Standard Copilot Studio author/manage/test via PAC;
- PAC MCP as an optional interface, not proof of tenant auth;
- Power Automate and Dataverse capabilities;
- supported evaluation path(s);
- `workiq.retrieve` as preview + conditional licensing/auth/tenant execution;
- custom-engine build path as exception-only;
- GHCP route absent from allowed providers or explicitly policy-blocked.

- [ ] **Step 2: Run registry tests and verify failure**

Run: `python3 -m unittest tests.test_capability_registry -v`
Expected: FAIL against V1 JSON/status model.

- [ ] **Step 3: Create V2 YAML registry and update routing contract/CSV**

Seed evidence with dated first-party references and existing V1 live evidence. Preserve the distinction between “documented/discovered” and “tenant-executed”.

- [ ] **Step 4: Run registry/routing tests**

Run: `python3 -m unittest tests.test_capability_registry -v`
Expected: PASS.

- [ ] **Step 5: Run full tests and commit**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

Commit: `feat: add multidimensional capability registry`

---

### Task 6: Add deterministic Codex Cloud bootstrap and Microsoft Learn integration

**Files:**
- Create: `scripts/bootstrap_codex_cloud.sh`
- Create: `tests/test_bootstrap_contract.py`
- Modify: `docs/installation.md`

**Interfaces:**
- Script exits nonzero with actionable text if Node major <24 or .NET major <10.
- Script is idempotent: existing current tools are verified/updated, not treated as an error.

- [ ] **Step 1: Write static bootstrap contract tests**

Tests assert the script:
- uses `set -euo pipefail`;
- installs `requirements.txt`;
- verifies Node >=24 and .NET >=10 before Microsoft CLI installation;
- installs/updates `@microsoft/wiqd` and `@microsoft/m365agentstoolkit-cli` with npm;
- installs/updates `Microsoft.PowerApps.CLI.Tool` with `dotnet tool` and ensures `$HOME/.dotnet/tools` is usable;
- verifies `wiqd --help`, `atk -h`, and `pac help`;
- when `codex` is present, runs `codex mcp add microsoft-learn --url https://learn.microsoft.com/api/mcp` only when not already configured, then verifies with `codex mcp list`;
- does not configure Work IQ MCP by default;
- does not run interactive Microsoft 365 authentication during bootstrap.

- [ ] **Step 2: Run test and verify failure**

Run: `python3 -m unittest tests.test_bootstrap_contract -v`
Expected: FAIL because script does not exist.

- [ ] **Step 3: Implement the bootstrap script**

Use current Microsoft-supported package/install commands:
- `npm install -g @microsoft/wiqd@latest @microsoft/m365agentstoolkit-cli@latest`
- `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` when absent; `dotnet tool update --global Microsoft.PowerApps.CLI.Tool` when present.
- Microsoft Learn MCP endpoint: `https://learn.microsoft.com/api/mcp`.

Do not install GitHub Copilot CLI or any GHCP harness dependency.

- [ ] **Step 4: Run bootstrap contract and shell syntax checks**

Run: `python3 -m unittest tests.test_bootstrap_contract -v`
Run: `bash -n scripts/bootstrap_codex_cloud.sh`
Expected: PASS.

- [ ] **Step 5: Document environment setup and commit**

Document that Microsoft authentication is a separate post-bootstrap preflight because credentials must not be stored in the repo/setup script.

Commit: `feat: bootstrap AgentFactory Codex cloud tooling`

---

### Task 7: Add first-build readiness checker

**Files:**
- Create: `scripts/readiness_check.py`
- Create: `tests/test_readiness_check.py`
- Modify: `docs/installation.md`

**Interfaces:**
- `run_checks(command_runner=...) -> list[CheckResult]`
- `CheckResult` fields: `name`, `status`, `detail`, `required`; status is `PASS`, `FAIL`, `CONDITIONAL`, or `BLOCKED`.
- CLI supports `--json`; exit 0 only when every required check is `PASS` and optional Work IQ is `PASS`, `CONDITIONAL`, or `BLOCKED` with a recorded reason.

- [ ] **Step 1: Write failing unit tests with a fake command runner**

Cover:
- correct repo/branch and skill layout;
- Python dependency import;
- Node 24+;
- .NET 10+;
- `wiqd`, `atk`, `pac` help surfaces;
- Microsoft Learn MCP present in `codex mcp list` when Codex CLI is available;
- Development/M365 authentication is required but may be a distinct manual-preflight failure;
- Work IQ MCP never blocks first-build readiness solely because it is conditional/unconfigured;
- unsupported runtime versions produce clear required failures.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_readiness_check -v`
Expected: FAIL because checker does not exist.

- [ ] **Step 3: Implement readiness checker**

Do not mutate tenant state. Authentication/environment checks must be read-only and may report `FAIL`/`BLOCKED` with the exact next step instead of guessing.

- [ ] **Step 4: Run unit tests and local dry check**

Run: `python3 -m unittest tests.test_readiness_check -v`
Run: `python3 scripts/readiness_check.py --json`
Expected: unit tests PASS; local result accurately reports the current host rather than being forced to green.

- [ ] **Step 5: Commit**

Commit: `feat: add first-build readiness checks`

---

### Task 8: Define and validate the disposable first-build path

**Files:**
- Create: `tests/fixtures/first-build/objective.md`
- Create: `tests/fixtures/first-build/expected-architecture.json`
- Create: `docs/first-build.md`
- Modify: `tests/test_golden_scenarios.py`

**Interfaces:**
- First-build objective: a low-risk internal declarative knowledge agent for Microsoft 365 Copilot, no external mutation, no Dataverse, no Power Automate, no GHCP, no embedded Work IQ.
- Expected build path: declarative agent → WIQD primary → Agents Toolkit fallback → `CLOUD_BUILDABLE` or `CLOUD_BUILDABLE_WITH_MANUAL_DEPLOY` based on live tenant/auth checks.

- [ ] **Step 1: Add failing first-build routing test**

Test asserts the fixture routes to declarative/WIQD and explicitly marks direct Work IQ MCP `not_required` for the first build.

- [ ] **Step 2: Run golden tests and verify failure**

Run: `python3 -m unittest tests.test_golden_scenarios -v`
Expected: FAIL until first-build fixture/expectation exists.

- [ ] **Step 3: Add first-build fixture and operator runbook**

`docs/first-build.md` must separate:
1. offline readiness;
2. Microsoft 365/Development authentication;
3. `wiqd doctor`;
4. disposable agent creation;
5. static/deep validation;
6. provision only to the approved Development target;
7. functional test in Microsoft 365 Copilot;
8. cleanup or retention decision;
9. no organization-wide share/publish without explicit approval.

- [ ] **Step 4: Run golden tests**

Run: `python3 -m unittest tests.test_golden_scenarios -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `docs: define AgentFactory V2 first build`

---

### Task 9: Final verification and cloud-environment handoff

**Files:**
- Modify only if verification exposes defects.

**Interfaces:**
- Produces a clean V2 repo ready to connect to a fresh Codex Cloud environment named `AgentFactory`.

- [ ] **Step 1: Run the complete repository test suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all tests PASS.

- [ ] **Step 2: Run deterministic integrity checks**

Run: `python3 scripts/traceability_check.py --spec docs/specs/m365-agent-factory-spec.md --traceability docs/acceptance-traceability.csv --release`
Expected: preserve the historical V1 acceptance result; V2 changes must not silently rewrite V1 evidence.

Run: `python3 -m compileall scripts tests`
Expected: PASS.

Run: `git diff --check`
Expected: no whitespace errors.

- [ ] **Step 3: Run V2 readiness output**

Run: `python3 scripts/readiness_check.py --json`
Expected: repo/tool checks reflect the implementation host honestly. Any authentication/tenant check not executable here remains explicit rather than fabricated.

- [ ] **Step 4: Whole-branch review**

Review specifically for: accidental GHCP routing, hidden Work IQ billing dependency, stale `.github/skills` references, invented tenant claims, and V1-history corruption.

- [ ] **Step 5: Commit any review fixes and prepare the Codex Cloud setup handoff**

Final commit if needed: `chore: finalize AgentFactory V2 readiness`

Handoff sequence after merge/branch selection:
1. Create a fresh Codex Cloud environment named `AgentFactory` pointing only to `Ryan9876/AgentFactory`.
2. Run `scripts/bootstrap_codex_cloud.sh` as the environment setup/bootstrap step.
3. Start a task and run `python3 scripts/readiness_check.py --json`.
4. Complete Microsoft 365/PAC/WIQD authentication using supported interactive/account mechanisms outside repository secrets.
5. Re-run readiness until the required first-build checks pass.
6. Execute `docs/first-build.md` and collect evidence before using AgentFactory on a real organizational agent.

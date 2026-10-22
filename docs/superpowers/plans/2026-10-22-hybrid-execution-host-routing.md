# Hybrid Execution Host Routing Implementation Plan

> **For agentic workers:** This work follows the approved user brief inline. Keep changes on this feature branch until the user chooses integration.

**Goal:** Encode capability-specific Cloud, Desktop Local, browser identity, fallback, human-presence, and blocker routing; add a non-secret local readiness report.

**Architecture:** Extend `config/capability-registry.yaml` with execution routing keyed to registered capability IDs. Add a distinct, read-only local readiness command while preserving the Cloud bootstrap/readiness path. Update existing architecture, workflow, installation, platform, and skill guidance.

**Tech Stack:** YAML; Python standard library; existing unittest suite; shell/git.

**Spec:** User implementation brief; AgentFactory V2 design and Work Radar lessons addendum.

## Global Constraints

- Development is the default; no tenant mutations.
- No authentication material or absolute local user/profile path in portable configuration or fixtures.
- Preserve evidence-state distinctions; tool discovery is not runtime qualification.
- Tenant/policy blockers and human/admin boundaries stop host hopping.
- PAC authentication precedes PAC MCP startup; fresh Copilot Studio MCP verifies account, environment, and live catalog.
- AgentFactory Chrome is persistent identity only; Chrome for Testing with a disposable profile handles deterministic regression.

## Review Focus

- Public documentation may run on either host; tenant operations prefer Desktop Local.
- Tenant/policy blockers stop instead of triggering a host fallback.
- User-presence requirements stop automation without bypassing authentication or consent.
- Runtime qualification remains distinct from installed tools and schema discovery.
- Portable configuration identifies the visible profile name, never a user-specific directory path.

---

### Task 1: Capability-based host and browser routing

**Files:** Modify `config/capability-registry.yaml`, `.agents/skills/agentfactory/references/capability-registry.md`, `.agents/skills/agentfactory/references/build-routing.md`, `tests/test_capability_registry.py`; add `tests/test_host_routing.py`.

- [ ] Add failing tests for Cloud engineering, Local tenant operations, EITHER public documentation, blocker/human stops, browser role separation, PAC ordering, runtime-vs-discovery, and portable profile metadata.
- [ ] Verify RED, then add registry data and concise guidance without a second routing subsystem.
- [ ] Run focused tests to GREEN.

### Task 2: Separate local readiness activation

**Files:** Add `scripts/local_readiness_check.py`, `tests/test_local_readiness.py`; preserve `scripts/bootstrap_codex_cloud.sh` and `scripts/readiness_check.py`.

- [ ] Test an injectable local, non-secret readiness report with stubbed command execution and profile metadata.
- [ ] Verify RED, then implement platform/tool/MCP/profile/auth/environment/blocker checks using supported read-only status commands and environment inputs. Never infer sign-in from installation.
- [ ] Verify GREEN and output that omits profile paths and credential-like material.

### Task 3: Routing and operating documentation

**Files:** Modify `docs/architecture.md`, `docs/installation.md`, `docs/workflow.md`, `docs/supported-platforms.md`, `.agents/skills/agentfactory/references/engineering-guardrails.md` and justified acceptance/readiness docs.

- [ ] Document host selection, browser split, PAC ordering, fresh Copilot Studio MCP checks, failure classification, and host-hop stop conditions.
- [ ] Verify acceptance language makes no unsupported tenant/runtime claims.

### Task 4: Independent convergence and delivery

- [ ] Run full tests, compileall, and `git diff --check`.
- [ ] Review against ORIGINAL-OBJECTIVE, ACCEPTANCE, V2 architecture, Work Radar lessons, autonomy-first, and least-resistance requirements.
- [ ] Fix critical/important findings and rerun verification.
- [ ] Commit the change on this branch; do not merge or create Qualification Lab resources.

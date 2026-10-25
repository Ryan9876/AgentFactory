# AgentFactory V2 repository acceptance

This is repository acceptance evidence, not tenant or cloud qualification. Status values are PASS, FAIL, NOT VERIFIED, or N/A and refer to this committed tree.

## Requirements to evidence

| Requirement / outcome | Evidence | Status |
|---|---|---|
| Codex-first canonical skills; lessons guardrails survive migration | `.agents/skills/`, `tests/test_skill_layout.py`, `tests/test_lessons_guardrails.py` | PASS |
| Ryan AgentFactory Stack preserves objective, requirements, convergence, and runtime qualification | `docs/product/ORIGINAL-OBJECTIVE.md`, `.agents/skills/ryan-agentfactory-stack/SKILL.md`, `tests/test_v2_policy.py` | PASS |
| Least-complex architecture, buildability, qualification, restoration, reassessment | `templates/architecture-decision.md`, architecture rules, fixture/tests | PASS |
| Organization constraints and capability evidence are machine-readable and do not treat docs as tenant proof | `config/constraints.yaml`, `config/capability-registry.yaml`, associated tests | PASS |
| Tooling bootstrap uses current documented Microsoft routes and separates authentication | `scripts/bootstrap_codex_cloud.sh`, `tests/test_bootstrap_contract.py`, Microsoft docs linked in installation guide | PASS (static contract; installer not executed) |
| First-build procedure preserves disposable Development scope, fixtures, evidence, and publication gate | `docs/first-build.md` | PASS (procedure defined; no agent created) |
| Preserved V1 release evidence and traceability | `docs/v1-acceptance.md`, release-mode traceability check (38 mandatory rows) | PASS |
| Repository tests, compile, whitespace | The complete applicable repository test suite must pass; compileall and `git diff --check` must pass | PASS (latest exact counts are reported by the validation run, not fixed here) |
| Desktop Local readiness and qualification gates | Repository-local readiness checks and durable Lab B target preflight | NOT VERIFIED — Lab B target is `UNQUALIFIED`, `CREATE_ALLOWED=NO`; Azure subscription readiness is unknown |
| Platform runtime qualification of the new declarative path | No target agent built; intentionally deferred until repository/readiness acceptance and approved project spec | NOT VERIFIED |

## Hybrid execution-host routing contract

| Requirement / outcome | Evidence | Status |
|---|---|---|
| Capability-specific Cloud/Local/either preference, supported fallback, auth/policy/human stop, browser-role separation, and distinct runtime evidence | `config/capability-registry.yaml`, `scripts/host_routing.py`, `tests/test_host_routing.py`, `tests/test_capability_registry.py` | Locally contract-tested; no tenant runtime claim |
| Separate Desktop Local readiness reports local tools, PAC/ATK state, PAC MCP, Copilot Studio MCP package, Stable/profile discovery, expected identity/environment when configured, and current known blockers without emitting raw CLI output or absolute profile paths | `scripts/local_readiness_check.py`, `tests/test_local_readiness.py`, `docs/installation.md` | Locally contract-tested; live account/browser/environment state remains environment-dependent |
| Probe A distinguishes runtime-qualified Copilot Studio MCP reads from a fixed current-environment lifecycle boundary and schema-advertised, untested operations | `docs/qualification-labs/copilot-studio-mcp-probe-a.md`, `config/capability-registry.yaml` | Lab complete; inventory/lifecycle unavailable through tested MCP route under existing entitlements; independent labs continue |
| Architecture selection rejects known unavailable entitlements before implementation, chooses viable current-entitlement alternatives, and marks unavailable capabilities without access requests | `config/constraints.yaml`, `config/capability-registry.yaml`, `scripts/config_loader.py`, architecture rules and regression tests | Contract-tested locally; environment facts remain user-specific and explicitly reevaluable |
| Original four qualification labs have resumable objectives, capability requirements, dependencies, fixtures, stop conditions, evidence, and restoration state | `config/qualification-labs.yaml`, `docs/qualification-labs/`, `docs/qualification-labs/qualification-summary.md`, `tests/test_qualification_labs.py` | A/B/C/D outcomes consolidated with verified reads, fixed constraints, and unresolved runtime evidence; no lab mutation occurred in this checkpoint |
| Declarative lifecycle feasibility isolates sideload, Personal owner-only, and optional sharing prerequisites | `config/qualification-labs.yaml`, `tests/test_qualification_labs.py`, Lab B evidence/specification | ATK rejected by fixed sideload; Personal candidate excludes unnecessary share/Azure dependencies; optional share remains unverified; all WIQD lifecycle prerequisites fail closed until qualified; no resource created |
| Host-composed Work IQ requires a real context-transfer test in Microsoft 365 Copilot with a suitable specialized agent | `docs/qualification-labs/host-composed-work-iq-lab-c.md` | Browser Copilot/catalog and partial published metadata read verified; declared tool operation/schema/data scope and full knowledge-source inventory remain unverified; no tool invoked and all context-transfer fixtures NOT TESTED |
| Direct Work IQ MCP assessment applies the fixed program premise without repeating known-boundary checks | `docs/qualification-labs/direct-work-iq-mcp-lab-d.md`, capability registry, current Microsoft Learn prerequisites | Assessment complete from registry/program premise; individual tenant prerequisites not reverified; auth, live schema, retrieval, and evaluation NOT TESTED |

## Workflow provenance

- Product truth: approved V2 design/addenda plus this original-objective record and existing AgentFactory requirement/approval machinery.
- Engineering profile: repo-local Ryan AgentFactory Stack; Superpowers concepts used as engineering principles, not a top-level product workflow.
- UI design gate: N/A; no custom UI is in scope.
- Implementation and checks: repository edits, targeted unittest contracts, full suite, compilation, shell syntax, traceability, diff checks.
- Independent acceptance: requirement-to-evidence audit recorded above. Microsoft runtime/platform review remains NOT VERIFIED until the selected Development target is available.
- Branch finishing: changes committed to `agentfactory-v2`; no merge or push.

## Known limitations and next gate

The repository is ready for creation of the fresh Codex Cloud environment and bootstrap. First-build execution is not yet qualified: bootstrap must run in that environment; WIQD must be available; Microsoft authentication and a positively identified Development target must pass readiness; then approved disposable-agent requirements and actual runtime fixtures are required. No Production change or organization-wide publication is authorized by this acceptance record.

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
| Repository tests, compile, shell syntax, whitespace | 99 tests; compileall; `bash -n`; `git diff --check` on accepted tree | PASS |
| Codex host has WIQD, Microsoft Learn MCP, and live Microsoft authentication/Development target | Local readiness output | NOT VERIFIED / BLOCKED: WIQD missing; auth and target not established |
| Platform runtime qualification of the new declarative path | No target agent built; intentionally deferred until repository/readiness acceptance and approved project spec | NOT VERIFIED |

## Workflow provenance

- Product truth: approved V2 design/addenda plus this original-objective record and existing AgentFactory requirement/approval machinery.
- Engineering profile: repo-local Ryan AgentFactory Stack; Superpowers concepts used as engineering principles, not a top-level product workflow.
- UI design gate: N/A; no custom UI is in scope.
- Implementation and checks: repository edits, targeted unittest contracts, full suite, compilation, shell syntax, traceability, diff checks.
- Independent acceptance: requirement-to-evidence audit recorded above. Microsoft runtime/platform review remains NOT VERIFIED until the selected Development target is available.
- Branch finishing: changes committed to `agentfactory-v2`; no merge or push.

## Known limitations and next gate

The repository is ready for creation of the fresh Codex Cloud environment and bootstrap. First-build execution is not yet qualified: bootstrap must run in that environment; WIQD must be available; Microsoft authentication and a positively identified Development target must pass readiness; then approved disposable-agent requirements and actual runtime fixtures are required. No Production change or organization-wide publication is authorized by this acceptance record.

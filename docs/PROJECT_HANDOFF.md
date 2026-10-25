# AgentFactory project handoff

Use this file to resume AgentFactory work without rebuilding context from conversation history. Verify the current branch, commit, and working tree before continuing.

## Current repository and work

- Repository: `Ryan9876/AgentFactory`
- Local path: `/Users/ryan2015/Projects/AgentFactory`
- Qualification branch: `codex/labs-bc-auth-checkpoint`
- Baseline at the start of this remediation: `fe329660e314ddfc33241f530f77dfed99760443`
- Do not commit, merge, or push unless Ryan explicitly authorizes it.
- Project-local `.agent-factory/` is generated state and is ignored. Tests and durable qualification claims must use tracked files only.
- Machine-readable qualification states are in [`config/qualification-labs.yaml`](../config/qualification-labs.yaml). Compact durable Lab B/C records are in [`docs/qualification-labs/evidence/`](qualification-labs/evidence/).

## What AgentFactory is

AgentFactory V2 is a Codex-first control plane for designing, building, verifying, and packaging internal Microsoft 365 agents. It selects the least-complex viable supported architecture and does not create its own Microsoft 365 runtime, retrieval layer, generic API abstraction, or browser automation layer.

Core method: **Use → Configure → Integrate → Automate → Extend → Build.** Prefer supported routes within current entitlements, diagnose the failing layer, and distinguish static/source checks from runtime qualification.

## Repository instructions and guardrails

Read `AGENTS.md` and follow the repo-local `agentfactory` and `ryan-agentfactory-stack` skills. Read `.agents/skills/agentfactory/references/engineering-guardrails.md` before architecture selection, cloud mutation, or qualification. The V2 design and lessons are in `docs/superpowers/specs/2026-10-21-agentfactory-v2-design.md` and `docs/superpowers/specs/2026-10-21-agentfactory-v2-lessons-addendum.md`; organization constraints are in `config/constraints.yaml`.

Use current first-party Microsoft documentation for mutable platform facts. Do not bypass user authentication, security, tenant policy, or admin boundaries. Production mutation and organization-wide publication require explicit approval.

## Original four qualification labs

See the [consolidated qualification summary](qualification-labs/qualification-summary.md) and the individual records linked from `config/qualification-labs.yaml`.

- **Lab A — Copilot Studio MCP:** `COMPLETE`; disposition `CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT`. Missing `prvReadbot` blocks agent inventory. Lifecycle mutations and cleanup remain `NOT_TESTED`; do not retry or host-hop around the boundary.
- **Lab B — declarative agent lifecycle:** `PREFLIGHT_BLOCKED`; target `UNQUALIFIED`; `CREATE_ALLOWED=NO`. The sole active approved spec is [`lab-b-corporate-tenant-spec.md`](qualification-labs/lab-b-corporate-tenant-spec.md), SHA-256 `0d27ae6d9927b8d12cb3edf29ccdd8882c742812c5d0e9ad8da678f46511dd88`, dated 2026-10-23. Specification approval does not authorize execution. The prior frozen digest is superseded after sanitization; the earlier [`lab-b-disposable-agent-spec.md`](qualification-labs/lab-b-disposable-agent-spec.md) is also superseded and inactive. Current Production target is blocked by known disabled custom-app upload/sideload; no qualifying Development/Test target was identified in available local surfaces, and Azure readiness is unknown. Do not create or repeat fixed policy checks.
- **Lab C — host-composed Work IQ:** overall `RUNTIME_NOT_TESTED`; the local fixture contract alone is `SOURCE_QUALIFIED`. Complete effective knowledge and tool-retrieval scope remains unverified. Do not invoke the tool or send fixtures until a materially new supported read-only source resolves the gap.
- **Lab D — direct Work IQ MCP:** `ASSESSMENT_COMPLETE`; disposition `CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT`. Direct authentication, catalog, retrieval, and evaluation operations remain `NOT_TESTED`; do not retry known fixed prerequisites.

No lab created a cloud resource in the recorded qualification work. See the individual evidence records for cleanup/restoration status.

## Preserved Probe A

Full evidence: [`copilot-studio-mcp-probe-a.md`](qualification-labs/copilot-studio-mcp-probe-a.md).

A fresh Copilot Studio MCP process authenticated, selected the Development environment, and loaded the live catalog. Connection and workflow listings succeeded. Agent inventory was blocked by missing `prvReadbot`. Advertised lifecycle schemas are discovery evidence, not runtime qualification. No agent was created or changed. Probe A is complete with a fixed-environment blocker; independent labs continue.

## Verification

For repository changes, run:

```sh
PATH=.venv/bin:$PATH python3 -m unittest discover -s tests -v
PATH=.venv/bin:$PATH python3 -m compileall scripts tests
git diff --check
```

Report the actual test count from each run. Do not record a fixed test count as a durable acceptance requirement.

## Resume prompt

“Continue AgentFactory from `docs/PROJECT_HANDOFF.md` and `config/qualification-labs.yaml`. Verify branch, HEAD, and working tree first. Preserve local generated `.agent-factory/` state and do not commit, merge, or push without authorization. Keep Lab A/D at their recorded fixed-constraint dispositions, Lab B preflight-blocked with CREATE prohibited, and Lab C runtime untested. Do not repeat tenant checks, authenticate, invoke agent tools, or mutate Microsoft resources unless separately authorized and all recorded gates pass.”

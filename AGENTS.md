# AgentFactory V2

This Codex-first repository designs, builds, verifies, and packages internal Microsoft 365 agents.

Before implementation, apply the approved [V2 design](docs/superpowers/specs/2026-10-21-agentfactory-v2-design.md), [lessons addendum](docs/superpowers/specs/2026-10-21-agentfactory-v2-lessons-addendum.md), and [organization constraints](config/constraints.yaml). Follow the repo-local `agentfactory` and `ryan-agentfactory-stack` skills. The engineering-guardrails reference is mandatory before architecture selection, cloud mutation, and qualification.

Use current first-party Microsoft documentation for mutable platform facts. Diagnose the failing layer before changing architecture. Runtime qualification is distinct from source/static validation. Execute safe repository, CLI, API, MCP, and browser work autonomously; exhaust reasonable supported fallbacks within existing entitlements before handoff. Stop at genuine user-presence boundaries; treat admin/security/tenant policy blockers as fixed constraints and redesign within existing authority. Production/publication boundaries require explicit approval.

Design and qualify only within Ryan's existing entitlements as recorded in `config/constraints.yaml` and the capability registry. Do not recommend seeking additional privileges, licenses, credits, billing, consent, policy exceptions, or tenant-wide enablement. Treat known entitlement/policy blockers as architecture inputs, evaluate supported alternatives within current authority, and continue independent qualification labs.

Development is the default. Production mutation and organization-wide publication require explicit approval. Never invent tenant/environment IDs, schemas, credentials, URLs, connector operations, permissions, or verification results.

Verify repository changes with `PATH=.venv/bin:$PATH python3 -m unittest discover -s tests -v`, `PATH=.venv/bin:$PATH python3 -m compileall scripts tests`, and `git diff --check`.

# AgentFactory V2

AgentFactory is a Codex-first control plane for designing, building, verifying, and packaging internal Microsoft 365 agents. It selects the least-complex viable supported architecture and retains explicit approval, traceability, and evidence gates.

**Method:** Use → Configure → Integrate → Automate → Extend → Build. **Execution:** Automate first, try supported fallbacks, exhaust reasonable options, and hand off only irreducibly human steps.

## Skills and policy

Canonical repo skills live in `.agents/skills/`: `agentfactory`, `ryan-agentfactory-stack`, `agent-spec-verifier`, and `power-platform-resilience`. Organization constraints are in `config/constraints.yaml`; design, workflow, lessons, and first-build procedure are under `docs/`.

Declarative agents are preferred when suitable. GitHub Copilot harness agents and Copilot Studio embedded Work IQ are disallowed under current constraints. Direct Work IQ MCP is conditional and is not a first-build dependency. Development is the default; Production mutation and organization-wide publication require explicit approval.

## Readiness

Repository tests prove local contracts only. Source/static validation is distinct from cloud synchronization and target-runtime qualification. Microsoft authentication, Development environment suitability, host skill discovery, and live first-party tooling remain to be verified in the fresh Codex Cloud environment; consult `docs/installation.md` and `docs/first-build.md`.

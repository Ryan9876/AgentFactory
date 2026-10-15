# Architecture decision rules — planned, not implemented

Use Standard Copilot Studio by default. Select a newer GHCP-style harness only when explicitly requested or when it offers a material architectural advantage, required tooling exists, and maturity/compatibility is acceptable; record why.

- Knowledge: searchable factual/reference content.
- Skill: reusable procedural knowledge or multi-step guidance.
- Tool: external action, live-system data, deterministic computation, or API execution.
- Power Automate: prefer for deterministic branching, approvals, multiple connectors, retries/recovery, asynchronous processing, and workflow state.
- Dataverse: add only for actual structured persistence, relationships, ownership/security semantics, durable workflow state, or solution-managed structured data. Reuse an authoritative system when it owns the state.
- Additional agents: require a meaningful responsibility, security, permissions, data, lifecycle, tool-surface, or evaluation boundary; do not split prompts for organization alone.
- Custom development preference: native Copilot Studio → knowledge → built-in connector/tool → Power Automate → Dataverse → existing MCP/API → custom connector → custom code. This is a preference, not a hard rule.

Architecture precedes specification. Justify every selected component and record rejected alternatives where consequential.

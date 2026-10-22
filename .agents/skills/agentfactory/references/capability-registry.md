# Capability registry V2

`config/capability-registry.yaml` is the canonical multidimensional evidence record. `capability-routes.csv` maps stable requirement-scoped intents to owners and unavailable behavior. The registry distinguishes Microsoft documentation/support, preview status, organization policy, licensing, Codex host discovery, authentication, tenant execution, cloud synchronization, runtime qualification, user-presence/admin boundaries, and tool-host blocks.

Evidence is time- and host-specific. Preserve source and date. A documentation hit or CLI help output cannot mark authentication, tenant execution, synchronization, or runtime qualification as passed. Historical Work Radar and V1 evidence remain historical; they do not prove current Codex Cloud readiness.

Unknown capability intent has no automatic fallback: block only dependent tasks with the missing intent and evidence needed. Select a fallback only after verifying it is supported and still satisfies approved requirements. Keep `BLOCKED`, `FAILED`, `NOT_TESTED`, `CLOUD_SYNCHRONIZED`, and `RUNTIME_QUALIFIED` distinct.

Never route GitHub Copilot harness under current constraints. Keep host-composed Work IQ independent from conditional direct Work IQ MCP. Do not make direct Work IQ MCP a default dependency.

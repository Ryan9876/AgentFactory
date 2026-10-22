# Disposable declarative first build

The first build is a low-risk internal declarative knowledge agent. It has no external mutation, Dataverse, Power Automate, GHCP, embedded Work IQ, or direct Work IQ MCP dependency. WIQD is primary; evaluate Agents Toolkit when WIQD prerequisites (including Azure access) block the route and the fallback still meets approved requirements.

1. Run offline repository tests and readiness on the selected host; run Desktop Local readiness before tenant-authenticated stages.
2. Complete supported Microsoft authentication and positively identify Development; stop only at genuine user-presence/admin boundaries.
3. Run `wiqd doctor`; record evidence and decide WIQD versus Agents Toolkit.
4. Approve objective, architecture, spec, path-of-least-resistance record, security/publication boundary, and positive/negative/boundary/non-applicable/repeatability fixtures.
5. Create disposable agent, run static/package validation, then Development-only provision/sideload if authorized and available.
6. Test grounded and unsupported prompts in the actual Microsoft 365 Copilot runtime; capture evidence and distinguish implemented from runtime-qualified.
7. Record cleanup/retention decision. No organization-wide share or publication without explicit approval.

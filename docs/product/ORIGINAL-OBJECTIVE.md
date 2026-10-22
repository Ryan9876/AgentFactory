# AgentFactory V2 original objective and constraints

Source: user instruction in the AgentFactory V2 implementation session, 2026-10-21. This record preserves the governing objective for implementation convergence; it is not a second product specification or approval artifact. The approved design and addenda remain the detailed product truth.

## Objective

Make this repository a clean, Codex-first AgentFactory V2 environment that builds Microsoft 365 agents quickly and reliably using the least-complex supported architecture. Continue repo-side work autonomously; stop only at genuine user-presence or administrator boundaries. Do not modify `main`, rewrite Git history, merge, push, deploy to Production, or perform organization-wide publication. Preserve accepted V1 evidence.

## Governing method and execution

- Implementation order: **Use → Configure → Integrate → Automate → Extend → Build**.
- Execution: **AUTOMATE FIRST → TRY THE NEXT SUPPORTED PATH → EXHAUST REASONABLE OPTIONS → HAND OFF ONLY THE IRREDUCIBLY HUMAN STEP**.
- Original requirements outrank derived plans; no requirement erosion for implementation convenience.
- Trace requirements to implementation and evidence; independently converge against original requirements.
- Runtime qualification is distinct from source correctness; passing tests alone do not prove platform correctness.
- Diagnose the failing layer before architecture changes; use supported fallbacks; continue independent work.
- Security, authentication, approval, user-presence, and administrator boundaries remain binding.

## Architecture and security constraints

- Declarative agent first when suitable; Standard Copilot Studio for justified structured/Power Platform workflows; custom engine by exception.
- GitHub Copilot harness and Copilot Studio embedded Work IQ are disallowed under current organization constraints.
- Host-composed Work IQ is distinct from direct Work IQ MCP; direct MCP is conditional and not a first-build dependency.
- Development is default. Production and organization-wide publication require explicit approval.
- Never invent tenant/environment IDs, schemas, credentials, URLs, connector operations, permissions, or verification results.

## Methodology composition

AgentFactory's intake, approved specification, integrity, and traceability are the product-truth authority; do not run a duplicate Spec Kit. Use a Microsoft platform specialist step for current first-party capabilities. Superpowers may provide replaceable planning, TDD, execution, debugging, review, and verification primitives. OJO/Impeccable are conditional on substantial custom UI/UX and do not gate ordinary agents or backend/platform work.

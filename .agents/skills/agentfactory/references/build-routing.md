# Build routing contract

## Before routing

1. Confirm the user-selected target; Development is the default. Do not infer an environment from a saved profile.
2. Verify the approved spec SHA-256 before initial build or resume. A mismatch sets `SPEC_CHANGED` and blocks work until explicit reapproval.
3. Load/check only capabilities required by the approved architecture, using current registry evidence and the target environment's prerequisites.
   - Apply `environment_constraints.capability_availability` before generating implementation tasks. Eliminate candidates requiring known unavailable entitlements and select the first viable supported architecture within current authority. Record `CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT` if none remains.
4. Resolve each capability through `scripts/host_routing.py` and `execution_routing.routes` in `config/capability-registry.yaml`. Use the preferred host, then an explicitly supported alternate host only for a host/tool-surface outage, then another supported platform surface, then a human handoff if intrinsically required.
5. Generate dependency-ordered manifest tasks mapped to stable capability intents and only relevant requirement IDs.

Use the deterministic API in `../../../../scripts/build_state.py` for approval digest storage, integrity gates, manifest dependency ordering, task evidence transitions, state serialization, and resume selection. If the runtime cannot invoke the helper, record that dependency as blocked; do not approximate the digest or transition rules.

## Route each manifest task

For each agent configuration operation, record operation-specific support/evidence for candidate implementation surfaces. Pass proposed_surface and surface_assessments to scripts.host_routing.choose_execution_route; it enforces scripts.surface_routing.choose_implementation_surface with the registry preference order before routing configuration hosts. A proposed browser UI/automation route is rejected with STOP_REASSESS when any higher-priority structured surface is supported or unverified. Browser fallback requires evidence that all higher-priority routes are unavailable or insufficient and a bounded reason. After that operation, route adjacent configuration back through the highest-priority supported structured surface. Authentication, tenant permissions, security, licensing, MFA/consent, and admin/approval blockers remain authoritative and cannot be bypassed by changing surfaces.

- Select the smallest capability that owns the platform operation; Microsoft capabilities own authoring, flow/data work, evaluation, validation, and ALM.
- Pass only the task's input/output, relevant requirement IDs, approved context, dependencies, and existing artifact evidence. Do not pass unrelated project context.
- Resolve the stable ID through `config/capability-registry.yaml` and current provider evidence. Keep provider/tool details out of requirement IDs and architecture intent.
- Record provider selection, evidence status, prerequisites, output artifact, implementation evidence, and status in the manifest and traceability record.
- Mark implementation `COMPLETE` only with inspectable artifact and implementation evidence; mark it `VERIFIED` only after verification evidence is recorded.
- If an unknown capability intent is requested, or a required provider is unavailable, mark only the dependent task `BLOCKED`, record the concrete reason and owner, and continue independent tasks where safe. Do not silently fall back or fabricate a provider. Revisit architecture only through an explicit documented decision.

## Capability intent route matrix

See `capability-routes.csv` for task patterns, capability intent, relevant requirement IDs, focused context, and unavailable behavior. The matrix covers Copilot Studio authoring/testing, Power Automate, Dataverse, evaluation, and solution ALM. The execution-host mapping is in `config/capability-registry.yaml`; routing is guidance, not proof that an operation is authorized or available in the selected environment.

Never host-hop or switch to browser automation to work around authentication/MFA, consent, missing permissions, tenant/admin/security policy, licensing, billing, Production approval, or publication approval. Preserve the blocker as `BLOCKED_BY_TENANT_OR_POLICY` or `FIXED_ENVIRONMENT_CONSTRAINT`; do not recommend seeking more authority or spend. `USER_PRESENCE_REQUIRED` stops at its human boundary. `ADMIN_REQUIRED` is recorded as a fixed design constraint for this program, then alternative architectures are evaluated. Continue independent tasks and labs.

For PAC MCP, authenticate PAC first, then start or restart the MCP process to avoid stale profile state. For every fresh Copilot Studio MCP process, verify account and Development environment, then refresh the online schema/tool catalog. Keep process-local credentials opaque. Tool discovery is not runtime qualification.

## Harness decision

Standard Copilot Studio is the default. A GHCP-style harness is routed only when explicitly requested or when a material architectural advantage is documented and required tooling, maturity, and compatibility are verified. A listed-but-unavailable plugin cannot satisfy that gate.

## Resume

Recheck spec integrity, read persisted state and manifest, inspect existing platform artifacts, and verify evidence for completed work. Reuse only completed work with inspectable verification evidence. An inspected incomplete task becomes ready to restart; an uninspected artifact or uncertain prior side effect is blocked. Resume at the first incomplete dependency-ready task and continue independent safe work; do not repeat a side effect when its prior outcome is uncertain.

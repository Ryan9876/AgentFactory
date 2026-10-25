# AgentFactory V2 Architecture

Select the least-complex viable supported architecture; Standard Copilot Studio is not the universal default. Diagnose platform, tool-host, authentication, browser, environment, authoring, connector, and runtime failures before changing architecture. Source/static validation does not establish cloud synchronization or runtime qualification. The mandatory engineering policy is `.agents/skills/agentfactory/references/engineering-guardrails.md`.

## Boundary

Agent Factory is a thin orchestration and control plane. It maintains objective context, decisions, approved requirements, routing, progress, evidence, and acceptance state. The execution plane consists of Microsoft Copilot Studio and Power Platform capabilities that create, run, validate, evaluate, and package platform artifacts.

Execution host is selected per capability from `config/capability-registry.yaml`; it is not a global Cloud/Local switch. Codex Cloud is the reproducible engineering surface. Desktop Local is the preferred Microsoft tenant-authenticated and target-runtime surface. `scripts/host_routing.py` applies the declared capability preference and blocks fallback on policy, permission, authentication, MFA, consent, billing/licensing, admin, or publication boundaries.

```text
User objective
      ↓
Custom control-plane skills ── state/spec/traceability ── approval gates
      ↓ focused delegation
Microsoft capability registry
      ↓
Capability-specific host route: Codex Cloud | Desktop Local
      ↓
Copilot Studio | Power Automate | Dataverse | evaluation | solution ALM
      ↓ evidence
Spec verifier → SHIP / ITERATE / BLOCK → acceptance package
```

The Factory does not implement an agent runtime, Copilot Studio schema, Power Automate API wrapper, Dataverse SDK abstraction, generalized CI/CD system, or replacement authoring UI.

## Custom skills

`m365-agent-factory` owns objective intake through approved specification and build orchestration. `power-platform-resilience` defines cross-cutting policies and review guidance; it is not an implementation engine. `agent-spec-verifier` owns evidence checks, validation order, remediation routing, and the acceptance verdict.

## Microsoft capabilities

Use Microsoft capabilities for platform operations wherever they exist. The capability registry records capability family, purpose, availability, host, version/compatibility evidence, and fallback or blocking behavior without binding the control plane to a particular evolving command. Route only relevant requirements to the responsible capability.

For agent configuration, choose the highest-priority supported operation-specific surface: MCP, CLI, API/SDK, supported code/config editor, declarative/source or import/export, then browser UI/automation. Browser automation is rejected whenever a structured route works or remains unverified; fallback requires recorded evidence and a bounded reason. Browser interaction remains valid for identity, MFA/consent, visual/runtime observation, and portal-only operations. It does not replace reliable platform interfaces. See `docs/supported-platforms.md` for the Cloud/Local and Chrome surface split.

Apply the existing-entitlements-only constraint before committing to architecture. Compare candidate requirements with `environment_constraints.capability_availability` in `config/capability-registry.yaml`; use `scripts.config_loader.evaluate_architecture_candidates` in least-complex-first order. Reject candidates that depend on fixed unavailable privileges, licenses, credits, consent, policy, sideloading, billing, service principals, or Production access. Select a viable route within current authority, or record `CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT`. Never remediate by recommending increased access or spend. Reevaluate the map only after Ryan explicitly states that the premise changed.

## Architecture rules

- Default to Standard Copilot Studio. Consider the newer GHCP-style harness only when explicitly requested or when it gives a material advantage and tooling maturity/compatibility is acceptable; record the decision.
- Use knowledge for searchable facts and reference content; skills for reusable procedures; tools for external actions, live data, deterministic computation, or API execution.
- Prefer Power Automate for deterministic branching, approvals, multiple connectors, retries/recovery, asynchronous work, or workflow state.
- Add Dataverse only for actual needs such as structured persistent data, relationships, ownership/security, durable workflow state, or solution-managed structured data. Reuse an authoritative state system when suitable.
- Add agents only across meaningful responsibility, security, permission, data, lifecycle, tool, or evaluation boundaries.
- Evaluate custom development in this preference order: native Copilot Studio capability → knowledge → built-in connector/tool → Power Automate → Dataverse → existing MCP/API → custom connector → custom code. This is guidance, not an absolute rule.

## Project state

Each generated agent receives `.agent-factory/` for control-plane state, including the objective, clarifications, decisions, approved specification and hash state, manifest, traceability, acceptance report, and eval materials. This directory does not replace Copilot Studio project files, flows, Dataverse solutions, or other Microsoft-owned artifacts.

# Architecture

## Boundary

Agent Factory is a thin orchestration and control plane. It maintains objective context, decisions, approved requirements, routing, progress, evidence, and acceptance state. The execution plane consists of Microsoft Copilot Studio and Power Platform capabilities that create, run, validate, evaluate, and package platform artifacts.

```text
User objective
      ↓
Custom control-plane skills ── state/spec/traceability ── approval gates
      ↓ focused delegation
Microsoft capability registry
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

## Architecture rules

- Default to Standard Copilot Studio. Consider the newer GHCP-style harness only when explicitly requested or when it gives a material advantage and tooling maturity/compatibility is acceptable; record the decision.
- Use knowledge for searchable facts and reference content; skills for reusable procedures; tools for external actions, live data, deterministic computation, or API execution.
- Prefer Power Automate for deterministic branching, approvals, multiple connectors, retries/recovery, asynchronous work, or workflow state.
- Add Dataverse only for actual needs such as structured persistent data, relationships, ownership/security, durable workflow state, or solution-managed structured data. Reuse an authoritative state system when suitable.
- Add agents only across meaningful responsibility, security, permission, data, lifecycle, tool, or evaluation boundaries.
- Evaluate custom development in this preference order: native Copilot Studio capability → knowledge → built-in connector/tool → Power Automate → Dataverse → existing MCP/API → custom connector → custom code. This is guidance, not an absolute rule.

## Project state

Each generated agent receives `.agent-factory/` for control-plane state, including the objective, clarifications, decisions, approved specification and hash state, manifest, traceability, acceptance report, and eval materials. This directory does not replace Copilot Studio project files, flows, Dataverse solutions, or other Microsoft-owned artifacts.

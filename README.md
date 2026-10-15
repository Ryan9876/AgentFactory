# M365 Agent Factory

M365 Agent Factory is a low-effort control plane for designing and developing useful Microsoft 365 Copilot agents with Copilot Studio and Power Platform. It is being implemented as a thin skill pack that turns a business objective into a clarified, approved, traceable specification, then coordinates implementation and verification through Microsoft capabilities.

## Lifecycle

```text
objective → clarification → architecture → specification → approval
→ Development build → evaluation → verification → package
```

The Factory is a thin skill pack. Copilot Studio, Power Automate, Dataverse, Microsoft evaluation capabilities, and supported ALM tooling perform platform work where available. The Factory will not recreate those tools as a runtime or custom application.

## V1 custom skills

- `m365-agent-factory` owns intake, clarification, architecture, specification, approval, and implementation orchestration.
- `power-platform-resilience` provides cross-cutting identity, side-effect, recovery, configuration, and observability guidance.
- `agent-spec-verifier` checks spec integrity, requirement evidence, platform validation, evaluations, resilience, remediation, and acceptance.

The three skill files remain marked **NOT IMPLEMENTED** in this task sequence. Check each `SKILL.md` status before relying on a capability; a scaffold is not implementation evidence.

## Repository map

- `docs/specs/` — authoritative product and build specification.
- `docs/superpowers/plans/` — task-sized implementation plan derived from the specification.
- `docs/` — workflow, architecture, platform support, and installation guidance.
- `.github/skills/` — planned custom skill packages and reference boundaries.
- `templates/` — contracts for agent artifacts and acceptance records.
- `scripts/`, `tests/`, `examples/` — reserved for later helpers, tests, and examples.

## Development status

Implementation is in progress on an isolated feature branch. The repository/dependency baseline is recorded in [installation and preflight notes](docs/installation.md). The Copilot CLI is not installed in the current environment; the documented `.github/skills/` path is not runtime-tested here. Microsoft platform authoring and evaluation have not been exercised. See the authoritative [V1 specification](docs/specs/m365-agent-factory-spec.md) and [implementation plan](docs/superpowers/plans/2026-10-14-m365-agent-factory.md).

## Planned implementation sequence

The implementation plan orders baseline and artifact contracts; spec hash and traceability helpers; intake/clarification; architecture and specification contracts; resilience and capability routing; manifest/state/resume; verification and remediation; golden scenarios; a real Development environment pilot; then V1 acceptance and documentation.

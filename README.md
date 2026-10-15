# M365 Agent Factory

M365 Agent Factory is a low-effort control plane for designing and developing useful Microsoft 365 Copilot agents with Copilot Studio and Power Platform. Its three custom skills turn a business objective into a clarified, approved, traceable specification, then coordinate implementation and verification through Microsoft capabilities.

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

The three repository skill packages now contain their V1 procedural contracts and references. Repository tests verify local contracts and helper behavior; skill-host discovery and real Microsoft platform execution have not been exercised.

## Repository map

- `docs/specs/` — authoritative product and build specification.
- `docs/superpowers/plans/` — task-sized implementation plan derived from the specification.
- `docs/` — workflow, architecture, platform support, and installation guidance.
- `.github/skills/` — the three custom orchestration/reference skill packages and capability registry.
- `templates/` — contracts for objective, architecture, spec, manifest, state, traceability, and acceptance artifacts.
- `scripts/` — standard-library helpers for hashes, traceability, build state/resume, verification, and remediation routing.
- `tests/` — unit and contract tests, fixtures, and six golden scenarios.

## Development status

**Status: PARTIAL — live pilot and operational V1 acceptance are blocked.**

Local implementation is present on an isolated feature branch. The repository/dependency baseline is recorded in [installation and preflight notes](docs/installation.md). The Copilot CLI is not installed, so `.github/skills/` discovery is not runtime-tested. No Microsoft agent was authored, evaluated, or packaged in a live Development environment. The real Development pilot is blocked pending a positively selected target and verified Copilot Studio/evaluation paths. See the [V1 acceptance record](docs/v1-acceptance.md), [requirement evidence matrix](docs/acceptance-traceability.csv), authoritative [V1 specification](docs/specs/m365-agent-factory-spec.md), and [implementation plan](docs/superpowers/plans/2026-10-14-m365-agent-factory.md).

## Planned implementation sequence

The plan orders baseline and artifact contracts; deterministic helpers; intake, architecture, and specification contracts; resilience and capability routing; manifest/state/resume; verification and remediation; golden scenarios; a real Development environment pilot; then final acceptance and documentation. Local tasks through golden scenarios are implemented and tested. The live pilot and operational V1 acceptance remain blocked; see [acceptance status](docs/v1-acceptance.md).

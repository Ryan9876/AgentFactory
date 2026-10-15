---
name: agent-spec-verifier
description: Scaffold for verifying implementations against an approved agent specification.
---

# Status: NOT IMPLEMENTED

## Purpose

Verify spec integrity, requirement traceability, platform validation, functional behavior, evaluation, resilience, remediation, and acceptance.

## Boundaries

The verifier reports evidence-based `SHIP`, `ITERATE`, or `BLOCK`. It does not silently change approved requirements or substitute for platform tools.

## Inputs and outputs (planned)

- Inputs: approved spec and hash, artifacts, traceability, platform validation and evaluation evidence.
- Outputs: ordered verification record, findings/remediation routes, verdict, and acceptance report.

## Dependencies (planned, unverified)

Deterministic integrity/traceability helpers; responsible Microsoft platform validation and evaluation capabilities; resilience reference.

## References

See `references/` for protocol, traceability, and verdict contracts.

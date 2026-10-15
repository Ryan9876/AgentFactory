# Installation and prerequisites

## Current status

This repository contains planning documents and not-yet-implemented skill scaffolds. It is not currently installable as a working Agent Factory, and no Microsoft tool integration has been verified.

## Repository prerequisites

- Git and a working tree for the repository.
- Python 3 with its standard library for the planned deterministic helpers. The implementation plan may add a test runner after checking the repository baseline.
- Access to the relevant Microsoft 365 tenant and a designated Development environment for the later pilot.
- Appropriate access to Copilot Studio, Power Platform, and the Microsoft capabilities selected for the project.

## Intended skill layout

The three custom packages are under `.github/skills/<skill-name>/`, each with a `SKILL.md` and focused references. The implementation phase must verify that the target GitHub Copilot CLI or other chosen host discovers and loads this layout. Do not assume compatibility from the directory name alone.

Install or invoke Microsoft-provided capabilities using their verified, supported installation path. This repository intentionally does not prescribe unverified commands for Copilot Studio, Power Automate, Dataverse, PAC CLI, or evaluation tooling.

## Credentials

Use the approved local authentication flow for each Microsoft tool. Keep tokens, tenant authentication material, secrets, and local caches out of the repository. Never put credentials in specifications, manifests, tests, or examples.

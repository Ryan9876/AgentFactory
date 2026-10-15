# Installation and prerequisites

## Current status

Implementation is in progress. Check each skill's status before use. The local baseline below records tool availability; it does not claim that an end-to-end Microsoft integration has been verified.

## Repository prerequisites

- Git and a working tree for the repository.
- Python 3.9.6 was present during baseline inspection; the planned deterministic helpers use the standard library. `unittest` is available without an added package dependency.
- Access to the relevant Microsoft 365 tenant and a designated Development environment for the later pilot.
- Appropriate access to Copilot Studio, Power Platform, and the Microsoft capabilities selected for the project.

## Intended skill layout

The three custom packages are under `.github/skills/<skill-name>/`, each with a `SKILL.md` and focused references. GitHub's current [Copilot CLI skill guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) documents `.github/skills/` as a project-skill location and describes `/skills reload` and `/skills info`. The local `copilot` executable was unavailable during baseline inspection, so discovery/loading has not been exercised in this environment.

Install or invoke Microsoft-provided capabilities using their verified, supported installation path. This repository intentionally does not prescribe unverified commands for Copilot Studio, Power Automate, Dataverse, PAC CLI, or evaluation tooling.

## Credentials

Use the approved local authentication flow for each Microsoft tool. Keep tokens, tenant authentication material, secrets, and local caches out of the repository. Never put credentials in specifications, manifests, tests, or examples.

## Tooling preflight evidence

Observed 2026-10-14. These results are environment-specific and should be refreshed when a task first needs the corresponding capability.

| Capability/tool | Status | Evidence and limit |
|---|---|---|
| GitHub Copilot CLI | Unavailable locally | `copilot` was not found on `PATH`. GitHub documentation supports the skill directory layout above, but local discovery is unverified. |
| GitHub CLI | Installed; authentication unavailable | `gh` 2.96.0 was present. `gh auth status` reported its saved token invalid. Remote operations are not required for local implementation. |
| Copilot Studio Standard authoring | Documented; tenant access not verified | Microsoft documents native agent authoring and the Standard harness in [Create and delete agents](https://learn.microsoft.com/microsoft-copilot-studio/authoring-first-bot) and [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). No Copilot Studio authoring capability or live authoring access was exercised here. |
| GitHub Copilot harness | Documented; host/plugin unavailable locally | Microsoft documents the GitHub Copilot harness and its distinction from Standard/Copilot Chat. No Copilot Studio plugin/architect capability was available in this session. Use only if later architecture and verified tooling justify it. |
| Power Automate | Available in this host; environment selection pending | FlowAgent 3.2.1 exposes connector/operation discovery, flow authoring, validation, preflight, execution, and diagnostics. Its read-only doctor reported authentication/token checks passing and access to seven environments; no current environment is selected. A Development sandbox was listed, but Copilot Studio access and suitability for the pilot remain unverified. |
| Dataverse | Skill guidance available; execution path not verified | Dataverse skill guidance for metadata, data, security, administration, and solutions is present in the host catalog. No live Dataverse operation was attempted and no dedicated Dataverse MCP tool was present in the active tool inventory. |
| Microsoft agent evaluation | Native path documented; execution unavailable here | Microsoft documents [agent evaluation test sets](https://learn.microsoft.com/microsoft-copilot-studio/analytics-agent-evaluation-create). No dedicated evaluation capability was available in this session, and no tenant evaluation was run. |
| PAC CLI | Installed; live operations not verified | PAC CLI 2.13.1 (`microsoft.powerapps.cli.tool`) was installed. `pac help` lists `auth`, `env`, `solution`, and preview `copilot-studio` command groups; `pac solution` lists init/list/import/export/pack/unpack/check and related operations. A saved PAC auth profile was listed, but no target-environment operation was attempted. See [PAC command groups](https://learn.microsoft.com/power-platform/developer/cli/reference/) and [solution commands](https://learn.microsoft.com/power-platform/developer/cli/reference/solution). |
| Azure CLI / Power Automate identity | Available through FlowAgent; no target selected | FlowAgent doctor reported Azure CLI sign-in, token acquisition, and identity matching as passing. It reported no current Power Automate environment. No tenant or environment identifiers are stored in this repository. |

The PAC CLI `--version` and `version` forms are not valid commands in the installed 2.13.1 build; `pac help` prints the version. No custom wrapper or dependency was added. A local `az version` attempt was blocked while Azure CLI tried to write its profile diagnostic log, despite FlowAgent's successful read-only auth checks; this did not establish an Azure CLI auth failure.

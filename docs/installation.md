# Installation and prerequisites

## Current status

Implementation is partial. Check each skill's status before use. The local baseline below records tool availability; it does not claim that an end-to-end Microsoft integration has been verified.

## Repository prerequisites

- Git and a working tree for the repository.
- Python 3.9.6 was present during baseline inspection; the planned deterministic helpers use the standard library. `unittest` is available without an added package dependency.
- Access to the relevant Microsoft 365 tenant and a designated Development environment for the later pilot.
- Appropriate access to Copilot Studio, Power Platform, and the Microsoft capabilities selected for the project.

## Intended skill layout

The three custom packages are under `.github/skills/<skill-name>/`, each with a `SKILL.md` and focused references. GitHub's current [Copilot CLI skill guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) documents `.github/skills/` as a project-skill location and describes `/skills reload` and `/skills info`. The local `copilot` executable was unavailable during baseline inspection, so discovery/loading has not been exercised in this environment. Do not treat static repository tests as host compatibility evidence.

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
| Microsoft agent evaluation | Command surface available; execution and compatibility unverified | Microsoft documents [agent evaluation test sets](https://learn.microsoft.com/microsoft-copilot-studio/analytics-agent-evaluation-create). PAC 2.13.1 exposes Preview maker evaluation test-set list/get/run/result commands. Their applicability to the Standard harness, environment access, test-set setup, and approved project threshold were not verified; no tenant evaluation was run. |
| PAC CLI | Installed; local scaffold exercised; live operations not verified | PAC CLI 2.13.1 (`microsoft.powerapps.cli.tool`) exposes `pac copilot init/create/clone/pull/push`, solution commands, and preview evaluation commands. A `pac copilot init --template minimal` workspace was generated locally under `/private/tmp`; its defaults enabled web browsing and generative actions, so it was not uploaded. `pac copilot push` reported it requires a workspace produced by `clone`. No successful tenant authoring or validation was established. See [PAC command groups](https://learn.microsoft.com/power-platform/developer/cli/reference/) and [solution commands](https://learn.microsoft.com/power-platform/developer/cli/reference/solution). |
| Azure CLI / Power Automate identity | Available through FlowAgent; no target selected | FlowAgent doctor reported Azure CLI sign-in, token acquisition, and identity matching as passing. It reported no current Power Automate environment. No tenant or environment identifiers are stored in this repository. |

The Task 14 recheck on 2026-10-15 found FlowAgent authentication and environment-list access available, with seven environments visible and no current environment selected. The catalog includes a shared Sandbox, a personal Developer environment, and a separate Teams environment; Production entries are excluded. No candidate metadata available through these checks establishes Copilot Studio availability, maker rights, relevant licensing, DLP/admin suitability, or disposable-artifact suitability. No environment was selected. PAC's active profile name does not establish a safe target and its environment listing did not complete within the bounded check.

Static inspection found the three repository skills and their expected frontmatter. No supported host loaded them in this session: `m365-agent-factory`, `power-platform-resilience`, and `agent-spec-verifier` remain partially verified as repository artifacts, with runtime consumption unverified. The GitHub Copilot CLI remains unavailable and is not required for the Standard Copilot Studio architecture.

The PAC CLI `--version` and `version` forms are not valid commands in the installed 2.13.1 build; `pac help` prints the version. No custom wrapper or dependency was added. A local `az version` attempt was blocked while Azure CLI tried to write its profile diagnostic log, despite FlowAgent's successful read-only auth checks; this did not establish an Azure CLI auth failure. Do not use a merely active PAC profile as environment safety evidence.

## Deterministic helper usage

After implementation, calculate the generated project's specification digest with:

```sh
python3 scripts/spec_hash.py [--project-root PATH] [--approved-hash SHA256]
```

The root defaults to the current directory and the helper reads `.agent-factory/spec.md` as bytes. Success prints only the lowercase digest. When `--approved-hash` is supplied, a mismatch prints `SPEC_CHANGED` and exits nonzero. A missing or unreadable spec produces a diagnostic on stderr. These commands operate on local files and do not access Microsoft services.

Validate implementation coverage with:

```sh
python3 scripts/traceability_check.py --spec PATH --traceability PATH [--release]
```

The checker reads `REQ-NNN` definitions from requirement bullets or requirement table rows. It enforces the approved eight-column CSV header, rejects unknown/duplicate mappings, and requires implementation artifact/evidence for each mandatory requirement. `--release` also requires verification ID/evidence. It uses only Python's standard library; a nonzero exit means the input or coverage needs correction.

The local verification and remediation helpers can be invoked from the repository root with `python3 -m scripts.agent_spec_verifier --project-root <agent-project-root> --evidence-file <evidence-json>`. This consumes recorded external evidence; it does not execute Copilot Studio, Power Automate, Dataverse, or Microsoft evaluation checks. Remediation routing is exposed as `scripts.remediation.route_finding` and does not apply fixes.

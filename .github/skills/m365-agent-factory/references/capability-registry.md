# Capability registry contract

The control plane routes stable capability intents rather than embedding a provider's transient command or tool name in requirements or specifications. Current provider observations are data in `capability-registry.json`; routing relationships are in `capability-routes.csv`.

## Registry fields

Each provider records:

- name and observed version;
- discovery and execution status (`available`, `unavailable`, `blocked`, or `not_yet_verified`);
- install/discovery path;
- concrete compatibility evidence and date;
- prerequisites, limitations, and behavior when unavailable.

Each stable capability entry records its ID, family, operation scope, and one or more provider IDs. Update provider observations when the host or Microsoft tooling changes; capability IDs remain stable unless the product capability itself changes.

Discovery and execution are separate. A skill catalog entry, CLI help listing, or documentation page proves only the fact it directly shows. It does not prove tenant access, authentication, permission, environment compatibility, or a successful operation. Mark these dependencies separately and use `not_yet_verified` until checked. A preview operation must be labeled preview.

## Routing failure

Resolve every requested capability ID against the registry before preflight. An **unknown capability intent** has no safe implicit mapping and no automatic fallback: mark the affected manifest task `BLOCKED`, state the missing registry entry, and route the gap for architecture/registry review. If a known required capability has no available provider or its prerequisites fail, mark the task blocked with the evidence and owner. Do not invent a provider or substitute an unrelated tool. A simpler alternative is allowed only after an explicit architecture decision records why it still meets the requirement.

## GHCP harness selection

Standard Copilot Studio remains the default. Route to `copilot_studio.ghcp.author` only when the user explicitly requests that harness or the architecture records a material advantage, confirms required tooling exists, and establishes acceptable maturity/compatibility. Otherwise retain Standard Copilot Studio. Missing GHCP support is not a reason to invent an integration; use the default if it still meets the approved objective or block if GHCP is required.

## Evidence sources

Current host discovery and CLI output are recorded in the JSON registry. First-party platform evidence includes [PAC CLI reference](https://learn.microsoft.com/power-platform/developer/cli/reference/), [Copilot Studio harness documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), [agent evaluation guidance](https://learn.microsoft.com/microsoft-copilot-studio/analytics-agent-evaluation-create), and [GitHub Copilot CLI skill discovery](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills). Links document product behavior; they do not prove a local installation or tenant authorization.

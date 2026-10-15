# Intended platform support

This page distinguishes intended support from observed local capability. The status observations below were recorded during the 2026-10-14 implementation baseline; none proves end-to-end agent delivery.

| Area | Status | V1 intent | Must validate |
|---|---|---|---|
| Standard Copilot Studio | Planned support; default harness. Authoring documented; access not verified. | Agent authoring, knowledge, tools, and agent testing through Microsoft capabilities | Tenant authoring access, licensing, skill/tool availability, target environment |
| GitHub Copilot harness (GHCP-style) | Conditional planned support; product documented, local plugin unavailable | Select only by request or material advantage, with acceptable maturity and compatibility | Copilot Studio plugin/architect availability, installation, compatibility, evaluation path |
| Power Automate | Host tools available; no current environment selected | Discover connectors/operations; create, edit, validate, preflight, run, and diagnose flows using Microsoft capabilities | Select and verify a Development environment; connector permissions and policy constraints |
| Dataverse | Skill guidance available; execution path not verified | Metadata, data, security, administration, solutions, and ALM only when requirements need it | Verify tool path and environment access just in time; confirm data/solution ownership and security model |
| Evaluation | Microsoft native evaluation documented; runtime unavailable here | Use Microsoft agent evaluation guidance/tooling for plans, test generation, interpretation, and remediation | Verify available capability, supported agent types, reproducibility, and user-approved thresholds |
| Power Platform ALM / PAC CLI | PAC CLI 2.13.1 installed; live operations not verified | Use Microsoft-supported solution tooling and PAC CLI; no custom wrapper absent a demonstrated gap | Verify auth against the selected Development environment and supported solution lifecycle |
| GitHub Copilot CLI skill discovery | `.github/skills/` documented; local CLI unavailable | Host custom skills in the documented project-skill directory | Install/verify CLI and test discovery/reload/frontmatter compatibility |
| Development environment | A Development sandbox is listable via Power Automate; suitability/access for Copilot Studio not verified | Confirm the target before build; Development is default | Select target explicitly; verify licensing, Copilot Studio access, DLP/policies, and approvals |

Capability names and registry entries must remain replaceable as Microsoft tooling evolves. Do not pin workflows to a specific command until verified during implementation.

Evidence sources: [GitHub Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills), [Copilot Studio harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), [agent evaluation](https://learn.microsoft.com/microsoft-copilot-studio/analytics-agent-evaluation-create), and [PAC CLI command groups](https://learn.microsoft.com/power-platform/developer/cli/reference/).

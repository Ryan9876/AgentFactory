# Intended platform support

This page describes the intended V1 support boundary. No platform integration has been tested in this bootstrap.

| Area | Status | V1 intent | Must validate |
|---|---|---|---|
| Standard Copilot Studio | Planned support; default harness | Agent authoring, knowledge, tools, and agent testing through Microsoft capabilities | Current authoring path, skill/tool availability, host compatibility, tenant access |
| Newer Copilot Studio / GHCP harness | Planned conditional support | Select only by request or material advantage, with acceptable maturity and compatibility | Plugin/architect capability availability, installation, compatibility, evaluation path |
| Power Automate | Planned support | Discover connectors/operations; create, edit, validate, preflight, run, and diagnose flows using Microsoft capabilities | Current skill/tool path, connector permissions, environment and policy constraints |
| Dataverse | Conditional planned support | Metadata, data, security, administration, solutions, and ALM only when requirements need it | Tool path, environment access, data/solution ownership, security model |
| Evaluation | Planned support | Use Microsoft agent evaluation guidance/tooling for plans, test generation, interpretation, and remediation | Available evaluation tooling, supported agent types, reproducibility and thresholds |
| Power Platform ALM / PAC CLI | Planned support | Use Microsoft-supported solution tooling and PAC CLI; no custom wrapper absent a demonstrated gap | PAC CLI version and auth, supported solution lifecycle, target environment permissions |
| GitHub Copilot CLI skill discovery | Uncommitted dependency | Host the custom skills in `.github/skills/` if the selected CLI supports this layout | Exact CLI version, discovery rules, frontmatter/schema, plugin interaction |
| Development environment | Required for pilot; not yet available/validated | Confirm target environment before build; Development is default | Tenant/environment access, licensing, DLP/policies, admin approvals |

Capability names and registry entries must remain replaceable as Microsoft tooling evolves. Do not pin workflows to a specific command until verified during implementation.

# AgentFactory V2 design

Status: proposed V2 architecture for implementation planning and first-build readiness.

## 1. Objective

AgentFactory is a Codex Cloud development environment and repository whose sole purpose is to design, build, verify, and package Microsoft 365 agents for internal organizational use as quickly and reliably as possible.

AgentFactory is a thin control plane. It does not implement its own Microsoft 365 agent runtime, retrieval layer, Power Platform API abstraction, browser automation layer, or Microsoft documentation corpus. It selects the least-complex viable Microsoft-supported architecture, invokes the appropriate first-party tooling, records evidence, and blocks designs that conflict with known licensing, tenant, security, or automation constraints.

The implementation preference order is:

**Use → Configure → Integrate → Automate → Extend → Build.**

## 2. Existing V1 assets to preserve

V2 keeps the useful V1 control-plane behavior and evidence rather than replacing the project wholesale.

Preserve:

- objective intake and separation of facts, assumptions, and unknowns;
- architecture-before-specification discipline;
- explicit specification approval before implementation;
- specification hash/integrity checks;
- dependency-ordered build manifests;
- requirement traceability and evidence;
- resume behavior;
- resilience/security review;
- ordered verification and SHIP / ITERATE / BLOCK verdicts;
- explicit approval before Production mutation or organization-wide publication;
- the successful Standard Copilot Studio Development pilot and its acceptance evidence.

The V1 pilot remains evidence that Standard Copilot Studio authoring, packaging, clone/list verification, and functional testing can work through PAC in the Development environment. V2 does not invalidate that evidence.

## 3. Known organizational constraints

These constraints are architecture inputs, not advisory notes.

### 3.1 Allowed and available

- Microsoft 365 Copilot is available for internal use.
- Work IQ can be enabled and used in Microsoft 365 Copilot.
- Specialized agents built for the organization can be invoked from Microsoft 365 Copilot alongside Work IQ context where the product supports that composition.
- Standard Copilot Studio is an allowed build target.
- Power Automate and Dataverse are allowed when requirements justify them and Development access is verified.
- Declarative agents for Microsoft 365 Copilot are an allowed and preferred target when they satisfy the objective.

### 3.2 Disallowed or unavailable

- GitHub Copilot harness agents are disallowed because the required Copilot Credit funding is not available and cannot be assumed to become available.
- An architecture that requires the GitHub Copilot harness must be redesigned or marked BLOCKED.
- Work IQ embedded in a Copilot Studio agent is currently disallowed because the documented preview integration uses the GitHub Copilot harness and usage-based Copilot Credits.
- AgentFactory must not assume that direct Work IQ MCP/API usage is available merely because Work IQ is available in Microsoft 365 Copilot.

### 3.3 Conditional

Direct Work IQ MCP is optional and conditional. Microsoft currently documents the `retrieve` tool as public preview and requires tenant enablement, delegated Work IQ permission, and usage-based billing/spending policy for Work IQ API calls. AgentFactory must preflight those prerequisites before selecting direct Work IQ MCP as a build dependency.

If direct Work IQ MCP is unavailable, AgentFactory may still design agents intended to be composed with Work IQ at the Microsoft 365 Copilot host level.

Authoritative current references:

- Work IQ `retrieve`: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/mcp/retrieve
- Work IQ retrieval migration/billing notes: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/mcp/migrate-retrieval-api

## 4. Architecture selection model

V2 removes the V1 rule that Standard Copilot Studio is the default for every agent.

The default is now: **select the least-complex viable agent architecture after requirements, licensing, hosting, and automation constraints are known.**

### 4.1 Preferred routing

| Requirement pattern | Preferred architecture | Primary build path |
|---|---|---|
| Internal knowledge/expertise agent in Microsoft 365 Copilot | Declarative agent | Work IQ Dev Tools; Agents Toolkit fallback |
| Specialized agent intended to be invoked from Microsoft 365 Copilot | Declarative agent | Work IQ Dev Tools |
| Declarative agent with supported API or remote MCP actions | Declarative agent | Work IQ Dev Tools or Agents Toolkit |
| Structured, predictable conversation or Power Platform-heavy workflow | Standard Copilot Studio | PAC CLI / PAC MCP |
| Deterministic approvals, branching, retries, multiple connectors, workflow state | Standard Copilot Studio + Power Automate | PAC + Power Automate |
| Structured persistent business data/relationships/security | Add Dataverse only when justified | Dataverse + PAC solution tooling |
| Custom orchestration, hosting, models, or multi-channel runtime required | Custom engine | Microsoft 365 Agents SDK; exception path |
| Any design requiring GitHub Copilot harness | Disallowed | Redesign or BLOCK |
| Copilot Studio agent requiring embedded Work IQ preview | Disallowed under current constraints | Prefer host-composed Work IQ or redesign |

Microsoft currently recommends Work IQ Dev Tools as the pro-code starting point for declarative agents when its supported lifecycle fits, with Microsoft 365 Agents Toolkit used when lower-level control or capabilities outside WIQD scope are required:

- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-tool-comparison
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/choose-plugin-development-tools

### 4.2 Buildability classification

Every architecture decision must include one of these values:

- `CLOUD_BUILDABLE` — implementation, validation, and packaging can be performed from the supported command/tool surfaces available to the Codex environment.
- `CLOUD_BUILDABLE_WITH_MANUAL_DEPLOY` — build and validation are automatable, but a final tenant/admin/publish step must be performed manually.
- `PORTAL_STEP_REQUIRED` — one or more required build/configuration operations are only available through a portal or other unavailable interactive surface; record the exact step before implementation.
- `BLOCKED` — a hard licensing, permission, tenant, capability, or policy dependency makes the approved design nonviable.

AgentFactory must identify this classification during architecture, not after implementation begins.

## 5. Work IQ model

V2 treats Work IQ as three distinct capabilities.

### 5.1 Host-composed Work IQ

`HOST_COMPOSED_WORKIQ = AVAILABLE`

The preferred no-new-credit pattern is:

```text
Microsoft 365 Copilot
  + Work IQ context
  + specialized AgentFactory-built agent
  + user request
```

The specialized agent does not need embedded Work IQ solely to benefit from Work IQ context when the Microsoft 365 Copilot host supports composing them.

### 5.2 Copilot Studio embedded Work IQ

`COPILOT_STUDIO_EMBEDDED_WORKIQ = DISALLOWED`

Current Microsoft documentation ties the Copilot Studio Work IQ preview to the GitHub Copilot harness and Copilot Credits. AgentFactory must not select this path under current organizational constraints.

### 5.3 Direct Work IQ MCP

`DIRECT_WORKIQ_MCP = CONDITIONAL`

When available, `retrieve` is preferred for gathering grounding evidence that the caller will reason over. It is not a substitute for entity reads/writes or intentional delegation. AgentFactory must discover the live MCP tool schema and must not hard-code a copied preview schema.

Direct Work IQ MCP is useful for:

- requirements/context discovery from permitted Microsoft 365 data;
- evidence gathering during design or verification;
- source-aware grounding and citation metadata;
- optional agent implementations that explicitly require Work IQ MCP and pass billing/permission preflight.

It is not a mandatory dependency of AgentFactory.

## 6. Skill architecture

V2 keeps custom skills small and organization-specific. Rapidly changing Microsoft platform knowledge stays in Microsoft-maintained skills, MCP servers, CLIs, and current documentation.

### 6.1 Custom AgentFactory skills

Initial custom stack:

1. `agentfactory`
   - objective intake;
   - constraint application;
   - architecture selection;
   - specification and approval lifecycle;
   - capability routing;
   - build/resume orchestration.

2. `agent-spec-verifier`
   - spec integrity;
   - requirement/evidence coverage;
   - ordered verification;
   - remediation routing;
   - SHIP / ITERATE / BLOCK verdict.

3. `power-platform-resilience`
   - identity/authentication;
   - least privilege;
   - consequential side effects and confirmation;
   - retries/idempotency/partial failure/recovery;
   - permissions/error behavior;
   - secrets/configuration/observability/DLP review.

`m365-solution-router` should be a separate skill only if the architecture-routing rules become too large to keep `agentfactory` focused. Do not create it preemptively.

### 6.2 Microsoft-maintained skills

Use current Microsoft-maintained skills when available for:

- Microsoft documentation lookup and code references;
- declarative-agent development;
- Microsoft 365 agent evaluation;
- other platform-specific workflows where Microsoft publishes a maintained skill.

Do not duplicate Microsoft command syntax, schemas, or product documentation inside custom AgentFactory skills unless a stable organization-specific rule is required.

## 7. MCP architecture

### 7.1 Required

#### Microsoft Learn MCP

Purpose: current Microsoft platform documentation and code-reference retrieval.

AgentFactory must prefer first-party current documentation when a platform capability, API, command, schema, licensing rule, preview state, or prerequisite could have changed.

#### PAC CLI built-in MCP

Purpose: natural-language access to current PAC command capabilities for Power Platform/Copilot Studio operations where appropriate.

Microsoft documents the built-in server as:

```text
pac copilot mcp --run
```

Reference: https://learn.microsoft.com/en-us/power-platform/developer/howto/use-mcp

PAC CLI remains usable directly; MCP is a supported interface, not a mandatory wrapper around every command.

### 7.2 Optional

#### Work IQ MCP

Endpoint currently documented as:

```text
https://workiq.svc.cloud.microsoft/mcp
```

Status: optional/conditional due to billing, permission, and tenant-policy requirements.

### 7.3 Avoid by default

Do not add MCP servers merely because they exist. Add a server only when it materially improves an approved build path and does not duplicate a simpler native/CLI route.

## 8. Toolchain

The AgentFactory Codex Cloud environment should support the smallest reusable toolchain needed for the approved lanes.

### Baseline

- Git
- Python 3
- Node.js 24+
- Power Platform CLI (PAC)
- Work IQ Dev Tools (WIQD)
- Microsoft 365 Agents Toolkit CLI (`atk`)

### On demand

- Microsoft 365 Agents SDK dependencies only when a custom-engine architecture is approved.
- PowerShell 7 where required by WIQD on the selected environment/OS.

Do not install large SDK/framework stacks globally when no approved architecture needs them.

## 9. Repository layout

V2 should use one canonical Codex-facing skill location and avoid unnecessary compatibility layers.

Target layout:

```text
AgentFactory/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── agentfactory/
│       ├── agent-spec-verifier/
│       ├── power-platform-resilience/
│       └── <selected Microsoft-maintained skills or installation metadata>
├── config/
│   ├── constraints.yaml
│   └── capability-registry.yaml
├── docs/
│   ├── architecture.md
│   ├── supported-platforms.md
│   ├── workflow.md
│   ├── specs/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── scripts/
├── templates/
└── tests/
```

The existing `.github/skills/` content may be migrated to `.agents/skills/` during implementation. The current `.agents/skills` symlink is not itself proof of a sync failure; the V2 change is to remove indirection because this repository's target host is Codex.

## 10. AGENTS.md policy

The root `AGENTS.md` must be repaired. The current file contains the literal shell construction used to create it rather than only the intended guidance.

V2 `AGENTS.md` should be short and contain only:

- repository purpose;
- mandatory architecture/constraint check before implementation;
- references to the authoritative design/spec/policy files;
- rule to use current Microsoft first-party documentation for mutable platform facts;
- Development-by-default and explicit Production/org-publication approval boundaries;
- verification command(s);
- prohibition on invented tenant IDs, environment IDs, schemas, credentials, URLs, connector operations, permissions, or verification results.

Detailed procedures belong in skills and references, not in the root instruction file.

## 11. Constraint file

Create `config/constraints.yaml` as machine-readable architecture input.

Minimum fields:

```yaml
organization:
  purpose: internal_m365_agents
  development_environment_only_by_default: true

licensing:
  github_copilot_harness: disallowed
  usage_based_copilot_credits_for_agent_builds: unavailable

work_iq:
  m365_copilot: available
  host_composition_with_agents: available
  copilot_studio_embedded: disallowed
  direct_mcp_api: conditional

agent_architectures:
  declarative_agent: preferred_when_suitable
  copilot_studio_standard: allowed
  github_copilot_harness: disallowed
  custom_engine: exception_only

deployment:
  production_requires_explicit_approval: true
  organization_publish_requires_explicit_approval: true

architecture:
  prefer_native_before_custom: true
  verify_current_microsoft_docs_before_mutable_platform_decisions: true
```

Do not include tenant secrets or credentials.

## 12. Capability registry V2

Replace the stale single-dimension provider status model with separate evidence dimensions.

For each capability/provider record, track at least:

- `microsoft_support_status`
- `preview_status`
- `organization_policy_status`
- `licensing_status`
- `codex_cloud_tool_status`
- `authentication_status`
- `tenant_execution_status`
- `last_verified_at`
- `evidence`
- `limitations`
- `fallback`

Example conceptual record:

```yaml
workiq.retrieve:
  microsoft_support_status: supported_preview
  organization_policy_status: allowed_if_enabled
  licensing_status: conditional
  codex_cloud_tool_status: not_yet_verified
  authentication_status: not_yet_verified
  tenant_execution_status: not_yet_verified
  fallback: host_composed_workiq
```

Do not interpret documentation discovery as proof of authentication or live tenant execution.

## 13. Workflow changes

Preserve the V1 state machine unless implementation demonstrates a specific reason to change it.

Add these architecture outputs before specification drafting:

- selected agent type/runtime;
- selected authoring/build tool;
- buildability classification;
- hard constraints applied;
- optional capabilities and fallbacks;
- licensing/tenant assumptions that must be verified during preflight.

Preflight must verify only the capabilities selected by the approved architecture.

## 14. Verification model

Continue the V1 ordered verification model:

1. spec integrity;
2. requirement coverage;
3. platform validation;
4. functional verification;
5. evaluation;
6. resilience review;
7. verdict.

Use Microsoft evaluation tooling where supported. For deployed declarative agents, Microsoft currently recommends the Work IQ Dev Tools evaluation workflow as a guided route; use lower-level evaluation tooling only when necessary.

Reference: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/evaluation-overview

Do not invent quality thresholds.

## 15. Cloud environment design

Create a fresh Codex Cloud environment named `AgentFactory` after the V2 repo cleanup is merged/available on the target branch.

The environment's sole repository should be `Ryan9876/AgentFactory` unless a build explicitly needs another repository.

The environment setup should:

- install the baseline toolchain;
- configure required MCP servers through supported Codex mechanisms;
- avoid persistent secrets in the repository;
- make required skills discoverable from the repository;
- run deterministic self-checks after setup;
- keep preview/optional Work IQ MCP disabled until its prerequisites are explicitly verified.

The repository must remain the source of truth for AgentFactory policy and skills. Cloud-environment setup should contain installation/bootstrap logic, not duplicate the architecture policy.

## 16. First-build readiness gates

Before using AgentFactory for a real organizational agent, run a capability acceptance pass.

Required checks:

| Capability | Required result for first build |
|---|---|
| Repository checkout/branch identity | PASS |
| Root `AGENTS.md` parsing/guidance | PASS |
| Repository skill discovery | PASS |
| Microsoft Learn/current-doc route | PASS |
| WIQD CLI installation/help | PASS |
| Agents Toolkit CLI installation/help | PASS |
| PAC CLI installation/help | PASS |
| PAC MCP discovery/start path | PASS or documented direct-CLI fallback |
| M365/PAC authentication | PASS for selected Development environment |
| Development environment identification | PASS |
| Work IQ MCP | PASS or explicitly CONDITIONAL/BLOCKED; not a first-build dependency |

## 17. First build

The first V2 build should be a disposable, low-risk **declarative knowledge agent** for Microsoft 365 Copilot.

Purpose of the first build is to validate the new preferred lane, not to deliver a production business solution.

Acceptance criteria:

- AgentFactory classifies it as a declarative agent without unnecessary Copilot Studio, Power Automate, Dataverse, Work IQ MCP, or custom code.
- Build path uses WIQD if supported by the environment; Agents Toolkit is the documented fallback.
- Source files are committed and reproducible.
- Static/package validation succeeds.
- Development provisioning or supported sideload/test succeeds when tenant/auth prerequisites permit.
- Representative grounded and unsupported prompts are tested.
- Evidence is captured in the standard AgentFactory traceability/acceptance flow.
- No Production mutation or organization-wide publication occurs.

After that passes, run two additional golden-path acceptance builds before declaring the Factory broadly operational:

1. Standard Copilot Studio knowledge agent using PAC.
2. Standard Copilot Studio agent with one simple deterministic action/workflow.

## 18. Non-goals

V2 does not build:

- a custom AgentFactory UI;
- a custom agent runtime;
- a custom Microsoft Graph/RAG abstraction;
- a custom Work IQ wrapper;
- a custom PAC wrapper;
- browser automation as a required platform authoring path;
- a generalized CI/CD platform;
- a generic LangChain/LangGraph framework layer;
- GitHub Copilot harness agents under the current organization constraints.

## 19. Implementation sequence

Implementation should be decomposed into these stages:

1. Preserve V1 baseline and create V2 working branch.
2. Repair root `AGENTS.md`.
3. Establish canonical `.agents/skills/` layout and migrate the three custom skills without changing their behavior unnecessarily.
4. Add `config/constraints.yaml` and capability-registry V2 schema/data.
5. Update architecture/routing documentation and tests for declarative-first selection and GHCP/embedded-Work-IQ blocking.
6. Add/install Microsoft-maintained documentation and M365-agent skills through the supported mechanism chosen during implementation.
7. Define Codex Cloud bootstrap/setup for Microsoft Learn MCP, WIQD, Agents Toolkit, PAC, and PAC MCP/direct fallback.
8. Run local/static repository verification.
9. Create the fresh Codex Cloud `AgentFactory` environment.
10. Run capability acceptance checks.
11. Execute the disposable declarative-agent first build.
12. Record evidence and decide whether to proceed to the remaining golden-path builds.

## 20. Success criteria

AgentFactory V2 is ready for its first real organizational build when:

- architecture selection is constraint-aware and does not default blindly to Copilot Studio;
- GitHub Copilot harness and embedded Copilot Studio Work IQ designs are reliably blocked under current constraints;
- host-composed Work IQ is recognized as an available design pattern;
- direct Work IQ MCP is treated as optional/conditional rather than assumed;
- skills load consistently in the Codex target host;
- Microsoft mutable platform facts are resolved through current first-party sources/tool discovery;
- declarative-agent, Standard Copilot Studio, and Power Platform lanes have explicit tools and fallbacks;
- cloud buildability/manual-step status is known before implementation;
- the disposable declarative-agent first build passes its applicable validation and evidence gates;
- the repository can resume and verify work without relying on hidden conversational state.

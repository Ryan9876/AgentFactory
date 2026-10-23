# Probe A — Copilot Studio MCP lifecycle

**Date:** 2026-10-22  
**Target:** GTM PowerApp - Development (environment ID `763580d9-7ae2-ef77-ac55-8b393205010f`)  
**Outcome:** `COPILOT_STUDIO_MCP_LIFECYCLE_BLOCKED`

This is a bounded Development qualification record. It separates successful runtime-qualified reads from schema-advertised actions and operations that were not attempted. No agent was created, modified, published, tested, evaluated, or deleted.

## Read-only preflight

A fresh Copilot Studio MCP process used the supported sign-in flow through Chrome Stable and the visible `AgentFactory` profile. The intended organizational account and exact Development environment were verified, and the live tool catalog loaded. The Microsoft guide describes this sign-in/environment-selection flow and notes that tools depend on account permissions and environment: [Copilot Studio MCP guide](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/copilot-studio-mcp).

| Operation | Result | Evidence boundary |
|---|---|---|
| Fresh-process sign-in and Development selection | **RUNTIME_QUALIFIED** | MCP status identified the intended account and Development environment. Authentication was repeated for each fresh server process. |
| Connection visibility | **RUNTIME_QUALIFIED** | `discover_resources.list_connections` returned three entries. |
| Workflow visibility | **RUNTIME_QUALIFIED** | `manage_workflows.list` returned two workflows. |
| Agent visibility | **BLOCKED** | `manage_agents.list` failed because the Development identity lacks `prvReadbot`. This remains a tenant permission boundary. |

The local package documentation says credentials are process-local and discarded when the server exits. Browser interaction was used for sign-in and account selection. No PAC or Copilot Studio portal fallback was used.

## Catalog discovery, not lifecycle qualification

The live `tools/list` schema advertised these operation families:

- **Agents:** `get_definition`, `get_evaluation_run`, `get_evaluation_suite`, `get_publish_status`, `get_summary`, `list`, `list_evaluation_suites`, `search`; mutations `create`, `create_evaluation_suite`, `delete`, `generate_evaluation_cases`, `publish`, `start_evaluation_run`, `update`; and `validate`, `test`.
- **Workflows:** `get_definition`, `get_run`, `get_summary`, `inspect_run`, `list`, `list_run_actions`, `list_runs`, `search`; mutations `create`, `delete`, `publish`, `set_enabled`, `update`; and `validate`, `test`.
- **Discovery:** `list_connections`, `read_detail_resource`, `callable_workflows`, `connectable_agents`, `foundry_knowledge_bases`, `browse_parameter_tree`, `describe_actions`, `get_operation_schema`, `resolve_dynamic_schema`, `resolve_parameter_values`, `search_operations`, and `search_operations_with_schemas`.
- **Evaluation:** `create_evaluation_suite`, `generate_evaluation_cases`, `start_evaluation_run`, `get_evaluation_run`, and `get_evaluation_suite`.
- **Workflow diagnostics:** `get_run`, `inspect_run`, `list_runs`, and `list_run_actions`.

The live action enums were inspected, but focused per-action parameter contracts through `describe_actions` were not retrieved. These catalog entries are discovery evidence only; they do not establish that an operation is authorized, executable, or behaviorally correct in this tenant.

## Lifecycle decision

**Create, update, validate, test, evaluate, and cleanup remain NOT_TESTED.** Since agent inventory was blocked, the preflight could not verify a unique disposable name, rule out a name collision, or prove cleanup. No resource was created, so no cleanup was needed. Stop before creation; do not work around the missing permission.

Work Radar-era lifecycle constraints remain in force. Prefer Copilot Studio MCP for the lifecycle only after `prvReadbot` is resolved and a unique, reversible create-to-cleanup path can be established. Use PAC as a supported fallback only for operations it exposes. Never bypass tenant permissions. **Probe B should wait** until the inventory/permission boundary is resolved.

No tenant permissions, policies, billing, Production, or publication settings were changed. The separate GitHub push blocker is credential setup on the Mac; complete `gh auth login --hostname github.com --git-protocol https --web` there before retrying the push. Do not send credentials or codes in chat.


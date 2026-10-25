# Lab D — Direct Work IQ MCP

**Date:** 2026-10-23
**Host:** Desktop Local
**Intended identity:** `smithr@opentext.com`
**Disposition:** `CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT` for current route feasibility; all direct authentication and runtime operations remain `NOT_TESTED`.

## Assessment

The existing capability registry and program premise classify the direct Work IQ MCP route as unavailable under the fixed tenant, permission, service-principal, enablement, and Copilot Credits/billing constraints. This assessment applies that instruction without retrying the boundary. The repository does not contain dated tenant-specific observations for each prerequisite, so their individual current states are **not reverified** here. No sign-in, consent, enablement, billing, or `tools/list` attempt was repeated.

Current [Microsoft Learn prerequisites for Work IQ MCP retrieve](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/mcp/retrieve) require tenant enablement, Copilot Credits billing and a Work IQ API spending policy, a client application with delegated `WorkIQAgent.Ask`, and an enabled MCP policy where applicable. Microsoft's [retrieval migration guidance](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/mcp/migrate-retrieval-api) identifies an unprovisioned Work IQ service principal and missing consent/spending policy among direct API blockers. These current docs support keeping this route separate from Microsoft 365 Copilot's built-in host context; they do not establish current tenant runtime availability.

## Evidence boundary

| Operation | Evidence state | Result |
|---|---|---|
| Current fixed-prerequisite assessment | `BLOCKED` | The recorded program premise rules out selecting this route; underlying individual tenant facts are not reverified in this session. |
| Direct Work IQ authentication | `NOT_TESTED` | Not repeated because prerequisites already rule out the route. |
| Live Work IQ MCP catalog | `NOT_TESTED` | No live schema fetched; schema discovery would not cure prerequisite constraints. |
| `retrieve` operation | `NOT_TESTED` | No call made. |
| Evaluation or runtime grounding | `NOT_TESTED` | No call made. |
| Cleanup | `NOT_TESTED` / unnecessary | No connection, client, or tenant resource was created. |

The supported alternative is Lab C's host-composed Work IQ, which uses Microsoft 365 Copilot's own context and does not prove or require direct Work IQ MCP. Lab C still needs actual host and specialized-agent runtime evidence.

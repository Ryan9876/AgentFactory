# Supported architecture and capability status

Architecture selection is requirements-led and chooses the least-complex viable supported path. Declarative agents are preferred for suitable internal Microsoft 365 knowledge/expertise scenarios. Standard Copilot Studio and Power Platform remain supported when requirements justify them; custom engine is exception-only.

| Capability | Policy/status | Evidence boundary |
|---|---|---|
| Declarative agents | Preferred when suitable; WIQD primary, Agents Toolkit fallback | Tool install, auth, tenant execution, provisioning, and runtime require separate checks |
| Standard Copilot Studio | Allowed for structured/Power Platform-heavy needs | Existing V1 pilot is historical Development evidence, not proof for a new host/target |
| GitHub Copilot harness (GHCP) | **Disallowed** under current organization constraints | Redesign or block any dependency on it |
| Copilot Studio embedded Work IQ | **Disallowed** while requiring GHCP/Copilot Credits | Host-composed Work IQ is a separate available pattern |
| Direct Work IQ MCP | Conditional; not required for first build | Verify current docs, tenant enablement, delegated permission, and billing policy before selecting |
| Power Automate / Dataverse | Allowed when justified | Verify selected Development access and ownership/security requirements |
| Microsoft evaluation | Use supported current path | No quality threshold may be invented |

Mutable Microsoft capabilities must be checked against current first-party documentation and tool discovery. Documentation discovery is not authentication, cloud synchronization, or runtime evidence. See `config/capability-registry.yaml` and `docs/installation.md` for host-specific evidence.

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

## Execution hosts and browser surfaces

Host selection follows capability support in `config/capability-registry.yaml`, not one global preference.

| Work | Preferred surface | Fallback and stop behavior |
|---|---|---|
| Repository/source engineering, isolated reproducible tests, package/build validation | Codex Cloud | Desktop Local when Cloud is unavailable and the operation is supported there |
| Public Microsoft Learn/docs or public source research without tenant identity | Either Codex Cloud or Desktop Local | Use the next available documented surface |
| Microsoft interactive authentication; PAC/PAC MCP; authenticated Power Platform/Dataverse Development; Copilot Studio MCP; Agents Toolkit; Developer Portal; Graph; WIQD; Microsoft tenant runtime qualification | Desktop Local | Use an alternate host only when it supports the capability and the preferred host itself is unavailable. Stop for auth, MFA, consent, permission, admin/security policy, licensing, billing, or publication blockers. |
| Persistent local Microsoft identity and real-session verification | Regular Chrome Stable, visible profile `AgentFactory` | Profile directory is discovered by visible name; do not assume its identifier or persist a user-specific path. Browser login state does not prove unattended authentication. |
| Deterministic UI regression | Chrome for Testing with a disposable isolated user-data directory | Never use the authenticated `AgentFactory` profile as a generic regression profile. |

Within a supported capability, prefer MCP, CLI, or API/SDK for implementation; use browser UI for authentication, verification, or a supported fallback. A tool or schema listing remains discovery evidence and does not establish `RUNTIME_QUALIFIED`.

Known Development tenant/policy findings are blockers, not host failures: agent inventory lacks `prvReadbot`; custom-app upload/sideload is disabled; WIQD's upstream Work IQ service principal is missing; direct Work IQ MCP permissions, tenant enablement, and billing remain unverified. Keep these separate from tool availability and runtime qualification.

Probe A partially runtime-qualified Copilot Studio MCP sign-in/environment selection and connection/workflow list reads. Agent inventory remains blocked by `prvReadbot`; advertised mutation/evaluation operations remain untested. See [the Probe A evidence record](qualification-labs/copilot-studio-mcp-probe-a.md).

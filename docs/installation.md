# Installation and first-build readiness

The repository is Codex-first. Canonical skills are in `.agents/skills/`. Run `scripts/bootstrap_codex_cloud.sh` to install local prerequisites; it creates `.venv/` for Python dependencies and does not authenticate to Microsoft or mutate a tenant. Then run `PATH=.venv/bin:$PATH python3 scripts/readiness_check.py --json`.

## Desktop Local readiness

For Microsoft tenant work on the local workstation, first create the repository's Python environment and run the separate read-only local check:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PATH=.venv/bin:$PATH python3 scripts/local_readiness_check.py --json
```

This local path is separate from `scripts/bootstrap_codex_cloud.sh` and `scripts/readiness_check.py`. It checks local execution, Node/.NET, PAC/ATK/WIQD commands, PAC MCP discovery, Copilot Studio MCP package availability, regular Chrome Stable, and the Chrome profile directory mapped to visible name `AgentFactory`. It invokes only supported status/help/discovery commands; it never starts an MCP server or initiates sign-in. PAC authentication is inspected before PAC MCP discovery. The checker emits status and a Chrome profile directory identifier, never the absolute profile path or raw CLI output.

Set `AGENTFACTORY_EXPECTED_UPN` and `AGENTFACTORY_DEVELOPMENT_ENVIRONMENT_ID` in the local shell to compare the active row in `pac auth list` with the intended identity and to verify the Development environment ID and URL through `pac env list --filter`. The active PAC profile URL must match the URL returned for the configured environment ID. This avoids interactive `pac auth who` prompts in a headless readiness check. The checker uses `atk auth list` only to report whether the account is connected in Agents Toolkit; it does not infer which ATK account is active. It reports `NOT_TESTED` when an expected value is absent; it does not infer identity from installed tools, profile names, or organization IDs. Verify the browser account through supported visible browser state. Readiness reports do not perform login, change profile selection, or mutate Microsoft resources.

Tooling follows current first-party setup surfaces: [Work IQ Dev Tools installation](https://microsoft.github.io/wiqd/getting-started/installation/) uses Microsoft's supported installer, not an assumed npm package; [Agents Toolkit CLI](https://learn.microsoft.com/microsoftteams/platform/toolkit/microsoft-365-agents-toolkit-cli) is distributed from npm; [PAC installation](https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction) uses Microsoft's documented .NET tool. [Microsoft Learn MCP](https://github.com/MicrosoftDocs/mcp) documents `codex mcp add microsoft-learn --url https://learn.microsoft.com/api/mcp`. Bootstrap skips optional WIQD host-plugin setup, does not configure Work IQ MCP, and does not authenticate.

The checker reports repository/tool-host facts and explicitly leaves Microsoft authentication and Development environment identification blocked until observed. Never treat discovery or installation as authentication, tenant execution, cloud synchronization, or runtime qualification. The V1 pilot in `docs/v1-acceptance.md` remains preserved historical evidence and does not qualify a new Codex host.

First build is not yet authorized by repo acceptance alone. Follow `docs/first-build.md` only after readiness and approved project requirements pass. Handle MFA, interactive consent/terms, administrator decisions, and explicit publication approval at their actual boundary; automate every supported safe step and try supported fallbacks first.

## Codex Cloud bootstrap and shell activation

The bootstrap provisions .NET 10 through Microsoft's non-admin CI installer when
its local SDK is absent. It uses the official builds feed, keeps TLS verification
on, and needs no sudo. Tools and caches live outside the checkout in
`/workspace/agentfactory-cloud` by default; set `AGENTFACTORY_TOOLS_DIR` to another
writable absolute directory before bootstrap if needed. This supports a
read-only home directory. Python dependencies remain in the ignored `.venv/`.

From `/workspace/AgentFactory`, use:

```sh
bash --noprofile --norc scripts/bootstrap_codex_cloud.sh
source scripts/cloud_env.sh
python3 scripts/readiness_check.py --json
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
git diff --check
```

Source `scripts/cloud_env.sh` in each new shell. It exports absolute paths,
`DOTNET_ROOT`, .NET tool paths, writable CLI/package caches, and a private runtime
directory for .NET named mutexes. It preserves HOME, injected authentication,
proxy settings, CA trust, and TLS verification.

PAC uses the supported .NET tool package in a writable tool directory. If that
installation fails, bootstrap verifies Microsoft's documented
`dnx Microsoft.PowerApps.CLI.Tool --yes help` route before creating a local
`pac` launcher. `pac copilot mcp` discovers the server; `pac copilot mcp --run`
starts it. Help/discovery is distinct from an MCP handshake or tenant execution.

WIQD uses the current `https://aka.ms/wiqd/install.sh` installer, never an assumed
npm installation command. The current installer requires interactive EULA
acceptance and can exit before installing in unattended sessions. Bootstrap does
not accept terms or configure host plugins. Verified Agents Toolkit CLI execution
provides the supported declarative fallback; missing WIQD alone does not block
first-build tooling. `wiqd doctor` runs only after a successful WIQD install.
Azure/tenant provisioning prerequisites must be assessed when that lane is used.

Microsoft Learn MCP uses `codex mcp add microsoft-learn --url
https://learn.microsoft.com/api/mcp`. When global Codex configuration cannot be
written, `bash scripts/codex_with_learn.sh <codex arguments>` supplies the supported
per-invocation configuration override without replacing managed settings or
credentials. The readiness checker uses the same override. A listed MCP server
proves configuration only; live protocol and search checks are separate evidence.

Authentication stays outside bootstrap. PAC device-code sign-in and ATK browser
sign-in stop at user-presence/MFA/consent boundaries. ATK additionally needs write
access to its user-local `.fx` state. Never enable cleartext secret caching to
work around a host limitation. Readiness remains blocked until Microsoft access
and a Development target are independently verified.

First-party references:

- [.NET non-admin CI installer](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-install-script)
- [Agents Toolkit CLI](https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/microsoft-365-agents-toolkit-cli)
- [PAC installation](https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction)
- [PAC one-shot execution](https://learn.microsoft.com/en-us/power-platform/developer/howto/dnx-cli)
- [PAC MCP](https://learn.microsoft.com/en-us/power-platform/developer/howto/use-mcp)
- [Microsoft Learn MCP](https://github.com/MicrosoftDocs/mcp)

### Bootstrap decision and validation evidence

The path-of-least-resistance assessment is **Configure**: retain Microsoft's
supported CLIs and installers, repair environment initialization, and use the
already-supported ATK lane when unattended WIQD installation reaches consent.
No agent architecture, tenant policy, or product requirement changes are needed.
Buildability is limited by sign-in and Development identification, not source
implementation. No tenant mutation or disposable agent build was performed.

Validated in Codex Cloud: Python 3.12.14, Node 24.19.0, .NET SDK 10.0.402
(`--version` and `--list-sdks`), ATK 1.1.18 help, PAC 2.14.1 help, PAC MCP initialize
and enumeration of 284 tools, and Microsoft Learn MCP initialize, tool listing,
and a successful documentation search. Bootstrap completed from a shell without
profile/rc initialization. These are local tool/protocol checks, not Microsoft
365 authentication, cloud synchronization, or runtime qualification.

Rollback is limited to this branch's bootstrap/readiness changes and the external
local tool directory; authentication state must be preserved separately and is
never committed. Stop at TLS/package verification failures, explicit network
policy denials, user-presence consent, and tenant authority boundaries. No network
allowlist expansion was required for the verified tool path.

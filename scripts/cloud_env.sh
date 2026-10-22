#!/usr/bin/env bash
# Source from any working directory; do not change HOME or injected proxy/auth.
AF_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export AGENTFACTORY_TOOLS_DIR="${AGENTFACTORY_TOOLS_DIR:-$AF_REPO_ROOT/../agentfactory-cloud}"
export DOTNET_ROOT="$AGENTFACTORY_TOOLS_DIR/dotnet"
export DOTNET_CLI_HOME="$AGENTFACTORY_TOOLS_DIR/state/dotnet"
export NUGET_PACKAGES="$AGENTFACTORY_TOOLS_DIR/state/nuget"
export NPM_CONFIG_PREFIX="$AGENTFACTORY_TOOLS_DIR/npm"
export NPM_CONFIG_CACHE="$AGENTFACTORY_TOOLS_DIR/state/npm"
# .NET named mutexes need a writable, private runtime directory on this host.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-$AGENTFACTORY_TOOLS_DIR/state/runtime}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$AGENTFACTORY_TOOLS_DIR/state/data}"
export DOTNET_NOLOGO=1
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_GENERATE_ASPNET_CERTIFICATE=false
export PATH="$AF_REPO_ROOT/.venv/bin:$AGENTFACTORY_TOOLS_DIR/bin:$DOTNET_ROOT:$DOTNET_ROOT/tools:$NPM_CONFIG_PREFIX/bin:$PATH"
unset AF_REPO_ROOT

#!/usr/bin/env bash
# Supported Codex CLI config override also works with a read-only CODEX_HOME.
# Preserve all inherited credentials and managed configuration.
exec codex -c 'mcp_servers.microsoft-learn.url="https://learn.microsoft.com/api/mcp"' "$@"

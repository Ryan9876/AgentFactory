#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }
major_version() { "$1" --version 2>/dev/null | head -n 1 | sed -E 's/^[^0-9]*([0-9]+).*/\1/'; }
require_major() {
  local tool="$1" minimum="$2" actual
  command -v "$tool" >/dev/null 2>&1 || fail "$tool $minimum or later is required; install it and rerun bootstrap."
  actual="$(major_version "$tool")"
  [[ "$actual" =~ ^[0-9]+$ ]] || fail "Could not determine $tool version."
  (( actual >= minimum )) || fail "$tool $minimum or later is required; found $actual."
}

python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install -r requirements.txt
require_major node 24
require_major dotnet 10

# Official WIQD installer; plugin auto-configuration is skipped to keep host
# changes explicit. The installer may update its CLI and VS Code extension.
curl -fsSL https://aka.ms/wiqd/install.sh | bash -s -- --skip-plugin
wiqd --version
wiqd doctor

npm install --global @microsoft/m365agentstoolkit-cli@latest
dotnet tool update --global Microsoft.PowerApps.CLI.Tool || dotnet tool install --global Microsoft.PowerApps.CLI.Tool
export PATH="$HOME/.dotnet/tools:$PATH"
atk -h
pac help

# The Microsoft Learn MCP endpoint is documented for Codex. Do not configure
# Work IQ MCP here; it is a separate conditional dependency.
if command -v codex >/dev/null 2>&1; then
  if ! codex mcp list | rg -q 'microsoft-learn'; then
    codex mcp add microsoft-learn --url https://learn.microsoft.com/api/mcp
  fi
  codex mcp list
else
  printf 'NOTICE: Codex CLI unavailable; configure Microsoft Learn MCP in the Codex environment when available.\n'
fi

printf 'Bootstrap complete. Microsoft authentication and Development target verification remain separate readiness gates.\n'

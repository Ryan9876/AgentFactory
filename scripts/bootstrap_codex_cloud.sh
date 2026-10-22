#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# All mutable tool state stays outside the checkout, even with read-only HOME.
source "$ROOT/scripts/cloud_env.sh"
mkdir -p "$AGENTFACTORY_TOOLS_DIR/bin" "$DOTNET_CLI_HOME" "$NUGET_PACKAGES" "$NPM_CONFIG_CACHE" "$XDG_RUNTIME_DIR" "$XDG_DATA_HOME"
chmod 700 "$XDG_RUNTIME_DIR"
fail() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }
major_version() { "$1" --version 2>/dev/null | head -n 1 | sed -E 's/^[^0-9]*([0-9]+).*/\1/'; }
require_major() {
  local tool="$1" minimum="$2" actual
  command -v "$tool" >/dev/null 2>&1 || fail "$tool $minimum or later is required."
  actual="$(major_version "$tool")"
  [[ "$actual" =~ ^[0-9]+$ ]] && (( actual >= minimum )) || fail "$tool $minimum or later is required; found $actual."
}

python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install -r requirements.txt
require_major node 24
if ! "$DOTNET_ROOT/dotnet" --list-sdks 2>/dev/null | grep -Eq '^(1[0-9]|[2-9][0-9])\.'; then
  # Microsoft documents dotnet-install for non-admin CI/cloud setup. The explicit
  # official feed avoids the unnecessary ci.dot.net preview-feed lookup.
  curl -fsSL https://dot.net/v1/dotnet-install.sh -o "$AGENTFACTORY_TOOLS_DIR/dotnet-install.sh"
  bash "$AGENTFACTORY_TOOLS_DIR/dotnet-install.sh" --channel 10.0 --azure-feed https://builds.dotnet.microsoft.com/dotnet --install-dir "$DOTNET_ROOT" --no-path
fi
require_major dotnet 10
dotnet --version
dotnet --list-sdks

npm install --global @microsoft/m365agentstoolkit-cli@latest
atk -h

if ! pac help >/dev/null 2>&1; then
  if ! dotnet tool update --tool-path "$AGENTFACTORY_TOOLS_DIR/bin" Microsoft.PowerApps.CLI.Tool --allow-roll-forward; then
    # Microsoft's documented one-shot PAC path; verify execution before using it.
    dnx Microsoft.PowerApps.CLI.Tool --yes help
    cat > "$AGENTFACTORY_TOOLS_DIR/bin/pac" <<'PAC'
#!/usr/bin/env bash
exec dnx Microsoft.PowerApps.CLI.Tool --yes "$@"
PAC
    chmod 700 "$AGENTFACTORY_TOOLS_DIR/bin/pac"
  fi
fi
pac help
if ! pac copilot mcp; then
  printf 'NOTICE: PAC MCP discovery unavailable; verified direct PAC CLI is the supported fallback.\n'
fi

# Current official installer. Never auto-accept EULAs/terms or modify the host's
# plugins. WIQD failure is not fatal when the verified ATK fallback is available.
if curl -fsSL https://aka.ms/wiqd/install.sh -o "$AGENTFACTORY_TOOLS_DIR/wiqd-install.sh" && bash "$AGENTFACTORY_TOOLS_DIR/wiqd-install.sh" --skip-plugin </dev/null; then
  if ! wiqd --version || ! wiqd doctor; then
    printf 'NOTICE: WIQD doctor needs follow-up; use verified ATK fallback.\n'
  fi
else
  printf 'NOTICE: WIQD installation unavailable (inspect installer output); verified ATK is the declarative fallback. EULA/consent requires user presence.\n'
fi

# Do not configure Work IQ MCP: it is a conditional, separate dependency.
if command -v codex >/dev/null 2>&1; then
  if ! codex mcp list | grep -Fq 'https://learn.microsoft.com/api/mcp'; then
    if ! codex mcp add microsoft-learn --url https://learn.microsoft.com/api/mcp; then
      printf 'NOTICE: Global Codex config is read-only; use the supported per-invocation configuration in scripts/codex_with_learn.sh.\n'
    fi
  fi
  bash "$ROOT/scripts/codex_with_learn.sh" mcp list
else
  printf 'NOTICE: Codex CLI unavailable; Microsoft Learn MCP needs the Codex CLI.\n'
fi
printf 'Bootstrap complete. Microsoft authentication and Development target verification remain separate readiness gates.\n'

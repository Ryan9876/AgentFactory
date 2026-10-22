"""Read-only, honest local readiness report for the first declarative build."""
import argparse
import importlib.util
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    required: bool

def run_checks(command_runner=None, command_finder=None):
    run = command_runner or subprocess.run
    find = command_finder or shutil.which
    checks = []
    def add(name, status, detail, required=True):
        checks.append(CheckResult(name, status, detail, required))
    add("canonical_skills", "PASS" if (ROOT/".agents/skills/agentfactory/SKILL.md").is_file() else "FAIL", "Canonical repo skill layout")
    add("pyyaml", "PASS" if importlib.util.find_spec("yaml") else "FAIL", "PyYAML import availability")
    for name, cmd in (("node", ["node", "--version"]),("dotnet", ["dotnet", "--version"])):
        if not find(cmd[0]):
            add(name, "FAIL", f"{cmd[0]} not installed")
            continue
        try:
            result = run(cmd, capture_output=True, text=True, timeout=10)
            detail = (result.stdout or result.stderr).strip()
            major = int(detail.lstrip("v").split(".")[0])
            minimum = 24 if name == "node" else 10
            add(name, "PASS" if result.returncode == 0 and major >= minimum else "FAIL", f"{detail}; requires {minimum}+")
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            add(name, "FAIL", str(exc))
    for name, command in (("wiqd", ["wiqd", "--help"]), ("atk", ["atk", "-h"]), ("pac", ["pac", "help"])):
        if not find(name):
            add(name, "FAIL", f"{name} not installed")
            continue
        try:
            result = run(command, capture_output=True, text=True, timeout=20)
            output = (result.stdout or result.stderr).strip()
            add(name, "PASS" if result.returncode == 0 else "FAIL", output[:500] or f"{command} returned {result.returncode}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            add(name, "FAIL", f"{command} could not be verified: {exc}")
    for check in checks:
        if check.name in {"wiqd", "atk"}:
            check.required = False
    declarative = any(c.name in {"wiqd", "atk"} and c.status == "PASS" for c in checks)
    add("declarative_build_path", "PASS" if declarative else "FAIL", "WIQD or supported Agents Toolkit fallback must execute")
    for name, relative in (("ryan_agentfactory_stack", ".agents/skills/ryan-agentfactory-stack/SKILL.md"), ("lessons_guardrails", ".agents/skills/agentfactory/references/engineering-guardrails.md")):
        add(name, "PASS" if (ROOT / relative).is_file() else "FAIL", relative)
    if find("pac"):
        try:
            result = run(["pac", "copilot", "mcp"], capture_output=True, text=True, timeout=20)
            add("pac_mcp", "PASS" if result.returncode == 0 else "CONDITIONAL", "MCP command discovery executed; direct PAC CLI remains available", False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            add("pac_mcp", "CONDITIONAL", f"Direct PAC CLI fallback: {exc}", False)
    if find("codex"):
        try:
            result = run(["codex", "-c", 'mcp_servers.microsoft-learn.url="https://learn.microsoft.com/api/mcp"', "mcp", "list"], capture_output=True, text=True, timeout=20)
            detail = (result.stdout or result.stderr).strip()
            found = result.returncode == 0 and "microsoft-learn" in detail.lower() and "https://learn.microsoft.com/api/mcp" in detail
            add("microsoft_learn_mcp", "PASS" if found else "FAIL", detail[:500] or "Microsoft Learn MCP not listed")
        except (OSError, subprocess.TimeoutExpired) as exc:
            add("microsoft_learn_mcp", "FAIL", f"MCP discovery unavailable: {exc}")
    else:
        add("microsoft_learn_mcp", "BLOCKED", "Codex CLI not present in this host; verify MCP in the target Codex environment")
    add("m365_development_auth", "BLOCKED", "Must verify supported Microsoft authentication and positively identify a Development environment in the target host")
    add("direct_workiq_mcp", "CONDITIONAL", "Not a first-build dependency; verify billing, permissions, tenant enablement only if selected", False)
    return checks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checks = [asdict(c) for c in run_checks()]
    if args.json: print(json.dumps(checks, indent=2))
    else:
        for c in checks: print(f"{c['status']}: {c['name']}: {c['detail']}")
    return 1 if any(c["required"] and c["status"] in {"FAIL", "BLOCKED"} for c in checks) else 0

if __name__ == "__main__": raise SystemExit(main())

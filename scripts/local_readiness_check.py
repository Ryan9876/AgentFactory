"""Report Desktop Local Microsoft readiness without exposing authentication data."""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    required: bool = False


def _run(run: Callable, command: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        result = run(command, capture_output=True, text=True, timeout=timeout)
        return result.returncode, (result.stdout or "") + "\n" + (result.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def _run_pac(run: Callable, command: list[str], home: Path, timeout: int = 20) -> tuple[int, str]:
    """Run PAC with the locally installed .NET runtime visible to its launcher."""
    dotnet_root = home / ".dotnet"
    if not (dotnet_root / "dotnet").is_file():
        return _run(run, command, timeout)
    child_env = dict(os.environ)
    child_env["DOTNET_ROOT"] = str(dotnet_root)
    child_env["PATH"] = f"{dotnet_root}{os.pathsep}{child_env.get('PATH', '')}"
    try:
        result = run(command, capture_output=True, text=True, timeout=timeout, env=child_env)
        return result.returncode, (result.stdout or "") + "\n" + (result.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def _find_local_command(name: str, find: Callable, home: Path, run: Callable, env: Mapping[str, str]) -> str | None:
    command = find(name)
    if command:
        return command
    candidates = []
    if name == "dotnet":
        candidates.extend((home / ".dotnet/dotnet", Path("/usr/local/share/dotnet/dotnet"), Path("/opt/homebrew/bin/dotnet")))
    elif name in {"pac", "atk", "wiqd", "copilot-studio-mcp"}:
        candidates.extend((
            home / ".dotnet/tools" / name,
            home / ".local/share/agentfactory-host/node_modules/.bin" / name,
        ))
        installed = next((path for path in candidates if path.is_file() and os.access(path, os.X_OK)), None)
        if installed:
            return str(installed)
        npm = find("npm")
        if npm:
            code, output = _run(run, [npm, "root", "-g"])
            if code == 0 and output.strip():
                candidates.append(Path(output.strip().splitlines()[0]) / ".bin" / name)
    return next((str(path) for path in candidates if path.is_file() and os.access(path, os.X_OK)), None)


def _chrome_binary(system: str, env: Mapping[str, str], find: Callable) -> str | None:
    if system == "Darwin":
        stable = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if stable.is_file():
            return str(stable)
        return find("google-chrome")
    if system == "Windows":
        for base in (env.get("PROGRAMFILES"), env.get("PROGRAMFILES(X86)"), env.get("LOCALAPPDATA")):
            if base:
                candidate = Path(base) / "Google/Chrome/Application/chrome.exe"
                if candidate.is_file():
                    return str(candidate)
        return find("chrome")
    return find("google-chrome-stable") or find("google-chrome")


def _profile_metadata_path(system: str, env: Mapping[str, str], home: Path) -> Path | None:
    if system == "Darwin":
        return home / "Library/Application Support/Google/Chrome/Local State"
    if system == "Windows":
        local = env.get("LOCALAPPDATA")
        return Path(local) / "Google/Chrome/User Data/Local State" if local else None
    return home / ".config/google-chrome/Local State"


def _find_profile_id(path: Path | None, visible_name: str) -> str | None:
    if path is None or not path.is_file():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        profiles = state.get("profile", {}).get("info_cache", {})
        return next((identifier for identifier, metadata in profiles.items() if metadata.get("name") == visible_name), None)
    except (OSError, ValueError, AttributeError):
        return None


def _environment_id_matches(output: str, expected: str) -> bool | None:
    try:
        data = json.loads(output)
    except ValueError:
        return None
    if isinstance(data, dict):
        for key, value in data.items():
            if key.casefold() in {"environmentid", "environment_id"}:
                return str(value).casefold() == expected.casefold()
            if isinstance(value, (dict, list)):
                nested = _environment_id_matches(json.dumps(value), expected)
                if nested is not None:
                    return nested
    elif isinstance(data, list):
        results = [_environment_id_matches(json.dumps(item), expected) for item in data]
        return next((result for result in results if result is not None), None)
    return None


def _identity_matches(output: str, expected: str) -> bool:
    return bool(re.search(rf"(?<![\w.+%-]){re.escape(expected)}(?![\w.+%-])", output, re.IGNORECASE))


def run_local_checks(
    command_runner=None,
    command_finder=None,
    env=None,
    home=None,
    system=None,
    root=ROOT,
):
    run = command_runner or subprocess.run
    find = command_finder or shutil.which
    current_env = dict(os.environ if env is None else env)
    home_path = Path.home() if home is None else Path(home)
    os_name = platform.system() if system is None else system
    checks: list[CheckResult] = []

    def add(name, status, detail, required=False):
        checks.append(CheckResult(name, status, detail, required))

    def _command(name):
        return _find_local_command(name, find, home_path, run, current_env)

    add("local_execution", "PASS" if os_name in {"Darwin", "Linux", "Windows"} else "FAIL", "Local shell platform detected", True)
    versions = (("node", ["node", "--version"], 24), ("dotnet", ["dotnet", "--version"], 10))
    for name, args, minimum in versions:
        executable = _command(args[0])
        if not executable:
            add(name, "FAIL", "Required command is unavailable", True)
            continue
        code, output = _run(run, [executable, *args[1:]])
        version = output.strip().splitlines()[0] if output.strip() else ""
        try:
            major = int(version.lstrip("v").split(".")[0])
        except ValueError:
            major = 0
        add(name, "PASS" if code == 0 and major >= minimum else "FAIL", f"version {version or 'unavailable'}; requires {minimum}+", True)

    chrome = _chrome_binary(os_name, current_env, find)
    if chrome is None:
        add("chrome_stable", "FAIL", "Regular Chrome Stable executable unavailable", True)
    else:
        code, output = _run(run, [chrome, "--version"])
        version = output.strip().splitlines()[0] if output.strip() else ""
        stable = code == 0 and "chrome for testing" not in version.casefold() and "chromium" not in version.casefold()
        add("chrome_stable", "PASS" if stable else "FAIL", f"{version or 'version unavailable'}; Chrome for Testing is not the identity surface", True)
    profile_id = _find_profile_id(_profile_metadata_path(os_name, current_env, home_path), "AgentFactory")
    add("agentfactory_chrome_profile", "PASS" if profile_id else "NOT_TESTED", f"Visible profile AgentFactory maps to {profile_id}" if profile_id else "Visible profile metadata is unavailable", True)
    add("agentfactory_browser_identity", "NOT_TESTED", "Verify intended account through supported browser UI; profile metadata does not establish sign-in")

    for name, args, required in (
        ("wiqd", ["wiqd", "--help"], False),
        ("atk", ["atk", "-h"], True),
        ("pac", ["pac", "help"], True),
    ):
        executable = _command(args[0])
        if not executable:
            add(name, "FAIL" if required else "CONDITIONAL", "Command unavailable", required)
            continue
        code, _ = (_run_pac(run, [executable, *args[1:]], home_path)
                   if name == "pac" else _run(run, [executable, *args[1:]]))
        add(name, "PASS" if code == 0 else "FAIL", "Supported local command responded" if code == 0 else "Command did not complete successfully", required)

    # Inspect only the selected PAC profile before PAC MCP discovery. `auth who`
    # avoids treating an inactive profile in `auth list` as the current identity.
    pac = _command("pac")
    if pac:
        code, pac_auth = _run_pac(run, [pac, "auth", "who"], home_path)
        expected_upn = current_env.get("AGENTFACTORY_EXPECTED_UPN", "").strip()
        if not expected_upn:
            identity_verified = False
            add("pac_identity", "NOT_TESTED", "Set AGENTFACTORY_EXPECTED_UPN to compare supported PAC account status")
        else:
            matched = code == 0 and _identity_matches(pac_auth, expected_upn)
            identity_verified = matched
            add("pac_identity", "PASS" if matched else "BLOCKED", "Supported PAC status matches intended identity" if matched else "PAC status is unavailable or does not match intended identity", True)

        expected_environment = current_env.get("AGENTFACTORY_DEVELOPMENT_ENVIRONMENT_ID", "").strip()
        if not expected_environment:
            add("development_environment", "NOT_TESTED", "Set AGENTFACTORY_DEVELOPMENT_ENVIRONMENT_ID to verify the selected Development target")
        elif not identity_verified:
            add("development_environment", "BLOCKED" if expected_upn else "NOT_TESTED", "PAC identity does not match the configured account" if expected_upn else "Verify the PAC identity before qualifying its Development target", True)
        else:
            env_code, environment = _run_pac(run, [pac, "env", "who", "--json"], home_path)
            matches = _environment_id_matches(environment, expected_environment) if env_code == 0 else False
            status = "PASS" if matches is True else "BLOCKED" if matches is False else "NOT_TESTED"
            detail = "Selected PAC environment matches the configured Development target" if matches is True else "Selected PAC environment does not match the configured Development target" if matches is False else "PAC response lacks an explicit environment ID; verify through a supported target selection surface"
            add("development_environment", status, detail, True)

        mcp_code, _ = _run_pac(run, [pac, "copilot", "mcp"], home_path)
        add("pac_mcp", "PASS" if mcp_code == 0 else "CONDITIONAL", "PAC MCP command discovery responded; this does not start or authenticate the server" if mcp_code == 0 else "PAC MCP discovery unavailable; direct PAC CLI remains a supported fallback")
    else:
        add("pac_identity", "BLOCKED", "PAC is unavailable", bool(current_env.get("AGENTFACTORY_EXPECTED_UPN", "").strip()))
        add("development_environment", "BLOCKED", "PAC is unavailable", bool(current_env.get("AGENTFACTORY_DEVELOPMENT_ENVIRONMENT_ID", "").strip()))
        add("pac_mcp", "CONDITIONAL", "PAC is unavailable; direct PAC CLI remains a supported fallback")

    atk = _command("atk")
    if atk:
        atk_code, atk_auth = _run(run, [atk, "auth", "list"], timeout=10)
        expected_upn = current_env.get("AGENTFACTORY_EXPECTED_UPN", "").strip()
        if not expected_upn:
            add("atk_connected_account", "NOT_TESTED", "Set AGENTFACTORY_EXPECTED_UPN to compare connected Toolkit accounts; active account is not established")
        else:
            matched = atk_code == 0 and _identity_matches(atk_auth, expected_upn)
            add("atk_connected_account", "PASS" if matched else "BLOCKED", "Expected account appears in Toolkit's connected-account list; this does not identify its active account" if matched else "Expected account is absent from the supported Toolkit account list")
    else:
        add("atk_connected_account", "BLOCKED", "Agents Toolkit is unavailable")

    package_dirs = [root / "node_modules"]
    configured_modules = current_env.get("AGENTFACTORY_NODE_MODULES_DIR")
    if configured_modules:
        package_dirs.append(Path(configured_modules))
    package_dirs.append(home_path / ".local/share/agentfactory-host/node_modules")
    npm = _command("npm")
    if npm:
        npm_code, npm_root = _run(run, [npm, "root", "-g"])
        if npm_code == 0 and npm_root.strip():
            package_dirs.append(Path(npm_root.strip().splitlines()[0]))
    package_found = any((directory / "@microsoft/copilot-studio-mcp/package.json").is_file() for directory in package_dirs)
    add("copilot_studio_mcp", "PASS" if package_found else "FAIL", "Installed local MCP package found; process sign-in and runtime must still be verified" if package_found else "Local MCP package not found; MCP server availability is not established", True)

    # These blockers are evidence, not host/tool failures. Only type and short
    # explanation are emitted; no authentication or tenant identifiers are read.
    try:
        try:
            from scripts.config_loader import load_yaml
        except ModuleNotFoundError:
            from config_loader import load_yaml
        registry = load_yaml(Path(root) / "config/capability-registry.yaml")
        blockers = registry.get("execution_routing", {}).get("capability_evidence_notes", {}).get("known_blockers", [])
        blocked = [f"{item.get('type')}: {item.get('reason')}" for item in blockers]
        add("current_blockers", "BLOCKED" if blocked else "PASS", "; ".join(blocked) if blocked else "No known tenant or policy blockers recorded")
    except (OSError, ValueError, ImportError):
        add("current_blockers", "NOT_TESTED", "Registry blocker evidence could not be loaded")

    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit status-only JSON; raw CLI output and local paths are never included")
    args = parser.parse_args()
    checks = [asdict(item) for item in run_local_checks()]
    if args.json:
        print(json.dumps(checks, indent=2))
    else:
        for check in checks:
            print(f"{check['status']}: {check['name']}: {check['detail']}")
    return 1 if any(item["required"] and item["status"] in {"FAIL", "BLOCKED", "NOT_TESTED"} for item in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())

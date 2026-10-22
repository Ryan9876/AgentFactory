"""Exercise bootstrap without downloads, credentials, or a writable home."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CloudBootstrapTests(unittest.TestCase):
    def test_missing_sdk_is_installed_and_wiqd_failure_keeps_atk_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            scripts = repo / "scripts"
            scripts.mkdir(parents=True)
            for name in ("bootstrap_codex_cloud.sh", "cloud_env.sh", "codex_with_learn.sh"):
                shutil.copy(ROOT / "scripts" / name, scripts / name)
            fake = base / "fake"
            fake.mkdir()
            tools = base / "tools"
            log = base / "calls"
            def executable(path, body):
                path.write_text("#!/bin/bash\nset -e\n" + body)
                path.chmod(0o700)
            executable(fake / "python3", 'mkdir -p "$3/bin"; printf "#!/bin/bash\\nexit 0\\n" > "$3/bin/python"; chmod +x "$3/bin/python"\n')
            executable(fake / "node", 'echo v24.1.0\n')
            executable(fake / "npm", 'mkdir -p "$NPM_CONFIG_PREFIX/bin"; printf "#!/bin/bash\\necho ATK help\\n" > "$NPM_CONFIG_PREFIX/bin/atk"; chmod +x "$NPM_CONFIG_PREFIX/bin/atk"\n')
            executable(fake / "codex", 'echo "microsoft-learn https://learn.microsoft.com/api/mcp"\n')
            # A fake network boundary supplies installers; actual shell control
            # flow, PATH propagation, fallback handling and repeatability run.
            executable(fake / "curl", '''echo "$*" >> "$AF_TEST_LOG"
if [[ "$2" == *dotnet-install.sh ]]; then
cat > "$4" <<'INSTALL'
#!/bin/bash
[[ "$DOTNET_ROOT" == "$AGENTFACTORY_TOOLS_DIR/dotnet" ]] || exit 11
mkdir -p "$DOTNET_ROOT"
cat > "$DOTNET_ROOT/dotnet" <<'SDK'
#!/bin/bash
case "$1" in
 --version) echo 10.0.1;;
 --list-sdks) echo '10.0.1 [/fake/sdk]';;
 tool)
 cat > "$AGENTFACTORY_TOOLS_DIR/bin/pac" <<'PAC'
#!/bin/bash
echo PAC help
PAC
 chmod +x "$AGENTFACTORY_TOOLS_DIR/bin/pac";;
esac
SDK
chmod +x "$DOTNET_ROOT/dotnet"
INSTALL
else
 printf '#!/bin/bash\\nexit 1\\n' > "$4"
fi
''')
            environment = dict(os.environ, PATH=f"{fake}:/usr/bin:/bin", AGENTFACTORY_TOOLS_DIR=str(tools), AF_TEST_LOG=str(log))
            for _ in range(2):
                result = subprocess.run(["bash", "--noprofile", "--norc", str(scripts / "bootstrap_codex_cloud.sh")], env=environment, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("verified ATK", result.stdout)
            self.assertEqual(log.read_text().count("https://dot.net/v1/dotnet-install.sh"), 1)

    def test_activation_uses_absolute_paths_from_another_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(["bash", "-c", 'source "$1"; command -v python3; printf "%s\\n" "$DOTNET_ROOT" "$HOME"', "bash", str(ROOT / "scripts/cloud_env.sh")], cwd=tmp, capture_output=True, text=True, check=True)
            lines = result.stdout.splitlines()
            self.assertTrue(lines[0].startswith("/"))
            self.assertTrue(lines[1].startswith("/"))
            self.assertEqual(lines[2], os.environ["HOME"])

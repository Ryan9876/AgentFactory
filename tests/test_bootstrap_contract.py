import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class BootstrapContractTests(unittest.TestCase):
    def test_bootstrap_uses_supported_first_party_surfaces_and_separate_auth(self):
        script = (ROOT / "scripts/bootstrap_codex_cloud.sh").read_text()
        self.assertIn("set -euo pipefail", script)
        self.assertIn("https://aka.ms/wiqd/install.sh", script)
        self.assertIn("--skip-plugin", script)
        self.assertIn("@microsoft/m365agentstoolkit-cli", script)
        self.assertIn("Microsoft.PowerApps.CLI.Tool", script)
        self.assertIn("wiqd doctor", script)
        self.assertIn("codex mcp add microsoft-learn", script)
        self.assertNotIn("workiq.svc", script)
        self.assertNotIn("wiqd auth login", script)
        self.assertIn("Development target verification remain separate", script)
if __name__ == "__main__": unittest.main()

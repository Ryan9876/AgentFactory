import unittest
import subprocess
from scripts.readiness_check import run_checks

class ReadinessCheckTests(unittest.TestCase):
    def test_unverified_live_access_is_blocked_not_guessed_from_installed_tools(self):
        checks = {item.name: item for item in run_checks()}
        self.assertEqual(checks["m365_development_auth"].status, "BLOCKED")
        self.assertTrue(checks["m365_development_auth"].required)
        self.assertEqual(checks["direct_workiq_mcp"].status, "CONDITIONAL")
        self.assertFalse(checks["direct_workiq_mcp"].required)
    def test_required_tools_are_reported_separately(self):
        checks = run_checks()
        names = {item.name for item in checks}
        self.assertTrue({"node", "dotnet", "wiqd", "atk", "pac", "canonical_skills"}.issubset(names))
        self.assertNotIn("microsoft_365_auth_passed", names)
    def test_fake_host_runner_qualifies_help_versions_and_mcp_without_auth_guess(self):
        def fake_run(command, **kwargs):
            output = {"node": "v24.1.0", "dotnet": "10.0.1"}.get(command[0], "help output")
            if command[:3] == ["codex", "mcp", "list"]: output = "microsoft-learn https://learn.microsoft.com/api/mcp"
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")
        checks = {c.name: c for c in run_checks(fake_run, command_finder=lambda name: "/fake/" + name)}
        self.assertEqual(checks["node"].status, "PASS")
        self.assertEqual(checks["dotnet"].status, "PASS")
        self.assertEqual(checks["wiqd"].status, "PASS")
        self.assertEqual(checks["microsoft_learn_mcp"].status, "PASS")
        self.assertEqual(checks["m365_development_auth"].status, "BLOCKED")
    def test_fake_host_old_node_and_dotnet_fail_with_requirement(self):
        def fake_run(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, stdout={"node":"v20.3.0","dotnet":"9.0.0"}.get(command[0],"help"), stderr="")
        checks = {c.name:c for c in run_checks(fake_run, command_finder=lambda name: "/fake/" + name)}
        self.assertEqual(checks["node"].status, "FAIL")
        self.assertIn("24+", checks["node"].detail)
        self.assertEqual(checks["dotnet"].status, "FAIL")
        self.assertIn("10+", checks["dotnet"].detail)
if __name__ == "__main__": unittest.main()

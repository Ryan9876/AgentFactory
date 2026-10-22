import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.local_readiness_check import run_local_checks

ROOT = Path(__file__).resolve().parents[1]


class LocalReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        chrome = self.home / "Library/Application Support/Google/Chrome"
        chrome.mkdir(parents=True)
        (chrome / "Local State").write_text(json.dumps({
            "profile": {"info_cache": {"Profile 7": {"name": "AgentFactory"}}}
        }))
        modules = self.home / "node_modules"
        package = modules / "@microsoft/copilot-studio-mcp"
        package.mkdir(parents=True)
        (package / "package.json").write_text('{"name":"@microsoft/copilot-studio-mcp"}')
        self.env = {
            "AGENTFACTORY_EXPECTED_UPN": "user@example.test",
            "AGENTFACTORY_DEVELOPMENT_ENVIRONMENT_ID": "sample-development-id",
            "AGENTFACTORY_NODE_MODULES_DIR": str(modules),
        }

    def tearDown(self):
        self.temp.cleanup()

    def fake_runner(self, command, **kwargs):
        key = (Path(command[0]).name, *command[1:])
        output = {
            ("node", "--version"): "v24.1.0",
            ("dotnet", "--version"): "10.0.1",
            ("wiqd", "--help"): "help",
            ("atk", "-h"): "Agents Toolkit CLI help",
            ("atk", "auth", "list"): "user@example.test",
            ("pac", "help"): "Power Platform CLI help",
            ("pac", "auth", "list"): "Index Active Kind Name Friendly Name Url User Cloud Type\n[1] * UNIVERSAL Dev Development https://sample.crm.dynamics.com/ user@example.test Public User",
            ("pac", "copilot", "mcp"): "MCP server command",
            ("pac", "env", "list", "--filter", "sample-development-id"): "Name Environment ID Url\nDevelopment sample-development-id https://sample.crm.dynamics.com/",
            ("Google Chrome", "--version"): "Google Chrome 155.0.0.0",
        }.get(key, "")
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

    def checks(self, runner=None, env=None):
        return {item.name: item for item in run_local_checks(
            command_runner=runner or self.fake_runner,
            command_finder=lambda name: f"/fake/{name}",
            env=self.env if env is None else env,
            home=self.home,
            system="Darwin",
            root=ROOT,
        )}

    def test_local_tools_pac_auth_mcp_and_development_identity_are_reported(self):
        checks = self.checks()
        for name in ("local_execution", "pac", "pac_mcp", "copilot_studio_mcp", "atk", "wiqd"):
            self.assertEqual(checks[name].status, "PASS", name)
        self.assertEqual(checks["pac_identity"].status, "PASS")
        self.assertEqual(checks["development_environment"].status, "PASS")
        self.assertEqual(checks["atk_connected_account"].status, "PASS")
        self.assertIn("does not identify its active account", checks["atk_connected_account"].detail)
        self.assertEqual(checks["current_blockers"].status, "BLOCKED")

    def test_profile_is_discovered_by_visible_name_without_emitting_home_path(self):
        checks = self.checks()
        self.assertEqual(checks["agentfactory_chrome_profile"].status, "PASS")
        self.assertIn("Profile 7", checks["agentfactory_chrome_profile"].detail)
        self.assertNotIn(str(self.home), json.dumps([item.__dict__ for item in checks.values()]))

    def test_installed_tools_do_not_imply_identity_or_environment_verification(self):
        checks = self.checks(env={"AGENTFACTORY_NODE_MODULES_DIR": str(self.home / "node_modules")})
        self.assertEqual(checks["pac"].status, "PASS")
        self.assertEqual(checks["pac_identity"].status, "NOT_TESTED")
        self.assertEqual(checks["development_environment"].status, "NOT_TESTED")
        self.assertEqual(checks["agentfactory_browser_identity"].status, "NOT_TESTED")

    def test_pac_authentication_check_precedes_pac_mcp_discovery(self):
        commands = []
        def runner(command, **kwargs):
            commands.append(tuple(command))
            return self.fake_runner(command, **kwargs)
        self.checks(runner=runner)
        normalized = [(Path(command[0]).name, *command[1:]) for command in commands]
        self.assertLess(normalized.index(("pac", "auth", "list")), normalized.index(("pac", "copilot", "mcp")))

    def test_pac_and_atk_output_is_never_echoed_in_readiness_details(self):
        checks = self.checks()
        serialized = json.dumps([item.__dict__ for item in checks.values()])
        self.assertNotIn("smithr@opentext.com", serialized)
        self.assertNotIn("user@example.test", serialized)
        self.assertNotIn(str(self.home), serialized)

    def test_missing_profile_and_expected_identity_are_reported_without_guessing(self):
        (self.home / "Library/Application Support/Google/Chrome/Local State").unlink()
        checks = self.checks(env={})
        self.assertEqual(checks["agentfactory_chrome_profile"].status, "NOT_TESTED")
        self.assertEqual(checks["pac_identity"].status, "NOT_TESTED")
        self.assertEqual(checks["development_environment"].status, "NOT_TESTED")

    def test_environment_list_must_contain_the_configured_environment_id(self):
        def runner(command, **kwargs):
            if (Path(command[0]).name, *command[1:]) == ("pac", "env", "list", "--filter", "sample-development-id"):
                return subprocess.CompletedProcess(command, 0, stdout="Development other-environment-id https://sample.crm.dynamics.com/", stderr="")
            return self.fake_runner(command, **kwargs)
        checks = self.checks(runner=runner)
        self.assertEqual(checks["development_environment"].status, "BLOCKED")

    def test_environment_id_prefix_does_not_match_a_different_environment_row(self):
        def runner(command, **kwargs):
            if (Path(command[0]).name, *command[1:]) == ("pac", "env", "list", "--filter", "sample-development-id"):
                return subprocess.CompletedProcess(command, 0, stdout="Development sample-development-id-suffix https://sample.crm.dynamics.com/", stderr="")
            return self.fake_runner(command, **kwargs)
        checks = self.checks(runner=runner)
        self.assertEqual(checks["development_environment"].status, "BLOCKED")

    def test_identity_comparison_requires_exact_account_boundary(self):
        def runner(command, **kwargs):
            if (Path(command[0]).name, *command[1:]) == ("pac", "auth", "list"):
                return subprocess.CompletedProcess(command, 0, stdout="other.smithr@opentext.com", stderr="")
            return self.fake_runner(command, **kwargs)
        checks = self.checks(runner=runner)
        self.assertEqual(checks["pac_identity"].status, "BLOCKED")

    def test_development_environment_is_not_qualified_under_mismatched_pac_identity(self):
        def runner(command, **kwargs):
            if (Path(command[0]).name, *command[1:]) == ("pac", "auth", "list"):
                return subprocess.CompletedProcess(command, 0, stdout="other@example.test", stderr="")
            return self.fake_runner(command, **kwargs)
        checks = self.checks(runner=runner)
        self.assertEqual(checks["pac_identity"].status, "BLOCKED")
        self.assertEqual(checks["development_environment"].status, "BLOCKED")
        self.assertTrue(checks["pac_identity"].required)
        self.assertTrue(checks["development_environment"].required)

    def test_expected_inactive_profile_does_not_pass_when_another_pac_profile_is_active(self):
        def runner(command, **kwargs):
            if (Path(command[0]).name, *command[1:]) == ("pac", "auth", "list"):
                return subprocess.CompletedProcess(command, 0, stdout="[1] * UNIVERSAL Other https://other.crm.dynamics.com/ other@example.test\n[2]   UNIVERSAL Expected https://sample.crm.dynamics.com/ user@example.test", stderr="")
            return self.fake_runner(command, **kwargs)
        checks = self.checks(runner=runner)
        self.assertEqual(checks["pac_identity"].status, "BLOCKED")
        self.assertEqual(checks["development_environment"].status, "BLOCKED")

    def test_missing_atk_account_is_reported_without_failing_local_host_readiness(self):
        def runner(command, **kwargs):
            if (Path(command[0]).name, *command[1:]) == ("atk", "auth", "list"):
                return subprocess.CompletedProcess(command, 0, stdout="Use atk auth login m365 to log in to Microsoft 365 account.", stderr="")
            return self.fake_runner(command, **kwargs)
        checks = self.checks(runner=runner)
        self.assertEqual(checks["atk_connected_account"].status, "BLOCKED")
        self.assertFalse(checks["atk_connected_account"].required)
        self.assertEqual(checks["pac_identity"].status, "PASS")
        self.assertEqual(checks["development_environment"].status, "PASS")

    def test_pac_mcp_discovery_does_not_start_the_server_or_authenticate(self):
        commands = []
        def runner(command, **kwargs):
            commands.append(tuple(command))
            return self.fake_runner(command, **kwargs)
        self.checks(runner=runner)
        normalized = [(Path(command[0]).name, *command[1:]) for command in commands]
        self.assertIn(("pac", "copilot", "mcp"), normalized)
        self.assertNotIn(("pac", "copilot", "mcp", "--run"), normalized)
        self.assertNotIn(("pac", "auth", "create"), normalized)


if __name__ == "__main__":
    unittest.main()

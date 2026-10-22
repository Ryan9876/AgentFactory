import unittest
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
if __name__ == "__main__": unittest.main()

import unittest
from pathlib import Path
from scripts.config_loader import load_yaml
from scripts.host_routing import choose_execution_route

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = load_yaml(ROOT / "config/capability-registry.yaml")

class HostRoutingTests(unittest.TestCase):
    def test_tenant_authenticated_operations_prefer_desktop_local(self):
        route = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"codex_cloud", "desktop_local"})
        self.assertEqual(route["host"], "desktop_local")
        self.assertEqual(route["status"], "ROUTED")

    def test_source_engineering_prefers_cloud(self):
        route = choose_execution_route(REGISTRY, "repository.engineering", {"codex_cloud", "desktop_local"})
        self.assertEqual(route["host"], "codex_cloud")

    def test_deterministic_agent_package_validation_prefers_cloud(self):
        for capability in ("package.build_validation", "declarative_agent.validate", "declarative_agent.package"):
            with self.subTest(capability=capability):
                route = choose_execution_route(REGISTRY, capability, {"codex_cloud", "desktop_local"})
                self.assertEqual(route["host"], "codex_cloud")

    def test_public_documentation_can_use_either_supported_host(self):
        route = choose_execution_route(REGISTRY, "public.documentation", {"desktop_local"})
        self.assertEqual(route["host"], "desktop_local")
        self.assertEqual(route["status"], "ROUTED")

    def test_supported_host_fallback_is_used_when_preferred_host_is_unavailable(self):
        route = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"codex_cloud"})
        self.assertEqual(route["host"], "codex_cloud")
        self.assertEqual(route["status"], "ROUTED")

    def test_authentication_failure_does_not_trigger_host_hopping(self):
        route = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"codex_cloud", "desktop_local"}, blocker="AUTH")
        self.assertIsNone(route["host"])
        self.assertEqual(route["status"], "BLOCKED")
        self.assertEqual(route["blocker"], "AUTH")

    def test_local_tool_host_failure_can_use_a_supported_alternate_host(self):
        route = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"codex_cloud", "desktop_local"}, blocker="TOOL_HOST")
        self.assertEqual(route["host"], "codex_cloud")
        self.assertEqual(route["status"], "ROUTED")

    def test_tenant_policy_blocker_never_causes_host_hop(self):
        route = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"codex_cloud", "desktop_local"}, blocker="BLOCKED_BY_TENANT_OR_POLICY")
        self.assertIsNone(route["host"])
        self.assertEqual(route["status"], "BLOCKED_BY_TENANT_OR_POLICY")

    def test_user_presence_requirement_stops_at_human_boundary(self):
        route = choose_execution_route(REGISTRY, "microsoft.interactive_authentication", {"desktop_local"}, human_presence_required=True)
        self.assertIsNone(route["host"])
        self.assertEqual(route["status"], "USER_PRESENCE_REQUIRED")

    def test_admin_required_stops_without_selecting_a_host(self):
        route = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"desktop_local", "codex_cloud"}, admin_required=True)
        self.assertIsNone(route["host"])
        self.assertEqual(route["status"], "ADMIN_REQUIRED")

    def test_runtime_qualification_capability_prefers_desktop_local(self):
        route = choose_execution_route(REGISTRY, "microsoft.runtime_qualification", {"desktop_local", "codex_cloud"})
        self.assertEqual(route["host"], "desktop_local")

    def test_implementation_surface_order_prefers_mcp_cli_then_api_before_browser(self):
        self.assertEqual(REGISTRY["execution_routing"]["surface_preference"], ["mcp", "cli", "api_sdk", "supported_editor_config", "declarative_source", "import_export", "supported_browser_ui", "browser_automation", "human_action"])

    def test_unknown_capability_has_no_automatic_fallback(self):
        route = choose_execution_route(REGISTRY, "unknown.capability", {"desktop_local", "codex_cloud"})
        self.assertIsNone(route["host"])
        self.assertEqual(route["status"], "BLOCKED")

    def test_only_cloud_testing_browser_is_generic_regression_profile(self):
        browser = REGISTRY["execution_routing"]["browser_surfaces"]
        self.assertEqual(browser["persistent_identity"]["browser"], "chrome_stable")
        self.assertEqual(browser["persistent_identity"]["profile_name"], "AgentFactory")
        self.assertFalse(browser["persistent_identity"]["generic_regression"])
        self.assertEqual(browser["deterministic_regression"]["browser"], "chrome_for_testing")
        self.assertEqual(browser["deterministic_regression"]["profile"], "disposable_isolated")
        self.assertNotIn("/Users/", str(browser))

    def test_chrome_surfaces_cannot_be_swapped(self):
        browser = REGISTRY["execution_routing"]["browser_surfaces"]
        self.assertNotEqual(browser["persistent_identity"]["browser"], browser["deterministic_regression"]["browser"])
        self.assertNotEqual(browser["persistent_identity"]["profile_requirement"], browser["deterministic_regression"]["profile"])

    def test_runtime_qualification_is_separate_from_tool_discovery(self):
        routing = REGISTRY["execution_routing"]
        self.assertEqual(routing["evidence_states"]["default_state"], "NOT_TESTED")
        self.assertTrue(routing["evidence_states"]["tool_discovery_does_not_imply_runtime_qualification"])
        route = choose_execution_route(REGISTRY, "copilot_studio.mcp", {"desktop_local"}, evidence="IMPLEMENTED")
        self.assertEqual(route["evidence_state"], "IMPLEMENTED")
        self.assertEqual(route["status"], "ROUTED")

    def test_pac_authentication_precedes_pac_mcp(self):
        ordering = REGISTRY["execution_routing"]["startup_order"]["pac_mcp"]
        self.assertEqual(ordering, ["pac_authentication", "start_or_restart_pac_mcp"])

    def test_copilot_studio_fresh_process_requires_account_environment_and_catalog(self):
        ordering = REGISTRY["execution_routing"]["startup_order"]["copilot_studio_mcp"]
        self.assertEqual(ordering, ["connect", "verify_account", "verify_development_environment", "refresh_live_catalog"])
        self.assertFalse(REGISTRY["execution_routing"]["authentication"]["browser_state_is_unattended_proof"])

if __name__ == "__main__":
    unittest.main()

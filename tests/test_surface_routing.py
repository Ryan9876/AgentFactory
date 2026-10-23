import unittest
from pathlib import Path

from scripts.config_loader import load_yaml
from scripts.surface_routing import choose_implementation_surface

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = load_yaml(ROOT / "config/capability-registry.yaml")


def evidence(status, detail):
    return {"status": status, "evidence": detail}


class SurfaceRoutingTests(unittest.TestCase):
    def test_structured_configuration_beats_proposed_playwright(self):
        routes = {
            "mcp": evidence("supported", "live operation"),
            "supported_editor_config": evidence("supported", "project source"),
        }
        result = choose_implementation_surface(REGISTRY, routes, proposed_surface="playwright")
        self.assertEqual(result["status"], "STOP_REASSESS")
        self.assertEqual(result["preferred_surface"], "mcp")

    def test_highest_priority_supported_structured_route_is_selected(self):
        routes = {
            "mcp": evidence("unavailable", "fresh process failure"),
            "cli": evidence("supported", "accepted operation"),
            "api_sdk": evidence("supported", "API operation"),
        }
        self.assertEqual(choose_implementation_surface(REGISTRY, routes)["surface"], "cli")

    def test_proposed_editor_is_rejected_when_higher_priority_mcp_works(self):
        result = choose_implementation_surface(
            REGISTRY,
            {
                "mcp": evidence("supported", "configuration operation"),
                "supported_editor_config": evidence("supported", "source editor"),
            },
            proposed_surface="supported_editor_config",
        )
        self.assertEqual(result["status"], "STOP_REASSESS")
        self.assertEqual(result["preferred_surface"], "mcp")

    def test_proposed_api_stops_when_higher_priority_routes_are_unverified(self):
        result = choose_implementation_surface(
            REGISTRY,
            {"api_sdk": evidence("supported", "configuration operation")},
            proposed_surface="api_sdk",
        )
        self.assertEqual(result["status"], "STOP_REASSESS")

    def test_browser_fallback_requires_evidence_all_higher_routes_rejected(self):
        order = REGISTRY["execution_routing"]["surface_preference"]
        routes = {
            key: evidence("unavailable", f"{key} checked; operation absent")
            for key in order
            if key not in ("supported_browser_ui", "browser_automation", "human_action")
        }
        routes["supported_browser_ui"] = evidence("insufficient", "cannot configure this setting")
        routes["browser_automation"] = evidence("supported", "portal-only setting verified")
        result = choose_implementation_surface(REGISTRY, routes, proposed_surface="playwright")
        self.assertEqual(result["surface"], "browser_automation")
        self.assertIn("supported_editor_config:", result["reason"])

    def test_unknown_structured_route_blocks_browser_proposal(self):
        result = choose_implementation_surface(
            REGISTRY, {"mcp": evidence("unavailable", "checked")}, proposed_surface="playwright"
        )
        self.assertEqual(result["status"], "STOP_REASSESS")

    def test_browser_cannot_be_chosen_just_because_session_is_open(self):
        routes = {
            "mcp": evidence("unavailable", "operation not exposed"),
            "cli": evidence("unavailable", "command absent"),
            "api_sdk": evidence("unavailable", "operation absent"),
            "supported_editor_config": evidence("unavailable", "no config file"),
            "declarative_source": evidence("unavailable", "no source representation"),
            "import_export": evidence("unavailable", "not supported"),
            "supported_browser_ui": evidence("insufficient", "requires scripted interaction"),
        }
        result = choose_implementation_surface(REGISTRY, routes, proposed_surface="playwright")
        self.assertEqual(result["status"], "BLOCKED")

    def test_configuration_can_follow_browser_authentication_through_mcp(self):
        from scripts.host_routing import choose_execution_route

        auth_route = choose_execution_route(
            REGISTRY, "microsoft.interactive_authentication", {"desktop_local"}
        )
        self.assertEqual(auth_route["status"], "ROUTED")
        config_route = choose_implementation_surface(
            REGISTRY, {"mcp": evidence("supported", "authenticated MCP method")}
        )
        self.assertEqual(config_route["surface"], "mcp")

    def test_runtime_observation_is_separate_from_configuration_surface(self):
        result = choose_implementation_surface(
            REGISTRY, {"mcp": evidence("supported", "configuration method")}
        )
        self.assertEqual(result["surface"], "mcp")
        self.assertEqual(REGISTRY["execution_routing"]["evidence_states"]["default_state"], "NOT_TESTED")
        self.assertTrue(
            REGISTRY["execution_routing"]["evidence_states"]
            ["tool_discovery_does_not_imply_runtime_qualification"]
        )

    def test_failed_one_route_does_not_authorize_browser_fallback(self):
        result = choose_implementation_surface(
            REGISTRY, {"mcp": evidence("unavailable", "tool error")}, proposed_surface="playwright"
        )
        self.assertEqual(result["status"], "STOP_REASSESS")

    def test_adjacent_configuration_returns_to_structured_route(self):
        browser_work = {
            "mcp": evidence("unavailable", "operation absent"),
            "cli": evidence("unavailable", "operation absent"),
            "api_sdk": evidence("unavailable", "operation absent"),
            "supported_editor_config": evidence("unavailable", "operation absent"),
            "declarative_source": evidence("unavailable", "operation absent"),
            "import_export": evidence("unavailable", "operation absent"),
            "supported_browser_ui": evidence("insufficient", "portal interaction required"),
            "browser_automation": evidence("supported", "bounded operation"),
        }
        result = choose_implementation_surface(REGISTRY, browser_work, proposed_surface="playwright")
        self.assertEqual(result["surface"], "browser_automation")
        next_operation = choose_implementation_surface(
            REGISTRY, {"supported_editor_config": evidence("supported", "next setting in source")}
        )
        self.assertEqual(next_operation["surface"], "supported_editor_config")

    def test_host_router_requires_surface_evidence_for_agent_configuration(self):
        from scripts.host_routing import choose_execution_route

        missing = choose_execution_route(
            REGISTRY, "copilot_studio.standard.author", {"desktop_local"}
        )
        self.assertEqual(missing["status"], "STOP_REASSESS")
        structured = choose_execution_route(
            REGISTRY,
            "copilot_studio.standard.author",
            {"desktop_local"},
            surface_assessments={
                "mcp": evidence("supported", "agent configuration operation")
            },
        )
        self.assertEqual(structured["status"], "ROUTED")
        self.assertEqual(structured["surface"], "mcp")
        rejected = choose_execution_route(
            REGISTRY,
            "copilot_studio.standard.author",
            {"desktop_local"},
            proposed_surface="playwright",
            surface_assessments={
                "mcp": evidence("supported", "agent configuration operation")
            },
        )
        self.assertEqual(rejected["status"], "STOP_REASSESS")
        self.assertIsNone(rejected["host"])

    def test_host_router_preserves_browser_fallback_evidence(self):
        from scripts.host_routing import choose_execution_route

        assessments = {
            key: evidence("unavailable", f"{key} cannot perform this operation")
            for key in REGISTRY["execution_routing"]["surface_preference"]
            if key not in ("supported_browser_ui", "browser_automation", "human_action")
        }
        assessments["supported_browser_ui"] = evidence("insufficient", "portal lacks an import action")
        assessments["browser_automation"] = evidence("supported", "one bounded import action")
        result = choose_execution_route(
            REGISTRY,
            "copilot_studio.standard.author",
            {"desktop_local"},
            proposed_surface="playwright",
            surface_assessments=assessments,
        )
        self.assertEqual(result["surface"], "browser_automation")
        self.assertIn("api_sdk: api_sdk cannot perform this operation", result["surface_decision_reason"])
        self.assertIn("browser_automation: one bounded import action", result["surface_decision_reason"])
        self.assertEqual(result["surface_assessments"], assessments)

    def test_tenant_security_and_authority_blockers_remain_stops(self):
        from scripts.host_routing import choose_execution_route

        for blocker in ("BLOCKED_BY_TENANT_OR_POLICY", "AUTH", "USER_PRESENCE_REQUIRED", "ADMIN_REQUIRED"):
            with self.subTest(blocker=blocker):
                result = choose_execution_route(
                    REGISTRY, "copilot_studio.standard.author",
                    {"desktop_local", "codex_cloud"}, blocker=blocker,
                )
                self.assertIsNone(result["host"])


if __name__ == "__main__":
    unittest.main()

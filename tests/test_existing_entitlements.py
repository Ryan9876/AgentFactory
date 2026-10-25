"""Regression coverage for architecture decisions within current entitlements."""

from copy import deepcopy
from pathlib import Path
import unittest

from scripts.config_loader import evaluate_architecture_candidates, load_yaml, validate_constraints
from scripts.host_routing import choose_execution_route


ROOT = Path(__file__).resolve().parents[1]
CONSTRAINTS = load_yaml(ROOT / "config/constraints.yaml")
REGISTRY = load_yaml(ROOT / "config/capability-registry.yaml")


class ExistingEntitlementsTests(unittest.TestCase):
    def test_unavailable_admin_privilege_rejects_architecture_before_build(self):
        result = evaluate_architecture_candidates(
            [{"name": "Copilot Studio MCP lifecycle", "requires": ["copilot_studio.agent_inventory"]}],
            REGISTRY["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT")
        self.assertEqual(result["evaluations"][0]["status"], "REJECTED_CURRENT_ENVIRONMENT")

    def test_no_elevated_role_recommendation_is_configured(self):
        forbidden = CONSTRAINTS["qualification"]["unavailable_entitlement_remediation"]["forbidden"]
        self.assertFalse(CONSTRAINTS["qualification"]["unavailable_entitlement_remediation"]["allowed"])
        self.assertIn("request_elevated_privileges_or_security_roles", forbidden)
        self.assertIn("request_tenant_admin_permissions_or_admin_consent", forbidden)
        skills = (ROOT / ".agents/skills/agentfactory/SKILL.md").read_text().lower()
        guardrails = (ROOT / ".agents/skills/agentfactory/references/engineering-guardrails.md").read_text().lower()
        self.assertIn("not an access request", skills)
        self.assertIn("do not provide an administrator request", guardrails)

    def test_missing_copilot_credits_rejects_credit_dependent_architecture(self):
        result = evaluate_architecture_candidates(
            [{"name": "Credit-dependent harness", "requires": ["github_copilot_harness"]}],
            REGISTRY["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT")

    def test_disabled_sideload_permission_rejects_required_deployment(self):
        result = evaluate_architecture_candidates(
            [{"name": "Sideloaded declarative app", "requires": ["agents_toolkit.custom_app_upload"]}],
            REGISTRY["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT")

    def test_missing_service_principal_is_a_fixed_constraint(self):
        entry = REGISTRY["environment_constraints"]["capability_availability"]["workiq.upstream_service_principal"]
        self.assertEqual(entry["classification"], "FIXED_ENVIRONMENT_CONSTRAINT")
        self.assertEqual(entry["environment_availability"], "unavailable")
        result = evaluate_architecture_candidates(
            [{"name": "Direct Work IQ", "requires": ["workiq.upstream_service_principal"]}],
            REGISTRY["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT")

    def test_authorization_denial_does_not_trigger_browser_automation(self):
        result = choose_execution_route(
            REGISTRY, "copilot_studio.agent_inventory", {"desktop_local", "codex_cloud"},
            blocker="BLOCKED_BY_TENANT_OR_POLICY", proposed_surface="browser_automation",
        )
        self.assertIsNone(result["host"])
        self.assertEqual(result["status"], "BLOCKED_BY_TENANT_OR_POLICY")

    def test_authorization_denial_does_not_trigger_host_hopping(self):
        result = choose_execution_route(
            REGISTRY, "power_platform.authenticated_operations", {"desktop_local", "codex_cloud"},
            blocker="BLOCKED_BY_TENANT_OR_POLICY",
        )
        self.assertIsNone(result["host"])
        self.assertEqual(result["status"], "BLOCKED_BY_TENANT_OR_POLICY")

    def test_architecture_selection_evaluates_supported_alternatives(self):
        result = evaluate_architecture_candidates(
            [
                {"name": "Direct Work IQ", "requires": ["workiq.direct_mcp"]},
                {"name": "Host-composed Work IQ", "requires": ["work_iq.host_composition"]},
            ],
            REGISTRY["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(result["architecture"], "Host-composed Work IQ")
        self.assertEqual(result["evaluations"][0]["status"], "REJECTED_CURRENT_ENVIRONMENT")

    def test_viable_lower_authority_route_is_selected(self):
        availability = {
            "requires_admin": {"environment_availability": "unavailable", "classification": "FIXED_ENVIRONMENT_CONSTRAINT"},
            "native_route": {"environment_availability": "available", "classification": "CURRENT_ENVIRONMENT_AVAILABLE"},
        }
        result = evaluate_architecture_candidates(
            [{"name": "Admin route", "requires": ["requires_admin"]}, {"name": "Native route", "requires": ["native_route"]}],
            availability,
        )
        self.assertEqual(result["architecture"], "Native route")

    def test_no_viable_route_marks_capability_unavailable(self):
        availability = {"blocked": {"environment_availability": "unavailable", "classification": "FIXED_ENVIRONMENT_CONSTRAINT"}}
        result = evaluate_architecture_candidates(
            [{"name": "Candidate A", "requires": ["blocked"]}, {"name": "Candidate B", "requires": ["blocked"]}],
            availability,
        )
        self.assertEqual(result["status"], "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT")
        self.assertIsNone(result["architecture"])

    def test_fixed_entitlement_block_is_not_a_tooling_failure(self):
        entry = REGISTRY["environment_constraints"]["capability_availability"]["copilot_studio.agent_inventory"]
        self.assertEqual(entry["classification"], "FIXED_ENVIRONMENT_CONSTRAINT")
        self.assertNotEqual(entry["classification"], "REMEDIABLE_TOOLING_FAILURE")

    def test_unconfirmed_fixed_change_does_not_hide_available_alternative(self):
        availability = {
            "constrained": {
                "environment_availability": "available",
                "classification": "FIXED_ENVIRONMENT_CONSTRAINT",
            },
            "alternative": {
                "environment_availability": "available",
                "classification": "CURRENT_ENVIRONMENT_AVAILABLE",
            },
        }
        result = evaluate_architecture_candidates(
            [
                {"name": "Changed-premise route", "requires": ["constrained"]},
                {"name": "Available alternative", "requires": ["alternative"]},
            ],
            availability,
        )
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(result["architecture"], "Available alternative")
        self.assertEqual(result["evaluations"][0]["status"], "PREMISE_CHANGE_CONFIRMATION_REQUIRED")

    def test_no_viable_alternative_preserves_confirmation_required_result(self):
        availability = {
            "constrained": {
                "environment_availability": "available",
                "classification": "FIXED_ENVIRONMENT_CONSTRAINT",
            },
            "unavailable": {
                "environment_availability": "unavailable",
                "classification": "FIXED_ENVIRONMENT_CONSTRAINT",
            },
        }
        result = evaluate_architecture_candidates(
            [
                {"name": "Changed-premise route", "requires": ["constrained"]},
                {"name": "Unavailable alternative", "requires": ["unavailable"]},
            ],
            availability,
        )
        self.assertEqual(result["status"], "PREMISE_CHANGE_CONFIRMATION_REQUIRED")
        self.assertIsNone(result["architecture"])
        self.assertEqual(result["evaluations"][0]["capabilities"], ["constrained"])

    def test_unrelated_confirmation_does_not_unlock_constrained_candidate(self):
        availability = {
            "constrained": {
                "environment_availability": "available",
                "classification": "FIXED_ENVIRONMENT_CONSTRAINT",
            },
            "unrelated": {
                "environment_availability": "available",
                "classification": "FIXED_ENVIRONMENT_CONSTRAINT",
            },
        }
        result = evaluate_architecture_candidates(
            [{"name": "Changed-premise route", "requires": ["constrained"]}],
            availability,
            confirmed_changed_capabilities={"unrelated"},
        )
        self.assertEqual(result["status"], "PREMISE_CHANGE_CONFIRMATION_REQUIRED")
        self.assertEqual(result["evaluations"][0]["capabilities"], ["constrained"])

    def test_blocked_lab_completes_and_independent_labs_continue(self):
        policy = REGISTRY["environment_constraints"]["qualification"]
        self.assertEqual(policy["fixed_environment_constraint_result"], "CAPABILITY_BLOCKED_BY_FIXED_ENVIRONMENT_CONSTRAINT")
        self.assertTrue(policy["counts_as_completed_lab"])
        self.assertTrue(policy["continue_independent_labs"])
        self.assertTrue(policy["block_later_lab_only_when_technically_dependent"])

    def test_unverified_prerequisite_fails_closed(self):
        result = evaluate_architecture_candidates(
            [{"name": "Unknown route", "requires": ["unknown_capability"]}],
            REGISTRY["environment_constraints"]["capability_availability"],
        )
        self.assertEqual(result["status"], "BLOCKED_UNVERIFIED_REQUIREMENT")

    def test_remediable_tooling_failure_is_not_reclassified_as_fixed_entitlement(self):
        result = evaluate_architecture_candidates(
            [{"name": "Tool-host route", "requires": ["temporarily_unavailable"]}],
            {"temporarily_unavailable": {
                "environment_availability": "unavailable",
                "classification": "REMEDIABLE_TOOLING_FAILURE",
                "blocker": "temporary tool host outage",
            }},
        )
        self.assertEqual(result["status"], "REMEDIATION_REQUIRED")

    def test_fixed_constraint_requires_explicit_premise_change_to_reevaluate(self):
        availability = deepcopy(REGISTRY["environment_constraints"]["capability_availability"])
        availability["copilot_studio.agent_inventory"]["environment_availability"] = "available"
        candidates = [
            {"name": "Copilot Studio MCP lifecycle", "requires": ["copilot_studio.agent_inventory"]}
        ]
        unconfirmed = evaluate_architecture_candidates(
            candidates, availability,
        )
        self.assertEqual(unconfirmed["status"], "PREMISE_CHANGE_CONFIRMATION_REQUIRED")

        confirmed = evaluate_architecture_candidates(
            candidates,
            availability,
            confirmed_changed_capabilities={"copilot_studio.agent_inventory"},
        )
        self.assertEqual(confirmed["architecture"], "Copilot Studio MCP lifecycle")

        unrelated_confirmation = evaluate_architecture_candidates(
            [{"name": "Sideload route", "requires": ["agents_toolkit.custom_app_upload"]}],
            availability,
            confirmed_changed_capabilities={"copilot_studio.agent_inventory"},
        )
        self.assertEqual(unrelated_confirmation["status"], "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT")

    def test_structured_config_first_routing_remains_intact(self):
        self.assertEqual(
            REGISTRY["execution_routing"]["surface_preference"],
            ["mcp", "cli", "api_sdk", "supported_editor_config", "declarative_source", "import_export", "supported_browser_ui", "browser_automation", "human_action"],
        )

    def test_hybrid_host_routing_and_runtime_evidence_remain_intact(self):
        cloud = choose_execution_route(REGISTRY, "repository.engineering", {"codex_cloud", "desktop_local"})
        local = choose_execution_route(REGISTRY, "power_platform.authenticated_operations", {"codex_cloud", "desktop_local"})
        self.assertEqual(cloud["host"], "codex_cloud")
        self.assertEqual(local["host"], "desktop_local")
        evidence = REGISTRY["execution_routing"]["evidence_states"]
        self.assertTrue(evidence["tool_discovery_does_not_imply_runtime_qualification"])

    def test_constraint_config_is_valid_and_existing_entitlements_only(self):
        self.assertEqual(validate_constraints(CONSTRAINTS), [])
        self.assertEqual(CONSTRAINTS["qualification"]["entitlement_policy"], "existing_entitlements_only")
        self.assertTrue(CONSTRAINTS["qualification"]["fixed_for_program_unless_explicitly_changed"])


if __name__ == "__main__":
    unittest.main()

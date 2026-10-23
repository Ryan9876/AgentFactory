import csv
import re
import unittest
from pathlib import Path
from scripts.config_loader import load_yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/capability-registry.yaml"
ROUTES = ROOT / ".agents/skills/agentfactory/references/capability-routes.csv"
SPEC = ROOT / "docs/specs/m365-agent-factory-spec.md"
FIELDS = {"microsoft_support_status", "preview_status", "organization_policy_status", "licensing_status", "codex_cloud_tool_status", "authentication_status", "tenant_execution_status", "cloud_synchronization_status", "runtime_qualification_status", "user_presence_required", "admin_required", "tool_host_block", "last_verified_at", "evidence", "limitations", "fallback"}

class CapabilityRegistryTests(unittest.TestCase):
    def test_registry_has_independent_evidence_dimensions_and_safe_unknowns(self):
        data = load_yaml(REGISTRY)
        self.assertEqual(data["schema_version"], 2)
        self.assertTrue({"wiqd", "agents_toolkit", "pac", "pac_mcp", "power_automate", "dataverse", "agent_evaluation", "workiq_retrieve", "host_composed_workiq", "custom_engine", "github_copilot_harness"}.issubset(data["providers"]))
        for name, provider in data["providers"].items():
            with self.subTest(provider=name):
                self.assertTrue(FIELDS.issubset(provider))
                self.assertNotEqual(provider["authentication_status"], "pass")
                self.assertNotEqual(provider["tenant_execution_status"], "pass")
        self.assertEqual(data["providers"]["github_copilot_harness"]["organization_policy_status"], "disallowed")
        self.assertEqual(data["providers"]["workiq_retrieve"]["licensing_status"], "conditional")
        self.assertNotEqual(data["providers"]["host_composed_workiq"]["organization_policy_status"], "disallowed")

    def test_route_matrix_has_known_ids_and_focused_context(self):
        approved = set(re.findall(r"\bREQ-\d{3}\b", SPEC.read_text()))
        with ROUTES.open(newline="") as stream: rows = list(csv.DictReader(stream))
        self.assertGreaterEqual(len(rows), 10)
        known = set(load_yaml(REGISTRY)["capabilities"])
        for row in rows:
            self.assertIn(row["capability_id"], known)
            self.assertRegex(row["requirement_ids"], r"^REQ-\d{3}(;REQ-\d{3})*$")
            self.assertTrue(set(row["requirement_ids"].split(";")).issubset(approved))
            self.assertTrue(row["focused_context"].strip())
            self.assertTrue(row["unavailable_behavior"].strip())

    def test_probe_a_keeps_schema_discovery_separate_from_runtime_qualification(self):
        notes = load_yaml(REGISTRY)["execution_routing"]["capability_evidence_notes"]
        probe = notes["probe_a_copilot_studio_mcp"]
        self.assertEqual(probe["agent_inventory"], "BLOCKED_BY_TENANT_OR_POLICY")
        self.assertFalse(probe["schema_advertised_operations_are_runtime_qualified"])
        self.assertEqual(probe["create_update_validate_test_evaluate_cleanup"], "NOT_TESTED")
        self.assertTrue(probe["no_agent_created"])
        self.assertTrue(probe["probe_b_waits_for_inventory_permission_resolution"])

    def test_no_duplicate_v1_json_registry_remains_authoritative(self):
        self.assertFalse((ROOT / ".agents/skills/agentfactory/references/capability-registry.json").exists())

    def test_execution_routing_covers_registered_capabilities_without_user_paths(self):
        data = load_yaml(REGISTRY)
        routing = data["execution_routing"]
        routed = {capability for route in routing["routes"].values() for capability in route["capabilities"]}
        self.assertEqual(routed, set(data["capabilities"]))
        self.assertNotIn("/Users/", str(routing))
        self.assertTrue(routing["browser_automation_gate"]["reject_if_structured_route_supported"])
        self.assertFalse(routing["browser_automation_gate"]["session_already_open_is_justification"])
        self.assertEqual(routing["browser_surfaces"]["persistent_identity"]["profile_name"], "AgentFactory")
        blockers = routing["host_fallback"]["never_when_blocker"]
        self.assertIn("BLOCKED_BY_TENANT_OR_POLICY", blockers)
        self.assertIn("USER_PRESENCE_REQUIRED", blockers)


if __name__ == "__main__": unittest.main()

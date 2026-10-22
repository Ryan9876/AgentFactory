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
        for row in rows:
            self.assertRegex(row["requirement_ids"], r"^REQ-\d{3}(;REQ-\d{3})*$")
            self.assertTrue(set(row["requirement_ids"].split(";")).issubset(approved))
            self.assertTrue(row["focused_context"].strip())
            self.assertTrue(row["unavailable_behavior"].strip())

    def test_no_duplicate_v1_json_registry_remains_authoritative(self):
        self.assertFalse((ROOT / ".agents/skills/agentfactory/references/capability-registry.json").exists())

if __name__ == "__main__": unittest.main()

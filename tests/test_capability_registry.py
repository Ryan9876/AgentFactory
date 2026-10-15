"""Schema and routing checks for capability intent/provider separation."""

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / ".github/skills/m365-agent-factory/references/capability-registry.json"
REGISTRY_CONTRACT = ROOT / ".github/skills/m365-agent-factory/references/capability-registry.md"
ROUTING = ROOT / ".github/skills/m365-agent-factory/references/build-routing.md"
ROUTES_PATH = ROOT / ".github/skills/m365-agent-factory/references/capability-routes.csv"
SPEC_PATH = ROOT / "docs/specs/m365-agent-factory-spec.md"
PROVIDER_FIELDS = {
    "name", "version", "discovery_status", "execution_status", "install_or_discovery_path",
    "compatibility_evidence", "checked_at", "prerequisites", "limitations", "unavailable_behavior",
}
CAPABILITY_FIELDS = {"capability_id", "family", "operation_scope", "provider_ids"}
EXPECTED_CAPABILITIES = {
    "copilot_studio.standard.author", "copilot_studio.standard.manage", "copilot_studio.standard.test",
    "copilot_studio.ghcp.author", "power_automate.connector.discover", "power_automate.flow.build",
    "power_automate.flow.edit", "power_automate.flow.validate", "power_automate.flow.preflight",
    "power_automate.flow.execute", "power_automate.flow.diagnose", "dataverse.metadata",
    "dataverse.data", "dataverse.security", "dataverse.admin", "dataverse.solution",
    "agent.evaluate", "power_platform.solution.alm",
}


def load_registry():
    return json.loads(REGISTRY_PATH.read_text())


class CapabilityRegistryTests(unittest.TestCase):
    def test_registry_schema_separates_stable_intents_from_providers(self):
        registry = load_registry()
        self.assertEqual(registry["schema_version"], 1)
        self.assertEqual(set(registry["providers"]), {provider["provider_id"] for provider in registry["providers"].values()})
        self.assertEqual(len(registry["capabilities"]), len({entry["capability_id"] for entry in registry["capabilities"]}))
        for provider in registry["providers"].values():
            self.assertTrue(PROVIDER_FIELDS.issubset(provider))
            self.assertIn(provider["discovery_status"], {"available", "unavailable", "blocked", "not_yet_verified"})
            self.assertIn(provider["execution_status"], {"available", "unavailable", "blocked", "not_yet_verified"})
            self.assertTrue(provider["compatibility_evidence"].strip())
            self.assertTrue(provider["unavailable_behavior"].strip())
        for capability in registry["capabilities"]:
            self.assertEqual(set(capability), CAPABILITY_FIELDS)
            self.assertTrue(set(capability["provider_ids"]).issubset(registry["providers"]))

    def test_expected_platform_intents_have_registry_entries(self):
        registry = load_registry()
        self.assertTrue(EXPECTED_CAPABILITIES.issubset({entry["capability_id"] for entry in registry["capabilities"]}))

    def test_route_matrix_maps_tasks_to_known_capabilities_and_requirements(self):
        registry = load_registry()
        known = {entry["capability_id"] for entry in registry["capabilities"]}
        approved_requirements = set(re.findall(r"\bREQ-\d{3}\b", SPEC_PATH.read_text()))
        with ROUTES_PATH.open(newline="") as source:
            routes = list(csv.DictReader(source))
        self.assertGreaterEqual(len(routes), 10)
        for row in routes:
            self.assertIn(row["capability_id"], known)
            self.assertRegex(row["requirement_ids"], r"^REQ-\d{3}(;REQ-\d{3})*$")
            self.assertTrue(set(row["requirement_ids"].split(";")).issubset(approved_requirements))
            self.assertTrue(row["focused_context"].strip())
            self.assertTrue(row["unavailable_behavior"].strip())
        for family in ("copilot_studio", "power_automate", "dataverse", "agent", "power_platform"):
            self.assertTrue(any(row["capability_id"].startswith(family) for row in routes), family)

    def test_unknown_capability_blocks_with_actionable_dependency(self):
        contract = REGISTRY_CONTRACT.read_text().lower()
        routing = ROUTING.read_text().lower()
        self.assertIn("unknown capability intent", contract)
        self.assertIn("blocked", contract)
        self.assertIn("no automatic fallback", contract)
        self.assertIn("only relevant requirement ids", routing)

    def test_ghcp_harness_is_conditional(self):
        routing = ROUTING.read_text().lower()
        self.assertIn("standard copilot studio", routing)
        self.assertIn("explicitly requested", routing)
        self.assertIn("material architectural advantage", routing)
        ghcp = next(item for item in load_registry()["capabilities"] if item["capability_id"] == "copilot_studio.ghcp.author")
        self.assertTrue(any(token in " ".join(ghcp["provider_ids"]).lower() for token in ("ghcp", "copilot")))


if __name__ == "__main__":
    unittest.main()

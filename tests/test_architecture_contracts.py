"""Contract checks for reviewable architecture decisions and golden cases."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".github/skills/m365-agent-factory/references/architecture-rules.md"
TEMPLATE = ROOT / "templates/architecture-decision.md"
FIXTURES = ROOT / "tests/fixtures/architecture"
DECISIONS = (
    "harness",
    "knowledge",
    "skills",
    "tools_actions",
    "power_automate",
    "dataverse_state",
    "agents",
    "external_integrations",
    "custom_development",
)
DECISION_LABELS = {
    "harness": "harness",
    "knowledge": "knowledge",
    "skills": "skills",
    "tools_actions": "tools/actions",
    "power_automate": "power automate",
    "dataverse_state": "dataverse/state",
    "agents": "additional agents",
    "external_integrations": "external integrations",
    "custom_development": "custom development",
}
EVIDENCE_STATES = {"verified", "available", "not_required", "not_yet_verified", "blocked"}


def load_case(name):
    return json.loads((FIXTURES / name).read_text())


class ArchitectureContractTests(unittest.TestCase):
    def test_rules_are_implemented_and_make_decisions_before_spec(self):
        rules = RULES.read_text()
        self.assertNotIn("planned, not implemented", rules.lower())
        for phrase in (
            "standard copilot studio",
            "material architectural advantage",
            "knowledge",
            "power automate",
            "dataverse",
            "meaningful boundary",
            "architecture precedes specification",
            "evidence status",
        ):
            self.assertIn(phrase, rules.lower())

    def test_decision_template_covers_components_rationale_and_evidence(self):
        template = TEMPLATE.read_text()
        for name in DECISIONS:
            self.assertIn(DECISION_LABELS[name], template.lower())
        for phrase in ("rationale", "evidence status", "dependency", "alternatives", "assumptions", "unresolved blockers"):
            self.assertIn(phrase, template.lower())

    def test_golden_architectures_have_complete_explained_decisions(self):
        for name in (
            "knowledge-only.json",
            "it-ticketing.json",
            "approval-workflow.json",
            "ambiguous-refund.json",
        ):
            with self.subTest(name=name):
                case = load_case(name)
                self.assertIn(case["status"], {"DECIDED", "DECIDED_WITH_UNRESOLVED_DEPENDENCIES", "CLARIFICATION_REQUIRED"})
                self.assertEqual(set(case["decisions"]), set(DECISIONS))
                for decision in case["decisions"].values():
                    self.assertTrue(decision["selection"].strip())
                    self.assertTrue(decision["rationale"].strip())
                    self.assertIn(decision["evidence_status"], EVIDENCE_STATES)

    def test_knowledge_only_uses_minimal_standard_architecture(self):
        decisions = load_case("knowledge-only.json")["decisions"]
        self.assertEqual(decisions["harness"]["selection"], "Standard Copilot Studio")
        self.assertIn("SharePoint", decisions["knowledge"]["selection"])
        self.assertEqual(decisions["power_automate"]["selection"], "Not required")
        self.assertEqual(decisions["dataverse_state"]["selection"], "Not required")
        self.assertEqual(decisions["agents"]["selection"], "One agent; no child agent")

    def test_approval_uses_flow_and_does_not_invent_state_owner(self):
        decisions = load_case("approval-workflow.json")["decisions"]
        self.assertEqual(decisions["power_automate"]["selection"], "Power Automate workflow")
        self.assertIn("authoritative", decisions["dataverse_state"]["selection"].lower())
        self.assertNotEqual(decisions["dataverse_state"]["selection"], "Dataverse")
        self.assertIn("named yet", decisions["dataverse_state"]["rationale"].lower())

    def test_ambiguous_refund_blocks_architecture_and_integration_invention(self):
        case = load_case("ambiguous-refund.json")
        self.assertEqual(case["status"], "CLARIFICATION_REQUIRED")
        self.assertEqual(case["decisions"]["external_integrations"]["selection"], "None selected")
        self.assertIn("refund", case["unresolved_blockers"][0].lower())

    def test_unverified_capabilities_are_never_marked_verified(self):
        for path in FIXTURES.glob("*.json"):
            case = json.loads(path.read_text())
            if case["status"] != "DECIDED":
                continue
            for decision in case["decisions"].values():
                if decision.get("dependency"):
                    self.assertNotEqual(decision["evidence_status"], "verified", path.name)


if __name__ == "__main__":
    unittest.main()

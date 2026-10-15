"""Contract checks for the skill's reviewable intake records and examples."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FACTORY_SKILL = ROOT / ".github/skills/m365-agent-factory/SKILL.md"
CLARIFICATION_POLICY = ROOT / ".github/skills/m365-agent-factory/references/clarification-policy.md"
OBJECTIVE_TEMPLATE = ROOT / "templates/objective.md"
FIXTURES = ROOT / "tests/fixtures/intake"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text())


class IntakeContractTests(unittest.TestCase):
    def test_skill_directs_context_first_minimal_grouped_clarification(self):
        skill = FACTORY_SKILL.read_text()
        policy = CLARIFICATION_POLICY.read_text()
        self.assertNotIn("NOT IMPLEMENTED", skill)
        for phrase in (
            "Inspect all supplied conversation and project context",
            "separate facts, assumptions, and unknowns",
            "materially change",
            "one grouped clarification round",
            "safe recommended defaults",
            "Do not draft architecture",
        ):
            self.assertIn(phrase.lower(), skill.lower())
        self.assertIn("consequential", policy.lower())

    def test_objective_template_records_source_and_decision_status(self):
        template = OBJECTIVE_TEMPLATE.read_text()
        for heading in (
            "## Objective",
            "## Context inspected",
            "## Explicit facts",
            "## Assumptions and safe defaults",
            "## Unknowns",
            "## Consequential questions",
            "## Clarification responses",
            "## Intake disposition",
        ):
            self.assertIn(heading, template)

    def test_fixtures_separate_facts_assumptions_and_unknowns(self):
        for name in ("knowledge-only.json", "ambiguous-refund.json"):
            with self.subTest(name=name):
                case = load_fixture(name)
                self.assertTrue(case["objective"].strip())
                self.assertTrue(case["facts"])
                self.assertIn("assumptions", case)
                self.assertIn("unknowns", case)
                unknown_ids = {item["id"] for item in case["unknowns"]}
                for question in case["clarification_rounds"]:
                    for unknown_id in question["unknown_refs"]:
                        self.assertIn(unknown_id, unknown_ids)
                for unknown in case["unknowns"]:
                    if unknown["ask_now"]:
                        self.assertTrue(unknown["material_impact"])

    def test_supplied_knowledge_context_needs_no_repeat_question(self):
        case = load_fixture("knowledge-only.json")
        self.assertIn("SharePoint policy documents", case["facts"])
        self.assertEqual(case["clarification_rounds"], [])
        deferred = [item for item in case["unknowns"] if not item["ask_now"]]
        self.assertTrue(deferred)
        self.assertTrue(all(item["disposition"] for item in deferred))

    def test_refund_unknowns_are_asked_in_one_group_without_invented_provider(self):
        case = load_fixture("ambiguous-refund.json")
        self.assertEqual(len(case["clarification_rounds"]), 1)
        self.assertTrue(case["clarification_rounds"][0]["questions"])
        self.assertEqual(case["integrations_to_create"], [])
        self.assertIn("commerce or payment system", " ".join(item["prompt"] for item in case["unknowns"]))
        self.assertTrue(any(item["recommended_default"] for item in case["unknowns"]))
        self.assertFalse(case["architecture_can_start"])


if __name__ == "__main__":
    unittest.main()

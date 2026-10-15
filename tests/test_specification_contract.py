"""Checks for the generated specification and its approval boundary."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates/agent-spec.md"
CONTRACT = ROOT / ".github/skills/m365-agent-factory/references/specification-contract.md"
SKILL = ROOT / ".github/skills/m365-agent-factory/SKILL.md"
FIXTURE = ROOT / "tests/fixtures/specification/knowledge-only-draft.md"
REQUIRED_SECTIONS = (
    "Objective", "Business outcome", "Users", "Channels", "Success criteria",
    "In scope", "Out of scope", "User scenarios", "Agent responsibilities",
    "Architecture", "Instructions", "Knowledge", "Skills", "Tools/actions",
    "Power Automate flows", "Dataverse", "External systems", "Identity/authentication",
    "Permissions", "Confirmation rules", "Failure handling", "Escalation",
    "Observability", "ALM/deployment", "Functional requirements",
    "Resilience requirements", "Evaluation plan", "Acceptance criteria", "Release gates",
    "Known assumptions", "Known dependencies", "Unresolved blockers", "Approval record",
)


class SpecificationContractTests(unittest.TestCase):
    def test_template_contains_every_specification_contract_section(self):
        template = TEMPLATE.read_text()
        headings = {line[3:].lower() for line in template.splitlines() if line.startswith("## ")}
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertTrue(any(section.lower() in heading for heading in headings), section)

    def test_mandatory_requirement_ids_are_stable_and_unique_in_draft_fixture(self):
        draft = FIXTURE.read_text()
        ids = re.findall(r"\bREQ-\d{3}\b", draft)
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("Mandatory", draft)

    def test_draft_accounts_for_unresolved_blockers_explicitly(self):
        draft = FIXTURE.read_text()
        section = draft.split("## Unresolved blockers", 1)[1].split("## Approval record", 1)[0]
        self.assertTrue(section.strip())
        self.assertRegex(section, r"(?i)(none identified|blocker:)")

    def test_no_quality_threshold_is_invented(self):
        template = TEMPLATE.read_text().lower()
        fixture = FIXTURE.read_text().lower()
        self.assertIn("supplied in the objective/context", template)
        self.assertIn("explicitly approved by the user", template)
        self.assertIn("not supplied", fixture)
        self.assertNotRegex(template + fixture, r"\b(?:90|95|99)\s*%")

    def test_generation_ends_awaiting_approval_and_never_approves_itself(self):
        contract = CONTRACT.read_text().lower()
        skill = SKILL.read_text().lower()
        for phrase in ("awaiting_approval", "generation alone", "explicit human", "approved_spec_sha256"):
            self.assertIn(phrase, contract)
        self.assertIn("never begin implementation before the specification is approved", skill)
        self.assertIn("awaiting_approval", TEMPLATE.read_text().lower())
        self.assertNotRegex(TEMPLATE.read_text(), r"(?m)^Status: APPROVED$")


if __name__ == "__main__":
    unittest.main()

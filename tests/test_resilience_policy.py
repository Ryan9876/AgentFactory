"""Policy contract checks for cross-cutting resilience guidance."""

import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/power-platform-resilience/SKILL.md"
REFERENCES = ROOT / ".agents/skills/power-platform-resilience/references"
MATRIX = ROOT / "tests/fixtures/resilience/scenario-coverage.csv"
SCENARIOS = {
    "knowledge-only", "it-ticketing", "approval-workflow", "ambiguous-objective",
    "interrupted-build", "spec-drift",
}
CONTROLS = {
    "identity", "least_privilege", "context", "confirmation", "retries",
    "retry_safety", "idempotency", "duplicate_prevention", "partial_failure",
    "recovery", "timeouts", "unavailable_dependencies", "permissions", "errors",
    "configuration", "secrets", "observability", "dlp_policy", "escalation",
}


class ResiliencePolicyTests(unittest.TestCase):
    def test_skill_is_reference_guidance_not_platform_execution(self):
        skill = SKILL.read_text().lower()
        self.assertNotIn("not implemented", skill)
        self.assertIn("policy/reference", skill)
        self.assertIn("does not execute platform changes", skill)
        self.assertIn("approved architecture", skill)

    def test_reference_guidance_covers_required_resilience_domains(self):
        content = "\n".join(path.read_text().lower() for path in REFERENCES.glob("*.md"))
        for term in (
            "least privilege", "user-context", "service-context", "confirmation",
            "retry", "idempotency", "duplicate", "partial failure", "recovery",
            "timeout", "unavailable", "permission", "connection reference",
            "environment variable", "secret", "correlation", "dlp", "escalation",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_scenario_matrix_covers_all_golden_scenarios_and_resilience_controls(self):
        with MATRIX.open(newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertTrue(rows)
        self.assertEqual(set(rows[0]), {"scenario", "control", "expected_review_evidence"})
        self.assertTrue(SCENARIOS.issubset({row["scenario"] for row in rows}))
        self.assertTrue(CONTROLS.issubset({row["control"] for row in rows}))
        for row in rows:
            self.assertTrue(row["expected_review_evidence"].strip())

    def test_policy_artifacts_contain_no_credential_material(self):
        paths = [SKILL, *REFERENCES.glob("*.md"), MATRIX]
        forbidden = re.compile(r"(?i)(client[_ -]?secret\s*[:=]\s*[^\s<]|password\s*[:=]\s*[^\s<]|bearer\s+[A-Za-z0-9._-]{16,})")
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIsNone(forbidden.search(path.read_text()))


if __name__ == "__main__":
    unittest.main()

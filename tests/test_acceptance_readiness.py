"""Checks the final acceptance record matches live evidence and release gates."""

import csv
import unittest
from pathlib import Path

from scripts.traceability_check import CSV_FIELDS, read_requirements, validate_traceability


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/m365-agent-factory-spec.md"
MATRIX = ROOT / "docs/acceptance-traceability.csv"
REPORT = ROOT / "docs/v1-acceptance.md"


class AcceptanceReadinessTests(unittest.TestCase):
    def test_acceptance_matrix_maps_every_mandatory_requirement_with_explicit_status(self):
        errors = []
        requirements = read_requirements(SPEC, errors)
        self.assertEqual(errors, [])
        with MATRIX.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, CSV_FIELDS)
            rows = list(reader)
        self.assertEqual({row["requirement_id"] for row in rows}, set(requirements))
        self.assertEqual(len(rows), len(requirements))
        self.assertTrue(all(row["status"].strip() for row in rows))
        statuses = {row["status"] for row in rows}
        self.assertIn("ORDERED_GATES_PASS_FINAL_VERDICT_SHIP", statuses)
        self.assertEqual(validate_traceability(SPEC, MATRIX, release=True), [])

    def test_acceptance_report_records_pilot_passes_and_final_verifier_ship(self):
        report = REPORT.read_text()
        self.assertIn("## Release verdict\n\n**SHIP**", report)
        self.assertIn("Development-environment pilot", report)
        self.assertIn("14F Functional execution | **PASS**", report)
        self.assertIn("14G Evaluation | **PASS**", report)
        self.assertIn("**Task 15 — COMPLETE.**", report)
        self.assertIn("Copilot Studio", report)

    def test_readme_and_installation_report_actual_partial_status(self):
        readme = (ROOT / "README.md").read_text().lower()
        installation = (ROOT / "docs/installation.md").read_text().lower()
        self.assertIn("codex-first", readme)
        self.assertIn("host skill discovery", readme)
        self.assertNotIn("skill files remain marked **not implemented**", readme)
        self.assertIn("development environment identification blocked", installation)


if __name__ == "__main__":
    unittest.main()

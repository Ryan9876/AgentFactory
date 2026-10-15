"""Black-box coverage tests for the requirement traceability CLI."""

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "traceability_check.py"
HEADER = [
    "requirement_id",
    "requirement_summary",
    "mandatory",
    "implementation_artifact",
    "implementation_evidence",
    "verification_id",
    "verification_evidence",
    "status",
]


class TraceabilityCheckTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.spec = self.root / "spec.md"
        self.traceability = self.root / "traceability.csv"
        self.write_spec(
            "- **REQ-001 (mandatory):** Required behavior.\n"
            "- **REQ-002 (optional):** Optional behavior.\n"
        )

    def write_spec(self, content):
        self.spec.write_text(content)

    def row(self, requirement_id="REQ-001", **overrides):
        result = {
            "requirement_id": requirement_id,
            "requirement_summary": "Required behavior",
            "mandatory": "true",
            "implementation_artifact": "src/agent.md",
            "implementation_evidence": "reviewed artifact",
            "verification_id": "TEST-001",
            "verification_evidence": "test passed",
            "status": "VERIFIED",
        }
        result.update(overrides)
        return result

    def write_rows(self, rows):
        with self.traceability.open("w", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(rows)

    def run_cli(self, *options):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--spec",
                str(self.spec),
                "--traceability",
                str(self.traceability),
                *options,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_complete_mandatory_coverage_passes_with_optional_requirement_absent(self):
        self.write_rows([self.row()])
        result = self.run_cli("--release")
        self.assertEqual(result.returncode, 0)
        self.assertIn("passed", result.stdout.lower())
        self.assertEqual(result.stderr, "")

    def test_missing_mandatory_requirement_fails(self):
        self.write_rows([])
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("REQ-001", result.stderr)
        self.assertIn("missing", result.stderr.lower())

    def test_unknown_requirement_fails(self):
        self.write_rows([self.row(), self.row("REQ-999")])
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown requirement REQ-999", result.stderr)

    def test_missing_implementation_artifact_or_evidence_fails(self):
        for field in ("implementation_artifact", "implementation_evidence"):
            with self.subTest(field=field):
                self.write_rows([self.row(**{field: ""})])
                result = self.run_cli()
                self.assertEqual(result.returncode, 1)
                self.assertIn(field, result.stderr)

    def test_verification_evidence_is_required_only_in_release_mode(self):
        self.write_rows([self.row(verification_id="", verification_evidence="")])
        non_release = self.run_cli()
        release = self.run_cli("--release")
        self.assertEqual(non_release.returncode, 0)
        self.assertEqual(release.returncode, 1)
        self.assertIn("verification_id", release.stderr)
        self.assertIn("verification_evidence", release.stderr)

    def test_duplicate_requirement_mapping_fails(self):
        self.write_rows([self.row(), self.row()])
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate", result.stderr.lower())

    def test_invalid_requirement_identifier_fails(self):
        self.write_rows([self.row("REQ-01")])
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("REQ-NNN", result.stderr)

    def test_optional_requirement_row_does_not_require_implementation_evidence(self):
        optional = self.row(
            "REQ-002",
            requirement_summary="Optional behavior",
            mandatory="false",
            implementation_artifact="",
            implementation_evidence="",
        )
        self.write_rows([self.row(), optional])
        result = self.run_cli("--release")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_requirement_table_definition_is_recognized(self):
        self.write_spec(
            "## Functional requirements\n"
            "| ID | Mandatory | Requirement |\n"
            "|---|---|---|\n"
            "| REQ-003 | true | Table requirement |\n"
        )
        self.write_rows(
            [self.row("REQ-003", requirement_summary="Table requirement")]
        )
        result = self.run_cli("--release")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_csv_header_fails(self):
        self.traceability.write_text("id,summary\nREQ-001,Required behavior\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("header", result.stderr.lower())

    def test_malformed_requirement_definition_fails(self):
        self.write_spec("- **REQ-1 (mandatory):** Malformed ID.\n")
        self.write_rows([])
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("malformed requirement", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()

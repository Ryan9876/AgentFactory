"""Black-box tests for the deterministic approved-spec hash CLI."""

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "spec_hash.py"


class SpecHashTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.spec_path = self.root / ".agent-factory" / "spec.md"
        self.spec_path.parent.mkdir()
        self.spec_path.write_bytes(b"approved spec\n")

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_emits_known_lowercase_digest_with_explicit_project_root(self):
        expected = hashlib.sha256(b"approved spec\n").hexdigest()
        result = self.run_cli("--project-root", str(self.root))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, expected + "\n")
        self.assertEqual(result.stderr, "")

    def test_defaults_project_root_to_current_directory(self):
        expected = hashlib.sha256(b"approved spec\n").hexdigest()
        result = self.run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, expected + "\n")

    def test_approved_digest_match_succeeds(self):
        expected = hashlib.sha256(b"approved spec\n").hexdigest()
        result = self.run_cli("--approved-hash", expected)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, expected + "\n")

    def test_changed_spec_reports_spec_changed(self):
        approved = hashlib.sha256(b"approved spec\n").hexdigest()
        self.spec_path.write_bytes(b"changed spec\n")
        result = self.run_cli("--approved-hash", approved)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "SPEC_CHANGED\n")
        self.assertEqual(result.stderr, "")

    def test_missing_spec_has_deterministic_diagnostic(self):
        self.spec_path.unlink()
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn(".agent-factory/spec.md", result.stderr)

    def test_malformed_approved_hash_is_rejected(self):
        result = self.run_cli("--approved-hash", "not-a-digest")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("64 hexadecimal", result.stderr)


if __name__ == "__main__":
    unittest.main()

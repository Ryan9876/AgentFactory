"""Structural contract checks for generated Agent Factory project artifacts."""

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
SPEC = (ROOT / "docs/specs/m365-agent-factory-spec.md").read_text()


def allowed_states():
    block = SPEC.split("V1 state values are exactly:", 1)[1].split("```", 2)[1]
    return {line.strip() for line in block.splitlines() if line.strip()}


def markdown_table_header(path):
    for line in path.read_text().splitlines():
        if line.startswith("|") and "---" not in line:
            return [cell.strip().lower() for cell in line.strip("|").split("|")]
    return []


class ArtifactContractTests(unittest.TestCase):
    def test_state_template_has_resume_and_approval_fields(self):
        state = json.loads((TEMPLATES / "state.json").read_text())
        self.assertEqual(state["schema_version"], 1)
        self.assertIn(state["state"], allowed_states())
        self.assertIsNone(state["approved_spec_sha256"])
        self.assertIn("manifest_progress", state)
        self.assertIsInstance(state["manifest_progress"]["completed_task_ids"], list)
        self.assertIsNone(state["manifest_progress"]["next_task_id"])
        for key in (
            "project_id",
            "target_environment",
            "manifest_path",
            "traceability_path",
            "blockers",
            "updated_at",
        ):
            self.assertIn(key, state)

    def test_traceability_template_uses_exact_header(self):
        with (TEMPLATES / "traceability.csv").open(newline="") as source:
            header = next(csv.reader(source))
        self.assertEqual(
            header,
            [
                "requirement_id",
                "requirement_summary",
                "mandatory",
                "implementation_artifact",
                "implementation_evidence",
                "verification_id",
                "verification_evidence",
                "status",
            ],
        )

    def test_manifest_links_requirements_to_owner_and_evidence(self):
        header = markdown_table_header(TEMPLATES / "build-manifest.md")
        self.assertEqual(
            header,
            [
                "task id",
                "dependencies",
                "requirement ids",
                "owning capability",
                "provider",
                "output artifact",
                "status",
                "implementation evidence",
                "verification evidence",
                "artifact inspection evidence",
            ],
        )
        manifest = (TEMPLATES / "build-manifest.md").read_text()
        for required in ("Task ID", "Dependencies", "Requirement IDs", "Owning capability", "Status", "Implementation evidence"):
            self.assertIn(required, manifest)

    def test_agent_spec_template_has_required_contract_sections(self):
        spec = (TEMPLATES / "agent-spec.md").read_text()
        for section in (
            "## Objective",
            "## Business outcome",
            "## Architecture (link decision record)",
            "## Functional requirements",
            "## Resilience requirements",
            "## Evaluation plan",
            "## Acceptance criteria",
            "## Known assumptions",
            "## Known dependencies",
            "## Unresolved blockers",
            "## Approval record",
        ):
            self.assertIn(section, spec)

    def test_supporting_templates_have_required_acceptance_fields(self):
        architecture = (TEMPLATES / "architecture-decision.md").read_text()
        for field in ("Harness", "Knowledge", "Skills", "Tools/actions", "Power Automate", "Dataverse/state owner", "Additional agents", "Alternatives considered"):
            self.assertIn(field, architecture)
        acceptance = (TEMPLATES / "acceptance-report.md").read_text()
        for field in (
            "Agent",
            "Environment",
            "Approved spec hash",
            "Architecture",
            "Built components",
            "Evaluation result",
            "Requirement coverage",
            "Known limitations",
            "Manual deployment steps",
            "Remaining admin approvals",
            "Release verdict",
        ):
            self.assertIn(field, acceptance)

    def test_templates_do_not_contain_live_identifiers_or_credentials(self):
        patterns = (
            re.compile(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", re.I),
            re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
            re.compile(r"https?://", re.I),
            re.compile(r"-----BEGIN .*PRIVATE KEY-----"),
        )
        for path in TEMPLATES.iterdir():
            if path.is_file():
                content = path.read_text()
                for pattern in patterns:
                    self.assertIsNone(pattern.search(content), f"live value pattern in {path.name}")


if __name__ == "__main__":
    unittest.main()

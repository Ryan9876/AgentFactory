"""Test-first coverage for evidence-driven remediation routing."""

import tempfile
import unittest
from pathlib import Path

from scripts import remediation

ROOT = Path(__file__).resolve().parents[1]


class RemediationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.spec = Path(self.temporary.name) / "spec.md"
        self.spec.write_text(
            "- **REQ-021 (mandatory):** Build the approved flow.\n"
            "- **REQ-022 (mandatory):** Confirm the requested side effect.\n"
        )
        self.tasks = [
            {
                "task_id": "TASK-001", "requirement_ids": ["REQ-021"],
                "owning_capability": "power_automate.flow.build",
                "output_artifact": "flows/request-approval",
            },
            {
                "task_id": "TASK-002", "requirement_ids": ["REQ-022"],
                "owning_capability": "copilot_studio.standard.author",
                "output_artifact": "agents/request-agent",
            },
        ]

    def tearDown(self):
        self.temporary.cleanup()

    def test_routes_to_smallest_manifest_component_with_focused_requirement_context(self):
        result = remediation.route_finding(
            {"finding_id": "FIND-001", "requirement_ids": ["REQ-021"], "summary": "Flow branch is missing."},
            self.tasks,
            self.spec,
        )
        self.assertEqual(result["verdict"], "ITERATE")
        self.assertEqual(result["owner"], {
            "task_id": "TASK-001", "component": "flows/request-approval",
            "capability_id": "power_automate.flow.build",
        })
        self.assertEqual(result["focused_context"], [
            {"requirement_id": "REQ-021", "summary": "Build the approved flow."}
        ])
        self.assertEqual(result["component_retests"], ["TASK-001"])
        self.assertEqual(result["release_reruns"], list(remediation.RELEASE_GATES))

    def test_explicit_component_selects_smallest_owner_for_shared_requirement(self):
        duplicate_scope = [self.tasks[0], {
            "task_id": "TASK-003", "requirement_ids": ["REQ-021"],
            "owning_capability": "power_automate.flow.validate",
            "output_artifact": "flows/request-approval/tests",
        }]
        result = remediation.route_finding(
            {"requirement_ids": ["REQ-021"], "component": "TASK-003", "summary": "Validation assertion is wrong."},
            duplicate_scope,
            self.spec,
        )
        self.assertEqual(result["owner"]["task_id"], "TASK-003")
        self.assertEqual(result["owner"]["capability_id"], "power_automate.flow.validate")

    def test_unrouteable_and_ambiguous_findings_remain_blocked(self):
        unknown = remediation.route_finding(
            {"requirement_ids": ["REQ-999"], "summary": "Unknown requirement."}, self.tasks, self.spec
        )
        self.assertEqual(unknown["verdict"], "BLOCK")
        self.assertIsNone(unknown["owner"])

        shared = [self.tasks[0], dict(self.tasks[0], task_id="TASK-003", output_artifact="flow/other")]
        ambiguous = remediation.route_finding(
            {"requirement_ids": ["REQ-021"], "summary": "Shared requirement issue."}, shared, self.spec
        )
        self.assertEqual(ambiguous["verdict"], "BLOCK")
        self.assertIsNone(ambiguous["owner"])

    def test_requirement_change_requires_proposal_and_spec_reapproval(self):
        result = remediation.route_finding(
            {"requirement_ids": ["REQ-021"], "summary": "Requirement may need revision.", "requires_spec_change": True},
            self.tasks,
            self.spec,
        )
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["status"], "SPEC_CHANGE_PROPOSED")
        self.assertEqual(result["next_action"], "prepare_spec_change_for_explicit_reapproval")
        self.assertIn("SPEC_CHANGED", result["change_control"]["integrity_state_after_spec_edit"])

    def test_remediation_never_rewrites_requirement_text(self):
        original = self.spec.read_bytes()
        remediation.route_finding(
            {"requirement_ids": ["REQ-021"], "summary": "Failing behavior.", "requires_spec_change": True},
            self.tasks,
            self.spec,
        )
        self.assertEqual(self.spec.read_bytes(), original)

    def test_invalid_finding_or_manifest_is_blocked(self):
        result = remediation.route_finding({}, self.tasks, self.spec)
        self.assertEqual(result["verdict"], "BLOCK")
        bad_manifest = remediation.route_finding(
            {"requirement_ids": ["REQ-021"], "summary": "Issue."}, [{"task_id": "TASK-001"}], self.spec
        )
        self.assertEqual(bad_manifest["verdict"], "BLOCK")

    def test_skill_documents_component_retest_release_rerun_and_reapproval(self):
        skill = (ROOT / ".github/skills/agent-spec-verifier/SKILL.md").read_text().lower()
        guidance = (ROOT / ".github/skills/agent-spec-verifier/references/remediation-routing.md").read_text().lower()
        for phrase in ("smallest owning component", "retest", "release gate", "explicit approval", "do not edit"):
            self.assertIn(phrase, guidance)
        self.assertIn("unrouteable findings stay `block`", skill)


if __name__ == "__main__":
    unittest.main()

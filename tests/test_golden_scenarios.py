"""Executable acceptance checks for the six approved V1 scenarios."""

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import agent_spec_verifier, build_state
from scripts.traceability_check import validate_traceability


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "tests/scenarios"
ARCHITECTURE = ROOT / "tests/fixtures/architecture"
INTAKE = ROOT / "tests/fixtures/intake"


def architecture(name):
    return json.loads((ARCHITECTURE / name).read_text())


def intake(name):
    return json.loads((INTAKE / name).read_text())


def state_for(current, digest=None):
    return {
        "schema_version": 1,
        "state": current,
        "project_id": None,
        "target_environment": "Development",
        "approved_spec_sha256": digest,
        "manifest_path": "build-manifest.md",
        "manifest_progress": {"completed_task_ids": [], "next_task_id": None},
        "traceability_path": "traceability.csv",
        "blockers": [],
        "updated_at": None,
    }


class GoldenScenarioTests(unittest.TestCase):
    def test_knowledge_only_uses_minimal_architecture_without_flow_data_or_child_agent(self):
        case = architecture("knowledge-only.json")
        decisions = case["decisions"]
        self.assertEqual(case["status"], "DECIDED_WITH_UNRESOLVED_DEPENDENCIES")
        self.assertEqual(case["unresolved_blockers"], [])
        self.assertEqual(decisions["harness"]["selection"], "Declarative agent")
        self.assertIn("SharePoint", decisions["knowledge"]["selection"])
        self.assertEqual(decisions["power_automate"]["selection"], "Not required")
        self.assertEqual(decisions["dataverse_state"]["selection"], "Not required")
        self.assertEqual(decisions["agents"]["selection"], "One agent; no child agent")
        self.assertIn("no power automate", (SCENARIOS / "knowledge-only.md").read_text().lower())

    def test_knowledge_only_traceability_and_release_verdict_follow_architecture(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            control = project / ".agent-factory"
            control.mkdir()
            spec = control / "spec.md"
            spec.write_text(
                "# HR knowledge agent\n\n"
                "- **REQ-001 (mandatory):** Answer HR policy questions from approved SharePoint documents.\n"
                "- **REQ-002 (mandatory):** Do not create a flow, Dataverse store, or child agent without a new requirement.\n\n"
                "## Unresolved blockers\nNone identified.\n"
            )
            traceability = control / "traceability.csv"
            with traceability.open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow([
                    "requirement_id", "requirement_summary", "mandatory", "implementation_artifact",
                    "implementation_evidence", "verification_id", "verification_evidence", "status",
                ])
                writer.writerow(["REQ-001", "SharePoint grounded answers", "true", "agent", "knowledge source inspected", "TEST-001", "grounding test result", "VERIFIED"])
                writer.writerow(["REQ-002", "Minimal components", "true", "architecture", "decision record inspected", "TEST-002", "architecture assertions passed", "VERIFIED"])
            self.assertEqual(validate_traceability(spec, traceability, release=True), [])

            state = state_for("VERIFYING", hashlib.sha256(spec.read_bytes()).hexdigest())
            build_state.save_state(control / "state.json", state)
            evidence = {
                "platform_validation": {"status": "pass", "evidence": "synthetic platform evidence fixture"},
                "functional_verification": {"status": "pass", "evidence": "synthetic scenario evidence fixture"},
                "evaluation": {"status": "pass", "evidence": "synthetic evaluation evidence fixture", "thresholds_approved": True, "thresholds_source": "synthetic approved fixture"},
                "resilience_review": {"status": "pass", "evidence": "synthetic resilience evidence fixture", "unsafe": False},
            }
            result = agent_spec_verifier.verify_release(project, evidence)
            self.assertEqual(result["verdict"], "SHIP")
            self.assertEqual(result["state"], "READY_TO_PACKAGE")

    def test_it_ticketing_keeps_ticket_integration_uninvented_and_covers_side_effect(self):
        case = architecture("it-ticketing.json")
        decisions = case["decisions"]
        self.assertIn("internal incident documentation", decisions["knowledge"]["selection"].lower())
        self.assertIn("ticket", decisions["tools_actions"]["selection"].lower())
        self.assertTrue(decisions["dataverse_state"]["selection"].startswith("Not required"))
        combined = json.dumps(case).lower()
        self.assertTrue("confirm" in combined or "confirmation" in combined)
        self.assertIn("never invent connector operations", (SCENARIOS / "it-ticketing.md").read_text())

    def test_approval_workflow_selects_flow_and_leaves_authoritative_state_owner_open(self):
        case = architecture("approval-workflow.json")
        decisions = case["decisions"]
        self.assertIn("power automate", decisions["power_automate"]["selection"].lower())
        self.assertIn("authoritative", decisions["dataverse_state"]["selection"].lower())
        self.assertNotEqual(decisions["dataverse_state"]["selection"], "Dataverse")
        self.assertIn("recovery", json.dumps(case).lower())
        self.assertIn("authoritative persistent state source", (SCENARIOS / "approval-workflow.md").read_text())

    def test_ambiguous_refund_requests_one_group_and_does_not_invent_integration(self):
        case = intake("ambiguous-refund.json")
        decision = architecture("ambiguous-refund.json")
        self.assertEqual(len(case["clarification_rounds"]), 1)
        self.assertFalse(case["integrations_to_create"])
        self.assertFalse(case["architecture_can_start"])
        self.assertEqual(decision["status"], "CLARIFICATION_REQUIRED")
        self.assertEqual(decision["decisions"]["external_integrations"]["selection"], "None selected")

    def test_interrupted_build_reuses_only_inspected_verified_work_and_resumes_first_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / ".agent-factory/spec.md"
            spec.parent.mkdir()
            spec.write_text("approved spec\n")
            state = state_for("BUILDING", hashlib.sha256(spec.read_bytes()).hexdigest())
            self.assertTrue(build_state.verify_spec_integrity(state, spec, "resume"))
            tasks = [
                {"task_id": "TASK-001", "dependencies": [], "requirement_ids": ["REQ-001"], "owning_capability": "copilot_studio.standard.author", "output_artifact": "agent", "status": "VERIFIED", "implementation_evidence": "built", "verification_evidence": "verified"},
                {"task_id": "TASK-002", "dependencies": ["TASK-001"], "requirement_ids": ["REQ-002"], "owning_capability": "power_automate.flow.build", "output_artifact": "flow", "status": "IN_PROGRESS", "implementation_evidence": "started", "verification_evidence": ""},
            ]
            inspections = {
                "TASK-001": {"inspected": True, "artifact_present": True, "outcome": "complete", "inspection_evidence": "agent inspected", "verification_evidence": "prior test inspected"},
                "TASK-002": {"inspected": True, "artifact_present": False, "outcome": "incomplete", "inspection_evidence": "no flow artifact exists"},
            }
            resumed, next_task = build_state.resume_manifest(state, tasks, inspections)
            self.assertEqual(next_task, "TASK-002")
            self.assertEqual([task["status"] for task in resumed], ["VERIFIED", "READY"])
            self.assertEqual(state["manifest_progress"]["completed_task_ids"], ["TASK-001"])

    def test_spec_drift_sets_spec_changed_and_verifier_blocks_before_later_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / ".agent-factory"
            control.mkdir()
            spec = control / "spec.md"
            spec.write_text("# Approved\n- **REQ-001 (mandatory):** Existing requirement.\n")
            state = state_for("VERIFYING", hashlib.sha256(spec.read_bytes()).hexdigest())
            build_state.save_state(control / "state.json", state)
            with (control / "traceability.csv").open("w", newline="") as stream:
                csv.writer(stream).writerow([
                    "requirement_id", "requirement_summary", "mandatory", "implementation_artifact",
                    "implementation_evidence", "verification_id", "verification_evidence", "status",
                ])
            spec.write_text(spec.read_text() + "\nchanged\n")
            result = agent_spec_verifier.verify_release(root, {})
            self.assertEqual(result["verdict"], "BLOCK")
            self.assertEqual(result["state"], "SPEC_CHANGED")
            self.assertTrue(all(gate["status"] == "NOT_RUN" for gate in result["gates"][1:]))

    def test_each_approved_scenario_has_machine_checked_expectations(self):
        expected_files = {
            "knowledge-only.md", "it-ticketing.md", "approval-workflow.md",
            "ambiguous-objective.md", "interrupted-build.md", "spec-drift.md",
        }
        self.assertEqual({path.name for path in SCENARIOS.glob("*.md")}, expected_files)
        for filename in expected_files:
            with self.subTest(scenario=filename):
                self.assertIn("Expected", (SCENARIOS / filename).read_text())


if __name__ == "__main__":
    unittest.main()

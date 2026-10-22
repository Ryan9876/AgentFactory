"""TDD checks for ordered release verification and evidence-based verdicts."""

import csv
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import agent_spec_verifier
from scripts.build_state import load_state, save_state


ROOT = Path(__file__).resolve().parents[1]
VERIFIER_SKILL = ROOT / ".agents/skills/agent-spec-verifier/SKILL.md"
VERIFIER_REFERENCES = ROOT / ".agents/skills/agent-spec-verifier/references"


def project_with_evidence(directory):
    root = Path(directory)
    control = root / ".agent-factory"
    control.mkdir()
    spec = control / "spec.md"
    spec.write_text(
        "# Approved agent spec\n\n"
        "- **REQ-001 (mandatory):** Answer from approved knowledge.\n"
        "## Unresolved blockers\nNone identified.\n"
    )
    state = {
        "schema_version": 1,
        "state": "VERIFYING",
        "project_id": None,
        "target_environment": "Development",
        "approved_spec_sha256": hashlib.sha256(spec.read_bytes()).hexdigest(),
        "manifest_path": "build-manifest.md",
        "manifest_progress": {"completed_task_ids": ["TASK-001"], "next_task_id": None},
        "traceability_path": "traceability.csv",
        "blockers": [],
        "updated_at": None,
    }
    save_state(control / "state.json", state)
    with (control / "traceability.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "requirement_id", "requirement_summary", "mandatory", "implementation_artifact",
            "implementation_evidence", "verification_id", "verification_evidence", "status",
        ])
        writer.writerow(["REQ-001", "Answer from approved knowledge", "true", "agent", "artifact inspected", "TEST-001", "test result saved", "VERIFIED"])
    evidence = {
        "platform_validation": {"status": "pass", "evidence": "platform validation report"},
        "functional_verification": {"status": "pass", "evidence": "functional test report"},
        "evaluation": {"status": "pass", "evidence": "approved evaluation results", "thresholds_approved": True, "thresholds_source": "approved specification"},
        "resilience_review": {"status": "pass", "evidence": "resilience review report", "unsafe": False},
    }
    return root, control, spec, evidence


class AgentSpecVerifierTests(unittest.TestCase):
    def test_skill_and_references_encode_the_gate_order_and_verdict_boundaries(self):
        skill = VERIFIER_SKILL.read_text().lower()
        protocol = (VERIFIER_REFERENCES / "verification-protocol.md").read_text().lower()
        verdicts = (VERIFIER_REFERENCES / "verdict-rules.md").read_text().lower()
        self.assertNotIn("not implemented", skill)
        for phrase in (
            "spec integrity", "requirement coverage", "platform validation",
            "functional verification", "evaluation", "resilience review",
        ):
            self.assertIn(phrase, protocol)
        self.assertIn("ship", verdicts)
        self.assertIn("iterate", verdicts)
        self.assertIn("block", verdicts)
        self.assertIn("does not author or execute", skill)

    def test_all_release_gates_pass_in_required_order_for_ship(self):
        with tempfile.TemporaryDirectory() as directory:
            root, control, _, evidence = project_with_evidence(directory)
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertEqual(result["verdict"], "SHIP")
            self.assertEqual([gate["name"] for gate in result["gates"]], [
                "spec_integrity", "requirement_coverage", "platform_validation",
                "functional_verification", "evaluation", "resilience_review",
            ])
            self.assertTrue(all(gate["status"] == "PASS" for gate in result["gates"]))
            self.assertEqual(load_state(control / "state.json")["state"], "READY_TO_PACKAGE")

    def test_missing_optional_blocker_section_does_not_block_ship(self):
        with tempfile.TemporaryDirectory() as directory:
            root, control, spec, evidence = project_with_evidence(directory)
            spec.write_text(
                "# Approved agent spec\n\n"
                "- **REQ-001 (mandatory):** Answer from approved knowledge.\n"
            )
            state = load_state(control / "state.json")
            state["approved_spec_sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
            save_state(control / "state.json", state)

            result = agent_spec_verifier.verify_release(root, evidence)

            self.assertEqual(result["verdict"], "SHIP")
            self.assertFalse(result["findings"])

    def test_spec_drift_blocks_and_does_not_run_later_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root, control, spec, evidence = project_with_evidence(directory)
            spec.write_text(spec.read_text() + "\nchanged\n")
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertEqual(result["verdict"], "BLOCK")
            self.assertEqual(result["gates"][0]["status"], "FAIL")
            self.assertTrue(all(gate["status"] == "NOT_RUN" for gate in result["gates"][1:]))
            self.assertEqual(load_state(control / "state.json")["state"], "SPEC_CHANGED")

    def test_missing_mandatory_release_evidence_iterates_before_platform_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root, control, _, evidence = project_with_evidence(directory)
            with (control / "traceability.csv").open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow([
                    "requirement_id", "requirement_summary", "mandatory", "implementation_artifact",
                    "implementation_evidence", "verification_id", "verification_evidence", "status",
                ])
                writer.writerow(["REQ-001", "Answer from approved knowledge", "true", "agent", "", "", "", "PENDING"])
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertEqual(result["verdict"], "ITERATE")
            self.assertEqual(result["gates"][1]["status"], "FAIL")
            self.assertTrue(all(gate["status"] == "NOT_RUN" for gate in result["gates"][2:]))
            self.assertEqual(load_state(control / "state.json")["state"], "ITERATING")

    def test_failed_gate_routes_to_iteration_and_stops_later_checks(self):
        for key, gate_name in (
            ("platform_validation", "platform_validation"),
            ("functional_verification", "functional_verification"),
            ("evaluation", "evaluation"),
            ("resilience_review", "resilience_review"),
        ):
            with self.subTest(gate=gate_name), tempfile.TemporaryDirectory() as directory:
                root, _, _, evidence = project_with_evidence(directory)
                evidence[key]["status"] = "fail"
                result = agent_spec_verifier.verify_release(root, evidence)
                self.assertEqual(result["verdict"], "ITERATE")
                failed_index = next(index for index, gate in enumerate(result["gates"]) if gate["name"] == gate_name)
                self.assertEqual(result["gates"][failed_index]["status"], "FAIL")
                self.assertTrue(all(gate["status"] == "NOT_RUN" for gate in result["gates"][failed_index + 1:]))

    def test_blocked_dependency_and_unapproved_thresholds_block(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _, _, evidence = project_with_evidence(directory)
            evidence["platform_validation"]["status"] = "blocked"
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertEqual(result["verdict"], "BLOCK")
            self.assertEqual(result["gates"][2]["status"], "BLOCKED")

        with tempfile.TemporaryDirectory() as directory:
            root, _, _, evidence = project_with_evidence(directory)
            evidence["evaluation"]["thresholds_approved"] = False
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertEqual(result["verdict"], "BLOCK")
            self.assertEqual(result["gates"][4]["status"], "BLOCKED")

    def test_unresolved_blocker_prevents_ship_after_all_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root, control, _, evidence = project_with_evidence(directory)
            state = load_state(control / "state.json")
            state["blockers"] = ["Authoritative state owner remains unresolved."]
            save_state(control / "state.json", state)
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertEqual(result["verdict"], "BLOCK")
            self.assertTrue(all(gate["status"] == "PASS" for gate in result["gates"]))
            self.assertIn("unresolved blocker", " ".join(result["findings"]).lower())

    def test_only_allowed_verdicts_are_emitted(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _, _, evidence = project_with_evidence(directory)
            result = agent_spec_verifier.verify_release(root, evidence)
            self.assertIn(result["verdict"], {"SHIP", "ITERATE", "BLOCK"})

    def test_cli_emits_a_structured_verdict_from_evidence_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _, _, evidence = project_with_evidence(directory)
            evidence_path = root / "evidence.json"
            evidence_path.write_text(json.dumps(evidence))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = agent_spec_verifier.main([
                    "--project-root", str(root), "--evidence-file", str(evidence_path),
                ])
            result = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(result["verdict"], "SHIP")


if __name__ == "__main__":
    unittest.main()

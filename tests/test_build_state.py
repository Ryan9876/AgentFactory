"""TDD coverage for manifest ordering, integrity gates, and resumable state."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build_state


def base_state(current="AWAITING_APPROVAL"):
    return {
        "schema_version": 1,
        "state": current,
        "project_id": None,
        "target_environment": None,
        "approved_spec_sha256": None,
        "manifest_path": "build-manifest.md",
        "manifest_progress": {"completed_task_ids": [], "next_task_id": None},
        "traceability_path": "traceability.csv",
        "blockers": [],
        "updated_at": None,
    }


def spec_states():
    spec = (Path(__file__).resolve().parents[1] / "docs/specs/m365-agent-factory-spec.md").read_text()
    block = spec.split("V1 state values are exactly:", 1)[1].split("```", 2)[1]
    return {line.strip() for line in block.splitlines() if line.strip() and line.strip() != "text"}


def sample_tasks():
    return [
        {
            "task_id": "TASK-002", "dependencies": ["TASK-001"], "requirement_ids": ["REQ-002"],
            "owning_capability": "power_automate.flow.build", "output_artifact": "flow",
            "status": "PENDING", "implementation_evidence": "", "verification_evidence": "",
        },
        {
            "task_id": "TASK-001", "dependencies": [], "requirement_ids": ["REQ-001"],
            "owning_capability": "copilot_studio.standard.author", "output_artifact": "agent",
            "status": "PENDING", "implementation_evidence": "", "verification_evidence": "",
        },
    ]


class BuildStateTests(unittest.TestCase):
    def test_state_enum_matches_authoritative_spec_exactly(self):
        self.assertEqual(build_state.STATES, spec_states())

    def test_invalid_lifecycle_transition_is_rejected(self):
        state = base_state("OBJECTIVE_CAPTURED")
        with self.assertRaises(build_state.BuildStateError):
            build_state.transition_state(state, "BUILDING")
        self.assertEqual(state["state"], "OBJECTIVE_CAPTURED")

    def test_only_explicit_approval_records_spec_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            spec = project / ".agent-factory/spec.md"
            spec.parent.mkdir()
            spec.write_text("approved draft\n")
            state = base_state()
            with self.assertRaises(build_state.BuildStateError):
                build_state.approve_spec(state, spec, explicit_approval=False)
            self.assertIsNone(state["approved_spec_sha256"])
            digest = build_state.approve_spec(state, spec, explicit_approval=True)
            self.assertEqual(digest, hashlib.sha256(spec.read_bytes()).hexdigest())
            self.assertEqual(state["approved_spec_sha256"], digest)
            self.assertEqual(state["state"], "APPROVED")

    def test_spec_drift_blocks_initial_build_and_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "spec.md"
            spec.write_text("original\n")
            approved = hashlib.sha256(spec.read_bytes()).hexdigest()
            spec.write_text("changed\n")
            for phase, current in (("build", "APPROVED"), ("resume", "BUILDING"), ("final_verification", "VERIFYING")):
                with self.subTest(phase=phase):
                    state = base_state(current)
                    state["approved_spec_sha256"] = approved
                    self.assertFalse(build_state.verify_spec_integrity(state, spec, phase))
                    self.assertEqual(state["state"], "SPEC_CHANGED")
                    self.assertTrue(state["blockers"])

    def test_manifest_generation_checks_approval_and_dependency_orders_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "spec.md"
            spec.write_text("- **REQ-001 (mandatory):** Create an agent.\n- **REQ-002 (mandatory):** Create a flow.\n")
            state = base_state("APPROVED")
            state["approved_spec_sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
            architecture = {"status": "DECIDED", "accepted": True}
            tasks = sample_tasks()
            ordered = build_state.generate_manifest_tasks(
                state, spec, architecture, tasks,
                {"copilot_studio.standard.author", "power_automate.flow.build"},
            )
            self.assertEqual([task["task_id"] for task in ordered], ["TASK-001", "TASK-002"])
            self.assertEqual([task["status"] for task in ordered], ["PENDING", "PENDING"])

    def test_manifest_rejects_missing_requirement_unknown_capability_and_cycle(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "spec.md"
            spec.write_text("- **REQ-001 (mandatory):** Create an agent.\n- **REQ-002 (mandatory):** Create a flow.\n")
            state = base_state("APPROVED")
            state["approved_spec_sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
            architecture = {"status": "DECIDED", "accepted": True}
            with self.assertRaises(build_state.BuildStateError):
                build_state.generate_manifest_tasks(state, spec, architecture, [], set())
            invalid = sample_tasks()[1:]
            invalid[0]["owning_capability"] = "unknown.intent"
            with self.assertRaises(build_state.BuildStateError):
                build_state.generate_manifest_tasks(state, spec, architecture, invalid, set())
            cycle = sample_tasks()
            cycle[1]["dependencies"] = ["TASK-002"]
            with self.assertRaises(build_state.BuildStateError):
                build_state.generate_manifest_tasks(
                    state, spec, architecture, cycle,
                    {"copilot_studio.standard.author", "power_automate.flow.build"},
                )
            spec.write_text("- **REQ-001 (mandatory):** Create an agent.\n- **REQ-001 (mandatory):** Duplicate ID.\n")
            state["approved_spec_sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
            with self.assertRaises(build_state.BuildStateError):
                build_state.generate_manifest_tasks(state, spec, architecture, invalid, {"copilot_studio.standard.author"})

    def test_resume_reuses_inspected_verified_task_and_restarts_incomplete_task(self):
        tasks = sample_tasks()[::-1]
        tasks[0].update({
            "status": "VERIFIED", "implementation_evidence": "agent created",
            "verification_evidence": "agent validated",
        })
        tasks[1].update({"status": "IN_PROGRESS", "implementation_evidence": "flow build started"})
        inspections = {
            "TASK-001": {"inspected": True, "artifact_present": True, "outcome": "complete", "inspection_evidence": "agent workspace inspected", "verification_evidence": "prior validation still applies"},
            "TASK-002": {"inspected": True, "artifact_present": True, "outcome": "incomplete", "inspection_evidence": "flow definition absent; no operation completed"},
        }
        state = base_state("BUILDING")
        resumed, next_task = build_state.resume_manifest(state, tasks, inspections)
        self.assertEqual(resumed[0]["status"], "VERIFIED")
        self.assertEqual(resumed[1]["status"], "READY")
        self.assertEqual(next_task, "TASK-002")
        self.assertEqual(state["manifest_progress"]["completed_task_ids"], ["TASK-001"])
        self.assertEqual(state["manifest_progress"]["next_task_id"], "TASK-002")

    def test_resume_blocks_uninspected_or_unknown_outcome_without_replaying(self):
        tasks = sample_tasks()[::-1]
        tasks[0].update({"status": "VERIFIED", "implementation_evidence": "built", "verification_evidence": "tested"})
        tasks[1].update({"status": "IN_PROGRESS", "implementation_evidence": "submission attempted"})
        state = base_state("BUILDING")
        resumed, next_task = build_state.resume_manifest(
            state,
            tasks,
            {"TASK-001": {"inspected": True, "artifact_present": True, "outcome": "complete", "inspection_evidence": "checked", "verification_evidence": "checked"}},
        )
        self.assertEqual(resumed[1]["status"], "BLOCKED")
        self.assertIn("not inspected", resumed[1]["block_reason"].lower())
        self.assertIsNone(next_task)

        unknown_state = base_state("BUILDING")
        unknown, unknown_next = build_state.resume_manifest(
            unknown_state,
            tasks,
            {
                "TASK-001": {"inspected": True, "artifact_present": True, "outcome": "complete", "inspection_evidence": "checked", "verification_evidence": "checked"},
                "TASK-002": {"inspected": True, "artifact_present": True, "outcome": "unknown", "inspection_evidence": "run exists but outcome not resolved"},
            },
        )
        self.assertEqual(unknown[1]["status"], "BLOCKED")
        self.assertIn("outcome is unknown", unknown[1]["block_reason"])
        self.assertIsNone(unknown_next)

    def test_task_blocker_does_not_stop_independent_resume_work(self):
        tasks = sample_tasks()[::-1]
        tasks[0].update({"status": "VERIFIED", "implementation_evidence": "agent built", "verification_evidence": "validated"})
        tasks.append({
            "task_id": "TASK-003", "dependencies": [], "requirement_ids": ["REQ-001"],
            "owning_capability": "copilot_studio.standard.author", "output_artifact": "other agent",
            "status": "PENDING", "implementation_evidence": "", "verification_evidence": "",
        })
        inspections = {
            "TASK-001": {"inspected": True, "artifact_present": True, "outcome": "complete", "inspection_evidence": "agent checked", "verification_evidence": "validated"},
            "TASK-003": {"inspected": True, "artifact_present": False, "outcome": "incomplete", "inspection_evidence": "no prior artifact"},
        }
        state = base_state("BUILDING")
        resumed, next_task = build_state.resume_manifest(state, tasks, inspections)
        by_id = {task["task_id"]: task for task in resumed}
        self.assertEqual(by_id["TASK-002"]["status"], "BLOCKED")
        self.assertEqual(by_id["TASK-003"]["status"], "READY")
        self.assertEqual(next_task, "TASK-003")
        self.assertEqual(state["state"], "BUILDING")
        again, next_task_again = build_state.resume_manifest(state, resumed, inspections)
        self.assertEqual(next_task_again, next_task)
        self.assertEqual([task["status"] for task in again], [task["status"] for task in resumed])
        self.assertEqual(len(state["blockers"]), 1)

        inspections["TASK-002"] = {"inspected": True, "artifact_present": False, "outcome": "incomplete", "inspection_evidence": "confirmed not created"}
        resumed_after_resolution, next_task_after_resolution = build_state.resume_manifest(state, again, inspections)
        self.assertEqual(next_task_after_resolution, "TASK-003")
        self.assertEqual(state["state"], "BUILDING")
        self.assertFalse(any(message.startswith("TASK-002:") for message in state["blockers"]))
        self.assertEqual({task["task_id"]: task["status"] for task in resumed_after_resolution}["TASK-002"], "READY")

    def test_resume_routes_complete_tasks_to_verification_and_all_verified_to_verifying(self):
        task = sample_tasks()[1]
        task.update({"status": "COMPLETE", "implementation_evidence": "agent artifact created"})
        inspections = {"TASK-001": {"inspected": True, "artifact_present": True, "outcome": "complete", "inspection_evidence": "artifact inspected"}}
        state = base_state("BUILDING")
        resumed, next_task = build_state.resume_manifest(state, [task], inspections)
        self.assertEqual(resumed[0]["status"], "COMPLETE")
        self.assertEqual(next_task, "TASK-001")
        self.assertEqual(state["state"], "VERIFYING")

        inspections["TASK-001"]["verification_evidence"] = "acceptance evidence inspected"
        verified_state = base_state("BUILDING")
        verified, no_task = build_state.resume_manifest(verified_state, [task], inspections)
        self.assertEqual(verified[0]["status"], "VERIFIED")
        self.assertIsNone(no_task)
        self.assertEqual(verified_state["state"], "VERIFYING")

    def test_manifest_evidence_transitions_and_state_persistence_reject_secrets(self):
        task = sample_tasks()[1]
        task.update({"status": "IN_PROGRESS"})
        with self.assertRaises(build_state.BuildStateError):
            build_state.record_task_completion(task, "agent artifact", "")
        self.assertEqual(task["status"], "IN_PROGRESS")
        build_state.record_task_completion(task, "agent artifact", "creation evidence")
        self.assertEqual(task["status"], "COMPLETE")
        build_state.record_task_verification(task, "validation evidence")
        self.assertEqual(task["status"], "VERIFIED")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = base_state("APPROVED")
            build_state.save_state(path, state)
            self.assertEqual(json.loads(path.read_text()), state)
            state["client_secret"] = "redacted"
            with self.assertRaises(build_state.BuildStateError):
                build_state.save_state(path, state)
            self.assertNotIn("redacted", path.read_text())

            safe_shape = base_state("APPROVED")
            safe_shape["blockers"] = ["Authentication value omitted from this blocker."]
            with self.assertRaises(build_state.BuildStateError):
                unsafe = dict(safe_shape)
                unsafe["authentication_material"] = "redacted"
                build_state.save_state(path, unsafe)
            self.assertNotIn("redacted", path.read_text())


if __name__ == "__main__":
    unittest.main()

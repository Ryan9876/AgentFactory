#!/usr/bin/env python3
"""Deterministic state, manifest, and resume contracts for Agent Factory projects."""

import copy
import json
import os
import re
import tempfile
from pathlib import Path

from scripts.spec_hash import calculate_spec_hash


STATES = {
    "OBJECTIVE_CAPTURED", "CLARIFICATION_REQUIRED", "ARCHITECTING", "SPEC_DRAFTED",
    "AWAITING_APPROVAL", "APPROVED", "PREFLIGHT", "BUILDING", "VERIFYING",
    "ITERATING", "READY_TO_PACKAGE", "BLOCKED", "COMPLETE", "SPEC_CHANGED",
}
ALLOWED_TRANSITIONS = {
    "OBJECTIVE_CAPTURED": {"CLARIFICATION_REQUIRED", "ARCHITECTING", "BLOCKED"},
    "CLARIFICATION_REQUIRED": {"ARCHITECTING", "BLOCKED"},
    "ARCHITECTING": {"CLARIFICATION_REQUIRED", "SPEC_DRAFTED", "BLOCKED"},
    "SPEC_DRAFTED": {"ARCHITECTING", "AWAITING_APPROVAL", "BLOCKED"},
    "AWAITING_APPROVAL": {"SPEC_DRAFTED", "BLOCKED"},
    "APPROVED": {"PREFLIGHT", "SPEC_CHANGED", "BLOCKED"},
    "PREFLIGHT": {"BUILDING", "SPEC_CHANGED", "BLOCKED"},
    "BUILDING": {"VERIFYING", "SPEC_CHANGED", "BLOCKED"},
    "VERIFYING": {"ITERATING", "READY_TO_PACKAGE", "SPEC_CHANGED", "BLOCKED"},
    "ITERATING": {"BUILDING", "VERIFYING", "READY_TO_PACKAGE", "SPEC_CHANGED", "BLOCKED"},
    "READY_TO_PACKAGE": {"COMPLETE", "SPEC_CHANGED", "BLOCKED"},
    "BLOCKED": {"ARCHITECTING", "AWAITING_APPROVAL", "PREFLIGHT", "BUILDING", "VERIFYING", "SPEC_CHANGED"},
    "SPEC_CHANGED": {"AWAITING_APPROVAL", "BLOCKED"},
    "COMPLETE": set(),
}
STATE_FIELDS = {
    "schema_version", "state", "project_id", "target_environment", "approved_spec_sha256",
    "manifest_path", "manifest_progress", "traceability_path", "blockers", "updated_at",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REQUIREMENT_PATTERN = re.compile(r"^REQ-\d{3}$")
TASK_PATTERN = re.compile(r"^TASK-\d{3}$")
SECRET_PATTERN = re.compile(
    r"(?i)(?:client[_ -]?secret|password|access[_ -]?token|refresh[_ -]?token)\s*[:=]\s*[^\s,]+|"
    r"\bbearer\s+[A-Za-z0-9._~-]{16,}"
)


class BuildStateError(ValueError):
    """Raised when a project state or manifest would violate its contract."""


def transition_state(state, target):
    current = state.get("state")
    if current not in STATES or target not in STATES:
        raise BuildStateError("current or requested state is not an approved V1 state")
    if target == "APPROVED":
        raise BuildStateError("APPROVED requires approve_spec after explicit human approval")
    if target == "SPEC_CHANGED":
        raise BuildStateError("SPEC_CHANGED is set only by the specification integrity gate")
    if target not in ALLOWED_TRANSITIONS[current]:
        raise BuildStateError("invalid workflow transition: {} -> {}".format(current, target))
    state["state"] = target
    return state


def approve_spec(state, spec_path, explicit_approval=False):
    if explicit_approval is not True:
        raise BuildStateError("explicit human approval is required")
    if state.get("state") != "AWAITING_APPROVAL":
        raise BuildStateError("specification can be approved only from AWAITING_APPROVAL")
    try:
        digest = calculate_spec_hash(spec_path)
    except OSError as error:
        raise BuildStateError("cannot read specification for approval") from error
    state["approved_spec_sha256"] = digest
    state["state"] = "APPROVED"
    return digest


def verify_spec_integrity(state, spec_path, phase):
    if phase not in {"build", "resume", "final_verification"}:
        raise BuildStateError("integrity phase must be build, resume, or final_verification")
    approved = state.get("approved_spec_sha256")
    if not isinstance(approved, str) or not SHA256_PATTERN.fullmatch(approved):
        raise BuildStateError("approved_spec_sha256 is missing or malformed")
    try:
        actual = calculate_spec_hash(spec_path)
    except OSError as error:
        state["state"] = "BLOCKED"
        _add_blocker(state, "Cannot read approved specification during {} integrity check.".format(phase))
        return False
    if actual != approved:
        state["state"] = "SPEC_CHANGED"
        message = "Approved specification digest changed before {}.".format(phase)
        _add_blocker(state, message)
        return False
    return True


def _defined_requirements(spec_text):
    requirements = set()
    for line in spec_text.splitlines():
        bullet = re.match(r"^\s*-\s+\*\*(REQ-\d{3}) \((?:mandatory|optional)\):\*\*", line)
        if bullet:
            requirement_id = bullet.group(1)
            if requirement_id in requirements:
                raise BuildStateError("duplicate requirement definition {}".format(requirement_id))
            requirements.add(requirement_id)
            continue
        if line.lstrip().startswith("|"):
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            if len(cells) > 1 and REQUIREMENT_PATTERN.fullmatch(cells[0]) and cells[1].lower() in {"yes", "no", "true", "false", "mandatory", "optional"}:
                if cells[0] in requirements:
                    raise BuildStateError("duplicate requirement definition {}".format(cells[0]))
                requirements.add(cells[0])
    if not requirements:
        raise BuildStateError("approved specification contains no requirement definitions")
    return requirements


def _topological_order(tasks):
    if not isinstance(tasks, list) or any(not isinstance(task, dict) for task in tasks):
        raise BuildStateError("manifest tasks must be a list of objects")
    task_by_id = {}
    for task in tasks:
        task_id = task.get("task_id", "")
        if not isinstance(task_id, str) or not TASK_PATTERN.fullmatch(task_id):
            raise BuildStateError("task IDs must use TASK-NNN")
        if task_id in task_by_id:
            raise BuildStateError("duplicate manifest task {}".format(task_id))
        task_by_id[task_id] = task
    for task_id, task in task_by_id.items():
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list) or any(not isinstance(item, str) for item in dependencies):
            raise BuildStateError("dependencies must be a list for {}".format(task_id))
        if len(dependencies) != len(set(dependencies)):
            raise BuildStateError("duplicate dependency for {}".format(task_id))
        if task_id in dependencies or any(item not in task_by_id for item in dependencies):
            raise BuildStateError("self or unknown dependency for {}".format(task_id))

    ordered = []
    remaining = list(task_by_id)
    completed = set()
    while remaining:
        ready = [task_id for task_id in remaining if set(task_by_id[task_id]["dependencies"]).issubset(completed)]
        if not ready:
            raise BuildStateError("manifest dependencies contain a cycle")
        for task_id in ready:
            ordered.append(task_by_id[task_id])
            completed.add(task_id)
            remaining.remove(task_id)
    return ordered


def generate_manifest_tasks(state, spec_path, architecture, task_definitions, known_capabilities):
    if not isinstance(state, dict):
        raise BuildStateError("state must be an object")
    if state.get("state") != "APPROVED":
        raise BuildStateError("manifest generation requires an APPROVED specification")
    if not verify_spec_integrity(state, spec_path, "build"):
        raise BuildStateError("specification integrity failed; implementation is blocked")
    if not isinstance(architecture, dict) or architecture.get("status") not in {"DECIDED", "DECIDED_WITH_UNRESOLVED_DEPENDENCIES"} or architecture.get("accepted") is not True:
        raise BuildStateError("an accepted architecture decision is required before manifest generation")

    try:
        spec_text = Path(spec_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise BuildStateError("cannot read approved specification requirements") from error
    requirements = _defined_requirements(spec_text)
    _assert_safe(task_definitions)
    if not isinstance(task_definitions, list) or any(not isinstance(task, dict) for task in task_definitions):
        raise BuildStateError("manifest tasks must be a list of objects")
    tasks = copy.deepcopy(task_definitions)
    mapped_requirements = set()
    for task in tasks:
        for required in ("task_id", "owning_capability", "output_artifact"):
            if not isinstance(task.get(required), str) or not task[required].strip():
                raise BuildStateError("{} is required on every manifest task".format(required))
        if task["owning_capability"] not in known_capabilities:
            raise BuildStateError("unknown capability intent {}".format(task["owning_capability"]))
        ids = task.get("requirement_ids")
        if not isinstance(ids, list) or not ids:
            raise BuildStateError("every manifest task must map requirement IDs")
        for requirement_id in ids:
            if not isinstance(requirement_id, str) or not REQUIREMENT_PATTERN.fullmatch(requirement_id):
                raise BuildStateError("invalid requirement ID in manifest task")
            if requirement_id not in requirements:
                raise BuildStateError("unknown requirement {} in manifest".format(requirement_id))
            mapped_requirements.add(requirement_id)
        task.setdefault("status", "PENDING")
        task.setdefault("implementation_evidence", "")
        task.setdefault("verification_evidence", "")
        task.setdefault("inspection_evidence", "")
        task.setdefault("block_reason", "")
    missing = requirements - mapped_requirements
    if missing:
        raise BuildStateError("manifest does not map requirements: {}".format(", ".join(sorted(missing))))
    return _topological_order(tasks)


def record_task_completion(task, output_artifact, implementation_evidence):
    if not isinstance(task, dict):
        raise BuildStateError("manifest task must be an object")
    if task.get("status") != "IN_PROGRESS":
        raise BuildStateError("only an IN_PROGRESS task can be marked COMPLETE")
    if not isinstance(output_artifact, str) or not output_artifact.strip() or not isinstance(implementation_evidence, str) or not implementation_evidence.strip():
        raise BuildStateError("output artifact and implementation evidence are required")
    _assert_safe([output_artifact, implementation_evidence])
    task["output_artifact"] = output_artifact
    task["implementation_evidence"] = implementation_evidence
    task["status"] = "COMPLETE"
    return task


def record_task_verification(task, verification_evidence):
    if not isinstance(task, dict):
        raise BuildStateError("manifest task must be an object")
    if task.get("status") != "COMPLETE":
        raise BuildStateError("only a COMPLETE task can be marked VERIFIED")
    if not isinstance(verification_evidence, str) or not verification_evidence.strip() or not isinstance(task.get("implementation_evidence"), str) or not task["implementation_evidence"].strip():
        raise BuildStateError("implementation and verification evidence are required")
    _assert_safe([task, verification_evidence])
    task["verification_evidence"] = verification_evidence
    task["status"] = "VERIFIED"
    return task


def resume_manifest(state, task_definitions, artifact_inspections):
    if not isinstance(state, dict):
        raise BuildStateError("state must be an object")
    if not isinstance(artifact_inspections, dict):
        raise BuildStateError("artifact inspections must be an object keyed by task ID")
    if any(not isinstance(inspection, dict) for inspection in artifact_inspections.values()):
        raise BuildStateError("each artifact inspection must be an object")
    _assert_safe([state, task_definitions, artifact_inspections])
    tasks = copy.deepcopy(_topological_order(copy.deepcopy(task_definitions)))
    if not tasks:
        raise BuildStateError("cannot resume an empty manifest")
    task_by_id = {task["task_id"]: task for task in tasks}
    unknown_inspections = set(artifact_inspections) - set(task_by_id)
    if unknown_inspections:
        raise BuildStateError("artifact inspection references unknown task {}".format(sorted(unknown_inspections)[0]))
    for task in tasks:
        task.setdefault("implementation_evidence", "")
        task.setdefault("verification_evidence", "")
        task.setdefault("inspection_evidence", "")
        task.setdefault("block_reason", "")
        status = task.get("status", "PENDING")
        if status not in {"PENDING", "READY", "IN_PROGRESS", "BLOCKED", "COMPLETE", "VERIFIED"}:
            raise BuildStateError("invalid manifest status for {}".format(task["task_id"]))
        inspection = artifact_inspections.get(task["task_id"])
        if not inspection or inspection.get("inspected") is not True:
            task["status"] = "BLOCKED"
            task["block_reason"] = "Existing artifact was not inspected; safe resume cannot be confirmed."
            continue
        inspection_evidence = inspection.get("inspection_evidence", "")
        if not isinstance(inspection_evidence, str):
            raise BuildStateError("inspection evidence must be text")
        task["inspection_evidence"] = inspection_evidence
        if not inspection_evidence.strip():
            task["status"] = "BLOCKED"
            task["block_reason"] = "Artifact inspection has no evidence; safe resume cannot be confirmed."
            continue
        outcome = inspection.get("outcome")
        if outcome not in {"complete", "incomplete", "unknown"}:
            raise BuildStateError("inspection outcome must be complete, incomplete, or unknown")
        if outcome == "unknown":
            task["status"] = "BLOCKED"
            task["block_reason"] = "Prior operation outcome is unknown; inspect authoritative state before retry."
        elif outcome == "complete":
            if inspection.get("artifact_present") is not True or not task["inspection_evidence"].strip():
                task["status"] = "BLOCKED"
                task["block_reason"] = "Completed artifact presence and inspection evidence are required."
            elif not isinstance(task.get("implementation_evidence"), str) or not task["implementation_evidence"].strip():
                task["status"] = "BLOCKED"
                task["block_reason"] = "Implementation evidence is missing for an existing completed artifact."
            elif not isinstance(inspection.get("verification_evidence", task.get("verification_evidence", "")), str):
                raise BuildStateError("verification evidence must be text")
            elif inspection.get("verification_evidence", task.get("verification_evidence", "")).strip():
                task["verification_evidence"] = inspection.get("verification_evidence", task.get("verification_evidence", ""))
                task["status"] = "VERIFIED"
            else:
                task["status"] = "COMPLETE"
        else:
            task["verification_evidence"] = ""
            task["status"] = "READY"
            task["block_reason"] = ""

    next_task = None
    for task in tasks:
        if task["status"] not in {"READY", "COMPLETE"}:
            continue
        if all(task_by_id[dependency]["status"] == "VERIFIED" for dependency in task["dependencies"]):
            next_task = task["task_id"]
            break
        task["status"] = "PENDING"

    blocked_messages = [
        "{}: {}".format(task["task_id"], task["block_reason"])
        for task in tasks if task["status"] == "BLOCKED"
    ]
    blockers = state.setdefault("blockers", [])
    blockers[:] = [message for message in blockers if not re.match(r"^TASK-\d{3}: ", message)]
    for message in blocked_messages:
        if message not in blockers:
            blockers.append(message)
    global_blockers = [message for message in blockers if not re.match(r"^TASK-\d{3}: ", message)]
    if global_blockers:
        next_task = None
    progress = state.setdefault("manifest_progress", {"completed_task_ids": [], "next_task_id": None})
    progress["completed_task_ids"] = [task["task_id"] for task in tasks if task["status"] == "VERIFIED"]
    progress["next_task_id"] = next_task
    if global_blockers:
        state["state"] = "BLOCKED"
    elif next_task is not None:
        state["state"] = "VERIFYING" if task_by_id[next_task]["status"] == "COMPLETE" else "BUILDING"
    elif blocked_messages:
        state["state"] = "BLOCKED"
    else:
        state["state"] = "VERIFYING"
    return tasks, next_task


def _assert_safe(value):
    sensitive_key = re.compile(r"(?i)(password|secret|credential|access[_-]?token|refresh[_-]?token|authorization)")
    if isinstance(value, dict):
        for key, child in value.items():
            if sensitive_key.search(str(key)):
                raise BuildStateError("credential-like field is not allowed in persisted project artifacts")
            _assert_safe(child)
    elif isinstance(value, list):
        for child in value:
            _assert_safe(child)
    elif isinstance(value, str) and SECRET_PATTERN.search(value):
        raise BuildStateError("credential-like material is not allowed in persisted project artifacts")


def _add_blocker(state, message):
    blockers = state.setdefault("blockers", [])
    if not isinstance(blockers, list):
        raise BuildStateError("blockers must be a list of text")
    if message not in blockers:
        blockers.append(message)


def _validate_state(state):
    if not isinstance(state, dict):
        raise BuildStateError("state must be an object")
    if set(state) != STATE_FIELDS:
        raise BuildStateError("state contains unknown or missing fields; secrets and credentials are not allowed")
    if state.get("schema_version") != 1 or not isinstance(state.get("state"), str) or state.get("state") not in STATES:
        raise BuildStateError("state schema version or workflow state is invalid")
    if state.get("approved_spec_sha256") is not None and (not isinstance(state["approved_spec_sha256"], str) or not SHA256_PATTERN.fullmatch(state["approved_spec_sha256"])):
        raise BuildStateError("approved_spec_sha256 must be null or a lowercase SHA-256 digest")
    progress = state.get("manifest_progress")
    if not isinstance(progress, dict) or set(progress) != {"completed_task_ids", "next_task_id"}:
        raise BuildStateError("manifest_progress has an invalid shape")
    if not isinstance(progress["completed_task_ids"], list) or (progress["next_task_id"] is not None and not isinstance(progress["next_task_id"], str)):
        raise BuildStateError("manifest_progress values are invalid")
    if not isinstance(state.get("blockers"), list) or any(not isinstance(item, str) for item in state["blockers"]):
        raise BuildStateError("blockers must be a list of text")
    _assert_safe(state)


def save_state(path, state):
    _validate_state(state)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=str(path.parent), delete=False) as stream:
            temporary_path = Path(stream.name)
            json.dump(state, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary_path), str(path))
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_state(path):
    try:
        state = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise BuildStateError("cannot read valid state.json") from error
    if not isinstance(state, dict):
        raise BuildStateError("state.json must contain an object")
    _validate_state(state)
    return state

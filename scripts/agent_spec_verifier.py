#!/usr/bin/env python3
"""Ordered release gate evaluation for an approved Agent Factory project."""

import argparse
import json
import re
import sys
from pathlib import Path

from scripts.build_state import BuildStateError, load_state, save_state, transition_state, verify_spec_integrity
from scripts.traceability_check import validate_traceability


GATE_NAMES = (
    "spec_integrity",
    "requirement_coverage",
    "platform_validation",
    "functional_verification",
    "evaluation",
    "resilience_review",
)
ALLOWED_VERDICTS = {"SHIP", "ITERATE", "BLOCK"}
EVIDENCE_STATUSES = {"pass", "fail", "blocked"}


def _gate(name, status, findings=None, evidence=None):
    return {
        "name": name,
        "status": status,
        "findings": list(findings or []),
        "evidence": evidence or "",
    }


def _not_run_gates(start_index):
    return [_gate(name, "NOT_RUN") for name in GATE_NAMES[start_index:]]


def _evidence_gate(name, evidence):
    record = evidence.get(name)
    if not isinstance(record, dict):
        return _gate(name, "BLOCKED", ["Required evidence record is missing or malformed."]), "BLOCK"
    status = record.get("status")
    proof = record.get("evidence")
    if status not in EVIDENCE_STATUSES:
        return _gate(name, "BLOCKED", ["Evidence status must be pass, fail, or blocked."], proof), "BLOCK"
    if not isinstance(proof, str) or not proof.strip():
        return _gate(name, "BLOCKED", ["Inspectable evidence reference is missing."], ""), "BLOCK"
    if status == "blocked":
        return _gate(name, "BLOCKED", [record.get("reason", "Required capability or prerequisite is blocked.")], proof), "BLOCK"
    if status == "fail":
        return _gate(name, "FAIL", [record.get("finding", "The gate did not pass.")], proof), "ITERATE"
    return _gate(name, "PASS", evidence=proof), None


def _evaluation_gate(evidence):
    record = evidence.get("evaluation")
    if not isinstance(record, dict):
        return _gate("evaluation", "BLOCKED", ["Required evaluation evidence is missing or malformed."]), "BLOCK"
    thresholds_approved = record.get("thresholds_approved") is True
    threshold_source = record.get("thresholds_source")
    if not thresholds_approved or not isinstance(threshold_source, str) or not threshold_source.strip():
        return _gate("evaluation", "BLOCKED", ["Evaluation thresholds are not explicitly approved and sourced."], record.get("evidence")), "BLOCK"
    return _evidence_gate("evaluation", evidence)


def _resilience_gate(evidence):
    gate, verdict = _evidence_gate("resilience_review", evidence)
    record = evidence.get("resilience_review")
    if isinstance(record, dict) and record.get("unsafe") is True:
        finding = record.get("finding", "Resilience review reports unsafe behavior.")
        gate["status"] = "FAIL"
        gate["findings"] = [finding]
        return gate, "BLOCK"
    return gate, verdict


def _spec_blockers(spec_path):
    try:
        lines = Path(spec_path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return ["Approved specification cannot be read to inspect blocker accounting."]
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^##\s+Unresolved blockers\s*$", line.strip(), re.IGNORECASE):
            start = index + 1
            break
    if start is None:
        return []
    body = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        line = re.sub(r"<!--.*?-->", "", line).strip()
        if line and not re.fullmatch(r"[-| :]+", line):
            body.append(line)
    content = " ".join(body).strip()
    if not content:
        return ["Unresolved blocker section is empty; explicitly record None identified or list blockers."]
    if re.fullmatch(r"(?i)(?:[-*]\s*)?none identified\.?", content):
        return []
    return ["Specification lists unresolved blockers: {}".format(content)]


def _finish(state, state_path, gates, verdict, findings):
    if verdict not in ALLOWED_VERDICTS:
        raise BuildStateError("verifier produced an unsupported release verdict")
    if verdict == "SHIP":
        target_state = "READY_TO_PACKAGE"
    elif verdict == "ITERATE":
        target_state = "ITERATING"
    else:
        target_state = "BLOCKED"
    if state.get("state") != target_state:
        transition_state(state, target_state)
    save_state(state_path, state)
    return {"gates": gates, "verdict": verdict, "findings": findings, "state": state["state"]}


def verify_release(project_root, evidence):
    """Run release checks in specification order using supplied platform evidence."""
    root = Path(project_root)
    control = root / ".agent-factory"
    state_path = control / "state.json"
    spec_path = control / "spec.md"
    traceability_path = control / "traceability.csv"
    gates = []
    findings = []
    try:
        state = load_state(state_path)
    except BuildStateError as error:
        gate = _gate("spec_integrity", "BLOCKED", [str(error)])
        gates.append(gate)
        gates.extend(_not_run_gates(1))
        return {"gates": gates, "verdict": "BLOCK", "findings": gate["findings"], "state": "BLOCKED"}

    if state["state"] not in {"VERIFYING", "ITERATING"}:
        gate = _gate("spec_integrity", "BLOCKED", ["Final verification requires VERIFYING or ITERATING state."])
        gates.append(gate)
        gates.extend(_not_run_gates(1))
        state["state"] = "BLOCKED"
        save_state(state_path, state)
        return {"gates": gates, "verdict": "BLOCK", "findings": gate["findings"], "state": state["state"]}

    if not verify_spec_integrity(state, spec_path, "final_verification"):
        gate = _gate("spec_integrity", "FAIL", ["Specification digest mismatch or approved specification is unavailable."])
        gates.append(gate)
        gates.extend(_not_run_gates(1))
        save_state(state_path, state)
        return {"gates": gates, "verdict": "BLOCK", "findings": gate["findings"], "state": state["state"]}
    gates.append(_gate("spec_integrity", "PASS", evidence="approved SHA-256 matches current spec.md"))

    coverage_errors = validate_traceability(spec_path, traceability_path, release=True)
    if coverage_errors:
        gates.append(_gate("requirement_coverage", "FAIL", coverage_errors))
        gates.extend(_not_run_gates(2))
        findings.extend(coverage_errors)
        malformed_spec = any(
            phrase in error.lower()
            for error in coverage_errors
            for phrase in ("malformed requirement definition", "duplicate requirement definition", "no req-nnn requirement definitions")
        )
        return _finish(state, state_path, gates, "BLOCK" if malformed_spec else "ITERATE", findings)
    gates.append(_gate("requirement_coverage", "PASS", evidence="all mandatory requirements have implementation and verification evidence"))

    for name in ("platform_validation", "functional_verification"):
        gate, verdict = _evidence_gate(name, evidence if isinstance(evidence, dict) else {})
        gates.append(gate)
        if verdict:
            gates.extend(_not_run_gates(len(gates)))
            findings.extend(gate["findings"])
            return _finish(state, state_path, gates, verdict, findings)

    gate, verdict = _evaluation_gate(evidence if isinstance(evidence, dict) else {})
    gates.append(gate)
    if verdict:
        gates.extend(_not_run_gates(len(gates)))
        findings.extend(gate["findings"])
        return _finish(state, state_path, gates, verdict, findings)

    gate, verdict = _resilience_gate(evidence if isinstance(evidence, dict) else {})
    gates.append(gate)
    if verdict:
        gates.extend(_not_run_gates(len(gates)))
        findings.extend(gate["findings"])
        return _finish(state, state_path, gates, verdict, findings)

    blockers = list(state.get("blockers", [])) + _spec_blockers(spec_path)
    if blockers:
        findings.extend("Unresolved blocker: {}".format(blocker) for blocker in blockers)
        return _finish(state, state_path, gates, "BLOCK", findings)
    return _finish(state, state_path, gates, "SHIP", findings)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path, help="project containing .agent-factory/")
    parser.add_argument("--evidence-file", required=True, type=Path, help="JSON evidence from Microsoft platform/evaluation checks")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    input_error = None
    try:
        evidence = json.loads(args.evidence_file.read_text(encoding="utf-8"))
        if not isinstance(evidence, dict):
            raise ValueError("evidence JSON must be an object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        evidence = {}
        input_error = "Evidence file could not be read as a JSON object."

    result = verify_release(args.project_root, evidence)
    if input_error:
        result["findings"].append(input_error)
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"SHIP": 0, "ITERATE": 1, "BLOCK": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())

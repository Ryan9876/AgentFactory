#!/usr/bin/env python3
"""Route verifier findings to their smallest manifest owner and retests."""

import csv
import re
from pathlib import Path


RELEASE_GATES = (
    "spec_integrity",
    "requirement_coverage",
    "platform_validation",
    "functional_verification",
    "evaluation",
    "resilience_review",
    "verdict",
)
REQUIREMENT_ID = re.compile(r"^REQ-[0-9]{3}$")
REQUIREMENT_LINE = re.compile(
    r"^\s*-\s+\*\*(REQ-[0-9]{3}) \((?:mandatory|optional)\):\*\*\s*(.*?)\s*$"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _blocked(reason):
    return {
        "status": "UNROUTABLE",
        "verdict": "BLOCK",
        "reason": reason,
        "owner": None,
        "focused_context": [],
        "component_retests": [],
        "release_reruns": [],
        "next_action": "resolve_finding_ownership_or_requirement_mapping",
    }


def _read_requirements(spec_path):
    requirements = {}
    try:
        lines = Path(spec_path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        raise ValueError("approved specification is unavailable for focused requirement context")
    for line in lines:
        match = REQUIREMENT_LINE.match(line)
        if match:
            requirement_id, summary = match.groups()
            if requirement_id in requirements:
                raise ValueError("approved specification contains duplicate requirement IDs")
            requirements[requirement_id] = summary
    if not requirements:
        raise ValueError("approved specification contains no parseable REQ-NNN requirements")
    return requirements


def _known_capabilities(registry_path):
    try:
        with Path(registry_path).open(encoding="utf-8", newline="") as stream:
            return {row["capability_id"] for row in csv.DictReader(stream) if row.get("capability_id")}
    except (OSError, UnicodeError, csv.Error, KeyError):
        return set()


def route_finding(finding, manifest_tasks, spec_path, registry_path=None):
    """Return a focused remediation route without modifying approved artifacts.

    Unrouteable findings return BLOCK. A proposed requirement change is returned
    as a BLOCK pending explicit reapproval; the integrity verifier will set
    SPEC_CHANGED after an approved edit changes the digest.
    """
    if not isinstance(finding, dict):
        return _blocked("verification finding must be an object")
    summary = finding.get("summary")
    requirement_ids = finding.get("requirement_ids")
    if not isinstance(summary, str) or not summary.strip():
        return _blocked("finding summary is required")
    if not isinstance(requirement_ids, list) or not requirement_ids:
        return _blocked("finding must identify one or more requirement IDs")
    if any(not isinstance(item, str) or not REQUIREMENT_ID.fullmatch(item) for item in requirement_ids):
        return _blocked("finding contains an invalid requirement ID")
    if len(set(requirement_ids)) != len(requirement_ids):
        return _blocked("finding contains duplicate requirement IDs")
    if not isinstance(manifest_tasks, list) or not manifest_tasks:
        return _blocked("build manifest tasks are unavailable")

    try:
        requirements = _read_requirements(spec_path)
    except ValueError as error:
        return _blocked(str(error))
    unknown = sorted(set(requirement_ids) - set(requirements))
    if unknown:
        return _blocked("finding references requirements absent from the approved specification: {}".format(", ".join(unknown)))

    capabilities = _known_capabilities(
        registry_path or REPOSITORY_ROOT / ".agents/skills/agentfactory/references/capability-routes.csv"
    )
    matches = []
    requested_component = finding.get("component")
    for task in manifest_tasks:
        if not isinstance(task, dict):
            return _blocked("build manifest contains a malformed task")
        task_id = task.get("task_id")
        capability_id = task.get("owning_capability")
        component = task.get("output_artifact")
        task_requirements = task.get("requirement_ids")
        if (
            not isinstance(task_id, str) or not task_id.strip()
            or not isinstance(capability_id, str) or capability_id not in capabilities
            or not isinstance(component, str) or not component.strip()
            or not isinstance(task_requirements, list)
            or any(not isinstance(item, str) or not REQUIREMENT_ID.fullmatch(item) for item in task_requirements)
        ):
            return _blocked("build manifest contains an invalid owner, capability, component, or requirement mapping")
        if not set(requirement_ids).issubset(set(task_requirements)):
            continue
        if requested_component and requested_component not in {task_id, component}:
            continue
        matches.append(task)

    if len(matches) != 1:
        reason = "finding has no manifest owner covering all referenced requirements" if not matches else "finding maps to multiple components; specify the smallest owning component"
        return _blocked(reason)

    owner_task = matches[0]
    owner = {
        "task_id": owner_task["task_id"],
        "component": owner_task["output_artifact"],
        "capability_id": owner_task["owning_capability"],
    }
    focused_context = [
        {"requirement_id": requirement_id, "summary": requirements[requirement_id]}
        for requirement_id in requirement_ids
    ]
    if finding.get("requires_spec_change") is True:
        return {
            "status": "SPEC_CHANGE_PROPOSED",
            "verdict": "BLOCK",
            "reason": "A requirement change needs an explicit proposal and reapproval; the approved requirement remains in force.",
            "owner": owner,
            "focused_context": focused_context,
            "component_retests": [],
            "release_reruns": [],
            "next_action": "prepare_spec_change_for_explicit_reapproval",
            "change_control": {
                "integrity_state_after_spec_edit": "SPEC_CHANGED",
                "resume_state_after_reapproval": "AWAITING_APPROVAL",
                "must_not_weaken_approved_requirement": True,
            },
        }

    return {
        "status": "ROUTED",
        "verdict": "ITERATE",
        "reason": summary.strip(),
        "owner": owner,
        "focused_context": focused_context,
        "component_retests": [owner_task["task_id"]],
        "release_reruns": list(RELEASE_GATES),
        "next_action": "fix_smallest_owner_retest_component_then_rerun_release_gates",
    }

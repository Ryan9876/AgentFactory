"""Load and validate AgentFactory's machine-readable architecture constraints."""
from pathlib import Path
import yaml

REQUIRED = {
    "organization": ("purpose", "development_environment_only_by_default"),
    "licensing": ("github_copilot_harness", "usage_based_copilot_credits_for_agent_builds"),
    "work_iq": ("m365_copilot", "host_composition_with_agents", "copilot_studio_embedded", "direct_mcp_api"),
    "agent_architectures": ("declarative_agent", "copilot_studio_standard", "github_copilot_harness", "custom_engine"),
    "deployment": ("production_requires_explicit_approval", "organization_publish_requires_explicit_approval"),
    "architecture": ("prefer_native_before_custom", "verify_current_microsoft_docs_before_mutable_platform_decisions"),
}

def load_yaml(path: Path) -> dict[str, object]:
    with Path(path).open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the document root")
    return data

def validate_constraints(data: dict[str, object]) -> list[str]:
    errors = []
    for section, fields in REQUIRED.items():
        value = data.get(section)
        if not isinstance(value, dict):
            errors.append(f"missing or malformed top-level section: {section}")
            continue
        for field in fields:
            if field not in value:
                errors.append(f"{section}.{field} is required")
    qualification = data.get("qualification")
    if not isinstance(qualification, dict):
        errors.append("qualification must be a mapping")
    else:
        if qualification.get("entitlement_policy") != "existing_entitlements_only":
            errors.append("qualification.entitlement_policy must be existing_entitlements_only")
        if qualification.get("fixed_for_program_unless_explicitly_changed") is not True:
            errors.append("qualification must keep environment constraints fixed until explicitly changed")
        remediation = qualification.get("unavailable_entitlement_remediation", {})
        if not isinstance(remediation, dict) or remediation.get("allowed") is not False:
            errors.append("qualification must prohibit remediation by acquiring more entitlements")
    return errors


def evaluate_architecture_candidates(
    candidates: list[dict],
    capability_availability: dict,
    *,
    confirmed_changed_capabilities: set[str] | None = None,
) -> dict:
    """Choose the first viable candidate using explicit current-environment evidence.

    Candidates are supplied in least-complex-first order. Known unavailable
    capabilities eliminate only candidates that require them. An unknown or
    unverified requirement fails closed instead of being treated as available.
    A previously fixed constraint cannot become available unless the caller
    identifies that exact capability as explicitly changed by Ryan.
    This evaluates current evidence; it never proposes acquiring new authority.
    """
    evaluations = []
    has_confirmation_blocker = False
    for candidate in candidates:
        name = candidate.get("name", "unnamed")
        unavailable = []
        remediable = []
        unverified = []
        confirmation_required = []
        for capability in candidate.get("requires", []):
            evidence = capability_availability.get(capability, {})
            availability = evidence.get("environment_availability", "unverified")
            classification = evidence.get("classification", "UNVERIFIED")
            if (
                availability == "available"
                and classification == "FIXED_ENVIRONMENT_CONSTRAINT"
                and capability not in (confirmed_changed_capabilities or set())
            ):
                confirmation_required.append(capability)
                continue
            if availability == "unavailable":
                blocker = {
                    "capability": capability,
                    "classification": classification,
                    "blocker": evidence.get("blocker", "current environment does not provide this capability"),
                }
                if blocker["classification"] == "FIXED_ENVIRONMENT_CONSTRAINT":
                    unavailable.append(blocker)
                elif blocker["classification"] == "REMEDIABLE_TOOLING_FAILURE":
                    remediable.append(blocker)
                else:
                    unverified.append(capability)
            elif availability != "available":
                unverified.append(capability)

        if unavailable:
            evaluations.append({"name": name, "status": "REJECTED_CURRENT_ENVIRONMENT", "blockers": unavailable})
            continue
        if remediable:
            evaluations.append({"name": name, "status": "REMEDIATION_REQUIRED", "blockers": remediable})
            return {"status": "REMEDIATION_REQUIRED", "architecture": None, "evaluations": evaluations}
        if confirmation_required:
            evaluations.append({
                "name": name,
                "status": "PREMISE_CHANGE_CONFIRMATION_REQUIRED",
                "capabilities": confirmation_required,
            })
            has_confirmation_blocker = True
            continue
        if unverified:
            evaluations.append({"name": name, "status": "NOT_YET_QUALIFIED", "unverified": unverified})
            return {"status": "BLOCKED_UNVERIFIED_REQUIREMENT", "architecture": None, "evaluations": evaluations}
        evaluations.append({"name": name, "status": "SELECTED"})
        return {"status": "SELECTED", "architecture": name, "evaluations": evaluations}

    return {
        "status": (
            "PREMISE_CHANGE_CONFIRMATION_REQUIRED"
            if has_confirmation_blocker
            else "CAPABILITY_UNAVAILABLE_CURRENT_ENVIRONMENT"
        ),
        "architecture": None,
        "evaluations": evaluations,
    }

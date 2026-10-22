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
    return errors

"""Small capability router backed by the canonical capability registry."""

from collections.abc import Iterable, Mapping

EVIDENCE_STATES = {
    "DESIGNED", "IMPLEMENTED", "CLOUD_SYNCHRONIZED", "RUNTIME_QUALIFIED",
    "BLOCKED", "FAILED", "NOT_TESTED", "USER_PRESENCE_REQUIRED", "ADMIN_REQUIRED",
}


def _route_for_capability(registry: Mapping, capability_id: str) -> Mapping | None:
    routes = registry.get("execution_routing", {}).get("routes", {})
    for route in routes.values():
        if capability_id in route.get("capabilities", []):
            return route
    return None


def choose_execution_route(
    registry: Mapping,
    capability_id: str,
    available_hosts: Iterable[str],
    *,
    blocker: str | None = None,
    human_presence_required: bool = False,
    admin_required: bool = False,
    evidence: str = "NOT_TESTED",
) -> dict[str, str | None]:
    """Choose a supported host, stopping before policy or human boundaries."""
    hosts = set(available_hosts)
    route = _route_for_capability(registry, capability_id)
    if route is None:
        return {"status": "BLOCKED", "host": None, "reason": "unknown capability"}
    if admin_required:
        return {"status": "ADMIN_REQUIRED", "host": None, "reason": "administrator boundary"}
    if human_presence_required:
        return {"status": "USER_PRESENCE_REQUIRED", "host": None, "reason": "human presence boundary"}

    routing = registry["execution_routing"]
    no_hop = set(routing["host_fallback"]["never_when_blocker"])
    preferred_host_failed = blocker == "TOOL_HOST"
    if blocker:
        status = blocker if blocker in EVIDENCE_STATES | {"BLOCKED_BY_TENANT_OR_POLICY"} else "BLOCKED"
        if blocker in no_hop or not preferred_host_failed:
            return {"status": status, "host": None, "blocker": blocker, "reason": f"existing {blocker} blocker; host fallback prohibited"}

    preference = route.get("host_preference_order")
    if preference is None:
        preference = [route.get("preferred_host"), route.get("fallback_host")]
    if preferred_host_failed:
        preference = [host for host in preference if host != route.get("preferred_host")]
    for host in preference:
        if host and (host == "either" or host in hosts):
            selected = next((candidate for candidate in route.get("host_preference_order", hosts) if candidate in hosts), None) if host == "either" else host
            return {
                "status": "ROUTED",
                "host": selected,
                "reason": "preferred supported host" if selected == route.get("preferred_host") else "next supported host",
                "evidence_state": evidence if evidence in EVIDENCE_STATES else "NOT_TESTED",
            }
    return {"status": "BLOCKED", "host": None, "reason": "no supported execution host is available"}

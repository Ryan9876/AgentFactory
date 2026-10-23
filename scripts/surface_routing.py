"""Fail-closed routing for agent implementation surfaces."""

from collections.abc import Mapping


def choose_implementation_surface(
    registry: Mapping,
    assessments: Mapping[str, Mapping],
    *,
    proposed_surface: str | None = None,
) -> dict[str, str | None]:
    """Choose deterministic surfaces first and require evidence for browser fallback.

    Assessments are operation-specific. Status must be supported, unavailable, or
    insufficient and include concrete evidence. One failed route does not establish
    that every other structured route is unavailable.
    """
    routing = registry.get("execution_routing", {})
    preference = routing.get("surface_preference", [])
    aliases = {
        "playwright": "browser_automation",
        "browser_ui": "supported_browser_ui",
        "browser_clicking": "browser_automation",
        "ui_field_entry": "browser_automation",
    }
    proposed = aliases.get(proposed_surface, proposed_surface) if proposed_surface else None
    if proposed and proposed not in set(preference):
        return {"status": "STOP_REASSESS", "surface": None, "reason": "proposed surface is not registered"}

    def status(surface):
        value = assessments.get(surface)
        if not isinstance(value, Mapping) or not value.get("evidence"):
            return "not_tested"
        result = value.get("status")
        return result if result in {"supported", "unavailable", "insufficient"} else "not_tested"

    if proposed in {"supported_browser_ui", "browser_automation"}:
        earlier = [s for s in preference[:preference.index("supported_browser_ui")] if s != "human_action"]
        working = [s for s in earlier if status(s) == "supported"]
        if working:
            return {"status": "STOP_REASSESS", "surface": None, "preferred_surface": working[0],
                    "reason": "supported structured surface outranks browser configuration"}
        unknown = [s for s in earlier if status(s) == "not_tested"]
        if unknown:
            return {"status": "STOP_REASSESS", "surface": None,
                    "reason": "structured surface availability is unverified: " + ", ".join(unknown)}
        if proposed == "browser_automation" and status("supported_browser_ui") == "supported":
            return {"status": "STOP_REASSESS", "surface": None, "preferred_surface": "supported_browser_ui",
                    "reason": "supported browser UI outranks browser automation"}
        if proposed == "browser_automation" and status("supported_browser_ui") == "not_tested":
            return {"status": "STOP_REASSESS", "surface": None,
                    "reason": "supported browser UI availability is unverified"}
        if status(proposed) != "supported":
            return {"status": "BLOCKED", "surface": None,
                    "reason": "browser fallback lacks operation-specific support evidence"}
        rejected = "; ".join(
            f"{s}: {assessments[s]['evidence']}"
            for s in earlier + ["supported_browser_ui"] if s in assessments
        )
        return {
            "status": "ROUTED",
            "surface": proposed,
            "reason": "structured routes unavailable or insufficient; " + rejected
            + f"; browser_automation: {assessments[proposed]['evidence']}",
        }

    if proposed:
        earlier = [s for s in preference[:preference.index(proposed)] if s not in {
            "supported_browser_ui", "browser_automation", "human_action"
        }]
        working = [s for s in earlier if status(s) == "supported"]
        if working:
            return {"status": "STOP_REASSESS", "surface": None, "preferred_surface": working[0],
                    "reason": "higher-priority structured surface is supported"}
        unknown = [s for s in earlier if status(s) == "not_tested"]
        if unknown:
            return {"status": "STOP_REASSESS", "surface": None,
                    "reason": "higher-priority structured surface is unverified: " + ", ".join(unknown)}
        if status(proposed) == "supported":
            return {"status": "ROUTED", "surface": proposed,
                    "reason": "higher-priority structured routes evidenced unavailable or insufficient"}
        return {"status": "BLOCKED", "surface": None,
                "reason": "proposed structured surface is not evidenced as supported"}

    for surface in preference:
        if surface in {"supported_browser_ui", "browser_automation", "human_action"}:
            continue
        if status(surface) == "supported":
            return {"status": "ROUTED", "surface": surface,
                    "reason": "highest-priority supported structured surface"}
    return {"status": "STOP_REASSESS", "surface": None,
            "reason": "no supported structured surface established"}

# Remediation routing

For each verification finding, use `scripts.remediation.route_finding(finding, manifest_tasks, spec_path)` to identify its owner. The helper returns a structured route but never executes a platform change.

The finding must name its `REQ-NNN` IDs and concise summary. The manifest must contain a unique task whose requirement mapping covers all cited IDs, whose component is inspectable, and whose owning capability exists in `capability-routes.csv`. If multiple tasks qualify, include the smallest owning component's task ID or output artifact as `component`. Missing, malformed, or ambiguous ownership returns `BLOCK` and no route.

A routed fix receives only the cited requirement summaries, owner task/component/capability, a component retest, and the complete release rerun order. Send that focused context to the responsible Microsoft capability. Inspect the resulting artifact, record evidence in the manifest and traceability row, rerun the affected component test, then rerun every required release gate before final acceptance. A finding remains `ITERATE` until retests clear it.

If the approved requirement itself needs a change, return `SPEC_CHANGE_PROPOSED` with `BLOCK`. Prepare a reviewable proposed specification change for explicit approval; do not edit or weaken the approved requirement to make a test pass. Once an approved edit changes the project spec, the next integrity check records `SPEC_CHANGED`. Continue only after the revised spec receives explicit approval and a new digest is recorded.

This helper does not run the Microsoft capability, apply a fix, edit the spec, change project state, or manufacture implementation/verification evidence. Keep unresolved or unrouteable findings blocked.

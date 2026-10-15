# HR policy agent — specification draft

Status: `AWAITING_APPROVAL`

## Objective

Build an HR policy agent using SharePoint policy documents.

## Success criteria and approved quality thresholds

The agent answers employee questions from the approved HR policy source. Threshold: Not supplied; approval required before evaluation thresholds are set.

## Architecture

Standard Copilot Studio with SharePoint knowledge. No flow, Dataverse, action, or child agent is proposed on current facts. Exact source and access remain a preflight dependency.

## Functional requirements

| ID (`REQ-NNN`) | Mandatory | Requirement | Acceptance evidence |
| --- | --- | --- | --- |
| REQ-001 | yes | Answer HR policy questions using the approved SharePoint policy documents. | Evaluation cases demonstrate grounded answers and cite or identify source content where supported. |
| REQ-002 | yes | Do not invent policy when the source lacks an answer; explain the gap and route to the designated HR escalation path once supplied. | Missing-answer case demonstrates a safe response; escalation destination is a known dependency. |

## Known assumptions

| Assumption | Basis/source | Accepted by user? |
| --- | --- | --- |
| Employees are the intended initial audience. | Transparent conventional assumption from HR policy objective. | Pending |

## Known dependencies

| Dependency | Evidence status | Owner / resolution stage |
| --- | --- | --- |
| Identify authoritative SharePoint location and access. | not_yet_verified | Project owner / Development preflight |

## Unresolved blockers

None identified for drafting architecture-specific requirements. The source and access dependency must be resolved before implementation.

## Approval record

- Approver: pending explicit human decision
- Approved at: pending
- Approved spec SHA-256: pending until approval
- Approval status: `AWAITING_APPROVAL`

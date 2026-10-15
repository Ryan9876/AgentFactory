# Verdict rules

Exactly one final verdict is returned:

- `SHIP`: specification integrity matches the approved digest; every mandatory requirement has implementation and verification evidence; platform validation, functional verification, evaluation, and resilience review pass; approved evaluation thresholds are sourced; no unresolved blocker remains.
- `ITERATE`: a verification gate found a remediable implementation or evaluation gap and work can safely continue. Stop at the first failed gate and retest the affected component before rerunning the release sequence.
- `BLOCK`: specification drift, an unavailable required dependency or permission, an unresolved consequential decision, unsafe behavior, missing approved evaluation thresholds, or another condition prevents valid progress or acceptance.

Only these three verdict strings are allowed. Never weaken an approved requirement to obtain `SHIP`; propose a specification change, enter `SPEC_CHANGED`, and obtain explicit reapproval instead. Production deployment and organization-wide publication remain explicit approval boundaries.

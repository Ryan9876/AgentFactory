# Verdict rules — planned, not implemented

- `SHIP`: all release gates pass; every mandatory requirement has implementation and verification evidence; no unresolved blocker.
- `ITERATE`: a remediable implementation/evaluation gap exists and work can safely continue.
- `BLOCK`: spec drift, unavailable required dependency/permission, unresolved consequential decision, unsafe behavior, or another condition prevents valid progress/acceptance.

Only these three verdict strings are allowed. Never weaken an approved requirement to obtain `SHIP`; propose a spec change and obtain reapproval instead. Production deployment and organization-wide publication remain explicit approval boundaries.

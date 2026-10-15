# Traceability rules — planned, not implemented

Requirement identifiers are stable `REQ-NNN`. CSV header and order:

```text
requirement_id,requirement_summary,mandatory,implementation_artifact,implementation_evidence,verification_id,verification_evidence,status
```

Every mandatory requirement must map to implementation and verification evidence before release. Unknown IDs, missing mandatory rows, missing implementation evidence, or missing release verification evidence fail coverage. Evidence must point to inspectable artifacts or recorded results; a status label alone is not evidence.

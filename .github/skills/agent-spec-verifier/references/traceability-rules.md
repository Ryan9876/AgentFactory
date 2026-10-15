# Requirement traceability rules

Requirement IDs are stable `REQ-NNN` identifiers. Preserve each mandatory requirement from the approved specification through the build manifest, implementation evidence, verification, and acceptance report.

The CSV header and column order are exact:

```text
requirement_id,requirement_summary,mandatory,implementation_artifact,implementation_evidence,verification_id,verification_evidence,status
```

In release mode, fail coverage when:

- a mandatory requirement has no row;
- an unknown or malformed requirement ID appears;
- an ID maps more than once or its mandatory flag differs from the approved spec;
- implementation artifact/evidence is absent;
- verification ID/evidence is absent.

Evidence must point to an inspectable artifact or recorded result. A status label, successful demo, or general project statement does not prove the requirement. Optional requirements may lack implementation/verification evidence unless the approved project specification makes them release gates.

Do not edit the approved specification to make a coverage check pass. Correct the implementation/mapping, or route a necessary requirement change through spec drift and explicit reapproval.

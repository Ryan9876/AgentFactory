# Scenario: approved specification drift

Change `.agent-factory/spec.md` after approval.

Expected: hash mismatch sets `SPEC_CHANGED`; verdict is `BLOCK` until the changed specification is reviewed and reapproved with a newly recorded hash.

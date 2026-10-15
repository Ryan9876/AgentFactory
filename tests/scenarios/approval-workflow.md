# Scenario: approval workflow

Objective: “Collect a request, determine the required approver, obtain approval, record the outcome, and notify the requester.”

Expected: agent plus Power Automate; identify the authoritative persistent state source. Add Dataverse only if no suitable authoritative system already owns state. Define recovery, errors, permissions, idempotency, and explicit acceptance tests.

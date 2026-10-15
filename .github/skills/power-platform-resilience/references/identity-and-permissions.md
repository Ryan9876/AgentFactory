# Identity and permissions — planned, not implemented

Record authentication mechanism and identity for every action, distinguishing user-context from service-context execution. Apply least privilege. Specify required roles, connector connections/references, consent/admin prerequisites, data access boundaries, expiry/rotation expectations for secrets, and behavior when authorization is absent or revoked. Never store credentials in Factory state or source control. Unverified roles or tenant settings remain dependencies, not assumptions presented as facts.

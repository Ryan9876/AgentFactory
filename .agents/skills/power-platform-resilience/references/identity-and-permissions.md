# Identity and permissions review

For every knowledge source, tool/action, flow, connector, state store, and external system, record the identity that performs the operation and the identity whose authority governs the data access.

## Context and authentication

- Distinguish user-context execution from service-context execution. Do not assume the two have equivalent access or audit semantics.
- Identify the authentication mechanism and connection owner only from verified platform/environment evidence.
- Explain whether the user is prompted to sign in, whether a connection is delegated, or whether a service identity acts. Record unresolved behavior as a dependency.
- Preserve the initiating user and request correlation when a service-context action is required and the platform supports it.

## Least privilege and boundaries

- Identify only permissions required for the approved action and data scope. This program does not request additional permissions; treat missing authority as a fixed environment constraint unless Ryan explicitly says the premise changed.
- Record required roles, scopes, consent, administrator prerequisites, and data access boundaries from authoritative sources.
- Do not use privileged credentials to work around a missing user permission. Do not infer that a maker's access grants end-user access.
- Respect record ownership and row/environment boundaries where the selected platform exposes them.

## Connections and secrets

- Identify connection references, connection owners, environment variables, and consent requirements as configuration dependencies, without inventing names or values.
- Do not store passwords, tokens, client secrets, or other authentication material in Factory artifacts, prompts, code, logs, or source control.
- Use only an approved secure connection or secret-management mechanism. Define rotation/expiry handling where applicable without recording secret values.

## Missing or changed authorization

- If permission is absent, expired, revoked, or insufficient, stop the affected operation and avoid retry loops that cannot restore authorization.
- Explain the safe consequence, record the missing permission, and evaluate an alternative within current entitlements. Do not route an access request to an administrator or owner.
- Do not silently switch from user-context to service-context or escalate privileges.
- Record unknown roles, policies, consent, and access configuration as explicit blockers/dependencies until verified.

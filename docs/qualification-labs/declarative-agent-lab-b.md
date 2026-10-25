# Lab B — Declarative Microsoft 365 agent lifecycle

**Date:** 2026-10-23
**Host:** Desktop Local
**Disposition:** `PREFLIGHT_BLOCKED`
**Target gate:** `UNQUALIFIED`
**Create allowed:** `NO`

## Active specification

The sole active Lab B specification is [lab-b-corporate-tenant-spec.md](lab-b-corporate-tenant-spec.md). Its approved SHA-256 is `0d27ae6d9927b8d12cb3edf29ccdd8882c742812c5d0e9ad8da678f46511dd88`, with approval dated 2026-10-23. The approval is bound to the immutable bytes recorded in [the qualification index](../../config/qualification-labs.yaml). Specification approval does not authorize implementation or deployment. The previous frozen digest is superseded after sanitization, and the earlier disposable-target specification remains superseded and inactive in that same index.

## Read-only preflight result

The approved target is the existing live OpenText Production tenant. Its custom-app upload/sideload status was already confirmed disabled, and Microsoft documentation describes WIQD provisioning as using a package-and-sideload loop. This target is therefore blocked for the proposed WIQD provisioning route. No qualifying Development/Test target was identified in the available local surfaces; this does not prove that no other tenant exists. Azure subscription readiness is unknown. The complete effective target correlation, in-scope title inventory, and cleanup-absence proof remain unverified.

The compact sanitized record is [Lab B preflight evidence](evidence/lab-b-preflight.json). [The gate review](lab-b-gate-review.md) contains the read-only method, evidence limits, and current first-party documentation references. Transient authentication and browser-session observations are intentionally not persisted in the qualification baseline.

The Agents Toolkit candidate remains blocked by the fixed sideload constraint. The separate WIQD Personal candidate remains documented but unqualified; the failed Production target and unknown prerequisites keep the route fail-closed. No permission, policy, billing, licensing, or tenant setting was changed.

## Lifecycle and restoration

| Stage | State | Result |
|---|---|---|
| Create/scaffold, validate, package | `NOT_TESTED` | No local agent project was created. |
| Provision, read, update, runtime test, evaluate, share, delete | `NOT_TESTED` | No disposable agent or cloud resource was created. |
| Cleanup | `UNNECESSARY` | There is no resource from this lab to remove. |

Do not repeat the known Production policy check or continue collision/cleanup checks until an already-authorized target qualifies and its preflight gates can be established. A different target or any change to the approved bytes requires a new specification and explicit approval. Labs A and D remain frozen; Lab C is independent. No merge or push occurred.

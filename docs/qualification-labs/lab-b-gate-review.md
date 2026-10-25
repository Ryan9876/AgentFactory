# Lab B gate review and proposed specification revision

**Review date:** 2026-10-23
**Historical preflight specification SHA-256:** `43afbd15acde0c6129dc5884203bf336d3dc0943c58f470c3265969e3e7ca5f8`
**Disposition:** Read-only target preflight only. No cloud resource or local agent project created. This specification digest is superseded after sanitization; the target-preflight conclusions remain historical evidence. Any future change to the active specification requires a new digest and explicit approval before implementation.

## Latest target preflight — 2026-10-23

**Terminal state:** `LAB_B_TARGET_GATE = UNQUALIFIED`

**Mutation state:** `CREATE_ALLOWED = NO`

The available local surfaces did not establish a qualifying existing non-Production Microsoft 365 target and Azure subscription together. The approved OpenText Production tenant is positively blocked for WIQD provisioning: Ryan supplied the already-confirmed status `is-sideloading-allowed=false`, and current Microsoft guidance documents `wiqd agent provision` as deploying the packaged app through the package-and-sideload loop. No provisioning, upload, installation, or policy retry was made. Because Azure CLI is not installed and no other candidate was positively discovered, the overall result is `UNQUALIFIED` rather than an assertion that no other tenant or subscription exists.

| Evidence area | Read-only observation | Result |
|---|---|---|
| Existing CLI/toolchain | `wiqd` is installed. `az`, `atk`, `pac`, `m365`, `teams`, and `pwsh` were not available on PATH during the bounded preflight. No tool was installed. | No Azure CLI account/subscription inventory available; no Agents Toolkit or PAC tenant inventory available. |
| Local WIQD project configuration | `wiqd agent env list` in the repository reports “Not an agent project.” No project/environment target was created or inferred. | No configured WIQD environment target available from this checkout. A slot name would not qualify an M365 tenant in any case. |
| Current OpenText target | Approved specification identifies it as live Production. User-supplied current status is `is-sideloading-allowed=false`. | `TARGET_CLASS=DEVELOPMENT_OR_TEST` **NO**; `CUSTOM_APP_UPLOAD=ENABLED` **NO**. This target fails the WIQD requirements. |
| Other M365 target candidates | No non-Production tenant surfaced in the available local/configured tool surfaces. | None positively identified; this is not proof that no other tenant exists. |
| Azure subscription | Azure CLI is absent; no already-authenticated Azure subscription view was available. | `AZURE_SUBSCRIPTION=UNKNOWN`, not PASS and not FAIL. |
| Current-user target access | No alternate development/test tenant was discovered to test access against. | No candidate meets all five required conditions. |

Microsoft's [MCP plugin build walkthrough](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/build-mcp-plugins) explicitly calls the WIQD path a package-and-sideload loop and says `wiqd agent provision` deploys the package to the tenant for testing. Microsoft's [WIQD setup prerequisites](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/prerequisites) require a development or test tenant and permission for the custom-app actions needed by the route. Together with the user-supplied false sideload status, this resolves the previously open question for the approved Production target. The false policy result was not re-queried.

**Gate conclusion:** the known Production candidate is blocked by fixed tenant policy and does not qualify as a development/test target. No alternate candidate was established. Azure subscription readiness and the universe of other accounts remain unknown because no Azure CLI or other authorized inventory surface was available. Do not continue to uniqueness/cleanup checks, and do not create an agent, until a non-Production M365 target is positively identified using existing authority and its upload status, subscription, and current-user access are all verifiably enabled. Do not use the Power Platform `Developer` environment, Copilot Studio Sandbox routing group, a WIQD slot name, or opaque `tenant-1` as target-class evidence.

## Gate classification

| Gate | Classification | Evidence and consequence |
|---|---|---|
| Agents Toolkit custom-app upload/sideload | **Fixed policy constraint for the current Production target** | The supplied current-tenant status is `is-sideloading-allowed=false`. Keep Agents Toolkit rejected for this target. |
| Authentication evidence | **Transient and not retained** | Previous execution-context observations do not establish the target, inventory, or cleanup gates. Do not inspect credential storage or repeat sign-in to explain them. |
| WIQD target type | **Documented prerequisite conflict; not an observed permission denial** | The approved target is explicitly the live corporate/Production tenant. Current Microsoft WIQD-specific prerequisites call for a development or test tenant. General Copilot extensibility guidance separately allows some development directly in an eligible production environment, so these pages do not establish that this WIQD route is denied; they do leave the approved Production target unqualified against the WIQD-specific prerequisite. Do not infer the Power Platform Development environment is a WIQD tenant. Before any cloud operation, establish that an already-authorized target qualifies as a WIQD development/test tenant. If only the recorded Production tenant is available, stop; do not silently substitute a target or seek a new tenant/permission. A different target requires a revised specification and explicit approval. |
| WIQD provision on current Production target | **Fixed policy constraint** | Microsoft documents `wiqd agent provision` as part of the package-and-sideload loop that deploys the packaged app into the tenant for testing. The supplied current-tenant status is `is-sideloading-allowed=false`. Therefore this approved Production target cannot perform WIQD provisioning. No retry or bypass is appropriate. A different already-authorized development/test tenant must independently pass the full target gate. |
| Effective WIQD target tenant | **Verification-method gap** | Existing evidence does not establish which tenant a future WIQD environment will target. WIQD documents that the selected environment file controls the tenant used for upstream authentication. Resolve through the exact environment target configuration and an authorized target assertion; do not infer a match from project-slot names or incomplete identifiers. |
| Azure subscription for WIQD provisioning | **Required platform prerequisite; current access unknown** | Current Microsoft documentation lists an Azure subscription when provisioning WIQD agents. Existing subscription access has not been established. This is not yet a demonstrated permission denial. Check only whether an already-existing subscription is available in the already-authorized qualifying target directory and whether the signed-in identity can use the documented provision route. Visibility of a subscription alone does not prove provisioning authorization. If absent or denied, stop; do not create a subscription, request roles, or change billing. |
| Work IQ inventory surface | **Unverified and not required to change the current gate** | `wiqd agent list` belongs to the separate Work IQ extension; its inventory completeness is unproven. Do not treat that as an authorization denial or retry it for the blocked Production target. |
| Optional sharing | **Unnecessary for the proposed private owner-only lifecycle** | The inspected local WIQD template resolves to Personal/owner-only. Remove optional sharing from the revised test path. If the generated project or platform requests Shared/Tenant scope or a share action to make the agent accessible to Ryan as owner, stop rather than broadening access. |
| Name uniqueness | **Verification-method gap** | The prior Agent Store exact-name search had no visible result, and the expanded installed-agent list was not complete for owned/unacquired Personal titles. The Developer Portal's zero-app result covers app records only. None proves the exact in-scope title is absent. |
| Complete cleanup | **Verification-method gap, with a supported cleanup path identified** | Installed WIQD source inspection found that title-ID-only deletion does not remove the Developer Portal app record; environment/project deletion covers both the portal app and the Microsoft 365 title/acquisition for the inspected template. The remaining gap is a bounded, complete absence check for every created resource after cleanup. A missing `agent info` result alone is ambiguous and is not sufficient. |
| Local toolchain | **Verified for tool presence only** | Node 24 and WIQD Core were present during preflight. Tool presence does not prove Azure subscription eligibility or any cloud lifecycle operation. |

**Bottom line:** both Agents Toolkit and WIQD provisioning are blocked in the current Production tenant by the confirmed disabled custom-app upload/sideload policy. This is target-specific and does not prove WIQD is blocked in every tenant. No existing development/test candidate was found in available local surfaces; Azure subscription readiness is unknown. Overall target discovery is unqualified, and Lab B is stopped before downstream uniqueness/cleanup work.

## Concrete read-only preflight plan

The approved bytes authorize only Ryan's existing OpenText corporate tenant, one new private disposable agent, synthetic fixture only, and no tenant-wide publication or access changes. The current target has now been positively ruled out for WIQD provisioning. The target-only inventory above is the latest preflight; the remaining uniqueness and cleanup checks below are **deferred** and must not be run unless an already-authorized alternate target first qualifies. No cloud mutation is eligible under the current target.

1. **Preserve the approved scope.** Verify the current specification digest against the approval sidecar. Keep the exact proposed name `AgentFactory Qualification B 2026-10-23 337e6f3c (DISPOSABLE)` unless a collision is found. A collision requires a replacement name and a new reviewed/approved digest; never silently rename.

2. **Verify identity without reauthentication.** In the existing authenticated-local context, use the already-supported `wiqd auth status --json` and retain only the Core account/state. In Chrome Stable's existing `AgentFactory` profile, verify `smithr@opentext.com` and the OpenText directory in the account UI. If Core is signed out in the context being used, stop; do not inspect caches or repeat sign-in to explain the discrepancy.

3. **Resolve the WIQD target type, then check an existing Azure subscription.** This target-only gate was not cleared: the available tools exposed only the Production tenant, which fails the supplied custom-app policy status and the WIQD development/test requirement. Azure subscription state remains unknown because Azure CLI is not installed and no already-authenticated subscription view was available. Do not create a subscription, change billing, request roles, or start Azure login.

4. **Bind the future WIQD environment and operation set.** Deferred. Do not scaffold a local agent project or create a WIQD environment until a qualifying target is established and a revised specification is explicitly approved. Any later target check must use an allowlist of nonsecret target fields and compare the actual configured tenant to the verified M365 tenant and existing subscription directory.

5. **Check uniqueness through bounded user/agent-specific reads.** Deferred. Do not repeat inventory or cleanup work for the blocked Production target.

6. **Reconfirm cleanup before provision.** Deferred until a target qualifies and the specification is revised and approved.

7. **Run the minimum lifecycle only after every read-only gate passes.** Not authorized by this target-preflight task; no CREATE, package upload, provisioning, share, or publish operation was run.

8. **Clean up and prove each resource absent.** Not applicable; no resource was created. Keep cleanup proof deferred with uniqueness checks.

## Changes required to the approved specification

The current approved text remains unchanged at the hash above. The following edits are required in a new revision before any implementation:

### Replace the conditional Azure prerequisite

**Current:** “Azure subscription/access only if required by the selected provision operation.”

**Proposed:** “An already-existing Azure subscription accessible to Ryan in the verified OpenText tenant is a required WIQD provisioning prerequisite. Verify it through read-only account/subscription views before provisioning. No subscription creation, billing activation, or role/permission change is authorized. If unavailable, stop and record the WIQD route blocked under current entitlements.”

### Resolve the Production versus WIQD development/test target

**Current:** The approved specification explicitly names Ryan's existing live corporate/Production tenant as the WIQD target.

**Required before implementation:** The current [Microsoft WIQD setup prerequisites](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/prerequisites) list a development or test tenant for Work IQ Dev Tools. General Copilot extensibility docs permit some development in an eligible Production environment, but they do not waive the WIQD-specific requirement. The revised specification must either identify an already-authorized qualifying development/test tenant and replace every target reference with its verified identity/tenant details, or retain Production and record the route blocked until Microsoft documentation/support establishes that this WIQD scenario is supported there. Do not create or request another tenant. Any target change requires Ryan's explicit approval of the new exact specification bytes.

### Resolve whether WIQD invokes a fixed-disabled app-install operation

**Current:** The approved WIQD candidate is treated as independent of the blocked Agents Toolkit route, while Microsoft setup prerequisites also require a target that permits whichever custom-app installation, sharing, or catalog actions the chosen WIQD operation needs.

**Required before implementation:** Map the selected Personal create/provision/test path to current documented operations and the installed package's nonsecret operation contract. Sharing and catalog publication are excluded. If the Personal path requires the known-disabled upload/sideload action, classify WIQD as blocked by that fixed policy. If it does not, retain the independent WIQD candidate but leave tenant-specific eligibility unverified until all other gates pass. Do not invoke provision to discover whether policy blocks it.

### Replace tenant verification language

**Current:** “Verify the effective WIQD deployment identity and tenant match that intended account and tenant before provisioning.”

**Proposed:** “Verify the signed-in Core identity as `smithr@opentext.com`; verify the Azure subscription's directory and the selected WIQD project's actual named-environment target match the OpenText tenant GUID shown in the existing account/portal UI. Inspect only nonsecret environment fields. WIQD's masked `tenant-1` report label is not a tenant ID and cannot be compared across reports. If the current supported environment configuration cannot expose the target before provisioning, stop before provision.”

### Replace collision and cleanup gates

**Current:** one exact-name absence check and a generic resource-specific delete/absence contract.

**Proposed:** “Before provision, check the exact approved title in the complete owner/Can-edit My agents view and one bounded exact-marker `wiqd agent list` query if the existing Work IQ provider is already usable; the latter must show a complete, nontruncated result for the in-scope title class. Refresh the Developer Portal Apps baseline for its separate app-record scope. If any view is unavailable or incomplete, stop. Before provision, verify the exact isolated project's environment-delete contract covers all returned resource types. After provision, record returned IDs; delete by isolated project/environment so both the Developer Portal app and Microsoft 365 title/acquisition are removed. Verify the title ID absent through a complete exact-ID inventory and the app ID absent from Developer Portal Apps. A failed `agent info` lookup alone is not proof of absence. Stop if any cleanup path or verification is ambiguous.”

### Remove optional sharing from the test sequence

Use Personal owner-only scope and Ryan as sole owner. Remove the optional `SHARE` stage from this qualification route. Any generated Shared/Tenant scope, access prompt, or requirement to add users/groups is a stop condition. Keep organization-catalog publication excluded.

These changes alter the approved bytes and therefore require a fresh specification digest and Ryan's explicit approval. The prior approval cannot be carried over to the revised bytes.

## Current first-party references

- Microsoft, [Compare tools for declarative agents](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-tool-comparison) — lists an Azure subscription as a Work IQ Dev Tools provisioning requirement.
- Microsoft, [Build a plugin for a declarative agent from an MCP server](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/build-mcp-plugins) — documents the Work IQ package-and-sideload loop and says `wiqd agent provision` deploys the package to the tenant for testing.
- Microsoft, [Set up your development environment for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/prerequisites) — current Work IQ Dev Tools prerequisites include a development or test tenant; the same page separately describes a licensed Production environment as a general Copilot development option. This leaves the recorded Production target unresolved for the WIQD-specific route.
- WIQD, [Environments](https://microsoft.github.io/wiqd/concepts/environments/) — documents that the selected named environment determines the tenant the upstream tool authenticates against and the app registration updated; names such as `local` are conventions, not enforced targets.
- WIQD, [Authentication](https://microsoft.github.io/wiqd/getting-started/authentication/) — documents that `tenant-1` labels are report-local and raw tenant IDs are not displayed; the Work IQ extension does not expose a supported read-only auth-status command.
- WIQD, [CLI reference](https://microsoft.github.io/wiqd/cli/reference/) — documents `wiqd agent list` substring filters and environment/project deletion options.
- Microsoft, [Share and manage agents built in Agent Builder](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-share-manage-agents) — documents `My agents → View all agents` and the ownership/Can edit coverage of that view.
- Microsoft Graph, [List Copilot packages](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/admin-settings/package/copilotpackages-list) — tenant package inventory requires Microsoft Agent 365 licensing and `CopilotPackages.Read.All`; this review does not assume either and does not propose requesting them.

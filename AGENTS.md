# AgentFactory Codex Guidance

This repository implements the M365 Agent Factory skill pack.

Before making architectural or workflow changes, review:

- docs/specs/m365-agent-factory-spec.md
- docs/architecture.md
- docs/installation.md

## Workflow

Follow this sequence:

objective
→ clarification
→ architecture
→ specification
→ approval
→ build
→ evaluation
→ verification
→ package

Do not bypass specification approval.

## Safety and accuracy

Do not invent:

- tenant IDs
- environment IDs
- connector operations
- credentials
- URLs
- Microsoft platform capabilities
- deployment results

Default platform work to Development unless explicitly instructed otherwise.

Prefer existing repository conventions over introducing new frameworks.

For current Microsoft 365, Power Platform, Copilot Studio, Graph, Entra,
Azure, or Microsoft agent-platform details, consult Microsoft Learn before
relying on remembered commands or APIs.

## Verification

Before completing repository changes, run:

./scripts/verify.sh

Report any failed or skipped checks.

Do not claim tenant-side or portal-side configuration succeeded unless it was
actually verified.

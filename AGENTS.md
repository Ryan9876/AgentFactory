cat > AGENTS.md <<'EOF'
# AgentFactory Codex Guidance

This repository implements the M365 Agent Factory skill pack.

Before making architectural or workflow changes, review:

- docs/specs/m365-agent-factory-spec.md
- docs/architecture.md
- docs/installation.md
- docs/workflow.md

## Workflow

Follow the repository's existing approval-gated workflow.

Do not bypass specification approval.

Default Microsoft platform work to Development unless explicitly instructed otherwise.

Production deployment or organization-wide publication requires explicit approval.

## Accuracy

Do not invent:

- tenant IDs
- environment IDs
- connector operations
- credentials
- URLs
- Microsoft platform capabilities
- deployment or verification results

For current Microsoft 365, Power Platform, Copilot Studio, Graph, Entra,
Azure, or Microsoft agent-platform details, use current Microsoft Learn
documentation rather than relying only on remembered commands or APIs.

## Verification

Before completing repository changes, run:

python3 -m unittest discover -s tests -v

Report failed or skipped checks.

Do not claim tenant-side or portal-side configuration succeeded unless it was
actually observed or verified.
EOF
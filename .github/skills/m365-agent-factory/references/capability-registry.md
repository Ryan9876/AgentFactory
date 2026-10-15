# Capability registry contract — planned, not implemented

The registry lets Microsoft capabilities evolve independently of this control plane. Each entry should record capability family, provider/skill, supported operation scope, discovery/install path, host and version, compatibility evidence and date, prerequisites/permissions, limitations, and unavailable behavior. Mark capabilities unverified until checked against current primary documentation and the target environment. Do not pin the design to an unverified command. Missing required capability becomes an explicit blocker.

Expected families: Standard Copilot Studio author/manage/test/advisor; conditional newer Copilot Studio/GHCP plugin and architect; Power Automate connector/operation discovery, create/edit/validate/preflight/run/diagnose; Dataverse metadata/data/security/admin/solutions/ALM; Microsoft agent evaluation; Power Platform solutions and PAC CLI.

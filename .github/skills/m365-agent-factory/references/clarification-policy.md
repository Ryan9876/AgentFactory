# Clarification policy

## Evidence intake

Inspect all supplied conversation and project context before asking questions. Treat a statement as a fact only when supplied by the user or authoritative project artifact. Keep inferences in an assumptions list with their basis. Keep unresolved details in an unknowns list with impact and disposition.

## Ask only consequential questions

An unknown is consequential when its answer can materially change:

- required behavior or business outcome;
- architecture or authoritative data source;
- identity, authentication, or permissions;
- a consequential action or its confirmation boundary;
- user experience or escalation;
- evaluation criteria or release acceptance;
- deployment target or release safety.

Do not ask about a detail that can be safely resolved in a later architecture or preflight step. Record the unknown and the stage that owns it. Do not run a generic requirements interview or repeat information already provided.

## Ask in a useful form

- Prefer one grouped clarification round containing only currently blocking consequential questions.
- State briefly which decision each question affects.
- Give a safe recommended default when one exists, clearly labeling it as a proposal that requires acceptance.
- A second round is allowed only for genuinely blocking unknowns exposed by the first answers.
- If a safe default cannot be established, keep the decision blocked rather than guessing.

## Safety and disposition

Never invent integrations, tenant/environment IDs, connector names or operations, schemas, credentials, permissions, or URLs. Never treat silence as approval of a consequential action. An unresolved consequential unknown blocks architecture or implementation when it prevents a safe decision; the user may explicitly accept a documented assumption where appropriate. Preserve deferred unknowns in project state and resolve them at their stated stage.

Record intake using `templates/objective.md`. Do not draft architecture while a blocking consequential unknown remains. Once the intake gate is clear, continue to the architecture decision before drafting the implementation specification.

# Scenario: interrupted build

Expected: read persisted state and approved hash; inspect existing platform artifacts; reuse completed verified work; resume at the first incomplete component. If the spec hash changed, set `SPEC_CHANGED` and block until reapproved.

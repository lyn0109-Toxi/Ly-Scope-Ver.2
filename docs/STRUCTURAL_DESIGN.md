# LY-Scope Ver.2 Structural Design

This document captures the current Ver.2 information architecture and screen structure.

## Screen Order

```text
Decision Cockpit
-> Visual Signal Board
-> Decision Logic Chain
-> Architecture Rail
-> Decision Inputs
-> Portfolio, Stock Research, and Real Estate Detail
-> Scenario Model
-> Decision Evidence
-> AI Interpretation
-> Decision Memory
-> Ver.1 Legacy Foundation
```

## Product Principle

The app should feel like a working decision console, not a landing page. The first viewport shows the current decision, recommendation, score, and primary operating controls. Detailed modules are grouped below by decision flow.

For customer-facing reading, the first layer should not assume the user understands detailed numbers. It should answer three questions visually before asking the user to inspect figures:

- What is my current situation?
- What direction gets me closer to the goal?
- Where is the crisis or risk?

## Layout Zones

| Zone | Role |
| --- | --- |
| Top Bar | Project identity and explicit actions: save, export, reset |
| Decision Cockpit | Current question, recommendation signal, and score; supporting text and metrics reveal on hover/click |
| Visual Signal Board | Customer-facing picture of now, direction, and crisis, with numbers and text revealed on hover/click |
| Decision Logic Chain | Shows why the recommendation follows from financial base, goal pressure, scenario effect, risk, evidence, and final decision; explanation text is hidden until hover/click |
| Architecture Rail | Persistent map of `User -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory` |
| Workspace Main | Editable modules grouped by the decision flow |
| Legacy Foundation | Preserved Ver.1 data, formulas, and migration status |

## Section Boundaries

| Section | Owns |
| --- | --- |
| Decision Inputs | User profile, financial foundation, goals |
| Portfolio, Stock Research, and Real Estate Detail | Portfolio holdings, selected stock assumptions, real estate assumptions, Ver.1 sample loading, asset scores, warnings, forecast |
| Scenario Model | Scenario assumptions, risk and resilience |
| Decision Evidence | Evidence signals generated from the model |
| AI Interpretation | Plain-language decision reading and next actions |
| Decision Memory | Saved decision log and memory entries |
| Ver.1 Base | Copied Ver.1 reference and ported logic inventory |

## Plausibility Layer

The `Decision Logic Chain` is the first explicit plausibility layer. It should answer:

- What condition creates or weakens decision capacity?
- Which priority pressure competes with the decision?
- Which portfolio, market asset, or real estate detail changes the evidence balance?
- What happens under the active scenario?
- Which risk filter changes the interpretation?
- Which evidence signal is strongest?
- Why does the recommendation follow?

This layer should stay short and traceable. It is not a chatbot answer; it is an audit trail that makes the recommendation feel grounded.

## Customer-Facing Display Rule

The default view should prefer visual signals over explanations:

- Show current situation, goal direction, and crisis first.
- Hide detailed text until hover, focus, or click.
- Keep numbers secondary unless the user requests detail.
- Use words like `stable`, `on route`, `watch`, and `crisis` before raw scores.
- Use section details for users who need the underlying assumptions.

## Next Structural Step

The next design pass should introduce actual workspace modes or tabs after the module behavior stabilizes. Good candidates:

- Overview
- Foundation
- Goals
- Scenario
- Evidence
- Decision Memory
- Ver.1 Reference

# Module Boundaries

LY-Scope-Ver.2는 의사결정 흐름을 코드 경계로 분리합니다.

```text
Customer Purpose -> Strategy -> Situation -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory
```

## Dependency Rules

- `src/domain/*` modules do not import `src/ui` or `src/storage`.
- `src/ui` renders state and calls app actions. It does not own financial logic.
- `src/storage` only persists state. It does not calculate decisions.
- `src/app/pipeline.js` is the main orchestrator.
- Future AI provider calls should enter through `domain/ai-interpretation` or an adapter under `src/app`.

## Domain Ownership

| Module | Owns | Does Not Own |
| --- | --- | --- |
| `domain/user` | customer purpose, profile, preferences, priorities | saved decisions |
| `domain/goals` | strategy path, goal pressure, required contribution | scenario math |
| `domain/data` | normalized input snapshot | scoring |
| `domain/financial-foundation` | cash flow, net worth, runway, health | UI labels |
| `domain/projection` | month-by-month projections | recommendation labels |
| `domain/scenario` | changed assumptions and comparison | memory |
| `domain/portfolio` | holdings, market value, concentration, portfolio score | personal cash flow |
| `domain/risk-resilience` | risks, buffers, resilience score | AI prose |
| `domain/evidence` | evidence signals | final recommendation |
| `domain/model` | score and recommendation | natural-language interpretation |
| `domain/ai-interpretation` | plain-language reading | persistence |
| `domain/decision` | decision record | historical insight |
| `domain/memory` | learning summary | current financial calculation |

## Extension Pattern

When adding a new Ver.2 capability:

1. Add a pure domain module first.
2. Add tests for the module.
3. Connect it to `src/app/pipeline.js`.
4. Render the result in `src/ui/render.js`.
5. Persist only the minimum required input state.

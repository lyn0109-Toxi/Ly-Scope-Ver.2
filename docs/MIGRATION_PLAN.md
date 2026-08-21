# Ver.1 to Ver.2 Migration Plan

The Ver.2 base is ready for a no-touch Ver.1 migration. The original Ver.1 app should remain unchanged throughout the process.

## Phase 1: Reference Inventory

- List Ver.1 screens, forms, calculations, storage keys, and AI prompts.
- Mark each item as keep, modify, or retire using `docs/VER1_INVENTORY.md`.
- Identify logic that already has clear inputs and outputs.

## Phase 2: Domain Migration

- Move financial formulas into `domain/financial-foundation`.
- Move goal formulas into `domain/goals`.
- Move projection formulas into `domain/projection`.
- Move scenario formulas into `domain/scenario`.
- Convert risk labels into structured `risk-resilience` outputs.

## Phase 3: Decision Pipeline

- Convert Ver.1 decision logic into model factors.
- Convert supporting data into evidence signals.
- Rewrite AI interpretation so it cites evidence and risk outputs.
- Store final results as decision records and memory entries.

## Phase 4: UI Stabilization

- Preserve familiar Ver.1 workflows where useful.
- Keep Ver.2 screen changes small until the model is stable.
- Add import adapters if Ver.1 local storage or exports need to be read.

## Phase 5: Regression Coverage

- Add tests for every migrated formula.
- Add sample states from Ver.1.
- Compare Ver.1 and Ver.2 outputs before changing the visible experience.

# LY-Scope Ver.2

LY-Scope Ver.2 is a new codebase for a personal decision intelligence app. It does not modify LY-Scope Ver.1. Ver.1 stays as a reference source, while useful logic is migrated into the Ver.2 structure.

The product goal is to help users understand their current financial situation, the direction required to reach goals, and the risks that could block a decision.

## Core Architecture

```text
User -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory
```

The app also includes extension modules for:

- Financial Foundation
- Goals
- Market Assets
- Real Estate
- Portfolio
- Projection
- Scenario
- Risk/Resilience
- Life Board

## Ver.1 Reference

The local development workspace can keep a private Ver.1 reference copy at:

```text
legacy/ver1-reference/
```

That folder is intentionally ignored for the public GitHub repository because it
can contain copied source, reports, and user-like sample data. The original
Ver.1 repository remains untouched.

Ver.2 also includes active JavaScript ports of the most important Ver.1 logic:

- Stock scoring and warnings
- REIT scoring, warnings, and forecast bands
- Real estate market scoring, warnings, forecast bands, mortgage math, and property calculator
- Portfolio snapshot calculations
- Life Board context weighting

## Run Locally

```bash
npm run dev
```

Then open the local URL printed in the terminal.

## Run with Streamlit

Streamlit Cloud can use this compatibility entrypoint:

```text
streamlit_app.py
```

For Streamlit Cloud, set:

- Branch: `main`
- Main file path: `streamlit_app.py`

## Test

```bash
npm test
```

## GitHub

Recommended repository name:

```text
ly-scope-ver2
```

The project includes a GitHub Actions workflow at `.github/workflows/ci.yml`.
It runs syntax checks and tests on pushes and pull requests to `main`.

See `docs/GITHUB_SETUP.md` for the first push checklist.

## Code Map

- `src/app`: application orchestration and the decision pipeline
- `src/core`: architecture metadata
- `src/domain/user`: user profile and preferences
- `src/domain/data`: normalized app data layer
- `src/domain/financial-foundation`: net worth, cash flow, runway, debt, health score
- `src/domain/goals`: goal normalization and progress checks
- `src/domain/market-assets`: Ver.1 stock and REIT scoring ports
- `src/domain/real-estate`: Ver.1 real estate scoring and property calculator ports
- `src/domain/portfolio`: Ver.1-style portfolio snapshot
- `src/domain/life-board`: Ver.1 Life Board context model
- `src/domain/projection`: time-based cash and net worth projection
- `src/domain/scenario`: scenario changes and comparison
- `src/domain/risk-resilience`: risk flags and resilience score
- `src/domain/evidence`: evidence signals
- `src/domain/model`: deterministic recommendation model
- `src/domain/ai-interpretation`: interpretation layer prepared for future AI integration
- `src/domain/decision`: decision records
- `src/domain/memory`: decision memory and learning summary
- `src/storage`: browser-local persistence
- `src/ui`: DOM rendering
- `src/adapters/ver1`: Ver.1 inventory, copied-data loader, and migration bridge
- `legacy/README.md`: local Ver.1 reference policy

## Current Scope

This first Ver.2 base keeps the app intentionally stable: local state, deterministic calculations, visible architecture boundaries, and tests for the decision pipeline. It is ready for Ver.1 logic migration without changing Ver.1.

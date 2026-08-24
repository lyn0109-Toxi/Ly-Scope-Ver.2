# ToxiGuard-NORA Core Ontology

Product class:

```text
Personal Decision Intelligence Application
```

Production app:

```text
https://toxiguard-nora.streamlit.app/
```

ToxiGuard-NORA uses one core decision path:

```text
User -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory
```

## Layer Definitions

| Layer | Purpose | Current App Surface |
| --- | --- | --- |
| User | Understand life stage, income state, capital, goals, horizon, and decision question. | Life, Finance, Advisor Reports |
| Data | Collect structured inputs for finance, holdings, stocks, REITs, real estate exposure, scenarios, and diary snapshots. | Finance, Portfolio, Search, REIT, Diary |
| Model | Calculate valuation, runway, goal progress, portfolio quality, concentration, stress impact, and resilience. | Finance engine, Portfolio metrics, REIT module, Scenario |
| Evidence | Show formulas, source limits, assumptions, warnings, and score drivers before interpretation. | Details, Advisor Reports, AI Coach context |
| AI Interpretation | Translate the evidence into current situation, direction, risk signal, and trade-off language. | AI Coach, Advisor Reports |
| Decision | Produce next action, watch item, avoid item, and report summary without presenting professional advice. | Advisor Reports, Current Situation Report |
| Memory | Store review history, financial diary snapshots, PDF reports, and reusable reasoning context. | Diary, PDF export, JSON download |

## Expansion Modules

| Module | Ontology Role |
| --- | --- |
| Financial Foundation | User + Data + Model baseline for cash flow, debt, savings, runway, and risk capacity. |
| Goals | User intent and measurable target path. |
| Market Assets | Stock/portfolio data, valuation, beta, risk, and concentration. |
| Real Estate | REIT/property-linked exposure, income durability, and rate sensitivity. |
| Projection | Forward view of capital, goal progress, and runway. |
| Scenario | Stress testing for income, expenses, cash shock, portfolio shock, FX, and rates. |
| Risk / Resilience | Crisis signal: liquidity, concentration, volatility, debt pressure, and downside capacity. |
| Evidence | Audit trail for formulas, assumptions, and data quality. |
| AI Interpretation | Plain-language reasoning layer for non-expert customers. |
| Decision | Next step, watch item, avoid item, and PDF-ready conclusion. |
| Memory | Diary, reports, snapshots, and later review context. |

## Product Rule

ToxiGuard-NORA should not jump from data to a recommendation. The app must pass through model, evidence, interpretation, decision framing, and memory so users can understand the situation before acting.

# LY-Scope-Ver.2 Core Ontology

Product class:

```text
Personal Decision Intelligence Application
```

Current Streamlit deployment URL:

```text
https://ly-scope-ver2.streamlit.app/
```

LY-Scope-Ver.2 uses one core decision path:

```text
Customer Purpose -> Strategy -> Situation -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory
```

## Layer Definitions

| Layer | Purpose | Current App Surface |
| --- | --- | --- |
| Customer Purpose | Understand what the customer wants: desired outcome, values, time horizon, constraints, and decision question. | Life, Finance, Advisor Reports |
| Strategy | Turn purpose into a practical path: required capital, sequence, resources, and review rhythm. | Finance, Scenario, Advisor Reports |
| Situation | Read the customer's current reality: capital, income state, expenses, holdings, real estate exposure, liquidity, and risk pressure. | Life, Finance, Portfolio, REIT |
| Data | Collect structured inputs for finance, holdings, stocks, REITs, real estate exposure, scenarios, and diary snapshots. | Finance, Portfolio, Search, REIT, Diary |
| Model | Calculate valuation, runway, goal progress, portfolio quality, concentration, stress impact, and resilience. | Finance engine, Portfolio metrics, REIT module, Scenario |
| Evidence | Show formulas, source limits, assumptions, warnings, and score drivers before interpretation. | Details, Advisor Reports, AI Coach context |
| AI Interpretation | Translate the evidence into current situation, direction, risk signal, and trade-off language. | AI Coach, Advisor Reports |
| Decision | Produce next action, watch item, avoid item, and report summary without presenting professional advice. | Advisor Reports, Current Situation Report |
| Memory | Store review history, financial diary snapshots, PDF reports, and reusable reasoning context. | Diary, PDF export, JSON download |

## Expansion Modules

| Module | Ontology Role |
| --- | --- |
| Financial Foundation | Situation + Data + Model baseline for cash flow, debt, savings, runway, and risk capacity. |
| Goals | Customer Purpose + Strategy as a measurable target path. |
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

LY-Scope-Ver.2 should not jump from data to a recommendation. The app must first ask what the customer wants, then test the strategy and current situation before moving through data, model, evidence, interpretation, decision framing, and memory.

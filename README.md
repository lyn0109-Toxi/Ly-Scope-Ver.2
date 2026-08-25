# LY-Scope-Ver.2

LY-Scope-Ver.2 is the user-facing product name for the new personal decision intelligence architecture.
Current Streamlit deployment URL:

```text
https://ly-scope-ver2.streamlit.app/
```

Product class:

```text
Personal Decision Intelligence Application
```

The app combines useful Ver.1 market-asset logic with a new personal decision intelligence structure: stock and portfolio valuation, real estate valuation, personal finance, goals, scenario stress tests, advisor-style reports, calculation transparency, AI interpretation readiness, and decision memory.

Ver.1 remains a reference prototype only. Ver.2 should not modify Ver.1 directly.

## Core Ontology

LY-Scope-Ver.2 must keep this decision path visible and intact:

```text
Customer Purpose -> Strategy -> Situation -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory
```

This ontology means every output should answer six customer-facing questions:

- What does the customer want?
- What strategy connects that purpose to action?
- What is the current situation?
- What data and model produced this view?
- What evidence or warning supports it?
- What should be remembered for later review?

See the full product foundation in [`docs/PRODUCT_BLUEPRINT.md`](docs/PRODUCT_BLUEPRINT.md).

## Section Map

- **Financial Foundation:** income, expenses, cash, debt, runway, savings rate, risk capacity.
- **Goals:** target amount, monthly commitment, progress, feasibility.
- **Market Assets:** stock ticker/company search, valuation, risk, beta, portfolio scoring.
- **Real Estate:** property valuation, rent support, cash flow, leverage, stress value, and listed REIT reference data.
- **Projection:** goal and capital path over time.
- **Scenario:** income shock, market shock, FX/rate shock, cash shock.
- **Risk / Resilience:** liquidity, concentration, volatility, downside capacity.
- **Evidence:** formulas, assumptions, data source limits, calculation details.
- **AI Interpretation:** plain-language status, direction, crisis signal, trade-off explanation.
- **Decision:** next action, watch item, avoid item, report output.
- **Memory:** financial diary, report PDFs, snapshots, review history.

## Purpose

This app is designed as an educational personal financial intelligence platform, not an investment recommendation service. The goal is to help users understand, protect, and manage their financial life by connecting income, spending, savings, investments, real estate exposure, portfolio risk, and life goals with real market examples.

## AI Reasoning Era Direction

LY-Scope-Ver.2 is being prepared as an early prototype for the coming AI reasoning and agentic intelligence era. The product direction is not to become a stock picker. It is to become a structured financial reasoning environment where a future AI assistant can help users ask better questions, understand trade-offs, and review the assumptions behind financial decisions.

Future-facing design principles:

- **Reasoning before recommendation:** the app should explain risk, trade-offs, assumptions, and scenarios before suggesting any action.
- **Life context before asset selection:** portfolio analysis should be interpreted alongside income, spending, savings, debt, emergency funds, real estate exposure, and life goals.
- **Scenario support:** users should be able to ask what happens if interest rates change, income falls, portfolio value declines, real estate cash flow weakens, or a major life expense appears.
- **Memory with privacy:** the Financial Diary is a seed for user-controlled financial memory. It should support reflection without requiring sensitive account connections in the prototype stage.
- **Explainability:** Calculation Details should act as a reasoning audit trail, showing formulas, inputs, assumptions, limitations, and data sources.
- **Voice and agent readiness:** future interfaces may use AirPods, mobile assistants, or AI agents. LY-Scope-Ver.2 should support short summaries, deeper explanations, and detailed evidence views.

## Current Preparation Stage

The current project should be treated as an educational prototype and venture-preparation asset. It can support user interviews, professor feedback, portfolio demonstration, pitch preparation, and product validation. It should not be operated as a paid financial advisory service without legal, data licensing, privacy, and immigration review.

Because the founder is considering venture creation while in F-1 student status, monetization, employment through a founder-owned company, and commercial operation should be reviewed with the university DSO and a qualified immigration attorney before launch. In the current stage, the safer positioning is free educational beta, academic validation, and responsible prototype development.

## App Structure

- `streamlit_app.py`: Main LY-Scope-Ver.2 stock valuation and portfolio analytics app.
- `reit_analysis_module.py`: Real Estate valuation module with listed REIT reference data used inside the main app.
- `pages/01_REIT_Focused_Analysis.py`: Optional standalone legacy REIT-focused page.
- `personal_finance_engine.py`: Experimental Personal Finance calculation engine.
- `personal_finance_module.py`: Personal Finance Streamlit UI module.
- `advisor_report_engine.py`: Virtual client advisor report engine with PDF export support.
- `data/virtual_clients.json`: Bilingual fictional client dataset with life situation, finance profile, portfolio sample, valuation upside, and real estate stress inputs.
- `docs/PRODUCT_BLUEPRINT.md`: Canonical Ver.2 product blueprint, target users, ontology, engine map, data schema direction, MVP scope, and Ver.1 migration rule.
- `docs/`: real estate analysis blueprint, personal finance structure, and data dictionary.
- `ontology/`: NORA core ontology and real estate sub-ontology.
- `DATA_SOURCES.md`: Data source, API, limitation, and usage notice.
- `PROFESSOR_REVIEW_AUDIT.md`: Pre-share audit for data provenance, warnings,
  known limitations, and professor demo checklist.

## Planned Analysis Areas

- Stock valuation and portfolio analytics migrated from the Ver.1 reference logic.
- Korean stock search expansion with approximately 100 major KOSPI/KOSDAQ companies searchable by company name or ticker.
- Multi-currency portfolio view for US and Korean stocks, with USD/KRW conversion using a live FX rate when available and a manual fallback rate when live data is unavailable.
- Real estate valuation: property value, rent support, NOI, cap rate, debt service coverage, cash flow, and stress value.
- Listed real estate reference: REIT sector classification, dividend yield, price to FFO, AFFO payout ratio, NAV premium or discount.
- Interest-rate sensitivity: relationship between property financing, listed real estate returns, Treasury yields, and financing conditions.
- Portfolio analysis: real estate allocation, sector concentration, beta, covariance, correlation, diversification, cost basis, unrealized profit/loss, and personal return tracking.
- Educational comparison: stock-style valuation versus property-income valuation.
- Personal Finance test engine: net worth, cash flow, emergency fund, savings rate, debt-to-income, risk capacity, and financial health score.
- Advisor Reports: 10 fictional bilingual client profiles, rule-based advisor interpretation, visual scorecards, portfolio/valuation samples, real estate stress signals, evidence mapping, decision actions, and downloadable selected/all-client PDF reports.
- What-if Scenario Lab: stress-test income, expenses, cash shocks, portfolio moves, USD/KRW changes, interest-rate moves, and rate-sensitive allocation.
- Calculation Details: transparent formulas, data inputs, assumptions, valuation contribution, covariance, correlation, and personal finance score breakdown.
- Financial Diary: session-based portfolio and personal finance snapshots, current situation reports, user notes, next actions, PDF report export, and JSON download/restore.
- Life Design entry screen: one-click first screen that frames LY-Scope-Ver.2 as a personal life and financial intelligence dashboard before entering the main app.
- AI Coach: rule-based by default, with linked guidance cards for Portfolio, Personal Finance, Scenario, Diary, and Calculation Details plus an optional verified OpenAI Responses API layer for structured reasoning answers.
- Structured Scenario Packet: downloadable JSON context that can later become an input format for an AI financial reasoning coach.

## Streamlit Cloud

Main file:

```text
streamlit_app.py
```

Recommended secrets:

```toml
FINNHUB_API_KEY = "your_finnhub_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
OPENAI_MODEL = "gpt-5-mini"
OPENAI_REASONING_EFFORT = "medium"
OPENAI_AI_DEFAULT_ON = "false"
```

The app can run with sample real estate and listed REIT reference data even when an API key is not configured.

`OPENAI_API_KEY` is optional. Without it, AI Coach remains a local rule-based prototype. With it, users can enable a verified model mode that sends structured LY-Scope-Ver.2 context to OpenAI's Responses API and then passes the answer through local safety validation before display.

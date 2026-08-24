# LY-Scope-Ver.2 Product Blueprint

## Canonical Definition

LY-Scope-Ver.2 is the user-facing product name for the new personal decision intelligence architecture.

Product class:

```text
Personal Decision Intelligence Application
```

Current Streamlit deployment URL:

```text
https://toxiguard-nora.streamlit.app/
```

Core ontology:

```text
Customer Purpose -> Plan -> Situation -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory
```

LY-Scope Ver.1 remains a reference prototype only. Ver.2 should not modify Ver.1 directly. Useful Ver.1 logic may be migrated only when it fits the Ver.2 ontology, data boundary, and educational safety rules.

## Product Thesis

Most customers do not need more raw numbers first. They need to clarify what they want, understand the plan that could reach it, read the current situation honestly, see the risks that could interrupt that path, and inspect the evidence behind the interpretation.

LY-Scope-Ver.2 should turn financial fragments into a structured decision memory:

- What does the customer want?
- What plan connects that purpose to action?
- What is the user's current life and financial situation?
- What data is known, missing, delayed, or assumed?
- What model produced the current reading?
- What evidence supports the reading?
- What does the situation mean in plain language?
- What decision direction is reasonable to consider?
- What should be saved for later review?

## Target Users

### 1. Capital Holder in Study or Career Transition

Example: a user who worked for many years, saved capital, is currently studying, and has little or no active income.

Primary need: protect runway, understand portfolio exposure, avoid forced selling, and plan the next income or liquidity decision.

### 2. Self-Directed Investor

Example: a user with several stock positions across U.S. and Korean markets.

Primary need: search by ticker or company name, understand valuation, portfolio concentration, beta, sector exposure, and risk quality.

### 3. Real Estate-Aware Household

Example: a user with REIT exposure, property interest, rent sensitivity, or mortgage/rate concerns.

Primary need: connect real estate exposure with income durability, rates, liquidity, and scenario stress.

### 4. Goal-Oriented Planner

Example: a user saving for tuition, home purchase, emergency fund, family support, or business launch.

Primary need: convert a target into monthly effort, feasibility, risk signal, and review rhythm.

### 5. Advisor / Professor / Demo Reviewer

Example: a reviewer who needs to inspect the logic, evidence, limits, and user journey.

Primary need: clear audit trail, fictional client reports, formula transparency, and exportable PDF summaries.

## Customer Promise

LY-Scope-Ver.2 should help the user see three things before acting:

- Customer purpose: what the user actually wants and why it matters.
- Plan: what path, resources, sequence, and review rhythm are needed.
- Situation and crisis signal: where the user stands now and what could break the path.

The interface should be visual-first. Detailed text and numbers should appear through hover, click, expandable details, report export, and calculation transparency rather than overwhelming the first view.

## Core User Journey

1. Customer Purpose
   The app asks what the customer wants, why it matters, the time horizon, constraints, values, and the decision question.

2. Plan
   The app turns purpose into a practical path: required capital, sequence, resources, and review rhythm.

3. Situation
   The app reads current reality: capital, income state, spending, liquidity, holdings, real estate exposure, and risk pressure.

4. Data
   The app collects structured inputs: cash, debt, income, expenses, holdings, market assets, real estate exposure, scenarios, and diary notes.

5. Model
   The app calculates financial foundation, valuation, diversification, runway, goal progress, stress impact, and resilience.

6. Evidence
   The app exposes formulas, assumptions, data source limits, confidence signals, and warnings.

7. AI Interpretation
   The app converts evidence into plain-language status, direction, crisis point, and trade-off explanation.

8. Decision
   The app frames next action, watch item, avoid item, and report conclusion without pretending to provide professional advice.

9. Memory
   The app saves diary entries, snapshots, PDF reports, and reusable context for future review.

## Engine Map

| Engine | Role | Current or Near-Term Surface |
| --- | --- | --- |
| User Profile Engine | Captures life stage, income state, location, horizon, and goals. | Life, Finance |
| Financial Foundation Engine | Calculates net worth, monthly cash flow, emergency runway, savings rate, debt pressure, and risk capacity. | Finance |
| Goals Engine | Turns user targets into progress, required contribution, and feasibility. | Finance, Scenario |
| Market Asset Engine | Searches stocks by ticker or company name and applies valuation/risk readings. | Search, Portfolio |
| Portfolio Engine | Scores holdings, concentration, beta, sector exposure, valuation mix, and diversification. | Portfolio |
| Real Estate Engine | Models REIT/property-linked exposure, rate sensitivity, income pressure, and allocation fit. | REIT |
| Projection Engine | Projects capital path, goal path, and runway over time. | Scenario |
| Scenario Engine | Stress-tests income loss, expense increase, cash shock, market decline, FX movement, and rates. | Scenario |
| Risk / Resilience Engine | Converts shocks into crisis signals and protection gaps. | Finance, Portfolio, Scenario |
| Evidence Engine | Keeps formulas, data assumptions, warnings, and source limits inspectable. | Details |
| AI Interpretation Engine | Converts structured context into plain-language reasoning. | AI Coach, Advisor Reports |
| Decision Engine | Produces next action, watch item, avoid item, and report summary. | Advisor Reports, Diary |
| Memory Engine | Stores snapshots, notes, PDF reports, and review history. | Diary |

## Data Schema Direction

### user_profile

```text
user_id, language, life_stage, income_state, household_context, location,
planning_horizon_months, primary_question
```

### finance_snapshot

```text
cash, investments, real_estate_value, debt, monthly_income, monthly_expenses,
monthly_savings, emergency_months, net_worth, currency, timestamp
```

### goal

```text
goal_id, label, target_amount, current_amount, target_date,
monthly_commitment, priority, confidence
```

### holding

```text
ticker, company_name, market, sector, shares, average_cost,
current_price, currency, beta, dividend_yield, valuation_status
```

### market_asset_snapshot

```text
ticker, company_name, price, fair_value_estimate, upside,
valuation_inputs, risk_inputs, source_notes, timestamp
```

### real_estate_exposure

```text
property_type, market_region, reit_ticker, property_value,
debt_amount, rent_income, rate_sensitivity, income_sensitivity
```

### scenario_packet

```text
income_shock, expense_shock, cash_shock, market_shock,
fx_shock, rate_shock, stressed_capital, resilience_score
```

### evidence_item

```text
evidence_id, layer, source, formula, input_values,
assumption, limitation, confidence, warning
```

### interpretation

```text
status, direction, crisis_signal, tradeoffs, confidence,
linked_evidence_ids
```

### decision_record

```text
decision_id, question, decision_status, next_action,
watch_item, avoid_item, review_date, linked_snapshot_id
```

### memory_entry

```text
entry_id, timestamp, snapshot_summary, user_note,
decision_record_id, report_file, review_outcome
```

## MVP Scope

Ver.2 should focus on a stable, explainable base before adding heavy automation:

- Visual-first dashboard tied to the NORA ontology.
- Bilingual English/Korean interface, with English as default.
- Finance input and financial foundation scoring.
- Ticker or company-name stock search.
- Portfolio scoring for multiple holdings.
- Stock valuation lens migrated from useful Ver.1 logic.
- REIT and real-estate exposure analysis.
- Goal and scenario stress-testing.
- Evidence and calculation transparency.
- Rule-based AI interpretation layer, with optional verified model mode.
- Virtual client advisor reports.
- PDF export for reports and current situation summaries.
- Diary and decision memory.

## Out of Scope Until Ready

- Paid financial advisory operation.
- Automated trading or direct buy/sell instructions.
- Production account aggregation.
- Unlicensed redistribution of market, real estate, MLS, or broker data.
- Tax, legal, accounting, immigration, or professional financial advice.
- Durable multi-user storage without privacy, consent, security, and data-retention design.

## Migration Rule From Ver.1

Ver.1 content may be carried into Ver.2 only when it passes this filter:

1. It supports one or more NORA layers.
2. It preserves useful educational logic.
3. It can be explained in calculation details or evidence.
4. It avoids direct advice language.
5. It fits the new modular boundary.

## Verification Checklist

Each major feature should be checked against three questions:

- Ontology check: does it move through Customer Purpose -> Plan -> Situation -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory?
- Customer check: can a non-expert understand purpose, plan, situation, and crisis signal visually?
- Evidence check: can the formulas, assumptions, and limits be inspected before trusting the output?

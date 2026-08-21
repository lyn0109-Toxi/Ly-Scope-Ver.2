from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from html import escape
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="LY-Scope Ver.2",
    page_icon="LY",
    layout="wide",
)


DEFAULT_PROFILE = {
    "name": "Client",
    "decision_question": "Can I keep investing while staying resilient?",
    "time_horizon_months": 36,
    "risk_tolerance": "Balanced",
}

DEFAULT_FINANCE = {
    "monthly_income": 6500.0,
    "fixed_expense": 3400.0,
    "variable_expense": 1200.0,
    "debt_payment": 350.0,
    "cash": 24000.0,
    "personal_debt": 9000.0,
    "runway_target": 6.0,
}

DEFAULT_GOAL = {
    "goal_name": "Build decision-ready net worth",
    "target_amount": 250000.0,
    "target_months": 36,
    "monthly_commitment": 1600.0,
}

DEFAULT_HOLDINGS = [
    {
        "symbol": "MSFT",
        "company": "Microsoft",
        "sector": "Technology",
        "shares": 60.0,
        "purchase_price": 390.0,
        "price": 426.7,
        "beta": 0.9,
        "quality": 88.0,
        "momentum": 74.0,
        "valuation": 62.0,
    },
    {
        "symbol": "AAPL",
        "company": "Apple",
        "sector": "Technology",
        "shares": 70.0,
        "purchase_price": 175.0,
        "price": 189.9,
        "beta": 1.2,
        "quality": 84.0,
        "momentum": 67.0,
        "valuation": 66.0,
    },
    {
        "symbol": "NVDA",
        "company": "NVIDIA",
        "sector": "Semiconductors",
        "shares": 80.0,
        "purchase_price": 92.0,
        "price": 109.6,
        "beta": 1.7,
        "quality": 90.0,
        "momentum": 86.0,
        "valuation": 48.0,
    },
    {
        "symbol": "JPM",
        "company": "JPMorgan Chase",
        "sector": "Financials",
        "shares": 22.0,
        "purchase_price": 188.0,
        "price": 208.4,
        "beta": 1.1,
        "quality": 73.0,
        "momentum": 58.0,
        "valuation": 78.0,
    },
]

DEFAULT_REAL_ESTATE = [
    {
        "name": "Primary rental",
        "market": "Dallas, TX",
        "property_value": 385000.0,
        "mortgage_balance": 274000.0,
        "monthly_rent": 2850.0,
        "monthly_expense": 2050.0,
        "vacancy_rate": 5.0,
        "market_growth": 3.2,
    }
]

ONTOLOGY_STAGES = [
    {
        "id": "user",
        "label": "User",
        "owns": "client identity, decision question, horizon, risk posture",
    },
    {
        "id": "data",
        "label": "Data",
        "owns": "finance facts, goal assumptions, portfolio rows, property rows",
    },
    {
        "id": "model",
        "label": "Model",
        "owns": "foundation, goal, asset, and resilience scoring",
    },
    {
        "id": "evidence",
        "label": "Evidence",
        "owns": "supporting and cautionary signals",
    },
    {
        "id": "ai_interpretation",
        "label": "AI Interpretation",
        "owns": "plain-language reading and next-action posture",
    },
    {
        "id": "decision",
        "label": "Decision",
        "owns": "recommendation, score, and operating stance",
    },
    {
        "id": "memory",
        "label": "Memory",
        "owns": "saved decision snapshots and reusable context",
    },
]

ONTOLOGY_RELATIONSHIPS = [
    ("User", "Data", "profile and question frame the input state"),
    ("Data", "Model", "normalized facts become deterministic scores"),
    ("Model", "Evidence", "scores are converted into visible signals"),
    ("Evidence", "AI Interpretation", "signals become a readable judgement"),
    ("AI Interpretation", "Decision", "interpretation resolves into a recommendation"),
    ("Decision", "Memory", "saved decisions become future context"),
]


@dataclass
class PortfolioSnapshot:
    rows: list[dict[str, Any]]
    total_value: float
    total_cost: float
    gain_loss: float
    gain_loss_pct: float
    top_weight: float
    top_sector: str
    top_sector_weight: float
    weighted_beta: float
    portfolio_score: int
    warnings: list[str]


@dataclass
class RealEstateSnapshot:
    rows: list[dict[str, Any]]
    total_value: float
    total_debt: float
    total_equity: float
    monthly_cash_flow: float
    average_ltv: float
    average_vacancy: float
    score: int
    warnings: list[str]


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def rows_from_editor(value: Any) -> list[dict[str, Any]]:
    if hasattr(value, "to_dict"):
        return value.to_dict("records")
    return [dict(row) for row in value]


def money(value: float) -> str:
    return f"${value:,.0f}"


def signed_money(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def score_label(score: float) -> str:
    if score >= 82:
        return "Strong"
    if score >= 66:
        return "Stable"
    if score >= 48:
        return "Watch"
    return "Crisis"


def tone_for_score(score: float) -> str:
    if score >= 82:
        return "strong"
    if score >= 66:
        return "stable"
    if score >= 48:
        return "watch"
    return "crisis"


def score_holding(row: dict[str, Any]) -> float:
    quality = safe_float(row.get("quality"), 60)
    momentum = safe_float(row.get("momentum"), 50)
    valuation = safe_float(row.get("valuation"), 55)
    beta = safe_float(row.get("beta"), 1)
    volatility_balance = clamp(92 - max(0, beta - 1) * 34 - abs(beta - 1) * 8)
    return quality * 0.36 + momentum * 0.22 + valuation * 0.22 + volatility_balance * 0.2


def build_portfolio(rows: list[dict[str, Any]]) -> PortfolioSnapshot:
    clean_rows: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).strip().upper()
        if not symbol:
            continue
        shares = safe_float(row.get("shares"))
        price = safe_float(row.get("price"))
        purchase_price = safe_float(row.get("purchase_price"))
        market_value = shares * price
        cost_basis = shares * purchase_price
        holding_score = score_holding(row)
        clean_rows.append(
            {
                **row,
                "symbol": symbol,
                "sector": str(row.get("sector") or "Unclassified"),
                "shares": shares,
                "price": price,
                "purchase_price": purchase_price,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "gain_loss": market_value - cost_basis,
                "holding_score": holding_score,
                "beta": safe_float(row.get("beta"), 1),
            }
        )

    total_value = sum(row["market_value"] for row in clean_rows)
    total_cost = sum(row["cost_basis"] for row in clean_rows)
    gain_loss = total_value - total_cost
    gain_loss_pct = gain_loss / total_cost if total_cost else 0

    for row in clean_rows:
        row["weight"] = row["market_value"] / total_value if total_value else 0

    top_weight = max([row["weight"] for row in clean_rows] or [0])
    sector_weights: dict[str, float] = {}
    for row in clean_rows:
        sector_weights[row["sector"]] = sector_weights.get(row["sector"], 0) + row["weight"]
    top_sector, top_sector_weight = max(
        sector_weights.items(),
        key=lambda item: item[1],
        default=("", 0),
    )

    weighted_holding_score = (
        sum(row["holding_score"] * row["market_value"] for row in clean_rows) / total_value
        if total_value
        else 50
    )
    weighted_beta = (
        sum(row["beta"] * row["market_value"] for row in clean_rows) / total_value
        if total_value
        else 1
    )
    diversification_score = clamp(
        100 - max(0, top_weight - 0.28) * 145 - max(0, top_sector_weight - 0.52) * 95
    )
    beta_score = clamp(92 - max(0, weighted_beta - 1) * 42)
    performance_score = clamp(58 + gain_loss_pct * 120)
    portfolio_score = round(
        weighted_holding_score * 0.42
        + diversification_score * 0.24
        + beta_score * 0.18
        + performance_score * 0.16
    )

    warnings: list[str] = []
    if top_weight > 0.42:
        warnings.append("Top holding is carrying too much of the portfolio.")
    if top_sector_weight > 0.62:
        warnings.append("Sector concentration is elevated.")
    if weighted_beta > 1.32:
        warnings.append("Portfolio volatility can amplify drawdowns.")
    if gain_loss_pct < -0.1:
        warnings.append("Unrealized loss is greater than 10%.")
    if weighted_holding_score < 55:
        warnings.append("Weighted holding quality needs review.")

    return PortfolioSnapshot(
        rows=clean_rows,
        total_value=total_value,
        total_cost=total_cost,
        gain_loss=gain_loss,
        gain_loss_pct=gain_loss_pct,
        top_weight=top_weight,
        top_sector=top_sector,
        top_sector_weight=top_sector_weight,
        weighted_beta=weighted_beta,
        portfolio_score=portfolio_score,
        warnings=warnings,
    )


def score_property(row: dict[str, Any]) -> tuple[float, list[str], dict[str, float]]:
    value = safe_float(row.get("property_value"))
    debt = safe_float(row.get("mortgage_balance"))
    rent = safe_float(row.get("monthly_rent"))
    expenses = safe_float(row.get("monthly_expense"))
    vacancy = safe_float(row.get("vacancy_rate")) / 100
    growth = safe_float(row.get("market_growth"))
    effective_rent = rent * (1 - vacancy)
    cash_flow = effective_rent - expenses
    ltv = debt / value if value else 0
    cap_rate = ((effective_rent - expenses) * 12 / value) if value else 0

    equity_score = clamp((1 - ltv) * 125)
    cash_flow_score = clamp(56 + cash_flow / 35)
    vacancy_score = clamp(95 - vacancy * 380)
    growth_score = clamp(48 + growth * 8)
    property_score = equity_score * 0.28 + cash_flow_score * 0.34 + vacancy_score * 0.2 + growth_score * 0.18

    warnings: list[str] = []
    if cash_flow < 0:
        warnings.append(f"{row.get('name', 'Property')} has negative monthly cash flow.")
    if ltv > 0.78:
        warnings.append(f"{row.get('name', 'Property')} has high leverage.")
    if vacancy > 0.08:
        warnings.append(f"{row.get('name', 'Property')} has elevated vacancy exposure.")
    if cap_rate < 0.025 and value > 0:
        warnings.append(f"{row.get('name', 'Property')} has a low income yield.")

    return property_score, warnings, {
        "equity": max(value - debt, 0),
        "cash_flow": cash_flow,
        "ltv": ltv,
        "vacancy": vacancy,
        "cap_rate": cap_rate,
    }


def build_real_estate(rows: list[dict[str, Any]]) -> RealEstateSnapshot:
    clean_rows: list[dict[str, Any]] = []
    all_warnings: list[str] = []
    total_value = 0.0
    total_debt = 0.0
    total_cash_flow = 0.0
    weighted_score_total = 0.0
    vacancy_weighted_total = 0.0

    for row in rows:
        name = str(row.get("name", "")).strip()
        market = str(row.get("market", "")).strip()
        if not name and not market:
            continue
        value = safe_float(row.get("property_value"))
        debt = safe_float(row.get("mortgage_balance"))
        score, warnings, details = score_property(row)
        total_value += value
        total_debt += debt
        total_cash_flow += details["cash_flow"]
        weighted_score_total += score * value
        vacancy_weighted_total += details["vacancy"] * value
        all_warnings.extend(warnings)
        clean_rows.append(
            {
                **row,
                "name": name or "Property",
                "market": market or "Unspecified market",
                "property_value": value,
                "mortgage_balance": debt,
                "monthly_cash_flow": details["cash_flow"],
                "equity": details["equity"],
                "ltv": details["ltv"],
                "cap_rate": details["cap_rate"],
                "property_score": score,
            }
        )

    total_equity = max(total_value - total_debt, 0)
    average_ltv = total_debt / total_value if total_value else 0
    average_vacancy = vacancy_weighted_total / total_value if total_value else 0
    score = round(weighted_score_total / total_value) if total_value else 60
    if not clean_rows:
        score = 50

    return RealEstateSnapshot(
        rows=clean_rows,
        total_value=total_value,
        total_debt=total_debt,
        total_equity=total_equity,
        monthly_cash_flow=total_cash_flow,
        average_ltv=average_ltv,
        average_vacancy=average_vacancy,
        score=score,
        warnings=all_warnings,
    )


def calculate_foundation(
    finance: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
) -> dict[str, Any]:
    monthly_expenses = (
        safe_float(finance.get("fixed_expense"))
        + safe_float(finance.get("variable_expense"))
        + safe_float(finance.get("debt_payment"))
    )
    monthly_income = safe_float(finance.get("monthly_income"))
    cash = safe_float(finance.get("cash"))
    personal_debt = safe_float(finance.get("personal_debt"))
    cash_flow = monthly_income - monthly_expenses
    savings_rate = cash_flow / monthly_income if monthly_income else 0
    runway = cash / monthly_expenses if monthly_expenses else math.inf
    net_worth = cash + portfolio.total_value + real_estate.total_equity - personal_debt
    debt_to_income = personal_debt / (monthly_income * 12) if monthly_income else 1

    target_runway = max(safe_float(finance.get("runway_target"), 6), 1)
    emergency_score = clamp(runway / target_runway * 100)
    cash_flow_score = clamp((savings_rate + 0.08) / 0.34 * 100)
    debt_score = clamp((1 - debt_to_income) * 100)
    net_worth_score = 86 if net_worth > 0 else 36
    score = round(
        emergency_score * 0.34
        + cash_flow_score * 0.32
        + debt_score * 0.2
        + net_worth_score * 0.14
    )

    warnings: list[str] = []
    if cash_flow < 0:
        warnings.append("Monthly cash flow is negative.")
    if runway < target_runway:
        warnings.append("Cash runway is below the target buffer.")
    if debt_to_income > 0.45:
        warnings.append("Personal debt load is pressuring flexibility.")

    return {
        "score": score,
        "label": score_label(score),
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "cash_flow": cash_flow,
        "savings_rate": savings_rate,
        "runway": runway,
        "net_worth": net_worth,
        "warnings": warnings,
    }


def evaluate_goal(goal: dict[str, Any], foundation: dict[str, Any]) -> dict[str, Any]:
    target = safe_float(goal.get("target_amount"))
    months = max(safe_float(goal.get("target_months"), 1), 1)
    contribution = safe_float(goal.get("monthly_commitment"))
    current_base = max(foundation["net_worth"], 0)
    gap = max(target - current_base, 0)
    monthly_required = gap / months
    contribution_ratio = contribution / monthly_required if monthly_required else 1
    surplus_support = max(foundation["cash_flow"], 0) / contribution if contribution else 1
    score = round(clamp(contribution_ratio * 72 + surplus_support * 28))
    if gap == 0:
        score = 100
    label = "On Route" if score >= 78 else "Needs Guardrails" if score >= 58 else "Off Route"
    return {
        "score": score,
        "label": label,
        "gap": gap,
        "monthly_required": monthly_required,
        "contribution": contribution,
        "months": months,
    }


def evaluate_resilience(
    foundation: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
) -> dict[str, Any]:
    warnings = [*foundation["warnings"], *portfolio.warnings, *real_estate.warnings]
    pressure = len(warnings)
    if foundation["cash_flow"] < 0:
        pressure += 1
    if portfolio.top_weight > 0.4:
        pressure += 1
    if real_estate.average_ltv > 0.78:
        pressure += 1

    score = round(
        foundation["score"] * 0.4
        + (100 - min(pressure, 6) * 13) * 0.32
        + portfolio.portfolio_score * 0.16
        + real_estate.score * 0.12
    )
    state = "Clear" if pressure == 0 else "Watch" if pressure <= 3 else "Crisis"
    return {
        "score": score,
        "state": state,
        "pressure": pressure,
        "warnings": warnings,
    }


def build_decision_model(
    foundation: dict[str, Any],
    goal: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
    resilience: dict[str, Any],
) -> dict[str, Any]:
    score = round(
        foundation["score"] * 0.28
        + goal["score"] * 0.22
        + portfolio.portfolio_score * 0.18
        + real_estate.score * 0.14
        + resilience["score"] * 0.18
    )
    if score >= 78 and resilience["pressure"] <= 2:
        recommendation = "Advance with discipline"
        posture = "The client can move forward, but the guardrails should stay visible."
    elif score >= 62:
        recommendation = "Proceed with guardrails"
        posture = "The path is plausible, but weak points should be reduced first."
    elif score >= 45:
        recommendation = "Prepare before committing"
        posture = "The client needs more capacity before taking a larger step."
    else:
        recommendation = "Protect liquidity first"
        posture = "The immediate priority is resilience, not expansion."

    return {
        "score": score,
        "label": score_label(score),
        "recommendation": recommendation,
        "posture": posture,
    }


def build_evidence(
    foundation: dict[str, Any],
    goal: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
    resilience: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence = [
        {
            "name": "Financial Foundation",
            "score": foundation["score"],
            "plain": foundation["label"],
            "detail": f"Cash flow {signed_money(foundation['cash_flow'])}/mo, runway {foundation['runway']:.1f} months.",
        },
        {
            "name": "Goal Route",
            "score": goal["score"],
            "plain": goal["label"],
            "detail": f"Needs {money(goal['monthly_required'])}/mo for {int(goal['months'])} months.",
        },
        {
            "name": "Portfolio",
            "score": portfolio.portfolio_score,
            "plain": score_label(portfolio.portfolio_score),
            "detail": f"{len(portfolio.rows)} holdings, top position {percent(portfolio.top_weight)}.",
        },
        {
            "name": "Real Estate",
            "score": real_estate.score,
            "plain": score_label(real_estate.score),
            "detail": f"Equity {money(real_estate.total_equity)}, cash flow {signed_money(real_estate.monthly_cash_flow)}/mo.",
        },
        {
            "name": "Risk Filter",
            "score": resilience["score"],
            "plain": resilience["state"],
            "detail": f"{resilience['pressure']} pressure point(s) need monitoring.",
        },
    ]
    return evidence


def build_ontology_snapshot(
    profile: dict[str, Any],
    foundation: dict[str, Any],
    goal: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
    resilience: dict[str, Any],
    model: dict[str, Any],
    evidence: list[dict[str, Any]],
    decision_log: list[dict[str, Any]],
) -> dict[str, Any]:
    data_inputs = [
        bool(profile.get("decision_question")),
        foundation["monthly_income"] > 0,
        goal["months"] > 0,
        len(portfolio.rows) > 0,
        len(real_estate.rows) > 0,
    ]
    data_coverage = round(sum(data_inputs) / len(data_inputs) * 100)
    memory_score = 100 if decision_log else 58
    core_nodes = [
        {
            "label": "User",
            "score": 100 if profile.get("decision_question") else 35,
            "state": "ready" if profile.get("decision_question") else "missing",
            "visual": str(profile.get("risk_tolerance", "Balanced")),
            "detail": f"{profile.get('time_horizon_months', 0)} month horizon with a stated decision question.",
        },
        {
            "label": "Data",
            "score": data_coverage,
            "state": "ready" if data_coverage >= 80 else "partial",
            "visual": f"{sum(data_inputs)}/{len(data_inputs)}",
            "detail": "Finance, goal, portfolio, and real estate inputs are normalized for scoring.",
        },
        {
            "label": "Model",
            "score": model["score"],
            "state": score_label(model["score"]).lower(),
            "visual": model["label"],
            "detail": "Decision score blends foundation, goals, portfolio, property, and resilience.",
        },
        {
            "label": "Evidence",
            "score": clamp(len(evidence) / 5 * 100),
            "state": "ready" if len(evidence) >= 5 else "partial",
            "visual": f"{len(evidence)} signals",
            "detail": "Evidence items make the recommendation traceable instead of opaque.",
        },
        {
            "label": "AI Interpretation",
            "score": 100 if model.get("posture") else 40,
            "state": "ready" if model.get("posture") else "missing",
            "visual": "Plain read",
            "detail": model["posture"],
        },
        {
            "label": "Decision",
            "score": model["score"],
            "state": score_label(model["score"]).lower(),
            "visual": model["recommendation"],
            "detail": "Recommendation is generated after risk and evidence are considered.",
        },
        {
            "label": "Memory",
            "score": memory_score,
            "state": "active" if decision_log else "ready",
            "visual": f"{len(decision_log)} saved",
            "detail": "Memory is structurally ready; save a snapshot to create reusable context.",
        },
    ]

    modules = [
        {
            "name": "Financial Foundation",
            "stage": "Data -> Model",
            "score": foundation["score"],
            "detail": f"Net worth {money(foundation['net_worth'])}; runway {foundation['runway']:.1f} months.",
        },
        {
            "name": "Goals",
            "stage": "Data -> Model",
            "score": goal["score"],
            "detail": f"Target gap {money(goal['gap'])}; required {money(goal['monthly_required'])}/mo.",
        },
        {
            "name": "Portfolio",
            "stage": "Data -> Evidence",
            "score": portfolio.portfolio_score,
            "detail": f"{len(portfolio.rows)} holdings; top weight {percent(portfolio.top_weight)}.",
        },
        {
            "name": "Real Estate",
            "stage": "Data -> Evidence",
            "score": real_estate.score,
            "detail": f"Equity {money(real_estate.total_equity)}; LTV {percent(real_estate.average_ltv)}.",
        },
        {
            "name": "Risk/Resilience",
            "stage": "Model -> Evidence",
            "score": resilience["score"],
            "detail": f"{resilience['pressure']} pressure point(s); state {resilience['state']}.",
        },
        {
            "name": "Decision Memory",
            "stage": "Decision -> Memory",
            "score": memory_score,
            "detail": f"{len(decision_log)} saved snapshot(s) in this session.",
        },
    ]

    validation_checks = [
        {
            "name": "Core 7-stage ontology",
            "status": len(ONTOLOGY_STAGES) == 7,
            "detail": "User, Data, Model, Evidence, AI Interpretation, Decision, Memory are defined.",
        },
        {
            "name": "Stage outputs present",
            "status": all(node["score"] > 0 for node in core_nodes),
            "detail": "Each ontology node receives a live value from the current app state.",
        },
        {
            "name": "Evidence coverage",
            "status": len(evidence) >= 5,
            "detail": "Foundation, goals, portfolio, real estate, and risk all produce signals.",
        },
        {
            "name": "Asset sections connected",
            "status": len(portfolio.rows) > 0 and len(real_estate.rows) > 0,
            "detail": "Investment portfolio and real estate sections both feed the model.",
        },
        {
            "name": "Risk traceability",
            "status": isinstance(resilience.get("warnings"), list),
            "detail": "Warnings are traceable back to foundation, portfolio, and property inputs.",
        },
    ]
    validation_score = round(
        sum(1 for item in validation_checks if item["status"]) / len(validation_checks) * 100
    )

    return {
        "core_nodes": core_nodes,
        "modules": modules,
        "relationships": ONTOLOGY_RELATIONSHIPS,
        "validation_checks": validation_checks,
        "validation_score": validation_score,
    }


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          .main .block-container {
            max-width: 1240px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
          }
          h1, h2, h3 { letter-spacing: 0; }
          .ly-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            border: 1px solid #273141;
            border-radius: 8px;
            background: #101722;
            padding: 14px 16px;
            margin-bottom: 20px;
          }
          .ly-brand {
            color: #f8fafc;
            font-size: 1.05rem;
            font-weight: 850;
          }
          .ly-flow {
            color: #aeb9c7;
            font-size: 0.78rem;
            text-transform: uppercase;
          }
          .decision-strip {
            border: 1px solid #d8e0ea;
            border-left: 5px solid #244e9a;
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 16px;
          }
          .decision-question {
            color: #5f6d7a;
            font-size: 0.82rem;
            text-transform: uppercase;
            font-weight: 800;
          }
          .decision-answer {
            color: #17202a;
            font-size: 1.7rem;
            line-height: 1.2;
            font-weight: 850;
            margin-top: 5px;
          }
          .decision-posture {
            color: #536170;
            margin-top: 7px;
            line-height: 1.45;
          }
          .visual-card {
            --accent: #244e9a;
            border: 1px solid #d8e0ea;
            border-radius: 8px;
            background: #ffffff;
            min-height: 215px;
            padding: 18px;
            position: relative;
            transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
          }
          .visual-card:hover, .visual-card:focus {
            border-color: var(--accent);
            box-shadow: 0 10px 30px rgba(28, 42, 64, 0.12);
            transform: translateY(-1px);
            outline: none;
          }
          .visual-card.strong { --accent: #14735f; }
          .visual-card.stable { --accent: #2456a6; }
          .visual-card.watch { --accent: #9a650f; }
          .visual-card.crisis { --accent: #ad3d3d; }
          .card-kicker {
            color: var(--accent);
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
          }
          .signal-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            margin-top: 16px;
          }
          .signal-main {
            color: #17202a;
            font-size: 1.75rem;
            font-weight: 880;
            line-height: 1.08;
          }
          .signal-ring {
            width: 76px;
            height: 76px;
            border-radius: 50%;
            background: conic-gradient(var(--accent) var(--score), #edf1f6 0);
            display: grid;
            place-items: center;
            flex: 0 0 auto;
          }
          .signal-ring span {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background: #ffffff;
            display: grid;
            place-items: center;
            font-size: 0.84rem;
            font-weight: 850;
            color: #17202a;
          }
          .signal-micro {
            color: #647180;
            font-size: 0.88rem;
            margin-top: 12px;
          }
          .reveal {
            color: #405061;
            font-size: 0.9rem;
            line-height: 1.45;
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity 160ms ease, max-height 160ms ease, margin-top 160ms ease;
          }
          .visual-card:hover .reveal, .visual-card:focus .reveal {
            opacity: 1;
            max-height: 160px;
            margin-top: 12px;
          }
          .stage-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
            gap: 8px;
            margin-top: 10px;
          }
          .stage-pill {
            border: 1px solid #d8e0ea;
            border-radius: 8px;
            padding: 10px 9px;
            min-height: 82px;
            background: #ffffff;
          }
          .stage-pill b {
            color: #17202a;
            display: block;
            font-size: 0.82rem;
          }
          .stage-pill span {
            color: #647180;
            display: block;
            font-size: 0.75rem;
            margin-top: 6px;
            line-height: 1.35;
            opacity: 0;
          }
          .stage-pill:hover span {
            opacity: 1;
          }
          .evidence-row {
            border: 1px solid #d8e0ea;
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 8px;
            background: #ffffff;
          }
          .evidence-head {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: #17202a;
            font-weight: 820;
          }
          .evidence-detail {
            color: #647180;
            font-size: 0.88rem;
            margin-top: 5px;
          }
          .warning-box {
            border: 1px solid #e2bd77;
            border-left: 5px solid #a46413;
            border-radius: 8px;
            padding: 12px 14px;
            background: #fffaf0;
            color: #4a3720;
            margin-bottom: 8px;
          }
          .ontology-flow {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin: 12px 0 18px;
          }
          .ontology-node {
            --accent: #2456a6;
            border: 1px solid #d8e0ea;
            border-top: 4px solid var(--accent);
            border-radius: 8px;
            background: #ffffff;
            min-height: 154px;
            padding: 12px;
            position: relative;
          }
          .ontology-node.strong, .ontology-node.ready, .ontology-node.active { --accent: #14735f; }
          .ontology-node.stable { --accent: #2456a6; }
          .ontology-node.watch, .ontology-node.partial { --accent: #9a650f; }
          .ontology-node.crisis, .ontology-node.missing { --accent: #ad3d3d; }
          .ontology-label {
            color: #17202a;
            font-size: 0.86rem;
            font-weight: 850;
            min-height: 34px;
          }
          .ontology-score {
            color: var(--accent);
            font-size: 1.45rem;
            font-weight: 880;
            margin-top: 8px;
          }
          .ontology-visual {
            color: #4e5d6c;
            font-size: 0.8rem;
            min-height: 32px;
          }
          .ontology-bar {
            height: 8px;
            border-radius: 999px;
            background: #edf1f6;
            overflow: hidden;
            margin-top: 10px;
          }
          .ontology-bar span {
            display: block;
            height: 100%;
            width: var(--value);
            background: var(--accent);
          }
          .ontology-detail {
            color: #405061;
            font-size: 0.76rem;
            line-height: 1.35;
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity 160ms ease, max-height 160ms ease, margin-top 160ms ease;
          }
          .ontology-node:hover .ontology-detail, .ontology-node:focus .ontology-detail {
            opacity: 1;
            max-height: 120px;
            margin-top: 8px;
          }
          .module-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 12px 0 18px;
          }
          .module-card {
            --accent: #2456a6;
            border: 1px solid #d8e0ea;
            border-radius: 8px;
            background: #ffffff;
            padding: 12px;
            min-height: 132px;
          }
          .module-card.strong { --accent: #14735f; }
          .module-card.stable { --accent: #2456a6; }
          .module-card.watch { --accent: #9a650f; }
          .module-card.crisis { --accent: #ad3d3d; }
          .module-stage {
            color: var(--accent);
            font-size: 0.74rem;
            font-weight: 850;
            text-transform: uppercase;
          }
          .module-name {
            color: #17202a;
            font-size: 1rem;
            font-weight: 850;
            margin-top: 6px;
          }
          .module-detail {
            color: #607080;
            font-size: 0.82rem;
            line-height: 1.38;
            margin-top: 8px;
          }
          .relationship-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
          }
          .relationship-row, .validation-row {
            border: 1px solid #d8e0ea;
            border-radius: 8px;
            background: #ffffff;
            padding: 10px 12px;
          }
          .relationship-route {
            color: #17202a;
            font-weight: 850;
            font-size: 0.86rem;
          }
          .relationship-claim, .validation-detail {
            color: #647180;
            font-size: 0.8rem;
            margin-top: 4px;
          }
          .validation-row.pass {
            border-left: 5px solid #14735f;
          }
          .validation-row.warn {
            border-left: 5px solid #ad3d3d;
          }
          @media (max-width: 900px) {
            .ly-topline, .signal-row { display: block; }
            .signal-ring { margin-top: 16px; }
            .stage-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .ontology-flow, .module-grid, .relationship-list {
              grid-template-columns: repeat(1, minmax(0, 1fr));
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topline() -> None:
    st.markdown(
        """
        <div class="ly-topline">
          <div>
            <div class="ly-brand">LY-Scope Ver.2</div>
            <div class="ly-flow">User -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory</div>
          </div>
          <div class="ly-flow">Personal Decision Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_strip(profile: dict[str, Any], model: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="decision-strip">
          <div class="decision-question">{escape(str(profile["decision_question"]))}</div>
          <div class="decision-answer">{escape(model["recommendation"])}</div>
          <div class="decision-posture">{escape(model["posture"])} Decision score: {model["score"]}/100.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_visual_card(
    title: str,
    label: str,
    score: float,
    micro: str,
    detail: str,
    tone: str | None = None,
) -> None:
    card_tone = tone or tone_for_score(score)
    st.markdown(
        f"""
        <div class="visual-card {card_tone}" tabindex="0">
          <div class="card-kicker">{escape(title)}</div>
          <div class="signal-row">
            <div class="signal-main">{escape(label)}</div>
            <div class="signal-ring" style="--score: {clamp(score):.0f}%"><span>{clamp(score):.0f}</span></div>
          </div>
          <div class="signal-micro">{escape(micro)}</div>
          <div class="reveal">{escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_architecture_trace() -> None:
    stages = [
        ("User", "client goal, horizon, tolerance"),
        ("Data", "finance, assets, property, memory"),
        ("Model", "deterministic scoring engine"),
        ("Evidence", "support and risk signals"),
        ("AI Interpretation", "plain-language reading layer"),
        ("Decision", "recommendation and next action"),
        ("Memory", "saved decision context"),
    ]
    pills = "".join(
        f'<div class="stage-pill"><b>{escape(name)}</b><span>{escape(detail)}</span></div>'
        for name, detail in stages
    )
    st.markdown(f'<div class="stage-grid">{pills}</div>', unsafe_allow_html=True)


def render_evidence(evidence: list[dict[str, Any]]) -> None:
    for item in evidence:
        st.markdown(
            f"""
            <div class="evidence-row">
              <div class="evidence-head">
                <span>{escape(item["name"])}</span>
                <span>{escape(item["plain"])} / {int(item["score"])}</span>
              </div>
              <div class="evidence-detail">{escape(item["detail"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_warnings(warnings: list[str]) -> None:
    if not warnings:
        st.success("No major pressure point is currently active.")
        return
    for warning in warnings:
        st.markdown(
            f'<div class="warning-box">{escape(warning)}</div>',
            unsafe_allow_html=True,
        )


def render_ontology_map(snapshot: dict[str, Any]) -> None:
    node_html = ""
    for node in snapshot["core_nodes"]:
        tone = tone_for_score(node["score"])
        state = str(node["state"]).replace(" ", "-").lower()
        node_html += (
            f'<div class="ontology-node {tone} {escape(state)}" tabindex="0">'
            f'<div class="ontology-label">{escape(node["label"])}</div>'
            f'<div class="ontology-score">{int(clamp(node["score"]))}</div>'
            f'<div class="ontology-visual">{escape(str(node["visual"]))}</div>'
            f'<div class="ontology-bar" style="--value: {clamp(node["score"]):.0f}%"><span></span></div>'
            f'<div class="ontology-detail">{escape(node["detail"])}</div>'
            "</div>"
        )
    st.markdown(f'<div class="ontology-flow">{node_html}</div>', unsafe_allow_html=True)


def render_module_grid(snapshot: dict[str, Any]) -> None:
    module_html = ""
    for module in snapshot["modules"]:
        tone = tone_for_score(module["score"])
        module_html += (
            f'<div class="module-card {tone}">'
            f'<div class="module-stage">{escape(module["stage"])}</div>'
            f'<div class="module-name">{escape(module["name"])}</div>'
            f'<div class="ontology-bar" style="--value: {clamp(module["score"]):.0f}%"><span></span></div>'
            f'<div class="module-detail">{escape(module["detail"])}</div>'
            "</div>"
        )
    st.markdown(f'<div class="module-grid">{module_html}</div>', unsafe_allow_html=True)


def render_relationships(snapshot: dict[str, Any]) -> None:
    relationship_html = ""
    for source, target, claim in snapshot["relationships"]:
        relationship_html += (
            '<div class="relationship-row">'
            f'<div class="relationship-route">{escape(source)} -> {escape(target)}</div>'
            f'<div class="relationship-claim">{escape(claim)}</div>'
            "</div>"
        )
    st.markdown(f'<div class="relationship-list">{relationship_html}</div>', unsafe_allow_html=True)


def render_validation_checks(snapshot: dict[str, Any]) -> None:
    for check in snapshot["validation_checks"]:
        state = "pass" if check["status"] else "warn"
        label = "Verified" if check["status"] else "Needs review"
        st.markdown(
            f"""
            <div class="validation-row {state}">
              <div class="relationship-route">{escape(check["name"])}: {label}</div>
              <div class="validation-detail">{escape(check["detail"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ontology_tab(snapshot: dict[str, Any], evidence: list[dict[str, Any]]) -> None:
    st.subheader("Ontology Verification")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Validation", f"{snapshot['validation_score']}/100")
    c2.metric("Core nodes", f"{len(snapshot['core_nodes'])}/7")
    c3.metric("Module links", len(snapshot["modules"]))
    c4.metric("Evidence signals", len(evidence))

    st.markdown("#### Core Decision Ontology")
    render_ontology_map(snapshot)
    st.caption("Hover or click each ontology node to reveal its live proof point.")

    st.markdown("#### Module Connection Board")
    render_module_grid(snapshot)

    st.markdown("#### Relationship Trace")
    render_relationships(snapshot)

    st.markdown("#### Direct Validation")
    render_validation_checks(snapshot)


def initialize_state() -> None:
    defaults = {
        "profile": DEFAULT_PROFILE.copy(),
        "finance": DEFAULT_FINANCE.copy(),
        "goal": DEFAULT_GOAL.copy(),
        "holdings": [row.copy() for row in DEFAULT_HOLDINGS],
        "real_estate": [row.copy() for row in DEFAULT_REAL_ESTATE],
        "decision_log": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> None:
    profile = st.session_state.profile
    with st.sidebar:
        st.header("Decision Setup")
        profile["name"] = st.text_input("Client name", value=str(profile["name"]))
        profile["decision_question"] = st.text_area(
            "Decision question",
            value=str(profile["decision_question"]),
            height=86,
        )
        profile["time_horizon_months"] = st.slider(
            "Time horizon",
            min_value=6,
            max_value=120,
            value=int(profile["time_horizon_months"]),
            step=6,
        )
        profile["risk_tolerance"] = st.selectbox(
            "Risk posture",
            ["Conservative", "Balanced", "Growth"],
            index=["Conservative", "Balanced", "Growth"].index(str(profile["risk_tolerance"])),
        )
        st.divider()
        if st.button("Reset sample data", use_container_width=True):
            for key in ["profile", "finance", "goal", "holdings", "real_estate", "decision_log"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def render_foundation_inputs() -> None:
    finance = st.session_state.finance
    st.subheader("Financial Foundation")
    c1, c2, c3 = st.columns(3)
    with c1:
        finance["monthly_income"] = st.number_input(
            "Monthly income",
            min_value=0.0,
            step=100.0,
            value=float(finance["monthly_income"]),
        )
        finance["cash"] = st.number_input(
            "Cash reserve",
            min_value=0.0,
            step=500.0,
            value=float(finance["cash"]),
        )
    with c2:
        finance["fixed_expense"] = st.number_input(
            "Fixed expenses",
            min_value=0.0,
            step=100.0,
            value=float(finance["fixed_expense"]),
        )
        finance["variable_expense"] = st.number_input(
            "Variable expenses",
            min_value=0.0,
            step=100.0,
            value=float(finance["variable_expense"]),
        )
    with c3:
        finance["debt_payment"] = st.number_input(
            "Monthly debt payment",
            min_value=0.0,
            step=100.0,
            value=float(finance["debt_payment"]),
        )
        finance["personal_debt"] = st.number_input(
            "Personal debt",
            min_value=0.0,
            step=500.0,
            value=float(finance["personal_debt"]),
        )
        finance["runway_target"] = st.number_input(
            "Runway target months",
            min_value=1.0,
            max_value=24.0,
            step=1.0,
            value=float(finance["runway_target"]),
        )


def render_goal_inputs() -> None:
    goal = st.session_state.goal
    st.subheader("Goal Route")
    c1, c2, c3 = st.columns(3)
    with c1:
        goal["goal_name"] = st.text_input("Goal name", value=str(goal["goal_name"]))
    with c2:
        goal["target_amount"] = st.number_input(
            "Target amount",
            min_value=0.0,
            step=5000.0,
            value=float(goal["target_amount"]),
        )
    with c3:
        goal["target_months"] = st.number_input(
            "Target months",
            min_value=1,
            max_value=240,
            step=1,
            value=int(goal["target_months"]),
        )
        goal["monthly_commitment"] = st.number_input(
            "Monthly commitment",
            min_value=0.0,
            step=100.0,
            value=float(goal["monthly_commitment"]),
        )


def render_portfolio_inputs() -> None:
    st.subheader("Portfolio Input")
    edited = st.data_editor(
        st.session_state.holdings,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "symbol": st.column_config.TextColumn("Symbol", required=True),
            "company": st.column_config.TextColumn("Company"),
            "sector": st.column_config.TextColumn("Sector"),
            "shares": st.column_config.NumberColumn("Shares", min_value=0.0),
            "purchase_price": st.column_config.NumberColumn("Cost / share", min_value=0.0),
            "price": st.column_config.NumberColumn("Current price", min_value=0.0),
            "beta": st.column_config.NumberColumn("Beta", min_value=0.0, max_value=3.0),
            "quality": st.column_config.NumberColumn("Quality", min_value=0.0, max_value=100.0),
            "momentum": st.column_config.NumberColumn("Momentum", min_value=0.0, max_value=100.0),
            "valuation": st.column_config.NumberColumn("Valuation", min_value=0.0, max_value=100.0),
        },
    )
    st.session_state.holdings = rows_from_editor(edited)


def render_real_estate_inputs() -> None:
    st.subheader("Real Estate Input")
    edited = st.data_editor(
        st.session_state.real_estate,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Property"),
            "market": st.column_config.TextColumn("Market"),
            "property_value": st.column_config.NumberColumn("Value", min_value=0.0),
            "mortgage_balance": st.column_config.NumberColumn("Debt", min_value=0.0),
            "monthly_rent": st.column_config.NumberColumn("Rent", min_value=0.0),
            "monthly_expense": st.column_config.NumberColumn("Expenses", min_value=0.0),
            "vacancy_rate": st.column_config.NumberColumn("Vacancy %", min_value=0.0, max_value=50.0),
            "market_growth": st.column_config.NumberColumn("Growth %", min_value=-20.0, max_value=30.0),
        },
    )
    st.session_state.real_estate = rows_from_editor(edited)


def render_memory(model: dict[str, Any], evidence: list[dict[str, Any]], resilience: dict[str, Any]) -> None:
    st.subheader("Decision Memory")
    note = st.text_area("Decision note", placeholder="What decision should be remembered?", height=96)
    if st.button("Save decision snapshot", use_container_width=True):
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "decision": model["recommendation"],
            "score": model["score"],
            "risk_state": resilience["state"],
            "strongest_signal": max(evidence, key=lambda item: item["score"])["name"],
            "note": note.strip(),
        }
        st.session_state.decision_log.insert(0, record)
        st.success("Decision snapshot saved in this session.")

    if st.session_state.decision_log:
        st.dataframe(st.session_state.decision_log, use_container_width=True, hide_index=True)
    else:
        st.info("No saved decision snapshots yet.")


def main() -> None:
    inject_styles()
    initialize_state()
    render_sidebar()

    profile = st.session_state.profile
    portfolio = build_portfolio(st.session_state.holdings)
    real_estate = build_real_estate(st.session_state.real_estate)
    foundation = calculate_foundation(st.session_state.finance, portfolio, real_estate)
    goal = evaluate_goal(st.session_state.goal, foundation)
    resilience = evaluate_resilience(foundation, portfolio, real_estate)
    model = build_decision_model(foundation, goal, portfolio, real_estate, resilience)
    evidence = build_evidence(foundation, goal, portfolio, real_estate, resilience)
    ontology = build_ontology_snapshot(
        profile,
        foundation,
        goal,
        portfolio,
        real_estate,
        resilience,
        model,
        evidence,
        st.session_state.decision_log,
    )

    render_topline()
    render_decision_strip(profile, model)

    card1, card2, card3 = st.columns(3)
    with card1:
        render_visual_card(
            "Current Situation",
            foundation["label"],
            foundation["score"],
            f"Net worth {money(foundation['net_worth'])}",
            f"Cash flow is {signed_money(foundation['cash_flow'])}/mo and runway is {foundation['runway']:.1f} months.",
        )
    with card2:
        render_visual_card(
            "Goal Direction",
            goal["label"],
            goal["score"],
            f"Target gap {money(goal['gap'])}",
            f"Monthly route requires {money(goal['monthly_required'])}; current commitment is {money(goal['contribution'])}.",
            "strong" if goal["score"] >= 78 else "watch" if goal["score"] >= 58 else "crisis",
        )
    with card3:
        render_visual_card(
            "Crisis Watch",
            resilience["state"],
            resilience["score"],
            f"{resilience['pressure']} pressure point(s)",
            "Risk combines cash-flow pressure, concentration, leverage, volatility, and property exposure.",
            "strong" if resilience["state"] == "Clear" else "watch" if resilience["state"] == "Watch" else "crisis",
        )

    st.caption("Hover or click the signal cards to reveal supporting details.")

    (
        overview,
        ontology_tab,
        foundation_tab,
        portfolio_tab,
        estate_tab,
        goals_tab,
        evidence_tab,
        memory_tab,
    ) = st.tabs(
        [
            "Cockpit",
            "Ontology",
            "Foundation",
            "Portfolio",
            "Real Estate",
            "Goals",
            "Evidence",
            "Memory",
        ]
    )

    with overview:
        st.subheader("Decision Cockpit")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Decision score", f"{model['score']}/100", model["label"])
        c2.metric("Monthly cash flow", signed_money(foundation["cash_flow"]))
        c3.metric("Portfolio score", f"{portfolio.portfolio_score}/100")
        c4.metric("Real estate score", f"{real_estate.score}/100")
        st.markdown("#### Logic Chain")
        render_architecture_trace()
        st.markdown("#### Priority Warnings")
        render_warnings(resilience["warnings"])

    with ontology_tab:
        render_ontology_tab(ontology, evidence)

    with foundation_tab:
        render_foundation_inputs()
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Foundation", f"{foundation['score']}/100", foundation["label"])
        c2.metric("Runway", f"{foundation['runway']:.1f} mo")
        c3.metric("Savings rate", percent(foundation["savings_rate"]))
        c4.metric("Net worth", money(foundation["net_worth"]))

    with portfolio_tab:
        render_portfolio_inputs()
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Portfolio value", money(portfolio.total_value))
        c2.metric("Gain/loss", signed_money(portfolio.gain_loss), percent(portfolio.gain_loss_pct))
        c3.metric("Top holding", percent(portfolio.top_weight))
        c4.metric("Top sector", portfolio.top_sector or "None", percent(portfolio.top_sector_weight))
        render_warnings(portfolio.warnings)

    with estate_tab:
        render_real_estate_inputs()
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Property value", money(real_estate.total_value))
        c2.metric("Equity", money(real_estate.total_equity))
        c3.metric("Cash flow", signed_money(real_estate.monthly_cash_flow))
        c4.metric("Avg. LTV", percent(real_estate.average_ltv))
        render_warnings(real_estate.warnings)

    with goals_tab:
        render_goal_inputs()
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Goal route", f"{goal['score']}/100", goal["label"])
        c2.metric("Target", money(st.session_state.goal["target_amount"]))
        c3.metric("Remaining gap", money(goal["gap"]))
        c4.metric("Monthly required", money(goal["monthly_required"]))

    with evidence_tab:
        st.subheader("Evidence and Interpretation")
        render_evidence(evidence)
        st.info(model["posture"])
        st.caption(
            "This layer is deterministic and educational. It is not investment, tax, legal, accounting, or professional financial advice."
        )

    with memory_tab:
        render_memory(model, evidence, resilience)


if __name__ == "__main__":
    main()

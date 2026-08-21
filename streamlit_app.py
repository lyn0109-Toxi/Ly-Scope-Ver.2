from __future__ import annotations

import math
from copy import deepcopy
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
    "retirement_accounts": 52000.0,
    "monthly_savings_goal": 1600.0,
    "target_goal_amount": 250000.0,
    "current_goal_savings": 76000.0,
    "investment_risk_score": 45.0,
}

DEFAULT_GOAL = {
    "goal_name": "Build decision-ready net worth",
    "target_amount": 250000.0,
    "target_months": 36,
    "monthly_commitment": 1600.0,
}

DEFAULT_SCENARIO = {
    "income_shock_pct": -10.0,
    "market_asset_shock_pct": -15.0,
    "real_estate_shock_pct": -8.0,
}

STOCK_UNIVERSE = [
    {
        "symbol": "AAPL",
        "company": "Apple",
        "sector": "Technology",
        "price": 189.9,
        "pe": 28.4,
        "dividend_yield": 0.5,
        "beta": 1.2,
        "momentum_6m": 9.5,
        "revenue_growth": 4.1,
        "margin_quality": 86.0,
        "debt_risk": 34.0,
        "thesis": "High-quality cash generation with valuation discipline needed.",
    },
    {
        "symbol": "MSFT",
        "company": "Microsoft",
        "sector": "Technology",
        "price": 426.7,
        "pe": 32.2,
        "dividend_yield": 0.7,
        "beta": 0.9,
        "momentum_6m": 13.1,
        "revenue_growth": 12.0,
        "margin_quality": 90.0,
        "debt_risk": 24.0,
        "thesis": "Durable enterprise platform with AI and cloud optionality.",
    },
    {
        "symbol": "NVDA",
        "company": "NVIDIA",
        "sector": "Semiconductors",
        "price": 109.6,
        "pe": 45.5,
        "dividend_yield": 0.0,
        "beta": 1.7,
        "momentum_6m": 31.8,
        "revenue_growth": 29.0,
        "margin_quality": 93.0,
        "debt_risk": 28.0,
        "thesis": "Exceptional growth profile, but scenario risk is valuation-driven.",
    },
    {
        "symbol": "JPM",
        "company": "JPMorgan Chase",
        "sector": "Financials",
        "price": 208.4,
        "pe": 12.6,
        "dividend_yield": 2.1,
        "beta": 1.1,
        "momentum_6m": 6.8,
        "revenue_growth": 5.4,
        "margin_quality": 72.0,
        "debt_risk": 42.0,
        "thesis": "Scale advantage, rate-cycle sensitivity, and credit risk should be watched together.",
    },
    {
        "symbol": "LLY",
        "company": "Eli Lilly",
        "sector": "Healthcare",
        "price": 772.3,
        "pe": 39.8,
        "dividend_yield": 0.7,
        "beta": 0.4,
        "momentum_6m": 18.4,
        "revenue_growth": 20.0,
        "margin_quality": 84.0,
        "debt_risk": 30.0,
        "thesis": "Strong product-cycle story with high expectations embedded.",
    },
    {
        "symbol": "XOM",
        "company": "Exxon Mobil",
        "sector": "Energy",
        "price": 116.1,
        "pe": 14.1,
        "dividend_yield": 3.3,
        "beta": 0.9,
        "momentum_6m": 4.6,
        "revenue_growth": 1.8,
        "margin_quality": 69.0,
        "debt_risk": 32.0,
        "thesis": "Income and commodity-cycle exposure with balance-sheet strength.",
    },
]

REIT_UNIVERSE = [
    {
        "symbol": "PLD",
        "company": "Prologis",
        "sector": "Industrial",
        "region": "Global logistics",
        "price": 111.4,
        "dividend_yield": 3.55,
        "price_to_ffo": 19.8,
        "affo_payout": 72.0,
        "nav_discount": -3.2,
        "debt_to_ebitda": 5.1,
        "occupancy": 97.2,
        "rent_growth": 4.6,
        "ffo_growth": 5.8,
        "price_momentum": 4.2,
        "demand_score": 82.0,
        "supply_pressure": 48.0,
        "liquidity_score": 84.0,
        "insurance_disaster_risk": 44.0,
        "rate_risk": 58.0,
        "property_note": "Logistics demand remains strong, but valuation is not deeply discounted.",
    },
    {
        "symbol": "O",
        "company": "Realty Income",
        "sector": "Retail Net Lease",
        "region": "US and Europe",
        "price": 56.2,
        "dividend_yield": 5.65,
        "price_to_ffo": 13.4,
        "affo_payout": 76.0,
        "nav_discount": -8.5,
        "debt_to_ebitda": 5.5,
        "occupancy": 98.6,
        "rent_growth": 2.7,
        "ffo_growth": 3.2,
        "price_momentum": 2.4,
        "demand_score": 72.0,
        "supply_pressure": 35.0,
        "liquidity_score": 78.0,
        "insurance_disaster_risk": 36.0,
        "rate_risk": 66.0,
        "property_note": "Stable lease income profile; rate sensitivity is the key watch item.",
    },
    {
        "symbol": "EQIX",
        "company": "Equinix",
        "sector": "Data Center",
        "region": "Global interconnection",
        "price": 792.5,
        "dividend_yield": 2.15,
        "price_to_ffo": 24.6,
        "affo_payout": 64.0,
        "nav_discount": 5.4,
        "debt_to_ebitda": 4.2,
        "occupancy": 96.1,
        "rent_growth": 5.5,
        "ffo_growth": 7.4,
        "price_momentum": 11.8,
        "demand_score": 88.0,
        "supply_pressure": 58.0,
        "liquidity_score": 82.0,
        "insurance_disaster_risk": 32.0,
        "rate_risk": 46.0,
        "property_note": "Premium growth REIT; upside depends on sustained data-center demand.",
    },
    {
        "symbol": "AVB",
        "company": "AvalonBay Communities",
        "sector": "Residential",
        "region": "Coastal apartments",
        "price": 197.8,
        "dividend_yield": 3.4,
        "price_to_ffo": 17.1,
        "affo_payout": 68.0,
        "nav_discount": -2.1,
        "debt_to_ebitda": 4.8,
        "occupancy": 95.8,
        "rent_growth": 3.8,
        "ffo_growth": 4.1,
        "price_momentum": 5.1,
        "demand_score": 76.0,
        "supply_pressure": 62.0,
        "liquidity_score": 74.0,
        "insurance_disaster_risk": 50.0,
        "rate_risk": 52.0,
        "property_note": "Good household-demand exposure; supply and insurance pressure need monitoring.",
    },
    {
        "symbol": "BXP",
        "company": "BXP",
        "sector": "Office",
        "region": "Gateway office",
        "price": 66.4,
        "dividend_yield": 5.9,
        "price_to_ffo": 9.2,
        "affo_payout": 82.0,
        "nav_discount": -18.0,
        "debt_to_ebitda": 7.1,
        "occupancy": 88.6,
        "rent_growth": 0.8,
        "ffo_growth": -1.4,
        "price_momentum": -8.5,
        "demand_score": 41.0,
        "supply_pressure": 78.0,
        "liquidity_score": 44.0,
        "insurance_disaster_risk": 38.0,
        "rate_risk": 82.0,
        "property_note": "Deep discount can be tempting, but office demand and refinancing risk dominate.",
    },
]

REAL_ESTATE_MARKETS = [
    {
        "market_id": "AUS-78704",
        "city": "Austin",
        "county": "Travis County",
        "state": "TX",
        "zip_code": "78704",
        "market_type": "Growth / tech migration",
        "median_price": 742000.0,
        "price_momentum_12m": -2.8,
        "pir": 7.9,
        "affordability_index": 61.0,
        "inventory_months": 5.8,
        "active_inventory_yoy": 34.0,
        "rent_estimate": 3150.0,
        "gross_rent_yield": 5.1,
        "permits_per_1k": 8.2,
        "employment_growth": 1.9,
        "unemployment_rate": 3.5,
        "migration_score": 68.0,
        "disaster_risk": 46.0,
        "insurance_pressure": 55.0,
        "transaction_volume_yoy": -18.0,
        "market_note": "Demand is still supported by jobs, but affordability and new supply require caution.",
    },
    {
        "market_id": "TPA-33602",
        "city": "Tampa",
        "county": "Hillsborough County",
        "state": "FL",
        "zip_code": "33602",
        "market_type": "Coastal income / insurance watch",
        "median_price": 462000.0,
        "price_momentum_12m": -1.5,
        "pir": 6.4,
        "affordability_index": 66.0,
        "inventory_months": 6.4,
        "active_inventory_yoy": 48.0,
        "rent_estimate": 2550.0,
        "gross_rent_yield": 6.6,
        "permits_per_1k": 6.4,
        "employment_growth": 1.7,
        "unemployment_rate": 3.4,
        "migration_score": 76.0,
        "disaster_risk": 76.0,
        "insurance_pressure": 84.0,
        "transaction_volume_yoy": -22.0,
        "market_note": "Rental yield is attractive, but insurance, storm risk, and inventory growth are key checks.",
    },
    {
        "market_id": "CLT-28202",
        "city": "Charlotte",
        "county": "Mecklenburg County",
        "state": "NC",
        "zip_code": "28202",
        "market_type": "Banking / migration growth",
        "median_price": 421000.0,
        "price_momentum_12m": 3.4,
        "pir": 4.9,
        "affordability_index": 86.0,
        "inventory_months": 3.5,
        "active_inventory_yoy": 15.0,
        "rent_estimate": 2290.0,
        "gross_rent_yield": 6.5,
        "permits_per_1k": 4.8,
        "employment_growth": 2.4,
        "unemployment_rate": 3.3,
        "migration_score": 81.0,
        "disaster_risk": 38.0,
        "insurance_pressure": 35.0,
        "transaction_volume_yoy": 4.0,
        "market_note": "Strong demand, decent affordability, and manageable risk make this a high-quality MVP sample.",
    },
    {
        "market_id": "CMH-43215",
        "city": "Columbus",
        "county": "Franklin County",
        "state": "OH",
        "zip_code": "43215",
        "market_type": "Midwest affordability / jobs",
        "median_price": 336000.0,
        "price_momentum_12m": 4.1,
        "pir": 4.1,
        "affordability_index": 101.0,
        "inventory_months": 2.9,
        "active_inventory_yoy": 8.0,
        "rent_estimate": 2010.0,
        "gross_rent_yield": 7.2,
        "permits_per_1k": 3.3,
        "employment_growth": 1.6,
        "unemployment_rate": 3.6,
        "migration_score": 64.0,
        "disaster_risk": 30.0,
        "insurance_pressure": 28.0,
        "transaction_volume_yoy": 6.0,
        "market_note": "Affordability and rent yield are strong, with lower disaster and insurance pressure.",
    },
    {
        "market_id": "ATL-30309",
        "city": "Atlanta",
        "county": "Fulton County",
        "state": "GA",
        "zip_code": "30309",
        "market_type": "Large metro / diversified jobs",
        "median_price": 448000.0,
        "price_momentum_12m": 2.2,
        "pir": 5.2,
        "affordability_index": 82.0,
        "inventory_months": 4.1,
        "active_inventory_yoy": 18.0,
        "rent_estimate": 2390.0,
        "gross_rent_yield": 6.4,
        "permits_per_1k": 4.9,
        "employment_growth": 1.8,
        "unemployment_rate": 3.4,
        "migration_score": 72.0,
        "disaster_risk": 42.0,
        "insurance_pressure": 40.0,
        "transaction_volume_yoy": -3.0,
        "market_note": "Diversified demand and reasonable yield, with moderate supply and insurance pressure.",
    },
]

DEFAULT_OBJECTIVES = [
    {
        "name": "Home Down Payment",
        "objective_type": "Home Purchase",
        "target_amount": 80000.0,
        "target_years": 5.0,
        "current_amount": 30000.0,
        "monthly_contribution": 1200.0,
        "account_type": "Taxable Brokerage",
        "expected_return_pct": 6.0,
        "tax_fee_drag_pct": 1.0,
        "priority": "High",
    },
    {
        "name": "Emergency Fund",
        "objective_type": "Emergency Reserve",
        "target_amount": 27600.0,
        "target_years": 1.0,
        "current_amount": 24000.0,
        "monthly_contribution": 400.0,
        "account_type": "Cash / Savings",
        "expected_return_pct": 2.5,
        "tax_fee_drag_pct": 0.5,
        "priority": "High",
    },
    {
        "name": "Retirement Readiness",
        "objective_type": "Retirement",
        "target_amount": 1200000.0,
        "target_years": 25.0,
        "current_amount": 52000.0,
        "monthly_contribution": 800.0,
        "account_type": "Retirement Account",
        "expected_return_pct": 6.5,
        "tax_fee_drag_pct": 0.4,
        "priority": "Medium",
    },
]

DEFAULT_HOLDINGS = [
    {
        "symbol": "MSFT",
        "company": "Microsoft",
        "sector": "Technology",
        "shares": 60.0,
        "purchase_price": 390.0,
        "price": 426.7,
        "beta": 0.9,
        "pe": 32.2,
        "dividend_yield": 0.7,
        "momentum_6m": 13.1,
        "revenue_growth": 12.0,
        "margin_quality": 90.0,
        "debt_risk": 24.0,
    },
    {
        "symbol": "AAPL",
        "company": "Apple",
        "sector": "Technology",
        "shares": 70.0,
        "purchase_price": 175.0,
        "price": 189.9,
        "beta": 1.2,
        "pe": 28.4,
        "dividend_yield": 0.5,
        "momentum_6m": 9.5,
        "revenue_growth": 4.1,
        "margin_quality": 86.0,
        "debt_risk": 34.0,
    },
    {
        "symbol": "NVDA",
        "company": "NVIDIA",
        "sector": "Semiconductors",
        "shares": 80.0,
        "purchase_price": 92.0,
        "price": 109.6,
        "beta": 1.7,
        "pe": 45.5,
        "dividend_yield": 0.0,
        "momentum_6m": 31.8,
        "revenue_growth": 29.0,
        "margin_quality": 93.0,
        "debt_risk": 28.0,
    },
    {
        "symbol": "JPM",
        "company": "JPMorgan Chase",
        "sector": "Financials",
        "shares": 22.0,
        "purchase_price": 188.0,
        "price": 208.4,
        "beta": 1.1,
        "pe": 12.6,
        "dividend_yield": 2.1,
        "momentum_6m": 6.8,
        "revenue_growth": 5.4,
        "margin_quality": 72.0,
        "debt_risk": 42.0,
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
    weighted_score: float
    concentration_score: float
    beta_score: float
    performance_score: float
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
    market: dict[str, Any] | None
    market_forecast: list[dict[str, Any]]
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


def pct_value(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}%"


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def stock_by_symbol(symbol: str) -> dict[str, Any] | None:
    clean = str(symbol or "").strip().upper()
    return next((row for row in STOCK_UNIVERSE if row["symbol"] == clean), None)


def reit_by_symbol(symbol: str) -> dict[str, Any] | None:
    clean = str(symbol or "").strip().upper()
    return next((row for row in REIT_UNIVERSE if row["symbol"] == clean), None)


def market_by_id(market_id: str) -> dict[str, Any] | None:
    clean = str(market_id or "").strip()
    return next((row for row in REAL_ESTATE_MARKETS if row["market_id"] == clean), None)


def merge_stock_reference(row: dict[str, Any]) -> dict[str, Any]:
    reference = stock_by_symbol(str(row.get("symbol", ""))) or {}
    return {**reference, **row}


def enrich_stock(row: dict[str, Any]) -> dict[str, Any]:
    record = merge_stock_reference(row)
    pe = safe_float(record.get("pe"), 18.0)
    dividend_yield = safe_float(record.get("dividend_yield"))
    momentum_6m = safe_float(record.get("momentum_6m"))
    margin_quality = safe_float(record.get("margin_quality"), safe_float(record.get("quality"), 60.0))
    revenue_growth = safe_float(record.get("revenue_growth"))
    debt_risk = safe_float(record.get("debt_risk"), 35.0)
    beta = safe_float(record.get("beta"), 1.0)
    value_score = clamp(95 - max(0.0, pe - 10.0) * 2.0 + dividend_yield * 2.5)
    momentum_score = clamp(48 + momentum_6m * 2.1)
    quality_score = clamp(margin_quality * 0.72 + revenue_growth * 1.2 - debt_risk * 0.18)
    risk_balance_score = clamp(92 - abs(beta - 1.0) * 28 - debt_risk * 0.22)
    life_stock_score = (
        value_score * 0.25
        + momentum_score * 0.25
        + quality_score * 0.30
        + risk_balance_score * 0.20
    )
    return {
        **record,
        "symbol": str(record.get("symbol", "")).strip().upper(),
        "company": str(record.get("company") or record.get("symbol") or "").strip(),
        "sector": str(record.get("sector") or "Unclassified"),
        "price": safe_float(record.get("price")),
        "pe": pe,
        "dividend_yield": dividend_yield,
        "beta": beta,
        "momentum_6m": momentum_6m,
        "revenue_growth": revenue_growth,
        "margin_quality": margin_quality,
        "debt_risk": debt_risk,
        "value_score": value_score,
        "momentum_score": momentum_score,
        "quality_score": quality_score,
        "risk_balance_score": risk_balance_score,
        "life_stock_score": life_stock_score,
    }


def stock_warnings(row: dict[str, Any]) -> list[str]:
    item = enrich_stock(row)
    warnings: list[str] = []
    if item["pe"] >= 35:
        warnings.append("Valuation expectations are high.")
    if item["beta"] >= 1.45:
        warnings.append("High beta can amplify drawdowns.")
    if item["momentum_6m"] < 0:
        warnings.append("Price momentum is negative.")
    if item["debt_risk"] >= 55:
        warnings.append("Debt risk needs review.")
    return warnings


def stock_score_basis(row: dict[str, Any]) -> list[dict[str, Any]]:
    item = enrich_stock(row)
    return [
        {"Pillar": "Valuation", "Score": item["value_score"], "Weight": "25%", "Signal": f"P/E {item['pe']:.1f}x, yield {pct_value(item['dividend_yield'], 2)}"},
        {"Pillar": "Momentum", "Score": item["momentum_score"], "Weight": "25%", "Signal": f"6M price change {pct_value(item['momentum_6m'])}"},
        {"Pillar": "Quality", "Score": item["quality_score"], "Weight": "30%", "Signal": f"margin {item['margin_quality']:.0f}/100, growth {pct_value(item['revenue_growth'])}"},
        {"Pillar": "Risk Balance", "Score": item["risk_balance_score"], "Weight": "20%", "Signal": f"beta {item['beta']:.2f}, debt risk {item['debt_risk']:.0f}/100"},
    ]


def enrich_reit(row: dict[str, Any]) -> dict[str, Any]:
    nav_discount = safe_float(row.get("nav_discount"))
    price_to_ffo = safe_float(row.get("price_to_ffo"))
    dividend_yield = safe_float(row.get("dividend_yield"))
    affo_payout = safe_float(row.get("affo_payout"))
    occupancy = safe_float(row.get("occupancy"))
    debt_to_ebitda = safe_float(row.get("debt_to_ebitda"))
    rent_growth = safe_float(row.get("rent_growth"))
    demand_score = safe_float(row.get("demand_score"))
    rate_risk = safe_float(row.get("rate_risk"))
    supply_pressure = safe_float(row.get("supply_pressure"))
    valuation_score = clamp(
        56
        + max(0.0, -nav_discount) * 1.2
        + (18 - price_to_ffo) * 2.0
        + (dividend_yield - 3.5) * 3.2
        - max(0.0, affo_payout - 78) * 1.4
    )
    income_score = clamp(
        45
        + dividend_yield * 6
        + (82 - affo_payout) * 0.55
        + (occupancy - 90) * 1.25
        - max(0.0, debt_to_ebitda - 5.5) * 6
    )
    property_score = clamp(occupancy * 0.62 + rent_growth * 4 + demand_score * 0.24)
    supply_score = clamp(100 - supply_pressure)
    rate_score = clamp(100 - rate_risk)
    ly_reit_score = (
        valuation_score * 0.22
        + income_score * 0.26
        + property_score * 0.24
        + supply_score * 0.14
        + rate_score * 0.14
    )
    return {
        **row,
        "symbol": str(row.get("symbol", "")).strip().upper(),
        "valuation_score": valuation_score,
        "income_score": income_score,
        "property_score": property_score,
        "supply_score": supply_score,
        "rate_score": rate_score,
        "ly_reit_score": ly_reit_score,
    }


def reit_warnings(row: dict[str, Any]) -> list[str]:
    item = enrich_reit(row)
    warnings: list[str] = []
    if safe_float(item.get("supply_pressure")) >= 65:
        warnings.append("Supply pressure / oversupply risk")
    if safe_float(item.get("price_to_ffo")) >= 24 or safe_float(item.get("nav_discount")) > 7:
        warnings.append("Valuation premium needs peer review")
    if safe_float(item.get("liquidity_score")) < 55:
        warnings.append("Trading liquidity slowdown")
    if safe_float(item.get("rate_risk")) >= 65 or safe_float(item.get("debt_to_ebitda")) >= 6.5:
        warnings.append("Rate and refinancing pressure")
    if safe_float(item.get("affo_payout")) >= 80:
        warnings.append("Dividend payout cushion is thin")
    return warnings


def reit_forecast(row: dict[str, Any]) -> list[dict[str, float | str]]:
    item = enrich_reit(row)
    base_price = safe_float(item.get("price"))
    quality_push = (safe_float(item.get("demand_score")) - 55) * 0.10
    growth_push = safe_float(item.get("ffo_growth")) * 0.55 + safe_float(item.get("rent_growth")) * 0.35
    momentum_push = safe_float(item.get("price_momentum")) * 0.28
    supply_drag = max(0.0, safe_float(item.get("supply_pressure")) - 45) * 0.12
    rate_drag = max(0.0, safe_float(item.get("rate_risk")) - 50) * 0.10
    annual_mid = clamp(growth_push + momentum_push + quality_push - supply_drag - rate_drag, -10.0, 14.0)
    uncertainty = clamp(5.0 + safe_float(item.get("rate_risk")) * 0.045 + safe_float(item.get("supply_pressure")) * 0.035, 6.0, 14.0)
    rows: list[dict[str, float | str]] = []
    for year in (1, 2, 4):
        mid_return = annual_mid * year
        band = uncertainty * (year ** 0.55)
        rows.append(
            {
                "Horizon": f"{year}Y",
                "Low": base_price * (1 + (mid_return - band) / 100),
                "Base": base_price * (1 + mid_return / 100),
                "High": base_price * (1 + (mid_return + band) / 100),
                "Mid return %": mid_return,
            }
        )
    return rows


def enrich_market(row: dict[str, Any]) -> dict[str, Any]:
    price_momentum_12m = safe_float(row.get("price_momentum_12m"))
    pir = safe_float(row.get("pir"))
    affordability_index = safe_float(row.get("affordability_index"))
    inventory_months = safe_float(row.get("inventory_months"))
    active_inventory_yoy = safe_float(row.get("active_inventory_yoy"))
    gross_rent_yield = safe_float(row.get("gross_rent_yield"))
    permits_per_1k = safe_float(row.get("permits_per_1k"))
    employment_growth = safe_float(row.get("employment_growth"))
    migration_score = safe_float(row.get("migration_score"))
    disaster_risk = safe_float(row.get("disaster_risk"))
    insurance_pressure = safe_float(row.get("insurance_pressure"))
    price_momentum_score = clamp(58 + price_momentum_12m * 4.0 - max(0.0, price_momentum_12m - 7.0) * 5.5)
    affordability_score = clamp(100 - max(0.0, pir - 3.8) * 8 + (affordability_index - 75) * 0.45)
    inventory_score = clamp(88 - abs(inventory_months - 4.0) * 6 - max(0.0, active_inventory_yoy - 35) * 0.6)
    rental_score = clamp(42 + gross_rent_yield * 5.0 - max(0.0, insurance_pressure - 45) * 0.35)
    supply_score = clamp(96 - max(0.0, permits_per_1k - 2.0) * 3.7)
    employment_score = clamp(55 + employment_growth * 7.0 + (migration_score - 50) * 0.45)
    hazard_score = clamp(100 - disaster_risk * 0.55 - insurance_pressure * 0.42)
    ly_market_score = (
        price_momentum_score * 0.15
        + affordability_score * 0.18
        + inventory_score * 0.14
        + rental_score * 0.18
        + supply_score * 0.12
        + employment_score * 0.15
        + hazard_score * 0.08
    )
    return {
        **row,
        "price_momentum_score": price_momentum_score,
        "affordability_score": affordability_score,
        "inventory_score": inventory_score,
        "rental_score": rental_score,
        "supply_score": supply_score,
        "employment_score": employment_score,
        "hazard_score": hazard_score,
        "ly_market_score": ly_market_score,
    }


def real_estate_warnings(row: dict[str, Any]) -> list[str]:
    item = enrich_market(row)
    warnings: list[str] = []
    if item["supply_score"] < 45:
        warnings.append("Supply pressure is elevated.")
    if item["affordability_score"] < 45:
        warnings.append("Income-relative housing cost is stretched.")
    if item["hazard_score"] < 50:
        warnings.append("Hazard or insurance pressure needs review.")
    if item["inventory_score"] < 50:
        warnings.append("Inventory / liquidity is weakening.")
    return warnings


def real_estate_forecast(row: dict[str, Any]) -> list[dict[str, float | str]]:
    item = enrich_market(row)
    base_price = safe_float(item.get("median_price"))
    annual_mid = (
        safe_float(item.get("price_momentum_12m")) * 0.42
        + (item["employment_score"] - 60) * 0.04
        - max(0.0, 65 - item["affordability_score"]) * 0.045
        - max(0.0, 70 - item["supply_score"]) * 0.035
        + (item["rental_score"] - 60) * 0.035
        - max(0.0, 60 - item["hazard_score"]) * 0.045
    )
    annual_mid = clamp(annual_mid, -7.5, 9.5)
    uncertainty = clamp(5.5 + (100 - item["inventory_score"]) * 0.045 + (100 - item["hazard_score"]) * 0.045, 6.0, 14.0)
    rows: list[dict[str, float | str]] = []
    for year in (1, 2, 4):
        mid_return = annual_mid * year
        band = uncertainty * (year ** 0.55)
        rows.append(
            {
                "Horizon": f"{year}Y",
                "Low": base_price * (1 + (mid_return - band) / 100),
                "Base": base_price * (1 + mid_return / 100),
                "High": base_price * (1 + (mid_return + band) / 100),
                "Mid return %": mid_return,
            }
        )
    return rows


def mortgage_payment(principal: float, annual_rate_pct: float, years: int) -> float:
    monthly_rate = annual_rate_pct / 100 / 12
    months = years * 12
    if principal <= 0:
        return 0.0
    if months <= 0:
        return principal
    if monthly_rate <= 0:
        return principal / months
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def property_calculator_result(
    purchase_price: float,
    monthly_rent: float,
    down_payment_pct: float,
    mortgage_rate_pct: float,
    loan_years: int,
    property_tax_pct: float,
    insurance_monthly: float,
    hoa_monthly: float,
    maintenance_pct: float,
    vacancy_pct: float,
) -> dict[str, float]:
    down_payment = purchase_price * down_payment_pct / 100
    loan_amount = max(0.0, purchase_price - down_payment)
    debt_service = mortgage_payment(loan_amount, mortgage_rate_pct, loan_years)
    monthly_tax = purchase_price * property_tax_pct / 100 / 12
    monthly_maintenance = purchase_price * maintenance_pct / 100 / 12
    monthly_vacancy = monthly_rent * vacancy_pct / 100
    monthly_noi = monthly_rent - monthly_tax - insurance_monthly - hoa_monthly - monthly_maintenance - monthly_vacancy
    monthly_cash_flow = monthly_noi - debt_service
    cash_invested = down_payment + purchase_price * 0.03
    cap_rate = monthly_noi * 12 / purchase_price * 100 if purchase_price else 0.0
    cash_on_cash = monthly_cash_flow * 12 / cash_invested * 100 if cash_invested else 0.0
    fixed_before_vacancy = debt_service + monthly_tax + insurance_monthly + hoa_monthly + monthly_maintenance
    break_even_rent = fixed_before_vacancy / max(0.01, 1 - vacancy_pct / 100)
    return {
        "monthly_cash_flow": monthly_cash_flow,
        "monthly_noi": monthly_noi,
        "cap_rate": cap_rate,
        "cash_on_cash": cash_on_cash,
        "break_even_rent": break_even_rent,
        "cash_invested": cash_invested,
    }


def objective_net_return_pct(objective: dict[str, Any]) -> float:
    account = str(objective.get("account_type", "")).lower()
    tax_drag = safe_float(objective.get("tax_fee_drag_pct"))
    if "retirement" in account or "tax-advantaged" in account:
        tax_drag *= 0.35
    if "cash" in account:
        tax_drag *= 0.50
    return max(safe_float(objective.get("expected_return_pct")) - tax_drag, -99.0)


def projected_objective_amount(objective: dict[str, Any]) -> float:
    months = max(int(round(safe_float(objective.get("target_years")) * 12)), 0)
    current = safe_float(objective.get("current_amount"))
    contribution = safe_float(objective.get("monthly_contribution"))
    monthly_rate = objective_net_return_pct(objective) / 100 / 12
    if months <= 0:
        return current
    if abs(monthly_rate) < 0.0000001:
        return current + contribution * months
    growth_factor = (1 + monthly_rate) ** months
    return current * growth_factor + contribution * ((growth_factor - 1) / monthly_rate)


def required_monthly_contribution(objective: dict[str, Any]) -> float:
    months = max(int(round(safe_float(objective.get("target_years")) * 12)), 0)
    target = safe_float(objective.get("target_amount"))
    monthly_rate = objective_net_return_pct(objective) / 100 / 12
    if target <= 0:
        return 0.0
    if months <= 0:
        return max(0.0, target - safe_float(objective.get("current_amount")))
    if abs(monthly_rate) < 0.0000001:
        return max(0.0, (target - safe_float(objective.get("current_amount"))) / months)
    growth_factor = (1 + monthly_rate) ** months
    current_future_value = safe_float(objective.get("current_amount")) * growth_factor
    annuity_factor = (growth_factor - 1) / monthly_rate
    if annuity_factor <= 0:
        return 0.0
    return max(0.0, (target - current_future_value) / annuity_factor)


def normalize_objectives(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    objectives: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        name = str(row.get("name") or row.get("Goal") or "").strip()
        target_amount = max(safe_float(row.get("target_amount")), 0.0)
        current_amount = max(safe_float(row.get("current_amount")), 0.0)
        monthly_contribution = max(safe_float(row.get("monthly_contribution")), 0.0)
        if not name and target_amount <= 0 and current_amount <= 0 and monthly_contribution <= 0:
            continue
        objectives.append(
            {
                "name": name or f"Objective {index}",
                "objective_type": str(row.get("objective_type") or "Other"),
                "target_amount": target_amount,
                "target_years": max(safe_float(row.get("target_years")), 0.0),
                "current_amount": current_amount,
                "monthly_contribution": monthly_contribution,
                "account_type": str(row.get("account_type") or "Taxable Brokerage"),
                "expected_return_pct": safe_float(row.get("expected_return_pct")),
                "tax_fee_drag_pct": max(safe_float(row.get("tax_fee_drag_pct")), 0.0),
                "priority": str(row.get("priority") or "Medium"),
            }
        )
    return objectives


def analyze_objectives(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    analysis: list[dict[str, Any]] = []
    for objective in normalize_objectives(rows):
        projected = projected_objective_amount(objective)
        target = safe_float(objective.get("target_amount"))
        shortfall = target - projected
        readiness = clamp(safe_divide(projected, target) * 100 if target > 0 else 100.0)
        required = required_monthly_contribution(objective)
        monthly_gap = max(0.0, required - safe_float(objective.get("monthly_contribution")))
        status = "On Track" if readiness >= 100 else "Watch" if readiness >= 85 else "Behind"
        analysis.append(
            {
                "Goal": objective["name"],
                "Type": objective["objective_type"],
                "Priority": objective["priority"],
                "Target": target,
                "Years": objective["target_years"],
                "Current": objective["current_amount"],
                "Monthly": objective["monthly_contribution"],
                "Net Return %": objective_net_return_pct(objective),
                "Projected": projected,
                "Shortfall": max(0.0, shortfall),
                "Required Monthly": required,
                "Monthly Gap": monthly_gap,
                "Readiness": readiness,
                "Status": status,
            }
        )
    return analysis


def summarize_objectives(analysis: list[dict[str, Any]]) -> dict[str, Any]:
    if not analysis:
        return {
            "goal_count": 0,
            "average_readiness": 0.0,
            "on_track_count": 0,
            "behind_count": 0,
            "total_shortfall": 0.0,
            "required_monthly_total": 0.0,
            "monthly_gap_total": 0.0,
            "most_at_risk_goal": "No objectives",
            "warnings": ["Add at least one financial objective."],
        }
    average_readiness = sum(item["Readiness"] for item in analysis) / len(analysis)
    behind_count = sum(1 for item in analysis if item["Status"] == "Behind")
    warnings: list[str] = []
    monthly_gap_total = sum(item["Monthly Gap"] for item in analysis)
    if behind_count:
        warnings.append(f"{behind_count} financial objective(s) are behind plan.")
    if monthly_gap_total > 0:
        warnings.append(f"Current objectives need about {money(monthly_gap_total)} more monthly savings.")
    weakest = sorted(analysis, key=lambda item: item["Readiness"])[0]
    return {
        "goal_count": len(analysis),
        "average_readiness": average_readiness,
        "on_track_count": sum(1 for item in analysis if item["Status"] == "On Track"),
        "behind_count": behind_count,
        "total_shortfall": sum(item["Shortfall"] for item in analysis),
        "required_monthly_total": sum(item["Required Monthly"] for item in analysis),
        "monthly_gap_total": monthly_gap_total,
        "most_at_risk_goal": weakest["Goal"],
        "warnings": warnings,
    }


def evaluate_scenario(
    foundation: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
    scenario: dict[str, Any],
) -> dict[str, Any]:
    income_shock = safe_float(scenario.get("income_shock_pct"))
    market_shock = safe_float(scenario.get("market_asset_shock_pct"))
    housing_shock = safe_float(scenario.get("real_estate_shock_pct"))
    stressed_income = foundation["monthly_income"] * (1 + income_shock / 100)
    stressed_cash_flow = stressed_income - foundation["monthly_expenses"]
    stressed_market_assets = portfolio.total_value * (1 + market_shock / 100)
    stressed_real_estate_equity = max(
        real_estate.total_value * (1 + housing_shock / 100) - real_estate.total_debt,
        0.0,
    )
    stressed_net_worth = (
        foundation["cash"]
        + stressed_market_assets
        + foundation["retirement_accounts"]
        + stressed_real_estate_equity
        - foundation["personal_debt"]
    )
    net_worth_change = stressed_net_worth - foundation["net_worth"]
    resilience_score = clamp(
        foundation["score"]
        + income_shock * 0.22
        + market_shock * 0.18
        + housing_shock * 0.12
    )
    return {
        "stressed_income": stressed_income,
        "stressed_cash_flow": stressed_cash_flow,
        "stressed_market_assets": stressed_market_assets,
        "stressed_real_estate_equity": stressed_real_estate_equity,
        "stressed_net_worth": stressed_net_worth,
        "net_worth_change": net_worth_change,
        "resilience_score": resilience_score,
    }


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
    return enrich_stock(row)["life_stock_score"]


def build_portfolio(rows: list[dict[str, Any]]) -> PortfolioSnapshot:
    clean_rows: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).strip().upper()
        if not symbol:
            continue
        enriched = enrich_stock(row)
        shares = safe_float(row.get("shares"))
        price = safe_float(row.get("price"), safe_float(enriched.get("price")))
        purchase_price = safe_float(row.get("purchase_price"))
        market_value = shares * price
        cost_basis = shares * purchase_price
        holding_score = safe_float(enriched.get("life_stock_score"), 50.0)
        clean_rows.append(
            {
                **enriched,
                "symbol": symbol,
                "sector": str(enriched.get("sector") or row.get("sector") or "Unclassified"),
                "shares": shares,
                "price": price,
                "purchase_price": purchase_price,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "gain_loss": market_value - cost_basis,
                "holding_score": holding_score,
                "beta": safe_float(enriched.get("beta"), 1),
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
    concentration_score = clamp(
        100 - max(0, top_weight - 0.25) * 150 - max(0, top_sector_weight - 0.50) * 100
    )
    beta_score = clamp(90 - max(0, weighted_beta - 1) * 42)
    performance_score = clamp(55 + gain_loss_pct * 100 * 1.2)
    portfolio_score = round(
        weighted_holding_score * 0.45
        + concentration_score * 0.25
        + beta_score * 0.15
        + performance_score * 0.15
    )

    warnings: list[str] = []
    if top_weight > 0.45:
        warnings.append("Top holding concentration is high.")
    if top_sector_weight > 0.62:
        warnings.append("Sector concentration is elevated.")
    if weighted_beta > 1.30:
        warnings.append("Portfolio beta can amplify volatility.")
    if gain_loss_pct < -0.1:
        warnings.append("Portfolio unrealized loss is greater than 10%.")
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
        weighted_score=weighted_holding_score,
        concentration_score=concentration_score,
        beta_score=beta_score,
        performance_score=performance_score,
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


def build_real_estate(rows: list[dict[str, Any]], selected_market_id: str | None = None) -> RealEstateSnapshot:
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
    property_score = weighted_score_total / total_value if total_value else None
    market_record = market_by_id(selected_market_id or "") or market_by_id("CLT-28202")
    market = enrich_market(market_record) if market_record else None
    market_forecast = real_estate_forecast(market) if market else []
    if market:
        all_warnings.extend(real_estate_warnings(market))
    if property_score is not None and market:
        score = round(property_score * 0.55 + safe_float(market.get("ly_market_score")) * 0.45)
    elif property_score is not None:
        score = round(property_score)
    elif market:
        score = round(safe_float(market.get("ly_market_score")))
    else:
        score = 50

    return RealEstateSnapshot(
        rows=clean_rows,
        total_value=total_value,
        total_debt=total_debt,
        total_equity=total_equity,
        monthly_cash_flow=total_cash_flow,
        average_ltv=average_ltv,
        average_vacancy=average_vacancy,
        market=market,
        market_forecast=market_forecast,
        score=score,
        warnings=list(dict.fromkeys(all_warnings)),
    )


def calculate_foundation(
    finance: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
) -> dict[str, Any]:
    monthly_income = safe_float(finance.get("monthly_income"))
    fixed_expense = safe_float(finance.get("fixed_expense"))
    variable_expense = safe_float(finance.get("variable_expense"))
    monthly_debt_payment = safe_float(finance.get("debt_payment"))
    cash = safe_float(finance.get("cash"))
    personal_debt = safe_float(finance.get("personal_debt"))
    retirement_accounts = safe_float(finance.get("retirement_accounts"))
    monthly_expenses = (
        fixed_expense
        + variable_expense
        + monthly_debt_payment
    )
    living_expenses = fixed_expense + variable_expense
    cash_flow = monthly_income - monthly_expenses
    savings_rate = safe_divide(max(cash_flow, 0.0), monthly_income)
    runway = safe_divide(cash, living_expenses)
    net_worth = cash + portfolio.total_value + retirement_accounts + real_estate.total_equity - personal_debt
    debt_to_income = safe_divide(monthly_debt_payment, monthly_income)
    goal_progress = safe_divide(
        safe_float(finance.get("current_goal_savings")),
        safe_float(finance.get("target_goal_amount")),
    )

    target_runway = max(safe_float(finance.get("runway_target"), 6), 1)
    liquidity_score = clamp(runway / target_runway * 100)
    debt_score = clamp(100 - debt_to_income / 0.36 * 100)
    savings_score = clamp(savings_rate / 0.20 * 100)
    goal_score = clamp(goal_progress * 100)
    risk_capacity_score = clamp(
        liquidity_score * 0.35
        + debt_score * 0.25
        + savings_score * 0.25
        + max(0.0, 100 - safe_float(finance.get("investment_risk_score"))) * 0.15
    )
    life_score = clamp(
        liquidity_score * 0.25
        + debt_score * 0.25
        + savings_score * 0.25
        + goal_score * 0.15
        + risk_capacity_score * 0.10
    )
    score = round(life_score)

    warnings: list[str] = []
    if cash_flow < 0:
        warnings.append("Monthly cash flow is negative.")
    if runway < 3:
        warnings.append("Emergency fund is below 3 months of living expenses.")
    elif runway >= target_runway:
        warnings.append("Emergency fund is strong relative to monthly expenses.")
    if debt_to_income > 0.36:
        warnings.append("Debt payments are high relative to income.")
    if savings_rate < 0.10:
        warnings.append("Savings rate is below the 10% baseline.")
    elif savings_rate >= 0.20:
        warnings.append("Savings rate is strong and supports long-term planning.")

    return {
        "score": score,
        "label": score_label(score),
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "living_expenses": living_expenses,
        "cash_flow": cash_flow,
        "savings_rate": savings_rate,
        "runway": runway,
        "net_worth": net_worth,
        "cash": cash,
        "personal_debt": personal_debt,
        "retirement_accounts": retirement_accounts,
        "warnings": warnings,
        "debt_to_income": debt_to_income,
        "goal_progress": goal_progress,
        "liquidity_score": liquidity_score,
        "debt_score": debt_score,
        "savings_score": savings_score,
        "goal_score": goal_score,
        "risk_capacity_score": risk_capacity_score,
    }


def evaluate_goal(
    goal: dict[str, Any],
    foundation: dict[str, Any],
    objective_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if objective_summary and objective_summary.get("goal_count", 0) > 0:
        score = round(clamp(safe_float(objective_summary.get("average_readiness"))))
        label = "On Route" if score >= 85 else "Needs Guardrails" if score >= 65 else "Off Route"
        return {
            "score": score,
            "label": label,
            "gap": safe_float(objective_summary.get("total_shortfall")),
            "monthly_required": safe_float(objective_summary.get("required_monthly_total")),
            "contribution": max(
                safe_float(objective_summary.get("required_monthly_total"))
                - safe_float(objective_summary.get("monthly_gap_total")),
                0.0,
            ),
            "months": safe_float(goal.get("target_months"), 1),
            "goal_count": int(objective_summary.get("goal_count", 0)),
            "most_at_risk_goal": str(objective_summary.get("most_at_risk_goal", "")),
            "warnings": list(objective_summary.get("warnings", [])),
        }
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
        "goal_count": 1,
        "most_at_risk_goal": str(goal.get("goal_name") or "Primary goal"),
        "warnings": [],
    }


def evaluate_resilience(
    foundation: dict[str, Any],
    portfolio: PortfolioSnapshot,
    real_estate: RealEstateSnapshot,
    extra_warnings: list[str] | None = None,
    scenario_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    warnings = [*foundation["warnings"], *portfolio.warnings, *real_estate.warnings]
    warnings.extend(extra_warnings or [])
    if scenario_result and scenario_result["net_worth_change"] < 0:
        warnings.append("Scenario stress reduces projected net worth.")
    warnings = list(dict.fromkeys(warnings))
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
    objective_summary: dict[str, Any] | None = None,
    stock_detail: dict[str, Any] | None = None,
    reit_detail: dict[str, Any] | None = None,
    scenario_result: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    evidence = [
        {
            "name": "Financial Foundation",
            "score": foundation["score"],
            "plain": foundation["label"],
            "detail": f"Liquidity {foundation['liquidity_score']:.0f}, debt {foundation['debt_score']:.0f}, savings {foundation['savings_score']:.0f}, risk capacity {foundation['risk_capacity_score']:.0f}.",
        },
        {
            "name": "Goal Route",
            "score": goal["score"],
            "plain": goal["label"],
            "detail": f"{goal.get('goal_count', 1)} objective(s), shortfall {money(goal['gap'])}, required {money(goal['monthly_required'])}/mo.",
        },
        {
            "name": "Portfolio",
            "score": portfolio.portfolio_score,
            "plain": score_label(portfolio.portfolio_score),
            "detail": f"{len(portfolio.rows)} holdings, weighted stock score {portfolio.weighted_score:.0f}, top position {percent(portfolio.top_weight)}.",
        },
        {
            "name": "Real Estate",
            "score": real_estate.score,
            "plain": score_label(real_estate.score),
            "detail": f"Market {real_estate.market['market_id'] if real_estate.market else 'N/A'}, equity {money(real_estate.total_equity)}, cash flow {signed_money(real_estate.monthly_cash_flow)}/mo.",
        },
        {
            "name": "Risk Filter",
            "score": resilience["score"],
            "plain": resilience["state"],
            "detail": f"{resilience['pressure']} pressure point(s) need monitoring.",
        },
    ]
    if stock_detail:
        evidence.append(
            {
                "name": f"Stock Lens: {stock_detail['symbol']}",
                "score": stock_detail["life_stock_score"],
                "plain": score_label(stock_detail["life_stock_score"]),
                "detail": f"Valuation {stock_detail['value_score']:.0f}, momentum {stock_detail['momentum_score']:.0f}, quality {stock_detail['quality_score']:.0f}, risk {stock_detail['risk_balance_score']:.0f}.",
            }
        )
    if reit_detail:
        evidence.append(
            {
                "name": f"REIT Lens: {reit_detail['symbol']}",
                "score": reit_detail["ly_reit_score"],
                "plain": score_label(reit_detail["ly_reit_score"]),
                "detail": f"Income {reit_detail['income_score']:.0f}, property {reit_detail['property_score']:.0f}, supply {reit_detail['supply_score']:.0f}, rate {reit_detail['rate_score']:.0f}.",
            }
        )
    if objective_summary and objective_summary.get("warnings"):
        evidence.append(
            {
                "name": "Objective Pressure",
                "score": max(0, 100 - safe_float(objective_summary.get("monthly_gap_total")) / 25),
                "plain": "Watch",
                "detail": " | ".join(str(item) for item in objective_summary["warnings"][:2]),
            }
        )
    if scenario_result:
        evidence.append(
            {
                "name": "Scenario Stress",
                "score": scenario_result["resilience_score"],
                "plain": score_label(scenario_result["resilience_score"]),
                "detail": f"Stress net worth change {signed_money(scenario_result['net_worth_change'])}; cash flow {signed_money(scenario_result['stressed_cash_flow'])}/mo.",
            }
        )
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
    stock_detail: dict[str, Any] | None = None,
    reit_detail: dict[str, Any] | None = None,
    scenario_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data_inputs = [
        bool(profile.get("decision_question")),
        foundation["monthly_income"] > 0,
        goal["months"] > 0,
        len(portfolio.rows) > 0,
        real_estate.market is not None,
        stock_detail is not None,
        reit_detail is not None,
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
            "name": "Stock Lens",
            "stage": "Data -> Evidence",
            "score": safe_float(stock_detail.get("life_stock_score") if stock_detail else 0),
            "detail": f"{stock_detail['symbol']} stock score and warnings are active." if stock_detail else "No selected stock.",
        },
        {
            "name": "REIT Lens",
            "stage": "Data -> Evidence",
            "score": safe_float(reit_detail.get("ly_reit_score") if reit_detail else 0),
            "detail": f"{reit_detail['symbol']} REIT score, forecast, and income lens are active." if reit_detail else "No selected REIT.",
        },
        {
            "name": "Real Estate",
            "stage": "Data -> Evidence",
            "score": real_estate.score,
            "detail": f"Market {real_estate.market['market_id'] if real_estate.market else 'N/A'}; equity {money(real_estate.total_equity)}.",
        },
        {
            "name": "Scenario",
            "stage": "Model -> Evidence",
            "score": safe_float(scenario_result.get("resilience_score") if scenario_result else 0),
            "detail": f"Stress net worth change {signed_money(scenario_result['net_worth_change'])}." if scenario_result else "No stress scenario.",
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
            "status": len(portfolio.rows) > 0 and real_estate.market is not None and stock_detail is not None and reit_detail is not None,
            "detail": "Portfolio, stock lens, REIT lens, and real estate market all feed the model.",
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
    verification_runs = [
        {
            "run": "Run 1",
            "name": "Structure",
            "score": 100 if validation_checks[0]["status"] else 0,
            "status": "PASS" if validation_checks[0]["status"] else "REVIEW",
            "proof": "7/7 core nodes",
            "detail": validation_checks[0]["detail"],
        },
        {
            "run": "Run 2",
            "name": "Live Binding",
            "score": 100 if validation_checks[1]["status"] and validation_checks[3]["status"] else 50,
            "status": "PASS" if validation_checks[1]["status"] and validation_checks[3]["status"] else "REVIEW",
            "proof": f"{len(modules)} module links",
            "detail": "All live sections feed the current model state.",
        },
        {
            "run": "Run 3",
            "name": "Evidence",
            "score": 100 if validation_checks[2]["status"] and validation_checks[4]["status"] else 50,
            "status": "PASS" if validation_checks[2]["status"] and validation_checks[4]["status"] else "REVIEW",
            "proof": f"{len(evidence)} signals",
            "detail": "Evidence and risk signals are traceable to source inputs.",
        },
    ]

    return {
        "core_nodes": core_nodes,
        "modules": modules,
        "relationships": ONTOLOGY_RELATIONSHIPS,
        "validation_checks": validation_checks,
        "validation_score": validation_score,
        "verification_runs": verification_runs,
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
            position: relative;
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
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity 160ms ease, max-height 160ms ease, margin-top 160ms ease;
          }
          .module-card:hover .module-detail, .module-card:focus .module-detail {
            opacity: 1;
            max-height: 90px;
            margin-top: 8px;
          }
          .relationship-list {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
          }
          .relationship-row, .validation-row {
            border: 1px solid #d8e0ea;
            border-radius: 8px;
            background: #ffffff;
            padding: 10px 12px;
            position: relative;
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
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity 160ms ease, max-height 160ms ease, margin-top 160ms ease;
          }
          .relationship-row:hover .relationship-claim,
          .relationship-row:focus .relationship-claim,
          .validation-row:hover .validation-detail,
          .validation-row:focus .validation-detail {
            opacity: 1;
            max-height: 80px;
            margin-top: 6px;
          }
          .validation-row.pass {
            border-left: 5px solid #14735f;
          }
          .validation-row.warn {
            border-left: 5px solid #ad3d3d;
          }
          .verification-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 12px 0 18px;
          }
          .verify-card {
            --accent: #14735f;
            border: 1px solid #d8e0ea;
            border-left: 5px solid var(--accent);
            border-radius: 8px;
            background: #ffffff;
            min-height: 142px;
            padding: 14px;
          }
          .verify-run {
            color: var(--accent);
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
          }
          .verify-name {
            color: #17202a;
            font-size: 1.1rem;
            font-weight: 880;
            margin-top: 7px;
          }
          .verify-status {
            display: inline-block;
            color: #ffffff;
            background: var(--accent);
            border-radius: 999px;
            padding: 3px 9px;
            font-size: 0.72rem;
            font-weight: 850;
            margin-top: 8px;
          }
          .verify-proof {
            color: #4e5d6c;
            font-size: 0.88rem;
            margin-top: 10px;
          }
          .verify-detail {
            color: #607080;
            font-size: 0.8rem;
            line-height: 1.35;
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity 160ms ease, max-height 160ms ease, margin-top 160ms ease;
          }
          .verify-card:hover .verify-detail, .verify-card:focus .verify-detail {
            opacity: 1;
            max-height: 80px;
            margin-top: 8px;
          }
          .status-dot {
            display: inline-block;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #14735f;
            margin-right: 7px;
            vertical-align: middle;
          }
          @media (max-width: 900px) {
            .ly-topline, .signal-row { display: block; }
            .signal-ring { margin-top: 16px; }
            .stage-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .ontology-flow, .module-grid, .relationship-list, .verification-strip {
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
            f'<div class="relationship-route"><span class="status-dot"></span>{escape(source)} -> {escape(target)}</div>'
            f'<div class="relationship-claim">{escape(claim)}</div>'
            "</div>"
        )
    st.markdown(f'<div class="relationship-list">{relationship_html}</div>', unsafe_allow_html=True)


def render_verification_runs(snapshot: dict[str, Any]) -> None:
    run_html = ""
    for item in snapshot["verification_runs"]:
        run_html += (
            '<div class="verify-card" tabindex="0">'
            f'<div class="verify-run">{escape(item["run"])}</div>'
            f'<div class="verify-name">{escape(item["name"])}</div>'
            f'<div class="verify-status">{escape(item["status"])}</div>'
            f'<div class="ontology-bar" style="--value: {clamp(item["score"]):.0f}%"><span></span></div>'
            f'<div class="verify-proof">{escape(item["proof"])}</div>'
            f'<div class="verify-detail">{escape(item["detail"])}</div>'
            "</div>"
        )
    st.markdown(f'<div class="verification-strip">{run_html}</div>', unsafe_allow_html=True)


def render_validation_checks(snapshot: dict[str, Any]) -> None:
    for check in snapshot["validation_checks"]:
        state = "pass" if check["status"] else "warn"
        label = "Verified" if check["status"] else "Needs review"
        st.markdown(
            f"""
            <div class="validation-row {state}" tabindex="0">
              <div class="relationship-route"><span class="status-dot"></span>{escape(check["name"])}: {label}</div>
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

    st.markdown("#### 3-Run Verification")
    render_verification_runs(snapshot)

    st.markdown("#### Core Decision Ontology")
    render_ontology_map(snapshot)

    st.markdown("#### Module Connection Board")
    render_module_grid(snapshot)

    st.markdown("#### Relationship Trace")
    render_relationships(snapshot)

    st.markdown("#### Direct Validation")
    render_validation_checks(snapshot)


def initialize_state() -> None:
    defaults = {
        "profile": deepcopy(DEFAULT_PROFILE),
        "finance": deepcopy(DEFAULT_FINANCE),
        "goal": deepcopy(DEFAULT_GOAL),
        "objectives": deepcopy(DEFAULT_OBJECTIVES),
        "scenario": deepcopy(DEFAULT_SCENARIO),
        "selected_stock_symbol": "MSFT",
        "selected_reit_symbol": "PLD",
        "selected_market_id": "CLT-28202",
        "holdings": deepcopy(DEFAULT_HOLDINGS),
        "real_estate": deepcopy(DEFAULT_REAL_ESTATE),
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
        if st.button("Reset sample data", width="stretch"):
            for key in [
                "profile",
                "finance",
                "goal",
                "objectives",
                "scenario",
                "selected_stock_symbol",
                "selected_reit_symbol",
                "selected_market_id",
                "holdings",
                "real_estate",
                "decision_log",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def render_foundation_inputs() -> None:
    finance = st.session_state.finance
    st.subheader("Financial Foundation")
    c1, c2, c3, c4 = st.columns(4)
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
        finance["retirement_accounts"] = st.number_input(
            "Retirement accounts",
            min_value=0.0,
            step=1000.0,
            value=float(finance["retirement_accounts"]),
        )
    with c4:
        finance["runway_target"] = st.number_input(
            "Runway target months",
            min_value=1.0,
            max_value=24.0,
            step=1.0,
            value=float(finance["runway_target"]),
        )
        finance["current_goal_savings"] = st.number_input(
            "Current goal savings",
            min_value=0.0,
            step=1000.0,
            value=float(finance["current_goal_savings"]),
        )
        finance["target_goal_amount"] = st.number_input(
            "Goal reference amount",
            min_value=0.0,
            step=5000.0,
            value=float(finance["target_goal_amount"]),
        )
        finance["investment_risk_score"] = st.slider(
            "Investment risk score",
            min_value=0,
            max_value=100,
            value=int(finance["investment_risk_score"]),
        )


def render_goal_inputs(objective_analysis: list[dict[str, Any]], objective_summary: dict[str, Any]) -> None:
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
    st.markdown("#### Financial Objectives")
    edited = st.data_editor(
        st.session_state.objectives,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "name": st.column_config.TextColumn("Goal"),
            "objective_type": st.column_config.TextColumn("Type"),
            "target_amount": st.column_config.NumberColumn("Target", min_value=0.0),
            "target_years": st.column_config.NumberColumn("Years", min_value=0.0, max_value=60.0),
            "current_amount": st.column_config.NumberColumn("Current", min_value=0.0),
            "monthly_contribution": st.column_config.NumberColumn("Monthly", min_value=0.0),
            "account_type": st.column_config.TextColumn("Account"),
            "expected_return_pct": st.column_config.NumberColumn("Return %", min_value=-25.0, max_value=25.0),
            "tax_fee_drag_pct": st.column_config.NumberColumn("Tax/Fee %", min_value=0.0, max_value=15.0),
            "priority": st.column_config.SelectboxColumn("Priority", options=["High", "Medium", "Low"]),
        },
    )
    st.session_state.objectives = rows_from_editor(edited)
    st.caption(
        f"{objective_summary['on_track_count']}/{objective_summary['goal_count']} on track. "
        f"Most at risk: {objective_summary['most_at_risk_goal']}."
    )
    if objective_analysis:
        st.dataframe(
            [
                {
                    "Goal": row["Goal"],
                    "Status": row["Status"],
                    "Readiness": round(row["Readiness"], 1),
                    "Projected": round(row["Projected"]),
                    "Shortfall": round(row["Shortfall"]),
                    "Required Monthly": round(row["Required Monthly"]),
                    "Monthly Gap": round(row["Monthly Gap"]),
                }
                for row in objective_analysis
            ],
            width="stretch",
            hide_index=True,
        )


def render_scenario_inputs(scenario_result: dict[str, Any]) -> None:
    scenario = st.session_state.scenario
    st.subheader("Scenario Stress")
    c1, c2, c3 = st.columns(3)
    with c1:
        scenario["income_shock_pct"] = st.slider(
            "Income shock %",
            min_value=-50.0,
            max_value=25.0,
            value=float(scenario["income_shock_pct"]),
            step=1.0,
        )
    with c2:
        scenario["market_asset_shock_pct"] = st.slider(
            "Market asset shock %",
            min_value=-60.0,
            max_value=40.0,
            value=float(scenario["market_asset_shock_pct"]),
            step=1.0,
        )
    with c3:
        scenario["real_estate_shock_pct"] = st.slider(
            "Real estate shock %",
            min_value=-40.0,
            max_value=30.0,
            value=float(scenario["real_estate_shock_pct"]),
            step=1.0,
        )
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Stress cash flow", signed_money(scenario_result["stressed_cash_flow"]))
    m2.metric("Stress net worth", money(scenario_result["stressed_net_worth"]))
    m3.metric("Net worth change", signed_money(scenario_result["net_worth_change"]))
    m4.metric("Stress resilience", f"{scenario_result['resilience_score']:.0f}/100")


def render_portfolio_inputs() -> None:
    st.subheader("Portfolio Input")
    symbols = [row["symbol"] for row in STOCK_UNIVERSE]
    if st.session_state.selected_stock_symbol not in symbols:
        st.session_state.selected_stock_symbol = symbols[0]
    selected_symbol = st.selectbox(
        "Stock detail lens",
        symbols,
        index=symbols.index(st.session_state.selected_stock_symbol),
        format_func=lambda symbol: f"{symbol} - {stock_by_symbol(symbol)['company']}",
    )
    st.session_state.selected_stock_symbol = selected_symbol
    selected_stock = enrich_stock(stock_by_symbol(selected_symbol) or {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stock score", f"{selected_stock['life_stock_score']:.0f}/100")
    c2.metric("Valuation", f"{selected_stock['value_score']:.0f}")
    c3.metric("Momentum", f"{selected_stock['momentum_score']:.0f}")
    c4.metric("Risk balance", f"{selected_stock['risk_balance_score']:.0f}")
    render_warnings(stock_warnings(selected_stock))
    with st.expander("Open stock score basis", expanded=False):
        st.dataframe(stock_score_basis(selected_stock), width="stretch", hide_index=True)
        st.caption(str(selected_stock.get("thesis", "")))
    st.markdown("#### Portfolio Holdings")
    edited = st.data_editor(
        st.session_state.holdings,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "symbol": st.column_config.TextColumn("Symbol", required=True),
            "company": st.column_config.TextColumn("Company"),
            "sector": st.column_config.TextColumn("Sector"),
            "shares": st.column_config.NumberColumn("Shares", min_value=0.0),
            "purchase_price": st.column_config.NumberColumn("Cost / share", min_value=0.0),
            "price": st.column_config.NumberColumn("Current price", min_value=0.0),
            "beta": st.column_config.NumberColumn("Beta", min_value=0.0, max_value=3.0),
            "pe": st.column_config.NumberColumn("P/E", min_value=0.0, max_value=200.0),
            "dividend_yield": st.column_config.NumberColumn("Yield %", min_value=0.0, max_value=20.0),
            "momentum_6m": st.column_config.NumberColumn("6M %", min_value=-80.0, max_value=150.0),
            "revenue_growth": st.column_config.NumberColumn("Growth %", min_value=-80.0, max_value=150.0),
            "margin_quality": st.column_config.NumberColumn("Margin quality", min_value=0.0, max_value=100.0),
            "debt_risk": st.column_config.NumberColumn("Debt risk", min_value=0.0, max_value=100.0),
        },
    )
    st.session_state.holdings = rows_from_editor(edited)


def render_reit_inputs(reit_detail: dict[str, Any]) -> None:
    st.subheader("REIT Property Intelligence")
    symbols = [row["symbol"] for row in REIT_UNIVERSE]
    if st.session_state.selected_reit_symbol not in symbols:
        st.session_state.selected_reit_symbol = symbols[0]
    selected_symbol = st.selectbox(
        "REIT lens",
        symbols,
        index=symbols.index(st.session_state.selected_reit_symbol),
        format_func=lambda symbol: f"{symbol} - {reit_by_symbol(symbol)['company']}",
    )
    st.session_state.selected_reit_symbol = selected_symbol
    reit_detail = enrich_reit(reit_by_symbol(selected_symbol) or reit_detail)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("REIT score", f"{reit_detail['ly_reit_score']:.0f}/100")
    c2.metric("Dividend yield", pct_value(safe_float(reit_detail.get("dividend_yield")), 2))
    c3.metric("P/FFO", f"{safe_float(reit_detail.get('price_to_ffo')):.1f}x")
    c4.metric("Rate risk", f"{safe_float(reit_detail.get('rate_risk')):.0f}/100")
    render_warnings(reit_warnings(reit_detail))
    st.caption(str(reit_detail.get("property_note", "")))
    st.markdown("#### REIT Score Basis")
    st.dataframe(
        [
            {"Pillar": "Valuation", "Score": round(reit_detail["valuation_score"], 1), "Weight": "22%"},
            {"Pillar": "Income", "Score": round(reit_detail["income_score"], 1), "Weight": "26%"},
            {"Pillar": "Property", "Score": round(reit_detail["property_score"], 1), "Weight": "24%"},
            {"Pillar": "Supply", "Score": round(reit_detail["supply_score"], 1), "Weight": "14%"},
            {"Pillar": "Rate", "Score": round(reit_detail["rate_score"], 1), "Weight": "14%"},
        ],
        width="stretch",
        hide_index=True,
    )
    st.markdown("#### Forecast Range")
    st.dataframe(
        [
            {
                "Horizon": row["Horizon"],
                "Low": round(safe_float(row["Low"]), 2),
                "Base": round(safe_float(row["Base"]), 2),
                "High": round(safe_float(row["High"]), 2),
                "Mid return %": round(safe_float(row["Mid return %"]), 1),
            }
            for row in reit_forecast(reit_detail)
        ],
        width="stretch",
        hide_index=True,
    )
    with st.expander("Dividend scenario", expanded=False):
        amount = st.number_input("Investment amount", min_value=100.0, value=10000.0, step=500.0)
        price_scenario = st.slider("12-month price scenario", -35, 35, 0, 1, format="%d%%")
        annual_income = amount * safe_float(reit_detail.get("dividend_yield")) / 100
        scenario_total = annual_income + amount * price_scenario / 100
        d1, d2, d3 = st.columns(3)
        d1.metric("Annual income", money(annual_income))
        d2.metric("Price scenario", signed_money(amount * price_scenario / 100))
        d3.metric("Scenario total", signed_money(scenario_total))


def render_real_estate_inputs() -> None:
    st.subheader("Real Estate Market Lens")
    market_ids = [row["market_id"] for row in REAL_ESTATE_MARKETS]
    if st.session_state.selected_market_id not in market_ids:
        st.session_state.selected_market_id = "CLT-28202"
    selected_market_id = st.selectbox(
        "Market lens",
        market_ids,
        index=market_ids.index(st.session_state.selected_market_id),
        format_func=lambda market_id: f"{market_by_id(market_id)['city']}, {market_by_id(market_id)['state']} - {market_id}",
    )
    st.session_state.selected_market_id = selected_market_id
    market = enrich_market(market_by_id(selected_market_id) or {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market score", f"{market['ly_market_score']:.0f}/100")
    c2.metric("Median price", money(safe_float(market.get("median_price"))))
    c3.metric("Rent yield", pct_value(safe_float(market.get("gross_rent_yield")), 1))
    c4.metric("Hazard", f"{market['hazard_score']:.0f}/100")
    render_warnings(real_estate_warnings(market))
    st.caption(str(market.get("market_note", "")))
    with st.expander("Open market score basis and forecast", expanded=False):
        st.dataframe(
            [
                {"Pillar": "Price Momentum", "Score": round(market["price_momentum_score"], 1), "Weight": "15%"},
                {"Pillar": "Affordability", "Score": round(market["affordability_score"], 1), "Weight": "18%"},
                {"Pillar": "Inventory", "Score": round(market["inventory_score"], 1), "Weight": "14%"},
                {"Pillar": "Rental Yield", "Score": round(market["rental_score"], 1), "Weight": "18%"},
                {"Pillar": "Supply", "Score": round(market["supply_score"], 1), "Weight": "12%"},
                {"Pillar": "Employment", "Score": round(market["employment_score"], 1), "Weight": "15%"},
                {"Pillar": "Hazard", "Score": round(market["hazard_score"], 1), "Weight": "8%"},
            ],
            width="stretch",
            hide_index=True,
        )
        st.dataframe(
            [
                {
                    "Horizon": row["Horizon"],
                    "Low": round(safe_float(row["Low"])),
                    "Base": round(safe_float(row["Base"])),
                    "High": round(safe_float(row["High"])),
                    "Mid return %": round(safe_float(row["Mid return %"]), 1),
                }
                for row in real_estate_forecast(market)
            ],
            width="stretch",
            hide_index=True,
        )
    with st.expander("Property calculator", expanded=False):
        p1, p2, p3 = st.columns(3)
        with p1:
            purchase_price = st.number_input("Purchase price", min_value=0.0, value=float(market["median_price"]), step=5000.0)
            monthly_rent = st.number_input("Monthly rent", min_value=0.0, value=float(market["rent_estimate"]), step=50.0)
            down_payment_pct = st.number_input("Down payment %", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        with p2:
            mortgage_rate_pct = st.number_input("Mortgage rate %", min_value=0.0, max_value=20.0, value=6.5, step=0.1)
            loan_years = st.number_input("Loan years", min_value=1, max_value=40, value=30, step=1)
            property_tax_pct = st.number_input("Property tax %", min_value=0.0, max_value=10.0, value=1.05, step=0.05)
        with p3:
            insurance_monthly = st.number_input("Insurance / mo", min_value=0.0, value=180.0, step=25.0)
            hoa_monthly = st.number_input("HOA / mo", min_value=0.0, value=0.0, step=25.0)
            maintenance_pct = st.number_input("Maintenance %", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
            vacancy_pct = st.number_input("Vacancy %", min_value=0.0, max_value=50.0, value=5.0, step=1.0)
        property_result = property_calculator_result(
            purchase_price,
            monthly_rent,
            down_payment_pct,
            mortgage_rate_pct,
            int(loan_years),
            property_tax_pct,
            insurance_monthly,
            hoa_monthly,
            maintenance_pct,
            vacancy_pct,
        )
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Cash flow", signed_money(property_result["monthly_cash_flow"]))
        r2.metric("NOI", money(property_result["monthly_noi"]))
        r3.metric("Cap rate", pct_value(property_result["cap_rate"], 1))
        r4.metric("Break-even rent", money(property_result["break_even_rent"]))
    st.markdown("#### Direct Property Input")
    edited = st.data_editor(
        st.session_state.real_estate,
        num_rows="dynamic",
        width="stretch",
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
    if st.button("Save decision snapshot", width="stretch"):
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
        st.dataframe(st.session_state.decision_log, width="stretch", hide_index=True)
    else:
        st.info("No saved decision snapshots yet.")


def main() -> None:
    inject_styles()
    initialize_state()
    render_sidebar()

    profile = st.session_state.profile
    portfolio = build_portfolio(st.session_state.holdings)
    real_estate = build_real_estate(st.session_state.real_estate, st.session_state.selected_market_id)
    foundation = calculate_foundation(st.session_state.finance, portfolio, real_estate)
    objective_analysis = analyze_objectives(st.session_state.objectives)
    objective_summary = summarize_objectives(objective_analysis)
    goal = evaluate_goal(st.session_state.goal, foundation, objective_summary)
    stock_detail = enrich_stock(stock_by_symbol(st.session_state.selected_stock_symbol) or STOCK_UNIVERSE[0])
    reit_detail = enrich_reit(reit_by_symbol(st.session_state.selected_reit_symbol) or REIT_UNIVERSE[0])
    scenario_result = evaluate_scenario(foundation, portfolio, real_estate, st.session_state.scenario)
    resilience = evaluate_resilience(
        foundation,
        portfolio,
        real_estate,
        [
            *goal.get("warnings", []),
            *stock_warnings(stock_detail),
            *reit_warnings(reit_detail),
        ],
        scenario_result,
    )
    model = build_decision_model(foundation, goal, portfolio, real_estate, resilience)
    evidence = build_evidence(
        foundation,
        goal,
        portfolio,
        real_estate,
        resilience,
        objective_summary,
        stock_detail,
        reit_detail,
        scenario_result,
    )
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
        stock_detail,
        reit_detail,
        scenario_result,
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

    (
        overview,
        ontology_tab,
        foundation_tab,
        portfolio_tab,
        reit_tab,
        estate_tab,
        goals_tab,
        scenario_tab,
        evidence_tab,
        memory_tab,
    ) = st.tabs(
        [
            "Cockpit",
            "Ontology",
            "Foundation",
            "Portfolio",
            "REITs",
            "Real Estate",
            "Goals",
            "Scenario",
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
        st.dataframe(
            [
                {"Pillar": "Liquidity", "Score": round(foundation["liquidity_score"], 1), "Weight": "25%"},
                {"Pillar": "Debt", "Score": round(foundation["debt_score"], 1), "Weight": "25%"},
                {"Pillar": "Savings", "Score": round(foundation["savings_score"], 1), "Weight": "25%"},
                {"Pillar": "Goal", "Score": round(foundation["goal_score"], 1), "Weight": "15%"},
                {"Pillar": "Risk Capacity", "Score": round(foundation["risk_capacity_score"], 1), "Weight": "10%"},
            ],
            width="stretch",
            hide_index=True,
        )

    with portfolio_tab:
        render_portfolio_inputs()
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Portfolio value", money(portfolio.total_value))
        c2.metric("Gain/loss", signed_money(portfolio.gain_loss), percent(portfolio.gain_loss_pct))
        c3.metric("Top holding", percent(portfolio.top_weight))
        c4.metric("Top sector", portfolio.top_sector or "None", percent(portfolio.top_sector_weight))
        st.dataframe(
            [
                {"Pillar": "Weighted holdings", "Score": round(portfolio.weighted_score, 1), "Weight": "45%"},
                {"Pillar": "Concentration", "Score": round(portfolio.concentration_score, 1), "Weight": "25%"},
                {"Pillar": "Beta", "Score": round(portfolio.beta_score, 1), "Weight": "15%"},
                {"Pillar": "Performance", "Score": round(portfolio.performance_score, 1), "Weight": "15%"},
            ],
            width="stretch",
            hide_index=True,
        )
        render_warnings(portfolio.warnings)

    with reit_tab:
        render_reit_inputs(reit_detail)

    with estate_tab:
        render_real_estate_inputs()
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Property value", money(real_estate.total_value))
        c2.metric("Equity", money(real_estate.total_equity))
        c3.metric("Cash flow", signed_money(real_estate.monthly_cash_flow))
        c4.metric("Market score", f"{safe_float(real_estate.market.get('ly_market_score') if real_estate.market else 0):.0f}/100")
        render_warnings(real_estate.warnings)

    with goals_tab:
        render_goal_inputs(objective_analysis, objective_summary)
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Goal route", f"{goal['score']}/100", goal["label"])
        c2.metric("Objectives", f"{objective_summary['goal_count']}")
        c3.metric("Remaining gap", money(goal["gap"]))
        c4.metric("Monthly required", money(goal["monthly_required"]))

    with scenario_tab:
        render_scenario_inputs(scenario_result)

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

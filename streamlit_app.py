from __future__ import annotations

import math
from dataclasses import dataclass

import streamlit as st


st.set_page_config(
    page_title="LY-Scope Ver.2",
    page_icon="LY",
    layout="wide",
)


DEFAULT_FINANCE = {
    "monthly_income": 6500.0,
    "fixed_expense": 3400.0,
    "variable_expense": 1200.0,
    "debt_payment": 350.0,
    "cash": 24000.0,
    "debt": 9000.0,
    "runway_target": 6.0,
}

DEFAULT_HOLDINGS = [
    {
        "symbol": "MSFT",
        "company": "Microsoft",
        "sector": "Technology",
        "shares": 60.0,
        "purchase_price": 390.0,
        "price": 426.7,
        "pe": 32.2,
        "beta": 0.9,
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
        "pe": 28.4,
        "beta": 1.2,
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
        "pe": 45.5,
        "beta": 1.7,
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
        "pe": 12.6,
        "beta": 1.1,
        "momentum_6m": 6.8,
        "revenue_growth": 5.4,
        "margin_quality": 72.0,
        "debt_risk": 42.0,
    },
]


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def score_stock(row: dict) -> float:
    pe = float(row.get("pe", 0) or 0)
    beta = float(row.get("beta", 1) or 1)
    momentum = float(row.get("momentum_6m", 0) or 0)
    revenue_growth = float(row.get("revenue_growth", 0) or 0)
    margin_quality = float(row.get("margin_quality", 0) or 0)
    debt_risk = float(row.get("debt_risk", 0) or 0)
    value_score = clamp(95 - max(0, pe - 10) * 2)
    momentum_score = clamp(48 + momentum * 2.1)
    quality_score = clamp(margin_quality * 0.72 + revenue_growth * 1.2 - debt_risk * 0.18)
    risk_balance = clamp(92 - abs(beta - 1) * 28 - debt_risk * 0.22)
    return value_score * 0.25 + momentum_score * 0.25 + quality_score * 0.3 + risk_balance * 0.2


@dataclass
class PortfolioSnapshot:
    rows: list[dict]
    total_value: float
    total_cost: float
    gain_loss: float
    top_weight: float
    top_sector: str
    top_sector_weight: float
    weighted_score: float
    weighted_beta: float
    portfolio_score: int
    warnings: list[str]


def build_portfolio(rows: list[dict]) -> PortfolioSnapshot:
    clean_rows = []
    for row in rows:
        symbol = str(row.get("symbol", "")).strip().upper()
        if not symbol:
            continue
        shares = float(row.get("shares", 0) or 0)
        price = float(row.get("price", 0) or 0)
        purchase_price = float(row.get("purchase_price", 0) or 0)
        market_value = shares * price
        cost_basis = shares * purchase_price
        clean_rows.append(
            {
                **row,
                "symbol": symbol,
                "shares": shares,
                "price": price,
                "purchase_price": purchase_price,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "gain_loss": market_value - cost_basis,
                "score": score_stock(row),
                "beta": float(row.get("beta", 1) or 1),
            }
        )

    total_value = sum(row["market_value"] for row in clean_rows)
    total_cost = sum(row["cost_basis"] for row in clean_rows)

    for row in clean_rows:
        row["weight"] = row["market_value"] / total_value if total_value else 0

    top_weight = max([row["weight"] for row in clean_rows] or [0])
    sector_weights = {}
    for row in clean_rows:
        sector = str(row.get("sector") or "Saved Holding")
        sector_weights[sector] = sector_weights.get(sector, 0) + row["weight"]
    top_sector, top_sector_weight = max(
        sector_weights.items(),
        key=lambda item: item[1],
        default=("", 0),
    )
    weighted_score = (
        sum(row["score"] * row["market_value"] for row in clean_rows) / total_value
        if total_value
        else 50
    )
    weighted_beta = (
        sum(row["beta"] * row["market_value"] for row in clean_rows) / total_value
        if total_value
        else 1
    )
    return_pct = ((total_value - total_cost) / total_cost * 100) if total_cost else 0
    concentration_score = clamp(
        100 - max(0, top_weight - 0.25) * 150 - max(0, top_sector_weight - 0.5) * 100
    )
    beta_score = clamp(90 - max(0, weighted_beta - 1) * 42)
    performance_score = clamp(55 + return_pct * 1.2)
    portfolio_score = round(
        weighted_score * 0.45
        + concentration_score * 0.25
        + beta_score * 0.15
        + performance_score * 0.15
    )
    warnings = []
    if top_weight > 0.45:
        warnings.append("Top holding concentration is high.")
    if top_sector_weight > 0.62:
        warnings.append("Sector concentration is elevated.")
    if weighted_beta > 1.3:
        warnings.append("Portfolio beta can amplify volatility.")
    if weighted_score < 55:
        warnings.append("Weighted holding quality needs review.")
    if total_cost and total_value < total_cost * 0.9:
        warnings.append("Portfolio unrealized loss is greater than 10%.")

    return PortfolioSnapshot(
        rows=clean_rows,
        total_value=total_value,
        total_cost=total_cost,
        gain_loss=total_value - total_cost,
        top_weight=top_weight,
        top_sector=top_sector,
        top_sector_weight=top_sector_weight,
        weighted_score=weighted_score,
        weighted_beta=weighted_beta,
        portfolio_score=portfolio_score,
        warnings=warnings,
    )


def foundation_score(finance: dict, portfolio_value: float) -> dict:
    monthly_expenses = (
        finance["fixed_expense"] + finance["variable_expense"] + finance["debt_payment"]
    )
    cash_flow = finance["monthly_income"] - monthly_expenses
    savings_rate = cash_flow / finance["monthly_income"] if finance["monthly_income"] else 0
    runway = finance["cash"] / monthly_expenses if monthly_expenses else math.inf
    net_worth = finance["cash"] + portfolio_value - finance["debt"]
    debt_to_income = finance["debt"] / (finance["monthly_income"] * 12) if finance["monthly_income"] else 1
    emergency_score = clamp(runway / finance["runway_target"], 0, 1)
    cash_flow_score = clamp((savings_rate + 0.1) / 0.35, 0, 1)
    debt_score = clamp(1 - debt_to_income, 0, 1)
    net_worth_score = 1 if net_worth > 0 else 0.35
    score = round(
        (emergency_score * 0.35 + cash_flow_score * 0.3 + debt_score * 0.2 + net_worth_score * 0.15)
        * 100
    )
    band = "strong" if score >= 80 else "stable" if score >= 62 else "watch" if score >= 45 else "fragile"
    return {
        "score": score,
        "band": band,
        "monthly_expenses": monthly_expenses,
        "cash_flow": cash_flow,
        "savings_rate": savings_rate,
        "runway": runway,
        "net_worth": net_worth,
    }


def card(title: str, label: str, detail: str, tone: str) -> None:
    st.markdown(
        f"""
        <div class="signal-card {tone}">
          <div class="signal-title">{title}</div>
          <div class="signal-label">{label}</div>
          <div class="signal-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          .main .block-container { padding-top: 2rem; }
          .signal-card {
            border: 1px solid #d7dee8;
            border-top: 4px solid #2855b8;
            border-radius: 8px;
            padding: 16px;
            min-height: 148px;
            background: #fff;
          }
          .signal-card.strong { border-top-color: #16745f; }
          .signal-card.watch { border-top-color: #a46413; }
          .signal-card.fragile { border-top-color: #b33b3b; }
          .signal-title {
            color: #2855b8;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
          }
          .signal-label {
            margin-top: 18px;
            color: #20242a;
            font-size: 1.8rem;
            font-weight: 850;
          }
          .signal-detail {
            margin-top: 12px;
            color: #64707d;
            font-size: 0.9rem;
            line-height: 1.45;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    st.title("LY-Scope Ver.2")
    st.caption("Personal Decision Intelligence Application")

    if "finance" not in st.session_state:
        st.session_state.finance = DEFAULT_FINANCE.copy()
    if "holdings" not in st.session_state:
        st.session_state.holdings = [row.copy() for row in DEFAULT_HOLDINGS]

    finance = st.session_state.finance
    with st.sidebar:
        st.header("Finance")
        finance["monthly_income"] = st.number_input("Monthly income", min_value=0.0, step=100.0, value=float(finance["monthly_income"]))
        finance["fixed_expense"] = st.number_input("Fixed expense", min_value=0.0, step=100.0, value=float(finance["fixed_expense"]))
        finance["variable_expense"] = st.number_input("Variable expense", min_value=0.0, step=100.0, value=float(finance["variable_expense"]))
        finance["debt_payment"] = st.number_input("Debt payment", min_value=0.0, step=100.0, value=float(finance["debt_payment"]))
        finance["cash"] = st.number_input("Cash", min_value=0.0, step=500.0, value=float(finance["cash"]))
        finance["debt"] = st.number_input("Debt", min_value=0.0, step=500.0, value=float(finance["debt"]))
        finance["runway_target"] = st.number_input("Runway target months", min_value=1.0, max_value=24.0, step=1.0, value=float(finance["runway_target"]))

    portfolio = build_portfolio(st.session_state.holdings)
    foundation = foundation_score(finance, portfolio.total_value)
    risk_count = len(portfolio.warnings)
    direction = "On Route" if foundation["cash_flow"] >= 0 and risk_count == 0 else "Protect" if foundation["cash_flow"] >= 0 else "Re-route"
    crisis = "Clear" if risk_count == 0 else "Watch"

    col1, col2, col3 = st.columns(3)
    with col1:
        card(
            "Now",
            foundation["band"].title(),
            f"{foundation['score']}/100 foundation, {money(foundation['cash_flow'])} monthly cash flow.",
            foundation["band"],
        )
    with col2:
        card(
            "Direction",
            direction,
            f"Portfolio value feeds Finance: {money(portfolio.total_value)}.",
            "strong" if direction == "On Route" else "watch",
        )
    with col3:
        card(
            "Crisis",
            crisis,
            f"{risk_count} portfolio warning(s), beta {portfolio.weighted_beta:.2f}.",
            "strong" if crisis == "Clear" else "watch",
        )

    overview, portfolio_tab, evidence_tab, architecture_tab = st.tabs(
        ["Overview", "Portfolio", "Evidence", "Architecture"]
    )

    with overview:
        st.subheader("Current Situation")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Net worth", money(foundation["net_worth"]))
        c2.metric("Runway", f"{foundation['runway']:.1f} mo")
        c3.metric("Portfolio score", f"{portfolio.portfolio_score}/100")
        c4.metric("Top holding", percent(portfolio.top_weight))

    with portfolio_tab:
        st.subheader("Portfolio Input")
        edited_rows = st.data_editor(
            st.session_state.holdings,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "symbol": st.column_config.TextColumn("Symbol", required=True),
                "shares": st.column_config.NumberColumn("Shares", min_value=0.0),
                "purchase_price": st.column_config.NumberColumn("Cost / share", min_value=0.0),
                "price": st.column_config.NumberColumn("Current price", min_value=0.0),
            },
        )
        st.session_state.holdings = edited_rows
        st.subheader("Portfolio Score")
        st.progress(portfolio.portfolio_score / 100)
        st.write(
            {
                "total_value": money(portfolio.total_value),
                "gain_loss": money(portfolio.gain_loss),
                "top_sector": portfolio.top_sector,
                "top_sector_weight": percent(portfolio.top_sector_weight),
            }
        )

    with evidence_tab:
        st.subheader("Signals")
        signals = [
            ("Foundation", foundation["score"], foundation["band"]),
            ("Portfolio", portfolio.portfolio_score, f"{len(portfolio.rows)} holding(s)"),
            ("Concentration", round(100 - portfolio.top_weight * 100), f"top holding {percent(portfolio.top_weight)}"),
            ("Risk", 100 - risk_count * 15, crisis),
        ]
        for name, score, detail in signals:
            st.metric(name, f"{score}/100", detail)
        if portfolio.warnings:
            st.warning("\n".join(portfolio.warnings))
        else:
            st.success("No major portfolio warnings.")

    with architecture_tab:
        st.subheader("Core Decision Architecture")
        st.code("User -> Data -> Model -> Evidence -> AI Interpretation -> Decision -> Memory")
        st.write(
            "This Streamlit entrypoint is a deployable compatibility layer. "
            "The main Ver.2 HTML/JavaScript app remains in index.html and src/."
        )


if __name__ == "__main__":
    main()


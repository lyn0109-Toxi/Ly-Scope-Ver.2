from __future__ import annotations

from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from personal_finance_engine import PersonalFinanceProfile, calculate_personal_finance

KO_TRANSLATIONS = {
    "Mobile Finance Readiness": "모바일 재무 준비도",
    "Start here before portfolio decisions. These cards compress cash flow, liquidity, debt pressure, and risk capacity into a phone-first view.": "포트폴리오 결정을 내리기 전에 여기서 시작하세요. 이 카드는 현금흐름, 유동성, 부채 압박, 위험 감당력을 모바일 중심으로 요약합니다.",
    "Health": "건강도",
    "Financial score": "재무 점수",
    "Planning score": "계획 점수",
    "Surplus": "잉여 현금",
    "Monthly cash flow": "월 현금흐름",
    "Reserve": "비상자금",
    "Emergency fund": "비상자금",
    "Debt": "부채",
    "Debt-to-income": "소득 대비 부채",
    "Savings": "저축",
    "Savings rate": "저축률",
    "Priority": "우선순위",
    "Next review point": "다음 점검 지점",
    "Build liquidity first": "유동성부터 확보",
    "Review portfolio risk": "포트폴리오 위험 점검",
    "Ready for scenario stress": "시나리오 테스트 가능",
    "Personal Finance": "개인 재무",
    "Understand liquidity, debt pressure, savings behavior, goals, and investment risk capacity before making portfolio decisions.": "포트폴리오 결정을 내리기 전에 유동성, 부채 압박, 저축 습관, 목표, 투자 위험 감당력을 이해하세요.",
    "Educational prototype only. Do not enter sensitive personal financial information. This module does not provide financial, tax, legal, or investment advice.": "교육용 프로토타입입니다. 민감한 개인 금융 정보를 입력하지 마세요. 이 모듈은 금융, 세무, 법률, 투자 조언을 제공하지 않습니다.",
    "Financial Inputs": "재무 입력",
    "Apply Situation Calculation": "상황 계산 다시 적용",
    "Calculation Applied": "계산 반영 완료",
    "Latest inputs are reflected in the visual result, scores, and AI Coach context.": "최신 입력값이 시각 결과, 점수, AI Coach 기준에 반영되어 있습니다.",
    "Inputs changed. Click Apply Situation Calculation to refresh the visual result, scores, and AI Coach context.": "입력값이 바뀌었습니다. 시각 결과, 점수, AI Coach 기준을 새로 반영하려면 상황 계산 다시 적용을 누르세요.",
    "Life Stage Setup": "라이프 단계 설정",
    "Display Currency": "표시 통화",
    "Runway Target Months": "목표 생존기간",
    "Study Months Remaining": "남은 학업 기간",
    "Use No-Income Study Example": "무소득 학업 예시 적용",
    "No-income mode turns on automatically when monthly income is 0 and monthly expenses are above 0.": "월수입이 0이고 월지출이 있으면 무소득 모드가 자동으로 켜집니다.",
    "Monthly Income": "월수입",
    "Monthly Savings Goal": "월 저축 목표",
    "Current Investment Risk Score": "현재 투자 위험 점수",
    "Fixed Expenses": "고정지출",
    "Variable Expenses": "변동지출",
    "Monthly Debt Payment": "월 부채 상환액",
    "Cash / Savings": "현금 / 저축",
    "Taxable Investments": "과세 투자자산",
    "Retirement Accounts": "은퇴 계좌",
    "Real Estate Value": "부동산 가치",
    "Credit Card Debt": "신용카드 부채",
    "Student Loan": "학자금 대출",
    "Auto Loan": "자동차 대출",
    "Mortgage": "모기지",
    "Goal": "목표",
    "Target Goal Amount": "목표 금액",
    "Current Goal Savings": "현재 목표 저축액",
    "Financial Snapshot": "재무 스냅샷",
    "Net Worth": "순자산",
    "Monthly Surplus": "월 잉여 현금",
    "Financial Health Score": "재무 건강 점수",
    "Planning Health Score": "계획 건강 점수",
    "Emergency Fund": "비상자금",
    "Study Runway Gap": "학업 생존기간 차이",
    "Investment Exposure": "투자 노출도",
    "Cash Buffer": "현금 완충력",
    "Visual Situation Map": "시각 상황 지도",
    "Cash Runway Under Expense Stress": "지출 변화별 현금 생존기간",
    "Capital After Stock Drawdown": "주식 하락 후 자본",
    "Current": "현재",
    "Expense +20%": "지출 +20%",
    "Expense +50%": "지출 +50%",
    "Remaining Capital": "남은 자본",
    "Stock Drawdown": "주식 하락",
    "Health Score Breakdown": "건강 점수 분해",
    "Liquidity": "유동성",
    "Goal Progress": "목표 진행률",
    "Risk Capacity": "위험 감당력",
    "Runway Readiness": "생존기간 준비도",
    "Investment Exposure Balance": "투자 노출 균형",
    "Decision-Support Insights": "의사결정 지원 인사이트",
    "No major warning signals from the current inputs.": "현재 입력값 기준 주요 경고 신호가 없습니다.",
    "Investment Readiness": "투자 준비도",
    "Personal Finance answers whether the user can afford investment risk. Stock and REIT analysis answer which assets may fit the user's goals and risk capacity.": "개인 재무는 사용자가 투자 위험을 감당할 수 있는지 답합니다. 주식과 REIT 분석은 어떤 자산이 사용자의 목표와 위험 감당력에 맞을 수 있는지 보여줍니다.",
}

FINANCE_DEFAULTS = {
    "pf_display_currency": "USD",
    "pf_monthly_income": 8000.0,
    "pf_monthly_savings_goal": 1200.0,
    "pf_investment_risk_score": 45,
    "pf_fixed_expenses": 2500.0,
    "pf_variable_expenses": 1500.0,
    "pf_monthly_debt_payment": 1600.0,
    "pf_cash_savings": 30000.0,
    "pf_taxable_investments": 45000.0,
    "pf_retirement_accounts": 90000.0,
    "pf_real_estate_value": 300000.0,
    "pf_credit_card_debt": 0.0,
    "pf_student_loan": 12000.0,
    "pf_auto_loan": 8000.0,
    "pf_mortgage": 220000.0,
    "pf_target_goal_amount": 60000.0,
    "pf_current_goal_savings": 30000.0,
    "pf_runway_target_months": 6.0,
    "pf_study_months_remaining": 0.0,
}


def tr(text: str) -> str:
    if st.session_state.get("app_language") == "ko":
        return KO_TRANSLATIONS.get(text, text)
    return text


def ensure_finance_defaults() -> None:
    for key, value in FINANCE_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def apply_no_income_study_example() -> None:
    st.session_state.update(
        {
            "pf_display_currency": "KRW",
            "pf_monthly_income": 0.0,
            "pf_monthly_savings_goal": 0.0,
            "pf_investment_risk_score": 67,
            "pf_fixed_expenses": 3_000_000.0,
            "pf_variable_expenses": 0.0,
            "pf_monthly_debt_payment": 0.0,
            "pf_cash_savings": 100_000_000.0,
            "pf_taxable_investments": 200_000_000.0,
            "pf_retirement_accounts": 0.0,
            "pf_real_estate_value": 0.0,
            "pf_credit_card_debt": 0.0,
            "pf_student_loan": 0.0,
            "pf_auto_loan": 0.0,
            "pf_mortgage": 0.0,
            "pf_target_goal_amount": 300_000_000.0,
            "pf_current_goal_savings": 300_000_000.0,
            "pf_runway_target_months": 24.0,
            "pf_study_months_remaining": 24.0,
            "_personal_finance_force_apply": True,
        }
    )


def money(value: float) -> str:
    if st.session_state.get("pf_display_currency") == "KRW":
        return f"₩{value:,.0f}"
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def score_color(score: float) -> str:
    if score >= 70:
        return "#16a34a"
    if score >= 45:
        return "#d97706"
    return "#dc2626"


def pf_metric(label: str, value: str, color: str = "#0f172a") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(str(label))}</div>
            <div class="metric-value" style="color:{escape(str(color))};">{escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def finance_profile_signature(profile: PersonalFinanceProfile) -> tuple[tuple[str, float], ...]:
    return tuple(
        (key, round(float(value), 6))
        for key, value in sorted(profile.__dict__.items())
    )


def store_personal_finance_calculation(profile: PersonalFinanceProfile) -> dict[str, object]:
    result = calculate_personal_finance(profile)
    st.session_state["last_personal_finance_profile"] = profile.__dict__.copy()
    st.session_state["last_personal_finance_result"] = result
    st.session_state["last_personal_finance_signature"] = finance_profile_signature(profile)
    return result


def applied_personal_finance_profile(fallback: PersonalFinanceProfile) -> PersonalFinanceProfile:
    stored_profile = st.session_state.get("last_personal_finance_profile")
    if isinstance(stored_profile, dict):
        try:
            return PersonalFinanceProfile(**stored_profile)
        except TypeError:
            return fallback
    return fallback


def mobile_finance_deck(result: dict[str, float | list[str]]) -> None:
    health = float(result.get("planning_health_score") or result["financial_health_score"])
    surplus = float(result["monthly_surplus"])
    emergency = float(result["emergency_months"])
    dti = float(result["debt_to_income"])
    savings = float(result["savings_rate"])
    risk_capacity = float(result["risk_capacity_score"])
    surplus_class = "mobile-positive" if surplus >= 0 else "mobile-negative"
    priority = "Build liquidity first"
    if emergency >= 3 and surplus > 0 and dti <= 0.36:
        priority = "Review portfolio risk"
    if health >= 70 and risk_capacity >= 70:
        priority = "Ready for scenario stress"

    st.markdown(
        f"""
        <div class="mobile-only-deck">
            <div class="mobile-focus-card">
                <h3>{escape(tr('Mobile Finance Readiness'))}</h3>
                <p>{escape(tr('Start here before portfolio decisions. These cards compress cash flow, liquidity, debt pressure, and risk capacity into a phone-first view.'))}</p>
            </div>
            <div class="mobile-card-grid">
                <div class="mobile-card"><div class="eyebrow">{escape(tr('Health'))}</div><div class="value">{health:.1f}/100</div><span class="label">{escape(tr('Planning score'))}</span></div>
                <div class="mobile-card"><div class="eyebrow">{escape(tr('Surplus'))}</div><div class="value {surplus_class}">{escape(money(surplus))}</div><span class="label">{escape(tr('Monthly cash flow'))}</span></div>
                <div class="mobile-card"><div class="eyebrow">{escape(tr('Reserve'))}</div><div class="value">{emergency:.1f} mo</div><span class="label">{escape(tr('Emergency fund'))}</span></div>
                <div class="mobile-card"><div class="eyebrow">{escape(tr('Debt'))}</div><div class="value">{dti * 100:.1f}%</div><span class="label">{escape(tr('Debt-to-income'))}</span></div>
                <div class="mobile-card"><div class="eyebrow">{escape(tr('Savings'))}</div><div class="value">{savings * 100:.1f}%</div><span class="label">{escape(tr('Savings rate'))}</span></div>
                <div class="mobile-card"><div class="eyebrow">{escape(tr('Priority'))}</div><div class="value">{escape(tr(priority))}</div><span class="label">{escape(tr('Next review point'))}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_visual_situation_map(profile: PersonalFinanceProfile, result: dict[str, float | list[str]]) -> None:
    living_expenses = profile.fixed_expenses + profile.variable_expenses
    total_debt = float(result["total_debt"])
    total_assets = float(result["total_assets"])
    if total_assets <= 0:
        return

    st.subheader(tr("Visual Situation Map"))
    expense_scenarios = [
        (tr("Current"), living_expenses),
        (tr("Expense +20%"), living_expenses * 1.20),
        (tr("Expense +50%"), living_expenses * 1.50),
    ]
    runway_rows = [
        {
            "Scenario": label,
            "Months": profile.cash_savings / expense if expense > 0 else 0,
            "Target": float(result["required_runway_months"]),
        }
        for label, expense in expense_scenarios
    ]
    runway_data = pd.DataFrame(runway_rows)
    runway_bars = (
        alt.Chart(runway_data)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("Scenario:N", sort=None, title=None),
            y=alt.Y("Months:Q", title="Months"),
            color=alt.Color("Scenario:N", legend=None),
            tooltip=["Scenario", alt.Tooltip("Months:Q", format=".1f"), alt.Tooltip("Target:Q", format=".1f")],
        )
    )
    runway_target = (
        alt.Chart(runway_data)
        .mark_rule(color="#334155", strokeDash=[6, 5])
        .encode(y="Target:Q")
    )

    drawdown_rows = []
    for drawdown in [0, 10, 20, 30, 40, 50]:
        remaining = (
            profile.cash_savings
            + profile.taxable_investments * (1 - drawdown / 100)
            + profile.retirement_accounts
            + profile.real_estate_value
            - total_debt
        )
        drawdown_rows.append(
            {
                "Stock Drawdown": f"-{drawdown}%",
                "Drawdown": drawdown,
                "Remaining Capital": max(remaining, 0),
            }
        )
    drawdown_data = pd.DataFrame(drawdown_rows)
    drawdown_chart = (
        alt.Chart(drawdown_data)
        .mark_line(point=True, strokeWidth=4)
        .encode(
            x=alt.X("Drawdown:Q", title=tr("Stock Drawdown")),
            y=alt.Y("Remaining Capital:Q", title=tr("Remaining Capital")),
            color=alt.value("#7c3aed"),
            tooltip=["Stock Drawdown", alt.Tooltip("Remaining Capital:Q", format=",.0f")],
        )
    )

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.caption(tr("Cash Runway Under Expense Stress"))
        st.altair_chart((runway_bars + runway_target).properties(height=280), width="stretch")
    with chart_cols[1]:
        st.caption(tr("Capital After Stock Drawdown"))
        st.altair_chart(drawdown_chart.properties(height=280), width="stretch")


def render_personal_finance() -> None:
    ensure_finance_defaults()
    st.markdown(
        f"""
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">{escape(tr('Personal Finance'))}</h1>
            <div class="hero-muted">{escape(tr('Understand liquidity, debt pressure, savings behavior, goals, and investment risk capacity before making portfolio decisions.'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        tr(
            "Educational prototype only. Do not enter sensitive personal financial information. This module does not provide financial, tax, legal, or investment advice."
        )
    )
    mobile_summary_slot = st.container()

    st.subheader(tr("Life Stage Setup"))
    preset_cols = st.columns([1, 2])
    with preset_cols[0]:
        if st.button(tr("Use No-Income Study Example"), width="stretch"):
            apply_no_income_study_example()
            st.rerun()
    with preset_cols[1]:
        st.caption(
            tr(
                "No-income mode turns on automatically when monthly income is 0 and monthly expenses are above 0."
            )
        )

    stage_cols = st.columns(3)
    with stage_cols[0]:
        st.selectbox(tr("Display Currency"), ["USD", "KRW"], key="pf_display_currency")
    with stage_cols[1]:
        runway_target_months = st.number_input(
            tr("Runway Target Months"), min_value=1.0, step=1.0, key="pf_runway_target_months"
        )
    with stage_cols[2]:
        study_months_remaining = st.number_input(
            tr("Study Months Remaining"), min_value=0.0, step=1.0, key="pf_study_months_remaining"
        )

    st.subheader(tr("Financial Inputs"))
    income_col, expense_col, asset_col = st.columns(3)
    with income_col:
        monthly_income = st.number_input(tr("Monthly Income"), min_value=0.0, step=100.0, key="pf_monthly_income")
        monthly_savings_goal = st.number_input(tr("Monthly Savings Goal"), min_value=0.0, step=50.0, key="pf_monthly_savings_goal")
        investment_risk_score = st.slider(tr("Current Investment Risk Score"), 0, 100, key="pf_investment_risk_score")

    with expense_col:
        fixed_expenses = st.number_input(tr("Fixed Expenses"), min_value=0.0, step=100.0, key="pf_fixed_expenses")
        variable_expenses = st.number_input(tr("Variable Expenses"), min_value=0.0, step=100.0, key="pf_variable_expenses")
        monthly_debt_payment = st.number_input(tr("Monthly Debt Payment"), min_value=0.0, step=100.0, key="pf_monthly_debt_payment")

    with asset_col:
        cash_savings = st.number_input(tr("Cash / Savings"), min_value=0.0, step=500.0, key="pf_cash_savings")
        taxable_investments = st.number_input(tr("Taxable Investments"), min_value=0.0, step=500.0, key="pf_taxable_investments")
        retirement_accounts = st.number_input(tr("Retirement Accounts"), min_value=0.0, step=500.0, key="pf_retirement_accounts")
        real_estate_value = st.number_input(tr("Real Estate Value"), min_value=0.0, step=1000.0, key="pf_real_estate_value")

    debt_col, goal_col = st.columns(2)
    with debt_col:
        st.subheader(tr("Debt"))
        credit_card_debt = st.number_input(tr("Credit Card Debt"), min_value=0.0, step=100.0, key="pf_credit_card_debt")
        student_loan = st.number_input(tr("Student Loan"), min_value=0.0, step=500.0, key="pf_student_loan")
        auto_loan = st.number_input(tr("Auto Loan"), min_value=0.0, step=500.0, key="pf_auto_loan")
        mortgage = st.number_input(tr("Mortgage"), min_value=0.0, step=1000.0, key="pf_mortgage")

    with goal_col:
        st.subheader(tr("Goal"))
        target_goal_amount = st.number_input(tr("Target Goal Amount"), min_value=1.0, step=1000.0, key="pf_target_goal_amount")
        current_goal_savings = st.number_input(tr("Current Goal Savings"), min_value=0.0, step=500.0, key="pf_current_goal_savings")

    profile = PersonalFinanceProfile(
        monthly_income=monthly_income,
        fixed_expenses=fixed_expenses,
        variable_expenses=variable_expenses,
        cash_savings=cash_savings,
        taxable_investments=taxable_investments,
        retirement_accounts=retirement_accounts,
        real_estate_value=real_estate_value,
        credit_card_debt=credit_card_debt,
        student_loan=student_loan,
        auto_loan=auto_loan,
        mortgage=mortgage,
        monthly_debt_payment=monthly_debt_payment,
        monthly_savings_goal=monthly_savings_goal,
        target_goal_amount=target_goal_amount,
        current_goal_savings=current_goal_savings,
        investment_risk_score=investment_risk_score,
        runway_target_months=runway_target_months,
        study_months_remaining=study_months_remaining,
    )
    current_signature = finance_profile_signature(profile)
    calculation_missing = (
        "last_personal_finance_result" not in st.session_state
        or "last_personal_finance_signature" not in st.session_state
    )
    force_apply = bool(st.session_state.pop("_personal_finance_force_apply", False))
    if calculation_missing or force_apply:
        store_personal_finance_calculation(profile)

    control_cols = st.columns([2.3, 1])
    with control_cols[1]:
        apply_clicked = st.button(
            tr("Apply Situation Calculation"),
            key="apply_situation_calculation",
            type="primary",
            width="stretch",
        )
    if apply_clicked:
        store_personal_finance_calculation(profile)

    applied_signature = st.session_state.get("last_personal_finance_signature")
    has_pending_inputs = current_signature != applied_signature
    with control_cols[0]:
        if has_pending_inputs:
            st.warning(
                tr(
                    "Inputs changed. Click Apply Situation Calculation to refresh the visual result, scores, and AI Coach context."
                )
            )
        elif apply_clicked:
            st.success(tr("Calculation Applied"))
        else:
            st.caption(
                tr(
                    "Latest inputs are reflected in the visual result, scores, and AI Coach context."
                )
            )

    result = st.session_state.get("last_personal_finance_result") or store_personal_finance_calculation(profile)
    applied_profile = applied_personal_finance_profile(profile)

    with mobile_summary_slot:
        mobile_finance_deck(result)

    st.subheader(tr("Financial Snapshot"))
    c1, c2, c3 = st.columns(3)
    with c1:
        pf_metric(tr("Net Worth"), money(float(result["net_worth"])))
    with c2:
        pf_metric(
            tr("Monthly Surplus"),
            money(float(result["monthly_surplus"])),
            "#16a34a" if float(result["monthly_surplus"]) >= 0 else "#dc2626",
        )
    with c3:
        health_key = "planning_health_score" if result.get("no_income_mode") else "financial_health_score"
        health_label = tr("Planning Health Score") if result.get("no_income_mode") else tr("Financial Health Score")
        pf_metric(
            health_label,
            f"{float(result[health_key]):.1f}/100",
            score_color(float(result[health_key])),
        )

    c4, c5, c6, c7 = st.columns(4)
    with c4:
        pf_metric(tr("Emergency Fund"), f"{float(result['emergency_months']):.1f} months")
    with c5:
        pf_metric(tr("Savings Rate"), percent(float(result["savings_rate"])))
    with c6:
        pf_metric(tr("Debt-to-Income"), percent(float(result["debt_to_income"])))
    with c7:
        pf_metric(tr("Investment Exposure"), percent(float(result["investment_exposure_ratio"])))

    if result.get("no_income_mode"):
        gap_cols = st.columns(3)
        with gap_cols[0]:
            pf_metric(tr("Study Runway Gap"), f"{float(result['runway_gap_months']):+.1f} months")
        with gap_cols[1]:
            pf_metric(tr("Cash Buffer"), percent(float(result["cash_to_assets_ratio"])))
        with gap_cols[2]:
            pf_metric(tr("Risk Capacity"), f"{float(result['risk_capacity_score']):.1f}/100")

    render_visual_situation_map(applied_profile, result)

    st.subheader(tr("Health Score Breakdown"))
    scores = pd.DataFrame(
        [
            {"Dimension": tr("Liquidity"), "Score": result["liquidity_score"]},
            {"Dimension": tr("Debt"), "Score": result["debt_score"]},
            {"Dimension": tr("Savings"), "Score": result["savings_score"]},
            {"Dimension": tr("Goal Progress"), "Score": result["goal_score"]},
            {"Dimension": tr("Risk Capacity"), "Score": result["risk_capacity_score"]},
            {"Dimension": tr("Runway Readiness"), "Score": result["runway_readiness_score"]},
            {"Dimension": tr("Investment Exposure Balance"), "Score": result["investment_exposure_score"]},
        ]
    )
    chart = (
        alt.Chart(scores)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("Dimension:N", sort=None),
            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Dimension:N", legend=None),
            tooltip=["Dimension", alt.Tooltip("Score:Q", format=".1f")],
        )
        .properties(height=330)
    )
    st.altair_chart(chart, width="stretch")

    st.subheader(tr("Decision-Support Insights"))
    insights = result["insights"]
    if isinstance(insights, list) and insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info(tr("No major warning signals from the current inputs."))

    st.subheader(tr("Investment Readiness"))
    st.write(
        tr(
            "Personal Finance answers whether the user can afford investment risk. Stock and REIT analysis answer which assets may fit the user's goals and risk capacity."
        )
    )

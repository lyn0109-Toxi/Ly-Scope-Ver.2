"""Deterministic, assumption-based savings projections for a single goal."""

from datetime import date, timedelta
import math


def months_until(start: date, deadline: date) -> int:
    if deadline <= start:
        return 0
    return (deadline.year - start.year) * 12 + deadline.month - start.month + int(deadline.day > start.day)


def project_goal(current: float, monthly: float, target: float, months: int,
                 annual_return: float = 0.0, annual_drag: float = 0.0) -> dict:
    values = (current, monthly, target, annual_return, annual_drag)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Inputs must be finite.")
    if current < 0 or monthly < 0 or target <= 0 or months < 1 or months > 1200:
        raise ValueError("Enter non-negative savings, a positive target and 1-1200 months.")
    net = (annual_return - annual_drag) / 100
    if annual_drag < 0 or not -1 < net <= 1:
        raise ValueError("Net annual return must be greater than -100% and at most 100%.")
    rate = math.expm1(math.log1p(net) / 12)
    growth = math.exp(months * math.log1p(rate))
    annuity = months if abs(rate) < 1e-12 else math.expm1(months * math.log1p(rate)) / rate
    projected = current * growth + monthly * annuity
    required = max(0.0, (target - current * growth) / annuity)
    balance = current
    path = [{"Month": 0, "Projected savings": balance, "Target": target}]
    for month in range(1, months + 1):
        balance = balance * (1 + rate) + monthly
        path.append({"Month": month, "Projected savings": balance, "Target": target})
    return {"projected": projected, "gap": projected - target, "required_monthly": required,
            "on_track": projected >= target, "net_return": net * 100, "months": months,
            "path": path}


def render_goal_planner(language: str) -> None:
    import altair as alt
    import pandas as pd
    import streamlit as st

    def text(en, ko):
        return ko if language == "ko" else en

    today = date.today()
    defaults = {
        "goal_name": "", "goal_currency": "USD", "goal_target": 0.0,
        "goal_current": 0.0, "goal_monthly": 0.0, "goal_return": 0.0,
        "goal_drag": 0.0, "goal_deadline": today + timedelta(days=1826),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    with st.form("goal_plan_form"):
        left, right = st.columns(2)
        with left:
            st.text_input(text("Goal name", "목표 이름"), key="goal_name",
                          placeholder=text("Home down payment", "주택 계약금 마련"))
            st.selectbox(text("Goal currency", "목표 통화"), ["USD", "KRW"], key="goal_currency")
            st.number_input(text("Target amount", "목표 금액"), min_value=0.0,
                            step=1000.0, key="goal_target")
            st.number_input(text("Savings allocated to this goal", "이 목표에 배정한 현재 자금"),
                            min_value=0.0, step=500.0, key="goal_current")
        with right:
            st.date_input(text("Target date", "목표 날짜"), key="goal_deadline",
                          min_value=today, max_value=today + timedelta(days=36525))
            st.number_input(text("Monthly contribution", "매월 적립액"), min_value=0.0,
                            step=100.0, key="goal_monthly")
            st.number_input(text("Assumed annual return (%)", "연 예상수익률 (%)"),
                            min_value=-80.0, max_value=50.0, step=0.5, key="goal_return")
            st.number_input(text("Annual tax / fee drag (%p)", "연 세금·비용 차감 가정 (%p)"),
                            min_value=0.0, max_value=15.0, step=0.1, key="goal_drag")
        submitted = st.form_submit_button(text("Calculate goal outlook", "목표 달성 전망 계산"),
                                          type="primary", icon=":material/calculate:")
    if submitted:
        months = months_until(today, st.session_state.goal_deadline)
        try:
            result = project_goal(st.session_state.goal_current, st.session_state.goal_monthly,
                                  st.session_state.goal_target, months,
                                  st.session_state.goal_return, st.session_state.goal_drag)
            st.session_state.goal_plan = {"name": st.session_state.goal_name,
                "currency": st.session_state.goal_currency, "target": st.session_state.goal_target,
                "current": st.session_state.goal_current, "monthly": st.session_state.goal_monthly,
                "annual_return": st.session_state.goal_return, "annual_drag": st.session_state.goal_drag,
                "deadline": st.session_state.goal_deadline.isoformat(), "calculated_at": today.isoformat(),
                "result": result}
            st.rerun()
        except ValueError:
            st.error(text("Enter a target above zero and a future target date.", "0보다 큰 목표 금액과 미래의 목표 날짜를 입력해 주세요."))
            return
    plan = st.session_state.get("goal_plan")
    if not plan:
        st.info(text("No goal calculation yet.", "아직 계산한 재무 목표가 없습니다."))
        return
    result = plan["result"]
    sign = "₩" if plan["currency"] == "KRW" else "$"
    money = lambda v: f"{'-' if v < 0 else ''}{sign}{abs(v):,.0f}"
    st.subheader(plan["name"] or text("Goal outlook", "목표 달성 전망"))
    st.caption(f"{plan['calculated_at']} · {plan['deadline']} · {plan['currency']}")
    cols = st.columns(3)
    cols[0].metric(text("Projected amount", "목표 시점 예상 자금"), money(result["projected"]))
    cols[1].metric(text("Surplus / shortfall", "목표 대비 초과·부족액"), money(result["gap"]))
    cols[2].metric(text("Required monthly saving", "필요한 월 적립액"), money(result["required_monthly"]))
    if result["on_track"]:
        st.success(text("On track under these assumptions.", "입력한 가정이 유지되면 목표에 도달할 전망입니다."))
    else:
        st.warning(text("Projected savings fall short of the target.", "현재 가정에서는 목표 금액에 미달할 전망입니다."))
    frame = pd.DataFrame(result["path"])
    chart = alt.Chart(frame).transform_fold(["Projected savings", "Target"], as_=["Series", "Amount"])
    chart = chart.mark_line(strokeWidth=2).encode(
        x=alt.X("Month:Q", title=text("Months from calculation", "계산일로부터 경과 개월")),
        y=alt.Y("Amount:Q", title=plan["currency"]),
        color=alt.Color("Series:N", scale=alt.Scale(domain=["Projected savings", "Target"],
                                                   range=["#0f766e", "#b7791f"]),
                        legend=alt.Legend(title=None, labelExpr="datum.label === 'Target' ? '목표 금액' : '예상 자금'" if language == "ko" else "datum.label")),
        tooltip=[alt.Tooltip("Month:Q", title=text("Month", "경과 개월")),
                 alt.Tooltip("Amount:Q", title=text("Amount", "금액"), format=",.0f")])
    st.altair_chart(chart.properties(height=260), width="stretch")
    rows = []
    for label, adjustment in [(text("Lower return", "수익률 하락"), -3),
                               (text("Base case", "기준 가정"), 0),
                               (text("Higher return", "수익률 상승"), 3)]:
        estimate = project_goal(plan["current"], plan["monthly"], plan["target"], result["months"],
                                plan["annual_return"] + adjustment, plan["annual_drag"])
        rows.append({text("Scenario", "시나리오"): label,
                     text("Net annual return", "연 순수익률 가정"): f"{estimate['net_return']:.1f}%",
                     text("Projected amount", "예상 자금"): money(estimate["projected"]),
                     text("Surplus / shortfall", "초과·부족액"): money(estimate["gap"])})
    st.dataframe(rows, hide_index=True, width="stretch")
    with st.expander(text("Calculation evidence", "계산 근거 및 한계")):
        st.latex(r"FV=P(1+r)^n+C\frac{(1+r)^n-1}{r}")
        st.write(text(
            "P: current allocated savings; C: month-end contribution; n: months; r: monthly compound rate from the assumed net annual return. At zero return, FV = P + C × n.",
            "P는 현재 배정 자금, C는 매월 말 적립액, n은 개월 수, r은 연 순수익률에서 환산한 월 복리 수익률입니다. 수익률이 0이면 예상 자금 = 현재 자금 + 월 적립액 × 개월 수입니다."))
        st.write(text(
            "The horizon rounds up to whole months. These are nominal, fixed-return estimates, not probabilities or guarantees. Tax/fee drag is a user assumption, not an account-specific tax calculation. Inflation, withdrawals and changing returns are not modeled. Goal savings are separate from the asset total and are not added again.",
            "기간은 월 단위로 올림합니다. 명목금액·고정수익률 추정이며 달성 확률이나 수익 보장이 아닙니다. 세금·비용은 사용자가 정한 차감 가정이며 계좌별 세법 계산이 아닙니다. 물가, 인출, 수익률 변동은 반영하지 않습니다. 목표 배정액은 총자산에 중복 가산하지 않습니다."))
    st.caption(text("Goal data is held in this session only.", "목표 정보는 현재 접속 세션에서만 유지됩니다."))

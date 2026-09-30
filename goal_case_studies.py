"""Read-only fictional goal cases, isolated from the user's financial inputs."""

from decimal import Decimal, localcontext
import json
from pathlib import Path

from goal_planning import goal_cashflow_message, project_goal


CASE_LABELS = {
    "G01": ("Harin", "Emergency fund", "비상자금", "Employed, starting a career", "사회초년 직장인"),
    "G02": ("Minjun", "First home deposit", "주택 계약금", "Preparing for a first home", "첫 주택을 준비하는 직장인"),
    "G03": ("Seoyeon", "Retirement savings", "은퇴자금", "Saving before retirement", "장기 은퇴를 준비하는 관리자"),
    "G04": ("Doyun", "Child's education", "자녀 교육비", "Parent saving for college", "자녀 교육비를 준비하는 학부모"),
    "G05": ("Jia", "Car purchase", "차량 구매", "Saving for a commuting car", "출퇴근용 차량이 필요한 직장인"),
    "G06": ("Jihoon", "Graduate studies", "대학원 유학", "Preparing to study abroad", "유학을 준비하는 직장인"),
    "G07": ("Naeun", "Business launch", "창업", "Freelancer planning a business", "창업을 준비하는 프리랜서"),
    "G08": ("Hyunwoo", "Career break", "휴직 생활비", "Career break without income", "소득이 없는 휴직자"),
    "G09": ("Subin", "Relocation", "해외 이주", "USD income, KRW goal", "달러 소득과 원화 목표를 가진 이주 예정자"),
    "G10": ("Taeo", "Professional certification", "직무 자격증", "Certification while employed", "재직 중 자격증을 준비하는 직장인"),
}

CASE_NOTES = {
    "G01": ("With zero return, contributions exactly close the gap.", "수익률 0%에서도 계획한 적립으로 목표액에 정확히 도달합니다."),
    "G02": ("The target is not met at the current contribution. Required saving remains within the stated surplus.", "현재 적립액으로는 목표에 미달합니다. 필요한 월 적립액은 설정한 잉여 현금 범위 안입니다."),
    "G03": ("This is an accumulation target, not a retirement-income or withdrawal sustainability test.", "은퇴 전 자산 축적에 대한 계산입니다. 은퇴 후 인출과 생활비 유지 가능성은 평가하지 않았습니다."),
    "G04": ("All goal and cash-flow amounts are in KRW. Tuition inflation is not included.", "목표와 현금흐름 모두 원화입니다. 교육비 물가 상승은 반영하지 않았습니다."),
    "G05": ("The required monthly saving exceeds available surplus. A larger contribution needs a funding change.", "필요한 월 적립액이 가용 잉여 현금을 넘습니다. 적립액을 늘리려면 재원도 달라져야 합니다."),
    "G06": ("The target is met only if the assumed contributions can be funded; the current surplus is insufficient.", "입력한 적립액을 실제로 납입해야 목표에 도달합니다. 현재 잉여 현금만으로는 부족합니다."),
    "G07": ("The existing monthly deficit is separate from the unfunded contribution. Neither is deducted from the projection.", "현재 생활의 월 적자와 추가 적립 재원 부족은 별개입니다. 전망에는 둘 다 차감하지 않았습니다."),
    "G08": ("The target is already funded, but living-cost withdrawals are excluded. With no contributions or return and USD 3,000 monthly withdrawals, USD 50,000 becomes USD 14,000 after 12 months.", "목표액은 이미 확보했지만 생활비 인출은 빠져 있습니다. 수익과 추가 적립 없이 월 3,000달러를 인출하면 50,000달러는 12개월 뒤 14,000달러가 됩니다."),
    "G09": ("Negative return reduces the balance. USD surplus cannot be compared directly with KRW contributions.", "음수 수익률로 잔액이 감소합니다. 달러 잉여 현금과 원화 적립액은 직접 비교할 수 없습니다."),
    "G10": ("The existing balance covers the target even under the assumed negative return; no additional contribution is required.", "설정한 손실 가정에서도 현재 자금이 목표를 충족하므로 추가 적립 필요액은 0입니다."),
}


def load_goal_cases():
    path = Path(__file__).resolve().parent / "data" / "goal_validation_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def calculate_case(case):
    return project_goal(case["current"], case["monthly"], case["target"],
                        case["months"], case["annual_return"], case["annual_drag"])


def case_cashflow_state(case):
    return {
        "last_personal_finance_currency": case["finance_currency"],
        "last_personal_finance_profile": {
            "monthly_income": case["income"], "fixed_expenses": case["fixed"],
            "variable_expenses": case["variable"], "monthly_debt_payment": case["debt_payment"],
        },
    }


def validate_goal_cases(cases):
    """Independent monthly recurrence, rather than the app's closed-form formula."""
    rows = []
    for case in cases:
        actual = calculate_case(case)
        with localcontext() as context:
            context.prec = 40
            net = (Decimal(str(case["annual_return"])) - Decimal(str(case["annual_drag"]))) / 100
            rate = (1 + net) ** (Decimal(1) / 12) - 1
            principal, unit = Decimal(str(case["current"])), Decimal(0)
            for _ in range(case["months"]):
                principal *= 1 + rate
                unit = unit * (1 + rate) + 1
            reference = principal + Decimal(str(case["monthly"])) * unit
            required = max(Decimal(0), (Decimal(str(case["target"])) - principal) / unit)
        error = max(abs(actual["projected"] - float(reference)),
                    abs(actual["required_monthly"] - float(required)))
        rows.append({"id": case["id"], "passed": error <= 0.01, "max_error": error})
    return rows


def render_goal_case_studies(language):
    import altair as alt
    import pandas as pd
    import streamlit as st

    ko = language == "ko"
    text = lambda en, kr: kr if ko else en
    cases = load_goal_cases()
    case_map = {case["id"]: case for case in cases}
    st.header(text("10 goals, 10 case studies", "10명의 재무 목표 사례"))
    st.caption(text("Fictional data only. Case results do not change your personal inputs. Fixed-return estimates, not financial advice or probabilities.",
                    "모든 인물과 금액은 가상 데이터입니다. 사례 조회는 개인 입력을 변경하지 않습니다. 고정 수익률 가정의 추정치이며 재무 권고나 달성 확률이 아닙니다."))
    if st.session_state.get("validation_case_id") not in case_map:
        st.session_state["validation_case_id"] = cases[0]["id"]

    def case_label(case_id):
        labels = CASE_LABELS[case_id]
        name = case_map[case_id]["name"] if ko else labels[0]
        return f"{case_id} · {name} · {labels[2] if ko else labels[1]}"

    # A language-specific widget refreshes the displayed label without losing the case.
    widget_key = f"validation_case_id_{language}"
    st.session_state[widget_key] = st.session_state["validation_case_id"]

    def select_case():
        st.session_state["validation_case_id"] = st.session_state[widget_key]

    selected = st.selectbox(text("Select a case", "케이스 선택"), list(case_map),
                            format_func=case_label, key=widget_key, on_change=select_case)
    case = case_map[selected]
    result = calculate_case(case)
    labels = CASE_LABELS[selected]
    money = lambda value, currency=case["currency"]: (
        f"{'-' if value < 0 else ''}{'₩' if currency == 'KRW' else '$'}{abs(value):,.0f}"
        if currency == "KRW" else f"{'-' if value < 0 else ''}${abs(value):,.2f}")
    st.subheader(case_label(selected))
    st.caption(f"{case['age']} {text('years old', '세')} · {labels[4] if ko else labels[3]} · {case['months']} {text('months', '개월')} · {case['currency']}")
    cols = st.columns(3)
    cols[0].metric(text("Projected amount", "목표 시점 예상 자금"), money(result["projected"]))
    cols[1].metric(text("Surplus / shortfall", "목표 대비 초과·부족액"), money(result["gap"]))
    cols[2].metric(text("Required monthly saving", "필요한 월 적립액"), money(result["required_monthly"]))
    plan = {**case, "result": result}
    severity, message = goal_cashflow_message(plan, case_cashflow_state(case), language)
    message = message.replace("최근 개인 재무 계산의", "이 사례의").replace("최근 계산한", "이 사례의")
    message = message.replace("applied monthly surplus", "this case's monthly surplus")
    getattr(st, severity)(message.replace("$", r"\$"))
    st.write(CASE_NOTES[selected][1 if ko else 0])

    with st.expander(text("Inputs and assumptions", "입력 조건과 계산 가정"), expanded=True):
        entries = [
            (text("Target", "목표 금액"), money(case["target"])),
            (text("Current allocated funds", "현재 배정 자금"), money(case["current"])),
            (text("Monthly contribution", "월 적립 계획"), money(case["monthly"])),
            (text("Annual return / cost drag", "연 수익률 / 비용 차감"), f"{case['annual_return']}% / {case['annual_drag']}%p"),
            (text("Monthly income", "월수입"), money(case["income"], case["finance_currency"])),
            (text("Fixed / variable costs / debt payment", "고정 지출 / 변동 지출 / 부채 상환"),
             " / ".join(money(case[key], case["finance_currency"]) for key in ("fixed", "variable", "debt_payment"))),
        ]
        st.dataframe(pd.DataFrame(entries, columns=[text("Input", "항목"), text("Value", "값")]),
                     hide_index=True, width="stretch")

    projected_label, target_label = text("Projected funds", "예상 자금"), text("Target", "목표 금액")
    chart_rows = [{"month": item["Month"], "amount": item[key], "series": label}
                  for item in result["path"]
                  for key, label in (("Projected savings", projected_label), ("Target", target_label))]
    chart = alt.Chart(pd.DataFrame(chart_rows)).mark_line(strokeWidth=2).encode(
        x=alt.X("month:Q", title=text("Month", "경과 개월")),
        y=alt.Y("amount:Q", title=case["currency"]),
        color=alt.Color("series:N", title=None, scale=alt.Scale(
            domain=[projected_label, target_label], range=["#14786f", "#ae761a"])),
        tooltip=[alt.Tooltip("month:Q", title=text("Month", "개월")),
                 alt.Tooltip("series:N", title=text("Series", "구분")),
                 alt.Tooltip("amount:Q", title=text("Amount", "금액"), format=",.2f")],
    ).properties(height=250, background="#ffffff").configure_axis(
        labelColor="#42515d", titleColor="#42515d", gridColor="#e7ecee").configure_legend(
        labelColor="#42515d").configure_view(stroke=None)
    st.altair_chart(chart, theme=None, width="stretch")

    with st.expander(text("Calculation evidence and limits", "계산 근거와 검증 범위")):
        st.latex(r"r_m=(1+r_{annual}-d)^{1/12}-1,\quad B_{m+1}=B_m(1+r_m)+C")
        st.caption(text("r: return; d: annual cost drag; C: month-end contribution. Withdrawals, tax-account rules, inflation and allocations to other goals are not modeled.",
                        "r: 수익률, d: 연 비용 차감, C: 월말 적립액. 생활비 인출, 계좌별 세금, 물가, 다른 목표로의 배분은 계산하지 않습니다."))
        st.write(text("The check compares all 10 goals with an independent monthly calculation (tolerance: 0.01 currency units). It is not a live-market, concurrent-user, storage, or load-performance test.",
                      "검증은 10개 목표를 별도 월별 계산과 비교합니다(허용 오차: 0.01 통화 단위). 실시간 시세, 동시 접속, 저장 안정성 또는 처리 속도 검사는 아닙니다."))
    if st.button(text("Verify all 10 calculations", "10개 사례 계산 검증"),
                 icon=":material/fact_check:", key="verify_goal_cases"):
        st.session_state["show_goal_case_validation"] = True
    if st.session_state.get("show_goal_case_validation"):
        checks = validate_goal_cases(cases)
        passed = sum(item["passed"] for item in checks)
        message = text(f"{passed}/10 calculations agree. This does not mean every financial goal is feasible.",
                       f"{passed}/10개 계산이 일치합니다. 모든 재무 목표가 달성 가능하다는 의미는 아닙니다.")
        (st.success if passed == len(cases) else st.error)(message)
        st.dataframe(pd.DataFrame([{
            text("Case", "사례"): case_label(item["id"]),
            text("Calculation", "계산 검증"): text("Pass", "일치") if item["passed"] else text("Mismatch", "불일치"),
            text("Maximum error", "최대 오차"): f"{item['max_error']:.8f}",
        } for item in checks]), hide_index=True, width="stretch")
    st.download_button(text("Download case data", "사례 데이터 다운로드"),
                       data=json.dumps({"fictional": True, "case": case, "result": result}, ensure_ascii=False, indent=2),
                       file_name=f"ly-scope-{selected}.json", mime="application/json", icon=":material/download:")

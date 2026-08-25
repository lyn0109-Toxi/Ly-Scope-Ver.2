from __future__ import annotations

from dataclasses import dataclass
from html import escape

import altair as alt
import pandas as pd
import streamlit as st

KO_TRANSLATIONS = {
    "REIT-focused educational analysis": "REIT 중심 교육 분석",
    "Developer": "개발자",
    "Comments or research notes": "의견 또는 리서치 메모",
    "Write questions, ideas, or professor feedback here.": "질문, 아이디어, 교수님 피드백을 여기에 적어 주세요.",
    "This prototype is for education and research discussion only.": "이 프로토타입은 교육 및 리서치 논의용입니다.",
    "REIT-focused finance education platform for valuation, income analysis, interest-rate sensitivity, portfolio risk, and sector specialization.": "가치평가, 소득 분석, 금리 민감도, 포트폴리오 위험, 섹터 특화를 위한 REIT 중심 금융 교육 플랫폼.",
    "Educational REIT Analytics - Not Investment Advice": "교육용 REIT 분석 - 투자 조언 아님",
    "REIT Market Lens": "REIT 시장 렌즈",
    "Start with property type, income quality, leverage, and valuation multiples.": "부동산 유형, 소득 품질, 레버리지, 가치평가 배수에서 시작하세요.",
    "Coverage Universe": "분석 대상",
    "Avg Dividend Yield": "평균 배당수익률",
    "Avg Price / FFO": "평균 Price / FFO",
    "Avg NAV Discount": "평균 NAV 할인",
    "Sample REIT Universe": "샘플 REIT 유니버스",
    "Peer Group Map": "피어 그룹 맵",
    "REITs should be compared within similar property sectors whenever possible.": "가능하면 REIT는 유사한 부동산 섹터 안에서 비교해야 합니다.",
    "REIT Valuation Triangulation": "REIT 가치평가 삼각 검증",
    "REITs are usually better studied with FFO, AFFO, NAV, dividend quality, and leverage.": "REIT는 보통 FFO, AFFO, NAV, 배당 품질, 레버리지로 보는 것이 더 적합합니다.",
    "Select REIT": "REIT 선택",
    "Dividend Yield": "배당수익률",
    "Price / FFO": "Price / FFO",
    "NAV Discount": "NAV 할인",
    "AFFO Payout": "AFFO 배당성향",
    "Dividend Safety": "배당 안전성",
    "Valuation Score": "가치평가 점수",
    "Debt/Rate Risk": "부채/금리 위험",
    "Property Quality": "부동산 품질",
    "Growth": "성장",
    "REIT Diagnostic Scorecard": "REIT 진단 스코어카드",
    "Interest-Rate Sensitivity": "금리 민감도",
    "REITs are often sensitive to financing conditions, Treasury yields, and income alternatives.": "REIT는 자금조달 환경, 국채금리, 대체 소득자산에 민감한 경우가 많습니다.",
    "A more negative rate sensitivity means the REIT may be more exposed to rising interest rates. This is an educational signal, not a forecast.": "금리 민감도가 더 음수일수록 금리 상승에 더 노출될 수 있습니다. 이는 교육용 신호이며 예측이 아닙니다.",
    "Debt and Rate Risk Ranking": "부채 및 금리 위험 순위",
    "Income Safety & Property Quality": "소득 안전성과 부동산 품질",
    "This view focuses on the information real estate investors usually care about first: income durability, tenant quality, occupancy, and growth.": "이 화면은 부동산 투자자가 먼저 보는 소득 지속성, 임차인 품질, 점유율, 성장성을 중심으로 합니다.",
    "Avg Safety Score": "평균 안전성 점수",
    "Avg Occupancy": "평균 점유율",
    "Avg Tenant Quality": "평균 임차인 품질",
    "Avg FFO Growth": "평균 FFO 성장률",
    "Quality and Growth Table": "품질 및 성장 테이블",
    "REIT Portfolio Studio": "REIT 포트폴리오 스튜디오",
    "Study sector concentration, income exposure, beta, and diversification.": "섹터 집중도, 소득 노출, 베타, 분산을 검토하세요.",
    "Select REIT holdings": "REIT 보유 종목 선택",
    "Select at least one REIT to build a portfolio view.": "포트폴리오 보기를 만들려면 최소 1개 REIT를 선택하세요.",
    "Weighting Mode": "비중 방식",
    "Equal-weighted": "동일비중",
    "Dollar allocation": "금액 배분",
    "allocation $": "배분 금액 $",
    "Weighted Dividend Yield": "가중 배당수익률",
    "Weighted Beta": "가중 베타",
    "Rate Sensitivity": "금리 민감도",
    "Income Safety": "소득 안전성",
    "Growth Profile": "성장 프로필",
    "Ver.2 Learning Guide": "Ver.2 학습 가이드",
    "Overview": "개요",
    "Valuation": "가치평가",
    "Quality": "품질",
    "Macro Sensitivity": "거시 민감도",
    "Portfolio": "포트폴리오",
    "Guide": "가이드",
    "LY-Scope-Ver.2 REIT module is an educational prototype. It does not provide investment, legal, tax, financial, accounting, or professional advice. Third-party market data remains subject to the terms of its providers.": "LY-Scope-Ver.2 REIT 모듈은 교육용 프로토타입입니다. 투자, 법률, 세무, 금융, 회계 또는 전문 조언을 제공하지 않습니다. 제3자 시장 데이터는 각 제공자의 약관을 따릅니다.",
}


def tr(text: str) -> str:
    if st.session_state.get("app_language") == "ko":
        return KO_TRANSLATIONS.get(text, text)
    return text


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 18% 12%, rgba(20, 184, 166, 0.16), transparent 30%),
            radial-gradient(circle at 88% 8%, rgba(245, 158, 11, 0.12), transparent 26%),
            linear-gradient(135deg, #0b1018 0%, #111827 52%, #070a0f 100%);
        color: #f8fafc;
    }
    .block-container {
        padding-top: 1.25rem;
        max-width: 1240px;
    }
    h1, h2, h3, p, li, label {
        letter-spacing: 0;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    p, li, label {
        color: #dbe7f3;
    }
    .reit-hero {
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 24px;
        padding: 34px 34px 30px;
        margin-bottom: 22px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(17, 24, 39, 0.88)),
            radial-gradient(circle at 82% 18%, rgba(245, 158, 11, 0.18), transparent 30%);
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
    }
    .brand-line {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
    }
    .brand-icon {
        width: 62px;
        height: 62px;
        display: grid;
        place-items: center;
        border-radius: 18px;
        border: 1px solid rgba(125, 211, 252, 0.36);
        background: linear-gradient(145deg, #0f2f43, #172033);
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 900;
    }
    .brand-title {
        font-size: clamp(2.4rem, 5vw, 4.8rem);
        line-height: 0.94;
        font-weight: 900;
        color: #f8fafc;
    }
    .brand-title span {
        color: #facc15;
    }
    .hero-muted {
        color: #cbd5e1;
        font-size: 1.08rem;
        max-width: 780px;
    }
    .pill {
        display: inline-block;
        padding: 8px 13px;
        border-radius: 999px;
        border: 1px solid rgba(250, 204, 21, 0.28);
        background: rgba(250, 204, 21, 0.10);
        color: #fde68a;
        font-weight: 800;
        margin-top: 18px;
    }
    .metric-card {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 18px;
        padding: 22px;
        min-height: 132px;
        background: #f8fafc;
        color: #0f172a;
        box-shadow: 0 16px 40px rgba(2, 6, 23, 0.22);
    }
    .metric-label {
        color: #64748b;
        font-weight: 800;
        margin-bottom: 14px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 2.1rem;
        font-weight: 900;
    }
    .section-panel {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 20px;
        padding: 22px;
        background: rgba(15, 23, 42, 0.70);
        margin: 16px 0 22px;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background: #f8fafc !important;
        color: #0f172a !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }
    @media (max-width: 680px) {
        .block-container {
            padding: 0.75rem 0.85rem 5.5rem;
        }
        .reit-hero {
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 18px;
        }
        .brand-line {
            gap: 10px;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .brand-icon {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            font-size: 1.1rem;
        }
        .brand-title {
            font-size: 1.65rem;
            line-height: 1;
        }
        .hero-muted {
            font-size: 0.88rem;
            line-height: 1.35;
        }
        .pill {
            margin-top: 12px;
            padding: 7px 10px;
            font-size: 0.78rem;
        }
        .section-panel {
            padding: 14px;
            border-radius: 16px;
            margin: 12px 0 16px;
        }
        .metric-card {
            min-height: 92px;
            padding: 14px;
            border-radius: 15px;
        }
        .metric-label {
            margin-bottom: 8px;
            font-size: 0.76rem;
        }
        .metric-value {
            font-size: 1.35rem;
        }
        div[data-testid="stTabs"] div[role="tablist"] {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px !important;
            padding: 4px 0 10px !important;
            margin-bottom: 12px !important;
            border-bottom: 0 !important;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            width: auto !important;
            height: 42px !important;
            min-width: 0 !important;
            min-height: 42px !important;
            padding: 7px 10px !important;
            border-radius: 14px !important;
            color: #0f172a !important;
            background:
                radial-gradient(circle at 18% 16%, rgba(255,255,255,0.96), transparent 30%),
                linear-gradient(135deg, rgba(255,255,255,0.96), rgba(240,249,255,0.86)) !important;
            box-shadow: 0 10px 22px rgba(14, 165, 233, 0.10) !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
            box-shadow: 0 12px 28px rgba(14, 165, 233, 0.22) !important;
        }
        div[data-testid="stTabs"] button[role="tab"] p {
            max-width: none !important;
            font-size: 0.78rem !important;
            line-height: 1.05 !important;
            white-space: normal !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@dataclass(frozen=True)
class ReitRecord:
    symbol: str
    company: str
    sector: str
    price: float
    dividend_yield: float
    price_to_ffo: float
    affo_payout: float
    nav_discount: float
    debt_to_ebitda: float
    occupancy: float
    ffo_growth: float
    rent_growth: float
    tenant_quality: float
    lease_duration: float
    beta: float
    rate_sensitivity: float


SAMPLE_REITS: list[ReitRecord] = [
    ReitRecord("PLD", "Prologis", "Industrial", 111.40, 3.55, 19.8, 72.0, -3.2, 5.1, 97.2, 5.8, 4.6, 8.8, 5.2, 1.02, -0.62),
    ReitRecord("O", "Realty Income", "Retail Net Lease", 56.20, 5.65, 13.4, 76.0, -8.5, 5.5, 98.6, 3.2, 2.7, 8.5, 9.1, 0.82, -0.78),
    ReitRecord("EQIX", "Equinix", "Data Center", 792.50, 2.15, 24.6, 64.0, 5.4, 4.2, 96.1, 7.4, 5.5, 9.1, 4.8, 0.94, -0.48),
    ReitRecord("AVB", "AvalonBay Communities", "Residential", 197.80, 3.40, 17.1, 68.0, -2.1, 4.8, 95.8, 4.1, 3.8, 8.0, 1.3, 0.88, -0.56),
    ReitRecord("WELL", "Welltower", "Healthcare", 126.70, 2.10, 27.2, 61.0, 9.0, 5.8, 87.5, 8.2, 5.0, 7.8, 6.4, 1.04, -0.44),
    ReitRecord("PSA", "Public Storage", "Storage", 288.30, 4.15, 18.7, 71.0, 1.8, 3.9, 92.8, 3.7, 3.0, 8.2, 0.8, 0.72, -0.40),
    ReitRecord("SPG", "Simon Property Group", "Retail Mall", 159.60, 5.00, 12.8, 67.0, -6.0, 5.9, 95.5, 2.8, 2.4, 7.2, 6.8, 1.35, -0.69),
    ReitRecord("BXP", "BXP", "Office", 66.40, 5.90, 9.2, 82.0, -18.0, 7.1, 88.6, -1.4, 0.8, 6.2, 5.7, 1.28, -0.84),
]


def reit_frame() -> pd.DataFrame:
    df = pd.DataFrame([record.__dict__ for record in SAMPLE_REITS])
    df["dividend_safety_score"] = df.apply(dividend_safety_score, axis=1)
    df["valuation_score"] = df.apply(reit_valuation_score, axis=1)
    df["debt_rate_risk_score"] = df.apply(debt_rate_risk_score, axis=1)
    df["property_quality_score"] = df.apply(property_quality_score, axis=1)
    df["growth_score"] = df.apply(growth_score, axis=1)
    df["reit_composite_score"] = (
        df["dividend_safety_score"] * 0.25
        + df["valuation_score"] * 0.25
        + df["property_quality_score"] * 0.20
        + df["growth_score"] * 0.15
        + (10 - df["debt_rate_risk_score"]) * 0.15
    )
    return df


def clamp_score(value: float) -> float:
    return max(0.0, min(10.0, float(value)))


def dividend_safety_score(row: pd.Series) -> float:
    payout_component = 10 - max(0, row["affo_payout"] - 60) / 4
    leverage_component = 10 - max(0, row["debt_to_ebitda"] - 4) * 1.4
    occupancy_component = row["occupancy"] / 10
    lease_component = min(10, row["lease_duration"] * 1.2)
    return clamp_score(
        payout_component * 0.35
        + leverage_component * 0.25
        + occupancy_component * 0.25
        + lease_component * 0.15
    )


def reit_valuation_score(row: pd.Series) -> float:
    nav_component = 5 - row["nav_discount"] / 4
    ffo_component = 10 - max(0, row["price_to_ffo"] - 10) / 2
    yield_component = min(10, row["dividend_yield"] * 1.35)
    payout_penalty = max(0, row["affo_payout"] - 80) / 5
    return clamp_score(nav_component * 0.35 + ffo_component * 0.35 + yield_component * 0.30 - payout_penalty)


def debt_rate_risk_score(row: pd.Series) -> float:
    leverage_risk = max(0, row["debt_to_ebitda"] - 3.5) * 1.4
    rate_risk = abs(row["rate_sensitivity"]) * 5
    beta_risk = max(0, row["beta"] - 0.8) * 2
    return clamp_score(leverage_risk * 0.45 + rate_risk * 0.35 + beta_risk * 0.20)


def property_quality_score(row: pd.Series) -> float:
    occupancy_component = row["occupancy"] / 10
    tenant_component = row["tenant_quality"]
    rent_component = min(10, max(0, row["rent_growth"] * 1.6))
    return clamp_score(occupancy_component * 0.40 + tenant_component * 0.35 + rent_component * 0.25)


def growth_score(row: pd.Series) -> float:
    ffo_component = min(10, max(0, row["ffo_growth"] * 1.25))
    rent_component = min(10, max(0, row["rent_growth"] * 1.5))
    quality_component = row["property_quality_score"] if "property_quality_score" in row else property_quality_score(row)
    return clamp_score(ffo_component * 0.45 + rent_component * 0.35 + quality_component * 0.20)


def metric_card(label: str, value: str, color: str = "#0f172a") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(str(label))}</div>
            <div class="metric-value" style="color:{escape(str(color))};">{escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def valuation_label(row: pd.Series) -> str:
    if row["reit_composite_score"] >= 7.2:
        return "High Quality / Attractive"
    if row["reit_composite_score"] >= 5.8:
        return "Balanced"
    if row["debt_rate_risk_score"] >= 6.5:
        return "Needs Caution"
    return "Watchlist"


def score_color(score: float, inverted: bool = False) -> str:
    value = 10 - score if inverted else score
    if value >= 7:
        return "#16a34a"
    if value >= 5:
        return "#d97706"
    return "#dc2626"


def build_sidebar() -> None:
    with st.sidebar:
        st.header("LY-Scope-Ver.2")
        st.write(tr("REIT-focused educational analysis"))
        st.divider()
        st.caption(tr("Developer"))
        st.write("Youngnam Lee")
        st.write("lyn0109@gmail.com")
        st.divider()
        st.text_area(tr("Comments or research notes"), placeholder=tr("Write questions, ideas, or professor feedback here."))
        st.caption(tr("This prototype is for education and research discussion only."))


def hero() -> None:
    st.markdown(
        f"""
        <div class="reit-hero">
            <div class="brand-line">
                <div class="brand-icon">RE</div>
                <div class="brand-title">LY-Scope-Ver.2 <span>REIT</span></div>
            </div>
            <div class="hero-muted">
                {escape(tr('REIT-focused finance education platform for valuation, income analysis, interest-rate sensitivity, portfolio risk, and sector specialization.'))}
            </div>
            <div class="pill">{escape(tr('Educational REIT Analytics - Not Investment Advice'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def overview_tab(df: pd.DataFrame) -> None:
    st.header(tr("REIT Market Lens"))
    st.caption(tr("Start with property type, income quality, leverage, and valuation multiples."))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(tr("Coverage Universe"), f"{len(df)} REITs")
    with c2:
        metric_card(tr("Avg Dividend Yield"), f"{df['dividend_yield'].mean():.2f}%", "#16a34a")
    with c3:
        metric_card(tr("Avg Price / FFO"), f"{df['price_to_ffo'].mean():.1f}x", "#2563eb")
    with c4:
        metric_card(tr("Avg NAV Discount"), f"{df['nav_discount'].mean():+.1f}%", "#d97706")

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader(tr("Sample REIT Universe"))
    table = df.copy()
    table["valuation_view"] = table.apply(valuation_label, axis=1)
    table = table.rename(
        columns={
            "symbol": "Symbol",
            "company": "Company",
            "sector": "REIT Sector",
            "price": "Price",
            "dividend_yield": "Dividend Yield %",
            "price_to_ffo": "Price / FFO",
            "affo_payout": "AFFO Payout %",
            "nav_discount": "NAV Discount %",
            "debt_to_ebitda": "Debt / EBITDA",
            "occupancy": "Occupancy %",
            "ffo_growth": "FFO Growth %",
            "rent_growth": "Rent Growth %",
            "tenant_quality": "Tenant Quality",
            "lease_duration": "Avg Lease Years",
            "beta": "Beta",
            "rate_sensitivity": "Rate Sensitivity",
            "dividend_safety_score": "Dividend Safety",
            "valuation_score": "REIT Valuation",
            "debt_rate_risk_score": "Debt/Rate Risk",
            "property_quality_score": "Property Quality",
            "growth_score": "Growth",
            "reit_composite_score": "Composite Score",
            "valuation_view": "Educational View",
        }
    )
    st.dataframe(table, hide_index=True, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader(tr("Peer Group Map"))
    st.caption(tr("REITs should be compared within similar property sectors whenever possible."))
    peer_chart = (
        alt.Chart(df)
        .mark_circle(size=180, opacity=0.84)
        .encode(
            x=alt.X("price_to_ffo:Q", title="Price / FFO"),
            y=alt.Y("dividend_yield:Q", title="Dividend Yield %"),
            color=alt.Color("sector:N", title="Property Sector"),
            size=alt.Size("reit_composite_score:Q", title="Composite Score"),
            tooltip=[
                "symbol",
                "company",
                "sector",
                alt.Tooltip("dividend_yield:Q", format=".2f"),
                alt.Tooltip("price_to_ffo:Q", format=".1f"),
                alt.Tooltip("reit_composite_score:Q", format=".1f"),
            ],
        )
        .properties(height=390)
    )
    st.altair_chart(peer_chart, width="stretch")


def valuation_tab(df: pd.DataFrame) -> None:
    st.header(tr("REIT Valuation Triangulation"))
    st.caption(tr("REITs are usually better studied with FFO, AFFO, NAV, dividend quality, and leverage."))

    selected_symbol = st.selectbox(
        tr("Select REIT"),
        options=df["symbol"].tolist(),
        format_func=lambda symbol: f"{symbol} - {df.loc[df['symbol'] == symbol, 'company'].iloc[0]}",
    )
    row = df[df["symbol"] == selected_symbol].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(tr("Dividend Yield"), f"{row['dividend_yield']:.2f}%", "#16a34a")
    with c2:
        metric_card(tr("Price / FFO"), f"{row['price_to_ffo']:.1f}x", "#2563eb")
    with c3:
        metric_card(tr("NAV Discount"), f"{row['nav_discount']:+.1f}%", "#d97706")
    with c4:
        metric_card(tr("AFFO Payout"), f"{row['affo_payout']:.1f}%", "#7c3aed")

    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        metric_card(tr("Dividend Safety"), f"{row['dividend_safety_score']:.1f}/10", score_color(row["dividend_safety_score"]))
    with s2:
        metric_card(tr("Valuation Score"), f"{row['valuation_score']:.1f}/10", score_color(row["valuation_score"]))
    with s3:
        metric_card(tr("Debt/Rate Risk"), f"{row['debt_rate_risk_score']:.1f}/10", score_color(row["debt_rate_risk_score"], inverted=True))
    with s4:
        metric_card(tr("Property Quality"), f"{row['property_quality_score']:.1f}/10", score_color(row["property_quality_score"]))
    with s5:
        metric_card(tr("Growth"), f"{row['growth_score']:.1f}/10", score_color(row["growth_score"]))

    triangulation = pd.DataFrame(
        [
            {"Approach": "Income", "Model": "Dividend / AFFO sustainability", "Signal": f"{row['dividend_yield']:.2f}% yield, {row['affo_payout']:.1f}% payout"},
            {"Approach": "Asset", "Model": "NAV premium or discount", "Signal": f"{row['nav_discount']:+.1f}% vs estimated NAV"},
            {"Approach": "Market", "Model": "Price / FFO peer multiple", "Signal": f"{row['price_to_ffo']:.1f}x Price / FFO"},
        ]
    )
    st.dataframe(triangulation, hide_index=True, width="stretch")

    diagnostics = pd.DataFrame(
        [
            {"Lens": "Income Safety", "What it checks": "Dividend yield, AFFO payout, leverage, occupancy, lease duration", "Reading": f"{row['dividend_safety_score']:.1f}/10"},
            {"Lens": "FFO/AFFO Valuation", "What it checks": "Price/FFO, NAV discount, yield, payout burden", "Reading": f"{row['valuation_score']:.1f}/10"},
            {"Lens": "Debt & Rate Risk", "What it checks": "Debt/EBITDA, beta, interest-rate sensitivity", "Reading": f"{row['debt_rate_risk_score']:.1f}/10 risk"},
            {"Lens": "Property Quality", "What it checks": "Occupancy, tenant quality, rent growth", "Reading": f"{row['property_quality_score']:.1f}/10"},
            {"Lens": "Growth", "What it checks": "FFO growth, rent growth, operating quality", "Reading": f"{row['growth_score']:.1f}/10"},
        ]
    )
    st.subheader(tr("REIT Diagnostic Scorecard"))
    st.dataframe(diagnostics, hide_index=True, width="stretch")

    radar = pd.DataFrame(
        [
            {"Dimension": "Dividend Safety", "Score": row["dividend_safety_score"]},
            {"Dimension": "Valuation", "Score": row["valuation_score"]},
            {"Dimension": "Balance Sheet", "Score": 10 - row["debt_rate_risk_score"]},
            {"Dimension": "Property Quality", "Score": row["property_quality_score"]},
            {"Dimension": "Growth", "Score": row["growth_score"]},
        ]
    )
    chart = (
        alt.Chart(radar)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("Dimension:N", sort=None),
            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 10])),
            color=alt.Color("Dimension:N", legend=None),
            tooltip=["Dimension", alt.Tooltip("Score:Q", format=".1f")],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")


def macro_tab(df: pd.DataFrame) -> None:
    st.header(tr("Interest-Rate Sensitivity"))
    st.caption(tr("REITs are often sensitive to financing conditions, Treasury yields, and income alternatives."))

    chart = (
        alt.Chart(df)
        .mark_circle(size=180, opacity=0.82)
        .encode(
            x=alt.X("dividend_yield:Q", title="Dividend Yield %"),
            y=alt.Y("rate_sensitivity:Q", title="Rate Sensitivity"),
            color=alt.Color("sector:N", title="Sector"),
            tooltip=["symbol", "company", "sector", "dividend_yield", "rate_sensitivity", "debt_to_ebitda"],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, width="stretch")
    st.info(
        tr("A more negative rate sensitivity means the REIT may be more exposed to rising interest rates. This is an educational signal, not a forecast.")
    )

    st.subheader(tr("Debt and Rate Risk Ranking"))
    risk_table = df[
        [
            "symbol",
            "company",
            "sector",
            "debt_to_ebitda",
            "rate_sensitivity",
            "beta",
            "debt_rate_risk_score",
        ]
    ].sort_values("debt_rate_risk_score", ascending=False)
    st.dataframe(risk_table, hide_index=True, width="stretch")


def quality_tab(df: pd.DataFrame) -> None:
    st.header(tr("Income Safety & Property Quality"))
    st.caption(tr("This view focuses on the information real estate investors usually care about first: income durability, tenant quality, occupancy, and growth."))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(tr("Avg Safety Score"), f"{df['dividend_safety_score'].mean():.1f}/10", score_color(df["dividend_safety_score"].mean()))
    with c2:
        metric_card(tr("Avg Occupancy"), f"{df['occupancy'].mean():.1f}%", "#2563eb")
    with c3:
        metric_card(tr("Avg Tenant Quality"), f"{df['tenant_quality'].mean():.1f}/10", score_color(df["tenant_quality"].mean()))
    with c4:
        metric_card(tr("Avg FFO Growth"), f"{df['ffo_growth'].mean():+.1f}%", "#d97706")

    quality_chart = (
        alt.Chart(df)
        .mark_circle(size=190, opacity=0.82)
        .encode(
            x=alt.X("occupancy:Q", title="Occupancy %", scale=alt.Scale(domain=[84, 100])),
            y=alt.Y("affo_payout:Q", title="AFFO Payout %"),
            color=alt.Color("sector:N", title="Property Sector"),
            size=alt.Size("dividend_safety_score:Q", title="Dividend Safety"),
            tooltip=[
                "symbol",
                "company",
                "sector",
                alt.Tooltip("occupancy:Q", format=".1f"),
                alt.Tooltip("affo_payout:Q", format=".1f"),
                alt.Tooltip("tenant_quality:Q", format=".1f"),
                alt.Tooltip("dividend_safety_score:Q", format=".1f"),
            ],
        )
        .properties(height=390)
    )
    st.altair_chart(quality_chart, width="stretch")

    st.subheader(tr("Quality and Growth Table"))
    table = df[
        [
            "symbol",
            "company",
            "sector",
            "occupancy",
            "tenant_quality",
            "lease_duration",
            "rent_growth",
            "ffo_growth",
            "dividend_safety_score",
            "property_quality_score",
            "growth_score",
        ]
    ].sort_values("property_quality_score", ascending=False)
    st.dataframe(table, hide_index=True, width="stretch")


def portfolio_tab(df: pd.DataFrame) -> None:
    st.header(tr("REIT Portfolio Studio"))
    st.caption(tr("Study sector concentration, income exposure, beta, and diversification."))

    selected = st.multiselect(
        tr("Select REIT holdings"),
        options=df["symbol"].tolist(),
        default=["PLD", "O", "EQIX", "AVB"],
        format_func=lambda symbol: f"{symbol} - {df.loc[df['symbol'] == symbol, 'company'].iloc[0]}",
    )
    if not selected:
        st.info(tr("Select at least one REIT to build a portfolio view."))
        return

    mode_labels = {"Equal-weighted": tr("Equal-weighted"), "Dollar allocation": tr("Dollar allocation")}
    selected_mode_label = st.radio(tr("Weighting Mode"), list(mode_labels.values()), horizontal=True)
    mode = next(key for key, label in mode_labels.items() if label == selected_mode_label)
    selected_df = df[df["symbol"].isin(selected)].copy()

    if mode == "Equal-weighted":
        selected_df["Weight"] = 1 / len(selected_df)
    else:
        allocations: dict[str, float] = {}
        cols = st.columns(min(3, len(selected)))
        for idx, symbol in enumerate(selected):
            allocations[symbol] = cols[idx % len(cols)].number_input(
                f"{symbol} {tr('allocation $')}",
                min_value=0.0,
                value=1000.0,
                step=100.0,
            )
        total_allocation = sum(allocations.values())
        selected_df["Weight"] = selected_df["symbol"].map(
            lambda symbol: allocations[symbol] / total_allocation if total_allocation else 0
        )

    weighted_yield = float((selected_df["dividend_yield"] * selected_df["Weight"]).sum())
    weighted_beta = float((selected_df["beta"] * selected_df["Weight"]).sum())
    weighted_rate_sensitivity = float((selected_df["rate_sensitivity"] * selected_df["Weight"]).sum())
    weighted_safety = float((selected_df["dividend_safety_score"] * selected_df["Weight"]).sum())
    weighted_quality = float((selected_df["property_quality_score"] * selected_df["Weight"]).sum())
    weighted_growth = float((selected_df["growth_score"] * selected_df["Weight"]).sum())

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(tr("Weighted Dividend Yield"), f"{weighted_yield:.2f}%", "#16a34a")
    with c2:
        metric_card(tr("Weighted Beta"), f"{weighted_beta:.2f}", "#2563eb")
    with c3:
        metric_card(tr("Rate Sensitivity"), f"{weighted_rate_sensitivity:.2f}", "#d97706")

    q1, q2, q3 = st.columns(3)
    with q1:
        metric_card(tr("Income Safety"), f"{weighted_safety:.1f}/10", score_color(weighted_safety))
    with q2:
        metric_card(tr("Property Quality"), f"{weighted_quality:.1f}/10", score_color(weighted_quality))
    with q3:
        metric_card(tr("Growth Profile"), f"{weighted_growth:.1f}/10", score_color(weighted_growth))

    sector_weights = selected_df.groupby("sector", as_index=False)["Weight"].sum()
    pie = (
        alt.Chart(sector_weights)
        .mark_arc(innerRadius=70, outerRadius=130)
        .encode(
            theta=alt.Theta("Weight:Q"),
            color=alt.Color("sector:N", title="REIT Sector"),
            tooltip=["sector", alt.Tooltip("Weight:Q", format=".1%")],
        )
        .properties(height=360)
    )
    st.altair_chart(pie, width="stretch")

    display = selected_df[
        [
            "symbol",
            "company",
            "sector",
            "Weight",
            "dividend_yield",
            "price_to_ffo",
            "nav_discount",
            "dividend_safety_score",
            "property_quality_score",
            "debt_rate_risk_score",
            "beta",
        ]
    ].copy()
    display["Weight"] = display["Weight"].map(lambda value: f"{value * 100:.1f}%")
    st.dataframe(display, hide_index=True, width="stretch")


def guide_tab() -> None:
    st.header(tr("Ver.2 Learning Guide"))
    st.markdown(
        """
        ### Why REITs need a separate model

        REITs are real estate companies that usually distribute a large portion of taxable income as dividends.
        Because depreciation can make accounting earnings less useful, REIT analysis often focuses on FFO,
        AFFO, dividend sustainability, NAV, leverage, occupancy, and interest-rate sensitivity.

        ### Finance theories connected to this app

        - Income approach: dividend and AFFO-based sustainability
        - Asset approach: NAV premium or discount
        - Market approach: Price / FFO peer comparison
        - CAPM: beta and expected return discussion
        - Portfolio risk: weights, covariance, correlation, and diversification
        - Capital structure: debt burden, financing cost, and interest-rate exposure

        ### Future build path

        1. Add live data integration.
        2. Build REIT peer groups by property type.
        3. Add historical price and yield charts.
        4. Add simple equal-weight REIT backtesting.
        5. Add REIT-specific ontology for property type, tenant base, and macro sensitivity.

        ### Customer-focused analysis lenses

        - Income Safety: dividend yield, AFFO payout, occupancy, lease duration, and leverage.
        - FFO/AFFO Valuation: Price/FFO, NAV discount or premium, yield, and payout pressure.
        - Debt & Rate Risk: Debt/EBITDA, beta, and interest-rate sensitivity.
        - Property Quality: occupancy, tenant quality, and rent growth.
        - Growth Profile: FFO growth, rent growth, and operating quality.

        These scores are currently educational sample signals. A professional version should connect
        them to current filings, REIT supplemental reports, Nareit-style sector data, and reliable market feeds.
        """
    )


def main(include_sidebar: bool = True) -> None:
    if include_sidebar:
        build_sidebar()
    hero()
    df = reit_frame()
    tabs = st.tabs([tr("Overview"), tr("Valuation"), tr("Quality"), tr("Macro Sensitivity"), tr("Portfolio"), tr("Guide")])
    with tabs[0]:
        overview_tab(df)
    with tabs[1]:
        valuation_tab(df)
    with tabs[2]:
        quality_tab(df)
    with tabs[3]:
        macro_tab(df)
    with tabs[4]:
        portfolio_tab(df)
    with tabs[5]:
        guide_tab()

    st.divider()
    st.caption(
        tr("LY-Scope-Ver.2 REIT module is an educational prototype. It does not provide investment, legal, tax, financial, accounting, or professional advice. Third-party market data remains subject to the terms of its providers.")
    )


if __name__ == "__main__":
    main()

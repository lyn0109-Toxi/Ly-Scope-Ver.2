from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from personal_finance_engine import PersonalFinanceProfile, calculate_personal_finance


DATA_PATH = Path(__file__).with_name("data") / "virtual_clients.json"
SUPPORTED_LANGUAGES = {"en", "ko"}
_PDF_FONT_CACHE: dict[str, tuple[str, str]] = {}

LABELS = {
    "en": {
        "advisor_report": "LY-Scope-Ver.2 Advisor Report",
        "all_reports": "LY-Scope-Ver.2 Advisor Reports",
        "fictional": "Fictional client sample for education and product validation.",
        "metric": "Metric",
        "reading": "Reading",
        "layer": "Layer",
        "visual": "Visual",
        "generated": "Generated",
        "situation": "Situation",
        "advisor_interpretation": "Advisor Interpretation",
        "evidence": "Evidence",
        "recommended_decisions": "Recommended Decisions",
        "memory_checkpoint": "Memory Checkpoint",
        "visual_score_reading": "Visual Score Reading",
        "portfolio_sample": "Portfolio / Valuation Sample",
        "market_stress_capital": "-30% market stress capital",
        "months": "months",
        "client": "Client",
        "name": "Name",
        "ticker": "Ticker",
        "sector": "Sector",
        "weight": "Weight",
        "beta": "Beta",
        "valuation": "Valuation",
        "planning_health": "Planning Health",
        "cash_runway": "Cash Runway",
        "goal_progress": "Goal Progress",
        "risk_capacity": "Risk Capacity",
        "portfolio_quality": "Portfolio Quality",
        "crisis_signal": "Crisis Signal",
        "survival_bar": "Survival Bar",
        "goal_distance": "Goal Distance",
        "decision_compass": "Decision Compass",
        "status": "Status",
        "age": "Age",
        "segment": "Segment",
        "primary_goal": "Primary goal",
        "portfolio_note": "Portfolio note",
        "real_estate_note": "Real estate note",
        "advisor_focus": "Advisor focus",
        "net_worth": "Net worth",
        "monthly_surplus": "Monthly surplus",
        "debt_to_income": "Debt-to-income",
        "investment_exposure": "Investment exposure",
        "required_runway": "Required runway",
        "portfolio_beta": "Portfolio beta",
        "largest_holding": "Largest holding",
        "real_estate_ltv": "Real estate LTV",
        "data": "Data",
        "model": "Model",
        "ai_interpretation": "AI Interpretation",
        "decision": "Decision",
        "memory": "Memory",
        "customer_purpose": "Customer Purpose",
        "strategy": "Strategy",
        "user": "Customer Purpose",
        "decision_path_data": "Income, expenses, assets, debts, goals, portfolio, real estate",
        "decision_path_model": "Personal Finance engine + portfolio quality + real estate stress",
        "decision_path_evidence": "Runway, surplus, DTI, exposure, goal progress, beta, LTV",
        "decision_path_memory": "Save PDF and compare at next review",
        "asset_cash": "Cash",
        "asset_taxable": "Taxable investments",
        "asset_retirement": "Retirement",
        "asset_real_estate": "Real estate",
        "stress_base": "Base",
        "stress_stock_20": "Stock -20%",
        "stress_stock_30": "Stock -30%",
        "stress_stock_40": "Stock -40%",
        "strong": "Strong",
        "stable": "Stable",
        "watch": "Watch",
        "at_risk": "At Risk",
        "save_memory": "Save this report date, the weakest signal, and the next action.",
        "review_memory": "Review again after a major income, market, debt, or family-status change.",
        "disclaimer": "Educational use only. This report is not financial, investment, legal, tax, accounting, or professional advice.",
    },
    "ko": {
        "advisor_report": "LY-Scope-Ver.2 어드바이저 리포트",
        "all_reports": "LY-Scope-Ver.2 어드바이저 리포트 모음",
        "fictional": "교육 및 제품 검증용 가상 고객 샘플입니다.",
        "metric": "지표",
        "reading": "판독",
        "layer": "레이어",
        "visual": "시각 신호",
        "generated": "생성일",
        "situation": "고객 상황",
        "advisor_interpretation": "어드바이저 해석",
        "evidence": "근거",
        "recommended_decisions": "권장 의사결정",
        "memory_checkpoint": "메모리 체크포인트",
        "visual_score_reading": "시각 점수 판독",
        "portfolio_sample": "포트폴리오 / 가치평가 샘플",
        "market_stress_capital": "-30% 시장 스트레스 후 자본",
        "months": "개월",
        "client": "고객",
        "name": "이름",
        "ticker": "티커",
        "sector": "섹터",
        "weight": "비중",
        "beta": "베타",
        "valuation": "가치평가",
        "planning_health": "계획 건강도",
        "cash_runway": "현금 생존기간",
        "goal_progress": "목표 진행률",
        "risk_capacity": "위험 감당력",
        "portfolio_quality": "포트폴리오 품질",
        "crisis_signal": "위기 신호",
        "survival_bar": "생존기간 바",
        "goal_distance": "목표 거리",
        "decision_compass": "의사결정 나침반",
        "status": "상태",
        "age": "나이",
        "segment": "고객군",
        "primary_goal": "핵심 목표",
        "portfolio_note": "포트폴리오 메모",
        "real_estate_note": "부동산 메모",
        "advisor_focus": "어드바이저 초점",
        "net_worth": "순자산",
        "monthly_surplus": "월 잉여현금",
        "debt_to_income": "소득 대비 부채상환",
        "investment_exposure": "투자 노출도",
        "required_runway": "필요 생존기간",
        "portfolio_beta": "포트폴리오 베타",
        "largest_holding": "최대 보유비중",
        "real_estate_ltv": "부동산 LTV",
        "data": "데이터",
        "model": "모델",
        "ai_interpretation": "AI 해석",
        "decision": "의사결정",
        "memory": "메모리",
        "customer_purpose": "고객 목적",
        "strategy": "전략",
        "user": "고객 목적",
        "decision_path_data": "소득, 지출, 자산, 부채, 목표, 포트폴리오, 부동산",
        "decision_path_model": "개인 재무 엔진 + 포트폴리오 품질 + 부동산 스트레스",
        "decision_path_evidence": "생존기간, 잉여현금, DTI, 노출도, 목표 진행률, 베타, LTV",
        "decision_path_memory": "PDF를 저장하고 다음 리뷰와 비교",
        "asset_cash": "현금",
        "asset_taxable": "과세 투자자산",
        "asset_retirement": "은퇴자산",
        "asset_real_estate": "부동산",
        "stress_base": "기준",
        "stress_stock_20": "주식 -20%",
        "stress_stock_30": "주식 -30%",
        "stress_stock_40": "주식 -40%",
        "strong": "강함",
        "stable": "안정",
        "watch": "주의",
        "at_risk": "위험",
        "save_memory": "이 리포트 날짜, 가장 약한 신호, 다음 행동을 저장하세요.",
        "review_memory": "소득, 시장, 부채, 가족상황이 크게 바뀌면 다시 검토하세요.",
        "disclaimer": "교육 및 정보 제공용입니다. 금융, 투자, 법률, 세무, 회계 또는 전문 조언이 아닙니다.",
    },
}

PHRASES = {
    "runway_ok_equity_risk": {
        "en": "Runway is acceptable, but equity drawdown risk is the main decision constraint.",
        "ko": "생존기간은 충분하지만 주식 하락 위험이 가장 중요한 의사결정 제약입니다.",
    },
    "runway_gap": {
        "en": "Cash runway is below the required planning window, so liquidity protection comes first.",
        "ko": "현금 생존기간이 필요한 계획기간보다 짧아 유동성 보호가 먼저입니다.",
    },
    "cash_flow_negative": {
        "en": "Monthly cash flow is negative, so the plan needs expense, debt, or income repair before more risk.",
        "ko": "월 현금흐름이 음수이므로 추가 위험보다 지출, 부채, 소득 구조 개선이 먼저입니다.",
    },
    "debt_pressure": {
        "en": "Debt pressure is the dominant weakness and should be stress-tested before growth decisions.",
        "ko": "부채 압박이 가장 큰 약점이므로 성장 결정 전에 스트레스 테스트가 필요합니다.",
    },
    "cash_thin": {
        "en": "Cash reserve is too thin for the current risk profile.",
        "ko": "현재 위험구조에 비해 현금 준비금이 얇습니다.",
    },
    "market_concentration": {
        "en": "Market exposure is high relative to total assets and should be reviewed for concentration risk.",
        "ko": "총자산 대비 시장 노출이 높아 집중 위험 검토가 필요합니다.",
    },
    "foundation_strong": {
        "en": "The foundation is strong enough to move from protection into scenario planning.",
        "ko": "기초 체력이 좋아 보호 단계에서 시나리오 계획 단계로 넘어갈 수 있습니다.",
    },
    "usable_watch_weakest": {
        "en": "The plan is usable, but the next step should focus on the weakest readiness signal.",
        "ko": "계획은 사용 가능하지만 다음 단계는 가장 약한 준비 신호에 집중해야 합니다.",
    },
    "monthly_runway_checkpoint": {
        "en": "Set a monthly runway checkpoint until earned income resumes.",
        "ko": "근로소득이 재개될 때까지 매월 생존기간을 점검하세요.",
    },
    "move_cash_like": {
        "en": "Move enough assets to cash-like reserves to cover the runway gap.",
        "ko": "생존기간 부족분을 메우도록 일부 자산을 현금성 준비금으로 옮기세요.",
    },
    "stock_stress": {
        "en": "Run a -25% and -40% stock stress test before relying on portfolio withdrawals.",
        "ko": "포트폴리오 인출에 기대기 전에 주식 -25%와 -40% 스트레스를 확인하세요.",
    },
    "build_six_months": {
        "en": "Build or reserve at least six months of living expenses before increasing portfolio risk.",
        "ko": "포트폴리오 위험을 늘리기 전에 최소 6개월 생활비를 확보하거나 분리하세요.",
    },
    "repair_cash_flow": {
        "en": "Repair monthly cash flow with expense cuts, income bridge, or debt payment restructuring.",
        "ko": "지출 축소, 소득 브리지, 부채상환 구조 조정으로 월 현금흐름을 복구하세요.",
    },
    "review_debt_pressure": {
        "en": "Review debt-service pressure under one income shock and one rate shock.",
        "ko": "소득 충격 1개와 금리 충격 1개에서 부채상환 압박을 확인하세요.",
    },
    "reduce_concentration": {
        "en": "Reduce single-theme concentration risk by defining max allocation limits.",
        "ko": "최대 배분 한도를 정해 단일 테마 집중 위험을 낮추세요.",
    },
    "model_real_estate_stress": {
        "en": "Model vacancy, maintenance, and refinancing stress for the real estate position.",
        "ko": "부동산 포지션에 대해 공실, 유지비, 리파이낸싱 스트레스를 모델링하세요.",
    },
    "goal_90_day": {
        "en": "Break the main goal into a 90-day funding target and a long-term target.",
        "ko": "핵심 목표를 90일 자금 목표와 장기 목표로 나누세요.",
    },
    "memory_save": {
        "en": "Save this report as a Memory checkpoint and compare it with the next review.",
        "ko": "이 리포트를 메모리 체크포인트로 저장하고 다음 리뷰와 비교하세요.",
    },
    "protect_cash": {"en": "Protect cash runway", "ko": "현금 생존기간 보호"},
    "reduce_risk": {"en": "Reduce concentration risk", "ko": "집중 위험 축소"},
    "repair_debt": {"en": "Repair debt pressure", "ko": "부채 압박 개선"},
    "scenario_plan": {"en": "Move to scenario planning", "ko": "시나리오 계획으로 이동"},
    "rebuild_goal": {"en": "Rebuild goal funding", "ko": "목표 자금 재구축"},
}


@dataclass(frozen=True)
class VirtualClient:
    client_id: str
    name: str
    age: int
    currency: str
    segment: dict[str, str]
    situation: dict[str, str]
    goal: dict[str, str]
    portfolio_note: dict[str, str]
    real_estate_note: dict[str, str]
    advisor_focus: dict[str, str]
    profile: PersonalFinanceProfile
    portfolio_sample: list[dict[str, Any]]
    real_estate_sample: dict[str, Any]

    def text(self, field: str, language: str = "en") -> str:
        value = getattr(self, field)
        if isinstance(value, dict):
            return value.get(normalize_language(language), value.get("en", ""))
        return str(value)


def normalize_language(language: str | None) -> str:
    return language if language in SUPPORTED_LANGUAGES else "en"


def label(key: str, language: str = "en") -> str:
    language = normalize_language(language)
    return LABELS[language].get(key, LABELS["en"].get(key, key))


def phrase(key: str, language: str = "en") -> str:
    language = normalize_language(language)
    return PHRASES[key].get(language, PHRASES[key]["en"])


def profile_from_dict(values: dict[str, Any]) -> PersonalFinanceProfile:
    return PersonalFinanceProfile(
        monthly_income=float(values.get("monthly_income", 0)),
        fixed_expenses=float(values.get("fixed_expenses", 0)),
        variable_expenses=float(values.get("variable_expenses", 0)),
        cash_savings=float(values.get("cash_savings", 0)),
        taxable_investments=float(values.get("taxable_investments", 0)),
        retirement_accounts=float(values.get("retirement_accounts", 0)),
        real_estate_value=float(values.get("real_estate_value", 0)),
        credit_card_debt=float(values.get("credit_card_debt", 0)),
        student_loan=float(values.get("student_loan", 0)),
        auto_loan=float(values.get("auto_loan", 0)),
        mortgage=float(values.get("mortgage", 0)),
        monthly_debt_payment=float(values.get("monthly_debt_payment", 0)),
        monthly_savings_goal=float(values.get("monthly_savings_goal", 0)),
        target_goal_amount=float(values.get("target_goal_amount", 0)),
        current_goal_savings=float(values.get("current_goal_savings", 0)),
        investment_risk_score=float(values.get("investment_risk_score", 0)),
        runway_target_months=float(values.get("runway_target_months", 6)),
        study_months_remaining=float(values.get("study_months_remaining", 0)),
    )


def virtual_clients(data_path: Path | None = None) -> list[VirtualClient]:
    path = data_path or DATA_PATH
    raw_clients = json.loads(path.read_text(encoding="utf-8"))
    return [
        VirtualClient(
            client_id=item["client_id"],
            name=item["name"],
            age=int(item["age"]),
            currency=item.get("currency", "USD"),
            segment=item["segment"],
            situation=item["situation"],
            goal=item["goal"],
            portfolio_note=item["portfolio_note"],
            real_estate_note=item["real_estate_note"],
            advisor_focus=item["advisor_focus"],
            profile=profile_from_dict(item["profile"]),
            portfolio_sample=item.get("portfolio_sample", []),
            real_estate_sample=item.get("real_estate_sample", {}),
        )
        for item in raw_clients
    ]


def clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def score_key(score: float) -> str:
    if score >= 75:
        return "strong"
    if score >= 60:
        return "stable"
    if score >= 45:
        return "watch"
    return "at_risk"


def score_label(score: float, language: str = "en") -> str:
    return label(score_key(score), language)


def risk_tone(score: float) -> str:
    if score >= 75:
        return "good"
    if score >= 60:
        return "mid"
    if score >= 45:
        return "watch"
    return "risk"


def money_text(value: float | int | None, currency: str, language: str = "en") -> str:
    if value is None:
        return "N/A"
    amount = float(value)
    if currency == "KRW":
        return f"KRW {amount:,.0f}" if language == "en" else f"{amount:,.0f}원"
    return f"USD {amount:,.0f}"


def pct(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.1f}%"


def stress_capital(profile: PersonalFinanceProfile, stock_drawdown: float, property_drawdown: float = 0.10) -> float:
    total_debt = profile.credit_card_debt + profile.student_loan + profile.auto_loan + profile.mortgage
    return (
        profile.cash_savings
        + profile.taxable_investments * (1 - stock_drawdown)
        + profile.retirement_accounts * (1 - stock_drawdown * 0.50)
        + profile.real_estate_value * (1 - property_drawdown)
        - total_debt
    )


def portfolio_summary(client: VirtualClient) -> dict[str, Any]:
    positions = client.portfolio_sample
    if not positions:
        return {
            "positions": [],
            "weighted_beta": 0.0,
            "weighted_upside": None,
            "largest_weight": 0.0,
            "sector_concentration": 0.0,
            "score": 50.0,
            "valuation_available_weight": 0.0,
        }

    total_weight = sum(float(item.get("weight") or 0) for item in positions) or 1.0
    weighted_beta = sum(float(item.get("weight") or 0) * float(item.get("beta") or 0) for item in positions) / total_weight
    available_weight = sum(float(item.get("weight") or 0) for item in positions if item.get("valuation_upside") is not None)
    weighted_upside = None
    if available_weight > 0:
        weighted_upside = (
            sum(float(item.get("weight") or 0) * float(item.get("valuation_upside") or 0) for item in positions if item.get("valuation_upside") is not None)
            / available_weight
        )
    sector_weights: dict[str, float] = {}
    for item in positions:
        sector = str(item.get("sector") or "Other")
        sector_weights[sector] = sector_weights.get(sector, 0.0) + float(item.get("weight") or 0) / total_weight

    largest_weight = max(float(item.get("weight") or 0) / total_weight for item in positions)
    sector_concentration = max(sector_weights.values()) if sector_weights else 0.0
    upside_bonus = 0.0 if weighted_upside is None else weighted_upside * 80
    score = clamp_percent(
        78
        + upside_bonus
        - max(0.0, weighted_beta - 1.0) * 24
        - max(0.0, largest_weight - 0.25) * 90
        - max(0.0, sector_concentration - 0.45) * 45
    )
    return {
        "positions": positions,
        "weighted_beta": weighted_beta,
        "weighted_upside": weighted_upside,
        "largest_weight": largest_weight,
        "sector_concentration": sector_concentration,
        "sector_weights": sector_weights,
        "score": score,
        "valuation_available_weight": available_weight / total_weight,
    }


def real_estate_summary(client: VirtualClient, result: dict[str, Any]) -> dict[str, Any]:
    sample = client.real_estate_sample or {}
    value = client.profile.real_estate_value
    total_assets = float(result["total_assets"]) or 1.0
    ltv = float(sample.get("loan_to_value") or 0)
    cash_flow = float(sample.get("cash_flow") or 0)
    value_share = value / total_assets
    score = 78 - ltv * 55 - max(0.0, -cash_flow / max(client.profile.monthly_income, 1)) * 35
    if value_share > 0.55:
        score -= 10
    if int(sample.get("property_count") or 0) == 0:
        score = 70
    return {
        "property_count": int(sample.get("property_count") or 0),
        "loan_to_value": ltv,
        "cash_flow": cash_flow,
        "value_share": value_share,
        "score": clamp_percent(score),
    }


def diagnosis_key(client: VirtualClient, result: dict[str, Any]) -> str:
    score = float(result["planning_health_score"])
    emergency = float(result["emergency_months"])
    exposure = float(result["investment_exposure_ratio"])
    dti = float(result["debt_to_income"])
    surplus = float(result["monthly_surplus"])
    no_income = bool(result["no_income_mode"])
    if no_income:
        if emergency >= float(result["required_runway_months"]) and exposure >= 0.60:
            return "runway_ok_equity_risk"
        if emergency < float(result["required_runway_months"]):
            return "runway_gap"
    if surplus < 0:
        return "cash_flow_negative"
    if dti > 0.36:
        return "debt_pressure"
    if emergency < 3:
        return "cash_thin"
    if exposure > 0.70:
        return "market_concentration"
    if score >= 75:
        return "foundation_strong"
    return "usable_watch_weakest"


def advisor_action_keys(client: VirtualClient, result: dict[str, Any], portfolio: dict[str, Any], real_estate: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    profile = client.profile
    emergency = float(result["emergency_months"])
    required = float(result["required_runway_months"])
    exposure = float(result["investment_exposure_ratio"])
    dti = float(result["debt_to_income"])
    surplus = float(result["monthly_surplus"])
    goal_progress = float(result["goal_progress"])
    no_income = bool(result["no_income_mode"])
    real_estate_ratio = profile.real_estate_value / max(float(result["total_assets"]), 1)

    if no_income:
        keys.append("monthly_runway_checkpoint")
        if emergency < required:
            keys.append("move_cash_like")
        if exposure >= 0.60:
            keys.append("stock_stress")
    if emergency < 6 and not no_income:
        keys.append("build_six_months")
    if surplus < 0 and not no_income:
        keys.append("repair_cash_flow")
    if dti > 0.36:
        keys.append("review_debt_pressure")
    if exposure > 0.70 or float(portfolio["largest_weight"]) > 0.30 or float(portfolio["sector_concentration"]) > 0.55:
        keys.append("reduce_concentration")
    if real_estate_ratio > 0.55 or float(real_estate["loan_to_value"]) > 0.65:
        keys.append("model_real_estate_stress")
    if goal_progress < 0.40:
        keys.append("goal_90_day")
    keys.append("memory_save")

    deduped: list[str] = []
    for key in keys:
        if key not in deduped:
            deduped.append(key)
    return deduped[:5]


def weakest_signal(result: dict[str, Any], portfolio: dict[str, Any], real_estate: dict[str, Any], language: str = "en") -> dict[str, Any]:
    signals = [
        (label("cash_runway", language), float(result["runway_readiness_score"])),
        (label("goal_progress", language), float(result["goal_score"])),
        (label("risk_capacity", language), float(result["risk_capacity_score"])),
        (label("portfolio_quality", language), float(portfolio["score"])),
        (label("real_estate_ltv", language), float(real_estate["score"])),
    ]
    name, score = min(signals, key=lambda item: item[1])
    return {"label": name, "score": score, "tone": risk_tone(score)}


def decision_compass_key(result: dict[str, Any], portfolio: dict[str, Any]) -> str:
    if float(result["runway_readiness_score"]) < 80:
        return "protect_cash"
    if float(result["debt_score"]) < 50:
        return "repair_debt"
    if float(portfolio["largest_weight"]) > 0.30 or float(portfolio["sector_concentration"]) > 0.55:
        return "reduce_risk"
    if float(result["goal_score"]) < 40:
        return "rebuild_goal"
    return "scenario_plan"


def evidence_items(client: VirtualClient, result: dict[str, Any], portfolio: dict[str, Any], real_estate: dict[str, Any], language: str = "en") -> list[str]:
    profile = client.profile
    month_unit = label("months", language)
    return [
        f"{label('monthly_surplus', language)}: {money_text(float(result['monthly_surplus']), client.currency, language)}",
        f"{label('cash_runway', language)}: {float(result['emergency_months']):.1f} {month_unit}",
        f"{label('required_runway', language)}: {float(result['required_runway_months']):.1f} {month_unit}",
        f"{label('debt_to_income', language)}: {float(result['debt_to_income']) * 100:.1f}%",
        f"{label('goal_progress', language)}: {float(result['goal_progress']) * 100:.1f}%",
        f"{label('investment_exposure', language)}: {float(result['investment_exposure_ratio']) * 100:.1f}%",
        f"{label('portfolio_beta', language)}: {float(portfolio['weighted_beta']):.2f}",
        f"{label('largest_holding', language)}: {float(portfolio['largest_weight']) * 100:.1f}%",
        f"{label('real_estate_ltv', language)}: {float(real_estate['loan_to_value']) * 100:.1f}%",
        f"{label('market_stress_capital', language)}: {money_text(stress_capital(profile, 0.30), client.currency, language)}",
    ]


def build_client_report(client: VirtualClient, language: str = "en") -> dict[str, Any]:
    language = normalize_language(language)
    result = calculate_personal_finance(client.profile)
    profile = client.profile
    portfolio = portfolio_summary(client)
    real_estate = real_estate_summary(client, result)
    diagnosis = phrase(diagnosis_key(client, result), language)
    action_keys = advisor_action_keys(client, result, portfolio, real_estate)
    actions = [phrase(key, language) for key in action_keys]
    score = float(result["planning_health_score"])
    emergency = float(result["emergency_months"])
    required = float(result["required_runway_months"])
    exposure = float(result["investment_exposure_ratio"])
    cash_ratio = float(result["cash_to_assets_ratio"])
    property_ratio = profile.real_estate_value / max(float(result["total_assets"]), 1)
    goal_progress = float(result["goal_progress"])
    crisis = weakest_signal(result, portfolio, real_estate, language)
    compass_key = decision_compass_key(result, portfolio)

    scorecards = [
        {
            "label": label("planning_health", language),
            "value": f"{score:.1f}/100",
            "score": score,
            "detail": "Composite readiness: liquidity, debt, savings/runway, goals, and risk capacity."
            if language == "en"
            else "유동성, 부채, 저축/생존기간, 목표, 위험 감당력을 합친 준비도입니다.",
        },
        {
            "label": label("survival_bar", language),
            "value": f"{emergency:.1f} mo" if language == "en" else f"{emergency:.1f}개월",
            "score": clamp_percent(emergency / max(required, 1) * 100),
            "detail": f"Required planning runway: {required:.1f} months."
            if language == "en"
            else f"필요 계획 생존기간: {required:.1f}개월.",
        },
        {
            "label": label("goal_distance", language),
            "value": f"{goal_progress * 100:.1f}%",
            "score": clamp_percent(goal_progress * 100),
            "detail": "Distance to the selected major life goal."
            if language == "en"
            else "선택한 핵심 인생 목표까지의 거리입니다.",
        },
        {
            "label": label("risk_capacity", language),
            "value": f"{float(result['risk_capacity_score']):.1f}/100",
            "score": float(result["risk_capacity_score"]),
            "detail": "Reads liquidity, debt, savings behavior, and current investment risk together."
            if language == "en"
            else "유동성, 부채, 저축 습관, 현재 투자위험을 함께 봅니다.",
        },
        {
            "label": label("portfolio_quality", language),
            "value": f"{float(portfolio['score']):.1f}/100",
            "score": float(portfolio["score"]),
            "detail": "Uses sample holdings, beta, valuation availability, and concentration."
            if language == "en"
            else "샘플 보유종목, 베타, 가치평가 가능 비중, 집중도를 사용합니다.",
        },
        {
            "label": label("crisis_signal", language),
            "value": f"{crisis['label']} {crisis['score']:.0f}",
            "score": float(crisis["score"]),
            "detail": "Lowest readiness signal in this client report."
            if language == "en"
            else "이 고객 리포트에서 가장 낮은 준비 신호입니다.",
        },
    ]

    report = {
        "language": language,
        "client": client,
        "result": result,
        "portfolio": portfolio,
        "real_estate": real_estate,
        "status": score_label(score, language),
        "status_key": score_key(score),
        "tone": risk_tone(score),
        "diagnosis": diagnosis,
        "actions": actions,
        "action_keys": action_keys,
        "evidence": evidence_items(client, result, portfolio, real_estate, language),
        "scorecards": scorecards,
        "weakest_signal": crisis,
        "decision_compass": phrase(compass_key, language),
        "asset_mix": [
            {"Asset": label("asset_cash", language), "Amount": profile.cash_savings, "Share": cash_ratio},
            {"Asset": label("asset_taxable", language), "Amount": profile.taxable_investments, "Share": exposure},
            {
                "Asset": label("asset_retirement", language),
                "Amount": profile.retirement_accounts,
                "Share": profile.retirement_accounts / max(float(result["total_assets"]), 1),
            },
            {"Asset": label("asset_real_estate", language), "Amount": profile.real_estate_value, "Share": property_ratio},
        ],
        "stress": [
            {"Scenario": label("stress_base", language), "Capital": float(result["net_worth"])},
            {"Scenario": label("stress_stock_20", language), "Capital": stress_capital(profile, 0.20)},
            {"Scenario": label("stress_stock_30", language), "Capital": stress_capital(profile, 0.30)},
            {"Scenario": label("stress_stock_40", language), "Capital": stress_capital(profile, 0.40)},
        ],
    }
    report["report_text"] = build_report_text(report, language)
    return report


def build_all_client_reports(language: str = "en") -> list[dict[str, Any]]:
    return [build_client_report(client, language) for client in virtual_clients()]


def build_report_text(report: dict[str, Any], language: str | None = None) -> str:
    language = normalize_language(language or report.get("language", "en"))
    client: VirtualClient = report["client"]
    result = report["result"]
    now_text = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"{label('advisor_report', language)} - {client.client_id} {client.name}",
        f"{label('generated', language)}: {now_text}",
        f"{label('fictional', language)}",
        "",
        f"1. {label('situation', language)}",
        f"- {label('segment', language)}: {client.text('segment', language)}",
        f"- {label('age', language)}: {client.age}",
        f"- {label('situation', language)}: {client.text('situation', language)}",
        f"- {label('primary_goal', language)}: {client.text('goal', language)}",
        f"- {label('portfolio_note', language)}: {client.text('portfolio_note', language)}",
        f"- {label('real_estate_note', language)}: {client.text('real_estate_note', language)}",
        "",
        f"2. {label('visual_score_reading', language)}",
        f"- {label('status', language)}: {report['status']}",
        f"- {label('planning_health', language)}: {float(result['planning_health_score']):.1f}/100",
        f"- {label('cash_runway', language)}: {float(result['emergency_months']):.1f} {label('months', language)}",
        f"- {label('net_worth', language)}: {money_text(float(result['net_worth']), client.currency, language)}",
        f"- {label('investment_exposure', language)}: {float(result['investment_exposure_ratio']) * 100:.1f}%",
        f"- {label('decision_compass', language)}: {report['decision_compass']}",
        "",
        f"3. {label('portfolio_sample', language)}",
    ]
    for holding in report["portfolio"]["positions"]:
        upside = holding.get("valuation_upside")
        valuation = "N/A" if upside is None else f"{float(upside) * 100:+.1f}%"
        lines.append(
            "- "
            f"{holding.get('symbol')} | {holding.get('name')} | "
            f"{label('sector', language)}: {holding.get('sector')} | "
            f"{label('weight', language)}: {float(holding.get('weight') or 0) * 100:.1f}% | "
            f"{label('beta', language)}: {float(holding.get('beta') or 0):.2f} | "
            f"{label('valuation', language)}: {valuation}"
        )
    lines.extend(
        [
            "",
            f"4. {label('advisor_interpretation', language)}",
            f"- {report['diagnosis']}",
            f"- {label('advisor_focus', language)}: {client.text('advisor_focus', language)}",
            "",
            f"5. {label('evidence', language)}",
        ]
    )
    lines.extend(f"- {item}" for item in report["evidence"])
    lines.extend(["", f"6. {label('recommended_decisions', language)}"])
    lines.extend(f"- {item}" for item in report["actions"])
    lines.extend(
        [
            "",
            f"7. {label('memory_checkpoint', language)}",
            f"- {label('save_memory', language)}",
            f"- {label('review_memory', language)}",
            "",
            label("disclaimer", language),
        ]
    )
    return "\n".join(lines)


def _register_pdf_fonts(language: str) -> tuple[str, str]:
    if language in _PDF_FONT_CACHE:
        return _PDF_FONT_CACHE[language]
    if language == "ko":
        candidate_paths = [
            Path(__file__).with_name("assets") / "fonts" / "NotoSansKR-Regular.otf",
            Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf"),
            Path("/System/Library/Fonts/Supplemental/NotoSansGothic-Regular.ttf"),
            Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJKkr-Regular.otf"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ]
        for font_path in candidate_paths:
            if not font_path.exists():
                continue
            try:
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont

                pdfmetrics.registerFont(TTFont("LYKoreanRegular", str(font_path)))
                _PDF_FONT_CACHE[language] = ("LYKoreanRegular", "LYKoreanRegular")
                return _PDF_FONT_CACHE[language]
            except Exception:
                continue
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont

            pdfmetrics.registerFont(UnicodeCIDFont("HYGoThic-Medium"))
            _PDF_FONT_CACHE[language] = ("HYGoThic-Medium", "HYGoThic-Medium")
            return _PDF_FONT_CACHE[language]
        except Exception:
            _PDF_FONT_CACHE[language] = ("Helvetica", "Helvetica-Bold")
            return _PDF_FONT_CACHE[language]
    _PDF_FONT_CACHE[language] = ("Helvetica", "Helvetica-Bold")
    return _PDF_FONT_CACHE[language]


def _reportlab_story_styles(language: str = "en") -> dict[str, Any]:
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch

    body_font, bold_font = _register_pdf_fonts(language)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="LYTitle",
            parent=styles["Title"],
            fontName=bold_font,
            fontSize=18,
            leading=22,
            textColor="#0f172a",
            spaceAfter=0.12 * inch,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LYSection",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=11,
            leading=14,
            textColor="#134e4a",
            spaceBefore=0.10 * inch,
            spaceAfter=0.05 * inch,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LYBody",
            parent=styles["BodyText"],
            fontName=body_font,
            fontSize=9.2,
            leading=12,
            textColor="#1f2937",
            spaceAfter=0.035 * inch,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LYSmall",
            parent=styles["BodyText"],
            fontName=body_font,
            fontSize=7.8,
            leading=10.2,
            textColor="#64748b",
        )
    )
    styles.add(
        ParagraphStyle(
            name="LYWarning",
            parent=styles["BodyText"],
            fontName=bold_font,
            fontSize=8.4,
            leading=10.8,
            textColor="#7c2d12",
            backColor="#fff7ed",
            borderPadding=6,
            spaceAfter=0.10 * inch,
        )
    )
    return styles


def _clean_pdf_text(text: Any) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _score_color(score: float) -> str:
    if score >= 75:
        return "#16a34a"
    if score >= 60:
        return "#0891b2"
    if score >= 45:
        return "#d97706"
    return "#dc2626"


def _score_bar(score: float) -> Any:
    from reportlab.graphics.shapes import Drawing, Rect

    width = 142
    height = 9
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 1, width, height - 2, fillColor="#e5e7eb", strokeColor="#e5e7eb", rx=3, ry=3))
    drawing.add(
        Rect(
            0,
            1,
            width * clamp_percent(score) / 100,
            height - 2,
            fillColor=_score_color(score),
            strokeColor=_score_color(score),
            rx=3,
            ry=3,
        )
    )
    return drawing


def _table_style(header_color: str = "#0f766e") -> list[tuple[Any, ...]]:
    from reportlab.lib import colors

    return [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.4),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]


def _story_from_report(report: dict[str, Any]) -> list[Any]:
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    language = normalize_language(report.get("language", "en"))
    body_font, bold_font = _register_pdf_fonts(language)
    styles = _reportlab_story_styles(language)
    client: VirtualClient = report["client"]
    result = report["result"]
    story: list[Any] = [
        Paragraph(_clean_pdf_text(f"{label('advisor_report', language)}: {client.name}"), styles["LYTitle"]),
        Paragraph(
            _clean_pdf_text(f"{client.client_id} - {client.text('segment', language)} - {report['status']}"),
            styles["LYSmall"],
        ),
        Spacer(1, 0.04 * inch),
        Paragraph(_clean_pdf_text(label("disclaimer", language)), styles["LYWarning"]),
    ]

    metric_rows = [
        [label("metric", language), label("reading", language)],
        [label("planning_health", language), f"{float(result['planning_health_score']):.1f}/100"],
        [label("net_worth", language), money_text(float(result["net_worth"]), client.currency, language)],
        [label("monthly_surplus", language), money_text(float(result["monthly_surplus"]), client.currency, language)],
        [label("cash_runway", language), f"{float(result['emergency_months']):.1f} {label('months', language)}"],
        [label("debt_to_income", language), f"{float(result['debt_to_income']) * 100:.1f}%"],
        [label("investment_exposure", language), f"{float(result['investment_exposure_ratio']) * 100:.1f}%"],
        [label("decision_compass", language), report["decision_compass"]],
    ]
    metric_table = Table(metric_rows, colWidths=[2.2 * inch, 3.55 * inch])
    metric_style = _table_style()
    metric_style.extend([("FONTNAME", (0, 0), (-1, -1), body_font), ("FONTNAME", (0, 0), (-1, 0), bold_font)])
    metric_table.setStyle(TableStyle(metric_style))
    story.extend([metric_table, Spacer(1, 0.10 * inch)])

    score_rows = [[label("metric", language), label("reading", language), label("visual", language)]]
    for card in report["scorecards"]:
        score_rows.append([card["label"], card["value"], _score_bar(float(card["score"]))])
    score_table = Table(score_rows, colWidths=[2.0 * inch, 1.25 * inch, 2.5 * inch])
    score_style = _table_style("#155e75")
    score_style.extend([("FONTNAME", (0, 0), (-1, -1), body_font), ("FONTNAME", (0, 0), (-1, 0), bold_font)])
    score_table.setStyle(TableStyle(score_style))
    story.extend([score_table, Spacer(1, 0.10 * inch)])

    if report["portfolio"]["positions"]:
        portfolio_rows = [[label("ticker", language), label("name", language), label("sector", language), label("weight", language), label("beta", language), label("valuation", language)]]
        for holding in report["portfolio"]["positions"]:
            upside = holding.get("valuation_upside")
            valuation = "N/A" if upside is None else f"{float(upside) * 100:+.1f}%"
            portfolio_rows.append(
                [
                    str(holding.get("symbol", "")),
                    str(holding.get("name", "")),
                    str(holding.get("sector", "")),
                    f"{float(holding.get('weight') or 0) * 100:.1f}%",
                    f"{float(holding.get('beta') or 0):.2f}",
                    valuation,
                ]
            )
        portfolio_table = Table(
            portfolio_rows,
            colWidths=[0.70 * inch, 1.85 * inch, 1.05 * inch, 0.72 * inch, 0.52 * inch, 0.78 * inch],
        )
        portfolio_style = _table_style("#0f766e")
        portfolio_style.extend([("FONTNAME", (0, 0), (-1, -1), body_font), ("FONTNAME", (0, 0), (-1, 0), bold_font)])
        portfolio_table.setStyle(TableStyle(portfolio_style))
        story.extend(
            [
                Paragraph(label("portfolio_sample", language), styles["LYSection"]),
                portfolio_table,
                Spacer(1, 0.10 * inch),
            ]
        )

    story.extend(
        [
            Paragraph(label("situation", language), styles["LYSection"]),
            Paragraph(_clean_pdf_text(client.text("situation", language)), styles["LYBody"]),
            Paragraph(label("advisor_interpretation", language), styles["LYSection"]),
            Paragraph(_clean_pdf_text(report["diagnosis"]), styles["LYBody"]),
            Paragraph(label("evidence", language), styles["LYSection"]),
        ]
    )
    for item in report["evidence"]:
        story.append(Paragraph(_clean_pdf_text(f"- {item}"), styles["LYBody"]))
    story.append(Paragraph(label("recommended_decisions", language), styles["LYSection"]))
    for item in report["actions"]:
        story.append(Paragraph(_clean_pdf_text(f"- {item}"), styles["LYBody"]))
    story.extend(
        [
            Paragraph(label("memory_checkpoint", language), styles["LYSection"]),
            Paragraph(_clean_pdf_text(label("save_memory", language)), styles["LYBody"]),
            Paragraph(_clean_pdf_text(label("review_memory", language)), styles["LYBody"]),
            Spacer(1, 0.08 * inch),
            Paragraph(_clean_pdf_text(label("fictional", language)), styles["LYSmall"]),
        ]
    )
    return story


def client_report_pdf_bytes(report: dict[str, Any]) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.48 * inch,
        leftMargin=0.48 * inch,
        topMargin=0.44 * inch,
        bottomMargin=0.44 * inch,
        title=label("advisor_report", report.get("language", "en")),
    )
    document.build(_story_from_report(report))
    return buffer.getvalue()


def all_clients_pdf_bytes(reports: list[dict[str, Any]]) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import PageBreak, SimpleDocTemplate

    language = normalize_language(reports[0].get("language", "en") if reports else "en")
    buffer = BytesIO()
    story: list[Any] = []
    for index, report in enumerate(reports):
        if index:
            story.append(PageBreak())
        story.extend(_story_from_report(report))
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.48 * inch,
        leftMargin=0.48 * inch,
        topMargin=0.44 * inch,
        bottomMargin=0.44 * inch,
        title=label("all_reports", language),
    )
    document.build(story)
    return buffer.getvalue()


def text_report_pdf_bytes(title: str, body: str, subtitle: str = "", language: str = "en") -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    language = normalize_language(language)
    styles = _reportlab_story_styles(language)
    buffer = BytesIO()
    story: list[Any] = [Paragraph(_clean_pdf_text(title), styles["LYTitle"])]
    if subtitle:
        story.extend([Paragraph(_clean_pdf_text(subtitle), styles["LYSmall"]), Spacer(1, 0.08 * inch)])
    story.append(Paragraph(_clean_pdf_text(label("disclaimer", language)), styles["LYWarning"]))
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 0.06 * inch))
        elif line[:2].isdigit() and "." in line[:4]:
            story.append(Paragraph(_clean_pdf_text(line), styles["LYSection"]))
        else:
            story.append(Paragraph(_clean_pdf_text(line), styles["LYBody"]))

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.50 * inch,
        leftMargin=0.50 * inch,
        topMargin=0.50 * inch,
        bottomMargin=0.50 * inch,
        title=title,
    )
    document.build(story)
    return buffer.getvalue()

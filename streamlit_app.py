import math
import os
import json
import base64
from html import escape
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent
from typing import Any
from urllib.parse import urlencode

import altair as alt
import pandas as pd
import requests
import streamlit as st
import yfinance as yf


st.set_page_config(page_title="ToxiGuard-NORA", layout="wide")

LANGUAGE_OPTIONS = {
    "en": "English",
    "ko": "한국어",
}

LANGUAGE_ALIASES = {
    "en": "en",
    "english": "en",
    "ko": "ko",
    "kr": "ko",
    "korean": "ko",
    "한국어": "ko",
}

KO_TRANSLATIONS = {
    "Language": "언어",
    "English": "English",
    "한국어": "한국어",
    "Default language is English. Korean mode translates the primary workflow, navigation, and key input surfaces.": "기본 언어는 영어입니다. 한국어 모드는 주요 흐름, 내비게이션, 핵심 입력 화면을 한국어로 전환합니다.",
    "Open or close this sidebar with the arrow in the upper-left corner.": "왼쪽 위 화살표로 사이드바를 열거나 닫을 수 있습니다.",
    "View Life Design Intro": "Life Design 인트로 보기",
    "Ver.2 Module": "Ver.2 모듈",
    "Use the REIT Analysis tab in the main screen.": "메인 화면의 REIT Analysis 메뉴를 사용하세요.",
    "Compare List": "비교 목록",
    "No stocks selected for comparison.": "비교할 종목이 아직 없습니다.",
    "Portfolio List": "포트폴리오 목록",
    "No stocks in portfolio.": "포트폴리오에 담긴 종목이 없습니다.",
    "Developer": "개발자",
    "Send a comment": "의견 보내기",
    "Write feedback or an issue to review later.": "나중에 검토할 의견이나 이슈를 적어 주세요.",
    "Save Comment": "의견 저장",
    "Comment saved in this session.": "이번 세션에 의견이 저장되었습니다.",
    "Please enter a comment first.": "먼저 의견을 입력해 주세요.",
    "Saved comments": "저장된 의견",
    "Your Life. Your Money. Your Future.": "당신의 삶. 당신의 돈. 당신의 미래.",
    "Personal Decision Intelligence Application": "개인 의사결정 인텔리전스 앱",
    "Design Your": "설계하세요",
    "Financial Life": "금융 생활",
    "ToxiGuard-NORA is a Personal Decision Intelligence Application for financial foundation, goals, market assets, real estate, scenarios, risk, evidence, decisions, and memory.": "ToxiGuard-NORA는 재무 기반, 목표, 시장 자산, 부동산, 시나리오, 위험, 근거, 결정, 메모리를 연결하는 개인 의사결정 인텔리전스 앱입니다.",
    "See Your": "나의",
    "Financial Path": "금융 경로",
    "What Does the Customer Want?": "고객은 무엇을 원하는가?",
    "NORA begins with purpose, then reads the plan and current situation.": "NORA는 목적에서 시작해 플랜과 현재 상황을 읽습니다.",
    "Customer Purpose": "고객 목적",
    "Purpose": "목적",
    "Plan": "플랜",
    "Situation": "상황",
    "What does the customer want?": "고객은 무엇을 원하는가?",
    "Purpose path": "목적 경로",
    "Current reality": "현재 현실",
    "NORA Purpose Map": "NORA 목적 맵",
    "Why": "이유",
    "Path": "경로",
    "Inputs": "입력",
    "Proof": "증명",
    "Review": "검토",
    "NORA Purpose Control Center": "NORA 목적 컨트롤 센터",
    "NORA starts with what the customer wants, then connects the plan, current situation, evidence, decision, and memory.": "NORA는 고객이 원하는 것에서 시작한 뒤 플랜, 현재 상황, 근거, 결정, 메모리를 연결합니다.",
    "Clarify the desired outcome before looking at numbers.": "숫자를 보기 전에 원하는 결과를 먼저 분명히 합니다.",
    "Turn purpose into a path, sequence, and review rhythm.": "목적을 경로, 순서, 점검 리듬으로 바꿉니다.",
    "Read capital, income state, portfolio, real estate, liquidity, and risks.": "자본, 소득 상태, 포트폴리오, 부동산, 유동성, 위험을 읽습니다.",
    "Keep formulas, assumptions, and warnings inspectable.": "공식, 가정, 경고를 확인 가능하게 유지합니다.",
    "Frame next action without pretending to be professional advice.": "전문 조언처럼 단정하지 않고 다음 행동을 정리합니다.",
    "Save reports, diary notes, and review history for later reasoning.": "리포트, 다이어리 노트, 검토 이력을 이후 추론을 위해 저장합니다.",
    "Desired outcome, time horizon, values, constraints, and decision question.": "원하는 결과, 기간, 가치관, 제약조건, 의사결정 질문.",
    "Goal path, required resources, sequence, and review rhythm.": "목표 경로, 필요한 자원, 실행 순서, 점검 리듬.",
    "Current capital, income state, spending, portfolio, real estate, liquidity, and risks.": "현재 자본, 소득 상태, 지출, 포트폴리오, 부동산, 유동성, 위험.",
    "Customer purpose comes before data.": "데이터보다 고객 목적이 먼저입니다.",
    "NORA asks purpose first, then turns the plan and situation into evidence.": "NORA는 목적을 먼저 묻고, 플랜과 상황을 근거로 바꿉니다.",
    "NORA starts with the customer purpose, then checks the plan and current situation before any model.": "NORA는 고객의 목적에서 시작하고, 어떤 모델보다 먼저 플랜과 현재 상황을 확인합니다.",
    "A calm visual map for current situation, direction, crisis signals, and memory.": "현재 상황, 목표 방향, 위험 신호, 메모리를 차분하게 보여주는 시각 맵입니다.",
    "Current Situation": "현재 상황",
    "Capital, cash flow, portfolio, and goal context in one view.": "자본, 현금흐름, 포트폴리오, 목표 맥락을 한눈에 봅니다.",
    "Direction": "목표 방향",
    "What path needs attention next.": "다음에 집중해야 할 경로를 확인합니다.",
    "Crisis Signals": "위험 신호",
    "Where liquidity, concentration, rates, or market shocks could interrupt the plan.": "유동성, 집중도, 금리, 시장 충격이 계획을 끊을 수 있는 지점을 봅니다.",
    "Use the visual signals first. Details appear when you hover or click.": "먼저 시각 신호를 보고, 세부 내용은 마우스를 올리거나 클릭할 때 확인하세요.",
    "Open Dashboard": "대시보드 열기",
    "Educational prototype only; not financial, investment, legal, or tax advice.": "교육용 프로토타입입니다. 금융, 투자, 법률, 세무 조언이 아닙니다.",
    "Start Your Life Map": "라이프 맵 시작",
    "Explore Dashboard": "대시보드 살펴보기",
    "Enter ToxiGuard-NORA Dashboard": "ToxiGuard-NORA 대시보드로 들어가기",
    "Build, review, and improve your financial life with real examples.": "실제 예시로 금융 생활을 만들고, 점검하고, 개선하세요.",
    "Life Design Dashboard": "라이프 설계 대시보드",
    "Income": "수입",
    "Cash Flow": "현금흐름",
    "Savings": "저축",
    "Liquidity": "유동성",
    "Risk": "위험",
    "Protection": "보호",
    "Assets": "자산",
    "Portfolio": "포트폴리오",
    "Goals": "목표",
    "Planning": "계획",
    "Diary": "다이어리",
    "Reflection": "회고",
    "Stock Valuation": "주식 가치평가",
    "Fair value, valuation status, and real market context.": "적정가치, 가치평가 상태, 실제 시장 맥락.",
    "Find Stock for Portfolio": "포트폴리오 종목 찾기",
    "Ticker or company search with valuation, risk, and portfolio action.": "티커 또는 회사명으로 가치평가, 위험, 포트폴리오 행동을 확인합니다.",
    "Ticker or company name": "티커 또는 회사명",
    "Ticker or company name: NVDA, AAPL, 삼성전자, NAVER": "티커 또는 회사명: NVDA, AAPL, 삼성전자, NAVER",
    "Search and Value Stock": "검색 및 가치평가",
    "Portfolio valuation lens": "포트폴리오 가치평가 렌즈",
    "Upside": "상승여력",
    "Current price": "현재가",
    "blended fair value": "종합 적정가치",
    "Risk": "위험",
    "drives the volatility read for portfolio fit.": "는 포트폴리오 적합성의 변동성 판단에 사용됩니다.",
    "Valuation Models": "가치평가 모델",
    "Income, asset, and market approaches are checked when source inputs are available.": "입력값이 있으면 수익, 자산, 시장 접근법을 함께 확인합니다.",
    "Growth / Quality": "성장 / 퀄리티",
    "are compressed into one visual signal.": "를 하나의 시각 신호로 압축합니다.",
    "Price": "가격",
    "Fair": "적정가치",
    "Modern Valuation Radar": "현대식 가치평가 레이더",
    "This radar summarizes the triangulation result into three readable dimensions: value opportunity, beta-adjusted risk balance, and growth/quality signal.": "이 레이더는 삼각 가치평가 결과를 가치 기회, 베타 조정 위험 균형, 성장/퀄리티 신호로 요약합니다.",
    "Value Opportunity": "가치 기회",
    "Risk Balance": "위험 균형",
    "Valuation radar chart": "가치평가 레이더 차트",
    "Open valuation basis": "가치평가 근거 열기",
    "Search another company": "다른 회사 검색",
    "Enter a stock ticker": "주식 티커 입력",
    "Search": "검색",
    "Analyze Ticker": "티커 분석",
    "REIT Analytics": "REIT 분석",
    "Income, real estate exposure, and rate sensitivity lens.": "소득, 부동산 노출, 금리 민감도 관점.",
    "Portfolio Diversification": "포트폴리오 분산",
    "Risk, covariance, correlation, and complementarity.": "위험, 공분산, 상관관계, 보완성.",
    "Financial Health": "재무 건강도",
    "Cash flow, savings, debt, liquidity, and capacity.": "현금흐름, 저축, 부채, 유동성, 감당 능력.",
    "Financial Diary": "금융 다이어리",
    "Advisor Reports": "어드바이저 리포트",
    "Advisor": "어드바이저",
    "Evidence": "근거",
    "Status": "상태",
    "Age": "나이",
    "Currency": "통화",
    "Save snapshots, notes, next actions, and reflection.": "스냅샷, 메모, 다음 행동, 회고 저장.",
    "AI Scenario Readiness": "AI 시나리오 준비도",
    "Prepare structured context for future reasoning assistants.": "향후 추론형 AI를 위한 구조화된 맥락 준비.",
    "Click the image buttons on desktop or Enter ToxiGuard-NORA Dashboard on mobile. Educational and informational use only; not financial, investment, legal, or tax advice.": "데스크톱에서는 이미지 버튼을, 모바일에서는 ToxiGuard-NORA 대시보드 진입 버튼을 누르세요. 교육 및 정보 제공용이며 금융, 투자, 법률, 세무 조언이 아닙니다.",
    "Life": "라이프",
    "Finance": "재무",
    "Diary": "다이어리",
    "Client": "고객",
    "Search": "검색",
    "Compare": "비교",
    "REIT": "REIT",
    "Details": "계산",
    "Scenario": "시나리오",
    "AI Coach": "AI 코치",
    "Guide": "가이드",
    "Settings": "설정",
    "Context": "맥락",
    "Market": "시장",
    "Analysis": "분석",
    "Stress Test": "스트레스 테스트",
    "Rule-Based Beta": "규칙 기반 베타",
    "Memory": "메모리",
    "Personal Memory": "개인 메모리",
    "Mobile App Mode · Orbit V2": "모바일 앱 모드 · Orbit V2",
    "Port": "자산",
    "Life Context": "라이프 맥락",
    "Finance Readiness": "재무 준비도",
    "Portfolio Check": "포트폴리오 점검",
    "Diary Memory": "다이어리 메모리",
    "Scenario Lab": "시나리오 실험실",
    "Market Search": "시장 검색",
    "Calculation Details": "계산 근거",
    "Start with Finance or Search.": "재무 또는 검색에서 시작하세요.",
    "Check surplus, reserve, debt, and savings.": "잉여 현금, 비상자금, 부채, 저축을 확인하세요.",
    "Enter shares and average purchase price.": "보유 수량과 평균 매입가를 입력하세요.",
    "Ask one focused question from your current data.": "현재 데이터 기준으로 한 가지 질문을 던져 보세요.",
    "Save one short next action after review.": "검토 후 짧은 다음 행동 하나를 저장하세요.",
    "Run one downside stress test.": "하방 스트레스 테스트를 하나 실행하세요.",
    "Search a ticker, then add it to Portfolio.": "티커를 검색한 뒤 포트폴리오에 추가하세요.",
    "Compare up to three selected stocks.": "선택한 종목을 최대 3개까지 비교하세요.",
    "Use REIT signals as sector education.": "REIT 신호를 섹터 학습용으로 활용하세요.",
    "Review formulas before trusting outputs.": "결과를 신뢰하기 전에 공식을 확인하세요.",
    "Check API and macro assumptions.": "API와 거시 가정을 확인하세요.",
    "Use this for professor/demo walkthroughs.": "교수님/데모 설명용으로 사용하세요.",
    "Review virtual clients and export advisor PDF reports.": "가상 고객을 검토하고 어드바이저 PDF 리포트를 내보내세요.",
    "Review virtual clients through the ToxiGuard-NORA decision architecture and export PDF reports.": "ToxiGuard-NORA 의사결정 아키텍처로 가상 고객을 검토하고 PDF 리포트를 내보내세요.",
    "These fictional reports use the existing Personal Finance engine plus a rule-based advisor layer. They are educational examples, not professional advice.": "이 가상 리포트는 기존 개인 재무 엔진과 규칙 기반 어드바이저 레이어를 사용합니다. 교육용 예시이며 전문 조언이 아닙니다.",
    "Select virtual client": "가상 고객 선택",
    "Advisor Interpretation": "어드바이저 해석",
    "Focus": "초점",
    "Asset Mix": "자산 구성",
    "Stress Capital": "스트레스 후 자본",
    "Decision Path": "의사결정 경로",
    "Layer": "레이어",
    "Reading": "판독",
    "Name": "이름",
    "Segment": "고객군",
    "Planning Health": "계획 건강도",
    "Planning Health Score": "계획 건강도 점수",
    "Cash Runway": "현금 생존기간",
    "Goal Progress": "목표 진행률",
    "Investment Exposure": "투자 노출도",
    "Portfolio Quality": "포트폴리오 품질",
    "Ticker": "티커",
    "Sector": "섹터",
    "Weight": "비중",
    "Beta": "베타",
    "Valuation": "가치평가",
    "Selected client report text": "선택 고객 리포트 텍스트",
    "Portfolio / Valuation Sample": "포트폴리오 / 가치평가 샘플",
    "Portfolio beta": "포트폴리오 베타",
    "Largest holding": "최대 보유 비중",
    "Sector concentration": "섹터 집중도",
    "Download Selected Client PDF": "선택 고객 PDF 다운로드",
    "Download All Client Reports PDF": "전체 고객 PDF 다운로드",
    "Load Client Into Finance": "고객을 재무 입력으로 불러오기",
    "All Virtual Client Results": "전체 가상 고객 결과",
    "Next actions:": "다음 행동:",
    "Inputs ready": "입력 준비됨",
    "Packet ready": "패킷 준비됨",
    "No packet yet": "아직 패킷 없음",
    "loaded": "개 로드됨",
    "selected": "개 선택됨",
    "Mobile view": "모바일 보기",
    "Now": "현재",
    "Data": "데이터",
    "Current screen": "현재 화면",
    "Context status": "맥락 상태",
    "Next mobile step": "다음 모바일 단계",
    "Review the current screen, then ask AI Coach for a linked summary.": "현재 화면을 검토한 뒤 AI 코치에게 연결 요약을 요청하세요.",
    "Life Design Control Center": "라이프 설계 컨트롤 센터",
    "ToxiGuard-NORA connects user context, financial data, models, evidence, AI interpretation, decisions, and memory. Use the circular menu above to move between valuation, portfolio risk, real estate exposure, personal finance, scenario stress testing, AI readiness, calculation transparency, and diary reflection.": "ToxiGuard-NORA는 사용자 맥락, 금융 데이터, 모델, 근거, AI 해석, 결정, 메모리를 연결합니다. 위 원형 메뉴로 가치평가, 포트폴리오 위험, 부동산 노출, 개인 재무, 시나리오 스트레스 테스트, AI 준비도, 계산 투명성, 다이어리 회고를 이동하세요.",
    "Understand monthly cash flow before taking investment risk.": "투자 위험을 감수하기 전 월 현금흐름을 이해하세요.",
    "Check liquidity and emergency capacity.": "유동성과 비상 대응력을 확인하세요.",
    "Investments": "투자",
    "Review stock value, beta, risk, and diversification.": "주식 가치, 베타, 위험, 분산을 검토하세요.",
    "Real Estate": "부동산",
    "Study REIT and property-linked exposure.": "REIT와 부동산 연계 노출을 학습하세요.",
    "Stress-test income, FX, rates, and portfolio shocks.": "소득, 환율, 금리, 포트폴리오 충격을 테스트하세요.",
    "Ask rule-based questions about readiness, risk, scenario, and memory.": "준비도, 위험, 시나리오, 메모리에 대해 규칙 기반 질문을 해보세요.",
    "Save snapshots and reflect on next actions.": "스냅샷을 저장하고 다음 행동을 회고하세요.",
    "Open Search": "검색 열기",
    "NORA Ontology": "NORA 온톨로지",
    "Ontology Locked": "온톨로지 고정",
    "User": "사용자",
    "Model": "모델",
    "AI Interpretation": "AI 해석",
    "Decision": "결정",
    "Identity and goals": "정체성/목표",
    "Structured inputs": "구조화 입력",
    "Calculation engine": "계산 엔진",
    "Proof and assumptions": "근거/가정",
    "Reasoning layer": "추론 레이어",
    "Action direction": "행동 방향",
    "Decision log": "결정 기록",
    "Financial Foundation": "재무 기반",
    "Market Assets": "시장 자산",
    "Projection": "전망",
    "Risk / Resilience": "위험 / 회복력",
    "NORA keeps every screen tied to the same decision path: current situation, evidence, interpretation, action, and memory.": "NORA는 모든 화면을 현재 상황, 근거, 해석, 행동, 기억이라는 동일한 의사결정 경로에 연결합니다.",
    "Hover or click each visual node to read its role.": "각 시각 노드에 마우스를 올리거나 클릭하면 역할을 볼 수 있습니다.",
    "ToxiGuard-NORA is provided for educational and informational use only and does not constitute or provide financial, investment, legal, tax, accounting, or professional advice. Do not enter sensitive personal financial information into this prototype. Market data and charts may be provided by third-party services such as Finnhub, TradingView, and Yahoo Finance/yfinance, subject to their own terms. All trademarks, company names, and ticker symbols remain the property of their respective owners. This interface uses original CSS/HTML design elements and does not claim ownership of third-party data, logos, or trademarks. Data may be delayed, incomplete, or unavailable and should be verified independently.": "ToxiGuard-NORA는 교육 및 정보 제공용이며 금융, 투자, 법률, 세무, 회계 또는 전문 조언을 제공하지 않습니다. 이 프로토타입에 민감한 개인 금융 정보를 입력하지 마세요. 시장 데이터와 차트는 Finnhub, TradingView, Yahoo Finance/yfinance 등 제3자 서비스에서 제공될 수 있으며 각 서비스 약관을 따릅니다. 모든 상표, 회사명, 티커 심볼은 각 소유자의 자산입니다. 이 인터페이스는 자체 CSS/HTML 디자인 요소를 사용하며 제3자 데이터, 로고, 상표의 소유권을 주장하지 않습니다. 데이터는 지연되거나 불완전하거나 제공되지 않을 수 있으므로 독립적으로 검증해야 합니다.",
}


def normalized_language(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if value is None:
        return None
    return LANGUAGE_ALIASES.get(str(value).strip().lower())


def query_language() -> str | None:
    try:
        return normalized_language(st.query_params.get("lang"))
    except Exception:
        try:
            return normalized_language(st.experimental_get_query_params().get("lang"))
        except Exception:
            return None


def current_language() -> str:
    query_value = query_language()
    if query_value:
        st.session_state.app_language = query_value
    return st.session_state.get("app_language", "en")


def ui(text: str) -> str:
    if current_language() == "ko":
        return KO_TRANSLATIONS.get(text, text)
    return text


def ui_html(text: str) -> str:
    return escape(ui(text))


def set_language(language: str) -> None:
    language = normalized_language(language) or "en"
    st.session_state.app_language = language
    try:
        st.query_params["lang"] = language
    except Exception:
        try:
            params = st.experimental_get_query_params()
            params["lang"] = language
            st.experimental_set_query_params(**params)
        except Exception:
            pass


def language_params() -> dict[str, str]:
    return {"lang": current_language()}


def render_language_switcher(key_suffix: str = "global") -> None:
    language = current_language()
    selected = st.radio(
        ui("Language"),
        options=list(LANGUAGE_OPTIONS.keys()),
        index=list(LANGUAGE_OPTIONS.keys()).index(language),
        format_func=lambda code: LANGUAGE_OPTIONS[code],
        horizontal=True,
        key=f"language_switcher_{key_suffix}",
    )
    if selected != language:
        set_language(selected)
        st.rerun()
    st.caption(ui("Default language is English. Korean mode translates the primary workflow, navigation, and key input surfaces."))

st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(90deg, rgba(34,211,238,0.035) 1px, transparent 1px),
            linear-gradient(0deg, rgba(20,184,166,0.030) 1px, transparent 1px),
            radial-gradient(circle at 18% 14%, rgba(14,165,233,0.18), transparent 30%),
            radial-gradient(circle at 86% 8%, rgba(20,184,166,0.13), transparent 24%),
            radial-gradient(circle at 52% 0%, rgba(59,130,246,0.10), transparent 34%),
            linear-gradient(135deg, #111827 0%, #172335 48%, #080c12 100%);
        background-size: 42px 42px, 42px 42px, auto, auto, auto;
        color: #f8fafc;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.45;
        background:
            linear-gradient(115deg, transparent 0%, transparent 40%, rgba(37,99,235,0.16) 41%, rgba(37,99,235,0.04) 46%, transparent 52%),
            linear-gradient(65deg, transparent 0%, transparent 58%, rgba(20,184,166,0.15) 59%, rgba(20,184,166,0.03) 64%, transparent 70%);
        animation: dataSweep 14s linear infinite;
    }
    .stApp::after {
        content: "";
        position: fixed;
        right: 28px;
        top: 92px;
        width: 320px;
        height: 180px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.22;
        background:
            linear-gradient(135deg, transparent 0 10%, rgba(37,99,235,0.32) 10% 11%, transparent 11% 25%, rgba(16,185,129,0.30) 25% 26%, transparent 26% 42%, rgba(245,158,11,0.34) 42% 43%, transparent 43% 100%);
        clip-path: polygon(0 80%, 10% 67%, 20% 72%, 30% 48%, 40% 57%, 52% 32%, 65% 40%, 78% 18%, 100% 28%, 100% 100%, 0 100%);
        animation: graphFloat 8s ease-in-out infinite;
    }
    .top-language-toggle {
        position: fixed;
        top: 16px;
        right: 76px;
        z-index: 100000;
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.76);
        box-shadow: 0 14px 36px rgba(2, 6, 23, 0.28);
        backdrop-filter: blur(14px);
    }
    .top-language-toggle .language-toggle-mark,
    .top-language-toggle a {
        width: 34px;
        height: 34px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.76rem;
        font-weight: 950;
        line-height: 1;
        letter-spacing: 0;
        text-decoration: none !important;
        white-space: nowrap;
    }
    .top-language-toggle .language-toggle-mark {
        color: #a7f3d0;
        background: rgba(20, 184, 166, 0.15);
        border: 1px solid rgba(45, 212, 191, 0.24);
    }
    .top-language-toggle a {
        color: #cbd5e1 !important;
        border: 1px solid transparent;
        background: transparent;
        transition: background 160ms ease, color 160ms ease, border-color 160ms ease, transform 160ms ease;
    }
    .top-language-toggle a:hover,
    .top-language-toggle a:focus {
        color: #ffffff !important;
        border-color: rgba(34, 211, 238, 0.32);
        background: rgba(14, 165, 233, 0.18);
        transform: translateY(-1px);
    }
    .top-language-toggle a.active {
        color: #02131f !important;
        background: #67e8f9;
        border-color: rgba(255, 255, 255, 0.54);
        box-shadow: 0 8px 20px rgba(34, 211, 238, 0.25);
    }
    @keyframes dataSweep {
        0% { transform: translateX(-18%) translateY(0); }
        100% { transform: translateX(18%) translateY(0); }
    }
    @keyframes graphFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(12px); }
    }
    h1, h2, h3 {
        color: #f8fafc;
        letter-spacing: 0;
    }
    p, li, label {
        color: #dbe7f3;
    }
    .block-container {
        padding-top: 1.25rem;
        max-width: 1280px;
        position: relative;
        z-index: 1;
    }
    div[data-testid="stHeadingWithActionElements"] h1 {
        font-size: 2.35rem;
        font-weight: 900;
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }
    .brand-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 18px;
        padding: 42px 30px 34px;
        margin: 0 0 20px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 28px;
        background:
            radial-gradient(circle at 54% 28%, rgba(20, 184, 166, 0.30), transparent 28%),
            radial-gradient(circle at 48% 20%, rgba(14, 165, 233, 0.22), transparent 34%),
            linear-gradient(135deg, #111827 0%, #172335 48%, #080c12 100%);
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
    }
    .brand-header::after {
        content: "";
        position: absolute;
        left: 7%;
        right: 7%;
        bottom: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #22d3ee, transparent);
        opacity: 0.95;
    }
    .nora-ontology {
        margin: 0 0 22px;
        padding: 18px;
        border: 1px solid rgba(125, 211, 252, 0.36);
        border-radius: 8px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.82), rgba(8, 13, 20, 0.76)),
            radial-gradient(circle at 14% 18%, rgba(45, 212, 191, 0.22), transparent 28%);
        box-shadow: 0 22px 48px rgba(2, 6, 23, 0.18);
        position: relative;
        overflow: visible;
    }
    .nora-ontology-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        margin-bottom: 14px;
    }
    .nora-ontology-kicker {
        font-size: 0.72rem;
        font-weight: 950;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #67e8f9;
    }
    .nora-ontology-title {
        margin-top: 3px;
        font-size: clamp(1.05rem, 2vw, 1.45rem);
        line-height: 1.15;
        font-weight: 950;
        color: #f8fafc;
        letter-spacing: 0;
    }
    .nora-ontology-caption {
        max-width: 520px;
        color: #cbd5e1;
        font-size: 0.86rem;
        line-height: 1.45;
        text-align: right;
    }
    .nora-path {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
        gap: 8px;
        align-items: stretch;
    }
    .nora-node {
        min-height: 88px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        background: rgba(15, 23, 42, 0.72);
        color: #e2e8f0;
        padding: 12px 10px;
        position: relative;
        text-decoration: none !important;
        appearance: none;
        cursor: help;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
    }
    .nora-node::after {
        content: "";
        position: absolute;
        right: -8px;
        top: 50%;
        width: 8px;
        height: 2px;
        background: linear-gradient(90deg, rgba(103,232,249,0.75), rgba(45,212,191,0.16));
        display: none;
    }
    .nora-node:last-child::after {
        display: none;
    }
    .nora-node:hover,
    .nora-node:focus {
        transform: translateY(-2px);
        border-color: rgba(103, 232, 249, 0.62);
        background: rgba(14, 116, 144, 0.30);
        outline: none;
    }
    .nora-node strong {
        display: block;
        color: #f8fafc;
        font-size: 0.92rem;
        line-height: 1.1;
        letter-spacing: 0;
    }
    .nora-node span {
        color: #94a3b8;
        font-size: 0.73rem;
        line-height: 1.22;
        margin-top: 6px;
    }
    .nora-glyph {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: grid;
        place-items: center;
        color: #03131d;
        font-size: 0.74rem;
        font-weight: 950;
        background: var(--nora-color, #67e8f9);
        box-shadow: 0 10px 24px rgba(34, 211, 238, 0.18);
    }
    .nora-detail {
        position: absolute;
        left: 8px;
        right: 8px;
        top: calc(100% + 8px);
        opacity: 0;
        pointer-events: none;
        transform: translateY(-4px);
        transition: opacity 160ms ease, transform 160ms ease;
        z-index: 4;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(125, 211, 252, 0.34);
        color: #dbeafe;
        background: rgba(2, 6, 23, 0.94);
        box-shadow: 0 16px 32px rgba(2, 6, 23, 0.34);
        font-size: 0.76rem;
        line-height: 1.36;
    }
    .nora-node:hover .nora-detail,
    .nora-node:focus .nora-detail {
        opacity: 1;
        pointer-events: auto;
        transform: translateY(0);
    }
    .nora-modules {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
        gap: 7px;
        margin-top: 14px;
    }
    .nora-module {
        min-height: 48px;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(248, 250, 252, 0.07);
        color: #cbd5e1 !important;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 8px;
        font-size: 0.72rem;
        line-height: 1.16;
        font-weight: 850;
        letter-spacing: 0;
    }
    .nora-module.active,
    .nora-module:hover,
    .nora-module:focus {
        color: #02131f !important;
        background: #a7f3d0;
        border-color: rgba(255, 255, 255, 0.60);
        outline: none;
    }
    .brand-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        position: relative;
        z-index: 1;
    }
    .brand-icon {
        width: 76px;
        height: 76px;
        border-radius: 20px;
        display: grid;
        place-items: center;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.18), transparent 32%),
            linear-gradient(135deg, rgba(34, 211, 238, 0.22), rgba(20, 184, 166, 0.18)),
            rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(34, 211, 238, 0.42);
        box-shadow: 0 0 30px rgba(34, 211, 238, 0.28), inset 0 0 24px rgba(34, 211, 238, 0.10);
        position: relative;
    }
    .brand-icon::after {
        content: "";
        width: 46px;
        height: 42px;
        background:
            linear-gradient(to top, #22d3ee 0 76%, transparent 76%),
            linear-gradient(to top, #10b981 0 52%, transparent 52%),
            linear-gradient(to top, #60a5fa 0 92%, transparent 92%),
            linear-gradient(to top, #f59e0b 0 63%, transparent 63%);
        background-size: 8px 100%;
        background-position: 2px 0, 14px 0, 26px 0, 38px 0;
        background-repeat: no-repeat;
        border-bottom: 2px solid rgba(226, 232, 240, 0.8);
    }
    .brand-icon::before {
        content: "";
        position: absolute;
        inset: 13px;
        border-radius: 12px;
        border: 1px solid rgba(226, 232, 240, 0.22);
    }
    .brand-name {
        color: #f8fafc;
        font-size: clamp(3.4rem, 7vw, 6.2rem);
        font-weight: 950;
        line-height: 0.92;
        letter-spacing: 0;
        text-shadow: 0 16px 42px rgba(34, 211, 238, 0.26);
    }
    .brand-name .scope-accent {
        color: #19dce8;
        text-shadow: 0 0 34px rgba(34, 211, 238, 0.58);
    }
    .brand-subtitle {
        color: #a9b7c9;
        font-size: 1.05rem;
        font-weight: 850;
        margin-top: 20px;
        letter-spacing: 0;
        text-align: center;
        max-width: 720px;
        overflow-wrap: anywhere;
    }
    .brand-badge {
        color: #fff7ed;
        background:
            radial-gradient(circle at 18% 22%, rgba(255, 255, 255, 0.24), transparent 30%),
            linear-gradient(135deg, rgba(124, 45, 18, 0.62), rgba(88, 28, 135, 0.52));
        border: 1px solid rgba(251, 146, 60, 0.46);
        border-radius: 999px;
        padding: 7px 15px 7px 8px;
        font-size: 0.88rem;
        font-weight: 850;
        white-space: nowrap;
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: 9px;
        text-decoration: none !important;
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }
    .brand-search-badge,
    .brand-search-badge:visited {
        color: #fff7ed !important;
    }
    .brand-badge:hover {
        color: #ffffff !important;
        transform: translateY(-1px);
        border-color: rgba(253, 186, 116, 0.72);
        box-shadow: 0 16px 34px rgba(244, 114, 182, 0.20);
        text-decoration: none !important;
    }
    .brand-search-icon {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        display: inline-grid;
        place-items: center;
        color: #f8fafc;
        font-size: 0.8rem;
        font-weight: 950;
        line-height: 1;
        letter-spacing: 0;
        overflow: hidden;
        position: relative;
        background:
            radial-gradient(circle at 30% 22%, rgba(255,255,255,0.80), transparent 20%),
            conic-gradient(from 205deg, #f97316, #facc15, #e11d48, #7c3aed, #f97316);
        box-shadow: 0 12px 26px rgba(225, 29, 72, 0.22), inset 0 0 18px rgba(255,255,255,0.24);
    }
    .brand-search-icon::after {
        content: "";
        position: absolute;
        inset: 4px;
        border-radius: inherit;
        border: 1px solid rgba(255,255,255,0.44);
        pointer-events: none;
    }
    .brand-search-sigil {
        position: absolute;
        inset: 4px;
        width: calc(100% - 8px);
        height: calc(100% - 8px);
        opacity: 0.62;
        fill: none;
        stroke: rgba(255, 255, 255, 0.86);
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-width: 2.2;
        transform: rotate(-10deg);
        z-index: 1;
    }
    .brand-search-initials {
        position: relative;
        z-index: 2;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(30, 41, 59, 0.34);
    }
    .brand-search-label {
        color: inherit !important;
        font-weight: 900;
        letter-spacing: 0;
    }
    .search-return-row {
        max-width: 620px;
        margin: -4px auto 10px;
        display: flex;
        justify-content: flex-start;
    }
    .search-return-link {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        min-height: 38px;
        padding: 8px 14px;
        border-radius: 999px;
        color: #f8fafc !important;
        background:
            radial-gradient(circle at 20% 18%, rgba(255,255,255,0.16), transparent 30%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.90), rgba(30, 41, 59, 0.82));
        border: 1px solid rgba(125, 211, 252, 0.34);
        box-shadow: 0 12px 26px rgba(15, 23, 42, 0.18);
        font-size: 0.86rem;
        font-weight: 900;
        text-decoration: none !important;
        transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
    }
    .search-return-link:hover {
        color: #ffffff !important;
        transform: translateY(-1px);
        border-color: rgba(251, 146, 60, 0.52);
        box-shadow: 0 14px 30px rgba(190, 24, 93, 0.15);
        text-decoration: none !important;
    }
    .search-return-arrow {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-grid;
        place-items: center;
        background: linear-gradient(135deg, #f97316, #7c3aed);
        color: #ffffff;
        font-size: 1rem;
        line-height: 1;
    }
    .terminal-showcase {
        position: relative;
        overflow: hidden;
        padding: 34px;
        margin: 0 0 24px;
        border-radius: 30px;
        border: 1px solid rgba(125, 211, 252, 0.24);
        background:
            radial-gradient(circle at 12% 72%, rgba(34, 211, 238, 0.34), transparent 18%),
            radial-gradient(circle at 86% 62%, rgba(59, 130, 246, 0.32), transparent 20%),
            radial-gradient(circle at 50% 10%, rgba(20, 184, 166, 0.16), transparent 34%),
            linear-gradient(145deg, #101722 0%, #0b1320 48%, #101827 100%);
        box-shadow: 0 28px 70px rgba(15, 23, 42, 0.28);
    }
    .terminal-showcase::before {
        content: "";
        position: absolute;
        inset: auto -8% 4% -8%;
        height: 170px;
        opacity: 0.55;
        background:
            radial-gradient(ellipse at center, rgba(34, 211, 238, 0.48), transparent 58%),
            repeating-radial-gradient(circle at 50% 80%, rgba(125, 211, 252, 0.22) 0 1px, transparent 1px 9px);
        clip-path: polygon(0 64%, 12% 56%, 24% 68%, 38% 42%, 52% 50%, 68% 26%, 84% 44%, 100% 20%, 100% 100%, 0 100%);
        animation: graphFloat 8s ease-in-out infinite;
    }
    .terminal-shell {
        position: relative;
        z-index: 1;
        max-width: 1080px;
        margin: 0 auto;
        border-radius: 26px;
        border: 1px solid rgba(148, 163, 184, 0.36);
        background: rgba(8, 15, 27, 0.88);
        box-shadow:
            0 0 0 5px rgba(148, 163, 184, 0.10),
            0 26px 60px rgba(2, 6, 23, 0.54),
            inset 0 0 44px rgba(14, 165, 233, 0.12);
        overflow: hidden;
    }
    .terminal-topbar {
        display: grid;
        grid-template-columns: 58px minmax(150px, 220px) 1fr auto;
        gap: 16px;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(15, 23, 42, 0.72);
    }
    .terminal-mini-logo {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: grid;
        place-items: center;
        color: #e0f2fe;
        font-weight: 950;
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.18), rgba(16, 185, 129, 0.12));
        border: 1px solid rgba(34, 211, 238, 0.30);
        box-shadow: 0 0 18px rgba(34, 211, 238, 0.20);
    }
    .terminal-search {
        height: 42px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(30, 41, 59, 0.78);
        color: #dbeafe;
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 0 13px;
        font-weight: 800;
    }
    .terminal-search span:first-child {
        color: #93c5fd;
        font-size: 1.15rem;
    }
    .terminal-nav {
        display: flex;
        gap: 24px;
        color: #94a3b8;
        font-size: 0.94rem;
        font-weight: 800;
        white-space: nowrap;
    }
    .terminal-nav .active {
        color: #f8fafc;
        position: relative;
    }
    .terminal-nav .active::after {
        content: "";
        position: absolute;
        left: -4px;
        right: -4px;
        bottom: -18px;
        height: 3px;
        border-radius: 999px;
        background: #22d3ee;
        box-shadow: 0 0 18px rgba(34, 211, 238, 0.72);
    }
    .terminal-user {
        color: #cbd5e1;
        font-size: 0.84rem;
        font-weight: 800;
        text-align: right;
        white-space: nowrap;
    }
    .terminal-user b {
        color: #34d399;
    }
    .terminal-body {
        display: grid;
        grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.9fr);
        gap: 16px;
        padding: 18px 20px 20px;
    }
    .terminal-chart-card,
    .terminal-side-card {
        border-radius: 18px;
        border: 1px solid rgba(125, 211, 252, 0.22);
        background:
            radial-gradient(circle at 50% 30%, rgba(34, 211, 238, 0.12), transparent 34%),
            rgba(15, 23, 42, 0.74);
        box-shadow: inset 0 0 34px rgba(14, 165, 233, 0.08);
    }
    .terminal-chart-card {
        min-height: 470px;
        padding: 18px;
    }
    .terminal-stock-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 14px;
    }
    .terminal-symbol {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1;
    }
    .terminal-company {
        color: #94a3b8;
        font-weight: 750;
        margin-top: 4px;
    }
    .terminal-price {
        color: #f8fafc;
        font-size: 1.7rem;
        font-weight: 950;
        text-align: right;
    }
    .terminal-price span {
        color: #6ee7b7;
        font-size: 1.35rem;
    }
    .terminal-chart-grid {
        position: relative;
        height: 300px;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 12px;
        background:
            repeating-linear-gradient(to bottom, transparent 0 58px, rgba(148, 163, 184, 0.15) 59px 60px),
            linear-gradient(180deg, rgba(8, 47, 73, 0.40), rgba(8, 13, 26, 0.22));
        overflow: hidden;
    }
    .ma-line {
        position: absolute;
        left: 5%;
        right: 5%;
        height: 3px;
        border-radius: 999px;
        transform: rotate(-11deg);
        opacity: 0.95;
    }
    .ma-green {
        top: 62%;
        background: linear-gradient(90deg, #86efac, #22c55e);
    }
    .ma-blue {
        top: 78%;
        background: linear-gradient(90deg, #38bdf8, #2563eb);
    }
    .candle-row {
        position: absolute;
        left: 5%;
        right: 5%;
        bottom: 32px;
        height: 230px;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 7px;
    }
    .candle {
        width: 13px;
        border-radius: 3px 3px 1px 1px;
        position: relative;
        box-shadow: 0 0 10px currentColor;
    }
    .candle::before {
        content: "";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        bottom: -18px;
        width: 2px;
        height: calc(100% + 36px);
        background: currentColor;
        opacity: 0.48;
    }
    .up { color: #7cff5f; background: #7cff5f; }
    .down { color: #ff674d; background: #ff674d; }
    .volume-row {
        height: 86px;
        margin-top: 14px;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 12px;
        display: flex;
        align-items: flex-end;
        gap: 8px;
        padding: 10px;
        background: rgba(8, 13, 26, 0.35);
    }
    .vol {
        flex: 1;
        min-width: 5px;
        border-radius: 2px 2px 0 0;
        opacity: 0.62;
    }
    .terminal-side {
        display: grid;
        gap: 16px;
    }
    .terminal-side-card {
        padding: 18px;
    }
    .side-title {
        color: #e2e8f0;
        font-size: 0.98rem;
        font-weight: 950;
        margin-bottom: 18px;
    }
    .metric-grid-dark {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
    .dark-label {
        color: #cbd5e1;
        font-size: 0.92rem;
        font-weight: 800;
    }
    .dark-value {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1.05;
        margin-top: 7px;
    }
    .dark-value.green { color: #72ef69; }
    .dark-value.red,
    .terminal-price span.red {
        color: #fb7185;
    }
    .terminal-price span.green {
        color: #6ee7b7;
    }
    .dark-value.orange { color: #fbbf24; font-size: 1.55rem; }
    .radar-wrap {
        width: 210px;
        height: 210px;
        margin: 4px auto 14px;
        border-radius: 50%;
        position: relative;
        background:
            radial-gradient(circle, rgba(125, 211, 252, 0.10) 0 18%, transparent 18% 32%, rgba(125, 211, 252, 0.08) 32% 34%, transparent 34% 49%, rgba(125, 211, 252, 0.08) 49% 51%, transparent 51%),
            conic-gradient(from 25deg, rgba(34, 211, 238, 0.20), rgba(163, 230, 53, 0.24), rgba(251, 191, 36, 0.24), rgba(34, 211, 238, 0.20));
        border: 1px solid rgba(125, 211, 252, 0.22);
    }
    .radar-triangle {
        position: absolute;
        inset: 34px 42px 34px;
        background: linear-gradient(135deg, rgba(163, 230, 53, 0.42), rgba(251, 191, 36, 0.28));
        clip-path: polygon(50% 0, 98% 82%, 0 88%);
        border: 1px solid rgba(255, 255, 255, 0.34);
        filter: drop-shadow(0 0 18px rgba(163, 230, 53, 0.40));
    }
    .radar-scores {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        color: #cbd5e1;
        font-size: 0.82rem;
        font-weight: 800;
    }
    .radar-scores b {
        display: block;
        color: #86efac;
        font-size: 1.35rem;
    }
    .result-terminal {
        margin: 18px 0 26px;
    }
    .terminal-status-strip {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        padding: 14px 20px 18px;
        border-top: 1px solid rgba(148, 163, 184, 0.18);
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 800;
        background: rgba(15, 23, 42, 0.52);
    }
    .terminal-status-strip b {
        color: #f8fafc;
    }
    .valuation-radar-card {
        display: grid;
        grid-template-columns: minmax(260px, 0.9fr) minmax(280px, 1.1fr);
        gap: 24px;
        align-items: center;
        border: 1px solid #b8c7da;
        border-radius: 18px;
        background:
            radial-gradient(circle at 26% 24%, rgba(34, 211, 238, 0.13), transparent 28%),
            linear-gradient(135deg, #ffffff 0%, #f6fbff 100%);
        box-shadow: 0 16px 34px rgba(30, 64, 105, 0.12);
        padding: 22px;
        margin: 14px 0 22px;
    }
    .valuation-radar-title {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 950;
        margin-bottom: 7px;
    }
    .valuation-radar-copy {
        color: #334155;
        font-size: 0.96rem;
        font-weight: 700;
        line-height: 1.55;
        margin-bottom: 14px;
    }
    .valuation-radar-legend {
        display: grid;
        gap: 10px;
    }
    .valuation-radar-legend div {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid #d8e2ef;
        padding-top: 10px;
        color: #334155;
        font-weight: 800;
    }
    .valuation-radar-legend b {
        color: #0f172a;
        font-size: 1.05rem;
    }
    .valuation-radar-svg {
        width: 100%;
        max-width: 380px;
        margin: 0 auto;
        display: block;
        filter: drop-shadow(0 16px 22px rgba(14, 116, 144, 0.14));
    }
    @media (max-width: 900px) {
        .terminal-showcase {
            padding: 18px;
        }
        .terminal-topbar {
            grid-template-columns: 44px 1fr;
        }
        .terminal-nav,
        .terminal-user {
            display: none;
        }
        .terminal-body {
            grid-template-columns: 1fr;
        }
        .brand-mark {
            flex-direction: column;
            text-align: center;
        }
        .brand-subtitle {
            letter-spacing: 0;
            line-height: 1.5;
        }
        .valuation-radar-card {
            grid-template-columns: 1fr;
        }
    }
    div[data-testid="stTabs"] div[role="tablist"] {
        gap: 16px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.20);
        padding: 10px 0 22px;
        margin-bottom: 24px;
        flex-wrap: wrap;
        align-items: center;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        width: 112px;
        height: 112px;
        min-width: 112px;
        min-height: 112px;
        display: grid;
        place-items: center;
        padding: 12px;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.34);
        color: #e2e8f0;
        background:
            radial-gradient(circle at 35% 24%, rgba(255,255,255,0.13), transparent 24%),
            radial-gradient(circle at 50% 58%, rgba(34, 211, 238, 0.10), transparent 56%),
            rgba(15, 23, 42, 0.78);
        box-shadow:
            inset 0 0 28px rgba(34, 211, 238, 0.05),
            0 14px 30px rgba(2, 6, 23, 0.26);
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        border-color: #22d3ee;
        color: #f8fafc;
        background:
            radial-gradient(circle at 35% 24%, rgba(255,255,255,0.18), transparent 24%),
            radial-gradient(circle at 50% 58%, rgba(34, 211, 238, 0.22), transparent 56%),
            rgba(15, 23, 42, 0.88);
        transform: translateY(-4px);
        box-shadow:
            0 0 0 8px rgba(34, 211, 238, 0.06),
            0 18px 36px rgba(34, 211, 238, 0.12);
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background:
            radial-gradient(circle at 34% 25%, rgba(255,255,255,0.32), transparent 23%),
            linear-gradient(135deg, #22d3ee 0%, #0ea5e9 46%, #14b8a6 100%);
        border-color: #22d3ee;
        color: #ffffff;
        box-shadow:
            0 0 0 9px rgba(34, 211, 238, 0.12),
            0 0 34px rgba(34, 211, 238, 0.32),
            0 18px 38px rgba(14, 116, 144, 0.24);
        transform: translateY(-3px);
    }
    div[data-testid="stTabs"] button[role="tab"] p {
        max-width: 86px;
        font-size: 15px;
        font-weight: 950;
        color: inherit;
        line-height: 1.05;
        text-align: center;
        white-space: normal;
        overflow-wrap: anywhere;
        margin: 0;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        display: none;
    }
    .circle-nav-wrap {
        margin: 24px 0 30px;
        padding: 24px 22px 28px;
        border-radius: 30px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background:
            radial-gradient(circle at 18% 12%, rgba(34, 211, 238, 0.16), transparent 24%),
            radial-gradient(circle at 82% 18%, rgba(16, 185, 129, 0.12), transparent 22%),
            rgba(8, 13, 22, 0.48);
        box-shadow: inset 0 0 42px rgba(34, 211, 238, 0.04), 0 18px 44px rgba(2, 6, 23, 0.22);
    }
    .circle-nav {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: clamp(14px, 1.8vw, 22px);
    }
    .circle-nav-item {
        width: 122px;
        height: 122px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        text-decoration: none !important;
        color: #eaf7ff !important;
        position: relative;
        overflow: hidden;
        isolation: isolate;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.24), transparent 22%),
            radial-gradient(circle at 50% 54%, rgba(34, 211, 238, 0.16), transparent 58%),
            linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(8, 13, 22, 0.92));
        border: 1px solid rgba(148, 163, 184, 0.30);
        box-shadow: 0 14px 32px rgba(2, 6, 23, 0.28), inset 0 0 30px rgba(34, 211, 238, 0.05);
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
    }
    .circle-nav-item::before {
        content: "";
        position: absolute;
        inset: 9px;
        border-radius: inherit;
        border: 1px solid rgba(103, 232, 249, 0.18);
        box-shadow: inset 0 0 24px rgba(255,255,255,0.04);
        z-index: -1;
    }
    .circle-nav-item::after {
        content: "";
        position: absolute;
        inset: -35%;
        background: conic-gradient(from 90deg, transparent, rgba(103, 232, 249, 0.28), transparent, rgba(20, 184, 166, 0.20), transparent);
        opacity: 0.28;
        animation: circleNavSpin 14s linear infinite;
        z-index: -2;
    }
    .circle-nav-item:hover {
        transform: translateY(-5px) scale(1.02);
        border-color: rgba(103, 232, 249, 0.70);
        box-shadow: 0 0 0 8px rgba(34, 211, 238, 0.08), 0 20px 42px rgba(34, 211, 238, 0.14);
    }
    .circle-nav-item.active {
        color: #ffffff !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.38), transparent 22%),
            linear-gradient(135deg, #22d3ee 0%, #0ea5e9 48%, #14b8a6 100%);
        border-color: rgba(103, 232, 249, 0.88);
        box-shadow: 0 0 0 10px rgba(34, 211, 238, 0.10), 0 0 38px rgba(34, 211, 238, 0.36), 0 22px 46px rgba(14, 116, 144, 0.24);
    }
    .circle-nav-content {
        display: grid;
        place-items: center;
        gap: 7px;
        text-align: center;
        padding: 10px;
    }
    .circle-nav-icon {
        width: 44px;
        height: 44px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-size: 0.88rem;
        font-weight: 950;
        letter-spacing: 0.03em;
        color: #ffffff;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.20);
        box-shadow: inset 0 0 16px rgba(255, 255, 255, 0.06);
    }
    .circle-nav-label {
        display: block;
        color: inherit;
        font-size: 0.88rem;
        font-weight: 950;
        line-height: 1.04;
        letter-spacing: 0;
    }
    .st-key-circle_nav {
        margin: 24px 0 30px;
        padding: 24px 22px 28px;
        border-radius: 30px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background:
            radial-gradient(circle at 18% 12%, rgba(34, 211, 238, 0.16), transparent 24%),
            radial-gradient(circle at 82% 18%, rgba(16, 185, 129, 0.12), transparent 22%),
            rgba(8, 13, 22, 0.48);
        box-shadow: inset 0 0 42px rgba(34, 211, 238, 0.04), 0 18px 44px rgba(2, 6, 23, 0.22);
    }
    .st-key-circle_nav div[data-testid="column"] {
        display: flex;
        justify-content: center;
    }
    .st-key-circle_nav div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .st-key-circle_nav div[data-testid="stButton"] button {
        width: 108px !important;
        height: 108px !important;
        min-width: 108px !important;
        min-height: 108px !important;
        padding: 0 !important;
        border-radius: 999px !important;
        color: #eaf7ff !important;
        border: 1px solid rgba(148, 163, 184, 0.30) !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.24), transparent 22%),
            radial-gradient(circle at 50% 54%, rgba(34, 211, 238, 0.16), transparent 58%),
            linear-gradient(145deg, rgba(15, 23, 42, 0.94), rgba(8, 13, 22, 0.94)) !important;
        box-shadow: 0 14px 30px rgba(2, 6, 23, 0.28), inset 0 0 30px rgba(34, 211, 238, 0.05) !important;
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
    }
    .st-key-circle_nav div[data-testid="stButton"] button:hover {
        transform: translateY(-5px) scale(1.02);
        border-color: rgba(103, 232, 249, 0.72) !important;
        box-shadow: 0 0 0 8px rgba(34, 211, 238, 0.08), 0 20px 42px rgba(34, 211, 238, 0.14) !important;
    }
    .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] {
        color: #ffffff !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.38), transparent 22%),
            linear-gradient(135deg, #22d3ee 0%, #0ea5e9 48%, #14b8a6 100%) !important;
        border-color: rgba(103, 232, 249, 0.90) !important;
        box-shadow: 0 0 0 10px rgba(34, 211, 238, 0.10), 0 0 38px rgba(34, 211, 238, 0.36), 0 22px 46px rgba(14, 116, 144, 0.24) !important;
    }
    .st-key-circle_nav div[data-testid="stButton"] button p {
        white-space: pre-line;
        text-align: center;
        line-height: 1.05;
        font-size: 0.86rem;
        font-weight: 950;
        margin: 0;
    }
    .life-compact-panel {
        border-radius: 28px;
        border: 1px solid rgba(103, 232, 249, 0.24);
        background:
            radial-gradient(circle at 18% 20%, rgba(34, 211, 238, 0.16), transparent 26%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.76), rgba(8, 13, 22, 0.86));
        padding: clamp(24px, 4vw, 42px);
        margin: 4px 0 22px;
        box-shadow: 0 18px 44px rgba(2, 6, 23, 0.22);
    }
    .life-compact-panel h1 {
        margin: 0 0 10px;
        color: #f8fafc;
        font-size: clamp(2rem, 3vw, 3.4rem);
        font-weight: 950;
    }
    .life-compact-panel p {
        max-width: 900px;
        color: #dbeafe;
        font-size: 1.05rem;
        line-height: 1.58;
        margin: 0;
    }
    .life-compact-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 14px;
        margin-top: 24px;
    }
    .life-compact-card {
        min-height: 118px;
        border-radius: 22px;
        padding: 18px;
        background: rgba(15, 23, 42, 0.64);
        border: 1px solid rgba(148, 163, 184, 0.20);
    }
    .life-compact-card b {
        color: #67e8f9;
        display: block;
        margin-bottom: 7px;
        font-size: 0.96rem;
    }
    .life-compact-card span {
        color: #dbeafe;
        font-size: 0.86rem;
        line-height: 1.4;
    }
    @keyframes circleNavSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @media (max-width: 760px) {
        .circle-nav {
            justify-content: center;
        }
        .circle-nav-item {
            width: 96px;
            height: 96px;
        }
        .circle-nav-icon {
            width: 34px;
            height: 34px;
            font-size: 0.72rem;
        }
        .circle-nav-label {
            font-size: 0.76rem;
        }
        .life-compact-grid {
            grid-template-columns: 1fr;
        }
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.48);
        border: 1px solid rgba(148, 163, 184, 0.30);
        border-radius: 18px;
        padding: 8px;
        box-shadow: 0 16px 34px rgba(2, 6, 23, 0.24);
    }
    div[data-testid="stForm"] {
        max-width: 620px;
        border: 1px solid rgba(34, 211, 238, 0.34);
        border-radius: 16px;
        padding: 16px 18px 18px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(17, 34, 52, 0.82));
        box-shadow: 0 14px 34px rgba(2, 6, 23, 0.24);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        border-color: #3b82f6;
        background: #f8fbff;
        color: #1e3a5f;
        min-height: 42px;
        font-weight: 700;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        border-color: #2563eb;
        color: #0f1f33;
        background: #edf5ff;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label {
        color: #e2e8f0;
        font-size: 15px;
        font-weight: 850;
    }
    div[data-testid="stTextInput"] {
        max-width: 540px;
    }
    div[data-baseweb="input"] {
        background: #ffffff !important;
        border: 2px solid #22d3ee;
        border-radius: 12px;
        box-shadow: 0 0 0 3px rgba(34,211,238,0.10), 0 10px 22px rgba(2,6,23,0.18);
        min-height: 42px;
    }
    div[data-baseweb="input"] > div {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    div[data-baseweb="input"] input {
        background: #ffffff !important;
        color: #0f172a !important;
        caret-color: #0f766e !important;
        font-size: 15px;
        font-weight: 750;
    }
    div[data-baseweb="input"] input::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #34d399;
        box-shadow: 0 0 0 4px rgba(52,211,153,0.22), 0 10px 24px rgba(15,118,110,0.18);
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #f8fafc;
        border: 2px solid #60a5fa;
        border-radius: 10px;
        color: #0f172a;
        min-height: 44px;
    }
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px;
        min-height: 40px;
        font-size: 14px;
        font-weight: 800;
    }
    .hero-panel {
        border: 1px solid rgba(125, 211, 252, 0.28);
        border-radius: 20px;
        background:
            radial-gradient(circle at 20% 18%, rgba(34, 211, 238, 0.18), transparent 30%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(17, 34, 52, 0.78));
        padding: 22px 24px;
        margin: 12px 0 22px;
        box-shadow: 0 18px 38px rgba(2, 6, 23, 0.22);
    }
    .hero-panel h1,
    .hero-panel h2,
    .hero-panel h3 {
        color: #f8fafc;
    }
    .hero-panel h1 {
        font-size: 2.1rem;
        line-height: 1.15;
    }
    .detail-hero-title {
        margin: 0 0 6px;
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1.12;
    }
    .detail-hero-meta {
        color: #cbd5e1;
        font-size: 1rem;
        font-weight: 800;
    }
    .hero-muted {
        color: #cbd5e1;
        font-size: 17px;
        font-weight: 700;
    }
    .metric-card {
        border: 1px solid #cbd7e6;
        border-radius: 14px;
        background: #ffffff;
        padding: 18px 20px;
        min-height: 112px;
        box-shadow: 0 8px 22px rgba(39, 62, 92, 0.07);
    }
    .metric-card .label {
        color: #52657f;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .metric-card .value {
        color: #102033;
        font-size: 27px;
        font-weight: 800;
    }
    .portfolio-valuation-board {
        border: 1px solid #d8e2ef;
        border-radius: 16px;
        background:
            radial-gradient(circle at 16% 14%, rgba(34, 211, 238, 0.10), transparent 30%),
            linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        padding: 18px;
        margin: 12px 0 16px;
        box-shadow: 0 16px 30px rgba(2, 6, 23, 0.10);
    }
    .portfolio-valuation-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 14px;
        padding-bottom: 14px;
        border-bottom: 1px solid #d8e2ef;
    }
    .portfolio-valuation-kicker {
        color: #0e7490;
        font-size: 0.76rem;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .portfolio-valuation-title {
        color: #0f172a;
        font-size: 1.55rem;
        line-height: 1.1;
        font-weight: 950;
        margin-top: 5px;
    }
    .portfolio-valuation-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 10px;
    }
    .portfolio-valuation-chip {
        color: #334155;
        background: #f8fafc;
        border: 1px solid #d8e2ef;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 0.78rem;
        font-weight: 800;
    }
    .portfolio-valuation-status {
        color: #ffffff;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.78rem;
        font-weight: 950;
        white-space: nowrap;
    }
    .portfolio-score-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 14px;
    }
    .portfolio-score-card {
        --accent: #0891b2;
        border: 1px solid #d8e2ef;
        border-top: 4px solid var(--accent);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.82);
        min-height: 124px;
        padding: 12px;
    }
    .portfolio-score-card.good { --accent: #059669; }
    .portfolio-score-card.mid { --accent: #0891b2; }
    .portfolio-score-card.watch { --accent: #d97706; }
    .portfolio-score-card.risk { --accent: #dc2626; }
    .portfolio-score-label {
        color: #52657f;
        font-size: 0.74rem;
        font-weight: 950;
        text-transform: uppercase;
    }
    .portfolio-score-value {
        color: var(--accent);
        font-size: 1.45rem;
        font-weight: 950;
        line-height: 1;
        margin-top: 10px;
    }
    .portfolio-score-bar {
        height: 8px;
        border-radius: 999px;
        background: #e2e8f0;
        overflow: hidden;
        margin-top: 10px;
    }
    .portfolio-score-bar span {
        display: block;
        width: var(--value);
        height: 100%;
        background: var(--accent);
    }
    .portfolio-score-detail {
        color: #475569;
        font-size: 0.78rem;
        line-height: 1.35;
        opacity: 0;
        max-height: 0;
        overflow: hidden;
        transition: opacity 160ms ease, max-height 160ms ease, margin-top 160ms ease;
    }
    .portfolio-score-card:hover .portfolio-score-detail,
    .portfolio-score-card:focus .portfolio-score-detail {
        opacity: 1;
        max-height: 86px;
        margin-top: 8px;
    }
    .guide-shot {
        border: 1px solid #334155;
        border-radius: 14px;
        overflow: hidden;
        margin: 12px 0 20px;
    }
    .stock-card-link {
        display: block;
        text-decoration: none !important;
        color: inherit !important;
    }
    .stock-card-panel {
        border: 1px solid #d8e2ef;
        border-radius: 16px;
        background:
            radial-gradient(circle at 18% 12%, rgba(34, 211, 238, 0.08), transparent 28%),
            linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        padding: 16px;
        min-height: 292px;
        box-shadow: 0 16px 30px rgba(2, 6, 23, 0.18);
        transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;
    }
    .stock-card-panel:hover {
        transform: translateY(-2px);
        border-color: #0891b2;
        box-shadow: 0 18px 38px rgba(8, 145, 178, 0.18);
    }
    .stock-card-head {
        display: grid;
        grid-template-columns: 52px minmax(0, 1fr);
        gap: 12px;
        align-items: start;
        padding-bottom: 14px;
        border-bottom: 1px solid #d8e2ef;
    }
    .company-logo {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        color: #ffffff;
        font-size: 17px;
        font-weight: 950;
        background:
            radial-gradient(circle at 30% 25%, rgba(255,255,255,0.35), transparent 32%),
            linear-gradient(135deg, #0f172a, #0891b2);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.22);
    }
    .company-title {
        color: #0f172a !important;
        font-size: 1.18rem;
        font-weight: 900;
        line-height: 1.18;
        margin: 0;
        min-height: 2.8em;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .company-meta {
        color: #475569;
        font-size: 0.82rem;
        font-weight: 750;
        margin-top: 4px;
    }
    .ticker-pill {
        display: inline-flex;
        align-items: center;
        color: #f8fafc;
        background: #111827;
        border-radius: 999px;
        padding: 3px 9px;
        margin-right: 7px;
        font-size: 0.76rem;
        font-weight: 900;
        letter-spacing: 0.04em;
    }
    .stock-card-price {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 12px;
        margin: 16px 0 14px;
        padding-bottom: 14px;
        border-bottom: 1px solid #d8e2ef;
    }
    .stock-card-price .price {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1;
    }
    .status-chip {
        color: white;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.75rem;
        font-weight: 850;
        white-space: nowrap;
    }
    .stock-card-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        color: #334155;
        font-size: 0.8rem;
        margin-bottom: 12px;
    }
    .stock-card-stats b {
        display: block;
        color: #0f172a;
        font-size: 1rem;
        margin-top: 3px;
    }
    .stock-card-actions {
        display: none;
    }
    .stock-action-chip {
        flex: 1;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 850;
    }
    .stock-card-link:hover .company-title {
        color: #0e7490 !important;
    }
    .click-hint {
        color: #64748b;
        font-size: 12px;
        margin-top: 8px;
    }
    .life-entry-wrap {
        min-height: 86vh;
        display: grid;
        align-items: center;
        padding: 28px 0 46px;
    }
    .life-entry {
        position: relative;
        overflow: hidden;
        border-radius: 34px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        background:
            radial-gradient(circle at 66% 18%, rgba(34, 211, 238, 0.22), transparent 26%),
            radial-gradient(circle at 24% 24%, rgba(16, 185, 129, 0.16), transparent 28%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(17, 24, 39, 0.94) 48%, rgba(4, 9, 15, 0.98));
        box-shadow: 0 32px 90px rgba(0, 0, 0, 0.34);
        padding: clamp(30px, 4.2vw, 58px);
    }
    .life-entry::before {
        content: "";
        position: absolute;
        inset: 0;
        opacity: 0.22;
        background:
            linear-gradient(90deg, rgba(34,211,238,0.12) 1px, transparent 1px),
            linear-gradient(0deg, rgba(16,185,129,0.09) 1px, transparent 1px);
        background-size: 48px 48px;
        animation: dataSweep 18s linear infinite;
    }
    .life-entry::after {
        content: "";
        position: absolute;
        inset: auto -18% 0 -18%;
        height: 38%;
        opacity: 0.24;
        background:
            linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.26), transparent),
            radial-gradient(ellipse at 50% 100%, rgba(20, 184, 166, 0.22), transparent 62%);
        animation: lifeBeam 8s ease-in-out infinite;
    }
    .life-entry-grid {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: minmax(0, 0.92fr) minmax(390px, 1.08fr);
        gap: clamp(34px, 4vw, 70px);
        align-items: center;
    }
    .life-kicker {
        color: #67e8f9;
        font-size: 0.82rem;
        font-weight: 900;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }
    .life-title {
        color: #f8fafc;
        font-size: clamp(2.6rem, 4.7vw, 5.25rem);
        line-height: 1.02;
        letter-spacing: 0;
        font-weight: 950;
        margin: 0;
    }
    .life-title span {
        color: #67e8f9;
        text-shadow: 0 0 32px rgba(34, 211, 238, 0.36);
        animation: titleGlow 5s ease-in-out infinite;
    }
    .life-copy {
        max-width: 720px;
        margin: 24px 0 24px;
        color: #e2e8f0;
        font-size: clamp(1rem, 1.45vw, 1.17rem);
        line-height: 1.58;
        font-weight: 760;
        padding: 20px 22px;
        border-radius: 22px;
        background: rgba(8, 13, 22, 0.38);
        border: 1px solid rgba(148, 163, 184, 0.14);
    }
    .life-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 11px;
        margin-top: 18px;
    }
    .life-pill {
        border: 1px solid rgba(103, 232, 249, 0.42);
        background: rgba(15, 23, 42, 0.82);
        color: #f0f9ff;
        border-radius: 999px;
        padding: 9px 15px;
        font-size: 0.84rem;
        font-weight: 900;
        box-shadow: inset 0 0 18px rgba(34, 211, 238, 0.06);
        position: relative;
        overflow: hidden;
    }
    .life-pill::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.18) 45%, transparent 70%);
        transform: translateX(-120%);
        animation: pillShine 7s ease-in-out infinite;
    }
    .life-map {
        min-height: 560px;
        border-radius: 32px;
        border: 1px solid rgba(148, 163, 184, 0.34);
        background:
            radial-gradient(circle at 50% 48%, rgba(34, 211, 238, 0.24), transparent 33%),
            radial-gradient(circle at 18% 20%, rgba(96, 165, 250, 0.10), transparent 23%),
            linear-gradient(160deg, rgba(15, 23, 42, 0.74), rgba(8, 13, 22, 0.94));
        box-shadow: inset 0 0 46px rgba(34, 211, 238, 0.10), 0 20px 48px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }
    .life-horizon {
        position: absolute;
        left: -18%;
        right: -18%;
        top: 50%;
        height: 44%;
        pointer-events: none;
        opacity: 0.30;
        background:
            radial-gradient(ellipse at 50% 50%, rgba(103, 232, 249, 0.18), transparent 44%),
            linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.28), rgba(20, 184, 166, 0.20), transparent);
        filter: blur(10px);
        transform: translateY(-50%) rotate(-8deg);
        animation: lifeHorizon 9s ease-in-out infinite;
    }
    .life-stream {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 3px;
        height: 46%;
        transform-origin: 50% 0;
        pointer-events: none;
        z-index: 1;
        opacity: 0.54;
        background: linear-gradient(180deg, rgba(103, 232, 249, 0.74), rgba(20, 184, 166, 0.18), transparent);
        filter: drop-shadow(0 0 10px rgba(34, 211, 238, 0.45));
        animation: streamPulse 4.6s ease-in-out infinite;
    }
    .life-stream.s1 { transform: rotate(0deg); animation-delay: -0.2s; }
    .life-stream.s2 { transform: rotate(60deg); animation-delay: -0.8s; }
    .life-stream.s3 { transform: rotate(120deg); animation-delay: -1.4s; }
    .life-stream.s4 { transform: rotate(180deg); animation-delay: -2.0s; }
    .life-stream.s5 { transform: rotate(240deg); animation-delay: -2.6s; }
    .life-stream.s6 { transform: rotate(300deg); animation-delay: -3.2s; }
    .life-spark {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: #a7f3d0;
        box-shadow: 0 0 18px rgba(103, 232, 249, 0.88), 0 0 36px rgba(20, 184, 166, 0.45);
        z-index: 3;
        pointer-events: none;
        animation: sparkOrbit 8s linear infinite;
    }
    .life-spark.two {
        width: 7px;
        height: 7px;
        background: #67e8f9;
        animation: sparkOrbit 11s linear infinite reverse;
        animation-delay: -3s;
    }
    .life-spark.three {
        width: 6px;
        height: 6px;
        background: #fef3c7;
        animation: sparkOrbitWide 13s linear infinite;
        animation-delay: -5s;
    }
    .life-map::before {
        content: "";
        position: absolute;
        left: 13%;
        right: 13%;
        top: 49%;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(103, 232, 249, 0.38), transparent);
        animation: flowLine 4.8s ease-in-out infinite;
    }
    .life-map::after {
        content: "";
        position: absolute;
        top: 12%;
        bottom: 12%;
        left: 49.8%;
        width: 2px;
        background: linear-gradient(180deg, transparent, rgba(20, 184, 166, 0.30), transparent);
        animation: flowLine 5.4s ease-in-out infinite reverse;
    }
    .life-orbit {
        position: absolute;
        inset: 70px;
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 50%;
        animation: orbitSpin 24s linear infinite;
    }
    .life-orbit.two {
        inset: 126px;
        border-color: rgba(103, 232, 249, 0.26);
        animation: orbitSpin 18s linear infinite reverse;
    }
    .life-core {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 174px;
        height: 174px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        text-align: center;
        color: #f8fafc;
        font-size: 1.08rem;
        line-height: 1.5;
        font-weight: 950;
        background:
            radial-gradient(circle at 35% 26%, rgba(255,255,255,0.34), transparent 22%),
            linear-gradient(135deg, rgba(34, 211, 238, 0.38), rgba(20, 184, 166, 0.24)),
            rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(103, 232, 249, 0.48);
        box-shadow: 0 0 48px rgba(34, 211, 238, 0.32);
        animation: corePulse 3.6s ease-in-out infinite;
    }
    .life-node {
        position: absolute;
        width: 138px;
        min-height: 74px;
        display: grid;
        place-items: center;
        text-align: center;
        border-radius: 20px;
        padding: 12px 13px;
        color: #f8fafc;
        font-size: 0.88rem;
        line-height: 1.18;
        font-weight: 900;
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.38);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.22);
        z-index: 2;
        animation: nodeFloat 7s ease-in-out infinite;
    }
    .life-node.income { left: 54px; top: 110px; animation-delay: -0.5s; }
    .life-node.saving { right: 54px; top: 118px; animation-delay: -1.2s; }
    .life-node.risk { left: 54px; bottom: 118px; animation-delay: -2.1s; }
    .life-node.assets { right: 54px; bottom: 118px; animation-delay: -3.0s; }
    .life-node.goals { left: 50%; top: 46px; transform: translateX(-50%); animation-delay: -1.7s; }
    .life-node.diary { left: 50%; bottom: 46px; transform: translateX(-50%); animation-delay: -2.7s; }
    @keyframes orbitSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes corePulse {
        0%, 100% { box-shadow: 0 0 42px rgba(34, 211, 238, 0.26); }
        50% { box-shadow: 0 0 68px rgba(34, 211, 238, 0.46); }
    }
    @keyframes nodeFloat {
        0%, 100% { margin-top: 0; }
        50% { margin-top: -8px; }
    }
    @keyframes flowLine {
        0%, 100% { opacity: 0.14; transform: scaleX(0.72); }
        50% { opacity: 0.52; transform: scaleX(1); }
    }
    @keyframes lifeBeam {
        0%, 100% { transform: translateX(-8%); opacity: 0.16; }
        50% { transform: translateX(8%); opacity: 0.30; }
    }
    @keyframes lifeHorizon {
        0%, 100% { transform: translateY(-50%) rotate(-8deg) translateX(-4%); opacity: 0.18; }
        50% { transform: translateY(-50%) rotate(8deg) translateX(4%); opacity: 0.36; }
    }
    @keyframes streamPulse {
        0%, 100% { opacity: 0.16; height: 34%; }
        45% { opacity: 0.70; height: 48%; }
        70% { opacity: 0.30; height: 42%; }
    }
    @keyframes sparkOrbit {
        from { transform: rotate(0deg) translateX(154px) rotate(0deg); }
        to { transform: rotate(360deg) translateX(154px) rotate(-360deg); }
    }
    @keyframes sparkOrbitWide {
        from { transform: rotate(0deg) translateX(218px) rotate(0deg); }
        to { transform: rotate(360deg) translateX(218px) rotate(-360deg); }
    }
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 0 24px rgba(34, 211, 238, 0.26); }
        50% { text-shadow: 0 0 44px rgba(34, 211, 238, 0.58); }
    }
    @keyframes pillShine {
        0%, 72% { transform: translateX(-120%); }
        86% { transform: translateX(120%); }
        100% { transform: translateX(120%); }
    }
    div[data-testid="stButton"] button[kind="primary"] {
        border-radius: 999px;
        padding: 0.78rem 1.4rem;
        font-weight: 950;
        border: 1px solid rgba(103, 232, 249, 0.48);
        background: linear-gradient(135deg, #22d3ee, #14b8a6);
        color: #06202a;
        box-shadow: 0 18px 42px rgba(34, 211, 238, 0.20);
    }
    @media (max-width: 900px) {
        .life-entry-grid {
            grid-template-columns: 1fr;
        }
        .life-map {
            min-height: 460px;
        }
        .life-node {
            width: 112px;
            min-height: 62px;
            font-size: 0.76rem;
        }
        .life-node.income { left: 18px; top: 94px; }
        .life-node.saving { right: 18px; top: 94px; }
        .life-node.risk { left: 18px; bottom: 94px; }
        .life-node.assets { right: 18px; bottom: 94px; }
        .life-node.goals { top: 26px; }
        .life-node.diary { bottom: 26px; }
        .life-stream {
            height: 38%;
        }
        @keyframes sparkOrbit {
            from { transform: rotate(0deg) translateX(118px) rotate(0deg); }
            to { transform: rotate(360deg) translateX(118px) rotate(-360deg); }
        }
        @keyframes sparkOrbitWide {
            from { transform: rotate(0deg) translateX(160px) rotate(0deg); }
            to { transform: rotate(360deg) translateX(160px) rotate(-360deg); }
        }
    }
    .life-entry {
        border-color: rgba(125, 211, 252, 0.46);
        background:
            radial-gradient(circle at 22% 18%, rgba(254, 240, 138, 0.30), transparent 22%),
            radial-gradient(circle at 75% 18%, rgba(125, 211, 252, 0.38), transparent 28%),
            radial-gradient(circle at 42% 78%, rgba(134, 239, 172, 0.18), transparent 32%),
            linear-gradient(135deg, rgba(240, 249, 255, 0.96), rgba(224, 242, 254, 0.91) 42%, rgba(236, 253, 245, 0.94));
        box-shadow: 0 30px 90px rgba(14, 116, 144, 0.16);
    }
    .life-entry::before {
        opacity: 0.30;
        background:
            linear-gradient(90deg, rgba(14, 165, 233, 0.13) 1px, transparent 1px),
            linear-gradient(0deg, rgba(16, 185, 129, 0.10) 1px, transparent 1px);
    }
    .life-entry::after {
        opacity: 0.42;
        height: 46%;
        background:
            linear-gradient(90deg, transparent, rgba(250, 204, 21, 0.24), rgba(45, 212, 191, 0.24), transparent),
            radial-gradient(ellipse at 50% 100%, rgba(125, 211, 252, 0.34), transparent 62%);
    }
    .life-kicker {
        color: #0e7490;
        text-shadow: 0 0 18px rgba(103, 232, 249, 0.24);
    }
    .life-title {
        color: #0f172a;
    }
    .life-title span {
        color: #0891b2;
        text-shadow: 0 0 30px rgba(34, 211, 238, 0.28);
    }
    .life-copy {
        color: #1e293b;
        background: rgba(255, 255, 255, 0.58);
        border: 1px solid rgba(14, 165, 233, 0.18);
        box-shadow: 0 18px 42px rgba(14, 116, 144, 0.10);
    }
    .life-pill {
        background: rgba(255, 255, 255, 0.72);
        color: #0f3f4a;
        border-color: rgba(14, 116, 144, 0.28);
        box-shadow: 0 10px 24px rgba(14, 116, 144, 0.08), inset 0 0 18px rgba(34, 211, 238, 0.08);
    }
    .life-map {
        border-color: rgba(14, 116, 144, 0.24);
        background:
            radial-gradient(circle at 50% 43%, rgba(254, 240, 138, 0.44), transparent 18%),
            radial-gradient(circle at 50% 50%, rgba(125, 211, 252, 0.34), transparent 34%),
            radial-gradient(circle at 25% 76%, rgba(134, 239, 172, 0.24), transparent 26%),
            linear-gradient(160deg, rgba(255, 255, 255, 0.76), rgba(224, 242, 254, 0.72));
        box-shadow: inset 0 0 42px rgba(14, 165, 233, 0.10), 0 20px 48px rgba(14, 116, 144, 0.13);
    }
    .life-map::before {
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.46), transparent);
    }
    .life-map::after {
        background: linear-gradient(180deg, transparent, rgba(16, 185, 129, 0.38), transparent);
    }
    .life-sun {
        position: absolute;
        right: 58px;
        top: 52px;
        width: 96px;
        height: 96px;
        border-radius: 999px;
        pointer-events: none;
        z-index: 1;
        background: radial-gradient(circle, rgba(254, 240, 138, 0.95), rgba(251, 191, 36, 0.28) 52%, transparent 72%);
        box-shadow: 0 0 58px rgba(250, 204, 21, 0.34);
        animation: sunBreathe 6s ease-in-out infinite;
    }
    .life-path {
        position: absolute;
        left: 9%;
        right: 9%;
        bottom: 18%;
        height: 90px;
        pointer-events: none;
        z-index: 1;
        opacity: 0.64;
        border-bottom: 5px solid rgba(14, 165, 233, 0.28);
        border-radius: 50%;
        transform: rotate(-2deg);
    }
    .life-path::after {
        content: "";
        position: absolute;
        left: 6%;
        bottom: -9px;
        width: 18px;
        height: 18px;
        border-radius: 999px;
        background: #0ea5e9;
        box-shadow: 0 0 22px rgba(14, 165, 233, 0.70);
        animation: pathJourney 9s ease-in-out infinite;
    }
    .life-human {
        position: absolute;
        left: 50%;
        top: 48%;
        transform: translate(-50%, -50%);
        width: 164px;
        height: 220px;
        z-index: 4;
        pointer-events: none;
        animation: humanRise 5.5s ease-in-out infinite;
    }
    .life-human::before {
        content: "";
        position: absolute;
        left: 50%;
        top: 0;
        transform: translateX(-50%);
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #fef3c7, #fbbf24);
        box-shadow: 0 0 34px rgba(251, 191, 36, 0.34);
    }
    .life-human::after {
        content: "";
        position: absolute;
        left: 50%;
        top: 64px;
        transform: translateX(-50%);
        width: 86px;
        height: 122px;
        border-radius: 44px 44px 34px 34px;
        background: linear-gradient(160deg, rgba(14, 165, 233, 0.88), rgba(20, 184, 166, 0.84));
        box-shadow: 0 18px 46px rgba(14, 116, 144, 0.20);
    }
    .life-arms {
        position: absolute;
        left: 50%;
        top: 94px;
        transform: translateX(-50%);
        width: 156px;
        height: 16px;
        border-radius: 999px;
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.82), rgba(20, 184, 166, 0.82), transparent);
        z-index: 5;
    }
    .life-core {
        width: 198px;
        height: 198px;
        color: #0f172a;
        background:
            radial-gradient(circle at 34% 24%, rgba(255,255,255,0.62), transparent 22%),
            linear-gradient(135deg, rgba(255, 255, 255, 0.70), rgba(186, 230, 253, 0.40)),
            rgba(236, 253, 245, 0.64);
        border-color: rgba(14, 165, 233, 0.38);
        box-shadow: 0 0 54px rgba(14, 165, 233, 0.20);
        opacity: 0.54;
    }
    .life-node {
        color: #0f172a;
        background: rgba(255, 255, 255, 0.74);
        border-color: rgba(14, 116, 144, 0.22);
        box-shadow: 0 16px 34px rgba(14, 116, 144, 0.12);
        backdrop-filter: blur(8px);
    }
    .life-stream {
        background: linear-gradient(180deg, rgba(14, 165, 233, 0.68), rgba(20, 184, 166, 0.22), transparent);
        filter: drop-shadow(0 0 12px rgba(14, 165, 233, 0.42));
    }
    .life-horizon {
        background:
            radial-gradient(ellipse at 50% 50%, rgba(250, 204, 21, 0.20), transparent 44%),
            linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.28), rgba(16, 185, 129, 0.22), transparent);
    }
    @keyframes sunBreathe {
        0%, 100% { transform: scale(0.96); opacity: 0.58; }
        50% { transform: scale(1.08); opacity: 0.90; }
    }
    @keyframes humanRise {
        0%, 100% { margin-top: 0; }
        50% { margin-top: -10px; }
    }
    @keyframes pathJourney {
        0% { transform: translateX(0) scale(0.82); opacity: 0.36; }
        42% { opacity: 0.90; }
        100% { transform: translateX(540px) scale(1.12); opacity: 0.20; }
    }
    .homepage-visual {
        min-height: 620px;
        aspect-ratio: 1672 / 941;
        padding: 0;
        border-color: rgba(37, 99, 235, 0.20);
        background:
            linear-gradient(135deg, #f8fbff 0%, #dff4ff 52%, #fff7ed 100%);
        background-size: cover;
        background-position: center top;
        background-repeat: no-repeat;
        color: #0f172a;
        box-shadow: 0 32px 90px rgba(15, 23, 42, 0.20);
    }
    .homepage-bg-img {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center top;
        z-index: 0;
    }
    .homepage-visual::before {
        opacity: 0.10;
        background:
            linear-gradient(115deg, transparent 0%, transparent 42%, rgba(255,255,255,0.54) 48%, rgba(125,211,252,0.18) 52%, transparent 58%);
        background-size: 180% 100%, auto;
        animation: homeLightSweep 9s ease-in-out infinite;
    }
    .homepage-visual::after {
        display: none;
        inset: auto -12% 0 -12%;
        height: 30%;
        opacity: 0.46;
        background:
            linear-gradient(90deg, transparent, rgba(59,130,246,0.18), rgba(20,184,166,0.20), rgba(250,204,21,0.20), transparent),
            radial-gradient(ellipse at 72% 100%, rgba(255, 255, 255, 0.58), transparent 66%);
        animation: homeGlowRoad 8s ease-in-out infinite;
    }
    .home-nav {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 22px;
        min-height: 88px;
        padding: 18px 34px;
        background: rgba(255, 255, 255, 0.93);
        border-bottom: 1px solid rgba(148, 163, 184, 0.20);
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        backdrop-filter: blur(16px);
    }
    .home-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 950;
    }
    .home-brand-mark {
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        border-radius: 14px;
        color: white;
        font-size: 1.32rem;
        background: linear-gradient(135deg, #2563eb, #22d3ee 46%, #14b8a6);
        box-shadow: 0 14px 28px rgba(37, 99, 235, 0.22);
    }
    .home-brand small {
        color: #2563eb;
        font-size: 0.9rem;
        margin-left: 4px;
    }
    .home-nav-links {
        display: flex;
        gap: clamp(16px, 3vw, 46px);
        color: #1e293b;
        font-size: 0.92rem;
        font-weight: 760;
    }
    .home-nav-actions {
        display: none;
        gap: 10px;
    }
    .home-action {
        border-radius: 14px;
        padding: 11px 18px;
        border: 1px solid rgba(37, 99, 235, 0.30);
        background: rgba(255, 255, 255, 0.72);
        color: #1d4ed8;
        font-weight: 900;
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
    }
    .home-action.primary {
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        color: #ffffff;
        border-color: rgba(37, 99, 235, 0.0);
    }
    .homepage-visual.has-home-image .life-entry-grid {
        display: none;
    }
    .homepage-entry-hotspot {
        position: absolute;
        z-index: 4;
        top: 51.0%;
        height: 5.8%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        border-radius: 999px;
        padding: 0 14px;
        text-indent: 0;
        overflow: hidden;
        outline: 0;
        cursor: pointer;
        color: #ffffff !important;
        -webkit-text-fill-color: currentColor !important;
        text-decoration: none !important;
        font-size: clamp(0.72rem, 1.05vw, 1.06rem);
        font-weight: 950;
        letter-spacing: 0;
        line-height: 1;
        white-space: nowrap;
        backdrop-filter: blur(12px);
        transform: translateZ(0);
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }
    .homepage-entry-hotspot.primary {
        left: 4.75%;
        width: 13.85%;
        background: linear-gradient(135deg, #2563eb, #0ea5e9 70%, #14b8a6);
        border: 1px solid rgba(255, 255, 255, 0.38);
        box-shadow: 0 16px 34px rgba(37, 99, 235, 0.30);
    }
    .homepage-entry-hotspot.secondary {
        left: 19.65%;
        width: 12.70%;
        color: #1d4ed8 !important;
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(37, 99, 235, 0.36);
        box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10);
    }
    .homepage-entry-hotspot:hover {
        transform: translateY(-2px);
        filter: saturate(1.04);
    }
    .homepage-entry-hotspot:focus-visible {
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.30);
    }
    .homepage-mobile-cta {
        display: none;
    }
    .homepage-direct-entry {
        position: relative;
        z-index: 5;
        display: flex;
        justify-content: center;
        margin: 20px auto 0;
        width: min(100%, 680px);
    }
    .homepage-direct-entry a {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        min-height: 58px;
        padding: 0 24px;
        border-radius: 999px;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-decoration: none !important;
        font-size: clamp(1rem, 1.7vw, 1.32rem);
        font-weight: 950;
        letter-spacing: 0;
        background: linear-gradient(135deg, #0ea5e9, #14b8a6 62%, #2563eb);
        border: 1px solid rgba(255, 255, 255, 0.48);
        box-shadow: 0 20px 44px rgba(14, 165, 233, 0.30);
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }
    .homepage-direct-entry a::after {
        content: "→";
        font-size: 1.25em;
        line-height: 1;
    }
    .homepage-direct-entry a:hover {
        transform: translateY(-2px);
        filter: saturate(1.04);
        box-shadow: 0 24px 52px rgba(37, 99, 235, 0.32);
    }
    .homepage-visual .life-kicker {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        padding: 9px 14px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(14, 165, 233, 0.18);
        color: #0f3f4a;
        letter-spacing: 0;
        text-transform: none;
        box-shadow: 0 12px 28px rgba(14, 116, 144, 0.08);
    }
    .homepage-visual .life-title {
        margin-top: 18px;
        max-width: 620px;
        font-size: clamp(3rem, 5vw, 5.6rem);
        color: #071631;
        text-shadow: 0 1px 0 rgba(255,255,255,0.40);
    }
    .homepage-visual .life-title span {
        color: transparent;
        background: linear-gradient(120deg, #14b8a6, #0ea5e9 52%, #2563eb);
        -webkit-background-clip: text;
        background-clip: text;
        text-shadow: none;
    }
    .homepage-visual .life-copy {
        max-width: 520px;
        padding: 0;
        margin-top: 24px;
        background: transparent;
        border: 0;
        box-shadow: none;
        color: #1e293b;
        font-size: clamp(1rem, 1.3vw, 1.16rem);
        line-height: 1.55;
        font-weight: 680;
    }
    .home-cta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin: 26px 0 16px;
    }
    .home-cta {
        border-radius: 999px;
        padding: 14px 22px;
        font-weight: 950;
        color: #ffffff;
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        box-shadow: 0 18px 38px rgba(37, 99, 235, 0.24);
    }
    .home-cta.secondary {
        color: #1d4ed8;
        background: rgba(255, 255, 255, 0.70);
        border: 1px solid rgba(37, 99, 235, 0.30);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
    }
    .home-proof {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #334155;
        font-size: 0.9rem;
        font-weight: 720;
        margin-top: 10px;
    }
    .home-proof-dots {
        display: flex;
    }
    .home-proof-dot {
        width: 30px;
        height: 30px;
        margin-left: -7px;
        border-radius: 999px;
        border: 2px solid rgba(255,255,255,0.88);
        background: linear-gradient(135deg, #2563eb, #22d3ee);
    }
    .home-proof-dot:first-child {
        margin-left: 0;
    }
    .homepage-visual .life-pill-row {
        display: none;
    }
    .homepage-visual .life-map {
        min-height: 560px;
        background:
            radial-gradient(circle at 50% 46%, rgba(255,255,255,0.76), rgba(219,234,254,0.58) 18%, rgba(255,255,255,0.18) 34%, transparent 50%),
            linear-gradient(135deg, rgba(255,255,255,0.40), rgba(255,255,255,0.12));
        border: 1px solid rgba(255,255,255,0.54);
        backdrop-filter: blur(12px);
        box-shadow: inset 0 0 42px rgba(255,255,255,0.18), 0 24px 52px rgba(15, 23, 42, 0.12);
    }
    .homepage-visual .life-node {
        color: #0f172a;
        background: rgba(255,255,255,0.72);
        border-color: rgba(37, 99, 235, 0.18);
        box-shadow: 0 14px 30px rgba(37, 99, 235, 0.10);
    }
    .homepage-visual .life-core {
        opacity: 1;
        color: #0f172a;
        background:
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.92), rgba(224,242,254,0.84) 48%, rgba(255,255,255,0.48));
        border-color: rgba(59, 130, 246, 0.24);
        box-shadow: 0 0 80px rgba(14, 165, 233, 0.26);
    }
    .home-module-grid {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 14px;
        margin-top: 24px;
    }
    .homepage-visual.has-home-image .home-module-grid {
        display: none;
    }
    .home-module-card {
        min-height: 128px;
        border-radius: 22px;
        padding: 18px;
        background: rgba(255,255,255,0.70);
        border: 1px solid rgba(255,255,255,0.72);
        box-shadow: 0 18px 38px rgba(15, 23, 42, 0.10);
        backdrop-filter: blur(10px);
        color: #0f172a;
    }
    .home-module-icon {
        width: 34px;
        height: 34px;
        border-radius: 12px;
        display: grid;
        place-items: center;
        color: white;
        margin-bottom: 12px;
        background: linear-gradient(135deg, #2563eb, #22d3ee);
    }
    .home-module-card b {
        display: block;
        font-size: 0.98rem;
        margin-bottom: 7px;
    }
    .home-module-card span {
        color: #475569;
        font-size: 0.84rem;
        line-height: 1.35;
    }
    @keyframes homeLightSweep {
        0%, 100% { background-position: -120% 0, center; opacity: 0.22; }
        50% { background-position: 120% 0, center; opacity: 0.46; }
    }
    @keyframes homeGlowRoad {
        0%, 100% { transform: translateX(-5%); opacity: 0.34; }
        50% { transform: translateX(5%); opacity: 0.56; }
    }
    @media (max-width: 1100px) {
        .portfolio-score-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .home-nav {
            flex-wrap: wrap;
        }
        .home-nav-links {
            order: 3;
            width: 100%;
            justify-content: center;
        }
        .homepage-visual.has-home-image .life-entry-grid {
            grid-template-columns: 1fr;
        }
        .home-module-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 680px) {
        .top-language-toggle {
            top: 14px;
            right: 14px;
            padding: 5px;
        }
        .top-language-toggle .language-toggle-mark,
        .top-language-toggle a {
            width: 31px;
            height: 31px;
            font-size: 0.70rem;
        }
        .nora-ontology {
            padding: 14px;
            margin-bottom: 16px;
        }
        .nora-ontology-top {
            display: block;
        }
        .nora-ontology-caption {
            max-width: none;
            text-align: left;
            margin-top: 8px;
        }
        .nora-path {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .nora-node {
            min-height: 78px;
        }
        .nora-node::after {
            display: none;
        }
        .nora-detail {
            position: static;
            opacity: 1;
            pointer-events: auto;
            transform: none;
            margin-top: 8px;
            font-size: 0.70rem;
        }
        .nora-modules {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .portfolio-valuation-head {
            display: block;
        }
        .portfolio-valuation-status {
            display: inline-block;
            margin-top: 12px;
        }
        .portfolio-score-grid {
            grid-template-columns: 1fr;
        }
        .homepage-visual {
            padding: 0;
            min-height: auto;
            aspect-ratio: auto;
        }
        .homepage-visual.has-home-image {
            overflow: hidden;
            border-radius: 26px;
            background:
                linear-gradient(135deg, rgba(240, 249, 255, 0.96), rgba(236, 253, 245, 0.90));
            box-shadow: 0 20px 46px rgba(14, 165, 233, 0.16);
        }
        .homepage-visual.has-home-image .homepage-bg-img {
            position: relative;
            inset: auto;
            display: block;
            width: 100%;
            height: auto;
            aspect-ratio: 1672 / 941;
            object-fit: contain;
            object-position: center top;
        }
        .homepage-visual.has-home-image .home-nav {
            display: none;
        }
        .homepage-entry-hotspot {
            display: none;
        }
        .homepage-mobile-cta {
            position: relative;
            z-index: 3;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 48px;
            margin: 12px 14px 16px;
            padding: 0 16px;
            border-radius: 999px;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            text-decoration: none !important;
            font-size: 0.98rem;
            font-weight: 950;
            letter-spacing: 0;
            background: linear-gradient(135deg, #0ea5e9, #14b8a6);
            box-shadow: 0 14px 30px rgba(14, 165, 233, 0.22);
        }
        .homepage-direct-entry {
            margin: 14px 14px 18px;
            width: auto;
        }
        .homepage-direct-entry a {
            min-height: 52px;
            padding: 0 16px;
            font-size: 1rem;
        }
        .home-nav-links,
        .home-nav-actions {
            display: none;
        }
        .homepage-visual .life-title {
            font-size: 2.7rem;
        }
        .home-module-grid {
            grid-template-columns: 1fr;
        }
    }
    /* First-screen readability pass: calmer background, smaller type, visual-first cards. */
    .life-entry-wrap {
        min-height: calc(100vh - 42px);
        align-items: start;
        padding: 16px 0 30px;
    }
    .homepage-visual {
        min-height: 560px;
        aspect-ratio: auto;
        border-radius: 24px;
        border: 1px solid rgba(37, 99, 235, 0.14);
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(240, 249, 255, 0.86)),
            linear-gradient(135deg, #f8fbff 0%, #e7f5fb 50%, #f8f3e8 100%);
        box-shadow: 0 22px 58px rgba(15, 23, 42, 0.12);
    }
    .homepage-visual::before {
        opacity: 0.14;
        animation: none;
        background:
            linear-gradient(90deg, rgba(14, 116, 144, 0.12) 1px, transparent 1px),
            linear-gradient(0deg, rgba(100, 116, 139, 0.10) 1px, transparent 1px);
        background-size: 54px 54px;
    }
    .homepage-visual::after,
    .homepage-entry-hotspot,
    .homepage-mobile-cta,
    .homepage-visual .life-sun,
    .homepage-visual .life-spark,
    .homepage-visual .life-path {
        display: none !important;
    }
    .home-nav {
        min-height: 64px;
        padding: 12px 24px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
    }
    .home-brand {
        gap: 10px;
        font-size: 1rem;
        letter-spacing: 0;
    }
    .home-brand-mark {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        font-size: 1rem;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.16);
    }
    .home-brand small {
        font-size: 0.74rem;
    }
    .home-nav-links {
        gap: 22px;
        color: #475569;
        font-size: 0.78rem;
        font-weight: 720;
    }
    .homepage-visual .life-entry-grid {
        grid-template-columns: minmax(0, 0.9fr) minmax(360px, 1fr);
        gap: 30px;
        padding: 34px 38px 0;
        align-items: center;
    }
    .homepage-visual .life-kicker {
        padding: 7px 11px;
        color: #0f766e;
        font-size: 0.74rem;
        font-weight: 820;
        box-shadow: none;
    }
    .homepage-visual .life-title {
        max-width: 520px;
        margin-top: 14px;
        color: #0f172a;
        font-size: 2.75rem;
        line-height: 1.05;
        font-weight: 900;
        text-shadow: none;
    }
    .homepage-visual .life-title span {
        color: #0e7490;
        background: none;
        -webkit-background-clip: initial;
        background-clip: initial;
    }
    .homepage-visual .life-copy {
        max-width: 470px;
        margin: 16px 0 0;
        color: #334155;
        font-size: 0.98rem;
        line-height: 1.48;
        font-weight: 620;
    }
    .home-cta-row {
        gap: 10px;
        margin: 20px 0 16px;
    }
    .home-cta {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        padding: 0 16px;
        border-radius: 12px;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-weight: 820;
        background: linear-gradient(135deg, #0f766e, #2563eb);
        box-shadow: 0 12px 24px rgba(37, 99, 235, 0.16);
    }
    .home-cta.secondary {
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(37, 99, 235, 0.18);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
    }
    .home-signal-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        max-width: 610px;
        margin-top: 18px;
    }
    .home-signal-card {
        min-height: 72px;
        border-radius: 14px;
        padding: 13px;
        color: #0f172a;
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.07);
        outline: 0;
        transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
    }
    .home-signal-card::before {
        content: "";
        display: block;
        width: 28px;
        height: 6px;
        border-radius: 999px;
        margin-bottom: 10px;
        background: #0f766e;
    }
    .home-signal-card.direction::before {
        background: #2563eb;
    }
    .home-signal-card.crisis::before {
        background: #d97706;
    }
    .home-signal-card b {
        display: block;
        font-size: 0.86rem;
        line-height: 1.2;
        font-weight: 860;
    }
    .home-signal-card span {
        display: block;
        margin-top: 8px;
        color: #475569;
        font-size: 0.74rem;
        line-height: 1.34;
        opacity: 0;
        max-height: 0;
        overflow: hidden;
        transition: opacity 140ms ease, max-height 140ms ease;
    }
    .home-signal-card:hover,
    .home-signal-card:focus {
        transform: translateY(-1px);
        border-color: rgba(14, 116, 144, 0.34);
        box-shadow: 0 16px 30px rgba(15, 23, 42, 0.10);
    }
    .home-signal-card:hover span,
    .home-signal-card:focus span {
        opacity: 1;
        max-height: 86px;
    }
    .home-proof {
        margin-top: 12px;
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 620;
    }
    .homepage-visual .life-map {
        min-height: 430px;
        border-radius: 22px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.62), rgba(236,253,245,0.28)),
            linear-gradient(135deg, rgba(219,234,254,0.38), rgba(255,247,237,0.30));
        border-color: rgba(14, 116, 144, 0.14);
        box-shadow: inset 0 0 34px rgba(255,255,255,0.30), 0 18px 38px rgba(15, 23, 42, 0.08);
    }
    .homepage-visual .life-map::before,
    .homepage-visual .life-map::after {
        opacity: 0.26;
        animation: none;
    }
    .homepage-visual .life-horizon {
        opacity: 0.12;
        filter: blur(6px);
        animation: none;
    }
    .homepage-visual .life-stream {
        height: 34%;
        opacity: 0.20;
        animation: none;
        filter: none;
    }
    .homepage-visual .life-orbit {
        inset: 58px;
        opacity: 0.20;
        animation: none;
        border-color: rgba(14, 116, 144, 0.20);
    }
    .homepage-visual .life-orbit.two {
        inset: 112px;
        opacity: 0.18;
    }
    .homepage-visual .life-core {
        width: 132px;
        height: 132px;
        color: #0f172a;
        font-size: 0.85rem;
        line-height: 1.34;
        font-weight: 850;
        animation: none;
        box-shadow: 0 18px 40px rgba(14, 116, 144, 0.12);
    }
    .homepage-visual .life-node {
        width: 112px;
        min-height: 58px;
        border-radius: 14px;
        padding: 9px 10px;
        font-size: 0.74rem;
        line-height: 1.18;
        font-weight: 820;
        animation: none;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.07);
    }
    .homepage-visual .life-node.income { left: 34px; top: 88px; }
    .homepage-visual .life-node.saving { right: 34px; top: 88px; }
    .homepage-visual .life-node.risk { left: 34px; bottom: 88px; }
    .homepage-visual .life-node.assets { right: 34px; bottom: 88px; }
    .homepage-visual .life-node.goals { top: 30px; }
    .homepage-visual .life-node.diary { bottom: 30px; }
    .home-module-grid {
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 10px;
        margin: 18px 38px 30px;
    }
    .home-module-card {
        min-height: 92px;
        border-radius: 14px;
        padding: 13px;
        background: rgba(255,255,255,0.70);
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
        outline: 0;
    }
    .home-module-icon {
        width: 28px;
        height: 28px;
        border-radius: 9px;
        margin-bottom: 9px;
        font-size: 0.70rem;
        font-weight: 840;
        background: linear-gradient(135deg, #0f766e, #2563eb);
    }
    .home-module-card b {
        font-size: 0.82rem;
        line-height: 1.18;
        font-weight: 820;
    }
    .home-module-card span {
        display: block;
        margin-top: 7px;
        color: #475569;
        font-size: 0.72rem;
        line-height: 1.32;
        opacity: 0;
        max-height: 0;
        overflow: hidden;
        transition: opacity 140ms ease, max-height 140ms ease;
    }
    .home-module-card:hover span,
    .home-module-card:focus span {
        opacity: 1;
        max-height: 72px;
    }
    .homepage-direct-entry {
        display: none !important;
    }
    .top-language-toggle {
        top: 72px;
        right: 28px;
        background: rgba(255, 255, 255, 0.92);
        border-color: rgba(14, 116, 144, 0.18);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
    }
    .top-language-toggle .language-toggle-mark {
        color: #0f766e;
        background: rgba(20, 184, 166, 0.10);
        border-color: rgba(20, 184, 166, 0.20);
    }
    .top-language-toggle a {
        color: #334155 !important;
    }
    .top-language-toggle a:hover,
    .top-language-toggle a:focus {
        color: #0f172a !important;
        border-color: rgba(14, 116, 144, 0.22);
        background: rgba(14, 116, 144, 0.08);
    }
    .top-language-toggle a.active {
        color: #ffffff !important;
        background: #0f766e;
        border-color: rgba(15, 118, 110, 0.10);
        box-shadow: 0 8px 18px rgba(15, 118, 110, 0.20);
    }
    @media (max-width: 1100px) {
        .homepage-visual .life-entry-grid {
            grid-template-columns: 1fr;
            padding: 28px 28px 0;
        }
        .home-signal-row {
            max-width: none;
        }
        .home-module-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
            margin-left: 28px;
            margin-right: 28px;
        }
    }
    @media (max-width: 680px) {
        .life-entry-wrap {
            min-height: auto;
            padding: 8px 0 22px;
        }
        .homepage-visual {
            border-radius: 18px;
            min-height: auto;
        }
        .home-nav {
            min-height: 56px;
            padding: 10px 14px;
        }
        .home-brand {
            font-size: 0.90rem;
        }
        .home-brand-mark {
            width: 30px;
            height: 30px;
            border-radius: 9px;
        }
        .homepage-visual .life-entry-grid {
            padding: 22px 18px 0;
            gap: 22px;
        }
        .homepage-visual .life-title {
            font-size: 1.95rem;
            line-height: 1.08;
        }
        .homepage-visual .life-copy {
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .home-signal-row {
            grid-template-columns: 1fr;
        }
        .homepage-visual .life-map {
            min-height: 330px;
        }
        .homepage-visual .life-core {
            width: 106px;
            height: 106px;
            font-size: 0.72rem;
        }
        .homepage-visual .life-node {
            width: 88px;
            min-height: 50px;
            font-size: 0.64rem;
            padding: 7px;
        }
        .homepage-visual .life-node.income { left: 14px; top: 72px; }
        .homepage-visual .life-node.saving { right: 14px; top: 72px; }
        .homepage-visual .life-node.risk { left: 14px; bottom: 72px; }
        .homepage-visual .life-node.assets { right: 14px; bottom: 72px; }
        .homepage-visual .life-node.goals { top: 18px; }
        .homepage-visual .life-node.diary { bottom: 18px; }
        .home-module-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin: 16px 18px 22px;
        }
        .home-module-card {
            min-height: 84px;
        }
        .home-module-card span {
            display: none;
        }
        .homepage-direct-entry {
            display: none !important;
        }
        .top-language-toggle {
            top: 70px;
            right: 12px;
        }
    }
    .app-footer {
        border-top: 1px solid rgba(148, 163, 184, 0.24);
        margin-top: 34px;
        padding: 18px 4px 26px;
        color: #cbd5e1;
        font-size: 0.86rem;
        line-height: 1.55;
    }
    .app-footer b {
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 30% 8%, rgba(34, 211, 238, 0.16), transparent 26%),
            linear-gradient(180deg, #0b1220 0%, #111827 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.22);
    }
    section[data-testid="stSidebar"] div[data-testid="stSidebarNav"],
    section[data-testid="stSidebar"] nav[data-testid="stSidebarNav"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] textarea {
        background: #ffffff !important;
        color: #0f172a !important;
        caret-color: #0f766e !important;
        border: 2px solid #22d3ee !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 18% 8%, rgba(255, 255, 255, 0.98), transparent 24%),
            radial-gradient(circle at 82% 10%, rgba(254, 240, 138, 0.42), transparent 22%),
            radial-gradient(circle at 74% 44%, rgba(125, 211, 252, 0.48), transparent 30%),
            radial-gradient(circle at 20% 72%, rgba(167, 243, 208, 0.38), transparent 28%),
            linear-gradient(90deg, rgba(14,165,233,0.075) 1px, transparent 1px),
            linear-gradient(0deg, rgba(20,184,166,0.055) 1px, transparent 1px),
            linear-gradient(135deg, #f8fcff 0%, #eaf7ff 42%, #fff8e8 100%) !important;
        background-size: auto, auto, auto, auto, 58px 58px, 58px 58px, auto !important;
        color: #102033;
    }
    .stApp::before {
        opacity: 0.42;
        background:
            linear-gradient(112deg, transparent 0%, transparent 42%, rgba(255,255,255,0.72) 48%, rgba(34,211,238,0.18) 54%, transparent 62%),
            linear-gradient(72deg, transparent 0%, transparent 60%, rgba(250,204,21,0.20) 64%, rgba(16,185,129,0.13) 69%, transparent 76%);
        animation: futureLightSweep 16s ease-in-out infinite;
    }
    .stApp::after {
        right: 2vw;
        top: 13vh;
        width: min(520px, 36vw);
        height: 280px;
        opacity: 0.26;
        background:
            radial-gradient(ellipse at 70% 80%, rgba(255,255,255,0.74), transparent 56%),
            linear-gradient(135deg, transparent 0 12%, rgba(14,165,233,0.34) 12% 13%, transparent 13% 28%, rgba(20,184,166,0.30) 28% 29%, transparent 29% 46%, rgba(250,204,21,0.30) 46% 47%, transparent 47% 100%);
        animation: futureGraphFloat 9s ease-in-out infinite;
    }
    @keyframes futureLightSweep {
        0%, 100% { transform: translateX(-10%) translateY(0); }
        50% { transform: translateX(10%) translateY(-8px); }
    }
    @keyframes futureGraphFloat {
        0%, 100% { transform: translateY(0) scale(0.98); }
        50% { transform: translateY(14px) scale(1.02); }
    }
    h1, h2, h3,
    div[data-testid="stHeadingWithActionElements"] h1 {
        color: #102033;
        text-shadow: none;
    }
    p, li, label {
        color: #334155;
    }
    .brand-header {
        border: 1px solid rgba(125, 211, 252, 0.42);
        background:
            radial-gradient(circle at 58% 12%, rgba(255, 255, 255, 0.94), transparent 22%),
            radial-gradient(circle at 50% 28%, rgba(125, 211, 252, 0.46), transparent 30%),
            radial-gradient(circle at 82% 26%, rgba(254, 240, 138, 0.38), transparent 25%),
            linear-gradient(135deg, rgba(255,255,255,0.92), rgba(224,242,254,0.84) 54%, rgba(236,253,245,0.82)) !important;
        box-shadow: 0 28px 78px rgba(14, 116, 144, 0.14);
    }
    .brand-header::after {
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(37,99,235,0.76), rgba(34,211,238,0.86), rgba(20,184,166,0.76), transparent);
        box-shadow: 0 0 26px rgba(34, 211, 238, 0.42);
    }
    .brand-icon {
        background:
            radial-gradient(circle at 34% 24%, rgba(255,255,255,0.76), transparent 26%),
            linear-gradient(135deg, rgba(56,189,248,0.92), rgba(45,212,191,0.78)) !important;
        border-color: rgba(14, 165, 233, 0.34);
        box-shadow: 0 18px 38px rgba(14, 165, 233, 0.22), inset 0 0 24px rgba(255,255,255,0.25);
    }
    .brand-name {
        color: #071631;
        text-shadow: 0 12px 32px rgba(14, 116, 144, 0.12);
    }
    .brand-name .scope-accent {
        color: #12b7d8;
        text-shadow: 0 0 32px rgba(34, 211, 238, 0.34);
    }
    .brand-subtitle {
        color: #48627e;
    }
    .brand-badge {
        color: #7c2d12;
        background:
            radial-gradient(circle at 16% 18%, rgba(255, 255, 255, 0.86), transparent 31%),
            linear-gradient(135deg, rgba(255, 247, 237, 0.92), rgba(253, 224, 171, 0.72) 46%, rgba(245, 208, 254, 0.68));
        border-color: rgba(249, 115, 22, 0.30);
        box-shadow: 0 14px 30px rgba(190, 24, 93, 0.12);
    }
    .brand-search-badge,
    .brand-search-badge:visited {
        color: #7c2d12 !important;
    }
    .brand-badge:hover {
        color: #701a75 !important;
        border-color: rgba(225, 29, 72, 0.42);
        box-shadow: 0 18px 38px rgba(190, 24, 93, 0.17);
    }
    .brand-search-icon {
        color: #ffffff;
        background:
            radial-gradient(circle at 30% 22%, rgba(255,255,255,0.82), transparent 20%),
            conic-gradient(from 205deg, #f97316, #facc15, #e11d48, #7c3aed, #f97316);
    }
    .search-return-link {
        color: #334155 !important;
        background:
            radial-gradient(circle at 18% 18%, rgba(255,255,255,0.88), transparent 30%),
            linear-gradient(135deg, rgba(255, 255, 255, 0.90), rgba(255, 247, 237, 0.78));
        border-color: rgba(249, 115, 22, 0.24);
        box-shadow: 0 12px 26px rgba(190, 24, 93, 0.10);
    }
    .search-return-link:hover {
        color: #7c2d12 !important;
        border-color: rgba(225, 29, 72, 0.36);
    }
    .st-key-circle_nav {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(125, 211, 252, 0.40);
        background:
            radial-gradient(circle at 15% 18%, rgba(255,255,255,0.94), transparent 26%),
            radial-gradient(circle at 88% 24%, rgba(254,240,138,0.28), transparent 26%),
            radial-gradient(circle at 50% 80%, rgba(167,243,208,0.28), transparent 32%),
            rgba(255, 255, 255, 0.50) !important;
        box-shadow: 0 22px 58px rgba(14, 116, 144, 0.14), inset 0 0 42px rgba(255,255,255,0.34);
        backdrop-filter: blur(14px);
    }
    .st-key-circle_nav::before {
        content: "";
        position: absolute;
        inset: 14px 5%;
        border-radius: 999px;
        pointer-events: none;
        opacity: 0.54;
        border: 2px solid rgba(125, 211, 252, 0.24);
        background:
            radial-gradient(circle at 18% 50%, rgba(14,165,233,0.18), transparent 12%),
            radial-gradient(circle at 82% 50%, rgba(250,204,21,0.16), transparent 13%);
        animation: futurePulse 7s ease-in-out infinite;
    }
    @keyframes futurePulse {
        0%, 100% { transform: scaleX(0.98); opacity: 0.38; }
        50% { transform: scaleX(1.02); opacity: 0.68; }
    }
    .st-key-circle_nav div[data-testid="stButton"] button {
        color: #102033 !important;
        border: 1px solid rgba(37, 99, 235, 0.16) !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.86), transparent 24%),
            radial-gradient(circle at 50% 56%, rgba(125,211,252,0.24), transparent 58%),
            linear-gradient(145deg, rgba(255,255,255,0.86), rgba(224,242,254,0.74)) !important;
        box-shadow: 0 18px 38px rgba(14, 116, 144, 0.13), inset 0 0 26px rgba(255,255,255,0.40) !important;
    }
    .st-key-circle_nav div[data-testid="stButton"] button:hover {
        border-color: rgba(14, 165, 233, 0.56) !important;
        box-shadow: 0 0 0 8px rgba(125, 211, 252, 0.18), 0 22px 48px rgba(14, 165, 233, 0.18) !important;
    }
    .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] {
        color: #ffffff !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.48), transparent 23%),
            linear-gradient(135deg, #60d7ff 0%, #22c7e8 42%, #34d399 100%) !important;
        border-color: rgba(14, 165, 233, 0.62) !important;
        box-shadow: 0 0 0 10px rgba(125, 211, 252, 0.22), 0 0 42px rgba(34, 211, 238, 0.38), 0 22px 46px rgba(14, 116, 144, 0.18) !important;
    }
    .st-key-circle_nav div[data-testid="stButton"] button p {
        color: inherit !important;
    }
    .life-compact-panel,
    .hero-panel {
        border: 1px solid rgba(125, 211, 252, 0.38);
        background:
            radial-gradient(circle at 16% 18%, rgba(255,255,255,0.92), transparent 26%),
            radial-gradient(circle at 88% 18%, rgba(254,240,138,0.26), transparent 24%),
            linear-gradient(135deg, rgba(255,255,255,0.78), rgba(224,242,254,0.68) 58%, rgba(236,253,245,0.72)) !important;
        box-shadow: 0 24px 64px rgba(14, 116, 144, 0.12);
        backdrop-filter: blur(12px);
    }
    .life-compact-panel h1,
    .hero-panel h1,
    .hero-panel h2,
    .hero-panel h3 {
        color: #102033 !important;
    }
    .life-compact-panel p,
    .hero-muted {
        color: #334155 !important;
    }
    .life-compact-card {
        background: rgba(255, 255, 255, 0.72);
        border-color: rgba(14, 165, 233, 0.18);
        box-shadow: 0 14px 30px rgba(14, 116, 144, 0.08);
    }
    .life-compact-card b {
        color: #0e7490;
    }
    .life-compact-card span {
        color: #475569;
    }
    .metric-card,
    div[data-testid="stMetric"],
    div[data-testid="stDataFrame"] {
        box-shadow: 0 14px 34px rgba(14, 116, 144, 0.08);
    }
    .app-footer {
        color: #475569;
        border-top-color: rgba(14, 165, 233, 0.18);
    }
    .app-footer b {
        color: #102033;
    }
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 28% 7%, rgba(125, 211, 252, 0.30), transparent 28%),
            radial-gradient(circle at 72% 38%, rgba(254, 240, 138, 0.18), transparent 26%),
            linear-gradient(180deg, rgba(248,252,255,0.96), rgba(224,242,254,0.92) 52%, rgba(236,253,245,0.90)) !important;
        border-right: 1px solid rgba(14, 165, 233, 0.22);
        box-shadow: 18px 0 40px rgba(14, 116, 144, 0.10);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #102033 !important;
    }
    section[data-testid="stSidebar"] code {
        color: #047857 !important;
        background: rgba(255,255,255,0.72) !important;
    }
    .stTextInput input,
    .stNumberInput input,
    textarea {
        background: #ffffff !important;
        color: #102033 !important;
        border-color: rgba(14, 165, 233, 0.38) !important;
        box-shadow: 0 10px 24px rgba(14, 116, 144, 0.08) !important;
    }
    .stTextInput input::placeholder,
    textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    div[data-testid="stButton"] button:not([kind="primary"]),
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stDownloadButton"] button {
        color: #ffffff !important;
        background:
            radial-gradient(circle at 30% 20%, rgba(255,255,255,0.16), transparent 24%),
            linear-gradient(135deg, #1f2937 0%, #111827 58%, #0f172a 100%) !important;
        border-color: rgba(226, 232, 240, 0.32) !important;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.18), inset 0 0 18px rgba(255,255,255,0.05) !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.24);
    }
    div[data-testid="stButton"] button:not([kind="primary"]) *,
    div[data-testid="stFormSubmitButton"] button *,
    div[data-testid="stDownloadButton"] button * {
        color: #ffffff !important;
    }
    div[data-testid="stButton"] button:not([kind="primary"]):hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        color: #ffffff !important;
        border-color: rgba(125, 211, 252, 0.64) !important;
        background:
            radial-gradient(circle at 30% 20%, rgba(255,255,255,0.20), transparent 24%),
            linear-gradient(135deg, #273449 0%, #172033 56%, #111827 100%) !important;
        box-shadow: 0 18px 36px rgba(14, 116, 144, 0.16), inset 0 0 22px rgba(125,211,252,0.06) !important;
    }
    .st-key-circle_nav div[data-testid="stButton"] button:not([kind="primary"]) {
        color: #102033 !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.86), transparent 24%),
            radial-gradient(circle at 50% 56%, rgba(125,211,252,0.24), transparent 58%),
            linear-gradient(145deg, rgba(255,255,255,0.86), rgba(224,242,254,0.74)) !important;
        border-color: rgba(37, 99, 235, 0.16) !important;
        text-shadow: none;
    }
    .st-key-circle_nav div[data-testid="stButton"] button:not([kind="primary"]) * {
        color: #102033 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    html body .stApp div[data-testid="stButton"] button,
    html body .stApp div[data-testid="stFormSubmitButton"] button,
    html body .stApp div[data-testid="stDownloadButton"] button {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    html body .stApp div[data-testid="stButton"] button p,
    html body .stApp div[data-testid="stButton"] button span,
    html body .stApp div[data-testid="stButton"] button div,
    html body .stApp div[data-testid="stFormSubmitButton"] button p,
    html body .stApp div[data-testid="stFormSubmitButton"] button span,
    html body .stApp div[data-testid="stFormSubmitButton"] button div,
    html body .stApp div[data-testid="stDownloadButton"] button p,
    html body .stApp div[data-testid="stDownloadButton"] button span,
    html body .stApp div[data-testid="stDownloadButton"] button div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    html body .stApp div[data-testid="stButton"] button:disabled,
    html body .stApp div[data-testid="stFormSubmitButton"] button:disabled,
    html body .stApp div[data-testid="stDownloadButton"] button:disabled {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 0.92 !important;
    }
    html body .stApp div[data-testid="stButton"] button:disabled p,
    html body .stApp div[data-testid="stButton"] button:disabled span,
    html body .stApp div[data-testid="stButton"] button:disabled div,
    html body .stApp div[data-testid="stFormSubmitButton"] button:disabled p,
    html body .stApp div[data-testid="stFormSubmitButton"] button:disabled span,
    html body .stApp div[data-testid="stFormSubmitButton"] button:disabled div,
    html body .stApp div[data-testid="stDownloadButton"] button:disabled p,
    html body .stApp div[data-testid="stDownloadButton"] button:disabled span,
    html body .stApp div[data-testid="stDownloadButton"] button:disabled div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button p,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button span,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button div {
        color: #102033 !important;
        -webkit-text-fill-color: #102033 !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"],
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] p,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] span,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    html body .stApp .nav-flow-strip {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 10px;
        width: min(1180px, 94%);
        margin: 4px auto 16px;
        padding: 10px;
        border: 1px solid rgba(14, 165, 233, 0.20);
        border-radius: 18px;
        background:
            linear-gradient(90deg, rgba(240, 249, 255, 0.92), rgba(255, 251, 235, 0.72)),
            rgba(255, 255, 255, 0.82);
        box-shadow:
            0 16px 36px rgba(14, 165, 233, 0.10),
            inset 0 0 0 1px rgba(255,255,255,0.70);
    }
    html body .stApp .nav-flow-step {
        display: flex;
        align-items: center;
        gap: 10px;
        min-height: 48px;
        padding: 9px 11px;
        border-radius: 14px;
        color: #0f172a;
        background: rgba(255, 255, 255, 0.68);
        border: 1px solid rgba(148, 163, 184, 0.20);
    }
    html body .stApp .nav-flow-step strong {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        flex: 0 0 30px;
        border-radius: 999px;
        color: #ffffff;
        font-size: 0.78rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0ea5e9, #14b8a6);
        box-shadow: 0 8px 18px rgba(14, 165, 233, 0.20);
    }
    html body .stApp .nav-flow-step span {
        display: block;
        color: #0f172a;
        font-size: 0.92rem;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: 0;
    }
    html body .stApp .nav-flow-step small {
        display: block;
        margin-top: 2px;
        color: #475569;
        font-size: 0.72rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: 0;
    }
    html body .stApp .nav-flow-step.scenario strong {
        background: linear-gradient(135deg, #f97316, #ef4444);
        box-shadow: 0 8px 18px rgba(249, 115, 22, 0.20);
    }
    html body .stApp .nav-flow-step.ai strong {
        background: linear-gradient(135deg, #06b6d4, #8b5cf6);
        box-shadow: 0 8px 18px rgba(6, 182, 212, 0.20);
    }
    html body .stApp .st-key-mobile_nav {
        display: none !important;
    }
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button {
        min-height: 46px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(14, 165, 233, 0.24) !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        background:
            radial-gradient(circle at 18% 18%, rgba(255,255,255,0.96), transparent 30%),
            linear-gradient(135deg, rgba(240,249,255,0.94), rgba(236,253,245,0.86)) !important;
        box-shadow: 0 10px 26px rgba(14, 165, 233, 0.10) !important;
        font-weight: 900 !important;
    }
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button[kind="primary"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
        border-color: rgba(255,255,255,0.54) !important;
    }
    html body .stApp .desktop-orbit-nav {
        width: min(540px, 92vw);
        margin: 6px auto 20px;
    }
    html body .stApp .desktop-orbit-shell {
        position: relative;
        width: min(500px, 90vw);
        aspect-ratio: 1 / 1;
        margin: 0 auto;
        border-radius: 50%;
        border: 0;
        background: transparent;
        box-shadow: none;
        overflow: visible;
    }
    html body .stApp .desktop-orbit-shell::before {
        content: "";
        position: absolute;
        z-index: 0;
        inset: 55px;
        border-radius: 50%;
        border: 1.5px dashed rgba(14, 165, 233, 0.30);
        background: transparent;
        opacity: 0.82;
    }
    html body .stApp .desktop-orbit-shell::after {
        content: "";
        position: absolute;
        z-index: 1;
        left: calc(50% - 5.5px);
        top: 49.5px;
        width: 11px;
        height: 11px;
        border-radius: 50%;
        background:
            radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(125,211,252,0.94) 42%, rgba(20,184,166,0.12) 70%, transparent 100%);
        box-shadow:
            0 0 12px rgba(14,165,233,0.58),
            0 0 24px rgba(20,184,166,0.34);
        pointer-events: none;
        transform-origin: 5.5px 200.5px;
        animation: desktopOrbitSpin 12s linear infinite;
    }
    html body .stApp .desktop-orbit-center,
    html body .stApp .desktop-orbit-item {
        position: absolute;
        z-index: 3;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 4px;
        text-align: center;
        text-decoration: none;
        border-radius: 50%;
        color: #0f172a;
        -webkit-text-fill-color: #0f172a;
        letter-spacing: 0;
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }
    html body .stApp .desktop-orbit-center {
        left: 50%;
        top: 50%;
        width: 110px;
        height: 110px;
        transform: translate(-50%, -50%);
        border: 2px solid rgba(20, 184, 166, 0.40);
        background:
            radial-gradient(circle at 28% 20%, rgba(255,255,255,0.52), transparent 34%),
            linear-gradient(135deg, rgba(14,165,233,0.96), rgba(20,184,166,0.88));
        color: #ffffff;
        -webkit-text-fill-color: #ffffff;
        box-shadow:
            0 18px 38px rgba(14, 165, 233, 0.22),
            0 0 0 12px rgba(20, 184, 166, 0.10);
    }
    html body .stApp .desktop-orbit-center b {
        font-size: 1.04rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .desktop-orbit-center span {
        max-width: 82px;
        font-size: 0.64rem;
        line-height: 1.1;
        font-weight: 850;
        text-transform: uppercase;
    }
    html body .stApp .desktop-orbit-item {
        left: var(--x);
        top: var(--y);
        width: 74px;
        height: 74px;
        transform: translate(-50%, -50%);
        border: 1px solid rgba(var(--accent-rgb), 0.34);
        background:
            radial-gradient(circle at 28% 22%, rgba(255,255,255,0.98), transparent 34%),
            linear-gradient(135deg, rgba(255,255,255,0.94), rgba(var(--accent-rgb), 0.14));
        box-shadow:
            0 14px 28px rgba(var(--accent-rgb), 0.14),
            inset 0 0 0 1px rgba(255,255,255,0.72);
    }
    html body .stApp .desktop-orbit-item b {
        color: var(--accent);
        -webkit-text-fill-color: var(--accent);
        font-size: 0.94rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .desktop-orbit-item span {
        max-width: 62px;
        color: #0f172a;
        -webkit-text-fill-color: #0f172a;
        font-size: 0.56rem;
        line-height: 1.05;
        font-weight: 900;
    }
    html body .stApp .desktop-orbit-item:hover {
        transform: translate(-50%, -50%) scale(1.055);
        border-color: rgba(var(--accent-rgb), 0.58);
        box-shadow:
            0 18px 34px rgba(var(--accent-rgb), 0.20),
            0 0 0 7px rgba(var(--accent-rgb), 0.08);
    }
    html body .stApp .desktop-orbit-item.active,
    html body .stApp .desktop-orbit-center.active {
        border-color: rgba(255,255,255,0.78);
        background: linear-gradient(135deg, var(--accent), #14b8a6);
        color: #ffffff;
        -webkit-text-fill-color: #ffffff;
        box-shadow:
            0 18px 36px rgba(var(--accent-rgb), 0.28),
            0 0 0 9px rgba(var(--accent-rgb), 0.12);
    }
    html body .stApp .desktop-orbit-item.active b,
    html body .stApp .desktop-orbit-item.active span {
        color: #ffffff;
        -webkit-text-fill-color: #ffffff;
    }
    @keyframes desktopOrbitSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    html body .stApp .ai-coach-hero {
        width: min(1120px, 100%);
        margin: 0 auto 18px;
        padding: 22px 24px;
        border-radius: 24px;
        border: 1px solid rgba(14, 165, 233, 0.24);
        background:
            radial-gradient(circle at 14% 18%, rgba(34,211,238,0.20), transparent 28%),
            radial-gradient(circle at 88% 16%, rgba(139,92,246,0.16), transparent 26%),
            linear-gradient(135deg, rgba(255,255,255,0.94), rgba(240,249,255,0.82));
        box-shadow: 0 22px 48px rgba(14, 165, 233, 0.12);
    }
    html body .stApp .ai-coach-hero h1 {
        margin: 0 0 8px;
        color: #0f172a;
        font-size: 2rem;
        font-weight: 950;
        letter-spacing: 0;
    }
    html body .stApp .ai-coach-hero p {
        margin: 0;
        max-width: 760px;
        color: #334155;
        font-weight: 750;
        line-height: 1.45;
    }
    html body .stApp .ai-coach-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 16px 0 0;
    }
    html body .stApp .ai-coach-signal {
        padding: 10px 12px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(255,255,255,0.72);
    }
    html body .stApp .ai-coach-signal b {
        display: block;
        color: #0f172a;
        font-size: 0.9rem;
        line-height: 1.05;
    }
    html body .stApp .ai-coach-signal span {
        display: block;
        margin-top: 4px;
        color: #475569;
        font-size: 0.78rem;
        line-height: 1.15;
        font-weight: 750;
    }
    html body .stApp .coach-disclaimer {
        padding: 12px 14px;
        border-radius: 16px;
        color: #334155;
        background: rgba(255, 251, 235, 0.86);
        border: 1px solid rgba(245, 158, 11, 0.24);
        font-weight: 760;
    }
    html body .stApp .linked-coach-card {
        min-height: 170px;
        margin: 0 0 10px;
        padding: 15px 16px;
        border-radius: 18px;
        border: 1px solid rgba(14, 165, 233, 0.20);
        background:
            radial-gradient(circle at 16% 18%, rgba(34,211,238,0.16), transparent 32%),
            linear-gradient(135deg, rgba(255,255,255,0.94), rgba(241,245,249,0.86));
        box-shadow: 0 16px 34px rgba(14, 165, 233, 0.10);
    }
    html body .stApp .linked-coach-card .eyebrow {
        color: #0f766e;
        font-size: 0.72rem;
        font-weight: 950;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }
    html body .stApp .linked-coach-card h3 {
        color: #0f172a;
        font-size: 1.02rem;
        margin: 0 0 6px;
        letter-spacing: 0;
    }
    html body .stApp .linked-coach-card .status {
        color: #0369a1;
        font-weight: 900;
        margin-bottom: 8px;
        line-height: 1.25;
    }
    html body .stApp .linked-coach-card p {
        color: #334155;
        font-size: 0.9rem;
        font-weight: 720;
        line-height: 1.38;
        margin: 0;
    }
    html body .stApp .st-key-circle_nav {
        padding: 30px 30px 28px !important;
    }
    html body .stApp .st-key-circle_nav .st-key-nav_life,
    html body .stApp .st-key-circle_nav .st-key-nav_search,
    html body .stApp .st-key-circle_nav .st-key-nav_compare,
    html body .stApp .st-key-circle_nav .st-key-nav_portfolio,
    html body .stApp .st-key-circle_nav .st-key-nav_reit,
    html body .stApp .st-key-circle_nav .st-key-nav_finance,
    html body .stApp .st-key-circle_nav .st-key-nav_scenario,
    html body .stApp .st-key-circle_nav .st-key-nav_details,
    html body .stApp .st-key-circle_nav .st-key-nav_ai,
    html body .stApp .st-key-circle_nav .st-key-nav_diary,
    html body .stApp .st-key-circle_nav .st-key-nav_settings,
    html body .stApp .st-key-circle_nav .st-key-nav_guide {
        --sig-a: rgba(14, 165, 233, 0.34);
        --sig-b: rgba(45, 212, 191, 0.28);
        --sig-c: rgba(255, 255, 255, 0.92);
        --sig-line: rgba(14, 165, 233, 0.38);
        --sig-shadow: rgba(14, 165, 233, 0.18);
        --sig-symbol:
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.72), transparent 13%),
            radial-gradient(circle at 50% 50%, rgba(14,165,233,0.30), transparent 36%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_life {
        --sig-a: rgba(45, 212, 191, 0.48);
        --sig-b: rgba(125, 211, 252, 0.40);
        --sig-line: rgba(20, 184, 166, 0.46);
        --sig-shadow: rgba(45, 212, 191, 0.24);
        --sig-symbol:
            radial-gradient(circle at 50% 62%, rgba(255,255,255,0.84), transparent 12%),
            radial-gradient(circle at 50% 62%, rgba(45,212,191,0.48), transparent 27%),
            linear-gradient(90deg, transparent 0 43%, rgba(20,184,166,0.54) 43% 57%, transparent 57% 100%),
            linear-gradient(0deg, transparent 0 43%, rgba(14,165,233,0.36) 43% 57%, transparent 57% 100%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_search {
        --sig-a: rgba(59, 130, 246, 0.44);
        --sig-b: rgba(14, 165, 233, 0.34);
        --sig-line: rgba(59, 130, 246, 0.50);
        --sig-shadow: rgba(59, 130, 246, 0.22);
        --sig-symbol:
            radial-gradient(circle at 45% 45%, transparent 0 23%, rgba(37,99,235,0.54) 24% 30%, transparent 31%),
            linear-gradient(135deg, transparent 0 58%, rgba(37,99,235,0.54) 59% 65%, transparent 66%),
            linear-gradient(0deg, transparent 0 46%, rgba(14,165,233,0.26) 47% 53%, transparent 54% 100%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_compare {
        --sig-a: rgba(168, 85, 247, 0.36);
        --sig-b: rgba(96, 165, 250, 0.28);
        --sig-line: rgba(124, 58, 237, 0.44);
        --sig-shadow: rgba(124, 58, 237, 0.18);
        --sig-symbol:
            linear-gradient(90deg, transparent 0 18%, rgba(124,58,237,0.50) 19% 24%, transparent 25% 75%, rgba(96,165,250,0.52) 76% 81%, transparent 82%),
            linear-gradient(0deg, transparent 0 38%, rgba(124,58,237,0.40) 39% 44%, transparent 45% 56%, rgba(96,165,250,0.40) 57% 62%, transparent 63%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_portfolio {
        --sig-a: rgba(34, 197, 94, 0.36);
        --sig-b: rgba(250, 204, 21, 0.34);
        --sig-line: rgba(34, 197, 94, 0.46);
        --sig-shadow: rgba(34, 197, 94, 0.18);
        --sig-symbol:
            conic-gradient(from 20deg, rgba(34,197,94,0.58) 0 34%, rgba(59,130,246,0.52) 34% 62%, rgba(250,204,21,0.54) 62% 82%, rgba(45,212,191,0.44) 82% 100%),
            radial-gradient(circle, rgba(255,255,255,0.90) 0 30%, transparent 31%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_reit {
        --sig-a: rgba(251, 191, 36, 0.42);
        --sig-b: rgba(20, 184, 166, 0.28);
        --sig-line: rgba(217, 119, 6, 0.42);
        --sig-shadow: rgba(251, 191, 36, 0.18);
        --sig-symbol:
            linear-gradient(90deg, transparent 0 16%, rgba(217,119,6,0.50) 17% 31%, transparent 32% 39%, rgba(20,184,166,0.42) 40% 58%, transparent 59% 66%, rgba(251,191,36,0.54) 67% 83%, transparent 84%),
            repeating-linear-gradient(0deg, transparent 0 12px, rgba(255,255,255,0.54) 13px 15px);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_finance {
        --sig-a: rgba(16, 185, 129, 0.42);
        --sig-b: rgba(59, 130, 246, 0.28);
        --sig-line: rgba(5, 150, 105, 0.50);
        --sig-shadow: rgba(16, 185, 129, 0.20);
        --sig-symbol:
            radial-gradient(circle at 26% 62%, rgba(16,185,129,0.56), transparent 8%),
            radial-gradient(circle at 48% 42%, rgba(59,130,246,0.48), transparent 8%),
            radial-gradient(circle at 72% 34%, rgba(34,197,94,0.54), transparent 8%),
            linear-gradient(135deg, transparent 0 45%, rgba(5,150,105,0.50) 46% 52%, transparent 53% 100%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_scenario {
        --sig-a: rgba(245, 158, 11, 0.46);
        --sig-b: rgba(239, 68, 68, 0.24);
        --sig-line: rgba(217, 119, 6, 0.48);
        --sig-shadow: rgba(245, 158, 11, 0.22);
        --sig-symbol:
            linear-gradient(115deg, transparent 0 36%, rgba(217,119,6,0.56) 37% 43%, transparent 44%),
            linear-gradient(65deg, transparent 0 50%, rgba(239,68,68,0.38) 51% 57%, transparent 58%),
            radial-gradient(circle at 30% 68%, rgba(245,158,11,0.58), transparent 9%),
            radial-gradient(circle at 70% 30%, rgba(239,68,68,0.46), transparent 9%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_details {
        --sig-a: rgba(14, 165, 233, 0.36);
        --sig-b: rgba(99, 102, 241, 0.26);
        --sig-line: rgba(2, 132, 199, 0.44);
        --sig-shadow: rgba(14, 165, 233, 0.17);
        --sig-symbol:
            radial-gradient(circle at 30% 30%, rgba(2,132,199,0.58) 0 5%, transparent 6%),
            radial-gradient(circle at 70% 30%, rgba(99,102,241,0.48) 0 5%, transparent 6%),
            radial-gradient(circle at 30% 70%, rgba(45,212,191,0.48) 0 5%, transparent 6%),
            radial-gradient(circle at 70% 70%, rgba(14,165,233,0.58) 0 5%, transparent 6%),
            linear-gradient(90deg, transparent 0 48%, rgba(2,132,199,0.35) 49% 51%, transparent 52%),
            linear-gradient(0deg, transparent 0 48%, rgba(2,132,199,0.35) 49% 51%, transparent 52%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_ai {
        --sig-a: rgba(34, 211, 238, 0.44);
        --sig-b: rgba(168, 85, 247, 0.28);
        --sig-line: rgba(8, 145, 178, 0.48);
        --sig-shadow: rgba(34, 211, 238, 0.24);
        --sig-symbol:
            radial-gradient(circle at 50% 50%, rgba(34,211,238,0.58) 0 8%, transparent 9%),
            radial-gradient(circle at 28% 28%, rgba(168,85,247,0.48) 0 5%, transparent 6%),
            radial-gradient(circle at 72% 28%, rgba(14,165,233,0.48) 0 5%, transparent 6%),
            radial-gradient(circle at 28% 72%, rgba(45,212,191,0.48) 0 5%, transparent 6%),
            radial-gradient(circle at 72% 72%, rgba(99,102,241,0.48) 0 5%, transparent 6%),
            linear-gradient(90deg, transparent 0 47%, rgba(8,145,178,0.36) 48% 52%, transparent 53%),
            linear-gradient(0deg, transparent 0 47%, rgba(8,145,178,0.36) 48% 52%, transparent 53%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_diary {
        --sig-a: rgba(244, 114, 182, 0.34);
        --sig-b: rgba(251, 191, 36, 0.26);
        --sig-line: rgba(219, 39, 119, 0.40);
        --sig-shadow: rgba(244, 114, 182, 0.18);
        --sig-symbol:
            linear-gradient(135deg, transparent 0 36%, rgba(219,39,119,0.48) 37% 43%, transparent 44%),
            linear-gradient(90deg, transparent 0 24%, rgba(251,191,36,0.28) 25% 76%, transparent 77%),
            repeating-linear-gradient(0deg, transparent 0 12px, rgba(219,39,119,0.22) 13px 15px);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_settings {
        --sig-a: rgba(100, 116, 139, 0.34);
        --sig-b: rgba(14, 165, 233, 0.22);
        --sig-line: rgba(71, 85, 105, 0.46);
        --sig-shadow: rgba(71, 85, 105, 0.18);
        --sig-symbol:
            repeating-conic-gradient(from 0deg, rgba(71,85,105,0.52) 0 10deg, transparent 10deg 24deg),
            radial-gradient(circle, rgba(255,255,255,0.94) 0 28%, transparent 29% 100%);
    }
    html body .stApp .st-key-circle_nav .st-key-nav_guide {
        --sig-a: rgba(250, 204, 21, 0.42);
        --sig-b: rgba(59, 130, 246, 0.28);
        --sig-line: rgba(202, 138, 4, 0.42);
        --sig-shadow: rgba(250, 204, 21, 0.18);
        --sig-symbol:
            conic-gradient(from 45deg, transparent 0 12%, rgba(202,138,4,0.54) 12% 18%, transparent 18% 62%, rgba(59,130,246,0.46) 62% 68%, transparent 68%),
            radial-gradient(circle, rgba(255,255,255,0.88) 0 12%, transparent 13% 100%),
            linear-gradient(90deg, transparent 0 48%, rgba(202,138,4,0.34) 49% 51%, transparent 52%),
            linear-gradient(0deg, transparent 0 48%, rgba(202,138,4,0.34) 49% 51%, transparent 52%);
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button {
        position: relative !important;
        isolation: isolate;
        overflow: hidden !important;
        width: min(136px, 100%) !important;
        height: auto !important;
        min-height: 0 !important;
        aspect-ratio: 1 / 1 !important;
        max-width: 136px;
        margin: 0 auto !important;
        border-radius: 999px !important;
        border: 1px solid rgba(59, 130, 246, 0.18) !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        background:
            radial-gradient(circle at 30% 22%, rgba(255,255,255,0.96), transparent 23%),
            radial-gradient(circle at 72% 78%, var(--sig-a), transparent 42%),
            conic-gradient(from 130deg, var(--sig-a), rgba(255,255,255,0.92), var(--sig-b), rgba(255,255,255,0.88), var(--sig-a)),
            linear-gradient(145deg, rgba(255,255,255,0.94), rgba(224,242,254,0.80)) !important;
        box-shadow:
            0 20px 42px var(--sig-shadow),
            inset 0 0 0 1px rgba(255,255,255,0.62),
            inset 0 0 34px rgba(255,255,255,0.34) !important;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button::before {
        content: "";
        position: absolute;
        inset: 10px;
        z-index: 0;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0.84;
        background:
            radial-gradient(circle at 30% 24%, rgba(255,255,255,0.78), transparent 16%),
            var(--sig-symbol);
        filter: saturate(1.08);
        animation: signatureBreath 5.5s ease-in-out infinite;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button::after {
        content: "";
        position: absolute;
        inset: 3px;
        z-index: 1;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0.78;
        border: 1px solid var(--sig-line);
        background:
            conic-gradient(from 0deg, transparent 0 12%, var(--sig-line) 13% 16%, transparent 17% 52%, rgba(255,255,255,0.64) 53% 56%, transparent 57% 100%);
        mask: radial-gradient(circle, transparent 0 57%, #000 58% 100%);
        -webkit-mask: radial-gradient(circle, transparent 0 57%, #000 58% 100%);
        animation: signatureOrbit 12s linear infinite;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button p,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button span,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button div {
        position: relative;
        z-index: 2;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 8px rgba(255,255,255,0.86);
        line-height: 1.08 !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button:hover {
        transform: translateY(-4px) scale(1.025);
        border-color: var(--sig-line) !important;
        box-shadow:
            0 0 0 8px rgba(255,255,255,0.42),
            0 24px 52px var(--sig-shadow),
            0 0 38px var(--sig-a),
            inset 0 0 0 1px rgba(255,255,255,0.68) !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background:
            radial-gradient(circle at 34% 22%, rgba(255,255,255,0.38), transparent 21%),
            radial-gradient(circle at 50% 56%, var(--sig-a), transparent 54%),
            conic-gradient(from 120deg, var(--sig-line), var(--sig-a), var(--sig-b), var(--sig-line)),
            linear-gradient(135deg, #2563eb, #06b6d4 52%, #10b981) !important;
        border-color: rgba(255, 255, 255, 0.56) !important;
        box-shadow:
            0 0 0 10px rgba(125, 211, 252, 0.23),
            0 0 48px var(--sig-a),
            0 24px 52px var(--sig-shadow),
            inset 0 0 34px rgba(255,255,255,0.18) !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] p,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] span,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.22);
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"]::before {
        opacity: 0.52;
        filter: saturate(1.3) brightness(1.12);
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"]::after {
        opacity: 0.95;
        border-color: rgba(255,255,255,0.74);
    }
    @keyframes signatureBreath {
        0%, 100% { transform: scale(0.94); opacity: 0.70; }
        50% { transform: scale(1.04); opacity: 0.95; }
    }
    @keyframes signatureOrbit {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @media (max-width: 920px) {
        html body .stApp .st-key-circle_nav {
            padding: 24px 18px !important;
        }
        html body .stApp .st-key-circle_nav div[data-testid="stButton"] button {
            width: min(116px, 100%) !important;
            max-width: 116px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    html body .stApp .st-key-circle_nav .st-key-nav_life {
        --nav-core: #14b8a6;
        --nav-core-2: #38bdf8;
        --nav-soft: rgba(45, 212, 191, 0.24);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M32 7c8 8 12 15 12 24 0 11-7 20-12 26-5-6-12-15-12-26 0-9 4-16 12-24Z%22 fill=%22black%22/%3E%3Cpath d=%22M18 36c8-2 20-2 28 0M32 18v30M23 26c6 3 12 3 18 0%22 fill=%22none%22 stroke=%22black%22 stroke-width=%225%22 stroke-linecap=%22round%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_search {
        --nav-core: #2563eb;
        --nav-core-2: #22d3ee;
        --nav-soft: rgba(59, 130, 246, 0.22);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Ccircle cx=%2228%22 cy=%2228%22 r=%2217%22 fill=%22none%22 stroke=%22black%22 stroke-width=%227%22/%3E%3Cpath d=%22M41 41l15 15%22 stroke=%22black%22 stroke-width=%227%22 stroke-linecap=%22round%22/%3E%3Cpath d=%22M18 28h20M28 18v20%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22 opacity=%22.65%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_compare {
        --nav-core: #7c3aed;
        --nav-core-2: #60a5fa;
        --nav-soft: rgba(124, 58, 237, 0.20);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M32 10v44M16 18h32M16 18l-9 18h18l-9-18ZM48 18l-9 18h18l-9-18ZM20 54h24%22 fill=%22none%22 stroke=%22black%22 stroke-width=%225%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_portfolio {
        --nav-core: #22c55e;
        --nav-core-2: #facc15;
        --nav-soft: rgba(34, 197, 94, 0.20);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M32 8a24 24 0 1 0 24 24H32V8Z%22 fill=%22black%22/%3E%3Cpath d=%22M38 8v18h18A24 24 0 0 0 38 8Z%22 fill=%22black%22 opacity=%22.55%22/%3E%3Cpath d=%22M18 42h20%22 stroke=%22white%22 stroke-width=%224%22 stroke-linecap=%22round%22 opacity=%22.9%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_reit {
        --nav-core: #f59e0b;
        --nav-core-2: #2dd4bf;
        --nav-soft: rgba(245, 158, 11, 0.22);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M10 56h44M16 56V20h17v36M35 56V10h15v46%22 fill=%22none%22 stroke=%22black%22 stroke-width=%226%22 stroke-linejoin=%22round%22/%3E%3Cpath d=%22M22 28h5M22 38h5M41 18h4M41 28h4M41 38h4%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_finance {
        --nav-core: #10b981;
        --nav-core-2: #3b82f6;
        --nav-soft: rgba(16, 185, 129, 0.22);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M12 22h40a6 6 0 0 1 6 6v22a6 6 0 0 1-6 6H12a6 6 0 0 1-6-6V18a6 6 0 0 1 6-6h32%22 fill=%22none%22 stroke=%22black%22 stroke-width=%226%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22/%3E%3Ccircle cx=%2248%22 cy=%2239%22 r=%224%22 fill=%22black%22/%3E%3Cpath d=%22M18 39h18%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_scenario {
        --nav-core: #f97316;
        --nav-core-2: #ef4444;
        --nav-soft: rgba(249, 115, 22, 0.22);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M10 50h44%22 stroke=%22black%22 stroke-width=%226%22 stroke-linecap=%22round%22/%3E%3Cpath d=%22M13 44l11-13 10 8 13-21 7 5%22 fill=%22none%22 stroke=%22black%22 stroke-width=%226%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22/%3E%3Ccircle cx=%2224%22 cy=%2231%22 r=%225%22 fill=%22black%22/%3E%3Ccircle cx=%2247%22 cy=%2218%22 r=%225%22 fill=%22black%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_details {
        --nav-core: #0ea5e9;
        --nav-core-2: #6366f1;
        --nav-soft: rgba(14, 165, 233, 0.20);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Crect x=%2210%22 y=%2210%22 width=%2244%22 height=%2244%22 rx=%228%22 fill=%22none%22 stroke=%22black%22 stroke-width=%226%22/%3E%3Cpath d=%22M20 24h24M20 34h10M38 34h6M20 44h24%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22/%3E%3Cpath d=%22M20 24l7 10-7 10%22 fill=%22none%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22 opacity=%22.65%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_ai {
        --nav-core: #06b6d4;
        --nav-core-2: #8b5cf6;
        --nav-soft: rgba(6, 182, 212, 0.22);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M21 20l22 24M43 20L21 44M32 14v36M14 32h36%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22 opacity=%22.72%22/%3E%3Ccircle cx=%2232%22 cy=%2232%22 r=%2210%22 fill=%22black%22/%3E%3Ccircle cx=%2215%22 cy=%2215%22 r=%226%22 fill=%22black%22/%3E%3Ccircle cx=%2249%22 cy=%2215%22 r=%226%22 fill=%22black%22/%3E%3Ccircle cx=%2215%22 cy=%2249%22 r=%226%22 fill=%22black%22/%3E%3Ccircle cx=%2249%22 cy=%2249%22 r=%226%22 fill=%22black%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_diary {
        --nav-core: #ec4899;
        --nav-core-2: #fbbf24;
        --nav-soft: rgba(236, 72, 153, 0.18);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M14 10h30a8 8 0 0 1 8 8v36H18a6 6 0 0 1-6-6V12a2 2 0 0 1 2-2Z%22 fill=%22none%22 stroke=%22black%22 stroke-width=%226%22 stroke-linejoin=%22round%22/%3E%3Cpath d=%22M24 24h16M24 34h14M24 44h9%22 stroke=%22black%22 stroke-width=%224%22 stroke-linecap=%22round%22/%3E%3Cpath d=%22M45 13v38%22 stroke=%22black%22 stroke-width=%224%22 opacity=%22.45%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_settings {
        --nav-core: #64748b;
        --nav-core-2: #38bdf8;
        --nav-soft: rgba(100, 116, 139, 0.18);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Cpath d=%22M32 8l5 8 9-1 3 9 7 5-5 8 1 9-9 3-5 7-8-5-9 1-3-9-7-5 5-8-1-9 9-3 5-7 8 5Z%22 fill=%22none%22 stroke=%22black%22 stroke-width=%225%22 stroke-linejoin=%22round%22/%3E%3Ccircle cx=%2232%22 cy=%2232%22 r=%229%22 fill=%22none%22 stroke=%22black%22 stroke-width=%225%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav .st-key-nav_guide {
        --nav-core: #facc15;
        --nav-core-2: #3b82f6;
        --nav-soft: rgba(250, 204, 21, 0.20);
        --nav-icon: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Ccircle cx=%2232%22 cy=%2232%22 r=%2224%22 fill=%22none%22 stroke=%22black%22 stroke-width=%225%22/%3E%3Cpath d=%22M41 18l-6 17-17 6 6-17 17-6Z%22 fill=%22black%22/%3E%3Ccircle cx=%2232%22 cy=%2232%22 r=%223%22 fill=%22white%22/%3E%3C/svg%3E');
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button {
        display: flex !important;
        align-items: flex-end !important;
        justify-content: center !important;
        padding: 74px 12px 22px !important;
        color: #102033 !important;
        -webkit-text-fill-color: #102033 !important;
        background:
            radial-gradient(circle at 30% 22%, rgba(255,255,255,0.98), transparent 23%),
            radial-gradient(circle at 52% 30%, color-mix(in srgb, var(--nav-core) 26%, transparent), transparent 26%),
            radial-gradient(circle at 72% 78%, var(--nav-soft), transparent 42%),
            conic-gradient(from 130deg, color-mix(in srgb, var(--nav-core) 30%, white), rgba(255,255,255,0.94), color-mix(in srgb, var(--nav-core-2) 26%, white), rgba(255,255,255,0.88), color-mix(in srgb, var(--nav-core) 30%, white)),
            linear-gradient(145deg, rgba(255,255,255,0.96), rgba(224,242,254,0.82)) !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button::before {
        content: "";
        position: absolute;
        top: 22px;
        left: 50%;
        width: 46px;
        height: 46px;
        z-index: 2;
        border-radius: 16px;
        pointer-events: none;
        opacity: 1;
        transform: translateX(-50%);
        background:
            linear-gradient(135deg, var(--nav-core), var(--nav-core-2)) !important;
        box-shadow:
            0 10px 24px color-mix(in srgb, var(--nav-core) 30%, transparent),
            0 0 0 10px rgba(255, 255, 255, 0.32);
        -webkit-mask: var(--nav-icon) center / 100% 100% no-repeat;
        mask: var(--nav-icon) center / 100% 100% no-repeat;
        filter: drop-shadow(0 2px 4px rgba(255,255,255,0.62));
        animation: navIconFloat 5.2s ease-in-out infinite;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button::after {
        border-color: color-mix(in srgb, var(--nav-core) 42%, white) !important;
        background:
            conic-gradient(from 0deg, transparent 0 12%, color-mix(in srgb, var(--nav-core) 52%, transparent) 13% 17%, transparent 18% 52%, rgba(255,255,255,0.76) 53% 57%, transparent 58% 100%) !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button p,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button span,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button div {
        color: #102033 !important;
        -webkit-text-fill-color: #102033 !important;
        font-size: 1rem !important;
        letter-spacing: 0 !important;
        line-height: 1.05 !important;
        text-shadow: 0 1px 9px rgba(255,255,255,0.92);
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background:
            radial-gradient(circle at 35% 18%, rgba(255,255,255,0.42), transparent 22%),
            radial-gradient(circle at 52% 32%, color-mix(in srgb, var(--nav-core-2) 54%, transparent), transparent 28%),
            conic-gradient(from 120deg, var(--nav-core), var(--nav-core-2), rgba(255,255,255,0.72), var(--nav-core)),
            linear-gradient(135deg, var(--nav-core), var(--nav-core-2)) !important;
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"]::before {
        opacity: 1;
        background: #0f172a !important;
        box-shadow:
            0 10px 28px rgba(15,23,42,0.20),
            0 0 0 11px rgba(255,255,255,0.28);
        filter: drop-shadow(0 2px 6px rgba(255,255,255,0.36));
        transform: translateX(-50%) scale(1.03);
    }
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] p,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] span,
    html body .stApp .st-key-circle_nav div[data-testid="stButton"] button[kind="primary"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.24);
    }
    @keyframes navIconFloat {
        0%, 100% { transform: translateX(-50%) translateY(0) scale(1); }
        50% { transform: translateX(-50%) translateY(-3px) scale(1.04); }
    }
    @media (max-width: 920px) {
        html body .stApp .nav-flow-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            width: min(720px, 94%);
        }
        html body .stApp .desktop-orbit-nav {
            width: min(462px, 94vw);
        }
        html body .stApp .desktop-orbit-shell {
            width: min(430px, 90vw);
        }
        html body .stApp .desktop-orbit-shell::before {
            inset: 47px;
        }
        html body .stApp .desktop-orbit-shell::after {
            left: calc(50% - 5px);
            top: 42px;
            width: 10px;
            height: 10px;
            transform-origin: 5px 178px;
        }
        html body .stApp .desktop-orbit-center {
            width: 96px;
            height: 96px;
        }
        html body .stApp .desktop-orbit-item {
            width: 66px;
            height: 66px;
        }
        html body .stApp .desktop-orbit-item span {
            font-size: 0.54rem;
        }
        html body .stApp .st-key-circle_nav div[data-testid="stButton"] button {
            padding: 62px 8px 18px !important;
        }
        html body .stApp .st-key-circle_nav div[data-testid="stButton"] button::before {
            width: 38px;
            height: 38px;
            top: 18px;
        }
        html body .stApp .st-key-circle_nav div[data-testid="stButton"] button p {
            font-size: 0.88rem !important;
        }
    }
    @media (max-width: 560px) {
        html body .stApp .brand-header {
            padding: 16px 12px 14px;
            margin-bottom: 8px;
            border-radius: 18px;
        }
        html body .stApp .brand-name {
            font-size: 1.78rem !important;
            line-height: 1 !important;
        }
        html body .stApp .brand-subtitle {
            font-size: 0.56rem !important;
            letter-spacing: 0 !important;
            text-align: center;
            line-height: 1.28;
        }
        html body .stApp .brand-search-badge {
            padding: 5px 9px 5px 6px;
            gap: 6px;
            font-size: 0.76rem;
        }
        html body .stApp .brand-search-icon {
            width: 31px;
            height: 31px;
            font-size: 0.66rem;
        }
        html body .stApp .nav-flow-strip {
            display: none !important;
        }
        html body .stApp .st-key-circle_nav {
            display: none !important;
        }
        html body .stApp .st-key-mobile_nav {
            display: block !important;
            width: min(360px, 94%);
            margin: 0 auto 16px;
            padding: 10px;
            border-radius: 18px;
            border: 1px solid rgba(14, 165, 233, 0.18);
            background: rgba(255,255,255,0.72);
            box-shadow: 0 14px 34px rgba(14, 165, 233, 0.10);
        }
        html body .stApp .ai-coach-hero {
            padding: 18px 16px;
            border-radius: 20px;
        }
        html body .stApp .ai-coach-hero h1 {
            font-size: 1.55rem;
        }
        html body .stApp .ai-coach-strip {
            grid-template-columns: 1fr 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    html body .stApp .mobile-only-deck {
        display: none;
    }
    html body .stApp .mobile-card-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        margin: 12px 0 16px;
    }
    html body .stApp .mobile-card,
    html body .stApp .mobile-holding-card,
    html body .stApp .mobile-diary-card {
        position: relative;
        overflow: hidden;
        border-radius: 18px;
        border: 1px solid rgba(14, 165, 233, 0.20);
        background:
            radial-gradient(circle at 16% 18%, rgba(34, 211, 238, 0.16), transparent 32%),
            linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 249, 255, 0.86));
        box-shadow: 0 14px 32px rgba(14, 165, 233, 0.10);
    }
    html body .stApp .mobile-card {
        padding: 14px;
        min-height: 98px;
    }
    html body .stApp .mobile-card .eyebrow,
    html body .stApp .mobile-holding-card .eyebrow,
    html body .stApp .mobile-diary-card .eyebrow {
        margin: 0 0 7px;
        color: #0f766e;
        font-size: 0.68rem;
        font-weight: 950;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    html body .stApp .mobile-card .value {
        color: #0f172a;
        font-size: 1.22rem;
        line-height: 1.05;
        font-weight: 950;
        overflow-wrap: anywhere;
    }
    html body .stApp .mobile-card .label,
    html body .stApp .mobile-card .hint,
    html body .stApp .mobile-holding-card .hint,
    html body .stApp .mobile-diary-card .hint {
        display: block;
        margin-top: 6px;
        color: #475569;
        font-size: 0.82rem;
        line-height: 1.28;
        font-weight: 760;
    }
    html body .stApp .mobile-focus-card {
        margin: 12px 0;
        padding: 16px;
        border-radius: 20px;
        border: 1px solid rgba(14, 165, 233, 0.22);
        background:
            radial-gradient(circle at 88% 18%, rgba(139, 92, 246, 0.13), transparent 30%),
            linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(236, 253, 245, 0.86));
        box-shadow: 0 16px 36px rgba(14, 165, 233, 0.12);
    }
    html body .stApp .mobile-focus-card h3 {
        margin: 0 0 8px;
        color: #0f172a;
        font-size: 1.05rem;
        line-height: 1.15;
        font-weight: 950;
    }
    html body .stApp .mobile-focus-card p {
        margin: 0;
        color: #334155;
        line-height: 1.38;
        font-weight: 760;
    }
    html body .stApp .mobile-holding-grid,
    html body .stApp .mobile-diary-feed {
        display: grid;
        grid-template-columns: 1fr;
        gap: 10px;
        margin: 10px 0 16px;
    }
    html body .stApp .mobile-holding-card,
    html body .stApp .mobile-diary-card {
        padding: 14px;
    }
    html body .stApp .mobile-holding-card .title,
    html body .stApp .mobile-diary-card .title {
        color: #0f172a;
        font-size: 1rem;
        line-height: 1.18;
        font-weight: 950;
        overflow-wrap: anywhere;
    }
    html body .stApp .mobile-holding-card .meta,
    html body .stApp .mobile-diary-card .meta {
        margin-top: 8px;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
    }
    html body .stApp .mobile-mini-stat {
        padding: 8px 9px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.66);
        border: 1px solid rgba(148, 163, 184, 0.18);
    }
    html body .stApp .mobile-mini-stat b {
        display: block;
        color: #0f172a;
        font-size: 0.9rem;
        line-height: 1.1;
        overflow-wrap: anywhere;
    }
    html body .stApp .mobile-mini-stat span {
        display: block;
        margin-top: 3px;
        color: #64748b;
        font-size: 0.68rem;
        line-height: 1;
        font-weight: 850;
        text-transform: uppercase;
    }
    html body .stApp .mobile-positive {
        color: #059669 !important;
    }
    html body .stApp .mobile-negative {
        color: #dc2626 !important;
    }
    html body .stApp .mobile-link-nav {
        display: none;
    }
    html body .stApp .mobile-link-nav a {
        flex: 0 0 auto;
        min-width: 82px;
        padding: 10px 12px;
        border-radius: 999px;
        border: 1px solid rgba(14, 165, 233, 0.20);
        background: rgba(255, 255, 255, 0.82);
        color: #0f172a;
        font-size: 0.78rem;
        line-height: 1;
        font-weight: 900;
        text-align: center;
        text-decoration: none;
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.08);
        white-space: nowrap;
    }
    html body .stApp .mobile-link-nav a.active {
        border-color: rgba(255, 255, 255, 0.72);
        background: linear-gradient(135deg, #0ea5e9, #14b8a6);
        color: #ffffff;
        box-shadow: 0 12px 28px rgba(14, 165, 233, 0.22);
    }
    html body .stApp .mobile-view-summary {
        margin: 10px auto 16px;
    }
    html body .stApp .mobile-view-summary .mobile-card-grid {
        margin-bottom: 0;
    }
    html body .stApp .mobile-orbit-nav {
        display: none;
    }
    html body .stApp .mobile-orbit-stamp {
        width: min(320px, 94vw);
        margin: 8px auto 0;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(20, 184, 166, 0.28);
        background: rgba(240, 253, 250, 0.88);
        color: #0f766e;
        -webkit-text-fill-color: #0f766e;
        font-size: 0.72rem;
        line-height: 1;
        font-weight: 950;
        text-align: center;
        letter-spacing: 0;
        box-shadow: 0 10px 24px rgba(20, 184, 166, 0.10);
    }
    html body .stApp .mobile-orbit-shell {
        position: relative;
        width: min(320px, 94vw);
        height: min(320px, 94vw);
        margin: 10px auto 8px;
        border-radius: 30px;
        border: 1px solid rgba(14, 165, 233, 0.20);
        background:
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.98), rgba(240,249,255,0.84) 58%, rgba(236,253,245,0.66)),
            linear-gradient(135deg, rgba(255,255,255,0.94), rgba(240,249,255,0.82));
        box-shadow: 0 18px 42px rgba(14, 165, 233, 0.12);
        overflow: hidden;
    }
    html body .stApp .mobile-orbit-shell::before {
        content: "";
        position: absolute;
        inset: 45px;
        border-radius: 50%;
        border: 1px dashed rgba(15, 118, 110, 0.26);
        background: transparent;
        opacity: 0.70;
    }
    html body .stApp .mobile-orbit-shell::after {
        content: "";
        position: absolute;
        left: calc(50% - 4px);
        top: 41px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        border: 0;
        background: #22d3ee;
        box-shadow:
            0 0 0 5px rgba(34, 211, 238, 0.14),
            0 0 18px rgba(14, 165, 233, 0.62);
        transform-origin: 4px 119px;
        animation: mobileOrbitSpin 8s linear infinite;
    }
    html body .stApp .mobile-orbit-center,
    html body .stApp .mobile-orbit-item,
    html body .stApp .mobile-orbit-mini {
        position: absolute;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        text-decoration: none;
        color: #0f172a;
        -webkit-text-fill-color: #0f172a;
        box-shadow: 0 12px 28px rgba(14, 165, 233, 0.13);
    }
    html body .stApp .mobile-orbit-center {
        left: 50%;
        top: 50%;
        width: 94px;
        height: 94px;
        transform: translate(-50%, -50%);
        flex-direction: column;
        gap: 5px;
        border-radius: 50%;
        border: 2px solid rgba(20, 184, 166, 0.36);
        background: linear-gradient(135deg, rgba(14,165,233,0.95), rgba(20,184,166,0.88));
        color: #ffffff;
        -webkit-text-fill-color: #ffffff;
    }
    html body .stApp .mobile-orbit-center b {
        font-size: 0.94rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .mobile-orbit-center span {
        max-width: 72px;
        font-size: 0.56rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    html body .stApp .mobile-orbit-item {
        width: 58px;
        height: 58px;
        flex-direction: column;
        gap: 4px;
        border-radius: 50%;
        border: 1px solid rgba(14, 165, 233, 0.24);
        background:
            radial-gradient(circle at 28% 22%, rgba(255,255,255,0.98), transparent 34%),
            linear-gradient(135deg, rgba(255,255,255,0.92), rgba(236,253,245,0.76));
    }
    html body .stApp .mobile-orbit-item b {
        font-size: 0.76rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .mobile-orbit-item span {
        max-width: 50px;
        font-size: 0.48rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: 0;
    }
    html body .stApp .mobile-orbit-item.active,
    html body .stApp .mobile-orbit-center.active,
    html body .stApp .mobile-orbit-mini.active {
        border-color: rgba(255,255,255,0.78);
        background: linear-gradient(135deg, #0ea5e9, #14b8a6);
        color: #ffffff;
        -webkit-text-fill-color: #ffffff;
        box-shadow: 0 16px 32px rgba(14, 165, 233, 0.24);
    }
    html body .stApp .mobile-orbit-top { left: calc(50% - 29px); top: 16px; }
    html body .stApp .mobile-orbit-top-right { right: 42px; top: 42px; }
    html body .stApp .mobile-orbit-right { right: 16px; top: calc(50% - 29px); }
    html body .stApp .mobile-orbit-bottom-right { right: 42px; bottom: 42px; }
    html body .stApp .mobile-orbit-bottom { left: calc(50% - 29px); bottom: 16px; }
    html body .stApp .mobile-orbit-bottom-left { left: 42px; bottom: 42px; }
    html body .stApp .mobile-orbit-left { left: 16px; top: calc(50% - 29px); }
    html body .stApp .mobile-orbit-top-left { left: 42px; top: 42px; }
    html body .stApp .mobile-orbit-mini-row {
        position: relative;
        z-index: 3;
        display: flex;
        gap: 8px;
        justify-content: center;
        width: min(230px, 86%);
        margin: -2px auto 10px;
    }
    html body .stApp .mobile-orbit-mini {
        position: relative;
        min-width: 56px;
        padding: 6px 9px;
        border-radius: 999px;
        border: 1px solid rgba(14, 165, 233, 0.20);
        background: rgba(255,255,255,0.82);
        font-size: 0.62rem;
        font-weight: 900;
    }
    @keyframes mobileOrbitSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button:not([kind="primary"]),
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button:not([kind="primary"]) p,
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button:not([kind="primary"]) span,
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button:not([kind="primary"]) div {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        text-shadow: none !important;
    }
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button[kind="primary"],
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button[kind="primary"] p,
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button[kind="primary"] span,
    html body .stApp .st-key-mobile_nav div[data-testid="stButton"] button[kind="primary"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-shadow: 0 1px 8px rgba(15, 23, 42, 0.22) !important;
    }
    html body .stApp div[data-testid="stForm"] {
        background:
            radial-gradient(circle at 18% 12%, rgba(125, 211, 252, 0.16), transparent 26%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(22, 38, 57, 0.88)) !important;
        border-color: rgba(14, 165, 233, 0.52) !important;
    }
    html body .stApp div[data-testid="stForm"] div[data-testid="stTextInput"] label,
    html body .stApp div[data-testid="stForm"] div[data-testid="stTextInput"] label *,
    html body .stApp div[data-testid="stForm"] div[data-testid="stWidgetLabel"],
    html body .stApp div[data-testid="stForm"] div[data-testid="stWidgetLabel"] *,
    html body .stApp div[data-testid="stForm"] label,
    html body .stApp div[data-testid="stForm"] label p,
    html body .stApp div[data-testid="stForm"] label span {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        opacity: 1 !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 7px rgba(0, 0, 0, 0.28) !important;
    }
    html body .stApp div[data-testid="stForm"] button[title],
    html body .stApp div[data-testid="stForm"] button[aria-label*="Help"] {
        color: #e0f2fe !important;
        -webkit-text-fill-color: #e0f2fe !important;
        opacity: 0.95 !important;
    }
    html body .stApp div[data-testid="stForm"] div[data-baseweb="input"] {
        border-color: #22d3ee !important;
        box-shadow:
            0 0 0 4px rgba(34, 211, 238, 0.18),
            0 12px 28px rgba(2, 6, 23, 0.20) !important;
    }
    @media (max-width: 680px) {
        html body .stApp .brand-header {
            padding: 16px 12px 14px !important;
            margin-bottom: 8px !important;
            border-radius: 18px !important;
        }
        html body .stApp .brand-name {
            font-size: 1.78rem !important;
            line-height: 1 !important;
        }
        html body .stApp .brand-subtitle {
            font-size: 0.56rem !important;
            line-height: 1.28 !important;
        }
        html body .stApp .desktop-orbit-nav,
        html body .stApp .nav-flow-strip {
            display: none !important;
        }
        html body .stApp .mobile-only-deck {
            display: block;
        }
        html body .stApp .mobile-link-nav {
            position: fixed;
            left: 50%;
            right: auto;
            bottom: max(10px, env(safe-area-inset-bottom));
            z-index: 50;
            display: flex !important;
            gap: 8px;
            overflow-x: auto;
            width: min(380px, 96%);
            margin: 0;
            padding: 9px;
            transform: translateX(-50%);
            border-radius: 18px;
            border: 1px solid rgba(14, 165, 233, 0.18);
            background: rgba(248, 252, 255, 0.88);
            box-shadow: 0 14px 30px rgba(14, 165, 233, 0.12);
            backdrop-filter: blur(16px);
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }
        html body .stApp .mobile-orbit-nav {
            display: block;
        }
        html body .stApp .mobile-link-nav::-webkit-scrollbar {
            display: none;
        }
        html body .stApp .block-container {
            padding-bottom: 96px;
        }
        html body .stApp .mobile-card-grid {
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        html body .stApp .mobile-view-summary {
            margin: 4px auto 8px;
        }
        html body .stApp .mobile-view-summary .mobile-focus-card {
            display: none;
        }
        html body .stApp .mobile-card {
            min-height: 66px;
            padding: 10px;
        }
        html body .stApp .mobile-card .eyebrow {
            margin-bottom: 4px;
            font-size: 0.6rem;
        }
        html body .stApp .mobile-card .value {
            font-size: 0.92rem;
        }
        html body .stApp .mobile-card .label,
        html body .stApp .mobile-card .hint {
            margin-top: 4px;
            font-size: 0.68rem;
            line-height: 1.18;
        }
        html body .stApp .mobile-orbit-stamp {
            display: none;
        }
        html body .stApp .mobile-orbit-shell {
            width: min(292px, 90vw);
            height: min(292px, 90vw);
            margin: 4px auto 6px;
            border-radius: 24px;
        }
        html body .stApp .mobile-orbit-shell::before {
            inset: 39px;
        }
        html body .stApp .mobile-orbit-shell::after {
            left: calc(50% - 4px);
            top: 35px;
            transform-origin: 4px 111px;
        }
        html body .stApp .mobile-orbit-center {
            width: 84px;
            height: 84px;
        }
        html body .stApp .mobile-orbit-item {
            width: 54px;
            height: 54px;
            gap: 3px;
        }
        html body .stApp .mobile-orbit-item b {
            font-size: 0.72rem;
        }
        html body .stApp .mobile-orbit-item span {
            max-width: 46px;
            font-size: 0.45rem;
        }
        html body .stApp .mobile-orbit-top { left: calc(50% - 27px); top: 12px; }
        html body .stApp .mobile-orbit-top-right { right: 34px; top: 34px; }
        html body .stApp .mobile-orbit-right { right: 12px; top: calc(50% - 27px); }
        html body .stApp .mobile-orbit-bottom-right { right: 34px; bottom: 34px; }
        html body .stApp .mobile-orbit-bottom { left: calc(50% - 27px); bottom: 12px; }
        html body .stApp .mobile-orbit-bottom-left { left: 34px; bottom: 34px; }
        html body .stApp .mobile-orbit-left { left: 12px; top: calc(50% - 27px); }
        html body .stApp .mobile-orbit-top-left { left: 34px; top: 34px; }
        html body .stApp .mobile-orbit-mini-row {
            margin: -1px auto 8px;
        }
        html body .stApp div[data-testid="stTabs"] div[role="tablist"] {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px !important;
            padding: 4px 0 10px !important;
            margin-bottom: 12px !important;
            border-bottom: 0 !important;
        }
        html body .stApp div[data-testid="stTabs"] button[role="tab"] {
            width: auto !important;
            height: 42px !important;
            min-width: 0 !important;
            min-height: 42px !important;
            padding: 7px 10px !important;
            border-radius: 14px !important;
            transform: none !important;
            color: #0f172a !important;
            background:
                radial-gradient(circle at 18% 16%, rgba(255,255,255,0.96), transparent 30%),
                linear-gradient(135deg, rgba(255,255,255,0.96), rgba(240,249,255,0.86)) !important;
            box-shadow: 0 10px 22px rgba(14, 165, 233, 0.10) !important;
        }
        html body .stApp div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
            box-shadow: 0 12px 28px rgba(14, 165, 233, 0.22) !important;
        }
        html body .stApp div[data-testid="stTabs"] button[role="tab"] p {
            max-width: none !important;
            font-size: 0.78rem !important;
            line-height: 1.05 !important;
            white-space: normal !important;
        }
        html body .stApp .hero-panel {
            padding: 15px 16px;
            margin: 8px 0 12px;
            border-radius: 16px;
        }
        html body .stApp .hero-panel h1 {
            font-size: 1.42rem !important;
            line-height: 1.18;
        }
        html body .stApp .hero-muted {
            font-size: 0.86rem;
            line-height: 1.35;
        }
        html body .stApp .detail-hero-title {
            font-size: 1.45rem;
            line-height: 1.14;
        }
        html body .stApp .detail-hero-meta {
            font-size: 0.84rem;
            line-height: 1.25;
        }
        html body .stApp div[data-testid="stForm"] {
            max-width: 100% !important;
            padding: 12px !important;
            border-radius: 14px !important;
        }
        html body .stApp .search-return-row {
            max-width: 100%;
            margin: -2px 0 8px;
        }
        html body .stApp .search-return-link {
            min-height: 36px;
            padding: 7px 12px;
            font-size: 0.82rem;
        }
        html body .stApp .search-return-arrow {
            width: 24px;
            height: 24px;
        }
        html body .stApp div[data-testid="stTextInput"] {
            max-width: 100% !important;
        }
        html body .stApp .metric-card {
            min-height: 78px;
            padding: 12px;
        }
        html body .stApp .metric-card .label {
            font-size: 0.76rem;
            margin-bottom: 5px;
        }
        html body .stApp .metric-card .value {
            font-size: 1.1rem;
            line-height: 1.15;
        }
        html body .stApp .stock-card-panel {
            min-height: auto;
            padding: 13px;
            border-radius: 14px;
        }
        html body .stApp .stock-card-head {
            grid-template-columns: 42px minmax(0, 1fr);
            gap: 10px;
            padding-bottom: 10px;
        }
        html body .stApp .company-logo {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            font-size: 0.84rem;
        }
        html body .stApp .company-title {
            min-height: 0;
            font-size: 1rem;
            line-height: 1.16;
        }
        html body .stApp .company-meta {
            font-size: 0.74rem;
            line-height: 1.25;
        }
        html body .stApp .stock-card-price {
            margin: 12px 0 10px;
            padding-bottom: 10px;
        }
        html body .stApp .stock-card-price .price {
            font-size: 1.35rem;
        }
        html body .stApp .mobile-holding-card .meta,
        html body .stApp .mobile-diary-card .meta {
            grid-template-columns: 1fr 1fr;
        }
    }

    /* Goal-first simplification: closer to the quieter Ver.1 console. */
    html body .stApp .homepage-visual {
        max-width: 1080px !important;
        min-height: 520px !important;
        border-radius: 16px !important;
        background: #ffffff !important;
        box-shadow: 0 14px 38px rgba(15, 23, 42, 0.10) !important;
    }
    html body .stApp .homepage-visual::before,
    html body .stApp .homepage-visual::after,
    html body .stApp .home-nav-links,
    html body .stApp .home-signal-row,
    html body .stApp .home-module-grid,
    html body .stApp .life-map,
    html body .stApp .home-cta-row,
    html body .stApp .home-proof {
        display: none !important;
    }
    html body .stApp .home-nav {
        min-height: 58px !important;
        padding: 12px 18px !important;
        background: rgba(255, 255, 255, 0.96) !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: none !important;
    }
    html body .stApp .home-goal-layout {
        display: grid;
        grid-template-columns: minmax(0, 0.82fr) minmax(360px, 1fr);
        gap: 28px;
        padding: 36px;
        align-items: center;
    }
    html body .stApp .home-goal-intro {
        min-width: 0;
    }
    html body .stApp .homepage-visual .life-kicker {
        color: #0f766e !important;
        background: #ecfdf5 !important;
        border: 1px solid rgba(15, 118, 110, 0.12) !important;
        box-shadow: none !important;
    }
    html body .stApp .homepage-visual .life-title {
        max-width: 390px !important;
        margin-top: 14px !important;
        font-size: 2.28rem !important;
        line-height: 1.08 !important;
        color: #0f172a !important;
    }
    html body .stApp .homepage-visual .life-copy {
        max-width: 360px !important;
        color: #475569 !important;
        font-size: 0.95rem !important;
        line-height: 1.45 !important;
    }
    html body .stApp .goal-compass {
        position: relative;
        width: 174px;
        height: 174px;
        margin: 28px 0 10px;
        border-radius: 50%;
        background: radial-gradient(circle, #f8fafc 0 30%, #eff6ff 31% 54%, #ffffff 55%);
        border: 1px solid rgba(148, 163, 184, 0.20);
    }
    html body .stApp .goal-compass-ring {
        position: absolute;
        inset: 22px;
        border-radius: 50%;
        border: 1px solid rgba(14, 116, 144, 0.18);
    }
    html body .stApp .goal-compass-ring.two {
        inset: 54px;
        border-color: rgba(37, 99, 235, 0.18);
    }
    html body .stApp .goal-compass-core {
        position: absolute;
        inset: 59px;
        display: grid;
        place-items: center;
        border-radius: 50%;
        color: #ffffff;
        background: #0f766e;
        font-size: 0.82rem;
        font-weight: 900;
    }
    html body .stApp .goal-compass-dot {
        position: absolute;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #0f766e;
        box-shadow: 0 8px 18px rgba(15, 118, 110, 0.22);
    }
    html body .stApp .goal-compass-dot.d1 { left: calc(50% - 8px); top: 14px; }
    html body .stApp .goal-compass-dot.d2 { right: 14px; top: calc(50% - 8px); background: #2563eb; }
    html body .stApp .goal-compass-dot.d3 { left: calc(50% - 8px); bottom: 14px; background: #d97706; }
    html body .stApp .goal-compass-dot.d4 { left: 14px; top: calc(50% - 8px); background: #7c3aed; }
    html body .stApp .goal-compass-caption {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 720;
    }
    html body .stApp .home-skip-link {
        display: inline-flex;
        margin-top: 16px;
        color: #64748b !important;
        font-size: 0.82rem;
        text-decoration: none !important;
    }
    html body .stApp .home-goal-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }
    html body .stApp .home-goal-card {
        min-height: 104px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: #ffffff;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
        overflow: hidden;
    }
    html body .stApp .home-goal-card[open] {
        border-color: color-mix(in srgb, var(--goal-color) 42%, transparent);
        box-shadow: 0 14px 28px rgba(15, 23, 42, 0.10);
    }
    html body .stApp .home-goal-card summary {
        min-height: 104px;
        display: grid;
        grid-template-columns: 38px minmax(0, 1fr);
        grid-template-areas: "num text" "num hint";
        column-gap: 12px;
        align-items: center;
        padding: 16px;
        cursor: pointer;
        list-style: none;
    }
    html body .stApp .home-goal-card summary::-webkit-details-marker {
        display: none;
    }
    html body .stApp .goal-number {
        grid-area: num;
        width: 38px;
        height: 38px;
        display: grid;
        place-items: center;
        border-radius: 9px;
        color: #ffffff;
        background: var(--goal-color);
        font-size: 0.78rem;
        font-weight: 900;
    }
    html body .stApp .goal-summary {
        grid-area: text;
        min-width: 0;
    }
    html body .stApp .goal-summary b {
        display: block;
        color: #0f172a;
        font-size: 1rem;
        line-height: 1.18;
        font-weight: 850;
    }
    html body .stApp .goal-summary i {
        display: block;
        margin-top: 4px;
        color: #64748b;
        font-size: 0.78rem;
        font-style: normal;
        font-weight: 650;
    }
    html body .stApp .home-goal-card summary em {
        grid-area: hint;
        color: #94a3b8;
        font-size: 0.70rem;
        font-style: normal;
        font-weight: 650;
    }
    html body .stApp .goal-card-detail {
        margin: 0 16px 12px;
        color: #334155;
        font-size: 0.82rem;
        line-height: 1.42;
    }
    html body .stApp .goal-start {
        display: inline-flex;
        align-items: center;
        min-height: 34px;
        margin: 0 16px 16px;
        padding: 0 12px;
        border-radius: 8px;
        color: #ffffff !important;
        background: var(--goal-color);
        font-size: 0.80rem;
        font-weight: 800;
        text-decoration: none !important;
    }
    html body .stApp .goal-strategy-strip {
        display: grid;
        grid-template-columns: 12px minmax(0, 1fr) auto;
        gap: 12px;
        align-items: center;
        margin: 8px 0 12px;
        padding: 12px 14px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        background: #ffffff;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }
    html body .stApp .brand-header {
        min-height: 58px !important;
        padding: 10px 14px !important;
        margin: 0 0 10px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 12px !important;
        border-radius: 10px !important;
        background: #ffffff !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05) !important;
    }
    html body .stApp .brand-mark {
        gap: 10px !important;
    }
    html body .stApp .brand-icon {
        width: 34px !important;
        height: 34px !important;
        border-radius: 9px !important;
    }
    html body .stApp .brand-name {
        font-size: 1.34rem !important;
        line-height: 1 !important;
        letter-spacing: 0 !important;
    }
    html body .stApp .brand-subtitle {
        display: none !important;
    }
    html body .stApp .brand-badge {
        min-height: 36px !important;
        padding: 0 10px !important;
        border-radius: 9px !important;
        box-shadow: none !important;
    }
    html body .stApp .brand-search-icon {
        width: 24px !important;
        height: 24px !important;
    }
    html body .stApp .brand-search-label {
        font-size: 0.78rem !important;
    }
    html body .stApp .goal-strategy-mark {
        width: 12px;
        height: 44px;
        border-radius: 999px;
        background: var(--goal-color);
    }
    html body .stApp .goal-strategy-main b {
        display: block;
        color: #0f172a;
        font-size: 0.96rem;
        line-height: 1.15;
    }
    html body .stApp .goal-strategy-main span {
        display: block;
        margin-top: 3px;
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 650;
    }
    html body .stApp .goal-strategy-detail summary {
        min-height: 34px;
        padding: 0 12px;
        display: inline-flex;
        align-items: center;
        border-radius: 8px;
        color: #334155;
        background: #f8fafc;
        border: 1px solid rgba(148, 163, 184, 0.22);
        font-size: 0.78rem;
        font-weight: 780;
        cursor: pointer;
        list-style: none;
    }
    html body .stApp .goal-strategy-detail summary::-webkit-details-marker {
        display: none;
    }
    html body .stApp .goal-strategy-detail p {
        max-width: 520px;
        margin: 9px 0 8px;
        color: #334155;
        font-size: 0.82rem;
        line-height: 1.42;
    }
    html body .stApp .goal-strategy-detail a {
        color: var(--goal-color) !important;
        font-size: 0.80rem;
        font-weight: 800;
        text-decoration: none !important;
    }
    html body .stApp .nora-ontology {
        margin: 8px 0 12px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        background: #ffffff !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05) !important;
    }
    html body .stApp .nora-ontology summary {
        min-height: 42px;
        padding: 0 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        color: #0f172a;
        cursor: pointer;
        list-style: none;
    }
    html body .stApp .nora-ontology summary::-webkit-details-marker {
        display: none;
    }
    html body .stApp .nora-ontology summary b {
        font-size: 0.86rem;
        font-weight: 860;
    }
    html body .stApp .nora-ontology summary span {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 700;
    }
    html body .stApp .nora-ontology-body {
        padding: 0 14px 14px;
    }
    html body .stApp .nora-ontology-caption {
        max-width: none !important;
        margin: 2px 0 10px !important;
        text-align: left !important;
        color: #64748b !important;
        font-size: 0.78rem !important;
    }
    html body .stApp .nora-path,
    html body .stApp .nora-modules {
        grid-template-columns: repeat(auto-fit, minmax(92px, 1fr)) !important;
    }
    html body .stApp .nora-node {
        min-height: 76px !important;
        padding: 10px !important;
        background: #f8fafc !important;
        color: #0f172a !important;
        border-color: rgba(148, 163, 184, 0.18) !important;
    }
    html body .stApp .nora-node strong {
        color: #0f172a !important;
        font-size: 0.78rem !important;
    }
    html body .stApp .nora-node span {
        color: #64748b !important;
        font-size: 0.68rem !important;
    }
    html body .stApp .nora-detail {
        background: #ffffff !important;
        color: #334155 !important;
        border-color: rgba(148, 163, 184, 0.22) !important;
    }
    html body .stApp .nora-module {
        min-height: 34px !important;
        color: #334155 !important;
        background: #f8fafc !important;
    }
    html body .stApp .nav-flow-strip {
        display: none !important;
    }
    html body .stApp .desktop-orbit-nav {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        min-height: 0 !important;
        margin: 8px 0 14px !important;
        padding: 0 !important;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    html body .stApp .desktop-orbit-shell {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        min-height: 0 !important;
        aspect-ratio: auto !important;
        margin: 0 !important;
        border-radius: 0 !important;
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(96px, 1fr)) !important;
        gap: 8px !important;
        padding: 0 !important;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    html body .stApp .desktop-orbit-shell::before,
    html body .stApp .desktop-orbit-shell::after {
        display: none !important;
    }
    html body .stApp .desktop-orbit-center,
    html body .stApp .desktop-orbit-item {
        position: static !important;
        width: auto !important;
        height: 36px !important;
        min-width: 0 !important;
        padding: 0 11px !important;
        display: inline-flex !important;
        justify-content: center !important;
        flex-direction: row !important;
        gap: 6px !important;
        border-radius: 8px !important;
        transform: none !important;
        color: #334155 !important;
        background: #ffffff !important;
        border: 1px solid rgba(148, 163, 184, 0.20) !important;
        box-shadow: none !important;
    }
    html body .stApp .desktop-orbit-center b,
    html body .stApp .desktop-orbit-item b {
        width: auto !important;
        height: auto !important;
        padding: 0 !important;
        color: inherit !important;
        background: transparent !important;
        box-shadow: none !important;
        font-size: 0.70rem !important;
    }
    html body .stApp .desktop-orbit-center span,
    html body .stApp .desktop-orbit-item span {
        color: inherit !important;
        font-size: 0.78rem !important;
        font-weight: 760 !important;
        line-height: 1 !important;
    }
    html body .stApp .desktop-orbit-item.active,
    html body .stApp .desktop-orbit-center.active {
        color: #ffffff !important;
        background: #0f766e !important;
        border-color: #0f766e !important;
    }
    html body .stApp .life-compact-panel {
        padding: 16px !important;
        border-radius: 10px !important;
        background: #ffffff !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05) !important;
    }
    html body .stApp .life-compact-panel h1 {
        font-size: 1.35rem !important;
    }
    html body .stApp .life-compact-panel p {
        max-width: none !important;
        font-size: 0.86rem !important;
    }
    html body .stApp .life-goal-board {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
    }
    html body .stApp .life-goal-link {
        min-height: 70px;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px;
        border-radius: 9px;
        color: #0f172a !important;
        background: #f8fafc;
        border: 1px solid rgba(148, 163, 184, 0.20);
        text-decoration: none !important;
    }
    html body .stApp .life-goal-link span {
        width: 32px;
        height: 32px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        color: #ffffff;
        background: var(--goal-color);
        font-size: 0.72rem;
        font-weight: 900;
    }
    html body .stApp .life-goal-link b {
        font-size: 0.86rem;
        line-height: 1.12;
    }
    @media (max-width: 900px) {
        html body .stApp .home-goal-layout {
            grid-template-columns: 1fr;
            padding: 24px;
        }
        html body .stApp .home-goal-grid {
            grid-template-columns: 1fr;
        }
        html body .stApp .goal-strategy-strip {
            grid-template-columns: 10px minmax(0, 1fr);
        }
        html body .stApp .goal-strategy-detail {
            grid-column: 2;
        }
        html body .stApp .life-goal-board {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 680px) {
        html body .stApp .homepage-visual .life-title {
            font-size: 1.78rem !important;
        }
        html body .stApp .goal-compass {
            width: 138px;
            height: 138px;
            margin-top: 20px;
        }
        html body .stApp .goal-compass-core {
            inset: 47px;
            font-size: 0.72rem;
        }
        html body .stApp .home-goal-layout {
            padding: 20px 16px;
        }
        html body .stApp .home-goal-card,
        html body .stApp .home-goal-card summary {
            min-height: 88px;
        }
        html body .stApp .top-language-toggle {
            top: 66px !important;
            right: 12px !important;
        }
        html body .stApp .life-goal-board {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_secret_or_env(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default))).strip()
    except Exception:
        return os.getenv(name, default).strip()


def get_secret_bool(name: str, default: bool = False) -> bool:
    raw_value = get_secret_or_env(name, str(default)).strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


FINNHUB_API_KEY = get_secret_or_env("FINNHUB_API_KEY")
OPENAI_API_KEY = get_secret_or_env("OPENAI_API_KEY")
OPENAI_MODEL = get_secret_or_env("OPENAI_MODEL", "gpt-5-mini")
OPENAI_REASONING_EFFORT = get_secret_or_env("OPENAI_REASONING_EFFORT", "medium")
OPENAI_AI_DEFAULT_ON = get_secret_bool("OPENAI_AI_DEFAULT_ON", False)
DEFAULT_RISK_FREE_RATE = 0.045
DEFAULT_EQUITY_RISK_PREMIUM = 0.045
RISK_FREE_RATE = DEFAULT_RISK_FREE_RATE
EQUITY_RISK_PREMIUM = DEFAULT_EQUITY_RISK_PREMIUM


GUIDE_PDF_PATH = Path(__file__).with_name("ToxiGuard-NORA_User_Guide.pdf")
GUIDE_SCREENSHOT_DIR = Path(__file__).with_name("guide_assets") / "screenshots"
HOMEPAGE_BG_PATH = Path(__file__).parent / "assets" / "homepage_life_design.png"
USE_HOMEPAGE_REFERENCE_IMAGE = False
DEVELOPER_NAME = "Young Lee"
DEVELOPER_EMAIL = "lyn0109@gmail.com"
LIFE_ENTRY_VERSION = "life-homepage-2026-05-15-v4"
MAX_DIARY_RESTORE_BYTES = 250_000
MAX_DIARY_RESTORE_ENTRIES = 50


@st.cache_data(show_spinner=False)
def image_data_uri(path_text: str) -> str:
    image_path = Path(path_text)
    if not image_path.exists():
        return ""
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


KOREAN_STOCK_MAP = {
    "삼성전자": "005930.KS",
    "samsung electronics": "005930.KS",
    "sk하이닉스": "000660.KS",
    "sk hynix": "000660.KS",
    "lg에너지솔루션": "373220.KS",
    "lg energy solution": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "samsung biologics": "207940.KS",
    "현대차": "005380.KS",
    "hyundai motor": "005380.KS",
    "기아": "000270.KS",
    "kia": "000270.KS",
    "셀트리온": "068270.KS",
    "celltrion": "068270.KS",
    "kb금융": "105560.KS",
    "kb financial": "105560.KS",
    "신한지주": "055550.KS",
    "shinhan financial": "055550.KS",
    "posco홀딩스": "005490.KS",
    "posco holdings": "005490.KS",
    "naver": "035420.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS",
    "kakao": "035720.KS",
    "삼성sdi": "006400.KS",
    "samsung sdi": "006400.KS",
    "lg화학": "051910.KS",
    "lg chem": "051910.KS",
    "현대모비스": "012330.KS",
    "hyundai mobis": "012330.KS",
    "삼성물산": "028260.KS",
    "samsung c&t": "028260.KS",
    "포스코퓨처엠": "003670.KS",
    "posco future m": "003670.KS",
    "하나금융지주": "086790.KS",
    "hana financial": "086790.KS",
    "삼성생명": "032830.KS",
    "samsung life": "032830.KS",
    "lg전자": "066570.KS",
    "lg electronics": "066570.KS",
    "sk이노베이션": "096770.KS",
    "sk innovation": "096770.KS",
    "한화에어로스페이스": "012450.KS",
    "hanwha aerospace": "012450.KS",
    "hd현대중공업": "329180.KS",
    "hd hyundai heavy industries": "329180.KS",
    "삼성화재": "000810.KS",
    "samsung fire": "000810.KS",
    "kt&g": "033780.KS",
    "케이티앤지": "033780.KS",
    "우리금융지주": "316140.KS",
    "woori financial": "316140.KS",
    "하이브": "352820.KS",
    "hybe": "352820.KS",
    "크래프톤": "259960.KS",
    "krafton": "259960.KS",
    "sk텔레콤": "017670.KS",
    "sk telecom": "017670.KS",
    "기업은행": "024110.KS",
    "ibk": "024110.KS",
    "고려아연": "010130.KS",
    "korea zinc": "010130.KS",
    "삼성전기": "009150.KS",
    "samsung electro-mechanics": "009150.KS",
    "카카오뱅크": "323410.KS",
    "kakaobank": "323410.KS",
    "카카오페이": "377300.KS",
    "kakaopay": "377300.KS",
    "삼성에스디에스": "018260.KS",
    "samsung sds": "018260.KS",
    "lg": "003550.KS",
    "한국전력": "015760.KS",
    "kepco": "015760.KS",
    "kt": "030200.KS",
    "대한항공": "003490.KS",
    "korean air": "003490.KS",
    "아모레퍼시픽": "090430.KS",
    "amorepacific": "090430.KS",
    "넷마블": "251270.KS",
    "netmarble": "251270.KS",
    "엔씨소프트": "036570.KS",
    "ncsoft": "036570.KS",
    "롯데케미칼": "011170.KS",
    "lotte chemical": "011170.KS",
    "s-oil": "010950.KS",
    "에쓰오일": "010950.KS",
    "현대건설": "000720.KS",
    "hyundai engineering construction": "000720.KS",
    "두산에너빌리티": "034020.KS",
    "doosan enerbility": "034020.KS",
    "lg생활건강": "051900.KS",
    "lg h&h": "051900.KS",
    "한미약품": "128940.KS",
    "hanmi pharm": "128940.KS",
    "유한양행": "000100.KS",
    "yuhan": "000100.KS",
    "녹십자": "006280.KS",
    "gc pharma": "006280.KS",
    "한화솔루션": "009830.KS",
    "hanwha solutions": "009830.KS",
    "현대글로비스": "086280.KS",
    "hyundai glovis": "086280.KS",
    "cj제일제당": "097950.KS",
    "cj cheiljedang": "097950.KS",
    "오리온": "271560.KS",
    "orion": "271560.KS",
    "삼양식품": "003230.KS",
    "samyang foods": "003230.KS",
    "농심": "004370.KS",
    "nongshim": "004370.KS",
    "대한전선": "001440.KS",
    "taihan cable": "001440.KS",
    "현대로템": "064350.KS",
    "hyundai rotem": "064350.KS",
    "lg이노텍": "011070.KS",
    "lg innotek": "011070.KS",
    "ls electric": "010120.KS",
    "ls일렉트릭": "010120.KS",
    "코웨이": "021240.KS",
    "coway": "021240.KS",
    "미래에셋증권": "006800.KS",
    "mirae asset securities": "006800.KS",
    "삼성증권": "016360.KS",
    "samsung securities": "016360.KS",
    "한국금융지주": "071050.KS",
    "korea investment holdings": "071050.KS",
    "메리츠금융지주": "138040.KS",
    "meritz financial": "138040.KS",
    "에코프로비엠": "247540.KQ",
    "ecopro bm": "247540.KQ",
    "에코프로": "086520.KQ",
    "ecopro": "086520.KQ",
    "알테오젠": "196170.KQ",
    "alteogen": "196170.KQ",
    "hpsp": "403870.KQ",
    "에이치피에스피": "403870.KQ",
    "레인보우로보틱스": "277810.KQ",
    "rainbow robotics": "277810.KQ",
    "리노공업": "058470.KQ",
    "leeno": "058470.KQ",
    "셀트리온제약": "068760.KQ",
    "celltrion pharm": "068760.KQ",
    "hlb": "028300.KQ",
    "에스엠": "041510.KQ",
    "sm entertainment": "041510.KQ",
    "jyp ent": "035900.KQ",
    "jyp": "035900.KQ",
    "카카오게임즈": "293490.KQ",
    "kakao games": "293490.KQ",
    "펄어비스": "263750.KQ",
    "pearl abyss": "263750.KQ",
    "스튜디오드래곤": "253450.KQ",
    "studio dragon": "253450.KQ",
    "천보": "278280.KQ",
    "chunbo": "278280.KQ",
    "동진쎄미켐": "005290.KQ",
    "dongjin semichem": "005290.KQ",
    "솔브레인": "357780.KQ",
    "soulbrain": "357780.KQ",
    "원익ips": "240810.KQ",
    "wonik ips": "240810.KQ",
    "파마리서치": "214450.KQ",
    "pharma research": "214450.KQ",
    "삼천당제약": "000250.KQ",
    "samyangdang pharm": "000250.KQ",
    "휴젤": "145020.KQ",
    "hugel": "145020.KQ",
    "메디톡스": "086900.KQ",
    "medytox": "086900.KQ",
    "클래시스": "214150.KQ",
    "classys": "214150.KQ",
    "씨젠": "096530.KQ",
    "seegene": "096530.KQ",
    "오스템임플란트": "048260.KQ",
    "osstem implant": "048260.KQ",
    "파두": "440110.KQ",
    "fadu": "440110.KQ",
    "기가비스": "420770.KQ",
    "gigavis": "420770.KQ",
    "이오테크닉스": "039030.KQ",
    "eo technics": "039030.KQ",
    "제이앤티씨": "204270.KQ",
    "jntc": "204270.KQ",
    "hd한국조선해양": "009540.KS",
    "hd korea shipbuilding": "009540.KS",
    "삼성중공업": "010140.KS",
    "samsung heavy industries": "010140.KS",
    "한화오션": "042660.KS",
    "hanwha ocean": "042660.KS",
    "hmm": "011200.KS",
    "팬오션": "028670.KS",
    "pan ocean": "028670.KS",
    "ls": "006260.KS",
    "db하이텍": "000990.KS",
    "db hitek": "000990.KS",
    "db손해보험": "005830.KS",
    "db insurance": "005830.KS",
    "현대해상": "001450.KS",
    "hyundai marine fire": "001450.KS",
    "강원랜드": "035250.KS",
    "kangwon land": "035250.KS",
}


def init_state() -> None:
    st.session_state.setdefault("app_language", query_language() or "en")
    st.session_state.setdefault("stocks", {})
    st.session_state.setdefault("compare", [])
    st.session_state.setdefault("portfolio", {})
    st.session_state.setdefault("portfolio_weighting_mode", "Share-based")
    st.session_state.setdefault("portfolio_base_currency", "USD")
    st.session_state.setdefault("portfolio_quick_input_mode", "Current value amount")
    st.session_state.setdefault("portfolio_quick_entry", "")
    st.session_state.setdefault("portfolio_stock_search_query", "")
    st.session_state.setdefault("portfolio_search_result_symbol", None)
    st.session_state.setdefault("manual_usdkrw", 1350.0)
    st.session_state.setdefault("use_live_fx", False)
    st.session_state.setdefault("risk_free_rate_pct", DEFAULT_RISK_FREE_RATE * 100)
    st.session_state.setdefault("equity_risk_premium_pct", DEFAULT_EQUITY_RISK_PREMIUM * 100)
    st.session_state.setdefault("macro_risk_free_rate_pct_text", f"{DEFAULT_RISK_FREE_RATE * 100:.2f}")
    st.session_state.setdefault("macro_equity_risk_premium_pct_text", f"{DEFAULT_EQUITY_RISK_PREMIUM * 100:.2f}")
    st.session_state.setdefault(
        "_macro_assumptions_applied",
        (DEFAULT_RISK_FREE_RATE * 100, DEFAULT_EQUITY_RISK_PREMIUM * 100),
    )
    st.session_state.setdefault("last_query", "")
    st.session_state.setdefault("selected_detail", None)
    st.session_state.setdefault("_selection_restore_errors", {})
    st.session_state.setdefault("comments", [])
    st.session_state.setdefault("financial_diary", [])
    st.session_state.setdefault("ai_coach_messages", [])
    st.session_state.setdefault("pending_ai_question", None)
    st.session_state.setdefault("last_scenario_packet", None)
    st.session_state.setdefault("use_verified_ai_model", bool(OPENAI_API_KEY) and OPENAI_AI_DEFAULT_ON)
    st.session_state.setdefault("include_diary_text_for_ai", False)
    st.session_state.setdefault("life_entry_complete", False)
    st.session_state.setdefault("life_entry_version_seen", "")


@st.cache_data(ttl=300, show_spinner=False)
def finnhub_get(path: str, **params: Any) -> Any:
    if not FINNHUB_API_KEY:
        raise RuntimeError("FINNHUB_API_KEY is not configured in Streamlit secrets.")

    params["token"] = FINNHUB_API_KEY
    response = requests.get(
        f"https://finnhub.io/api/v1/{path}",
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def fmt_money(value: float | int | None, currency: str = "USD") -> str:
    if value is None:
        return "N/A"
    if currency == "KRW":
        return f"₩{value:,.0f}"
    return f"${value:,.2f}"


def fmt_signed_money(value: float | int | None, currency: str = "USD") -> str:
    if value is None:
        return "N/A"
    sign = "+" if float(value) >= 0 else "-"
    absolute_value = abs(float(value))
    if currency == "KRW":
        return f"{sign}₩{absolute_value:,.0f}"
    return f"{sign}${absolute_value:,.2f}"


def stock_money(stock: dict[str, Any], value: float | int | None) -> str:
    return fmt_money(value, stock.get("currency", "USD"))


def fmt_number(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{digits}f}"


def fmt_market_cap(value: float | int | None, currency: str = "USD") -> str:
    if not value:
        return "N/A"
    # Finnhub profile marketCapitalization is in millions.
    if currency == "KRW":
        trillions = float(value) / 1_000_000
        return f"₩{trillions:,.2f}T"
    billions = float(value) / 1000
    return f"${billions:,.2f}B"


@st.cache_data(ttl=3600, show_spinner=False)
def load_live_usdkrw() -> dict[str, Any]:
    try:
        history = yf.download(
            "KRW=X",
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False,
        )
    except Exception:
        return {"rate": None, "date": None, "source": "Unavailable"}

    clean = normalize_price_history(history.reset_index() if not history.empty else history)
    if clean.empty:
        return {"rate": None, "date": None, "source": "Unavailable"}

    latest = clean.iloc[-1]
    return {
        "rate": float(latest["Close"]),
        "date": latest["Date"].strftime("%Y-%m-%d"),
        "source": "Yahoo Finance KRW=X",
    }


def effective_usdkrw() -> tuple[float, str, str]:
    manual_rate = float(st.session_state.get("manual_usdkrw", 1350.0) or 1350.0)
    if st.session_state.get("use_live_fx", True):
        live = load_live_usdkrw()
        if live.get("rate"):
            return float(live["rate"]), str(live.get("source") or "Yahoo Finance KRW=X"), str(live.get("date") or "Latest")
    return manual_rate, "Manual fallback", "User input"


def macro_assumptions() -> tuple[float, float]:
    risk_free_rate = float(
        st.session_state.get("risk_free_rate_pct", DEFAULT_RISK_FREE_RATE * 100)
        or DEFAULT_RISK_FREE_RATE * 100
    )
    equity_risk_premium = float(
        st.session_state.get("equity_risk_premium_pct", DEFAULT_EQUITY_RISK_PREMIUM * 100)
        or DEFAULT_EQUITY_RISK_PREMIUM * 100
    )
    return max(risk_free_rate, 0.0) / 100, max(equity_risk_premium, 0.0) / 100


def convert_value(value: float, from_currency: str, to_currency: str, usdkrw: float) -> float:
    if from_currency == to_currency:
        return value
    if from_currency == "USD" and to_currency == "KRW":
        return value * usdkrw
    if from_currency == "KRW" and to_currency == "USD":
        return value / usdkrw if usdkrw > 0 else 0.0
    return value


def normalize_company_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def is_korean_symbol(symbol: str) -> bool:
    clean = symbol.strip().upper()
    return clean.endswith(".KS") or clean.endswith(".KQ")


def resolve_korean_ticker(query: str) -> str | None:
    clean = query.strip()
    normalized = normalize_company_query(clean)
    if normalized in KOREAN_STOCK_MAP:
        return KOREAN_STOCK_MAP[normalized]

    upper = clean.upper()
    if is_korean_symbol(upper):
        return upper

    if clean.isdigit() and len(clean) == 6:
        known_symbols = set(KOREAN_STOCK_MAP.values())
        kosdaq_symbol = f"{clean}.KQ"
        kospi_symbol = f"{clean}.KS"
        if kosdaq_symbol in known_symbols:
            return kosdaq_symbol
        return kospi_symbol

    return None


def company_name_for_korean_symbol(symbol: str) -> str:
    for name, mapped_symbol in KOREAN_STOCK_MAP.items():
        if mapped_symbol == symbol and any(ord(char) > 127 for char in name):
            return name
    return symbol


def resolve_ticker(query: str) -> str:
    query = query.strip().upper()
    data = finnhub_get("search", q=query)
    results = data.get("result", [])
    if not results:
        return query

    exact = next((item for item in results if item.get("symbol") == query), None)
    common = next((item for item in results if item.get("type") == "Common Stock"), None)
    return (exact or common or results[0]).get("symbol", query)


def safe_metric(symbol: str) -> dict[str, Any]:
    try:
        data = finnhub_get("stock/metric", symbol=symbol, metric="all")
        return data.get("metric", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def average_peer_pe(symbol: str) -> tuple[float, list[str]]:
    try:
        peers = finnhub_get("stock/peers", symbol=symbol)
    except Exception:
        peers = []

    top_peers = [item for item in peers if item != symbol][:3] if isinstance(peers, list) else []
    pe_values = []
    for peer in top_peers:
        metric = safe_metric(peer)
        pe = metric.get("peExclExtraTTM") or metric.get("peBasicExclExtraTTM")
        if pe and 0 < pe < 150:
            pe_values.append(float(pe))

    return (sum(pe_values) / len(pe_values) if pe_values else 15.0), top_peers


@st.cache_data(ttl=900, show_spinner=False)
def load_price_history(symbol: str, days: int = 180) -> pd.DataFrame:
    finnhub_history = normalize_price_history(load_price_history_from_finnhub(symbol, days))
    if not finnhub_history.empty:
        return finnhub_history
    return normalize_price_history(load_price_history_from_yahoo(symbol, days))


def normalize_price_history(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty:
        return pd.DataFrame()

    history = history.copy()
    if isinstance(history.columns, pd.MultiIndex):
        history.columns = [
            "_".join(str(part) for part in col if str(part))
            for col in history.columns.to_flat_index()
        ]

    if "Date" not in history.columns:
        history = history.reset_index()

    date_col = next((col for col in history.columns if str(col).lower() in {"date", "datetime"}), None)
    close_col = next((col for col in history.columns if str(col).lower() == "close" or str(col).lower().startswith("close_")), None)

    if not date_col or not close_col:
        return pd.DataFrame()

    clean = history[[date_col, close_col]].copy()
    clean.columns = ["Date", "Close"]
    clean["Date"] = pd.to_datetime(clean["Date"], errors="coerce")
    clean["Close"] = pd.to_numeric(clean["Close"], errors="coerce")
    clean = clean.dropna(subset=["Date", "Close"])
    return clean.sort_values("Date")


def load_price_history_from_finnhub(symbol: str, days: int) -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=days)
    try:
        data = finnhub_get(
            "stock/candle",
            symbol=symbol,
            resolution="D",
            **{"from": int(start.timestamp()), "to": int(end.timestamp())},
        )
    except Exception:
        return pd.DataFrame()

    if not isinstance(data, dict) or data.get("s") != "ok":
        return pd.DataFrame()

    closes = data.get("c") or []
    timestamps = data.get("t") or []
    if not closes or not timestamps:
        return pd.DataFrame()

    return pd.DataFrame(
        {
            "Date": [datetime.fromtimestamp(ts).date() for ts in timestamps],
            "Close": closes,
        }
    )


def load_price_history_from_yahoo(symbol: str, days: int) -> pd.DataFrame:
    try:
        history = yf.download(
            symbol,
            period=f"{max(days, 30)}d",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )
    except Exception:
        return pd.DataFrame()

    if history.empty:
        return pd.DataFrame()
    return history.reset_index()


def calculate_valuation(stock: dict[str, Any]) -> dict[str, Any]:
    beta = float(stock.get("beta") or 1.0)
    eps = float(stock.get("eps") or 0)
    dividend = float(stock.get("dividend") or 0)
    growth = float(stock.get("growth_rate") or 0.05)
    book_value = float(stock.get("book_value") or 0)
    peer_pe = float(stock.get("peer_average_pe") or 15)
    price = float(stock.get("price") or 0)

    risk_free_rate, equity_risk_premium = macro_assumptions()
    expected_return = risk_free_rate + beta * equity_risk_premium
    max_implied_pe = 50
    values = []

    income_value = 0.0
    income_model = "N/A"
    if dividend > 0 and expected_return > growth:
        income_value = (dividend * (1 + growth)) / (expected_return - growth)
        income_model = "GGM"
    elif eps > 0:
        adjusted_growth = min(growth, expected_return - 0.02)
        if adjusted_growth > 0 and expected_return > adjusted_growth:
            implied_pe = (1 + adjusted_growth) / (expected_return - adjusted_growth)
        else:
            implied_pe = 1 / expected_return if expected_return > 0 else 0
        income_value = eps * min(implied_pe, max_implied_pe)
        income_model = "ECM"
    if income_value > 0:
        values.append(income_value)

    graham_value = 0.0
    if eps > 0 and book_value > 0:
        graham_value = (22.5 * book_value * eps) ** 0.5
        values.append(graham_value)

    relative_value = 0.0
    if eps > 0 and peer_pe > 0:
        relative_value = eps * peer_pe
        values.append(relative_value)

    fair_price = sum(values) / len(values) if values else 0.0
    if fair_price <= 0 or price <= 0:
        status = "Fair Value"
    else:
        diff_ratio = (price - fair_price) / fair_price
        if diff_ratio > 0.05:
            status = "Overvalued"
        elif diff_ratio < -0.05:
            status = "Undervalued"
        else:
            status = "Fair Value"

    stock.update(
        {
            "expected_return": expected_return,
            "risk_free_rate": risk_free_rate,
            "equity_risk_premium": equity_risk_premium,
            "fair_price": fair_price,
            "valuation_status": status,
            "triangulation": {
                "income_model": income_model,
                "income_value": income_value,
                "asset_value": graham_value,
                "market_value": relative_value,
                "valid_models": len(values),
            },
        }
    )
    return stock


def recalculate_loaded_stocks() -> int:
    count = 0
    for symbol, stock in list(st.session_state.get("stocks", {}).items()):
        st.session_state.stocks[symbol] = calculate_valuation(stock)
        count += 1
    return count


def load_korean_stock(query: str) -> dict[str, Any]:
    symbol = resolve_korean_ticker(query)
    if not symbol:
        raise ValueError(f"{query} is not recognized as a Korean stock.")

    ticker = yf.Ticker(symbol)
    history = load_price_history_from_yahoo(symbol, days=30)
    if history.empty:
        raise ValueError(f"No Yahoo Finance price history was returned for {symbol}.")

    history = normalize_price_history(history)
    closes = history["Close"].astype(float).tolist()
    price = closes[-1] if closes else 0.0
    if price <= 0:
        raise ValueError(f"No current price was returned for {symbol}.")

    previous = closes[-2] if len(closes) >= 2 else price
    change_pct = ((price - previous) / previous * 100) if previous else 0.0

    try:
        info = ticker.get_info()
    except Exception:
        info = {}

    market_cap = info.get("marketCap")
    market_cap_millions = float(market_cap) / 1_000_000 if market_cap else None
    trailing_eps = info.get("trailingEps") or 0
    book_value = info.get("bookValue") or 0
    dividend_rate = info.get("dividendRate") or 0
    dividend_yield = (float(info.get("dividendYield") or 0) * 100)
    pe = info.get("trailingPE") or info.get("forwardPE")
    beta = info.get("beta") or 1.0
    growth_rate = info.get("earningsGrowth")
    if growth_rate is None:
        growth_rate = info.get("revenueGrowth")
    if growth_rate is None:
        growth_rate = 0.05

    name = (
        info.get("longName")
        or info.get("shortName")
        or company_name_for_korean_symbol(symbol)
    )
    industry = info.get("industry") or info.get("sector") or "Korean Equity"
    peer_pe = pe if pe and 0 < float(pe) < 100 else 15.0

    stock = {
        "symbol": symbol,
        "name": name,
        "industry": industry,
        "price": price,
        "change_pct": change_pct,
        "market_cap": market_cap_millions,
        "pe": pe,
        "dividend_yield": dividend_yield,
        "beta": beta,
        "eps": trailing_eps,
        "dividend": dividend_rate,
        "growth_rate": growth_rate,
        "book_value": book_value,
        "peer_average_pe": peer_pe,
        "peers": [],
        "market": "Korea",
        "currency": "KRW",
    }
    return calculate_valuation(stock)


def load_stock(query: str) -> dict[str, Any]:
    korean_symbol = resolve_korean_ticker(query)
    if korean_symbol:
        return load_korean_stock(korean_symbol)

    symbol = resolve_ticker(query)
    profile = finnhub_get("stock/profile2", symbol=symbol)
    quote = finnhub_get("quote", symbol=symbol)
    metric = safe_metric(symbol)
    peer_pe, peers = average_peer_pe(symbol)

    price = float(quote.get("c") or 0)
    if price <= 0:
        raise ValueError(f"No current price was returned for {symbol}.")

    stock = {
        "symbol": symbol,
        "name": profile.get("name") or symbol,
        "industry": profile.get("finnhubIndustry") or "N/A",
        "price": price,
        "change_pct": float(quote.get("dp") or 0),
        "market_cap": profile.get("marketCapitalization"),
        "pe": metric.get("peExclExtraTTM") or metric.get("peBasicExclExtraTTM"),
        "dividend_yield": metric.get("dividendYieldIndicatedAnnual") or 0,
        "beta": metric.get("beta") or 1.0,
        "eps": metric.get("epsExclExtraItemsTTM") or metric.get("epsBasicExclExtraItemsTTM") or 0,
        "dividend": metric.get("dividendPerShareAnnual") or 0,
        "growth_rate": (metric.get("epsGrowth3Y") or 5) / 100,
        "book_value": metric.get("bookValuePerShareAnnual") or 0,
        "peer_average_pe": peer_pe,
        "peers": peers,
        "market": "US",
        "currency": "USD",
    }
    return calculate_valuation(stock)


def status_color(status: str) -> str:
    return {
        "Undervalued": "#10b981",
        "Fair Value": "#f59e0b",
        "Overvalued": "#ef4444",
    }.get(status, "#94a3b8")


def metric_card(label: str, value: str, color: str = "#102033") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{escape(str(label))}</div>
            <div class="value" style="color:{escape(str(color))};">{escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def guide_image(filename: str, caption: str) -> None:
    image_path = GUIDE_SCREENSHOT_DIR / filename
    if image_path.exists():
        st.image(str(image_path), caption=caption, width="stretch")
    else:
        st.caption(f"Guide graphic unavailable: {filename}")


def parse_symbol_query_value(value: Any) -> list[str]:
    raw_values = value if isinstance(value, list) else [value]
    symbols: list[str] = []
    for raw_value in raw_values:
        if not raw_value:
            continue
        for item in str(raw_value).replace("|", ",").split(","):
            symbol = item.strip().upper()
            if symbol and symbol not in symbols:
                symbols.append(symbol)
    return symbols


def selected_symbols_for_url() -> list[str]:
    symbols: list[str] = []
    for symbol in st.session_state.get("compare", []):
        if symbol not in symbols:
            symbols.append(symbol)
    for symbol in st.session_state.get("portfolio", {}).keys():
        if symbol not in symbols:
            symbols.append(symbol)
    selected_detail = st.session_state.get("selected_detail")
    if selected_detail and selected_detail not in symbols:
        symbols.append(selected_detail)
    return symbols


def selection_state_params() -> dict[str, str]:
    params: dict[str, str] = {}
    symbols = selected_symbols_for_url()
    compare_symbols = [
        symbol for symbol in st.session_state.get("compare", []) if symbol
    ]
    portfolio_symbols = [
        symbol for symbol in st.session_state.get("portfolio", {}).keys() if symbol
    ]
    if symbols:
        params["symbols"] = ",".join(symbols)
    if compare_symbols:
        params["compare"] = ",".join(compare_symbols)
    if portfolio_symbols:
        params["portfolio"] = ",".join(portfolio_symbols)
    return params


def sync_selection_state_to_query() -> None:
    try:
        query_params = st.query_params
        for key in ("symbols", "compare", "portfolio"):
            if key in query_params:
                del query_params[key]
        for key, value in selection_state_params().items():
            query_params[key] = value
    except Exception:
        return


def restore_stock_for_symbol(symbol: str) -> bool:
    symbol = symbol.strip().upper()
    if not symbol:
        return False
    if symbol in st.session_state.stocks:
        return True

    restore_errors = st.session_state.setdefault("_selection_restore_errors", {})
    if symbol in restore_errors:
        return False

    try:
        stock = load_stock(symbol)
        st.session_state.stocks[stock["symbol"]] = stock
        if stock["symbol"] != symbol:
            st.session_state.stocks[symbol] = stock
        return True
    except Exception as exc:
        restore_errors[symbol] = str(exc)
        return False


def sync_selection_state_from_query() -> None:
    try:
        params = st.query_params
    except Exception:
        params = st.experimental_get_query_params()

    symbols = parse_symbol_query_value(params.get("symbols"))
    compare_symbols = parse_symbol_query_value(params.get("compare"))
    portfolio_symbols = parse_symbol_query_value(params.get("portfolio"))
    detail_symbols = parse_symbol_query_value(params.get("detail"))

    for symbol in symbols + compare_symbols + portfolio_symbols + detail_symbols:
        restore_stock_for_symbol(symbol)

    compare = st.session_state.compare
    for symbol in compare_symbols:
        if symbol in st.session_state.stocks and symbol not in compare and len(compare) < 3:
            st.session_state.pop(f"sidebar_compare_{symbol}", None)
            compare.append(symbol)

    portfolio = st.session_state.portfolio
    for symbol in portfolio_symbols:
        if symbol in st.session_state.stocks and symbol not in portfolio:
            st.session_state.pop(f"sidebar_portfolio_{symbol}", None)
            portfolio[symbol] = {"shares": 1.0, "purchase_price": 0.0}


def add_compare(symbol: str) -> None:
    compare = st.session_state.compare
    st.session_state.pop(f"sidebar_compare_{symbol}", None)
    if symbol in compare:
        sync_selection_state_to_query()
        return
    if len(compare) < 3:
        compare.append(symbol)
    else:
        st.warning("You can compare up to 3 stocks at a time.")
    sync_selection_state_to_query()


def remove_compare(symbol: str) -> None:
    if symbol in st.session_state.compare:
        st.session_state.compare.remove(symbol)
    st.session_state.pop(f"sidebar_compare_{symbol}", None)
    sync_selection_state_to_query()


def add_portfolio(symbol: str) -> None:
    portfolio = st.session_state.portfolio
    st.session_state.pop(f"sidebar_portfolio_{symbol}", None)
    if symbol not in portfolio:
        portfolio[symbol] = {"shares": 1.0, "purchase_price": 0.0}
    sync_selection_state_to_query()


def remove_portfolio(symbol: str) -> None:
    if symbol in st.session_state.portfolio:
        del st.session_state.portfolio[symbol]
    st.session_state.pop(f"sidebar_portfolio_{symbol}", None)
    sync_selection_state_to_query()


def parse_portfolio_number(raw_value: str) -> float:
    cleaned = (
        raw_value.strip()
        .replace("₩", "")
        .replace("$", "")
        .replace(",", "")
        .replace("_", "")
    )
    if cleaned.lower().endswith("m"):
        return float(cleaned[:-1]) * 1_000_000
    if cleaned.lower().endswith("k"):
        return float(cleaned[:-1]) * 1_000
    return float(cleaned)


def apply_quick_portfolio_entries(raw_text: str, input_mode: str) -> tuple[int, list[str]]:
    added = 0
    errors: list[str] = []
    portfolio = st.session_state.portfolio

    for line_number, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.replace("\t", ",").split(",") if part.strip()]
        if len(parts) < 2:
            errors.append(f"Line {line_number}: enter at least ticker and value/shares.")
            continue

        query = parts[0]
        try:
            quantity_or_value = parse_portfolio_number(parts[1])
            purchase_price = (
                parse_portfolio_number(parts[2])
                if len(parts) >= 3 and parts[2].strip()
                else None
            )
            stock = load_stock(query)
            symbol = stock["symbol"]
            st.session_state.stocks[symbol] = stock
            current_price = float(stock.get("price") or 0)
            if input_mode == "Current value amount":
                if current_price <= 0:
                    errors.append(f"Line {line_number}: {symbol} has no current price.")
                    continue
                shares = quantity_or_value / current_price
            else:
                shares = quantity_or_value

            existing = portfolio.get(symbol, {})
            portfolio[symbol] = {
                "shares": max(shares, 0.0),
                "purchase_price": (
                    max(purchase_price, 0.0)
                    if purchase_price is not None
                    else float(existing.get("purchase_price") or 0)
                ),
            }
            added += 1
        except Exception as exc:
            errors.append(f"Line {line_number}: {query} could not be loaded ({exc}).")

    if added:
        sync_selection_state_to_query()
    return added, errors


def render_quick_portfolio_entry() -> None:
    with st.expander("Quick Portfolio Entry", expanded=not bool(st.session_state.portfolio)):
        st.caption(
            "Paste one holding per line: ticker, current value or shares, optional average purchase price. "
            "Current value amount should be in the stock's native currency."
        )
        mode_cols = st.columns([1, 2])
        with mode_cols[0]:
            input_mode = st.radio(
                "Quick input type",
                ["Current value amount", "Share count"],
                horizontal=False,
                key="portfolio_quick_input_mode",
            )
        with mode_cols[1]:
            st.text_area(
                "Holdings input",
                key="portfolio_quick_entry",
                height=120,
                placeholder="AAPL, 5000, 180\n005930.KS, 10000000, 72000\nMSFT, 12, 310",
            )
        button_cols = st.columns([1, 2])
        with button_cols[0]:
            if st.button("Apply Holdings", width="stretch"):
                count, errors = apply_quick_portfolio_entries(
                    st.session_state.get("portfolio_quick_entry", ""),
                    st.session_state.get("portfolio_quick_input_mode", "Current value amount"),
                )
                if count:
                    st.session_state.portfolio_quick_entry = ""
                    st.success(f"Added or updated {count} holding(s).")
                    st.rerun()
                if errors:
                    for error in errors[:5]:
                        st.warning(error)
        with button_cols[1]:
            st.caption(
                "For a KRW 200M stock portfolio, enter each position value in KRW for Korean stocks "
                "or USD for U.S. stocks. The app estimates shares from current price."
            )


def toggle_portfolio(symbol: str) -> None:
    if symbol in st.session_state.portfolio:
        remove_portfolio(symbol)
    else:
        add_portfolio(symbol)


def select_detail(symbol: str) -> None:
    st.session_state.selected_detail = symbol
    sync_selection_state_to_query()


def select_detail_and_open_search(symbol: str) -> None:
    st.session_state.selected_detail = symbol
    set_active_nav_key("search")
    sync_selection_state_to_query()


def add_compare_and_open(symbol: str) -> None:
    add_compare(symbol)
    set_active_nav_key("compare")


def add_portfolio_and_open(symbol: str) -> None:
    add_portfolio(symbol)
    set_active_nav_key("portfolio")


def sync_selected_detail_from_query() -> None:
    try:
        params = st.query_params
    except Exception:
        params = st.experimental_get_query_params()

    detail = params.get("detail")
    if isinstance(detail, list):
        detail = detail[0] if detail else None
    if detail and detail in st.session_state.stocks:
        st.session_state.selected_detail = detail


def render_stock_card(stock: dict[str, Any]) -> None:
    symbol = stock["symbol"]
    status = stock["valuation_status"]
    compare_active = symbol in st.session_state.compare
    portfolio_active = symbol in st.session_state.portfolio
    detail_href = app_detail_href(symbol)
    safe_symbol = escape(str(symbol))
    safe_industry = escape(str(stock.get("industry", "N/A")))
    safe_status = escape(str(status))
    logo_text = escape(str(symbol[:2].upper()))
    with st.container(border=True):
        st.markdown(
            f"""
            <a class="stock-card-link" href="{detail_href}" target="_self">
            <div class="stock-card-panel">
                <div class="stock-card-head">
                    <div class="company-logo">{logo_text}</div>
                    <div>
                        <div class="company-title">{escape(str(stock['name']))}</div>
                        <div class="company-meta"><span class="ticker-pill">{safe_symbol}</span>{safe_industry}</div>
                    </div>
                </div>
                <div class="stock-card-price">
                    <div>
                        <div class="price">{stock_money(stock, stock['price'])}</div>
                        <div style="color:{'#059669' if stock['change_pct'] >= 0 else '#dc2626'};font-weight:850;margin-top:7px;">{stock['change_pct']:+.2f}% today</div>
                    </div>
                    <span class="status-chip" style="background:{status_color(status)};">{safe_status}</span>
                </div>
                <div class="stock-card-stats">
                    <span>Market Cap<b>{fmt_market_cap(stock['market_cap'], stock.get('currency', 'USD'))}</b></span>
                    <span>PER<b>{fmt_number(stock['pe'])}</b></span>
                </div>
                <div class="click-hint">Click this stock card to view details and price movement.</div>
            </div>
            </a>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        c1.button(
            "Added to Compare" if compare_active else "Add to Compare",
            key=f"compare_{symbol}",
            on_click=add_compare,
            args=(symbol,),
            width="stretch",
            disabled=compare_active,
        )
        c2.button(
            "In Portfolio" if portfolio_active else "Add to Portfolio",
            key=f"portfolio_{symbol}",
            on_click=add_portfolio,
            args=(symbol,),
            width="stretch",
            disabled=portfolio_active,
        )


def render_fair_value(stock: dict[str, Any]) -> None:
    tri = stock["triangulation"]
    st.subheader(f"{stock['name']} ({stock['symbol']})")
    st.metric("Current Price", stock_money(stock, stock["price"]), f"{stock['change_pct']:+.2f}%")
    st.metric("Blended Fair Value", stock_money(stock, stock["fair_price"]) if stock["fair_price"] else "N/A")
    st.write(f"**Status:** {stock['valuation_status']}")
    st.write(f"**Required Return (CAPM):** {stock['expected_return'] * 100:.2f}%")
    st.table(
        {
            "Approach": ["Income", "Asset", "Market"],
            "Model": [tri["income_model"], "Graham Number", "Peer P/E"],
            "Value": [
                stock_money(stock, tri["income_value"]) if tri["income_value"] else "N/A",
                stock_money(stock, tri["asset_value"]) if tri["asset_value"] else "N/A",
                stock_money(stock, tri["market_value"]) if tri["market_value"] else "N/A",
            ],
        }
    )


def render_tradingview_chart(symbol: str) -> None:
    container_id = f"tradingview_{symbol.replace('.', '_').replace('-', '_')}"
    tv_symbol = f"KRX:{symbol[:6]}" if is_korean_symbol(symbol) else symbol
    tv_symbol = "".join(
        char for char in tv_symbol if char.isascii() and (char.isalnum() or char in ":._-/")
    ) or "NASDAQ:AAPL"
    st.html(
        f"""
        <div class="tradingview-widget-container" style="height:520px;width:100%;">
            <div id="{container_id}" style="height:500px;width:100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#0f172a",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "save_image": false,
                "calendar": false,
                "container_id": "{container_id}"
            }});
            </script>
        </div>
        """,
        width="stretch",
        unsafe_allow_javascript=True,
    )


def valuation_upside(stock: dict[str, Any]) -> float | None:
    price = float(stock.get("price") or 0)
    fair_price = float(stock.get("fair_price") or 0)
    if price <= 0 or fair_price <= 0:
        return None
    return (fair_price - price) / price * 100


def risk_score_label(stock: dict[str, Any]) -> str:
    beta = float(stock.get("beta") or 1.0)
    if beta < 0.85:
        return "Low"
    if beta < 1.25:
        return "Low-Mid"
    if beta < 1.75:
        return "Mid-High"
    return "High"


def valuation_score_text(stock: dict[str, Any]) -> str:
    status = stock.get("valuation_status", "Fair Value")
    if status == "Undervalued":
        return "Attractive"
    if status == "Overvalued":
        return "Caution"
    return "Neutral"


def visual_score_pct(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def visual_score_tone(score: float) -> str:
    score = visual_score_pct(score)
    if score >= 72:
        return "good"
    if score >= 52:
        return "mid"
    if score >= 34:
        return "watch"
    return "risk"


def portfolio_score_card_html(label: str, value: str, score: float, detail: str) -> str:
    safe_score = visual_score_pct(score)
    return f"""
        <div class="portfolio-score-card {visual_score_tone(safe_score)}" tabindex="0">
            <div class="portfolio-score-label">{ui_html(str(label))}</div>
            <div class="portfolio-score-value">{escape(str(value))}</div>
            <div class="portfolio-score-bar"><span style="--value:{safe_score:.0f}%"></span></div>
            <div class="portfolio-score-detail">{escape(str(detail))}</div>
        </div>
    """


def render_portfolio_valuation_board(stock: dict[str, Any]) -> None:
    tri = stock.get("triangulation", {})
    upside = valuation_upside(stock)
    beta = float(stock.get("beta") or 1.0)
    pe = float(stock.get("pe") or 0.0)
    growth = float(stock.get("growth_rate") or 0.0) * 100
    valid_models = int(tri.get("valid_models") or 0)
    upside_score = 50.0 if upside is None else visual_score_pct(50 + upside * 1.8)
    risk_score = visual_score_pct(92 - abs(beta - 1.0) * 46)
    model_score = visual_score_pct(valid_models / 3 * 100)
    quality_score = visual_score_pct(54 + growth * 1.2 - max(pe - 25, 0) * 0.8)
    upside_text = "N/A" if upside is None else f"{upside:+.1f}%"
    fair_value = stock_money(stock, stock.get("fair_price")) if stock.get("fair_price") else "N/A"
    cards = "".join(
        [
            portfolio_score_card_html(
                "Upside",
                upside_text,
                upside_score,
                f"{ui('Current price')} {stock_money(stock, stock.get('price'))}; {ui('blended fair value')} {fair_value}.",
            ),
            portfolio_score_card_html(
                "Risk",
                risk_score_label(stock),
                risk_score,
                f"Beta {fmt_number(beta)} {ui('drives the volatility read for portfolio fit.')}",
            ),
            portfolio_score_card_html(
                "Valuation Models",
                f"{valid_models}/3",
                model_score,
                "Income, asset, and market approaches are checked when source inputs are available.",
            ),
            portfolio_score_card_html(
                "Growth / Quality",
                f"{quality_score:.0f}",
                quality_score,
                f"Growth {growth:.1f}% and PER {fmt_number(pe)} {ui('are compressed into one visual signal.')}",
            ),
        ]
    )
    st.markdown(
        f"""
        <div class="portfolio-valuation-board" tabindex="0">
            <div class="portfolio-valuation-head">
                <div>
                    <div class="portfolio-valuation-kicker">{ui_html('Portfolio valuation lens')}</div>
                    <div class="portfolio-valuation-title">{escape(str(stock.get("name", stock.get("symbol", "Stock"))))} ({escape(str(stock.get("symbol", "")))})</div>
                    <div class="portfolio-valuation-meta">
                        <span class="portfolio-valuation-chip">{escape(str(stock.get("industry", "N/A")))}</span>
                        <span class="portfolio-valuation-chip">{ui_html('Price')} {escape(stock_money(stock, stock.get("price")))}</span>
                        <span class="portfolio-valuation-chip">{ui_html('Fair')} {escape(fair_value)}</span>
                        <span class="portfolio-valuation-chip">PER {escape(fmt_number(pe))}</span>
                    </div>
                </div>
                <span class="portfolio-valuation-status" style="background:{status_color(str(stock.get("valuation_status", "Fair Value")))};">
                    {escape(str(stock.get("valuation_status", "N/A")))}
                </span>
            </div>
            <div class="portfolio-score-grid">{cards}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def candle_heights(symbol: str) -> list[tuple[str, int, int]]:
    history = load_price_history(symbol, days=90).tail(13)
    if history.empty or len(history) < 3:
        fallback = [52, 70, 86, 102, 132, 112, 92, 118, 154, 136, 172, 196, 180]
        return [("up" if idx % 3 != 0 else "down", height, 25 + (height % 55)) for idx, height in enumerate(fallback)]

    closes = history["Close"].astype(float).tolist()
    low = min(closes)
    high = max(closes)
    span = high - low if high > low else 1
    candles = []
    for idx, close in enumerate(closes):
        previous = closes[idx - 1] if idx else close
        direction = "up" if close >= previous else "down"
        height = int(56 + ((close - low) / span) * 142)
        volume_proxy = int(24 + abs(close - previous) / max(abs(previous), 1) * 900)
        candles.append((direction, max(48, min(height, 205)), max(24, min(volume_proxy, 78))))
    return candles


def render_stock_terminal(stock: dict[str, Any]) -> None:
    symbol = escape(str(stock["symbol"]))
    name = escape(str(stock["name"]))
    industry = escape(str(stock.get("industry") or "N/A"))
    status = escape(str(stock.get("valuation_status") or "Fair Value"))
    change = float(stock.get("change_pct") or 0)
    change_class = "green" if change >= 0 else "red"
    upside = valuation_upside(stock)
    upside_text = "N/A" if upside is None else f"{upside:+.1f}%"
    fair_value = stock_money(stock, stock["fair_price"]) if stock.get("fair_price") else "N/A"
    pe_text = fmt_number(stock.get("pe"))
    growth_text = f"{float(stock.get('growth_rate') or 0) * 100:.1f}%"
    beta_text = fmt_number(stock.get("beta"))
    candles = candle_heights(stock["symbol"])
    candle_html = "\n".join(
        f'<div class="candle {direction}" style="height:{height}px"></div>'
        for direction, height, _ in candles
    )
    volume_html = "\n".join(
        f'<div class="vol {direction}" style="height:{volume_height}%"></div>'
        for direction, _, volume_height in candles
    )
    st.markdown(
        f"""
        <div class="terminal-showcase result-terminal">
            <div class="terminal-shell">
                <div class="terminal-topbar">
                    <div class="terminal-mini-logo">N</div>
                    <div class="terminal-search"><span>Search</span><span>{symbol}</span></div>
                    <div class="terminal-nav">
                        <span class="active">Market</span>
                        <span>Valuation</span>
                        <span>Portfolio</span>
                        <span>Risk</span>
                        <span>Research</span>
                    </div>
                    <div class="terminal-user">{escape(datetime.now().strftime("%b %d, %Y"))}<br><b>Finnhub live data</b></div>
                </div>
                <div class="terminal-body">
                    <div class="terminal-chart-card">
                        <div class="terminal-stock-head">
                            <div>
                                <div class="terminal-symbol">{symbol}</div>
                                <div class="terminal-company">{name} · {industry}</div>
                            </div>
                            <div class="terminal-price">{stock_money(stock, stock["price"])} <span class="{change_class}">{change:+.2f}%</span></div>
                        </div>
                        <div class="terminal-chart-grid">
                            <div class="ma-line ma-green"></div>
                            <div class="ma-line ma-blue"></div>
                            <div class="candle-row">
                                {candle_html}
                            </div>
                        </div>
                        <div class="volume-row">
                            {volume_html}
                        </div>
                    </div>
                    <div class="terminal-side">
                        <div class="terminal-side-card">
                            <div class="side-title">INSTITUTIONAL METRICS: {symbol}</div>
                            <div class="metric-grid-dark">
                                <div><div class="dark-label">Fair Value</div><div class="dark-value">{fair_value}</div></div>
                                <div><div class="dark-label">Upside</div><div class="dark-value {'green' if upside is None or upside >= 0 else 'red'}">{upside_text}</div></div>
                                <div><div class="dark-label">Risk Score</div><div class="dark-value orange">{risk_score_label(stock)}</div></div>
                                <div><div class="dark-label">Valuation</div><div class="dark-value green">{valuation_score_text(stock)}</div></div>
                            </div>
                        </div>
                        <div class="terminal-side-card">
                            <div class="side-title">TRIANGLE VALUATION</div>
                            <div class="radar-wrap"><div class="radar-triangle"></div></div>
                            <div class="radar-scores">
                                <span>PER<b>{pe_text}</b></span>
                                <span>Growth<b>{growth_text}</b></span>
                                <span>Beta<b style="color:#fbbf24;">{beta_text}</b></span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="terminal-status-strip">
                    <span>Status: <b>{status}</b></span>
                    <span>Market Cap: <b>{fmt_market_cap(stock.get("market_cap"), stock.get("currency", "USD"))}</b></span>
                    <span>EPS: <b>{stock_money(stock, float(stock.get("eps") or 0))}</b></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def clamp_score(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return max(low, min(high, value))


def render_valuation_radar(stock: dict[str, Any]) -> None:
    upside = valuation_upside(stock)
    beta = float(stock.get("beta") or 1.0)
    growth = float(stock.get("growth_rate") or 0.0) * 100
    pe = float(stock.get("pe") or 0)

    value_score = clamp_score(5 + ((upside or 0) / 8))
    risk_score = clamp_score(10 - abs(beta - 1) * 4)
    quality_score = clamp_score(5 + min(growth, 40) / 10 - (max(pe - 25, 0) / 25))

    center_x = 150
    center_y = 150
    max_radius = 96
    axes = [(-90, value_score), (150, risk_score), (30, quality_score)]
    points = []
    for angle, score in axes:
        radius = max_radius * (score / 10)
        radians = math.radians(angle)
        x = center_x + radius * math.cos(radians)
        y = center_y + radius * math.sin(radians)
        points.append(f"{x:.1f},{y:.1f}")

    grid_triangles = []
    for ratio in [0.25, 0.5, 0.75, 1.0]:
        radius = max_radius * ratio
        grid_points = []
        for angle in [-90, 150, 30]:
            radians = math.radians(angle)
            x = center_x + radius * math.cos(radians)
            y = center_y + radius * math.sin(radians)
            grid_points.append(f"{x:.1f},{y:.1f}")
        grid_triangles.append(f'<polygon points="{" ".join(grid_points)}" fill="none" stroke="#cbd5e1" stroke-width="1"/>')

    upside_text = "N/A" if upside is None else f"{upside:+.1f}%"
    st.markdown(
        f"""
        <div class="valuation-radar-card">
            <div>
                <div class="valuation-radar-title">{ui_html('Modern Valuation Radar')}</div>
                <div class="valuation-radar-copy">
                    {ui_html('This radar summarizes the triangulation result into three readable dimensions: value opportunity, beta-adjusted risk balance, and growth/quality signal.')}
                </div>
                <div class="valuation-radar-legend">
                    <div><span>{ui_html('Value Opportunity')}</span><b>{value_score:.1f}/10</b></div>
                    <div><span>{ui_html('Risk Balance')}</span><b>{risk_score:.1f}/10</b></div>
                    <div><span>{ui_html('Growth / Quality')}</span><b>{quality_score:.1f}/10</b></div>
                </div>
            </div>
            <svg class="valuation-radar-svg" viewBox="0 0 300 300" role="img" aria-label="{ui_html('Valuation radar chart')}">
                <defs>
                    <linearGradient id="radarFill" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.62"/>
                        <stop offset="55%" stop-color="#22c55e" stop-opacity="0.46"/>
                        <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.42"/>
                    </linearGradient>
                </defs>
                <rect x="14" y="14" width="272" height="272" rx="28" fill="#f8fbff" stroke="#d8e2ef"/>
                <circle cx="150" cy="150" r="112" fill="#ffffff" stroke="#e2e8f0"/>
                {"".join(grid_triangles)}
                <line x1="150" y1="150" x2="150" y2="54" stroke="#d8e2ef" stroke-width="1"/>
                <line x1="150" y1="150" x2="66.9" y2="198" stroke="#d8e2ef" stroke-width="1"/>
                <line x1="150" y1="150" x2="233.1" y2="198" stroke="#d8e2ef" stroke-width="1"/>
                <polygon points="{" ".join(points)}" fill="url(#radarFill)" stroke="#0891b2" stroke-width="3"/>
                <circle cx="{points[0].split(',')[0]}" cy="{points[0].split(',')[1]}" r="5" fill="#0891b2"/>
                <circle cx="{points[1].split(',')[0]}" cy="{points[1].split(',')[1]}" r="5" fill="#16a34a"/>
                <circle cx="{points[2].split(',')[0]}" cy="{points[2].split(',')[1]}" r="5" fill="#f59e0b"/>
                <text x="150" y="38" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="800">Value {upside_text}</text>
                <text x="54" y="222" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="800">Risk β {fmt_number(beta)}</text>
                <text x="246" y="222" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="800">Growth {growth:.1f}%</text>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stock_search_form(form_key: str, compact: bool = False) -> tuple[bool, str]:
    label = ui("Search another company") if compact else ui("Enter a stock ticker")
    submit_label = ui("Search") if compact else ui("Analyze Ticker")
    with st.form(form_key):
        query = st.text_input(
            label,
            value=st.session_state.last_query,
            placeholder="Ticker or company name: NVDA, AAPL, 삼성전자, NAVER, SK하이닉스",
        )
        submitted = st.form_submit_button(submit_label, width="stretch")
    return submitted, query


def process_stock_search(query: str) -> bool:
    if not query.strip():
        return False
    with st.spinner("Loading stock data..."):
        try:
            if not FINNHUB_API_KEY and not resolve_korean_ticker(query):
                raise ValueError(
                    "US stock search requires FINNHUB_API_KEY. Try a Korean stock such as 삼성전자 or 005930.KS, or add the API key in Secrets."
                )
            stock = load_stock(query)
            st.session_state.stocks[stock["symbol"]] = stock
            st.session_state.last_query = query.strip()
            st.session_state.selected_detail = stock["symbol"]
            st.session_state.setdefault("_selection_restore_errors", {}).pop(stock["symbol"], None)
            sync_selection_state_to_query()
            return True
        except Exception as exc:
            st.error(f"Could not load stock data: {exc}")
            return False


def process_portfolio_stock_search(query: str) -> bool:
    if not query.strip():
        return False
    with st.spinner("Loading portfolio candidate..."):
        try:
            if not FINNHUB_API_KEY and not resolve_korean_ticker(query):
                raise ValueError(
                    "US stock search requires FINNHUB_API_KEY. Try a Korean stock such as 삼성전자 or 005930.KS, or add the API key in Secrets."
                )
            stock = load_stock(query)
            st.session_state.stocks[stock["symbol"]] = stock
            st.session_state.last_query = query.strip()
            st.session_state.portfolio_search_result_symbol = stock["symbol"]
            st.session_state.setdefault("_selection_restore_errors", {}).pop(stock["symbol"], None)
            sync_selection_state_to_query()
            return True
        except Exception as exc:
            st.error(f"Could not load portfolio candidate: {exc}")
            return False


def render_portfolio_stock_search() -> None:
    st.subheader(ui("Find Stock for Portfolio"))
    with st.container(border=True):
        st.caption(
            ui("Ticker or company search with valuation, risk, and portfolio action.")
        )
        with st.form("portfolio_stock_search_form"):
            search_cols = st.columns([3, 1])
            with search_cols[0]:
                query = st.text_input(
                    ui("Ticker or company name"),
                    value=st.session_state.get("portfolio_stock_search_query", ""),
                    placeholder=ui("Ticker or company name: NVDA, AAPL, 삼성전자, NAVER"),
                )
            with search_cols[1]:
                submitted = st.form_submit_button(ui("Search and Value Stock"), width="stretch")
        if submitted:
            st.session_state.portfolio_stock_search_query = query.strip()
            if process_portfolio_stock_search(query):
                st.rerun()

        symbol = st.session_state.get("portfolio_search_result_symbol")
        stock = st.session_state.stocks.get(symbol) if symbol else None
        if not stock:
            return

        tri = stock.get("triangulation", {})
        render_portfolio_valuation_board(stock)
        render_valuation_radar(stock)
        with st.expander(ui("Open valuation basis"), expanded=False):
            st.dataframe(
                [
                    {
                        "Approach": "Income",
                        "Model": tri.get("income_model", "N/A"),
                        "Value": stock_money(stock, tri.get("income_value")) if tri.get("income_value") else "N/A",
                    },
                    {
                        "Approach": "Asset",
                        "Model": "Graham Number",
                        "Value": stock_money(stock, tri.get("asset_value")) if tri.get("asset_value") else "N/A",
                    },
                    {
                        "Approach": "Market",
                        "Model": "Peer P/E",
                        "Value": stock_money(stock, tri.get("market_value")) if tri.get("market_value") else "N/A",
                    },
                ],
                hide_index=True,
                width="stretch",
            )
            detail_cols = st.columns(4)
            with detail_cols[0]:
                metric_card("Required Return", f"{float(stock.get('expected_return') or 0) * 100:.2f}%")
            with detail_cols[1]:
                metric_card("Beta", fmt_number(stock.get("beta")))
            with detail_cols[2]:
                metric_card("PER", fmt_number(stock.get("pe")))
            with detail_cols[3]:
                metric_card("Models Used", str(tri.get("valid_models", 0)))

        action_cols = st.columns(2)
        already_in_portfolio = symbol in st.session_state.portfolio
        action_cols[0].button(
            "Already in Portfolio" if already_in_portfolio else "Add Result to Portfolio",
            key=f"portfolio_search_add_{symbol}",
            on_click=add_portfolio,
            args=(symbol,),
            width="stretch",
            disabled=already_in_portfolio,
        )
        action_cols[1].button(
            "Open Full Stock Detail",
            key=f"portfolio_search_detail_{symbol}",
            on_click=select_detail_and_open_search,
            args=(symbol,),
            width="stretch",
        )


def render_search_return_button() -> None:
    menu_href = escape(app_view_href("life"), quote=True)
    st.markdown(
        f"""
        <div class="search-return-row">
            <a class="search-return-link" href="{menu_href}" target="_self" aria-label="Back to Menu">
                <span class="search-return-arrow" aria-hidden="true">&larr;</span>
                <span>Menu</span>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stock_detail(stock: dict[str, Any]) -> None:
    tri = stock["triangulation"]
    st.divider()
    st.markdown(
        f"""
        <div class="hero-panel">
            <h2 class="detail-hero-title">{escape(str(stock['name']))}</h2>
            <div class="detail-hero-meta">{escape(str(stock['symbol']))} - {escape(str(stock['industry']))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    submitted, query = render_stock_search_form(f"stock_search_inline_{stock['symbol']}", compact=True)
    if submitted and process_stock_search(query):
        st.rerun()

    symbol = stock["symbol"]
    compare_active = symbol in st.session_state.compare
    portfolio_active = symbol in st.session_state.portfolio
    action_cols = st.columns(4)
    action_cols[0].button(
        "Compare selected" if compare_active else "Add to Compare",
        key=f"detail_compare_{symbol}",
        on_click=add_compare,
        args=(symbol,),
        width="stretch",
        disabled=compare_active,
    )
    action_cols[1].button(
        "Portfolio selected" if portfolio_active else "Add to Portfolio",
        key=f"detail_portfolio_{symbol}",
        on_click=add_portfolio,
        args=(symbol,),
        width="stretch",
        disabled=portfolio_active,
    )
    action_cols[2].button(
        "Open Compare",
        key=f"detail_open_compare_{symbol}",
        on_click=add_compare_and_open,
        args=(symbol,),
        width="stretch",
    )
    action_cols[3].button(
        "Open Portfolio",
        key=f"detail_open_portfolio_{symbol}",
        on_click=add_portfolio_and_open,
        args=(symbol,),
        width="stretch",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Current Price", stock_money(stock, stock["price"]))
    with c2:
        metric_card("Daily Change", f"{stock['change_pct']:+.2f}%", "#10b981" if stock["change_pct"] >= 0 else "#ef4444")
    with c3:
        metric_card("Blended Fair Value", stock_money(stock, stock["fair_price"]) if stock["fair_price"] else "N/A")
    with c4:
        metric_card("Valuation", stock["valuation_status"], status_color(stock["valuation_status"]))

    st.markdown("#### Price Movement")
    render_tradingview_chart(stock["symbol"])
    st.caption("Interactive chart powered by TradingView. Financial metrics and valuation data remain powered by Finnhub.")

    st.markdown("#### Key Statistics")
    stats = {
        "Market Cap": fmt_market_cap(stock["market_cap"], stock.get("currency", "USD")),
        "PER (TTM)": fmt_number(stock["pe"]),
        "Dividend Yield": f"{float(stock['dividend_yield'] or 0):.2f}%",
        "Beta": fmt_number(stock["beta"]),
        "EPS": stock_money(stock, float(stock["eps"] or 0)),
        "Growth Rate": f"{float(stock['growth_rate'] or 0) * 100:.1f}%",
    }
    st.dataframe([stats], hide_index=True, width="stretch")

    st.markdown("#### Valuation Triangulation")
    st.dataframe(
        [
            {
                "Approach": "Income",
                "Model": tri["income_model"],
                "Value": stock_money(stock, tri["income_value"]) if tri["income_value"] else "N/A",
            },
            {
                "Approach": "Asset",
                "Model": "Graham Number",
                "Value": stock_money(stock, tri["asset_value"]) if tri["asset_value"] else "N/A",
            },
            {
                "Approach": "Market",
                "Model": "Peer P/E",
                "Value": stock_money(stock, tri["market_value"]) if tri["market_value"] else "N/A",
            },
        ],
        hide_index=True,
        width="stretch",
    )
    render_valuation_radar(stock)
    st.write(
        f"{stock['name']} belongs to the {stock['industry']} sector. "
        f"The blended fair value is based on {tri['valid_models']} available valuation model(s)."
    )


def search_tab() -> None:
    render_search_return_button()

    selected_symbol = st.session_state.selected_detail
    show_top_search = not selected_symbol or selected_symbol not in st.session_state.stocks
    if show_top_search:
        submitted, query = render_stock_search_form("stock_search")
        if submitted and process_stock_search(query):
            st.rerun()

    if not FINNHUB_API_KEY:
        st.warning(
            "FINNHUB_API_KEY is not configured, so US live stock search is temporarily unavailable. "
            "Korean stock search and REIT Analysis can still work with Yahoo Finance and educational sample data."
        )
        st.info("Add FINNHUB_API_KEY in Streamlit Cloud > App settings > Secrets to enable live stock analysis.")

    if selected_symbol and selected_symbol in st.session_state.stocks:
        render_stock_detail(st.session_state.stocks[selected_symbol])

    filters = ["All", "Undervalued", "Fair Value", "Overvalued"]
    selected_filter = st.radio("Valuation filter", filters, horizontal=True)

    stocks = list(st.session_state.stocks.values())
    if selected_filter != "All":
        stocks = [s for s in stocks if s["valuation_status"] == selected_filter]

    if not stocks:
        st.info("Enter a ticker above to generate the company analysis dashboard.")
        return

    for row_start in range(0, len(stocks), 3):
        cols = st.columns(3)
        for col, stock in zip(cols, stocks[row_start : row_start + 3]):
            with col:
                render_stock_card(stock)


def compare_tab() -> None:
    st.header("Side-by-Side Comparison")
    selected = [st.session_state.stocks[s] for s in st.session_state.compare if s in st.session_state.stocks]
    if not selected:
        st.info("Select stocks to compare from the Search tab. You can compare up to 3 stocks.")
        return

    rows = []
    metrics = [
        ("Current Price", lambda s: stock_money(s, s["price"])),
        ("Change", lambda s: f"{s['change_pct']:+.2f}%"),
        ("Market Cap", lambda s: fmt_market_cap(s["market_cap"], s.get("currency", "USD"))),
        ("PER", lambda s: fmt_number(s["pe"])),
        ("Dividend Yield", lambda s: f"{float(s['dividend_yield'] or 0):.2f}%"),
        ("Beta", lambda s: fmt_number(s["beta"])),
        ("EPS", lambda s: stock_money(s, float(s["eps"] or 0))),
        ("Fair Value", lambda s: stock_money(s, s["fair_price"]) if s["fair_price"] else "N/A"),
        ("Valuation", lambda s: s["valuation_status"]),
    ]
    for label, getter in metrics:
        row = {"Metric": label}
        for stock in selected:
            row[f"{stock['name']} ({stock['symbol']})"] = getter(stock)
        rows.append(row)
    st.dataframe(rows, hide_index=True, width="stretch")

    cols = st.columns(len(selected))
    for col, stock in zip(cols, selected):
        col.button("Remove " + stock["symbol"], key=f"remove_compare_{stock['symbol']}", on_click=remove_compare, args=(stock["symbol"],))


def portfolio_market_values() -> dict[str, float]:
    values: dict[str, float] = {}
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    usdkrw, _, _ = effective_usdkrw()
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        native_value = float(stock["price"]) * float(holding.get("shares") or 0)
        values[symbol] = convert_value(
            native_value,
            stock.get("currency", "USD"),
            base_currency,
            usdkrw,
        )
    return values


def portfolio_native_market_values() -> dict[str, float]:
    values: dict[str, float] = {}
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        values[symbol] = float(stock["price"]) * float(holding.get("shares") or 0)
    return values


def portfolio_currency_breakdown() -> dict[str, float]:
    breakdown: dict[str, float] = {}
    for symbol, value in portfolio_native_market_values().items():
        stock = st.session_state.stocks.get(symbol, {})
        currency = stock.get("currency", "USD")
        breakdown[currency] = breakdown.get(currency, 0.0) + value
    return breakdown


def portfolio_analysis_weights(symbols: list[str] | None = None) -> dict[str, float]:
    selected_symbols = symbols or [
        symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks
    ]
    selected_symbols = [symbol for symbol in selected_symbols if symbol in st.session_state.stocks]
    if not selected_symbols:
        return {}

    mode = st.session_state.get("portfolio_weighting_mode", "Share-based")
    if mode == "Equal-weighted":
        equal_weight = 1 / len(selected_symbols)
        return {symbol: equal_weight for symbol in selected_symbols}

    values = portfolio_market_values()
    selected_values = {symbol: values.get(symbol, 0.0) for symbol in selected_symbols}
    total = sum(selected_values.values())
    if total <= 0:
        return {}
    return {symbol: value / total for symbol, value in selected_values.items()}


def portfolio_metrics() -> tuple[float, float, float | None, dict[str, float]]:
    total_value = 0.0
    weighted_beta = 0.0
    weighted_upside = 0.0
    valued_weight = 0.0
    sector_values: dict[str, float] = {}

    holdings = []
    market_values = portfolio_market_values()
    weights = portfolio_analysis_weights()

    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        shares = float(holding.get("shares") or 0)
        market_value = market_values.get(symbol, 0.0)
        total_value += market_value
        holdings.append((symbol, stock, shares, market_value))

    if not holdings:
        return 0.0, 0.0, None, {}

    for symbol, stock, _, market_value in holdings:
        weight = weights.get(symbol, 0.0)
        weighted_beta += float(stock["beta"] or 0) * weight
        sector_values[stock["industry"]] = sector_values.get(stock["industry"], 0) + market_value
        if stock["fair_price"] > 0 and stock["price"] > 0:
            upside = (stock["fair_price"] - stock["price"]) / stock["price"]
            weighted_upside += upside * weight
            valued_weight += weight

    valuation_score = (weighted_upside / valued_weight) * 100 if valued_weight > 0 else None
    return total_value, weighted_beta, valuation_score, sector_values


def render_sector_pie_chart(sector_values: dict[str, float]) -> None:
    data = pd.DataFrame(
        [{"Sector": sector, "Value": value} for sector, value in sector_values.items()]
    )
    if data.empty:
        return

    data["Weight"] = data["Value"] / data["Value"].sum()
    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=55, outerRadius=120)
        .encode(
            theta=alt.Theta("Value:Q"),
            color=alt.Color(
                "Sector:N",
                scale=alt.Scale(
                    range=[
                        "#3b82f6",
                        "#10b981",
                        "#f59e0b",
                        "#ef4444",
                        "#8b5cf6",
                        "#ec4899",
                        "#14b8a6",
                    ]
                ),
                legend=alt.Legend(labelColor="#31445f", titleColor="#102033"),
            ),
            tooltip=[
                alt.Tooltip("Sector:N"),
                alt.Tooltip("Value:Q", format="$,.2f"),
                alt.Tooltip("Weight:Q", format=".1%"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")


def portfolio_return_frame(symbols: list[str]) -> pd.DataFrame:
    return_series = []
    for symbol in symbols:
        history = load_price_history(symbol)
        if history.empty:
            continue
        series = history.set_index("Date")["Close"].pct_change().dropna()
        if len(series) >= 5:
            series.name = symbol
            return_series.append(series)

    if len(return_series) < 2:
        return pd.DataFrame()
    return pd.concat(return_series, axis=1).dropna(how="any")


def portfolio_weights(symbols: list[str]) -> dict[str, float]:
    return portfolio_analysis_weights(symbols)


def portfolio_risk_metrics() -> dict[str, Any] | None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    if len(symbols) < 2:
        return None
    returns = portfolio_return_frame(symbols)
    if returns.empty or len(returns.columns) < 2:
        return None

    weights_map = portfolio_weights(list(returns.columns))
    if not weights_map:
        return None

    weights = pd.Series(weights_map).reindex(returns.columns).fillna(0)
    if weights.sum() <= 0:
        return None
    weights = weights / weights.sum()

    portfolio_daily_returns = returns.mul(weights, axis=1).sum(axis=1)
    daily_vol = float(portfolio_daily_returns.std())
    annual_vol = daily_vol * (252 ** 0.5)
    annual_return = float(portfolio_daily_returns.mean()) * 252
    covariance = returns.cov()
    correlation = returns.corr()
    weighted_individual_daily_vol = float((returns.std() * weights).sum())
    diversification_benefit = max(0.0, weighted_individual_daily_vol - daily_vol)

    return {
        "returns": returns,
        "weights": weights,
        "covariance": covariance,
        "correlation": correlation,
        "daily_vol": daily_vol,
        "annual_vol": annual_vol,
        "annual_return": annual_return,
        "weighted_individual_daily_vol": weighted_individual_daily_vol,
        "diversification_benefit": diversification_benefit,
    }


def render_portfolio_risk_analysis() -> None:
    st.subheader("Portfolio Risk")
    st.caption(
        "Portfolio risk uses daily return covariance from available price history: portfolio variance = w' x covariance x w."
    )

    risk = portfolio_risk_metrics()
    if not risk:
        st.info("At least two portfolio stocks with available price history are needed for portfolio risk analysis.")
        return

    risk_color = "#10b981" if risk["annual_vol"] < 0.18 else "#f59e0b" if risk["annual_vol"] < 0.30 else "#ef4444"
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Annualized Portfolio Risk", f"{risk['annual_vol'] * 100:.1f}%", risk_color)
    with c2:
        metric_card("Expected Annual Return", f"{risk['annual_return'] * 100:+.1f}%", "#60a5fa")
    with c3:
        metric_card("Diversification Benefit", f"{risk['diversification_benefit'] * 100:.2f}% daily", "#10b981")

    st.info(
        "This risk is not a simple average of each stock's volatility. "
        "It falls when holdings have lower correlation, because gains and losses offset each other."
    )

    rows = []
    for symbol in risk["returns"].columns:
        stock = st.session_state.stocks.get(symbol, {})
        rows.append(
            {
                "Stock": symbol,
                "Weight": f"{risk['weights'][symbol] * 100:.1f}%",
                "Average Daily Return": f"{risk['returns'][symbol].mean() * 100:.3f}%",
                "Daily SD": f"{risk['returns'][symbol].std() * 100:.3f}%",
                "Beta": fmt_number(stock.get("beta")),
            }
        )
    st.dataframe(rows, hide_index=True, width="stretch")


def render_complementarity_analysis() -> None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]

    st.subheader("Stock Complementarity")
    st.caption(
        "This checks whether holdings move together or offset each other using daily return correlations from available price history."
    )

    if len(symbols) < 2:
        st.info(
            "At least two portfolio stocks with available price history are needed for complementarity analysis."
        )
        return

    returns = portfolio_return_frame(symbols)

    if returns.empty or len(returns.columns) < 2:
        st.info(
            "At least two portfolio stocks with available price history are needed for complementarity analysis."
        )
        return

    corr = returns.corr()
    pair_values = []
    for i, first in enumerate(corr.columns):
        for second in corr.columns[i + 1 :]:
            pair_values.append((first, second, float(corr.loc[first, second])))

    avg_pair_corr = sum(item[2] for item in pair_values) / len(pair_values)
    complementarity_score = max(0, min(100, (1 - avg_pair_corr) * 100))
    best_pair = min(pair_values, key=lambda item: item[2])
    crowded_pair = max(pair_values, key=lambda item: item[2])

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Complementarity Score", f"{complementarity_score:.1f}", "#10b981" if complementarity_score >= 60 else "#f59e0b")
    with c2:
        metric_card("Average Pair Correlation", f"{avg_pair_corr:.3f}")
    with c3:
        metric_card("Best Offset Pair", f"{best_pair[0]} / {best_pair[1]}", "#60a5fa")

    st.info(
        f"Lowest co-movement pair: {best_pair[0]} and {best_pair[1]} ({best_pair[2]:.3f}). "
        f"Highest co-movement pair: {crowded_pair[0]} and {crowded_pair[1]} ({crowded_pair[2]:.3f}). "
        "Lower correlation usually means better diversification because holdings may offset each other more effectively."
    )

    rows = []
    for symbol in returns.columns:
        stock = st.session_state.stocks.get(symbol, {})
        peer_corr = corr[symbol].drop(symbol).mean()
        rows.append(
            {
                "Stock": symbol,
                "Avg Daily Return": f"{returns[symbol].mean() * 100:.3f}%",
                "Daily SD": f"{returns[symbol].std() * 100:.3f}%",
                "Avg Correlation": f"{peer_corr:.3f}",
                "Beta": fmt_number(stock.get("beta")),
                "Complement Role": "Diversifier" if peer_corr < 0.35 else "Core mover" if peer_corr < 0.65 else "Highly overlapping",
            }
        )

    st.dataframe(rows, hide_index=True, width="stretch")
    st.markdown("#### Correlation Matrix")
    st.caption(
        "Correlation close to +1 means two securities moved together historically. "
        "Correlation near 0 means weak co-movement. Negative correlation means they tended to move in opposite directions. "
        "This is useful for studying diversification, but it does not guarantee future risk reduction."
    )
    st.dataframe(corr.round(3), width="stretch")


def portfolio_valuation_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    weights = portfolio_analysis_weights()
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        price = float(stock.get("price") or 0)
        fair_price = float(stock.get("fair_price") or 0)
        upside = ((fair_price - price) / price * 100) if price > 0 and fair_price > 0 else None
        weight = weights.get(symbol, 0.0)
        rows.append(
            {
                "Stock": symbol,
                "Name": stock.get("name", symbol),
                "Price": stock_money(stock, price),
                "Fair Value": stock_money(stock, fair_price) if fair_price > 0 else "N/A",
                "Upside / Downside": "N/A" if upside is None else f"{upside:+.1f}%",
                "Analysis Weight": f"{weight * 100:.1f}%",
                "Weighted Contribution": "N/A" if upside is None else f"{upside * weight:+.2f} pts",
                "Valuation": stock.get("valuation_status", "N/A"),
            }
        )
    return rows


def complementarity_summary() -> dict[str, Any] | None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    if len(symbols) < 2:
        return None
    returns = portfolio_return_frame(symbols)
    if returns.empty or len(returns.columns) < 2:
        return None

    corr = returns.corr()
    pair_values = []
    for i, first in enumerate(corr.columns):
        for second in corr.columns[i + 1 :]:
            pair_values.append((first, second, float(corr.loc[first, second])))
    if not pair_values:
        return None

    avg_pair_corr = sum(item[2] for item in pair_values) / len(pair_values)
    best_pair = min(pair_values, key=lambda item: item[2])
    crowded_pair = max(pair_values, key=lambda item: item[2])
    return {
        "average_pair_correlation": avg_pair_corr,
        "complementarity_score": max(0, min(100, (1 - avg_pair_corr) * 100)),
        "best_offset_pair": best_pair,
        "highest_co_movement_pair": crowded_pair,
        "correlation_matrix": corr,
    }


def portfolio_holdings_snapshot() -> list[dict[str, Any]]:
    usdkrw, _, _ = effective_usdkrw()
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    market_values = portfolio_market_values()
    total_value = sum(market_values.values())
    weights = portfolio_analysis_weights()
    holdings = []
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        shares = float(holding.get("shares") or 0)
        purchase_price = float(holding.get("purchase_price") or 0)
        native_value = float(stock.get("price") or 0) * shares
        native_cost_basis = purchase_price * shares if purchase_price > 0 and shares > 0 else None
        base_value = convert_value(
            native_value,
            stock.get("currency", "USD"),
            base_currency,
            usdkrw,
        )
        base_cost_basis = (
            convert_value(
                native_cost_basis,
                stock.get("currency", "USD"),
                base_currency,
                usdkrw,
            )
            if native_cost_basis is not None
            else None
        )
        native_unrealized_gain = (
            native_value - native_cost_basis
            if native_cost_basis is not None
            else None
        )
        base_unrealized_gain = (
            base_value - base_cost_basis
            if base_cost_basis is not None
            else None
        )
        unrealized_return_pct = (
            native_unrealized_gain / native_cost_basis * 100
            if native_cost_basis and native_cost_basis > 0 and native_unrealized_gain is not None
            else None
        )
        holdings.append(
            {
                "symbol": symbol,
                "name": stock.get("name", symbol),
                "currency": stock.get("currency", "USD"),
                "shares": shares,
                "price": float(stock.get("price") or 0),
                "purchase_price": purchase_price,
                "native_cost_basis": native_cost_basis,
                "base_cost_basis": base_cost_basis,
                "native_market_value": native_value,
                "base_market_value": base_value,
                "native_unrealized_gain": native_unrealized_gain,
                "base_unrealized_gain": base_unrealized_gain,
                "unrealized_return_pct": unrealized_return_pct,
                "base_weight": base_value / total_value if total_value > 0 else 0,
                "analysis_weight": weights.get(symbol, 0.0),
                "valuation_status": stock.get("valuation_status", "N/A"),
            }
        )
    return holdings


def portfolio_gain_loss_summary(holdings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    holdings = holdings if holdings is not None else portfolio_holdings_snapshot()
    costed_holdings = [
        item
        for item in holdings
        if item.get("base_cost_basis") is not None
        and float(item.get("base_cost_basis") or 0) > 0
    ]
    total_cost = sum(float(item.get("base_cost_basis") or 0) for item in costed_holdings)
    current_value = sum(float(item.get("base_market_value") or 0) for item in costed_holdings)
    unrealized_gain = current_value - total_cost if total_cost > 0 else None
    unrealized_return_pct = unrealized_gain / total_cost * 100 if total_cost > 0 and unrealized_gain is not None else None
    return {
        "costed_holding_count": len(costed_holdings),
        "total_holding_count": len(holdings),
        "total_cost_basis": total_cost if total_cost > 0 else None,
        "current_value_for_costed_holdings": current_value if total_cost > 0 else None,
        "unrealized_gain": unrealized_gain,
        "unrealized_return_pct": unrealized_return_pct,
    }


def portfolio_resilience_summary(
    holdings: list[dict[str, Any]],
    sector_values: dict[str, float],
    weighted_beta: float | None,
    valuation_score: float | None,
) -> dict[str, Any] | None:
    if not holdings:
        return None

    total_value = sum(float(item.get("base_market_value") or 0) for item in holdings)
    if total_value <= 0:
        return None

    top_holding_weight = max(float(item.get("base_weight") or 0) for item in holdings)
    top_sector_weight = max(sector_values.values()) / total_value if sector_values else 0.0
    concentration_score = clamp_score(100 - max(0.0, top_holding_weight - 0.25) / 0.45 * 100, 0, 100)
    sector_score = clamp_score(100 - max(0.0, top_sector_weight - 0.35) / 0.45 * 100, 0, 100)
    beta_value = float(weighted_beta or 0)
    beta_score = clamp_score(100 - max(0.0, beta_value - 1.0) * 65, 0, 100)
    valuation_component = 50 if valuation_score is None else clamp_score(50 + float(valuation_score), 0, 100)
    score = (
        concentration_score * 0.35
        + sector_score * 0.25
        + beta_score * 0.20
        + valuation_component * 0.20
    )
    status = "Strong" if score >= 75 else "Watch" if score >= 55 else "Concentrated"
    return {
        "score": score,
        "status": status,
        "top_holding_weight": top_holding_weight,
        "top_sector_weight": top_sector_weight,
        "weighted_beta": beta_value,
        "valuation_score": valuation_score,
        "components": [
            {"Dimension": "Top holding balance", "Score": concentration_score},
            {"Dimension": "Sector spread", "Score": sector_score},
            {"Dimension": "Beta balance", "Score": beta_score},
            {"Dimension": "Valuation buffer", "Score": valuation_component},
        ],
    }


def render_portfolio_resilience_panel(summary: dict[str, Any] | None) -> None:
    if not summary:
        return

    st.subheader("Portfolio Resilience Score")
    score = float(summary["score"])
    score_color_value = "#10b981" if score >= 75 else "#f59e0b" if score >= 55 else "#ef4444"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Portfolio Score", f"{score:.0f}/100", score_color_value)
    with c2:
        metric_card("Status", str(summary["status"]), score_color_value)
    with c3:
        metric_card("Top Holding", f"{float(summary['top_holding_weight']) * 100:.1f}%")
    with c4:
        metric_card("Top Sector", f"{float(summary['top_sector_weight']) * 100:.1f}%")

    component_data = pd.DataFrame(summary["components"])
    chart = (
        alt.Chart(component_data)
        .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8)
        .encode(
            y=alt.Y("Dimension:N", sort=None, title=None),
            x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Dimension:N", legend=None),
            tooltip=["Dimension", alt.Tooltip("Score:Q", format=".1f")],
        )
        .properties(height=220)
    )
    st.altair_chart(chart, width="stretch")

    if float(summary["top_holding_weight"]) >= 0.40:
        st.warning("Top holding concentration is high. Review whether one position dominates the total outcome.")
    if float(summary["top_sector_weight"]) >= 0.60:
        st.warning("Top sector concentration is high. Review whether one theme dominates the portfolio.")


def mobile_signed_class(value: Any) -> str:
    numeric = safe_float(value, 4)
    if numeric is None:
        return ""
    return "mobile-positive" if numeric >= 0 else "mobile-negative"


def render_mobile_portfolio_deck(
    current_holdings: list[tuple],
    total_value: float,
    weighted_beta: float | None,
    valuation_score: float | None,
    total_cost_basis: float,
    total_unrealized_gain: float | None,
    total_unrealized_return_pct: float | None,
) -> None:
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    value_text = fmt_money(total_value, base_currency)
    beta_text = fmt_number(weighted_beta)
    valuation_text = "N/A" if valuation_score is None else f"{valuation_score:+.1f}%"
    cost_text = "Missing" if total_cost_basis <= 0 else fmt_money(total_cost_basis, base_currency)
    pnl_text = (
        "Needs cost basis"
        if total_unrealized_gain is None
        else fmt_signed_money(total_unrealized_gain, base_currency)
    )
    return_text = "N/A" if total_unrealized_return_pct is None else f"{total_unrealized_return_pct:+.1f}%"
    pnl_class = mobile_signed_class(total_unrealized_gain)

    holding_cards = []
    current_total = sum(float(item[5]) for item in current_holdings)
    for item in current_holdings[:6]:
        (
            symbol,
            stock,
            shares,
            purchase_price,
            _native_value,
            base_value,
            _native_cost_basis,
            _base_cost_basis,
            base_unrealized_gain,
            unrealized_return_pct,
        ) = item
        weight = base_value / current_total * 100 if current_total else 0
        holding_return = "N/A" if unrealized_return_pct is None else f"{unrealized_return_pct:+.1f}%"
        holding_pnl = fmt_signed_money(base_unrealized_gain, base_currency)
        holding_class = mobile_signed_class(base_unrealized_gain)
        purchase_text = "Missing" if purchase_price <= 0 else stock_money(stock, purchase_price)
        holding_cards.append(
            f"""
            <div class="mobile-holding-card">
                <div class="eyebrow">Holding</div>
                <div class="title">{escape(symbol)} · {escape(str(stock.get("name", symbol)))}</div>
                <span class="hint">{shares:g} shares · cost {escape(purchase_text)}</span>
                <div class="meta">
                    <div class="mobile-mini-stat"><b>{escape(fmt_money(base_value, base_currency))}</b><span>Market</span></div>
                    <div class="mobile-mini-stat"><b class="{holding_class}">{escape(holding_pnl)}</b><span>P/L</span></div>
                    <div class="mobile-mini-stat"><b>{holding_return}</b><span>Return</span></div>
                    <div class="mobile-mini-stat"><b>{weight:.1f}%</b><span>Weight</span></div>
                </div>
            </div>
            """
        )

    st.markdown(
        f"""
        <div class="mobile-only-deck">
            <div class="mobile-focus-card">
                <h3>Mobile Portfolio Snapshot</h3>
                <p>Start with value, cost basis, P/L, and risk readiness. The wide table below remains available for desktop-style review.</p>
            </div>
            <div class="mobile-card-grid">
                <div class="mobile-card"><div class="eyebrow">Value</div><div class="value">{escape(value_text)}</div><span class="label">Current market value</span></div>
                <div class="mobile-card"><div class="eyebrow">Cost</div><div class="value">{escape(cost_text)}</div><span class="label">Entered cost basis</span></div>
                <div class="mobile-card"><div class="eyebrow">P/L</div><div class="value {pnl_class}">{escape(pnl_text)}</div><span class="label">Unrealized return {escape(return_text)}</span></div>
                <div class="mobile-card"><div class="eyebrow">Risk</div><div class="value">{escape(beta_text)}</div><span class="label">Weighted beta · valuation {escape(valuation_text)}</span></div>
            </div>
            <div class="mobile-holding-grid">
                {''.join(holding_cards)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_financial_snapshot(note: str, mood: str, next_action: str) -> dict[str, Any]:
    total_value, weighted_beta, valuation_score, _ = portfolio_metrics()
    usdkrw, fx_source, fx_date = effective_usdkrw()
    risk = portfolio_risk_metrics()
    comp = complementarity_summary()
    personal_result = st.session_state.get("last_personal_finance_result", {})
    holdings = portfolio_holdings_snapshot()
    gain_loss = portfolio_gain_loss_summary(holdings)

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mood": mood,
        "note": note,
        "next_action": next_action,
        "base_currency": st.session_state.get("portfolio_base_currency", "USD"),
        "usdkrw": usdkrw,
        "fx_source": fx_source,
        "fx_date": fx_date,
        "portfolio": {
            "total_market_value": total_value,
            "weighted_beta": weighted_beta,
            "valuation_score": valuation_score,
            "weighting_mode": st.session_state.get("portfolio_weighting_mode", "Share-based"),
            "holdings": holdings,
            "gain_loss": gain_loss,
        },
        "risk": None
        if not risk
        else {
            "annualized_risk": risk["annual_vol"],
            "expected_annual_return": risk["annual_return"],
            "diversification_benefit_daily": risk["diversification_benefit"],
        },
        "complementarity": None
        if not comp
        else {
            "score": comp["complementarity_score"],
            "average_pair_correlation": comp["average_pair_correlation"],
            "best_offset_pair": list(comp["best_offset_pair"]),
            "highest_co_movement_pair": list(comp["highest_co_movement_pair"]),
        },
        "personal_finance": personal_result,
    }


def what_if_scenario_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">What-if Scenario Lab</h1>
            <div class="hero-muted">Stress-test life and portfolio assumptions before a future AI coach explains the trade-offs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "This is educational scenario analysis, not a forecast or investment recommendation. "
        "It helps users see which assumptions can move portfolio value, liquidity, debt pressure, and risk capacity."
    )

    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    usdkrw, fx_source, fx_date = effective_usdkrw()
    current_values = portfolio_market_values()
    current_total = sum(current_values.values())

    rate_sensitive_keywords = ("reit", "real estate", "property", "mortgage")
    rate_sensitive_value = 0.0
    for symbol, value in current_values.items():
        stock = st.session_state.stocks.get(symbol, {})
        descriptor = f"{stock.get('name', '')} {stock.get('industry', '')}".lower()
        if any(keyword in descriptor for keyword in rate_sensitive_keywords):
            rate_sensitive_value += value
    detected_rate_allocation = int(round(rate_sensitive_value / current_total * 100)) if current_total > 0 else 20

    st.subheader("Scenario Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        income_change_pct = st.slider("Monthly income change", -60, 20, -10, 5, format="%d%%")
        expense_change_pct = st.slider("Living expense change", -20, 60, 10, 5, format="%d%%")
        cash_shock = st.number_input("One-time cash shock", min_value=0.0, value=0.0, step=500.0)
    with c2:
        portfolio_change_pct = st.slider("Portfolio market move", -50, 30, -15, 5, format="%d%%")
        fx_change_pct = st.slider("USD/KRW rate change", -30, 30, 0, 5, format="%d%%")
        apply_drawdown_to_pf = st.checkbox("Apply portfolio move to taxable investments", value=True)
    with c3:
        rate_change_bps = st.slider("Interest-rate move", -200, 300, 100, 25)
        rate_sensitive_allocation = st.slider("Rate-sensitive allocation", 0, 100, detected_rate_allocation, 5)
        rate_price_sensitivity = st.slider("Price impact per +100 bps", -15, 5, -6, 1)

    scenario_usdkrw = usdkrw * (1 + fx_change_pct / 100)
    projected_rows: list[dict[str, Any]] = []
    projected_market_total = 0.0
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        shares = float(holding.get("shares") or 0)
        scenario_native_value = float(stock.get("price") or 0) * shares * (1 + portfolio_change_pct / 100)
        scenario_base_value = convert_value(
            scenario_native_value,
            stock.get("currency", "USD"),
            base_currency,
            scenario_usdkrw,
        )
        projected_market_total += scenario_base_value
        current_base_value = current_values.get(symbol, 0.0)
        projected_rows.append(
            {
                "Holding": symbol,
                "Currency": stock.get("currency", "USD"),
                "Current Value": fmt_money(current_base_value, base_currency),
                "Scenario Value": fmt_money(scenario_base_value, base_currency),
                "Change": fmt_money(scenario_base_value - current_base_value, base_currency),
            }
        )

    rate_effect = current_total * (rate_sensitive_allocation / 100) * (rate_change_bps / 100) * (rate_price_sensitivity / 100)
    projected_total = max(0.0, projected_market_total + rate_effect)
    total_delta = projected_total - current_total
    total_delta_pct = total_delta / current_total * 100 if current_total > 0 else 0.0

    st.subheader("Portfolio Stress Result")
    if current_total > 0:
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            metric_card("Current Portfolio", fmt_money(current_total, base_currency))
        with p2:
            metric_card("Scenario Portfolio", fmt_money(projected_total, base_currency), "#10b981" if total_delta >= 0 else "#ef4444")
        with p3:
            metric_card("Estimated Change", f"{total_delta_pct:+.1f}%", "#10b981" if total_delta >= 0 else "#ef4444")
        with p4:
            metric_card("Rate-Sleeve Effect", fmt_money(rate_effect, base_currency), "#f59e0b")
        st.caption(
            f"FX baseline: USD/KRW {usdkrw:,.2f} from {fx_source} ({fx_date}). "
            f"Scenario FX: USD/KRW {scenario_usdkrw:,.2f}."
        )
        st.dataframe(projected_rows, hide_index=True, width="stretch")
    else:
        st.warning("Add holdings in the Portfolio tab to stress-test portfolio value, FX exposure, and rate-sensitive allocation.")

    st.subheader("Personal Finance Stress Result")
    personal_profile = st.session_state.get("last_personal_finance_profile")
    personal_result = st.session_state.get("last_personal_finance_result")
    stressed_result: dict[str, Any] | None = None
    if personal_profile:
        from personal_finance_engine import PersonalFinanceProfile, calculate_personal_finance

        baseline_profile = dict(personal_profile)
        stressed_profile = {
            **baseline_profile,
            "monthly_income": max(0.0, float(baseline_profile["monthly_income"]) * (1 + income_change_pct / 100)),
            "fixed_expenses": max(0.0, float(baseline_profile["fixed_expenses"]) * (1 + expense_change_pct / 100)),
            "variable_expenses": max(0.0, float(baseline_profile["variable_expenses"]) * (1 + expense_change_pct / 100)),
            "cash_savings": max(0.0, float(baseline_profile["cash_savings"]) - cash_shock),
            "taxable_investments": max(
                0.0,
                float(baseline_profile["taxable_investments"])
                * (1 + portfolio_change_pct / 100 if apply_drawdown_to_pf else 1),
            ),
        }
        stressed_result = calculate_personal_finance(PersonalFinanceProfile(**stressed_profile))
        if not personal_result:
            personal_result = calculate_personal_finance(PersonalFinanceProfile(**baseline_profile))

        health_delta = float(stressed_result["financial_health_score"]) - float(personal_result["financial_health_score"])
        surplus_delta = float(stressed_result["monthly_surplus"]) - float(personal_result["monthly_surplus"])
        pf1, pf2, pf3, pf4 = st.columns(4)
        with pf1:
            metric_card("Health Score", f"{float(stressed_result['financial_health_score']):.1f}/100", "#10b981" if health_delta >= 0 else "#ef4444")
        with pf2:
            metric_card("Score Change", f"{health_delta:+.1f}", "#10b981" if health_delta >= 0 else "#ef4444")
        with pf3:
            metric_card("Monthly Surplus", fmt_money(float(stressed_result["monthly_surplus"])), "#10b981" if surplus_delta >= 0 else "#ef4444")
        with pf4:
            metric_card("Emergency Fund", f"{float(stressed_result['emergency_months']):.1f} months", "#10b981" if float(stressed_result["emergency_months"]) >= 3 else "#ef4444")
    else:
        st.warning("Open the Personal Finance tab once to create a baseline before running life-level stress tests.")

    st.subheader("AI-Ready Scenario Interpretation")
    interpretation: list[str] = []
    if current_total > 0:
        if total_delta_pct <= -20:
            interpretation.append("Portfolio stress is severe: selected assumptions create a decline greater than 20%.")
        elif total_delta_pct < 0:
            interpretation.append("Portfolio stress is moderate: selected assumptions reduce portfolio value.")
        else:
            interpretation.append("Portfolio scenario is positive under the selected market and FX assumptions.")
        if abs(fx_change_pct) >= 10:
            interpretation.append("FX movement is material; separate market return from currency translation effects.")
        if rate_change_bps > 0 and rate_sensitive_allocation > 0:
            interpretation.append("Higher rates pressure the rate-sensitive sleeve under the selected assumption.")
    if stressed_result:
        if bool(stressed_result.get("no_income_mode")):
            interpretation.append(
                "No-income planning mode: use runway target and drawdown resilience as the primary stress signals."
            )
            if float(stressed_result.get("runway_gap_months") or 0) < 0:
                interpretation.append(
                    "Runway warning: cash reserve is below the selected no-income planning target."
                )
            if float(stressed_result.get("investment_exposure_ratio") or 0) >= 0.60:
                interpretation.append(
                    "Investment exposure warning: taxable investments remain above 60% of assets during a no-income period."
                )
        if float(stressed_result["emergency_months"]) < 3:
            interpretation.append("Liquidity warning: emergency fund falls below 3 months of living expenses.")
        if float(stressed_result["debt_to_income"]) > 0.36:
            interpretation.append("Debt-pressure warning: debt-to-income rises above the common 36% reference level.")
        if float(stressed_result["financial_health_score"]) < 45:
            interpretation.append("Risk-capacity warning: financial health score suggests limited ability to absorb volatility.")
    if not interpretation:
        interpretation.append("Add portfolio holdings and Personal Finance inputs to generate richer scenario interpretation.")
    for item in interpretation:
        st.write(f"- {item}")

    scenario_packet = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "purpose": "Educational scenario analysis for AI reasoning readiness; not investment advice.",
        "inputs": {
            "income_change_pct": income_change_pct,
            "expense_change_pct": expense_change_pct,
            "cash_shock": cash_shock,
            "portfolio_change_pct": portfolio_change_pct,
            "fx_change_pct": fx_change_pct,
            "rate_change_bps": rate_change_bps,
            "rate_sensitive_allocation_pct": rate_sensitive_allocation,
            "rate_price_sensitivity_per_100bps_pct": rate_price_sensitivity,
        },
        "portfolio": {
            "base_currency": base_currency,
            "current_total": current_total,
            "scenario_total": projected_total,
            "scenario_delta_pct": total_delta_pct,
            "current_usdkrw": usdkrw,
            "scenario_usdkrw": scenario_usdkrw,
            "rate_effect": rate_effect,
        },
        "personal_finance": stressed_result,
        "interpretation": interpretation,
    }
    st.session_state.last_scenario_packet = scenario_packet
    with st.expander("Structured Scenario Packet for Future AI Coach"):
        st.json(scenario_packet)
        st.download_button(
            "Download Scenario JSON",
            data=json.dumps(scenario_packet, indent=2, ensure_ascii=False),
            file_name="toxiguard_nora_scenario_packet.json",
            mime="application/json",
            width="stretch",
        )


def ai_coach_context_snapshot() -> dict[str, Any]:
    total_value, weighted_beta, valuation_score, _ = portfolio_metrics()
    risk = portfolio_risk_metrics()
    comp = complementarity_summary()
    personal = st.session_state.get("last_personal_finance_result") or {}
    profile = st.session_state.get("last_personal_finance_profile") or {}
    diary = st.session_state.get("financial_diary", [])
    scenario = st.session_state.get("last_scenario_packet")
    holdings = portfolio_holdings_snapshot()

    missing: list[str] = []
    if not personal:
        missing.append("Personal Finance baseline")
    if not holdings:
        missing.append("Portfolio holdings")
    if not risk and len(holdings) < 2:
        missing.append("At least two holdings for covariance risk")
    if not scenario:
        missing.append("Scenario stress packet")
    if not diary:
        missing.append("Diary memory snapshot")

    return {
        "portfolio": {
            "total_value": total_value,
            "base_currency": st.session_state.get("portfolio_base_currency", "USD"),
            "weighted_beta": weighted_beta,
            "valuation_score": valuation_score,
            "holdings": holdings,
            "risk": risk,
            "complementarity": comp,
        },
        "personal": personal,
        "profile": profile,
        "scenario": scenario,
        "diary": diary,
        "missing": missing,
    }


def ai_coach_readiness(context: dict[str, Any]) -> dict[str, Any]:
    personal = context["personal"]
    portfolio = context["portfolio"]
    holdings = portfolio["holdings"]
    risk = portfolio["risk"]
    comp = portfolio["complementarity"]
    diary = context["diary"]
    scenario = context["scenario"]

    score = 0.0
    reasons: list[str] = []

    if personal:
        health = float(personal.get("financial_health_score") or 0)
        emergency_months = float(personal.get("emergency_months") or 0)
        dti = float(personal.get("debt_to_income") or 0)
        monthly_surplus = float(personal.get("monthly_surplus") or 0)
        score += max(0.0, min(42.0, health * 0.42))
        if emergency_months >= 6:
            score += 10
            reasons.append("Emergency fund is strong.")
        elif emergency_months >= 3:
            score += 7
            reasons.append("Emergency fund is usable but still worth monitoring.")
        else:
            score += 2
            reasons.append("Emergency fund is below the usual 3-month reference point.")
        if dti <= 0.25:
            score += 6
            reasons.append("Debt pressure looks manageable.")
        elif dti <= 0.36:
            score += 4
            reasons.append("Debt pressure is moderate.")
        else:
            score += 1
            reasons.append("Debt-to-income is above the common 36% reference point.")
        if monthly_surplus > 0:
            score += 6
            reasons.append("Monthly surplus is positive.")
        else:
            reasons.append("Monthly surplus is not positive.")
    else:
        reasons.append("Personal finance baseline is missing.")

    if holdings:
        score += 8
        beta = portfolio["weighted_beta"]
        valuation_score = portfolio["valuation_score"]
        if beta is not None:
            score += 5 if float(beta) <= 1.2 else 2
            reasons.append(f"Weighted beta is {fmt_number(beta)}.")
        if valuation_score is not None:
            score += 5
            reasons.append(f"Portfolio valuation score is {float(valuation_score):+.1f}%.")
        if risk:
            annual_vol = float(risk["annual_vol"])
            if annual_vol <= 0.18:
                score += 9
                reasons.append("Estimated annualized portfolio risk is relatively low.")
            elif annual_vol <= 0.30:
                score += 6
                reasons.append("Estimated annualized portfolio risk is moderate.")
            else:
                score += 2
                reasons.append("Estimated annualized portfolio risk is high.")
        if comp:
            comp_score = float(comp["complementarity_score"])
            score += 5 if comp_score >= 60 else 3 if comp_score >= 35 else 1
            reasons.append(f"Complementarity score is {comp_score:.1f}.")
    else:
        reasons.append("Portfolio holdings are missing.")

    if scenario:
        score += 5
        reasons.append("A scenario stress packet is available.")
    if diary:
        score += 4
        reasons.append("Diary memory exists for reflection.")

    score = max(0.0, min(100.0, score))
    if not personal or not holdings:
        label = "Data Needed"
    elif score >= 75:
        label = "Prepared"
    elif score >= 55:
        label = "Developing"
    elif score >= 35:
        label = "Caution"
    else:
        label = "Fragile"

    return {"score": score, "label": label, "reasons": reasons}


NORA_GOAL_STRATEGIES = {
    "protect_runway": {
        "icon": "01",
        "color": "#0f766e",
        "view": "finance",
        "label_en": "Protect Runway",
        "label_ko": "생존기간 보호",
        "short_en": "Cash first",
        "short_ko": "현금 우선",
        "strategy_en": "Check burn rate, emergency cash, debt pressure, and forced-selling risk before reviewing assets.",
        "strategy_ko": "자산보다 먼저 지출 속도, 비상현금, 부채 압력, 강제매도 위험을 확인합니다.",
    },
    "grow_capital": {
        "icon": "02",
        "color": "#2563eb",
        "view": "portfolio",
        "label_en": "Grow Capital",
        "label_ko": "자본 성장",
        "short_en": "Portfolio fit",
        "short_ko": "포트폴리오 적합성",
        "strategy_en": "Start from portfolio quality, concentration, valuation, beta, and downside capacity.",
        "strategy_ko": "포트폴리오 품질, 집중도, 가치평가, 베타, 하락 감당력을 먼저 봅니다.",
    },
    "build_income": {
        "icon": "03",
        "color": "#d97706",
        "view": "scenario",
        "label_en": "Build Income",
        "label_ko": "소득 만들기",
        "short_en": "Cash flow path",
        "short_ko": "현금흐름 경로",
        "strategy_en": "Compare study, career, dividend, and savings paths against monthly cash needs.",
        "strategy_ko": "학업, 커리어, 배당, 저축 경로를 월 현금 필요액과 비교합니다.",
    },
    "real_estate_plan": {
        "icon": "04",
        "color": "#7c3aed",
        "view": "reit",
        "label_en": "Real Estate Plan",
        "label_ko": "부동산 계획",
        "short_en": "Rate and property risk",
        "short_ko": "금리/자산 위험",
        "strategy_en": "Review REIT/property exposure, income durability, liquidity, and rate sensitivity.",
        "strategy_ko": "REIT/부동산 노출, 소득 지속성, 유동성, 금리 민감도를 확인합니다.",
    },
}


def normalized_goal_key(goal: str | None) -> str | None:
    if not goal:
        return None
    goal = str(goal).strip()
    return goal if goal in NORA_GOAL_STRATEGIES else None


def active_goal_key() -> str | None:
    goal = normalized_goal_key(query_param_value("goal"))
    if goal:
        st.session_state.nora_goal = goal
        return goal
    return normalized_goal_key(st.session_state.get("nora_goal"))


def active_goal_params() -> dict[str, str]:
    goal = active_goal_key()
    return {"goal": goal} if goal else {}


def goal_href(goal: str) -> str:
    goal = normalized_goal_key(goal) or "protect_runway"
    config = NORA_GOAL_STRATEGIES[goal]
    params = {"view": config["view"], "mode": "dashboard", "goal": goal}
    params.update(language_params())
    params.update(selection_state_params())
    return f"?{urlencode(params)}"


def app_view_href(view: str) -> str:
    params = {"view": view, "mode": "dashboard"}
    params.update(language_params())
    params.update(active_goal_params())
    params.update(selection_state_params())
    return f"?{urlencode(params)}"


def app_detail_href(symbol: str) -> str:
    params = {"view": "details", "detail": symbol, "mode": "dashboard"}
    params.update(language_params())
    params.update(selection_state_params())
    detail_symbols = selected_symbols_for_url()
    if symbol not in detail_symbols:
        detail_symbols.append(symbol)
    params["symbols"] = ",".join(detail_symbols)
    return f"?{urlencode(params)}"


def language_toggle_href(language: str) -> str:
    target_language = normalized_language(language) or "en"
    params: dict[str, str] = {"lang": target_language}
    valid_keys = {item["key"] for item in NAV_ITEMS} if "NAV_ITEMS" in globals() else set()
    current_view = query_param_value("view") or st.session_state.get("active_view")

    if current_view in valid_keys and (dashboard_mode_requested() or current_view != "life"):
        params.update({"view": current_view, "mode": "dashboard"})
        params.update(active_goal_params())
        params.update(selection_state_params())
        detail = query_param_value("detail")
        if current_view == "details" and detail:
            params["detail"] = detail
    return f"/?{urlencode(params)}"


def render_top_language_toggle() -> None:
    language = current_language()
    en_active = " active" if language == "en" else ""
    ko_active = " active" if language == "ko" else ""
    en_href = escape(language_toggle_href("en"), quote=True)
    ko_href = escape(language_toggle_href("ko"), quote=True)
    st.markdown(
        f"""
        <nav class="top-language-toggle" aria-label="Language switcher">
            <span class="language-toggle-mark" aria-hidden="true">Aa</span>
            <a class="{en_active.strip()}" href="{en_href}" target="_top" title="Switch to English" aria-label="Switch to English">EN</a>
            <a class="{ko_active.strip()}" href="{ko_href}" target="_top" title="한국어로 전환" aria-label="한국어로 전환">한</a>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def render_nora_ontology(active_key: str) -> None:
    language = current_language()
    step_nodes = []
    for step in NORA_ONTOLOGY_STEPS:
        detail = step["detail_ko"] if language == "ko" else step["detail_en"]
        step_nodes.append(
            f'<div class="nora-node" role="button" tabindex="0" title="{escape(detail, quote=True)}" '
            f'style="--nora-color: {escape(step["color"])};">'
            f'<div class="nora-glyph">{escape(step["glyph"])}</div>'
            f'<strong>{ui_html(step["label"])}</strong>'
            f'<span>{ui_html(step["tag"])}</span>'
            f'<div class="nora-detail">{escape(detail)}</div>'
            '</div>'
        )

    module_links = []
    for label, view in NORA_MODULE_MAP:
        active_class = " active" if view == active_key else ""
        href = escape(app_view_href(view), quote=True)
        module_links.append(
            f'<a class="nora-module{active_class}" href="{href}" target="_self" title="{ui_html(label)}">{ui_html(label)}</a>'
        )

    summary_label = "NORA Flow" if language == "en" else "NORA 흐름"
    summary_path = "Goal → Plan → Situation" if language == "en" else "목표 → 플랜 → 상황"
    ontology_html = (
        f'<details class="nora-ontology nora-ontology-minimal" aria-label="{ui_html("NORA Ontology")}">'
        '<summary>'
        f'<b>{escape(summary_label)}</b>'
        f'<span>{escape(summary_path)}</span>'
        '</summary>'
        '<div class="nora-ontology-body">'
        '<div class="nora-ontology-caption">'
        f'{ui_html("NORA starts with the customer purpose, then checks the plan and current situation before any model.")}'
        f'<br>{ui_html("Hover or click each visual node to read its role.")}'
        '</div>'
        f'<div class="nora-path">{"".join(step_nodes)}</div>'
        f'<div class="nora-modules">{"".join(module_links)}</div>'
        '</div>'
        '</details>'
    )
    st.markdown(ontology_html, unsafe_allow_html=True)


def app_view_link(view: str, label: str) -> str:
    return f"[{label}]({app_view_href(view)})"


def build_ai_coach_linked_guidance(
    context: dict[str, Any],
    readiness: dict[str, Any],
) -> list[dict[str, str]]:
    portfolio = context["portfolio"]
    holdings = portfolio.get("holdings", [])
    base_currency = portfolio.get("base_currency", "USD")
    personal = context.get("personal") or {}
    scenario = context.get("scenario")
    diary = context.get("diary", [])
    gain_loss = portfolio_gain_loss_summary(holdings)

    if not holdings:
        portfolio_status = "Needs holdings"
        portfolio_advice = "Add stocks first, then enter shares and average purchase price so the coach can compare cost basis with current value."
    elif gain_loss["unrealized_gain"] is None:
        portfolio_status = "Needs purchase prices"
        portfolio_advice = "Enter average purchase price for each holding to unlock personal unrealized P/L and return analysis."
    else:
        portfolio_status = (
            f"{fmt_signed_money(gain_loss['unrealized_gain'], base_currency)} "
            f"({float(gain_loss['unrealized_return_pct']):+.1f}%)"
        )
        if float(gain_loss["unrealized_gain"]) >= 0:
            portfolio_advice = "Compare gains with concentration, beta, and cash-flow capacity before treating performance as readiness."
        else:
            portfolio_advice = "Separate market drawdown from life liquidity; review whether cash flow can absorb the current unrealized loss."

    if personal:
        health = float(personal.get("financial_health_score") or 0)
        emergency = float(personal.get("emergency_months") or 0)
        surplus = float(personal.get("monthly_surplus") or 0)
        personal_status = f"Health {health:.1f}/100"
        if emergency < 3:
            personal_advice = "Emergency reserve is the first readiness checkpoint before adding investment risk."
        elif surplus <= 0:
            personal_advice = "Monthly cash flow should be stabilized before using portfolio gains or losses as the main signal."
        else:
            personal_advice = "Use surplus, emergency reserve, and DTI together with portfolio P/L for investment readiness."
    else:
        personal_status = "Needs baseline"
        personal_advice = "Complete Personal Finance once so the coach can connect risk capacity with portfolio behavior."

    if scenario:
        scenario_delta = float(scenario.get("portfolio", {}).get("scenario_delta_pct") or 0)
        scenario_status = f"Latest scenario {scenario_delta:+.1f}%"
        scenario_advice = "Ask the coach to compare this stress result with emergency fund, P/L, and current portfolio exposure."
    else:
        scenario_status = "Needs scenario"
        scenario_advice = "Run one what-if scenario so the coach can reason about downside, FX, rate, income, and expense shocks."

    diary_status = f"{len(diary)} saved entr{'y' if len(diary) == 1 else 'ies'}"
    if diary:
        diary_advice = "Use diary memory to compare today's decision context with prior notes and next actions."
    else:
        diary_advice = "Save the Current Situation Report so the coach has a memory checkpoint for future review."

    details_status = "Formulas ready"
    details_advice = "Open Calculation Details when you need the formula, assumption, or limit behind a coach answer."

    return [
        {
            "title": "Portfolio P/L",
            "view": "portfolio",
            "status": portfolio_status,
            "advice": portfolio_advice,
            "question": "Use my portfolio cost basis, unrealized P/L, current value, and risk metrics to explain my investment readiness.",
        },
        {
            "title": "Personal Finance",
            "view": "finance",
            "status": personal_status,
            "advice": personal_advice,
            "question": "Connect my personal finance baseline with my portfolio risk and tell me what readiness issue matters most.",
        },
        {
            "title": "Scenario Stress",
            "view": "scenario",
            "status": scenario_status,
            "advice": scenario_advice,
            "question": "Use my latest what-if scenario to explain the safest next review step.",
        },
        {
            "title": "Diary Report",
            "view": "diary",
            "status": diary_status,
            "advice": diary_advice,
            "question": "Use my Current Situation Report and diary memory to summarize what I should review next.",
        },
        {
            "title": "Calculation Details",
            "view": "details",
            "status": details_status,
            "advice": details_advice,
            "question": "Explain the formulas and assumptions behind my current portfolio P/L, readiness, and risk signals.",
        },
    ]


def format_ai_coach_direct_links(
    context: dict[str, Any],
    readiness: dict[str, Any],
) -> str:
    linked_items = build_ai_coach_linked_guidance(context, readiness)
    rows = [
        f"- {app_view_link(item['view'], item['title'])}: {item['status']} - {item['advice']}"
        for item in linked_items
    ]
    return "### Direct App Links\n" + "\n".join(rows)


def render_mobile_ai_coach_deck(context: dict[str, Any], readiness: dict[str, Any]) -> None:
    portfolio = context["portfolio"]
    personal = context.get("personal") or {}
    missing = context.get("missing", [])
    holdings = portfolio.get("holdings", [])
    base_currency = portfolio.get("base_currency", "USD")
    gain_loss = portfolio_gain_loss_summary(holdings)
    pnl_text = (
        "Needs cost basis"
        if gain_loss.get("unrealized_gain") is None
        else fmt_signed_money(gain_loss.get("unrealized_gain"), base_currency)
    )
    pnl_class = mobile_signed_class(gain_loss.get("unrealized_gain"))
    health_text = (
        "Missing"
        if not personal
        else f"{float(personal.get('financial_health_score') or 0):.1f}/100"
    )
    next_needed = missing[0] if missing else "Ready for focused question"
    scenario_status = "Ready" if context.get("scenario") else "Run once"

    st.markdown(
        f"""
        <div class="mobile-only-deck">
            <div class="mobile-focus-card">
                <h3>Mobile AI Coach Brief</h3>
                <p>Use this as the phone-first control panel: readiness, missing context, portfolio P/L, and the next question to ask.</p>
            </div>
            <div class="mobile-card-grid">
                <div class="mobile-card"><div class="eyebrow">Readiness</div><div class="value">{escape(readiness['label'])}</div><span class="label">{readiness['score']:.0f}/100 rule-based</span></div>
                <div class="mobile-card"><div class="eyebrow">Next Input</div><div class="value">{escape(next_needed)}</div><span class="label">Fill this first</span></div>
                <div class="mobile-card"><div class="eyebrow">Portfolio P/L</div><div class="value {pnl_class}">{escape(pnl_text)}</div><span class="label">{len(holdings)} holding(s)</span></div>
                <div class="mobile-card"><div class="eyebrow">Finance</div><div class="value">{escape(health_text)}</div><span class="label">Scenario {escape(scenario_status)}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def detect_ai_coach_intent(question: str) -> str:
    q = question.lower()
    if any(token in q for token in ("ready", "readiness", "invest", "투자", "준비")):
        return "readiness"
    if any(token in q for token in ("risk", "위험", "beta", "volatility", "correlation", "diversification")):
        return "risk"
    if any(token in q for token in ("scenario", "what if", "shock", "rate", "fx", "환율", "금리", "시나리오")):
        return "scenario"
    if any(token in q for token in ("diary", "memory", "remember", "지난", "기억", "메모리")):
        return "memory"
    if any(token in q for token in ("privacy", "legal", "f-1", "visa", "비자", "법", "개인정보")):
        return "caution"
    return "overview"


def compact_text(value: Any, max_chars: int = 360) -> str:
    text = str(value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def clean_restored_json_value(value: Any, max_depth: int = 3) -> Any:
    if max_depth <= 0:
        return compact_text(value, 300)
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in list(value.items())[:40]:
            cleaned[compact_text(key, 80)] = clean_restored_json_value(item, max_depth - 1)
        return cleaned
    if isinstance(value, list):
        return [clean_restored_json_value(item, max_depth - 1) for item in value[:100]]
    if isinstance(value, str):
        return compact_text(value, 1200)
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return compact_text(value, 300)


def clean_restored_diary_entries(restored: Any) -> list[dict[str, Any]]:
    if not isinstance(restored, list):
        raise ValueError("The uploaded diary file must contain a list of entries.")
    if len(restored) > MAX_DIARY_RESTORE_ENTRIES:
        raise ValueError(f"Diary restore is limited to {MAX_DIARY_RESTORE_ENTRIES} entries.")

    cleaned_entries: list[dict[str, Any]] = []
    for entry in restored:
        if not isinstance(entry, dict):
            raise ValueError("Each diary entry must be a JSON object.")
        cleaned_entries.append(
            {
                "time": compact_text(entry.get("time", "Restored"), 80),
                "mood": compact_text(entry.get("mood", "Restored"), 40),
                "note": compact_text(entry.get("note", ""), 1800),
                "next_action": compact_text(entry.get("next_action", ""), 600),
                "base_currency": compact_text(entry.get("base_currency", "USD"), 12),
                "usdkrw": clean_restored_json_value(entry.get("usdkrw")),
                "fx_source": compact_text(entry.get("fx_source", ""), 80),
                "fx_date": compact_text(entry.get("fx_date", ""), 40),
                "portfolio": clean_restored_json_value(entry.get("portfolio", {})),
                "risk": clean_restored_json_value(entry.get("risk")),
                "complementarity": clean_restored_json_value(entry.get("complementarity")),
                "personal_finance": clean_restored_json_value(entry.get("personal_finance", {})),
            }
        )
    return cleaned_entries


def safe_float(value: Any, digits: int = 4) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return round(numeric, digits)


def build_verified_ai_context(
    context: dict[str, Any],
    readiness: dict[str, Any],
    include_diary_text: bool,
) -> dict[str, Any]:
    portfolio = context["portfolio"]
    risk = portfolio.get("risk")
    comp = portfolio.get("complementarity")
    scenario = context.get("scenario")
    diary_entries = context.get("diary", [])[-3:]

    return {
        "purpose": (
            "Educational financial reasoning context for ToxiGuard-NORA AI Coach. "
            "Do not treat this as financial, legal, tax, or immigration advice."
        ),
        "readiness": {
            "label": readiness["label"],
            "score": safe_float(readiness["score"], 1),
            "rule_reasons": readiness["reasons"][:8],
        },
        "personal_finance": context.get("personal") or {},
        "portfolio": {
            "base_currency": portfolio.get("base_currency", "USD"),
            "total_value": safe_float(portfolio.get("total_value"), 2),
            "weighted_beta": safe_float(portfolio.get("weighted_beta"), 3),
            "valuation_score_pct": safe_float(portfolio.get("valuation_score"), 2),
            "holdings": [
                {
                    "symbol": item.get("symbol"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "shares": safe_float(item.get("shares"), 4),
                    "current_price": safe_float(item.get("price"), 4),
                    "purchase_price": safe_float(item.get("purchase_price"), 4),
                    "base_weight_pct": safe_float(float(item.get("base_weight", 0)) * 100, 2),
                    "analysis_weight_pct": safe_float(float(item.get("analysis_weight", 0)) * 100, 2),
                    "unrealized_gain_base": safe_float(item.get("base_unrealized_gain"), 2),
                    "unrealized_return_pct": safe_float(item.get("unrealized_return_pct"), 2),
                    "valuation_status": item.get("valuation_status"),
                }
                for item in portfolio.get("holdings", [])[:10]
            ],
            "gain_loss_summary": portfolio_gain_loss_summary(portfolio.get("holdings", [])),
            "risk_summary": None
            if not risk
            else {
                "annualized_risk_pct": safe_float(float(risk["annual_vol"]) * 100, 2),
                "expected_annual_return_pct": safe_float(float(risk["annual_return"]) * 100, 2),
                "diversification_benefit_daily_pct": safe_float(float(risk["diversification_benefit"]) * 100, 4),
            },
            "complementarity_summary": None
            if not comp
            else {
                "score": safe_float(comp.get("complementarity_score"), 1),
                "average_pair_correlation": safe_float(comp.get("average_pair_correlation"), 3),
                "best_offset_pair": list(comp.get("best_offset_pair", []))[:3],
                "highest_co_movement_pair": list(comp.get("highest_co_movement_pair", []))[:3],
            },
        },
        "scenario": None
        if not scenario
        else {
            "inputs": scenario.get("inputs", {}),
            "portfolio": scenario.get("portfolio", {}),
            "interpretation": scenario.get("interpretation", []),
        },
        "diary_memory": [
            {
                "time": entry.get("time"),
                "mood": entry.get("mood"),
                "next_action": compact_text(entry.get("next_action"), 220),
                "note": compact_text(entry.get("note"), 320) if include_diary_text else "[hidden unless user opts in]",
            }
            for entry in diary_entries
        ],
        "missing_inputs": context.get("missing", []),
        "linked_app_guidance": [
            {
                "section": item["title"],
                "app_view": item["view"],
                "status": item["status"],
                "coach_hint": item["advice"],
                "suggested_question": item["question"],
            }
            for item in build_ai_coach_linked_guidance(context, readiness)
        ],
    }


VERIFIED_AI_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "short_answer",
        "evidence",
        "assumptions",
        "missing_inputs",
        "risk_flags",
        "next_safe_step",
        "caution",
        "confidence",
    ],
    "properties": {
        "short_answer": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "missing_inputs": {"type": "array", "items": {"type": "string"}},
        "risk_flags": {"type": "array", "items": {"type": "string"}},
        "next_safe_step": {"type": "string"},
        "caution": {"type": "string"},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
    },
}


VERIFIED_AI_SYSTEM_PROMPT = """
You are the ToxiGuard-NORA Verified AI Model Layer.
Your job is educational financial reasoning, not financial advice.

Rules:
- Do not give buy, sell, hold, short, long, or target-price instructions.
- Do not guarantee returns or predict certainty.
- Do not provide legal, tax, accounting, immigration, or professional advice.
- If the user asks about F-1, work authorization, monetization, or company formation, give only general caution and tell them to consult the DSO and qualified counsel.
- Ground every answer in the provided ToxiGuard-NORA context.
- Use linked_app_guidance to point the user toward the Portfolio, Personal Finance, Scenario, Diary, or Calculation Details view when relevant.
- If data is missing, say so clearly.
- Keep the answer useful on mobile: concise, structured, and direct.
- Return only JSON matching the requested schema.
"""


def extract_response_text(response_json: dict[str, Any]) -> str:
    if response_json.get("output_text"):
        return str(response_json["output_text"]).strip()

    parts: list[str] = []
    for item in response_json.get("output", []) or []:
        for content in item.get("content", []) or []:
            if isinstance(content, dict):
                if "text" in content:
                    parts.append(str(content["text"]))
                elif content.get("type") == "output_text" and "value" in content:
                    parts.append(str(content["value"]))
    return "\n".join(parts).strip()


def parse_json_object(text: str) -> dict[str, Any]:
    clean_text = text.strip()
    if clean_text.startswith("```"):
        clean_text = clean_text.strip("`")
        clean_text = clean_text.replace("json\n", "", 1).strip()
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        start = clean_text.find("{")
        end = clean_text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(clean_text[start : end + 1])
        raise


def validate_verified_ai_payload(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in VERIFIED_AI_SCHEMA["required"]:
        if key not in payload:
            issues.append(f"Missing required field: {key}")

    combined = " ".join(
        str(payload.get(key, ""))
        for key in ("short_answer", "next_safe_step", "caution")
    ).lower()
    prohibited_patterns = (
        "you should buy",
        "you should sell",
        "i recommend buying",
        "i recommend selling",
        "guaranteed return",
        "guaranteed profit",
    )
    if any(pattern in combined for pattern in prohibited_patterns):
        issues.append("Model response included disallowed investment-directive language.")

    if "educational" not in str(payload.get("caution", "")).lower():
        issues.append("Caution field must clearly state educational use.")
    return issues


def format_verified_ai_payload(payload: dict[str, Any], model_name: str) -> str:
    def list_block(items: Any, fallback: str) -> str:
        if not items:
            return f"- {fallback}"
        return "\n".join(f"- {compact_text(item, 420)}" for item in items)

    return f"""### Short Answer
{compact_text(payload.get("short_answer"), 900)}

### Evidence From Your Data
{list_block(payload.get("evidence"), "No app evidence was available.")}

### Assumptions
{list_block(payload.get("assumptions"), "No assumptions were stated.")}

### Missing Inputs
{list_block(payload.get("missing_inputs"), "No major missing inputs were flagged.")}

### Risk Flags
{list_block(payload.get("risk_flags"), "No major risk flags were detected from available context.")}

### Next Safe Step
{compact_text(payload.get("next_safe_step"), 600)}

### Caution
{compact_text(payload.get("caution"), 700)}

_Verified AI layer: {model_name} | confidence: {payload.get("confidence", "medium")}._
"""


def call_verified_openai_model(
    question: str,
    context: dict[str, Any],
    readiness: dict[str, Any],
    include_diary_text: bool,
) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    model_context = build_verified_ai_context(context, readiness, include_diary_text)
    payload = {
        "model": OPENAI_MODEL,
        "input": [
            {"role": "system", "content": VERIFIED_AI_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_question": question,
                        "toxiguard_nora_context": model_context,
                        "required_output_style": "mobile-friendly structured JSON",
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "reasoning": {"effort": OPENAI_REASONING_EFFORT},
        "text": {
            "format": {
                "type": "json_schema",
                "name": "toxiguard_nora_verified_ai_response",
                "strict": True,
                "schema": VERIFIED_AI_SCHEMA,
            }
        },
        "max_output_tokens": 1400,
    }
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=45,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI API returned {response.status_code}: {compact_text(response.text, 220)}")

    response_json = response.json()
    response_text = extract_response_text(response_json)
    if not response_text:
        raise RuntimeError("OpenAI API returned an empty response.")

    model_payload = parse_json_object(response_text)
    validation_issues = validate_verified_ai_payload(model_payload)
    if validation_issues:
        raise RuntimeError("Verified AI response failed validation: " + "; ".join(validation_issues))

    return format_verified_ai_payload(model_payload, OPENAI_MODEL)


def ai_coach_response(question: str) -> str:
    context = ai_coach_context_snapshot()
    readiness = ai_coach_readiness(context)
    intent = detect_ai_coach_intent(question)
    portfolio = context["portfolio"]
    personal = context["personal"]
    scenario = context["scenario"]
    diary = context["diary"]
    missing = context["missing"]
    base_currency = portfolio["base_currency"]

    evidence: list[str] = []
    if personal:
        evidence.extend(
            [
                f"Financial health score: {float(personal.get('financial_health_score') or 0):.1f}/100.",
                f"Emergency fund: {float(personal.get('emergency_months') or 0):.1f} months.",
                f"Monthly surplus: {fmt_money(float(personal.get('monthly_surplus') or 0))}.",
                f"Debt-to-income: {float(personal.get('debt_to_income') or 0) * 100:.1f}%.",
            ]
        )
    if portfolio["holdings"]:
        gain_loss = portfolio_gain_loss_summary(portfolio["holdings"])
        evidence.append(f"Portfolio value: {fmt_money(portfolio['total_value'], base_currency)}.")
        evidence.append(f"Holdings tracked: {len(portfolio['holdings'])}.")
        if gain_loss["unrealized_gain"] is not None:
            evidence.append(
                f"Unrealized P/L: {fmt_signed_money(gain_loss['unrealized_gain'], base_currency)} "
                f"({float(gain_loss['unrealized_return_pct']):+.1f}%)."
            )
        if portfolio["weighted_beta"] is not None:
            evidence.append(f"Weighted beta: {fmt_number(portfolio['weighted_beta'])}.")
        if portfolio["valuation_score"] is not None:
            evidence.append(f"Valuation score: {float(portfolio['valuation_score']):+.1f}%.")
    if portfolio["risk"]:
        evidence.append(f"Annualized portfolio risk: {float(portfolio['risk']['annual_vol']) * 100:.1f}%.")
    if scenario:
        evidence.append(f"Last scenario portfolio move: {float(scenario['inputs']['portfolio_change_pct']):+.0f}%.")
        evidence.append(f"Last scenario result: {float(scenario['portfolio']['scenario_delta_pct']):+.1f}%.")
    if diary:
        latest = diary[-1]
        evidence.append(f"Latest diary mood: {latest.get('mood', 'N/A')}.")
        if latest.get("next_action"):
            evidence.append(f"Latest next action: {latest.get('next_action')}.")

    if intent == "readiness":
        short = (
            f"Your current investment readiness is **{readiness['label']}** "
            f"with a rule-based score of **{readiness['score']:.0f}/100**. "
            "This is a preparation signal, not a buy/sell recommendation."
        )
        next_step = "Complete the missing inputs, then run a downside scenario before making any real decision."
    elif intent == "risk":
        short = (
            "The main risk view should combine life capacity, portfolio volatility, beta, and diversification. "
            f"Current readiness label: **{readiness['label']}**."
        )
        next_step = "Check Portfolio Risk and Scenario together; risk is weaker when life liquidity and portfolio concentration both look strained."
    elif intent == "scenario":
        if scenario:
            short = (
                "The latest scenario packet is available and can be interpreted now. "
                f"It shows a **{float(scenario['portfolio']['scenario_delta_pct']):+.1f}%** portfolio-level scenario change."
            )
        else:
            short = "No scenario packet is available yet. Run the Scenario tab once, then ask this again."
        next_step = "Use Scenario to test income, expenses, market drawdown, FX, and rate pressure together."
    elif intent == "memory":
        short = (
            f"I found **{len(diary)} diary entr{'y' if len(diary) == 1 else 'ies'}** for memory-style reflection."
            if diary
            else "There is no diary memory yet. Save a Financial Diary snapshot first."
        )
        next_step = "Save a diary entry after each major review so future AI can compare your thinking over time."
    elif intent == "caution":
        short = (
            "Use this prototype as educational analysis only. For F-1 venture activity, monetization, work authorization, "
            "data licensing, and legal boundaries should be reviewed with the DSO and qualified counsel."
        )
        next_step = "Keep sensitive data out of the public prototype and document privacy, data source, and user consent boundaries."
    else:
        short = (
            f"I can summarize your current financial reasoning context. Rule-based readiness is "
            f"**{readiness['label']} ({readiness['score']:.0f}/100)**."
        )
        next_step = "Ask about readiness, risk, scenario, or memory to get a more focused answer."

    evidence_text = "\n".join(f"- {item}" for item in evidence) if evidence else "- Not enough app data has been entered yet."
    assumptions_text = "\n".join(
        [
            "- This response uses only data currently available inside this Streamlit session.",
            "- This local response is rule-based unless the verified OpenAI model layer is enabled.",
            "- Scores are educational heuristics and should be treated as prompts for review.",
        ]
    )
    missing_text = "\n".join(f"- {item}" for item in missing) if missing else "- No major missing context detected for this prototype."
    reason_text = "\n".join(f"- {item}" for item in readiness["reasons"][:6])
    direct_links_text = format_ai_coach_direct_links(context, readiness)

    return f"""### Short Answer
{short}

### Evidence From Your Data
{evidence_text}

### Rule-Based Reasoning
{reason_text}

### Assumptions
{assumptions_text}

### Missing Inputs
{missing_text}

{direct_links_text}

### Next Safe Step
{next_step}

### Caution
This is educational scenario reasoning only. It is not financial, investment, legal, tax, or immigration advice.
"""


def verified_or_rule_based_ai_response(question: str, use_verified_model: bool, include_diary_text: bool) -> str:
    context = ai_coach_context_snapshot()
    readiness = ai_coach_readiness(context)
    if use_verified_model and OPENAI_API_KEY:
        try:
            verified_answer = call_verified_openai_model(question, context, readiness, include_diary_text)
            return f"{verified_answer}\n\n{format_ai_coach_direct_links(context, readiness)}"
        except Exception as exc:
            fallback = ai_coach_response(question)
            return (
                f"{fallback}\n\n"
                f"### Verified AI Model Status\n"
                f"- The app fell back to the rule-based coach because the verified model layer could not complete safely.\n"
                f"- Reason: {compact_text(exc, 260)}"
            )
    return ai_coach_response(question)


def render_ai_coach_linked_guidance(
    context: dict[str, Any],
    readiness: dict[str, Any],
) -> str | None:
    st.subheader("Linked Coach Guidance")
    st.caption(
        "These cards are generated from Portfolio, Personal Finance, Scenario, Diary, and Calculation Details. "
        "Open the source view or ask AI Coach with that exact context."
    )
    pending_question = None
    linked_items = build_ai_coach_linked_guidance(context, readiness)
    for start in range(0, len(linked_items), 2):
        cols = st.columns(2, gap="medium")
        for idx, item in enumerate(linked_items[start : start + 2], start=start):
            with cols[idx - start]:
                st.markdown(
                    f"""
                    <div class="linked-coach-card">
                        <div class="eyebrow">Linked source</div>
                        <h3>{escape(item['title'])}</h3>
                        <div class="status">{escape(item['status'])}</div>
                        <p>{escape(item['advice'])}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                open_col, ask_col = st.columns(2)
                with open_col:
                    st.button(
                        "Open",
                        key=f"linked_open_{item['view']}_{idx}",
                        width="stretch",
                        on_click=set_active_nav_key,
                        args=(item["view"],),
                    )
                with ask_col:
                    if st.button("Ask Coach", key=f"linked_ask_{item['view']}_{idx}", width="stretch"):
                        pending_question = item["question"]
    return pending_question


def queue_ai_coach_question(question: str) -> None:
    st.session_state.pending_ai_question = question
    set_active_nav_key("ai")


def queue_current_report_ai_question() -> None:
    report = st.session_state.get("diary_current_report", "")
    st.session_state.pending_ai_question = (
        "Use this Current Situation Report plus the live Portfolio and Personal Finance context "
        "to give a linked readiness review. Report text: "
        f"{compact_text(report, 1800)}"
    )
    set_active_nav_key("ai")


def render_ai_coach() -> None:
    context = ai_coach_context_snapshot()
    readiness = ai_coach_readiness(context)
    portfolio = context["portfolio"]
    personal = context["personal"]
    diary = context["diary"]
    score = readiness["score"]
    label = readiness["label"]
    health_text = (
        f"{float(personal.get('financial_health_score') or 0):.1f}/100"
        if personal
        else "Missing"
    )
    portfolio_text = (
        fmt_money(portfolio["total_value"], portfolio["base_currency"])
        if portfolio["holdings"]
        else "Missing"
    )

    st.markdown(
        f"""
        <div class="ai-coach-hero">
            <h1>AI Coach</h1>
            <p>Ask ToxiGuard-NORA direct questions about readiness, risk, scenarios, and memory. This beta uses transparent rules first, then can later connect to an LLM API.</p>
            <div class="ai-coach-strip">
                <div class="ai-coach-signal"><b>{escape(label)}</b><span>Readiness {score:.0f}/100</span></div>
                <div class="ai-coach-signal"><b>{escape(health_text)}</b><span>Personal finance</span></div>
                <div class="ai-coach-signal"><b>{escape(portfolio_text)}</b><span>Portfolio context</span></div>
                <div class="ai-coach-signal"><b>{len(diary)}</b><span>Diary memories</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="coach-disclaimer">
            Verified AI Coach beta: educational reasoning only. If enabled, a reasoning model answers from structured ToxiGuard-NORA context and a local validator checks boundaries before display.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_mobile_ai_coach_deck(context, readiness)

    with st.expander("Verified AI Model Settings", expanded=False):
        if OPENAI_API_KEY:
            st.success(f"OPENAI_API_KEY is configured. Model: {OPENAI_MODEL}.")
        else:
            st.warning(
                "OPENAI_API_KEY is not configured, so AI Coach will use the local rule-based answer. "
                "Add OPENAI_API_KEY in Streamlit Secrets to enable verified model responses."
            )
        st.toggle(
            "Use verified OpenAI reasoning model",
            key="use_verified_ai_model",
            disabled=not bool(OPENAI_API_KEY),
            help="When enabled, structured app context is sent to OpenAI's Responses API and then validated locally before display.",
        )
        st.checkbox(
            "Include diary note text in model context",
            key="include_diary_text_for_ai",
            disabled=not bool(OPENAI_API_KEY) or not st.session_state.get("use_verified_ai_model", False),
            help="Leave off to send only diary count, mood, and next-action summaries.",
        )
        st.caption(
            "Privacy note: do not enter bank account numbers, tax IDs, passwords, or confidential records. "
            "Use this public prototype with minimal, non-sensitive examples."
        )

    pending_question = st.session_state.get("pending_ai_question")
    if pending_question:
        st.session_state.pending_ai_question = None

    if not st.session_state.ai_coach_messages:
        st.session_state.ai_coach_messages.append(
            {
                "role": "assistant",
                "content": (
                    "I am ready to review investment readiness, portfolio risk, scenario stress, and diary memory. "
                    "Use the linked cards below, start with a quick question, or type your own."
                ),
            }
        )

    linked_question = render_ai_coach_linked_guidance(context, readiness)
    if linked_question:
        pending_question = linked_question

    st.subheader("Quick Questions")
    quick_questions = [
        "Am I investment ready?",
        "Explain my biggest risk.",
        "What happens in my latest scenario?",
        "What should I track next?",
        "Summarize my diary memory.",
        "What privacy or F-1 caution matters?",
    ]
    quick_cols = st.columns(2)
    for idx, question in enumerate(quick_questions):
        with quick_cols[idx % 2]:
            if st.button(question, key=f"ai_quick_{idx}", width="stretch"):
                pending_question = question

    typed_question = st.chat_input("Ask ToxiGuard-NORA AI Coach about readiness, risk, scenario, or memory")
    if typed_question:
        pending_question = typed_question

    if pending_question:
        st.session_state.ai_coach_messages.append({"role": "user", "content": pending_question})
        st.session_state.ai_coach_messages.append(
            {
                "role": "assistant",
                "content": verified_or_rule_based_ai_response(
                    pending_question,
                    st.session_state.get("use_verified_ai_model", False),
                    st.session_state.get("include_diary_text_for_ai", False),
                ),
            }
        )

    reset_col, save_col = st.columns([1, 1])
    with reset_col:
        if st.button("Reset AI Coach Chat", width="stretch"):
            st.session_state.ai_coach_messages = []
            st.rerun()
    with save_col:
        if st.button("Save AI Summary to Diary", width="stretch"):
            last_answer = next(
                (
                    message["content"]
                    for message in reversed(st.session_state.ai_coach_messages)
                    if message["role"] == "assistant"
                ),
                "",
            )
            if last_answer:
                st.session_state.financial_diary.append(
                    build_financial_snapshot(
                        "AI Coach summary saved from chat.",
                        "Planning",
                        last_answer[:600],
                    )
                )
                st.success("AI Coach summary saved to Financial Diary memory for this session.")

    st.subheader("Conversation")
    for message in st.session_state.ai_coach_messages[-8:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def ai_reasoning_readiness_tab() -> None:
    render_ai_coach()

    with st.expander("AI Reasoning Product Thesis", expanded=False):
        st.write(
            """
            AI interfaces are moving toward voice, agents, and continuous assistance. A future user may ask:
            "Can I absorb this risk?", "What changes if rates rise?", or "What did I decide last time?"
            ToxiGuard-NORA prepares the structured context needed to answer those questions responsibly.
            """
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Core Position", "Reasoning, not stock picking", "#0f766e")
        with c2:
            metric_card("User Value", "Understand trade-offs", "#1d4ed8")
        with c3:
            metric_card("Launch Stage", "Educational beta", "#92400e")

        st.subheader("AI Coach Foundations")
        st.dataframe(
            [
                {"Layer": "Scenario", "Current foundation": "What-if Scenario Lab", "Future question": "What if income falls, FX moves, or rates rise?"},
                {"Layer": "Portfolio", "Current foundation": "Valuation score, beta, covariance, correlation", "Future question": "Where is my risk concentrated?"},
                {"Layer": "Personal finance", "Current foundation": "Surplus, emergency fund, DTI, health score", "Future question": "Can my life absorb this investment risk?"},
                {"Layer": "Memory", "Current foundation": "Financial Diary JSON", "Future question": "How has my thinking changed over time?"},
                {"Layer": "Explainability", "Current foundation": "Calculation Details", "Future question": "Which formula and assumption produced this signal?"},
            ],
            hide_index=True,
            width="stretch",
        )

        st.subheader("Responsible Boundaries")
        st.markdown(
            """
            - Keep outputs educational and scenario-based; avoid buy/sell instructions.
            - Do not collect sensitive real account data in this public prototype.
            - Review data licenses before commercial use.
            - For F-1 venture exploration, treat this as prototype validation and consult the DSO/immigration counsel before monetization.
            - Make every future AI answer show assumptions, evidence, limitations, and missing data.
            """
        )


def calculation_details_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Calculation Details</h1>
            <div class="hero-muted">Review the formulas, data inputs, assumptions, and interpretation logic behind ToxiGuard-NORA.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "This section is designed for transparency. It explains how the app creates each analytical signal, "
        "so users can understand the assumptions instead of treating the output as a recommendation."
    )

    with st.expander("1. Stock Valuation Triangulation", expanded=True):
        st.markdown(
            """
            **Blended Fair Value** is the average of the valid valuation models available for each stock.

            - **Income Approach:** Gordon Growth Model when dividends are available; otherwise EPS capitalization.
            - **Asset Approach:** Graham Number = square root of `22.5 x EPS x Book Value per Share`.
            - **Market Approach:** `EPS x Peer Average P/E`.
            - **CAPM Required Return:** `Risk-Free Rate + Beta x Equity Risk Premium`; users can adjust these assumptions in Settings.
            - **Valuation Status:** if current price is more than 5% above fair value, it is marked Overvalued; if more than 5% below, Undervalued.
            """
        )
        if st.session_state.stocks:
            symbols = list(st.session_state.stocks.keys())
            selected = st.selectbox("Inspect a loaded stock", symbols, key="calc_stock_symbol")
            stock = st.session_state.stocks[selected]
            tri = stock.get("triangulation", {})
            st.dataframe(
                [
                    {"Input": "Current Price", "Value": stock_money(stock, stock.get("price"))},
                    {"Input": "EPS", "Value": stock_money(stock, float(stock.get("eps") or 0))},
                    {"Input": "Book Value / Share", "Value": stock_money(stock, float(stock.get("book_value") or 0))},
                    {"Input": "Dividend / Share", "Value": stock_money(stock, float(stock.get("dividend") or 0))},
                    {"Input": "Beta", "Value": fmt_number(stock.get("beta"))},
                    {"Input": "Risk-Free Rate", "Value": f"{float(stock.get('risk_free_rate') or macro_assumptions()[0]) * 100:.2f}%"},
                    {"Input": "Equity Risk Premium", "Value": f"{float(stock.get('equity_risk_premium') or macro_assumptions()[1]) * 100:.2f}%"},
                    {"Input": "CAPM Required Return", "Value": f"{float(stock.get('expected_return') or 0) * 100:.2f}%"},
                    {"Input": "Growth Rate", "Value": f"{float(stock.get('growth_rate') or 0) * 100:.1f}%"},
                    {"Input": "Peer Average P/E", "Value": fmt_number(stock.get("peer_average_pe"))},
                ],
                hide_index=True,
                width="stretch",
            )
            st.dataframe(
                [
                    {"Approach": "Income", "Model": tri.get("income_model", "N/A"), "Value": stock_money(stock, tri.get("income_value")) if tri.get("income_value") else "N/A"},
                    {"Approach": "Asset", "Model": "Graham Number", "Value": stock_money(stock, tri.get("asset_value")) if tri.get("asset_value") else "N/A"},
                    {"Approach": "Market", "Model": "Peer P/E", "Value": stock_money(stock, tri.get("market_value")) if tri.get("market_value") else "N/A"},
                    {"Approach": "Blended", "Model": f"{tri.get('valid_models', 0)} valid model(s)", "Value": stock_money(stock, stock.get("fair_price")) if stock.get("fair_price") else "N/A"},
                ],
                hide_index=True,
                width="stretch",
            )
        else:
            st.caption("Search stocks first to inspect live valuation inputs.")

    with st.expander("2. Portfolio Valuation Score", expanded=True):
        st.markdown(
            """
            The portfolio valuation score measures weighted upside or downside versus each holding's blended fair value.

            `Portfolio Valuation Score = sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight`

            Positive means the portfolio appears undervalued under the app assumptions. Negative means the portfolio appears overvalued.
            """
        )
        rows = portfolio_valuation_rows()
        if rows:
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.caption("Add holdings to the portfolio to see contribution details.")

    with st.expander("3. Personal Cost Basis and Unrealized Profit/Loss"):
        st.markdown(
            """
            Personal portfolio profit/loss compares the user's entered average purchase price with the current market price.

            `Cost Basis = Average Purchase Price x Shares`

            `Unrealized P/L = Current Market Value - Cost Basis`

            `Unrealized Return % = Unrealized P/L / Cost Basis x 100`

            Cost basis is optional. If purchase price is left at 0, the app does not estimate profit/loss for that holding.
            """
        )
        holdings = portfolio_holdings_snapshot()
        gain_loss = portfolio_gain_loss_summary(holdings)
        base_currency = st.session_state.get("portfolio_base_currency", "USD")
        if gain_loss["total_cost_basis"] is not None:
            st.dataframe(
                [
                    {"Metric": "Costed Holdings", "Value": f"{gain_loss['costed_holding_count']} of {gain_loss['total_holding_count']}"},
                    {"Metric": "Total Cost Basis", "Value": fmt_money(gain_loss["total_cost_basis"], base_currency)},
                    {"Metric": "Current Value of Costed Holdings", "Value": fmt_money(gain_loss["current_value_for_costed_holdings"], base_currency)},
                    {"Metric": "Unrealized P/L", "Value": fmt_signed_money(gain_loss["unrealized_gain"], base_currency)},
                    {"Metric": "Unrealized Return", "Value": f"{float(gain_loss['unrealized_return_pct']):+.1f}%"},
                ],
                hide_index=True,
                width="stretch",
            )
        else:
            st.caption("Enter purchase prices in Portfolio to calculate personal profit/loss.")

    with st.expander("4. Portfolio Risk and Diversification"):
        st.markdown(
            """
            Portfolio risk is calculated from daily return covariance.

            `Portfolio Variance = w' x Covariance Matrix x w`

            `Annualized Risk = Daily Portfolio Standard Deviation x sqrt(252)`

            The calculation uses the selected portfolio weighting mode. For mixed-currency portfolios, weights are calculated in the selected base currency, but daily price returns currently do not include FX return effects.
            """
        )
        risk = portfolio_risk_metrics()
        if risk:
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Metric": "Daily Portfolio SD", "Value": f"{risk['daily_vol'] * 100:.3f}%"},
                        {"Metric": "Annualized Portfolio Risk", "Value": f"{risk['annual_vol'] * 100:.1f}%"},
                        {"Metric": "Expected Annual Return", "Value": f"{risk['annual_return'] * 100:+.1f}%"},
                        {"Metric": "Daily Diversification Benefit", "Value": f"{risk['diversification_benefit'] * 100:.3f}%"},
                    ]
                ),
                hide_index=True,
                width="stretch",
            )
            st.markdown("**Weight Vector**")
            st.dataframe(risk["weights"].rename("Weight").to_frame().style.format("{:.2%}"), width="stretch")
            st.markdown("**Covariance Matrix**")
            st.dataframe(risk["covariance"].round(6), width="stretch")
            st.markdown("**Correlation Matrix**")
            st.dataframe(risk["correlation"].round(3), width="stretch")
        else:
            st.caption("At least two portfolio holdings with price history are needed.")

    with st.expander("5. Personal Finance Health Score"):
        st.markdown(
            """
            Personal Finance connects investment readiness with life-level financial health.

            - **Net Worth:** total assets minus total debt.
            - **Monthly Surplus:** income minus fixed expenses, variable expenses, and debt payments.
            - **Emergency Fund:** cash savings divided by monthly living expenses.
            - **Savings Rate:** monthly surplus divided by monthly income.
            - **Debt-to-Income:** monthly debt payment divided by monthly income.
            - **Financial Health Score:** weighted score from liquidity, debt, savings, goal progress, and risk capacity.
            - **No-Income Planning Score:** when income is zero, the app adds runway target, study months, and investment exposure checks.
            """
        )
        result = st.session_state.get("last_personal_finance_result")
        if result:
            st.dataframe(
                [
                    {"Metric": "Net Worth", "Value": fmt_money(float(result["net_worth"]))},
                    {"Metric": "Monthly Surplus", "Value": fmt_money(float(result["monthly_surplus"]))},
                    {"Metric": "Emergency Fund", "Value": f"{float(result['emergency_months']):.1f} months"},
                    {"Metric": "Savings Rate", "Value": f"{float(result['savings_rate']) * 100:.1f}%"},
                    {"Metric": "Debt-to-Income", "Value": f"{float(result['debt_to_income']) * 100:.1f}%"},
                    {"Metric": "Financial Health Score", "Value": f"{float(result['financial_health_score']):.1f}/100"},
                    {"Metric": "Planning Health Score", "Value": f"{float(result.get('planning_health_score') or 0):.1f}/100"},
                    {"Metric": "Runway Target", "Value": f"{float(result.get('required_runway_months') or 0):.1f} months"},
                    {"Metric": "Runway Gap", "Value": f"{float(result.get('runway_gap_months') or 0):+.1f} months"},
                    {"Metric": "Investment Exposure", "Value": f"{float(result.get('investment_exposure_ratio') or 0) * 100:.1f}%"},
                ],
                hide_index=True,
                width="stretch",
            )
        else:
            st.caption("Open the Personal Finance tab first to calculate a personal finance snapshot.")

    with st.expander("6. AI Reasoning and Scenario Layer"):
        st.markdown(
            """
            ToxiGuard-NORA is being prepared for future AI-assisted financial reasoning. The app should not ask AI
            to make unsupported investment recommendations. Instead, each future AI response should be grounded
            in structured app data.

            **Reasoning context should include:**

            - Portfolio holdings, weights, valuation score, beta, covariance, and correlation.
            - Personal finance readiness: surplus, emergency fund, savings rate, debt-to-income, and health score.
            - REIT exposure and interest-rate sensitivity.
            - Diary snapshots, notes, and next actions when the user chooses to restore them.
            - Macro assumptions such as risk-free rate, equity risk premium, and FX rate.

            The What-if Scenario Lab is the first working version of this layer. It turns user-selected shocks
            into a structured scenario packet that a future AI coach can explain.
            """
        )


def apply_advisor_client_to_finance(report: dict[str, Any]) -> None:
    client = report["client"]
    profile = client.profile
    st.session_state.update(
        {
            "pf_display_currency": client.currency,
            "pf_monthly_income": profile.monthly_income,
            "pf_monthly_savings_goal": profile.monthly_savings_goal,
            "pf_investment_risk_score": int(profile.investment_risk_score),
            "pf_fixed_expenses": profile.fixed_expenses,
            "pf_variable_expenses": profile.variable_expenses,
            "pf_monthly_debt_payment": profile.monthly_debt_payment,
            "pf_cash_savings": profile.cash_savings,
            "pf_taxable_investments": profile.taxable_investments,
            "pf_retirement_accounts": profile.retirement_accounts,
            "pf_real_estate_value": profile.real_estate_value,
            "pf_credit_card_debt": profile.credit_card_debt,
            "pf_student_loan": profile.student_loan,
            "pf_auto_loan": profile.auto_loan,
            "pf_mortgage": profile.mortgage,
            "pf_target_goal_amount": profile.target_goal_amount,
            "pf_current_goal_savings": profile.current_goal_savings,
            "pf_runway_target_months": profile.runway_target_months,
            "pf_study_months_remaining": profile.study_months_remaining,
            "last_personal_finance_profile": profile.__dict__,
            "last_personal_finance_result": report["result"],
        }
    )


def render_advisor_report_style() -> None:
    st.markdown(
        """
        <style>
        .advisor-report-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
            gap: 18px;
            align-items: start;
        }
        .advisor-client-card {
            border: 1px solid rgba(148, 163, 184, 0.34);
            border-radius: 8px;
            padding: 18px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.10);
        }
        .advisor-kicker {
            color: #0f766e;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .advisor-title {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 900;
            line-height: 1.05;
            margin-top: 6px;
        }
        .advisor-subtitle {
            color: #475569;
            font-size: 0.95rem;
            margin-top: 8px;
            line-height: 1.45;
        }
        .advisor-status-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }
        .advisor-chip {
            border-radius: 999px;
            padding: 7px 11px;
            background: #ecfeff;
            color: #164e63;
            font-size: 0.78rem;
            font-weight: 850;
        }
        .advisor-memory-card {
            border: 1px solid rgba(20, 184, 166, 0.24);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(15, 118, 110, 0.96), rgba(15, 23, 42, 0.96));
            color: #f8fafc;
            padding: 18px;
        }
        .advisor-memory-card h3 {
            margin: 0;
            color: #ffffff;
            font-size: 1rem;
        }
        .advisor-memory-card p {
            color: #dbeafe;
            line-height: 1.48;
            margin: 10px 0 0;
        }
        .advisor-action-list {
            margin: 0;
            padding-left: 18px;
            color: #e0f2fe;
        }
        .advisor-action-list li {
            margin: 8px 0;
        }
        @media (max-width: 900px) {
            .advisor-report-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_advisor_reports_tab() -> None:
    from advisor_report_engine import (
        all_clients_pdf_bytes,
        build_all_client_reports,
        client_report_pdf_bytes,
        label as advisor_label,
        money_text,
    )

    render_advisor_report_style()
    advisor_language = current_language()
    reports = build_all_client_reports(language=advisor_language)
    report_map = {report["client"].client_id: report for report in reports}
    score_columns = {
        "client": advisor_label("client", advisor_language),
        "name": advisor_label("name", advisor_language),
        "segment": advisor_label("segment", advisor_language),
        "status": advisor_label("status", advisor_language),
        "planning": advisor_label("planning_health", advisor_language),
        "runway": advisor_label("cash_runway", advisor_language),
        "goal": advisor_label("goal_progress", advisor_language),
        "exposure": advisor_label("investment_exposure", advisor_language),
        "portfolio": advisor_label("portfolio_quality", advisor_language),
    }

    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">{}</h1>
            <div class="hero-muted">{}</div>
        </div>
        """.format(
            ui_html("Advisor Reports"),
            ui_html("Review virtual clients through the ToxiGuard-NORA decision architecture and export PDF reports."),
        ),
        unsafe_allow_html=True,
    )
    st.caption(
        ui("These fictional reports use the existing Personal Finance engine plus a rule-based advisor layer. They are educational examples, not professional advice.")
    )

    score_rows = []
    for item in reports:
        client = item["client"]
        result = item["result"]
        score_rows.append(
            {
                score_columns["client"]: f"{client.client_id} {client.name.split()[0]}",
                score_columns["name"]: client.name,
                score_columns["segment"]: client.text("segment", advisor_language),
                score_columns["status"]: item["status"],
                score_columns["planning"]: float(result["planning_health_score"]),
                score_columns["runway"]: float(result["emergency_months"]),
                score_columns["goal"]: float(result["goal_progress"]) * 100,
                score_columns["exposure"]: float(result["investment_exposure_ratio"]) * 100,
                score_columns["portfolio"]: float(item["portfolio"]["score"]),
            }
        )
    score_df = pd.DataFrame(score_rows)

    overview_cols = st.columns([2, 1])
    with overview_cols[0]:
        st.altair_chart(
            alt.Chart(score_df)
            .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8)
            .encode(
                y=alt.Y(f"{score_columns['client']}:N", sort="-x", title=None),
                x=alt.X(
                    f"{score_columns['planning']}:Q",
                    scale=alt.Scale(domain=[0, 100]),
                    title=ui("Planning Health Score"),
                ),
                color=alt.Color(
                    f"{score_columns['status']}:N",
                    legend=alt.Legend(title=score_columns["status"]),
                ),
                tooltip=[
                    score_columns["name"],
                    score_columns["segment"],
                    alt.Tooltip(f"{score_columns['planning']}:Q", format=".1f"),
                    alt.Tooltip(f"{score_columns['runway']}:Q", format=".1f"),
                    alt.Tooltip(f"{score_columns['exposure']}:Q", format=".1f"),
                ],
            )
            .properties(height=330),
            width="stretch",
        )
    with overview_cols[1]:
        st.dataframe(
            score_df[
                [
                    score_columns["client"],
                    score_columns["status"],
                    score_columns["planning"],
                    score_columns["runway"],
                    score_columns["portfolio"],
                    score_columns["exposure"],
                ]
            ].round(1),
            hide_index=True,
            width="stretch",
        )

    selected_id = st.selectbox(
        ui("Select virtual client"),
        options=list(report_map.keys()),
        format_func=lambda value: f"{value} - {report_map[value]['client'].name} | {report_map[value]['client'].text('segment', advisor_language)}",
        key="advisor_selected_client",
    )
    report = report_map[selected_id]
    client = report["client"]
    result = report["result"]

    score_cards = "".join(
        "".join(
            line.strip()
            for line in portfolio_score_card_html(
                card["label"],
                card["value"],
                card["score"],
                card["detail"],
            ).splitlines()
        )
        for card in report["scorecards"]
    )
    actions_html = "".join(f"<li>{escape(action)}</li>" for action in report["actions"])
    st.markdown(
        f"""
        <div class="advisor-report-grid">
            <div class="advisor-client-card">
                <div class="advisor-kicker">{escape(client.client_id)} · {escape(client.text('segment', advisor_language))}</div>
                <div class="advisor-title">{escape(client.name)}</div>
                <div class="advisor-subtitle">{escape(client.text('situation', advisor_language))}</div>
                <div class="advisor-status-strip">
                    <span class="advisor-chip">{ui_html('Status')}: {escape(report['status'])}</span>
                    <span class="advisor-chip">{ui_html('Age')}: {client.age}</span>
                    <span class="advisor-chip">{ui_html('Currency')}: {escape(client.currency)}</span>
                    <span class="advisor-chip">{ui_html('Net Worth')}: {escape(money_text(float(result['net_worth']), client.currency, advisor_language))}</span>
                    <span class="advisor-chip">{escape(advisor_label('decision_compass', advisor_language))}: {escape(report['decision_compass'])}</span>
                    <span class="advisor-chip">{escape(advisor_label('crisis_signal', advisor_language))}: {escape(report['weakest_signal']['label'])}</span>
                </div>
            </div>
            <div class="advisor-memory-card">
                <h3>{ui_html('Advisor Interpretation')}</h3>
                <p>{escape(report['diagnosis'])}</p>
                <p><b>{ui_html('Focus')}:</b> {escape(client.text('advisor_focus', advisor_language))}</p>
                <ul class="advisor-action-list">{actions_html}</ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="portfolio-score-grid">{score_cards}</div>', unsafe_allow_html=True)

    visual_cols = st.columns(2)
    asset_df = pd.DataFrame(report["asset_mix"])
    asset_df["SharePct"] = asset_df["Share"] * 100
    with visual_cols[0]:
        st.subheader(ui("Asset Mix"))
        st.altair_chart(
            alt.Chart(asset_df[asset_df["Amount"] > 0])
            .mark_arc(innerRadius=58, outerRadius=120)
            .encode(
                theta=alt.Theta("Amount:Q"),
                color=alt.Color("Asset:N", legend=alt.Legend(title=None)),
                tooltip=[
                    "Asset",
                    alt.Tooltip("Amount:Q", format=",.0f"),
                    alt.Tooltip("SharePct:Q", title="Share", format=".1f"),
                ],
            )
            .properties(height=300),
            width="stretch",
        )
    with visual_cols[1]:
        st.subheader(ui("Stress Capital"))
        stress_df = pd.DataFrame(report["stress"])
        st.altair_chart(
            alt.Chart(stress_df)
            .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
            .encode(
                x=alt.X("Scenario:N", sort=None, title=None),
                y=alt.Y("Capital:Q", title=f"Capital ({client.currency})"),
                color=alt.Color("Scenario:N", legend=None),
                tooltip=["Scenario", alt.Tooltip("Capital:Q", format=",.0f")],
            )
            .properties(height=300),
            width="stretch",
        )

    evidence_cols = st.columns(2)
    with evidence_cols[0]:
        st.subheader(ui("Evidence"))
        st.dataframe(
            [{advisor_label("evidence", advisor_language): item} for item in report["evidence"]],
            hide_index=True,
            width="stretch",
        )
    with evidence_cols[1]:
        st.subheader(ui("Decision Path"))
        st.dataframe(
            [
                {advisor_label("layer", advisor_language): advisor_label("user", advisor_language), advisor_label("reading", advisor_language): client.text("segment", advisor_language)},
                {advisor_label("layer", advisor_language): advisor_label("data", advisor_language), advisor_label("reading", advisor_language): advisor_label("decision_path_data", advisor_language)},
                {advisor_label("layer", advisor_language): advisor_label("model", advisor_language), advisor_label("reading", advisor_language): advisor_label("decision_path_model", advisor_language)},
                {advisor_label("layer", advisor_language): advisor_label("evidence", advisor_language), advisor_label("reading", advisor_language): advisor_label("decision_path_evidence", advisor_language)},
                {advisor_label("layer", advisor_language): advisor_label("ai_interpretation", advisor_language), advisor_label("reading", advisor_language): report["diagnosis"]},
                {advisor_label("layer", advisor_language): advisor_label("decision", advisor_language), advisor_label("reading", advisor_language): report["actions"][0]},
                {advisor_label("layer", advisor_language): advisor_label("memory", advisor_language), advisor_label("reading", advisor_language): advisor_label("decision_path_memory", advisor_language)},
            ],
            hide_index=True,
            width="stretch",
        )

    portfolio_rows = []
    for holding in report["portfolio"]["positions"]:
        upside = holding.get("valuation_upside")
        portfolio_rows.append(
            {
                ui("Ticker"): holding.get("symbol"),
                ui("Name"): holding.get("name"),
                ui("Sector"): holding.get("sector"),
                ui("Weight"): f"{float(holding.get('weight') or 0) * 100:.1f}%",
                ui("Beta"): f"{float(holding.get('beta') or 0):.2f}",
                ui("Valuation"): "N/A" if upside is None else f"{float(upside) * 100:+.1f}%",
            }
        )
    if portfolio_rows:
        st.subheader(ui("Portfolio / Valuation Sample"))
        st.dataframe(portfolio_rows, hide_index=True, width="stretch")
        st.caption(
            f"{ui('Portfolio beta')} {float(report['portfolio']['weighted_beta']):.2f} · "
            f"{ui('Largest holding')} {float(report['portfolio']['largest_weight']) * 100:.1f}% · "
            f"{ui('Sector concentration')} {float(report['portfolio']['sector_concentration']) * 100:.1f}%"
        )

    with st.expander(ui("Selected client report text"), expanded=False):
        st.text_area(
            ui("Selected client report text"),
            value=report["report_text"],
            height=300,
            key=f"advisor_report_text_{client.client_id}",
        )

    selected_pdf = None
    all_pdf = None
    pdf_error = ""
    try:
        selected_pdf = client_report_pdf_bytes(report)
        all_pdf = all_clients_pdf_bytes(reports)
    except Exception as exc:
        pdf_error = str(exc)

    button_cols = st.columns(3)
    with button_cols[0]:
        st.download_button(
            ui("Download Selected Client PDF"),
            data=selected_pdf or b"",
            file_name=f"toxiguard_nora_advisor_report_{client.client_id.lower()}.pdf",
            mime="application/pdf",
            width="stretch",
            disabled=selected_pdf is None,
        )
    with button_cols[1]:
        st.download_button(
            ui("Download All Client Reports PDF"),
            data=all_pdf or b"",
            file_name=f"toxiguard_nora_advisor_reports_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            width="stretch",
            disabled=all_pdf is None,
        )
    with button_cols[2]:
        if st.button(ui("Load Client Into Finance"), width="stretch"):
            apply_advisor_client_to_finance(report)
            set_active_nav_key("finance")
            st.rerun()

    if pdf_error:
        st.warning(f"PDF export is unavailable until reportlab is installed: {pdf_error}")

    st.subheader(ui("All Virtual Client Results"))
    for item in reports:
        item_client = item["client"]
        item_result = item["result"]
        with st.expander(
            f"{item_client.client_id} - {item_client.name} | {item['status']} | "
            f"{float(item_result['planning_health_score']):.1f}/100",
            expanded=item_client.client_id == selected_id,
        ):
            st.write(item["diagnosis"])
            st.write(f"**{ui('Next actions:')}**")
            for action in item["actions"]:
                st.write(f"- {action}")


def build_current_situation_report_text() -> str:
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M")
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    total_value, weighted_beta, valuation_score, _ = portfolio_metrics()
    holdings = portfolio_holdings_snapshot()
    gain_loss = portfolio_gain_loss_summary(holdings)
    risk = portfolio_risk_metrics()
    comp = complementarity_summary()
    personal = st.session_state.get("last_personal_finance_result") or {}
    context = ai_coach_context_snapshot()
    readiness = ai_coach_readiness(context)

    lines = [
        f"ToxiGuard-NORA Current Situation Report - {now_text}",
        "",
        "1. Investment Readiness",
        f"- Readiness label: {readiness['label']} ({readiness['score']:.0f}/100)",
    ]
    for reason in readiness["reasons"][:4]:
        lines.append(f"- {reason}")

    lines.extend(
        [
            "",
            "2. Portfolio Position",
            f"- Total market value: {fmt_money(total_value, base_currency)}",
            f"- Weighted beta: {fmt_number(weighted_beta)}",
            "- Portfolio valuation score: "
            + ("N/A" if valuation_score is None else f"{valuation_score:+.1f}%"),
        ]
    )

    if gain_loss["total_cost_basis"] is not None:
        lines.extend(
            [
                f"- Cost basis entered for {gain_loss['costed_holding_count']} of {gain_loss['total_holding_count']} holding(s).",
                f"- Cost basis: {fmt_money(gain_loss['total_cost_basis'], base_currency)}",
                f"- Current value of costed holdings: {fmt_money(gain_loss['current_value_for_costed_holdings'], base_currency)}",
                f"- Unrealized P/L: {fmt_signed_money(gain_loss['unrealized_gain'], base_currency)}",
                f"- Unrealized return: {gain_loss['unrealized_return_pct']:+.1f}%",
            ]
        )
    else:
        lines.append("- Cost basis is not entered yet, so personal profit/loss is not calculated.")

    if holdings:
        lines.append("- Holdings summary:")
        for item in holdings[:6]:
            return_text = (
                "N/A"
                if item.get("unrealized_return_pct") is None
                else f"{float(item['unrealized_return_pct']):+.1f}%"
            )
            pl_text = fmt_signed_money(item.get("base_unrealized_gain"), base_currency)
            lines.append(
                f"  - {item['symbol']}: weight {float(item.get('base_weight', 0)) * 100:.1f}%, "
                f"P/L {pl_text}, return {return_text}, valuation {item.get('valuation_status', 'N/A')}"
            )
    else:
        lines.append("- No portfolio holdings are currently tracked.")

    if risk:
        lines.extend(
            [
                "",
                "3. Portfolio Risk",
                f"- Annualized portfolio risk: {float(risk['annual_vol']) * 100:.1f}%",
                f"- Expected annual return from history: {float(risk['annual_return']) * 100:+.1f}%",
                f"- Daily diversification benefit: {float(risk['diversification_benefit']) * 100:.3f}%",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "3. Portfolio Risk",
                "- At least two holdings with price history are needed for covariance-based risk analysis.",
            ]
        )

    if comp:
        lines.append(f"- Complementarity score: {float(comp['complementarity_score']):.1f}")

    lines.append("")
    lines.append("4. Personal Finance")
    if personal:
        lines.extend(
            [
                f"- Financial health score: {float(personal.get('financial_health_score', 0)):.1f}/100",
                f"- Monthly surplus: {fmt_money(float(personal.get('monthly_surplus', 0)))}",
                f"- Emergency fund: {float(personal.get('emergency_months', 0)):.1f} months",
                f"- Debt-to-income: {float(personal.get('debt_to_income', 0)) * 100:.1f}%",
                f"- Savings rate: {float(personal.get('savings_rate', 0)) * 100:.1f}%",
            ]
        )
    else:
        lines.append("- Personal Finance baseline has not been calculated yet.")

    missing = context.get("missing", [])
    lines.extend(["", "5. Missing Inputs"])
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- No major missing inputs detected for the current prototype.")

    lines.extend(
        [
            "",
            "6. Next Reflection Prompt",
            "- What changed since the last review?",
            "- Is my investment risk aligned with my cash flow and emergency reserve?",
            "- What is one safe next step before changing the portfolio?",
            "",
            "Caution: This report is educational and informational only. It is not financial, investment, legal, tax, or immigration advice.",
        ]
    )
    return "\n".join(lines)


def render_mobile_diary_deck(report_text: str) -> None:
    context = ai_coach_context_snapshot()
    readiness = ai_coach_readiness(context)
    diary = st.session_state.get("financial_diary", [])
    latest = diary[-1] if diary else {}
    portfolio = context["portfolio"]
    holdings = portfolio.get("holdings", [])
    gain_loss = portfolio_gain_loss_summary(holdings)
    base_currency = portfolio.get("base_currency", "USD")
    pnl_text = (
        "No cost basis"
        if gain_loss.get("unrealized_gain") is None
        else fmt_signed_money(gain_loss.get("unrealized_gain"), base_currency)
    )
    pnl_class = mobile_signed_class(gain_loss.get("unrealized_gain"))
    latest_action = latest.get("next_action") or "Save today's next action"
    report_lines = len([line for line in report_text.splitlines() if line.strip()])

    st.markdown(
        f"""
        <div class="mobile-only-deck">
            <div class="mobile-focus-card">
                <h3>Mobile Diary Memory</h3>
                <p>The diary becomes AI memory only when you save a snapshot. Keep notes short, non-sensitive, and action-oriented.</p>
            </div>
            <div class="mobile-card-grid">
                <div class="mobile-card"><div class="eyebrow">Readiness</div><div class="value">{escape(readiness['label'])}</div><span class="label">{readiness['score']:.0f}/100 now</span></div>
                <div class="mobile-card"><div class="eyebrow">Entries</div><div class="value">{len(diary)}</div><span class="label">Session memory</span></div>
                <div class="mobile-card"><div class="eyebrow">P/L Context</div><div class="value {pnl_class}">{escape(pnl_text)}</div><span class="label">Portfolio link</span></div>
                <div class="mobile-card"><div class="eyebrow">Report</div><div class="value">{report_lines}</div><span class="label">Lines ready</span></div>
            </div>
            <div class="mobile-diary-feed">
                <div class="mobile-diary-card">
                    <div class="eyebrow">Next Action</div>
                    <div class="title">{escape(compact_text(latest_action, 180))}</div>
                    <span class="hint">Use this as the first sentence for AI Coach reflection.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_saved_diary_cards(entries: list[dict[str, Any]]) -> None:
    cards = []
    for idx, entry in reversed(list(enumerate(entries, start=1))):
        if len(cards) >= 4:
            break
        portfolio = entry.get("portfolio", {})
        gain_loss = portfolio.get("gain_loss") or {}
        personal = entry.get("personal_finance") or {}
        base_currency = entry.get("base_currency", "USD")
        entry_gain = gain_loss.get("unrealized_gain")
        pnl_text = fmt_signed_money(entry_gain, base_currency) if entry_gain is not None else "N/A"
        pnl_class = mobile_signed_class(entry_gain)
        health_text = (
            "N/A"
            if not personal
            else f"{float(personal.get('financial_health_score', 0)):.1f}/100"
        )
        cards.append(
            f"""
            <div class="mobile-diary-card">
                <div class="eyebrow">Entry {idx}</div>
                <div class="title">{escape(str(entry.get("time", "No time")))} · {escape(str(entry.get("mood", "N/A")))}</div>
                <span class="hint">{escape(compact_text(entry.get("next_action") or "No next action recorded.", 180))}</span>
                <div class="meta">
                    <div class="mobile-mini-stat"><b>{escape(fmt_money(portfolio.get("total_market_value"), base_currency))}</b><span>Portfolio</span></div>
                    <div class="mobile-mini-stat"><b class="{pnl_class}">{escape(pnl_text)}</b><span>P/L</span></div>
                    <div class="mobile-mini-stat"><b>{escape(health_text)}</b><span>Health</span></div>
                    <div class="mobile-mini-stat"><b>{len(portfolio.get("holdings") or [])}</b><span>Holdings</span></div>
                </div>
            </div>
            """
        )

    if cards:
        st.markdown(
            f"""
            <div class="mobile-only-deck">
                <div class="mobile-diary-feed">
                    {''.join(cards)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def financial_diary_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Financial Diary</h1>
            <div class="hero-muted">Save snapshots of your financial life, portfolio structure, risk signals, and personal notes over time.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Diary entries are stored in the current Streamlit session unless downloaded. Avoid entering sensitive personal information in a public or shared browser."
    )

    st.subheader("Current Situation Report")
    report_text = build_current_situation_report_text()
    render_mobile_diary_deck(report_text)
    st.text_area(
        "Auto-generated report from Portfolio and Personal Finance",
        value=report_text,
        height=260,
        key="diary_current_report",
        help="This report uses current portfolio, cost basis, unrealized P/L, risk, and personal finance context.",
    )
    current_report_pdf = None
    current_report_pdf_error = ""
    try:
        from advisor_report_engine import text_report_pdf_bytes

        current_report_pdf = text_report_pdf_bytes(
            "ToxiGuard-NORA Current Situation Report",
            st.session_state.get("diary_current_report", report_text),
            "Portfolio, personal finance, risk, and memory checkpoint",
            language=current_language(),
        )
    except Exception as exc:
        current_report_pdf_error = str(exc)

    report_cols = st.columns(4)
    with report_cols[0]:
        if st.button("Use Report as Diary Note", width="stretch"):
            st.session_state.diary_note = st.session_state.get("diary_current_report", report_text)
            st.session_state.diary_next_action = "Review portfolio P/L, personal finance readiness, and one safe next step."
            st.rerun()
    with report_cols[1]:
        if st.button("Save Current Situation Report", width="stretch"):
            snapshot = build_financial_snapshot(
                st.session_state.get("diary_current_report", report_text).strip(),
                "Planning",
                "Review portfolio P/L, personal finance readiness, and one safe next step.",
            )
            st.session_state.financial_diary.append(snapshot)
            st.success("Current situation report saved to your Financial Diary.")
    with report_cols[2]:
        st.button(
            "Ask AI Coach",
            width="stretch",
            on_click=queue_current_report_ai_question,
        )
    with report_cols[3]:
        st.download_button(
            "Download Report PDF",
            data=current_report_pdf or b"",
            file_name=f"toxiguard_nora_current_situation_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            width="stretch",
            disabled=current_report_pdf is None,
        )
    if current_report_pdf_error:
        st.caption(f"PDF export is unavailable until reportlab is installed: {current_report_pdf_error}")

    mood = st.selectbox(
        "Today's financial feeling",
        ["Calm", "Curious", "Cautious", "Confident", "Concerned", "Planning"],
        key="diary_mood",
    )
    note = st.text_area(
        "Diary note",
        placeholder="Example: I reviewed my portfolio today and noticed that growth stocks still dominate my risk profile.",
        height=130,
        key="diary_note",
    )
    next_action = st.text_input(
        "Next action",
        placeholder="Example: Review cash reserve and reduce concentration risk next week.",
        key="diary_next_action",
    )

    save_col, download_col = st.columns([1, 2])
    with save_col:
        if st.button("Save Financial Snapshot", width="stretch"):
            snapshot = build_financial_snapshot(note.strip(), mood, next_action.strip())
            st.session_state.financial_diary.append(snapshot)
            st.success("Snapshot saved to your Financial Diary for this session.")

    diary_json = json.dumps(st.session_state.financial_diary, indent=2, ensure_ascii=False)
    with download_col:
        st.download_button(
            "Download Diary JSON",
            data=diary_json,
            file_name=f"toxiguard_nora_financial_diary_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            width="stretch",
            disabled=not bool(st.session_state.financial_diary),
        )

    uploaded = st.file_uploader("Restore diary JSON", type=["json"], key="diary_restore")
    if uploaded is not None:
        try:
            if getattr(uploaded, "size", 0) and uploaded.size > MAX_DIARY_RESTORE_BYTES:
                st.warning("Diary restore file is too large for this public prototype.")
                return
            raw_bytes = uploaded.getvalue()
            if len(raw_bytes) > MAX_DIARY_RESTORE_BYTES:
                st.warning("Diary restore file is too large for this public prototype.")
                return
            restored = json.loads(raw_bytes.decode("utf-8"))
            st.session_state.financial_diary = clean_restored_diary_entries(restored)
            st.success("Diary restored for this session.")
        except Exception as exc:
            st.warning(f"Could not restore diary file: {exc}")

    st.subheader("Saved Entries")
    if not st.session_state.financial_diary:
        st.info("No diary entries yet. Save a snapshot after reviewing your portfolio or personal finance status.")
        return

    summary_rows = []
    for idx, entry in enumerate(st.session_state.financial_diary, start=1):
        portfolio = entry.get("portfolio", {})
        gain_loss = portfolio.get("gain_loss") or {}
        personal = entry.get("personal_finance") or {}
        base_currency = entry.get("base_currency", "USD")
        entry_gain = gain_loss.get("unrealized_gain")
        entry_return = gain_loss.get("unrealized_return_pct")
        summary_rows.append(
            {
                "#": idx,
                "Time": entry.get("time"),
                "Mood": entry.get("mood"),
                "Portfolio Value": fmt_money(portfolio.get("total_market_value"), base_currency),
                "Unrealized P/L": fmt_signed_money(entry_gain, base_currency) if entry_gain is not None else "N/A",
                "Return": "N/A" if entry_return is None else f"{float(entry_return):+.1f}%",
                "Valuation Score": "N/A"
                if portfolio.get("valuation_score") is None
                else f"{float(portfolio.get('valuation_score')):+.1f}%",
                "Financial Health": "N/A"
                if not personal
                else f"{float(personal.get('financial_health_score', 0)):.1f}/100",
            }
        )
    render_mobile_saved_diary_cards(st.session_state.financial_diary)
    st.dataframe(summary_rows, hide_index=True, width="stretch")

    for idx, entry in reversed(list(enumerate(st.session_state.financial_diary, start=1))):
        with st.expander(f"Entry {idx}: {entry.get('time')} - {entry.get('mood')}", expanded=False):
            st.write(f"**Note:** {entry.get('note') or 'No note'}")
            st.write(f"**Next Action:** {entry.get('next_action') or 'No action recorded'}")
            portfolio = entry.get("portfolio", {})
            base_currency = entry.get("base_currency", "USD")
            gain_loss = portfolio.get("gain_loss") or {}
            entry_valuation = portfolio.get("valuation_score")
            valuation_text = "N/A" if entry_valuation is None else f"{float(entry_valuation):+.1f}%"
            gain_text = (
                "N/A"
                if gain_loss.get("unrealized_gain") is None
                else fmt_signed_money(gain_loss.get("unrealized_gain"), base_currency)
            )
            return_text = (
                "N/A"
                if gain_loss.get("unrealized_return_pct") is None
                else f"{float(gain_loss.get('unrealized_return_pct')):+.1f}%"
            )
            st.write(
                f"**Portfolio:** {fmt_money(portfolio.get('total_market_value'), base_currency)} | "
                f"Beta {fmt_number(portfolio.get('weighted_beta'))} | "
                f"Valuation Score {valuation_text} | "
                f"P/L {gain_text} ({return_text})"
            )
            holdings = portfolio.get("holdings") or []
            if holdings:
                st.dataframe(
                    [
                        {
                            "Stock": f"{item['symbol']} - {item['name']}",
                            "Currency": item["currency"],
                            "Shares": item["shares"],
                            "Avg Purchase Price": "N/A"
                            if not item.get("purchase_price")
                            else fmt_money(item.get("purchase_price"), item["currency"]),
                            "Current Price": fmt_money(item.get("price"), item["currency"]),
                            "Unrealized P/L": fmt_signed_money(item.get("base_unrealized_gain"), base_currency),
                            "Return": "N/A"
                            if item.get("unrealized_return_pct") is None
                            else f"{float(item['unrealized_return_pct']):+.1f}%",
                            "Base Weight": f"{float(item['base_weight']) * 100:.1f}%",
                            "Valuation": item["valuation_status"],
                        }
                        for item in holdings
                    ],
                    hide_index=True,
                    width="stretch",
                )


def render_portfolio_charts() -> None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    st.subheader("Portfolio Charts")
    st.caption("Select a holding to review its TradingView chart without leaving the Portfolio tab.")

    if not symbols:
        st.info("Add stocks to your portfolio to view holding charts.")
        return

    labels = {
        symbol: f"{symbol} - {st.session_state.stocks[symbol]['name']}"
        for symbol in symbols
    }
    selected = st.selectbox(
        "Select portfolio holding",
        options=symbols,
        format_func=lambda symbol: labels[symbol],
        key="portfolio_chart_symbol",
    )
    render_tradingview_chart(selected)


def portfolio_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Investment Portfolio</h1>
            <div class="hero-muted">Track weighted risk, return, and valuation across your holdings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_portfolio_stock_search()

    fx_col1, fx_col2, fx_col3 = st.columns(3)
    with fx_col1:
        st.selectbox(
            "Portfolio base currency",
            ["USD", "KRW"],
            key="portfolio_base_currency",
            help="Portfolio totals and weights are calculated after converting each holding into this currency.",
        )
    with fx_col2:
        st.checkbox(
            "Use live USD/KRW",
            key="use_live_fx",
            help="Uses Yahoo Finance KRW=X when available. Manual rate is used as fallback.",
        )
    with fx_col3:
        st.number_input(
            "Manual USD/KRW rate",
            min_value=1.0,
            step=1.0,
            key="manual_usdkrw",
        )

    usdkrw, fx_source, fx_date = effective_usdkrw()
    st.caption(
        f"FX setting: 1 USD = ₩{usdkrw:,.2f} | Source: {fx_source} | Date: {fx_date}. "
        "Portfolio weights use converted base-currency values."
    )

    st.radio(
        "Portfolio weighting mode",
        ["Share-based", "Equal-weighted"],
        horizontal=True,
        key="portfolio_weighting_mode",
        help=(
            "Share-based uses shares x current price. Equal-weighted assigns the same analysis weight "
            "to each holding, which is useful for classroom portfolio analysis."
        ),
    )
    if st.session_state.portfolio_weighting_mode == "Equal-weighted":
        st.info(
            "Equal weighting assigns the same analysis weight to each selected security. "
            "This is useful for classroom analysis and simple backtesting concepts, but maintaining "
            "equal weights in practice requires periodic rebalancing. Trading costs and taxes may reduce actual performance."
        )
    else:
        st.caption(
            "Share-based weighting uses each holding's current market value. A high-priced stock can dominate the portfolio if the share count is similar across holdings."
        )

    total_value, weighted_beta, valuation_score, sector_values = portfolio_metrics()
    c1, c2, c3 = st.columns(3)
    score_text = "N/A" if valuation_score is None else f"{valuation_score:+.1f}%"
    score_color = "#94a3b8"
    if valuation_score is not None:
        score_color = "#10b981" if valuation_score > 5 else "#ef4444" if valuation_score < -5 else "#f59e0b"
    with c1:
        metric_card("Total Market Value", fmt_money(total_value, st.session_state.portfolio_base_currency))
    with c2:
        metric_card("Weighted Beta", fmt_number(weighted_beta))
    with c3:
        metric_card("Portfolio Valuation Score", score_text, score_color)

    st.info(
        "Valuation Score estimates the portfolio's weighted upside or downside versus each stock's blended fair value. "
        "Formula: sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight. "
        "Positive means undervalued; negative means overvalued. Holdings without valid fair value are excluded. "
        f"Current analysis mode: {st.session_state.portfolio_weighting_mode}."
    )

    render_quick_portfolio_entry()

    if not st.session_state.portfolio:
        render_mobile_portfolio_deck([], total_value, weighted_beta, valuation_score, 0, None, None)
        st.info("No stocks in your portfolio yet. Add them from the search results.")
        st.button(
            "Ask AI Coach About Portfolio Setup",
            width="stretch",
            on_click=queue_ai_coach_question,
            args=(
                "My portfolio has no holdings yet. Explain what I should add first so portfolio P/L, cost basis, and investment readiness can work.",
            ),
        )
        return

    native_breakdown = portfolio_currency_breakdown()
    if len(native_breakdown) > 1:
        st.info(
            "This portfolio includes multiple currencies. Native market values are shown by currency, "
            f"and portfolio weights are calculated in {st.session_state.portfolio_base_currency} using the USD/KRW FX rate above."
        )
    if native_breakdown:
        st.caption(
            "Native currency breakdown: "
            + " | ".join(fmt_money(value, currency) for currency, value in sorted(native_breakdown.items()))
        )

    current_holdings = []
    for symbol, holding in list(st.session_state.portfolio.items()):
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        currency = stock.get("currency", "USD")
        input_cols = st.columns(2)
        with input_cols[0]:
            shares = st.number_input(
                f"{symbol} shares",
                min_value=0.0,
                value=float(holding.get("shares") or 0),
                step=1.0,
                key=f"shares_{symbol}",
            )
        with input_cols[1]:
            purchase_step = 100.0 if currency == "KRW" else 1.0
            purchase_price = st.number_input(
                f"{symbol} average purchase price ({currency})",
                min_value=0.0,
                value=float(holding.get("purchase_price") or 0),
                step=purchase_step,
                key=f"purchase_price_{symbol}",
                help="Enter the average price you paid per share. Leave 0 if you do not want to calculate profit/loss yet.",
            )
        st.session_state.portfolio[symbol]["shares"] = shares
        st.session_state.portfolio[symbol]["purchase_price"] = purchase_price
        native_value = float(stock["price"]) * shares
        native_cost_basis = purchase_price * shares if purchase_price > 0 and shares > 0 else None
        base_value = convert_value(
            native_value,
            currency,
            st.session_state.portfolio_base_currency,
            usdkrw,
        )
        base_cost_basis = (
            convert_value(
                native_cost_basis,
                currency,
                st.session_state.portfolio_base_currency,
                usdkrw,
            )
            if native_cost_basis is not None
            else None
        )
        base_unrealized_gain = (
            base_value - base_cost_basis if base_cost_basis is not None else None
        )
        unrealized_return_pct = (
            (native_value - native_cost_basis) / native_cost_basis * 100
            if native_cost_basis and native_cost_basis > 0
            else None
        )
        current_holdings.append(
            (
                symbol,
                stock,
                shares,
                purchase_price,
                native_value,
                base_value,
                native_cost_basis,
                base_cost_basis,
                base_unrealized_gain,
                unrealized_return_pct,
            )
        )

    rows = []
    current_total_value = sum(item[5] for item in current_holdings)
    costed_rows = [item for item in current_holdings if item[7] is not None and float(item[7]) > 0]
    total_cost_basis = sum(float(item[7]) for item in costed_rows)
    costed_market_value = sum(float(item[5]) for item in costed_rows)
    total_unrealized_gain = costed_market_value - total_cost_basis if total_cost_basis > 0 else None
    total_unrealized_return_pct = (
        total_unrealized_gain / total_cost_basis * 100
        if total_cost_basis > 0 and total_unrealized_gain is not None
        else None
    )
    if total_cost_basis > 0:
        pl_color = "#10b981" if (total_unrealized_gain or 0) >= 0 else "#ef4444"
        pnl_cols = st.columns(3)
        with pnl_cols[0]:
            metric_card("Cost Basis", fmt_money(total_cost_basis, st.session_state.portfolio_base_currency))
        with pnl_cols[1]:
            metric_card("Unrealized P/L", fmt_signed_money(total_unrealized_gain, st.session_state.portfolio_base_currency), pl_color)
        with pnl_cols[2]:
            metric_card("Unrealized Return", f"{total_unrealized_return_pct:+.1f}%", pl_color)
    else:
        st.info("Enter each holding's average purchase price to compare your cost basis with current market value.")

    render_mobile_portfolio_deck(
        current_holdings,
        current_total_value,
        weighted_beta,
        valuation_score,
        total_cost_basis,
        total_unrealized_gain,
        total_unrealized_return_pct,
    )
    render_portfolio_resilience_panel(
        portfolio_resilience_summary(
            portfolio_holdings_snapshot(),
            sector_values,
            weighted_beta,
            valuation_score,
        )
    )

    st.button(
        "Ask AI Coach About Portfolio P/L",
        width="stretch",
        on_click=queue_ai_coach_question,
        args=(
            "Use my portfolio shares, average purchase prices, unrealized P/L, current market value, and risk signals to explain what I should review next.",
        ),
    )

    analysis_weights = portfolio_analysis_weights()
    for (
        symbol,
        stock,
        shares,
        purchase_price,
        native_value,
        base_value,
        native_cost_basis,
        base_cost_basis,
        base_unrealized_gain,
        unrealized_return_pct,
    ) in current_holdings:
        currency = stock.get("currency", "USD")
        weight = base_value / current_total_value * 100 if current_total_value else 0
        analysis_weight = analysis_weights.get(symbol, 0.0) * 100
        rows.append(
            {
                "Stock": f"{symbol} - {stock['name']}",
                "Currency": currency,
                "Current Price": stock_money(stock, stock["price"]),
                "Avg Purchase Price": "N/A" if purchase_price <= 0 else stock_money(stock, purchase_price),
                "Shares": shares,
                "Cost Basis": "N/A" if native_cost_basis is None else fmt_money(native_cost_basis, currency),
                "Native Market Value": fmt_money(native_value, currency),
                f"{st.session_state.portfolio_base_currency} Market Value": fmt_money(base_value, st.session_state.portfolio_base_currency),
                "Unrealized P/L": fmt_signed_money(base_unrealized_gain, st.session_state.portfolio_base_currency),
                "Return": "N/A" if unrealized_return_pct is None else f"{unrealized_return_pct:+.1f}%",
                "Base Weight": f"{weight:.1f}%",
                "Analysis Weight": f"{analysis_weight:.1f}%",
            }
        )

    st.dataframe(rows, hide_index=True, width="stretch")
    remove_cols = st.columns(min(4, len(st.session_state.portfolio)))
    for idx, symbol in enumerate(list(st.session_state.portfolio.keys())):
        remove_cols[idx % len(remove_cols)].button(
            f"Remove {symbol}",
            key=f"remove_portfolio_{symbol}",
            on_click=remove_portfolio,
            args=(symbol,),
        )

    if sector_values:
        st.subheader("Sector Allocation")
        render_sector_pie_chart(sector_values)

    st.subheader("Backtesting Concept")
    st.info(
        "A simple educational backtest can start with an equal-weighted portfolio, as used in class. "
        "A full professional backtest also needs rebalancing frequency, transaction costs, taxes, benchmark selection, "
        "and survivorship-bias controls. ToxiGuard-NORA currently focuses on educational portfolio analytics rather than full performance backtesting."
    )
    st.caption(
        "Reference suggested for advanced analysis: Portfolio Visualizer. ToxiGuard-NORA can use it as a methodological benchmark while keeping this app focused on learning and interpretation."
    )

    render_portfolio_charts()
    render_portfolio_risk_analysis()
    render_complementarity_analysis()


def settings_tab() -> None:
    st.header("Real-Time Financial API Settings")
    st.success("FINNHUB_API_KEY is configured in Streamlit Secrets." if FINNHUB_API_KEY else "FINNHUB_API_KEY is missing.")
    st.write(
        """
        This version keeps the Finnhub API key on the Streamlit server side.
        External users do not need to enter a key, and the token is not stored in their browser.
        """
    )
    st.subheader("Verified AI Model")
    if OPENAI_API_KEY:
        st.success(f"OPENAI_API_KEY is configured. AI Coach can use {OPENAI_MODEL}.")
    else:
        st.warning("OPENAI_API_KEY is missing. AI Coach will remain rule-based until the key is added.")
    st.caption(
        f"Current AI model setting: {OPENAI_MODEL} with reasoning effort '{OPENAI_REASONING_EFFORT}'. "
        "Set OPENAI_AI_DEFAULT_ON = true only if you want the verified model toggle enabled by default."
    )
    st.subheader("Macroeconomic Variables")
    st.caption(
        "The app starts with 4.50% for both values. Users can revise these assumptions, "
        "and the updated values will be reflected in CAPM required return and valuation calculations."
    )

    if st.button("Reset macro assumptions to 4.50%", width="stretch"):
        st.session_state.risk_free_rate_pct = DEFAULT_RISK_FREE_RATE * 100
        st.session_state.equity_risk_premium_pct = DEFAULT_EQUITY_RISK_PREMIUM * 100
        st.session_state.macro_risk_free_rate_pct_text = f"{DEFAULT_RISK_FREE_RATE * 100:.2f}"
        st.session_state.macro_equity_risk_premium_pct_text = f"{DEFAULT_EQUITY_RISK_PREMIUM * 100:.2f}"
        st.session_state["_macro_assumptions_applied"] = (
            DEFAULT_RISK_FREE_RATE * 100,
            DEFAULT_EQUITY_RISK_PREMIUM * 100,
        )
        recalculated = recalculate_loaded_stocks()
        st.success(
            "Default assumptions restored."
            + (f" {recalculated} loaded stock(s) were recalculated." if recalculated else "")
        )

    with st.form("macro_assumptions_form"):
        macro_cols = st.columns(2)
        with macro_cols[0]:
            risk_free_pct_text = st.text_input(
                "Risk-Free Rate (%)",
                value=f"{float(st.session_state.get('risk_free_rate_pct', DEFAULT_RISK_FREE_RATE * 100)):.2f}",
                help="Used as the base rate in CAPM. Enter a percent value such as 4.50.",
            )
        with macro_cols[1]:
            equity_risk_premium_pct_text = st.text_input(
                "Equity Risk Premium (%)",
                value=f"{float(st.session_state.get('equity_risk_premium_pct', DEFAULT_EQUITY_RISK_PREMIUM * 100)):.2f}",
                help="Used as the market risk premium in CAPM. Enter a percent value such as 4.50.",
            )
        apply_macro = st.form_submit_button(
            "Apply macro assumptions to calculations",
            type="primary",
            width="stretch",
        )

    if apply_macro:
        try:
            risk_free_pct = float(str(risk_free_pct_text).strip().replace("%", ""))
            equity_risk_premium_pct = float(str(equity_risk_premium_pct_text).strip().replace("%", ""))
        except ValueError:
            st.error("Please enter valid numeric percentages, for example 4.50 or 5.25.")
            return

        if risk_free_pct < 0 or equity_risk_premium_pct < 0:
            st.error("Macro assumptions cannot be negative.")
            return
        if risk_free_pct > 25 or equity_risk_premium_pct > 25:
            st.error("Please keep macro assumptions at or below 25.00%.")
            return

        st.session_state.risk_free_rate_pct = risk_free_pct
        st.session_state.equity_risk_premium_pct = equity_risk_premium_pct
        st.session_state.macro_risk_free_rate_pct_text = f"{risk_free_pct:.2f}"
        st.session_state.macro_equity_risk_premium_pct_text = f"{equity_risk_premium_pct:.2f}"
        current_macro = (round(risk_free_pct, 4), round(equity_risk_premium_pct, 4))
        recalculated = recalculate_loaded_stocks()
        st.session_state["_macro_assumptions_applied"] = current_macro
        if recalculated:
            st.success(f"Updated assumptions applied. {recalculated} loaded stock(s) were recalculated.")
        else:
            st.info("Updated assumptions saved. New stock searches will use these values.")

    risk_free_rate, equity_risk_premium = macro_assumptions()
    st.info(
        f"Current CAPM assumption: Required Return = {risk_free_rate * 100:.2f}% "
        f"+ Beta x {equity_risk_premium * 100:.2f}%."
    )


def guide_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">ToxiGuard-NORA User Guide</h1>
            <div class="hero-muted">A practical in-app guide based on the English PDF user guide.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if GUIDE_PDF_PATH.exists():
        st.download_button(
            "Download PDF User Guide",
            data=GUIDE_PDF_PATH.read_bytes(),
            file_name="ToxiGuard-NORA_User_Guide.pdf",
            mime="application/pdf",
            width="stretch",
        )
    else:
        st.info("Upload ToxiGuard-NORA_User_Guide.pdf to the repository to enable PDF download.")

    st.subheader("1. Search and Explore Stocks")
    guide_image("01-search-dashboard.png", "Search dashboard")
    st.write(
        """
        Use the Search tab as the main workspace. Enter a stock ticker, then review
        the stock card for current price, market cap, PER, and valuation status.
        """
    )
    st.markdown(
        """
        - Use valuation filters to focus on Undervalued, Fair Value, or Overvalued stocks.
        - Use **Compare** to add up to three stocks to side-by-side comparison.
        - Use **Add to Portfolio** to include a holding in portfolio tracking.
        - Click a stock card to open the selected stock's TradingView price chart, key statistics, and valuation breakdown.
        """
    )

    st.subheader("2. Compare Selected Stocks")
    guide_image("02-compare.png", "Side-by-side comparison")
    st.write(
        "The Compare tab shows selected stocks side by side across price, daily change, market cap, PER, dividend yield, beta, EPS, fair value, and valuation status."
    )

    st.subheader("3. Track Your Portfolio")
    guide_image("03-portfolio.png", "Portfolio dashboard")
    st.write(
        """
        The Portfolio tab tracks current holdings, share counts, market value, portfolio weight,
        weighted beta, valuation score, sector allocation, portfolio risk, and stock complementarity.
        """
    )
    st.markdown(
        """
        - Sector Allocation is shown as a donut-style pie chart.
        - Enter average purchase price for each holding to calculate cost basis, unrealized profit/loss, and personal return.
        - Share-based mode uses shares x current price, so high-priced stocks can dominate if share counts are similar.
        - Equal-weighted mode assigns the same analysis weight to each holding, matching a simple classroom portfolio method.
        - Portfolio Risk uses the selected analysis weights plus daily return covariance.
        - Stock Complementarity shows whether holdings move together or offset each other.
        """
    )

    st.subheader("4. Portfolio Valuation Score")
    st.info(
        "Score = sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight"
    )
    st.markdown(
        """
        - A positive score means the valued part of the portfolio appears undervalued overall.
        - A negative score means it appears overvalued overall.
        - Holdings without a valid fair value are excluded from this score.
        - The score follows the selected portfolio weighting mode: Share-based or Equal-weighted.
        - The score is an analytical estimate, not a guaranteed return forecast.
        """
    )

    st.subheader("5. Portfolio Risk")
    st.write(
        """
        Portfolio risk is calculated from each holding's weight and the covariance of daily stock returns.
        This follows the portfolio risk concept from CAPM: diversification works when assets do not move perfectly together.
        """
    )
    st.info("Portfolio variance = w' x covariance matrix x w")
    st.markdown(
        """
        - Annualized Portfolio Risk shows the portfolio's estimated annual volatility.
        - Diversification Benefit compares weighted individual volatility with actual portfolio volatility.
        - Lower correlation between holdings generally improves risk reduction.
        - Equal-weighted analysis is useful for learning, but keeping equal weights in real portfolios requires rebalancing.
        - Rebalancing can create transaction costs and taxes, so ToxiGuard-NORA presents this as educational analysis rather than a full professional backtest.
        """
    )

    st.subheader("6. Educational Scope")
    st.write(
        """
        ToxiGuard-NORA is designed to connect finance theory with real market examples. It is not an
        investment recommendation service. The current focus is stock analysis, valuation
        triangulation, CAPM, portfolio variance, covariance, diversification, and correlation.
        Sector-specialized tools such as REIT analysis can be explored as a separate future project.
        """
    )

    st.subheader("7. What-if Scenario Lab")
    st.write(
        """
        The Scenario menu lets users stress-test assumptions before relying on any AI explanation.
        Users can adjust income, expenses, cash shocks, portfolio moves, USD/KRW changes, interest-rate moves,
        and rate-sensitive allocation. The output connects market stress with life-level readiness.
        """
    )
    st.markdown(
        """
        - Use scenarios to study trade-offs, not to predict the future.
        - Compare market risk with emergency funds, debt pressure, and health score.
        - Download the structured scenario JSON as future AI-coach context.
        """
    )

    st.subheader("8. AI Coach and Reasoning Readiness")
    st.write(
        """
        The AI Coach menu turns ToxiGuard-NORA from a dashboard into a conversation-first financial reasoning
        prototype. It can run locally as a rule-based coach or, when `OPENAI_API_KEY` is configured and the
        user enables the verified model toggle, call a reasoning model through OpenAI's Responses API.
        The AI Coach also shows linked guidance cards for Portfolio P/L, Personal Finance, Scenario,
        Diary Report, and Calculation Details, so the user can open the source view or ask a context-specific
        question directly. The answer is still constrained to evidence, assumptions, missing inputs, risk flags,
        next safe step, and caution.
        """
    )

    st.subheader("9. Stock Detail Page")
    guide_image("04-stock-detail.png", "Stock detail screen")
    st.write(
        "Click a stock card to review the TradingView price chart, current price, fair value, CAPM required return, key statistics, and valuation triangulation."
    )

    st.subheader("10. Calculation Details")
    st.write(
        """
        The Calculation Details tab explains the formulas, assumptions, and data inputs behind valuation,
        portfolio valuation score, portfolio risk, diversification, and personal finance health.
        Use this tab to understand why a result appears, not just what the result says. In a future
        AI version, this becomes the reasoning audit trail behind AI explanations.
        """
    )

    st.subheader("11. Financial Diary")
    st.write(
        """
        The Financial Diary tab saves a point-in-time snapshot of portfolio structure, risk signals,
        personal finance results, unrealized profit/loss, and the user's own reflection. It can also
        generate a Current Situation Report from Portfolio and Personal Finance before saving. Diary data
        is held in the current session unless downloaded as a JSON file. Long term, this becomes
        user-controlled financial memory for AI-assisted reflection.
        """
    )

    st.subheader("12. API and Macro Settings")
    guide_image("05-settings-modal.png", "Settings screen")
    st.write(
        """
        The Finnhub API key is stored in Streamlit Secrets and used only on the server side.
        External users do not need to enter a key, and the token is not stored in their browser.
        """
    )
    st.markdown(
        """
        - Risk-Free Rate and Equity Risk Premium begin at 4.50% each, but users can update them in Settings.
        - Updated macro assumptions are applied to CAPM required return and valuation calculations.
        - API keys should never be pasted into public code, screenshots, or browser-side scripts.
        - OPENAI_API_KEY enables the verified AI model layer for AI Coach.
        - OPENAI_MODEL defaults to gpt-5-mini unless changed in Streamlit Secrets.
        - OPENAI_AI_DEFAULT_ON can be set to true if the owner wants model mode enabled by default.
        """
    )

    st.subheader("13. Data, Privacy, and License")
    st.warning(
        "Prototype privacy notice: do not enter sensitive personal financial information such as bank "
        "account numbers, tax IDs, passwords, or confidential financial records."
    )
    st.markdown(
        """
        - ToxiGuard-NORA is an educational prototype, not financial, investment, tax, legal, accounting, or professional advice.
        - Market data and charts may be provided by Finnhub, TradingView, Yahoo Finance, and yfinance, subject to their own terms.
        - TradingView attribution should remain visible when chart widgets are used.
        - Third-party company names, ticker symbols, trademarks, and data remain the property of their respective owners.
        - For commercial use, review `LICENSE`, `DATA_SOURCES.md`, `PRIVACY_NOTICE.md`, and `THIRD_PARTY_NOTICES.md`.
        """
    )


def remove_sidebar_item(collection: str, symbol: str, key: str) -> None:
    if collection == "compare" and symbol in st.session_state.compare:
        st.session_state.compare.remove(symbol)
    if collection == "portfolio" and symbol in st.session_state.portfolio:
        del st.session_state.portfolio[symbol]
    if key in st.session_state:
        del st.session_state[key]
    sync_selection_state_to_query()
    st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## ToxiGuard-NORA")
        st.caption(ui("Open or close this sidebar with the arrow in the upper-left corner."))

        if st.button(ui("View Life Design Intro"), width="stretch"):
            st.session_state.life_entry_complete = False
            st.session_state.life_entry_version_seen = ""
            st.rerun()

        st.markdown(f"### {ui('Ver.2 Module')}")
        st.caption(ui("Use the REIT Analysis tab in the main screen."))

        st.markdown(f"### {ui('Compare List')}")
        if st.session_state.compare:
            for symbol in list(st.session_state.compare):
                stock = st.session_state.stocks.get(symbol, {"name": symbol})
                key = f"sidebar_compare_{symbol}"
                checked = st.checkbox(
                    f"{symbol} - {stock.get('name', symbol)}",
                    value=True,
                    key=key,
                )
                if not checked:
                    remove_sidebar_item("compare", symbol, key)
        else:
            st.caption(ui("No stocks selected for comparison."))

        st.markdown(f"### {ui('Portfolio List')}")
        if st.session_state.portfolio:
            for symbol in list(st.session_state.portfolio.keys()):
                stock = st.session_state.stocks.get(symbol, {"name": symbol})
                shares = st.session_state.portfolio.get(symbol, {}).get("shares", 0)
                key = f"sidebar_portfolio_{symbol}"
                checked = st.checkbox(
                    f"{symbol} - {stock.get('name', symbol)} ({shares:g} shares)",
                    value=True,
                    key=key,
                )
                if not checked:
                    remove_sidebar_item("portfolio", symbol, key)
        else:
            st.caption(ui("No stocks in portfolio."))

        st.divider()
        st.markdown(f"### {ui('Developer')}")
        st.write(f"**{DEVELOPER_NAME}**")
        st.write(f"Email: `{DEVELOPER_EMAIL}`")

        comment = st.text_area(
            ui("Send a comment"),
            placeholder=ui("Write feedback or an issue to review later."),
            height=110,
            key="sidebar_comment_text",
        )
        if st.button(ui("Save Comment"), width="stretch"):
            clean_comment = comment.strip()
            if clean_comment:
                st.session_state.comments.append(
                    {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "comment": clean_comment,
                    }
                )
                st.success(ui("Comment saved in this session."))
                st.rerun()
            else:
                st.warning(ui("Please enter a comment first."))

        if st.session_state.comments:
            with st.expander(ui("Saved comments"), expanded=False):
                for item in reversed(st.session_state.comments[-5:]):
                    st.caption(f"{item['time']} - {item['comment']}")


def render_footer() -> None:
    footer_text = ui(
        "ToxiGuard-NORA is provided for educational and informational use only and does not constitute or provide financial, investment, legal, tax, accounting, or professional advice. Do not enter sensitive personal financial information into this prototype. Market data and charts may be provided by third-party services such as Finnhub, TradingView, and Yahoo Finance/yfinance, subject to their own terms. All trademarks, company names, and ticker symbols remain the property of their respective owners. This interface uses original CSS/HTML design elements and does not claim ownership of third-party data, logos, or trademarks. Data may be delayed, incomplete, or unavailable and should be verified independently."
    )
    st.markdown(
        f"""
        <div class="app-footer">
            {escape(footer_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_life_entry_screen(standalone: bool = True) -> None:
    shell_style = (
        """
        <style>
        section[data-testid="stSidebar"] { display: none; }
        div[data-testid="collapsedControl"] { display: none; }
        .block-container { max-width: 1480px; padding-top: 1.2rem; }
        </style>
        """
        if standalone
        else ""
    )
    # The legacy bitmap has embedded LY-STScope copy, so the live HTML version
    # is safer until a ToxiGuard-NORA-specific image is generated.
    homepage_bg = image_data_uri(str(HOMEPAGE_BG_PATH)) if USE_HOMEPAGE_REFERENCE_IMAGE else ""
    homepage_class = " has-home-image" if homepage_bg else ""
    homepage_image = (
        f'<img class="homepage-bg-img" src="{homepage_bg}" alt="ToxiGuard-NORA life design homepage preview">'
        if homepage_bg
        else ""
    )
    language = current_language()
    dashboard_href = escape(app_view_href("life"), quote=True)
    life_title = "Goal을 <span>선택하세요</span>" if language == "ko" else 'Choose a <span>Goal</span>'
    life_copy = (
        "목표가 먼저입니다. 전략은 그 다음에 바뀝니다."
        if language == "ko"
        else "Goal first. Strategy changes from there."
    )
    start_text = "시작" if language == "ko" else "Start"
    detail_text = "클릭해서 보기" if language == "ko" else "Click for detail"
    goal_cards = []
    for goal_key, config in NORA_GOAL_STRATEGIES.items():
        goal_cards.append(
            f"""
            <details class="home-goal-card" style="--goal-color: {escape(config['color'])};">
                <summary>
                    <span class="goal-number">{escape(config['icon'])}</span>
                    <span class="goal-summary">
                        <b>{escape(config[f'label_{language}'])}</b>
                        <i>{escape(config[f'short_{language}'])}</i>
                    </span>
                    <em>{escape(detail_text)}</em>
                </summary>
                <div class="goal-card-detail">{escape(config[f'strategy_{language}'])}</div>
                <a class="goal-start" href="{escape(goal_href(goal_key), quote=True)}" target="_self">{escape(start_text)}</a>
            </details>
            """
        )
    goal_cards_html = "".join(goal_cards)
    compass_caption = "Goal → Strategy → Situation" if language == "en" else "목표 → 전략 → 상황"
    homepage_html = dedent(
        shell_style
        + f"""
        <div class="life-entry-wrap">
            <div class="life-entry homepage-visual{homepage_class}">
                {homepage_image}
                <div class="home-nav">
                    <div class="home-brand">
                        <div class="home-brand-mark">N</div>
                        <div>ToxiGuard-NORA <small>Ver.2</small></div>
                    </div>
                </div>
                <div class="home-goal-layout">
                    <section class="home-goal-intro" aria-label="NORA goal start">
                        <div class="life-kicker">{'Goal comes before strategy.' if language == 'en' else '전략보다 목표가 먼저입니다.'}</div>
                        <h1 class="life-title">{life_title}</h1>
                        <div class="life-copy">{escape(life_copy)}</div>
                        <div class="goal-compass" aria-hidden="true">
                            <span class="goal-compass-ring one"></span>
                            <span class="goal-compass-ring two"></span>
                            <span class="goal-compass-dot d1"></span>
                            <span class="goal-compass-dot d2"></span>
                            <span class="goal-compass-dot d3"></span>
                            <span class="goal-compass-dot d4"></span>
                            <div class="goal-compass-core">NORA</div>
                        </div>
                        <div class="goal-compass-caption">{escape(compass_caption)}</div>
                        <a class="home-skip-link" href="{dashboard_href}" target="_self">{'Open without goal' if language == 'en' else '목표 없이 열기'}</a>
                    </section>
                    <section class="home-goal-grid" aria-label="Goal choices">
                        {goal_cards_html}
                    </section>
                </div>
            </div>
        </div>
        """,
    )
    homepage_html = "\n".join(line.strip() for line in homepage_html.splitlines() if line.strip())
    st.markdown(homepage_html, unsafe_allow_html=True)

    st.caption(
        ui(
            "Educational prototype only; not financial, investment, legal, or tax advice."
        )
    )


NAV_ITEMS = [
    {"key": "life", "label": "Life", "icon": "LF"},
    {"key": "finance", "label": "Finance", "icon": "FI"},
    {"key": "portfolio", "label": "Portfolio", "icon": "PF"},
    {"key": "diary", "label": "Diary", "icon": "DY"},
    {"key": "advisor", "label": "Advisor Reports", "icon": "AR"},
    {"key": "search", "label": "Search", "icon": "SR"},
    {"key": "compare", "label": "Compare", "icon": "CP"},
    {"key": "reit", "label": "REIT", "icon": "RE"},
    {"key": "details", "label": "Details", "icon": "DT"},
    {"key": "scenario", "label": "Scenario", "icon": "SC"},
    {"key": "ai", "label": "AI Coach", "icon": "AI"},
    {"key": "guide", "label": "Guide", "icon": "GD"},
    {"key": "settings", "label": "Settings", "icon": "SE"},
]

DESKTOP_ORBIT_ITEMS = [
    {"key": "life", "x": "50%", "y": "11%", "accent": "#14b8a6", "accent_rgb": "20, 184, 166"},
    {"key": "finance", "x": "71%", "y": "17%", "accent": "#0ea5e9", "accent_rgb": "14, 165, 233"},
    {"key": "portfolio", "x": "85%", "y": "34%", "accent": "#84cc16", "accent_rgb": "132, 204, 22"},
    {"key": "search", "x": "89%", "y": "55%", "accent": "#3b82f6", "accent_rgb": "59, 130, 246"},
    {"key": "compare", "x": "80%", "y": "75%", "accent": "#8b5cf6", "accent_rgb": "139, 92, 246"},
    {"key": "reit", "x": "61%", "y": "87%", "accent": "#f59e0b", "accent_rgb": "245, 158, 11"},
    {"key": "advisor", "x": "50%", "y": "98%", "accent": "#ec4899", "accent_rgb": "236, 72, 153"},
    {"key": "details", "x": "39%", "y": "87%", "accent": "#06b6d4", "accent_rgb": "6, 182, 212"},
    {"key": "scenario", "x": "20%", "y": "75%", "accent": "#f97316", "accent_rgb": "249, 115, 22"},
    {"key": "ai", "x": "11%", "y": "55%", "accent": "#6366f1", "accent_rgb": "99, 102, 241"},
    {"key": "guide", "x": "15%", "y": "34%", "accent": "#eab308", "accent_rgb": "234, 179, 8"},
    {"key": "settings", "x": "29%", "y": "17%", "accent": "#64748b", "accent_rgb": "100, 116, 139"},
]

NORA_ONTOLOGY_STEPS = [
    {
        "glyph": "WHY",
        "label": "Customer Purpose",
        "tag": "What does the customer want?",
        "color": "#2dd4bf",
        "detail_en": "The user's desired outcome, life priority, time horizon, constraints, and decision question.",
        "detail_ko": "사용자가 원하는 결과, 삶의 우선순위, 기간, 제약조건, 의사결정 질문.",
    },
    {
        "glyph": "PLN",
        "label": "Plan",
        "tag": "Purpose path",
        "color": "#60a5fa",
        "detail_en": "The path that connects the purpose to required capital, sequence, resources, and review rhythm.",
        "detail_ko": "목적을 필요한 자본, 실행 순서, 자원, 점검 리듬과 연결하는 경로.",
    },
    {
        "glyph": "NOW",
        "label": "Situation",
        "tag": "Current reality",
        "color": "#fbbf24",
        "detail_en": "The current reality: capital, income state, expenses, holdings, real estate exposure, liquidity, and risk pressure.",
        "detail_ko": "현재 현실: 자본, 소득 상태, 지출, 보유자산, 부동산 노출, 유동성, 위험 압력.",
    },
    {
        "glyph": "DAT",
        "label": "Data",
        "tag": "Structured inputs",
        "color": "#a7f3d0",
        "detail_en": "Cash flow, assets, debt, stocks, REITs, real estate, goals, and diary snapshots.",
        "detail_ko": "현금흐름, 자산, 부채, 주식, REIT, 부동산, 목표, 다이어리 스냅샷.",
    },
    {
        "glyph": "MOD",
        "label": "Model",
        "tag": "Calculation engine",
        "color": "#fde68a",
        "detail_en": "Valuation, runway, stress, portfolio quality, concentration, and goal projection.",
        "detail_ko": "가치평가, 생존기간, 스트레스, 포트폴리오 품질, 집중도, 목표 전망.",
    },
    {
        "glyph": "EVD",
        "label": "Evidence",
        "tag": "Proof and assumptions",
        "color": "#bfdbfe",
        "detail_en": "Inputs, formulas, source limits, warnings, and confidence signals before interpretation.",
        "detail_ko": "해석 전 입력값, 공식, 데이터 한계, 경고, 신뢰 신호.",
    },
    {
        "glyph": "AI",
        "label": "AI Interpretation",
        "tag": "Reasoning layer",
        "color": "#c4b5fd",
        "detail_en": "Plain-language reading of status, direction, crisis points, and trade-offs.",
        "detail_ko": "현재 상태, 방향, 위기 지점, 선택의 대가를 쉬운 언어로 해석.",
    },
    {
        "glyph": "DEC",
        "label": "Decision",
        "tag": "Action direction",
        "color": "#f9a8d4",
        "detail_en": "Next action, watch item, avoid item, and decision status, without pretending to be advice.",
        "detail_ko": "조언처럼 단정하지 않고 다음 행동, 관찰 항목, 피할 항목, 결정 상태를 정리.",
    },
    {
        "glyph": "MEM",
        "label": "Memory",
        "tag": "Decision log",
        "color": "#fdba74",
        "detail_en": "Diary, report export, review history, and reusable context for later reasoning.",
        "detail_ko": "다이어리, 리포트 내보내기, 검토 이력, 이후 추론에 재사용할 맥락.",
    },
]

NORA_MODULE_MAP = [
    ("Customer Purpose", "life"),
    ("Plan", "finance"),
    ("Situation", "finance"),
    ("Financial Foundation", "finance"),
    ("Market Assets", "portfolio"),
    ("Real Estate", "reit"),
    ("Scenario", "scenario"),
    ("Risk / Resilience", "scenario"),
    ("Evidence", "details"),
    ("AI Interpretation", "ai"),
    ("Decision", "advisor"),
    ("Memory", "diary"),
]


def query_param_value(name: str) -> str | None:
    try:
        value = st.query_params.get(name)
    except Exception:
        params = st.experimental_get_query_params()
        value = params.get(name)

    if isinstance(value, list):
        return value[0] if value else None
    return value


def dashboard_mode_requested() -> bool:
    valid_keys = {item["key"] for item in NAV_ITEMS}
    mode = query_param_value("mode")
    view = query_param_value("view")
    if mode in {"dashboard", "app"}:
        return True
    return view in valid_keys and view != "life"


def active_nav_key() -> str:
    valid_keys = {item["key"] for item in NAV_ITEMS}

    view = query_param_value("view")

    if view in valid_keys:
        st.session_state.active_view = view
        return view

    session_view = st.session_state.get("active_view", "life")
    return session_view if session_view in valid_keys else "life"


def set_active_nav_key(view: str) -> None:
    valid_keys = {item["key"] for item in NAV_ITEMS}
    if view not in valid_keys:
        view = "life"
    st.session_state.active_view = view
    try:
        st.query_params["view"] = view
        st.query_params["mode"] = "dashboard"
        sync_selection_state_to_query()
    except Exception:
        params = {"view": view, "mode": "dashboard"}
        params.update(language_params())
        params.update(selection_state_params())
        st.experimental_set_query_params(**params)


def render_circle_navigation(active_key: str) -> None:
    st.markdown(
        f"""
        <div class="nav-flow-strip" aria-label="ToxiGuard-NORA workflow map">
            <div class="nav-flow-step"><strong>01</strong><span>{ui_html('Life')}<small>{ui_html('Context')}</small></span></div>
            <div class="nav-flow-step"><strong>02</strong><span>{ui_html('Market')}<small>{ui_html('Analysis')}</small></span></div>
            <div class="nav-flow-step scenario"><strong>03</strong><span>{ui_html('Scenario')}<small>{ui_html('Stress Test')}</small></span></div>
            <div class="nav-flow-step ai"><strong>04</strong><span>{ui_html('AI Coach')}<small>{ui_html('Rule-Based Beta')}</small></span></div>
            <div class="nav-flow-step"><strong>05</strong><span>{ui_html('Diary')}<small>{ui_html('Memory')}</small></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    nav_item_map = {item["key"]: item for item in NAV_ITEMS}
    orbit_links = []
    for orbit_item in DESKTOP_ORBIT_ITEMS:
        nav_item = nav_item_map[orbit_item["key"]]
        active_class = " active" if nav_item["key"] == active_key else ""
        href = escape(app_view_href(nav_item["key"]), quote=True)
        style = (
            f"--x: {orbit_item['x']}; --y: {orbit_item['y']}; "
            f"--accent: {orbit_item['accent']}; --accent-rgb: {orbit_item['accent_rgb']};"
        )
        orbit_links.append(
            f'<a class="desktop-orbit-item{active_class}" href="{href}" target="_self" '
            f'aria-label="{ui_html(nav_item["label"])}" style="{style}">'
            f'<b>{escape(nav_item["icon"])}</b><span>{ui_html(nav_item["label"])}</span></a>'
        )

    center_active = " active" if active_key == "diary" else ""
    diary_href = escape(app_view_href("diary"), quote=True)
    st.markdown(
        (
            '<div class="desktop-orbit-nav" aria-label="ToxiGuard-NORA compact orbit navigation">'
            '<div class="desktop-orbit-shell">'
            f'{"".join(orbit_links)}'
            f'<a class="desktop-orbit-center{center_active}" href="{diary_href}" target="_self" aria-label="{ui_html("Financial Diary")}" '
            'style="--accent: #ec4899; --accent-rgb: 236, 72, 153;">'
            f'<b>{ui_html("Diary")}</b><span>{ui_html("Personal Memory")}</span></a>'
            '</div></div>'
        ),
        unsafe_allow_html=True,
    )


def render_mobile_navigation(active_key: str) -> None:
    orbit_items = [
        {"key": "life", "label": "Life", "icon": "LF", "slot": "mobile-orbit-top"},
        {"key": "ai", "label": "AI", "icon": "AI", "slot": "mobile-orbit-top-right"},
        {"key": "portfolio", "label": "Port", "icon": "PF", "slot": "mobile-orbit-right"},
        {"key": "scenario", "label": "Scenario", "icon": "SC", "slot": "mobile-orbit-bottom-right"},
        {"key": "search", "label": "Search", "icon": "SR", "slot": "mobile-orbit-bottom"},
        {"key": "details", "label": "Details", "icon": "DT", "slot": "mobile-orbit-bottom-left"},
        {"key": "finance", "label": "Finance", "icon": "FI", "slot": "mobile-orbit-left"},
        {"key": "reit", "label": "REIT", "icon": "RE", "slot": "mobile-orbit-top-left"},
    ]
    orbit_links = []
    for item in orbit_items:
        active_class = " active" if item["key"] == active_key else ""
        href = escape(app_view_href(item["key"]), quote=True)
        orbit_links.append(
            f'<a class="mobile-orbit-item {item["slot"]}{active_class}" href="{href}" target="_self" aria-label="{ui_html(item["label"])}">'
            f'<b>{escape(item["icon"])}</b><span>{ui_html(item["label"])}</span></a>'
        )
    center_active = " active" if active_key == "diary" else ""
    settings_active = " active" if active_key == "settings" else ""
    guide_active = " active" if active_key == "guide" else ""
    advisor_active = " active" if active_key == "advisor" else ""
    diary_href = escape(app_view_href("diary"), quote=True)
    settings_href = escape(app_view_href("settings"), quote=True)
    guide_href = escape(app_view_href("guide"), quote=True)
    advisor_href = escape(app_view_href("advisor"), quote=True)
    st.markdown(
        (
            '<div class="mobile-orbit-nav mobile-only-deck" aria-label="Mobile ToxiGuard-NORA orbit navigation">'
            f'<div class="mobile-orbit-stamp">{ui_html("Mobile App Mode · Orbit V2")}</div>'
            '<div class="mobile-orbit-shell">'
            f'{"".join(orbit_links)}'
            f'<a class="mobile-orbit-center{center_active}" href="{diary_href}" target="_self" aria-label="{ui_html("Financial Diary")}">'
            f'<b>{ui_html("Diary")}</b><span>{ui_html("Personal Memory")}</span></a></div>'
            '<div class="mobile-orbit-mini-row">'
            f'<a class="mobile-orbit-mini{advisor_active}" href="{advisor_href}" target="_self">{ui_html("Advisor")}</a>'
            f'<a class="mobile-orbit-mini{settings_active}" href="{settings_href}" target="_self">{ui_html("Settings")}</a>'
            f'<a class="mobile-orbit-mini{guide_active}" href="{guide_href}" target="_self">{ui_html("Guide")}</a>'
            '</div></div>'
        ),
        unsafe_allow_html=True,
    )


def render_mobile_view_summary(active_key: str) -> None:
    title_map = {
        "life": "Life Context",
        "finance": "Finance Readiness",
        "portfolio": "Portfolio Check",
        "advisor": "Advisor Reports",
        "ai": "AI Coach",
        "diary": "Diary Memory",
        "scenario": "Scenario Lab",
        "search": "Market Search",
        "compare": "Compare",
        "reit": "REIT",
        "details": "Calculation Details",
        "settings": "Settings",
        "guide": "Guide",
    }
    next_map = {
        "life": "Start with Finance or Search.",
        "finance": "Check surplus, reserve, debt, and savings.",
        "portfolio": "Enter shares and average purchase price.",
        "advisor": "Review virtual clients and export advisor PDF reports.",
        "ai": "Ask one focused question from your current data.",
        "diary": "Save one short next action after review.",
        "scenario": "Run one downside stress test.",
        "search": "Search a ticker, then add it to Portfolio.",
        "compare": "Compare up to three selected stocks.",
        "reit": "Use REIT signals as sector education.",
        "details": "Review formulas before trusting outputs.",
        "settings": "Check API and macro assumptions.",
        "guide": "Use this for professor/demo walkthroughs.",
    }

    if active_key == "finance":
        personal = st.session_state.get("last_personal_finance_result") or {}
        data_text = (
            f"{ui('Financial Health')} {float(personal.get('financial_health_score', 0)):.0f}/100"
            if personal
            else ui("Inputs ready")
        )
    elif active_key == "portfolio":
        data_text = f"{len(st.session_state.get('portfolio', {}))} holding(s)"
    elif active_key == "advisor":
        data_text = "10 virtual clients"
    elif active_key == "ai":
        context = ai_coach_context_snapshot()
        readiness = ai_coach_readiness(context)
        data_text = f"{readiness['label']} {readiness['score']:.0f}/100"
    elif active_key == "diary":
        data_text = f"{len(st.session_state.get('financial_diary', []))} entr{'y' if len(st.session_state.get('financial_diary', [])) == 1 else 'ies'}"
    elif active_key == "scenario":
        data_text = ui("Packet ready") if st.session_state.get("last_scenario_packet") else ui("No packet yet")
    elif active_key == "search":
        data_text = f"{len(st.session_state.get('stocks', {}))} {ui('loaded')}"
    elif active_key == "compare":
        data_text = f"{len(st.session_state.get('compare', []))}/3 {ui('selected')}"
    else:
        data_text = ui("Mobile view")

    st.markdown(
        f"""
        <div class="mobile-only-deck mobile-view-summary">
            <div class="mobile-card-grid">
                <div class="mobile-card"><div class="eyebrow">{ui_html('Now')}</div><div class="value">{ui_html(title_map.get(active_key, 'ToxiGuard-NORA'))}</div><span class="label">{ui_html('Current screen')}</span></div>
                <div class="mobile-card"><div class="eyebrow">{ui_html('Data')}</div><div class="value">{escape(data_text)}</div><span class="label">{ui_html('Context status')}</span></div>
            </div>
            <div class="mobile-focus-card">
                <h3>{ui_html('Next mobile step')}</h3>
                <p>{ui_html(next_map.get(active_key, 'Review the current screen, then ask AI Coach for a linked summary.'))}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_goal_strategy_strip(active_key: str) -> None:
    language = current_language()
    goal = active_goal_key()
    if goal:
        config = NORA_GOAL_STRATEGIES[goal]
        label = config[f"label_{language}"]
        short = config[f"short_{language}"]
        strategy = config[f"strategy_{language}"]
        color = config["color"]
        target_href = escape(goal_href(goal), quote=True)
        target_text = "Open strategy screen" if language == "en" else "전략 화면 열기"
    else:
        label = "Choose a Goal" if language == "en" else "Goal 선택"
        short = "Strategy starts after the goal." if language == "en" else "목표가 정해지면 전략이 바뀝니다."
        strategy = (
            "Select a goal on the first screen to focus finance, portfolio, income, or real-estate analysis."
            if language == "en"
            else "첫 화면에서 목표를 선택하면 재무, 포트폴리오, 소득, 부동산 분석의 우선순위가 달라집니다."
        )
        color = "#64748b"
        target_href = escape(app_view_href("life"), quote=True)
        target_text = "Choose goal" if language == "en" else "목표 선택"

    detail_label = "Detail" if language == "en" else "상세"
    st.markdown(
        f"""
        <section class="goal-strategy-strip" style="--goal-color: {escape(color)};" aria-label="Selected goal strategy">
            <div class="goal-strategy-mark"></div>
            <div class="goal-strategy-main">
                <b>{escape(label)}</b>
                <span>{escape(short)}</span>
            </div>
            <details class="goal-strategy-detail">
                <summary>{escape(detail_label)}</summary>
                <p>{escape(strategy)}</p>
                <a href="{target_href}" target="_self">{escape(target_text)}</a>
            </details>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_life_compact_panel() -> None:
    language = current_language()
    compact_title = "Goal Board" if language == "en" else "Goal 보드"
    compact_copy = (
        "Pick the goal that should drive today's strategy."
        if language == "en"
        else "오늘의 전략을 바꿀 목표를 선택하세요."
    )
    cards = []
    for goal_key, config in NORA_GOAL_STRATEGIES.items():
        cards.append(
            f'<a class="life-goal-link" style="--goal-color: {escape(config["color"])};" '
            f'href="{escape(goal_href(goal_key), quote=True)}" target="_self">'
            f'<span>{escape(config["icon"])}</span><b>{escape(config[f"label_{language}"])}</b>'
            '</a>'
        )
    st.markdown(
        f"""
        <div class="life-compact-panel">
            <h1>{escape(compact_title)}</h1>
            <p>
                {escape(compact_copy)}
            </p>
            <div class="life-goal-board">
                {"".join(cards)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_main_app() -> None:
    sync_selection_state_from_query()
    sync_selected_detail_from_query()

    render_sidebar()

    search_href = escape(app_view_href("search"), quote=True)
    brand_subtitle = (
        "개인 의사결정 인텔리전스"
        if current_language() == "ko"
        else "PERSONAL DECISION INTELLIGENCE"
    )
    st.markdown(
        f"""
        <div class="brand-header">
            <div class="brand-mark">
                <div class="brand-icon" aria-hidden="true"></div>
                <div>
                    <div class="brand-name">ToxiGuard<span class="scope-accent">-NORA</span></div>
                    <div class="brand-subtitle">{brand_subtitle}</div>
                </div>
            </div>
            <a class="brand-badge brand-search-badge" href="{search_href}" target="_self" aria-label="{ui_html('Open Search')}">
                <span class="brand-search-icon" aria-hidden="true">
                    <svg class="brand-search-sigil" viewBox="0 0 44 44" focusable="false">
                        <path d="M10 27 C15 12 29 10 34 21 C38 30 25 36 15 31"></path>
                        <circle cx="33" cy="16" r="3.5"></circle>
                        <path d="M28 28 L36 36"></path>
                    </svg>
                    <span class="brand-search-initials">SR</span>
                </span>
                <span class="brand-search-label">{ui_html('Search')}</span>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    active_view = active_nav_key()
    render_goal_strategy_strip(active_view)
    render_nora_ontology(active_view)
    render_mobile_navigation(active_view)
    render_circle_navigation(active_view)
    render_mobile_view_summary(active_view)

    if active_view == "life":
        render_life_compact_panel()
    elif active_view == "search":
        search_tab()
    elif active_view == "compare":
        compare_tab()
    elif active_view == "portfolio":
        portfolio_tab()
    elif active_view == "advisor":
        render_advisor_reports_tab()
    elif active_view == "reit":
        from reit_analysis_module import main as render_reit_analysis

        render_reit_analysis(include_sidebar=False)
    elif active_view == "finance":
        from personal_finance_module import render_personal_finance

        render_personal_finance()
    elif active_view == "scenario":
        what_if_scenario_tab()
    elif active_view == "details":
        calculation_details_tab()
    elif active_view == "ai":
        ai_reasoning_readiness_tab()
    elif active_view == "diary":
        financial_diary_tab()
    elif active_view == "settings":
        settings_tab()
    elif active_view == "guide":
        guide_tab()

    render_footer()


init_state()
render_top_language_toggle()
if dashboard_mode_requested():
    st.session_state.life_entry_complete = True
    st.session_state.life_entry_version_seen = LIFE_ENTRY_VERSION
show_life_entry = (
    not st.session_state.life_entry_complete
    or st.session_state.life_entry_version_seen != LIFE_ENTRY_VERSION
)
if show_life_entry:
    render_life_entry_screen()
else:
    render_main_app()

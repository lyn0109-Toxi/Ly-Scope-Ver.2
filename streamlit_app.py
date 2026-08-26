import math
import os
import json
import base64
import importlib
from html import escape
from io import StringIO
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


st.set_page_config(page_title="LY-Scope-Ver.2", layout="wide")

APP_BUILD_STAMP = "2026-08-24-visual-design-b409cd4"

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
    "Use the Real Estate Valuation tab in the main screen.": "메인 화면의 부동산 가치평가 메뉴를 사용하세요.",
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
    "LY-Scope-Ver.2 is a Personal Decision Intelligence Application for financial foundation, goals, market assets, real estate, scenarios, risk, evidence, decisions, and memory.": "LY-Scope-Ver.2는 재무 기반, 목표, 시장 자산, 부동산, 시나리오, 위험, 근거, 결정, 메모리를 연결하는 개인 의사결정 인텔리전스 앱입니다.",
    "See Your": "나의",
    "Financial Path": "금융 경로",
    "What Does the Customer Want?": "고객은 무엇을 원하는가?",
    "NORA begins with purpose, then reads the strategy and current situation.": "NORA는 목적에서 시작해 전략과 현재 상황을 읽습니다.",
    "Customer Purpose": "고객 목적",
    "Purpose": "목적",
    "Plan": "계획",
    "Situation": "상황",
    "What does the customer want?": "고객은 무엇을 원하는가?",
    "Purpose path": "목적 경로",
    "Strategy path": "전략 경로",
    "Current reality": "현재 현실",
    "NORA Purpose Map": "NORA 목적 맵",
    "Why": "이유",
    "Path": "경로",
    "Inputs": "입력",
    "Proof": "증명",
    "Review": "검토",
    "NORA Purpose Control Center": "NORA 목적 컨트롤 센터",
    "NORA starts with what the customer wants, then connects the strategy, current situation, evidence, decision, and memory.": "NORA는 고객이 원하는 것에서 시작한 뒤 전략, 현재 상황, 근거, 결정, 메모리를 연결합니다.",
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
    "NORA asks purpose first, then turns the strategy and situation into evidence.": "NORA는 목적을 먼저 묻고, 전략과 상황을 근거로 바꿉니다.",
    "NORA starts with the customer purpose, then checks the strategy and current situation before any model.": "NORA는 고객의 목적에서 시작하고, 어떤 모델보다 먼저 전략과 현재 상황을 확인합니다.",
    "A calm visual map for current situation, direction, crisis signals, and memory.": "현재 상황, 목표 방향, 위험 신호, 메모리를 차분하게 보여주는 시각 맵입니다.",
    "Current Situation": "현재 상황",
    "Capital, cash flow, portfolio, and goal context in one view.": "자본, 현금흐름, 포트폴리오, 목표 맥락을 한눈에 봅니다.",
    "Direction": "목표 방향",
    "What path needs attention next.": "다음에 집중해야 할 경로를 확인합니다.",
    "Crisis Signals": "위험 신호",
    "Where liquidity, concentration, rates, or market shocks could interrupt the strategy.": "유동성, 집중도, 금리, 시장 충격이 전략을 끊을 수 있는 지점을 봅니다.",
    "Use the visual signals first. Details appear when you hover or click.": "먼저 시각 신호를 보고, 세부 내용은 마우스를 올리거나 클릭할 때 확인하세요.",
    "Open Dashboard": "대시보드 열기",
    "Educational prototype only; not financial, investment, legal, or tax advice.": "교육용 프로토타입입니다. 금융, 투자, 법률, 세무 조언이 아닙니다.",
    "Start Your Life Map": "라이프 맵 시작",
    "Explore Dashboard": "대시보드 살펴보기",
    "Enter LY-Scope-Ver.2 Dashboard": "LY-Scope-Ver.2 대시보드로 들어가기",
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
    "Goal": "목표",
    "Strategy": "전략",
    "Detail": "상세",
    "Planning": "계획",
    "Diary": "다이어리",
    "Reflection": "회고",
    "Stock Valuation": "주식 가치평가",
    "Fair value, valuation status, and real market context.": "적정가치, 가치평가 상태, 실제 시장 맥락.",
    "Investment Portfolio": "투자 포트폴리오",
    "Risk, return, and valuation across holdings": "보유 종목의 위험, 수익, 가치평가",
    "Find Stock for Portfolio": "포트폴리오 종목 찾기",
    "SR · Portfolio Search": "SR · 포트폴리오 검색",
    "Search ticker/company, review valuation, then add it to this portfolio.": "티커/회사명을 검색하고 가치평가를 확인한 뒤 포트폴리오에 추가합니다.",
    "Ticker or company search with valuation, risk, and portfolio action.": "티커 또는 회사명으로 가치평가, 위험, 포트폴리오 행동을 확인합니다.",
    "Ticker or company name": "티커 또는 회사명",
    "Ticker or company name: NVDA, AAPL, 삼성전자, NAVER": "티커 또는 회사명: NVDA, AAPL, 삼성전자, NAVER",
    "Search and Value Stock": "검색 및 가치평가",
    "Price unavailable": "가격 미확보",
    "Position input": "포지션 입력",
    "Current value amount": "현재 보유 금액",
    "Share count": "주식 수량",
    "Position size": "보유 규모",
    "Average purchase price (optional)": "평균 매입가 (선택)",
    "Enter position size before adding.": "추가하기 전에 보유 규모를 입력하세요.",
    "Add Position to Portfolio": "포지션을 포트폴리오에 추가",
    "Position added to portfolio.": "포지션이 포트폴리오에 추가되었습니다.",
    "Already in Portfolio": "이미 포트폴리오에 있음",
    "Open Full Stock Detail": "전체 종목 상세 열기",
    "Live Yahoo price history": "Yahoo 가격 이력",
    "Yahoo profile price": "Yahoo 프로필 가격",
    "Profile-only fallback; live Yahoo price unavailable": "프로필 기반 표시; 실시간 가격 미확보",
    "Fair Value": "적정가치",
    "Portfolio base currency": "포트폴리오 기준 통화",
    "Use live USD/KRW": "실시간 USD/KRW 사용",
    "Manual USD/KRW rate": "수동 USD/KRW 환율",
    "Portfolio weighting mode": "포트폴리오 가중 방식",
    "Share-based": "보유 수량 기준",
    "Equal-weighted": "동일 비중 기준",
    "Total Market Value": "총 시장가치",
    "Weighted Beta": "가중 베타",
    "Portfolio Valuation Score": "포트폴리오 가치평가 점수",
    "Native currency breakdown": "통화별 보유 금액",
    "shares": "수량",
    "average purchase price": "평균 매입가",
    "Enter each holding's average purchase price to compare your cost basis with current market value.": "평균 매입가를 입력하면 원가 기준과 현재 시장가치를 비교할 수 있습니다.",
    "Portfolio Resilience Score": "포트폴리오 회복력 점수",
    "Portfolio Score": "포트폴리오 점수",
    "Top Holding": "최대 보유 비중",
    "Top Sector": "최대 섹터 비중",
    "Ask AI Coach About Portfolio P/L": "포트폴리오 손익에 대해 AI 코치에게 묻기",
    "Remove": "삭제",
    "Quick Portfolio Entry": "빠른 포트폴리오 입력",
    "Paste one holding per line: ticker, current value or shares, optional average purchase price. Current value amount should be in the stock's native currency.": "한 줄에 한 종목씩 입력하세요: 티커, 현재 보유 금액 또는 수량, 선택 사항으로 평균 매입가. 현재 보유 금액은 해당 종목의 통화 기준입니다.",
    "Quick input type": "빠른 입력 방식",
    "Holdings input": "보유 종목 입력",
    "Apply Holdings": "보유 종목 적용",
    "For a KRW 200M stock portfolio, enter each position value in KRW for Korean stocks or USD for U.S. stocks. The app estimates shares from current price.": "2억원 규모의 주식 포트폴리오는 한국 종목은 원화, 미국 종목은 달러로 각 포지션 금액을 입력하세요. 앱이 현재가 기준 수량을 추정합니다.",
    "No stocks in your portfolio yet. Add them from the search results.": "아직 포트폴리오에 종목이 없습니다. 검색 결과에서 추가하세요.",
    "Ask AI Coach About Portfolio Setup": "포트폴리오 구성에 대해 AI 코치에게 묻기",
    "Portfolio valuation lens": "포트폴리오 가치평가 렌즈",
    "Portfolio valuation basis": "포트폴리오 가치평가 근거",
    "Risk-Free Rate": "무위험수익률",
    "Risk-Free Rate Source": "무위험수익률 출처",
    "Risk-Free Rate Date": "무위험수익률 기준일",
    "U.S. 10Y Treasury Yield": "미국 10년물 국채금리",
    "Use U.S. 10Y Treasury yield as Risk-Free Rate": "미국 10년물 국채금리를 무위험수익률로 사용",
    "Refresh U.S. 10Y Treasury yield": "미국 10년물 국채금리 새로고침",
    "Manual CAPM input": "수동 CAPM 입력값",
    "Rate unavailable": "금리 미확보",
    "Upside": "상승여력",
    "Current price": "현재가",
    "blended fair value": "종합 적정가치",
    "Risk": "위험",
    "drives the volatility read for portfolio fit.": "는 포트폴리오 적합성의 변동성 판단에 사용됩니다.",
    "Valuation Models": "가치평가 모델",
    "Income, asset, and market approaches are checked when source inputs are available.": "입력값이 있으면 수익, 자산, 시장 접근법을 함께 확인합니다.",
    "Growth / Quality": "성장 / 퀄리티",
    "Growth": "성장률",
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
    "Real Estate Valuation": "부동산 가치평가",
    "Property value, rent yield, cash flow, and rate sensitivity lens.": "부동산 가치, 임대수익률, 현금흐름, 금리 민감도 관점.",
    "Portfolio Diversification": "포트폴리오 분산",
    "Risk, covariance, correlation, and complementarity.": "위험, 공분산, 상관관계, 보완성.",
    "Financial Health": "재무 건강도",
    "Cash flow, savings, debt, liquidity, and capacity.": "현금흐름, 저축, 부채, 유동성, 감당 능력.",
    "Financial Diary": "금융 다이어리",
    "Advisor Reports": "어드바이저 리포트",
    "Advisor": "어드바이저",
    "Portfolio / SR": "포트폴리오 / SR",
    "Goal-first mobile map": "목표 중심 모바일 맵",
    "Rationality Gate": "합리성 게이트",
    "Disciplined": "절제됨",
    "Developing": "형성 중",
    "Fragile": "취약",
    "Rationality means goal-fit, evidence, model discipline, risk awareness, and memory before action.": "합리성은 행동 전에 목표 적합성, 근거, 모델 절제, 위험 인식, 기억이 연결되는지를 뜻합니다.",
    "Purpose → Evidence → Risk → Memory": "목적 → 근거 → 위험 → 기억",
    "Purpose Fit": "목적 적합성",
    "Evidence Quality": "근거 품질",
    "Model Discipline": "모델 절제",
    "Risk Awareness": "위험 인식",
    "Memory Feedback": "기억 피드백",
    "Evidence": "근거",
    "Status": "상태",
    "Age": "나이",
    "Currency": "통화",
    "Save snapshots, notes, next actions, and reflection.": "스냅샷, 메모, 다음 행동, 회고 저장.",
    "AI Scenario Readiness": "AI 시나리오 준비도",
    "Prepare structured context for future reasoning assistants.": "향후 추론형 AI를 위한 구조화된 맥락 준비.",
    "Click the image buttons on desktop or Enter LY-Scope-Ver.2 Dashboard on mobile. Educational and informational use only; not financial, investment, legal, or tax advice.": "데스크톱에서는 이미지 버튼을, 모바일에서는 LY-Scope-Ver.2 대시보드 진입 버튼을 누르세요. 교육 및 정보 제공용이며 금융, 투자, 법률, 세무 조언이 아닙니다.",
    "Life": "라이프",
    "Finance": "재무",
    "Diary": "다이어리",
    "Client": "고객",
    "Search": "검색",
    "Compare": "비교",
    "Real Estate": "부동산",
    "Details": "계산",
    "Scenario": "시나리오",
    "AI Coach": "AI 코치",
    "NORA Path": "NORA 경로",
    "Goal → Strategy → Situation → AI Coach": "목표 → 전략 → 상황 → AI 코치",
    "Choose the customer purpose first.": "고객의 목표를 먼저 선택합니다.",
    "Follow the strategy selected by the goal.": "목표가 선택한 전략을 따라갑니다.",
    "Read cash flow, capital, risk, and runway.": "현재 현금흐름, 자본, 위험, 생존기간을 확인합니다.",
    "Ask for a linked interpretation.": "근거를 쉬운 해석으로 바꿉니다.",
    "Selected goal": "선택된 목표",
    "No goal selected": "선택된 목표 없음",
    "Choose a goal to set strategy.": "목표를 선택하면 전략이 정해집니다.",
    "Support Lists": "보조 목록",
    "Selected stocks": "선택 종목",
    "Portfolio holdings": "포트폴리오 보유",
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
    "Start with a goal, then Finance or Portfolio.": "목표를 먼저 고른 뒤 재무 또는 포트폴리오로 이동하세요.",
    "Check surplus, reserve, debt, and savings.": "잉여 현금, 비상자금, 부채, 저축을 확인하세요.",
    "Enter shares and average purchase price.": "보유 수량과 평균 매입가를 입력하세요.",
    "Ask one focused question from your current data.": "현재 데이터 기준으로 한 가지 질문을 던져 보세요.",
    "Save one short next action after review.": "검토 후 짧은 다음 행동 하나를 저장하세요.",
    "Run one downside stress test.": "하방 스트레스 테스트를 하나 실행하세요.",
    "Search a ticker, then add it to Portfolio.": "티커를 검색한 뒤 포트폴리오에 추가하세요.",
    "Compare up to three selected stocks.": "선택한 종목을 최대 3개까지 비교하세요.",
    "Review property value and rent cash flow first.": "부동산 가치와 임대 현금흐름을 먼저 확인하세요.",
    "Review formulas before trusting outputs.": "결과를 신뢰하기 전에 공식을 확인하세요.",
    "Check API and macro assumptions.": "API와 거시 가정을 확인하세요.",
    "Use this for professor/demo walkthroughs.": "교수님/데모 설명용으로 사용하세요.",
    "Review virtual clients and export advisor PDF reports.": "가상 고객을 검토하고 어드바이저 PDF 리포트를 내보내세요.",
    "Review virtual clients through the LY-Scope-Ver.2 decision architecture and export PDF reports.": "LY-Scope-Ver.2 의사결정 아키텍처로 가상 고객을 검토하고 PDF 리포트를 내보내세요.",
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
    "LY-Scope-Ver.2 connects customer purpose, strategy, situation, financial data, models, evidence, AI interpretation, decisions, and memory. Use the circular menu above to move between valuation, portfolio risk, real estate exposure, personal finance, scenario stress testing, AI readiness, calculation transparency, and diary reflection.": "LY-Scope-Ver.2는 고객 목적, 전략, 상황, 금융 데이터, 모델, 근거, AI 해석, 결정, 메모리를 연결합니다. 위 원형 메뉴로 가치평가, 포트폴리오 위험, 부동산 노출, 개인 재무, 시나리오 스트레스 테스트, AI 준비도, 계산 투명성, 다이어리 회고를 이동하세요.",
    "Understand monthly cash flow before taking investment risk.": "투자 위험을 감수하기 전 월 현금흐름을 이해하세요.",
    "Check liquidity and emergency capacity.": "유동성과 비상 대응력을 확인하세요.",
    "Investments": "투자",
    "Review stock value, beta, risk, and diversification.": "주식 가치, 베타, 위험, 분산을 검토하세요.",
    "Real Estate": "부동산",
    "Review property value, rent support, cash flow, and rate sensitivity.": "부동산 가치, 임대수익 지지력, 현금흐름, 금리 민감도를 확인하세요.",
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
    "NORA keeps every screen tied to the same decision path: customer purpose, strategy, situation, evidence, interpretation, decision, and memory.": "NORA는 모든 화면을 고객 목적, 전략, 상황, 근거, 해석, 결정, 기억이라는 동일한 의사결정 경로에 연결합니다.",
    "Hover or click each visual node to read its role.": "각 시각 노드에 마우스를 올리거나 클릭하면 역할을 볼 수 있습니다.",
    "LY-Scope-Ver.2 is provided for educational and informational use only and does not constitute or provide financial, investment, legal, tax, accounting, or professional advice. Do not enter sensitive personal financial information into this prototype. Market data and charts may be provided by third-party services such as Finnhub, TradingView, and Yahoo Finance/yfinance, subject to their own terms. All trademarks, company names, and ticker symbols remain the property of their respective owners. This interface uses original CSS/HTML design elements and does not claim ownership of third-party data, logos, or trademarks. Data may be delayed, incomplete, or unavailable and should be verified independently.": "LY-Scope-Ver.2는 교육 및 정보 제공용이며 금융, 투자, 법률, 세무, 회계 또는 전문 조언을 제공하지 않습니다. 이 프로토타입에 민감한 개인 금융 정보를 입력하지 마세요. 시장 데이터와 차트는 Finnhub, TradingView, Yahoo Finance/yfinance 등 제3자 서비스에서 제공될 수 있으며 각 서비스 약관을 따릅니다. 모든 상표, 회사명, 티커 심볼은 각 소유자의 자산입니다. 이 인터페이스는 자체 CSS/HTML 디자인 요소를 사용하며 제3자 데이터, 로고, 상표의 소유권을 주장하지 않습니다. 데이터는 지연되거나 불완전하거나 제공되지 않을 수 있으므로 독립적으로 검증해야 합니다.",
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
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    .block-container {
        padding-top: 0.65rem !important;
    }
    .stApp {
        background:
            linear-gradient(90deg, rgba(34,211,238,0.035) 1px, transparent 1px),
            linear-gradient(0deg, rgba(20,184,166,0.030) 1px, transparent 1px),
            linear-gradient(135deg, #eef7f3 0%, #f8fafc 52%, #f4f0e6 100%);
        background-size: 42px 42px, 42px 42px, auto;
        color: #0f172a;
    }
    .stApp::before {
        display: none !important;
    }
    .stApp::after {
        display: none !important;
    }
    .top-language-toggle {
        position: fixed;
        top: 12px;
        right: 24px;
        z-index: 100000;
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.14);
        backdrop-filter: blur(14px);
    }
    .top-language-toggle .language-toggle-mark,
    .top-language-toggle a {
        width: 30px;
        height: 30px;
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
        color: #0f766e;
        background: rgba(20, 184, 166, 0.15);
        border: 1px solid rgba(45, 212, 191, 0.24);
    }
    .top-language-toggle a {
        color: #334155 !important;
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
        color: #ffffff !important;
        background: #0f766e;
        border-color: #0f766e;
        box-shadow: 0 8px 18px rgba(15, 118, 110, 0.20);
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
        padding: 9px 14px;
        font-size: 0.86rem;
        font-weight: 950;
        white-space: nowrap;
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.14);
    }
    .portfolio-price-stage {
        display: grid;
        grid-template-columns: 1.05fr 1.05fr 0.9fr;
        gap: 10px;
        margin-top: 14px;
    }
    .portfolio-price-card {
        border: 1px solid #d8e2ef;
        border-radius: 8px;
        background: #ffffff;
        padding: 14px 15px;
        min-height: 122px;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
        position: relative;
        overflow: hidden;
    }
    .portfolio-price-card::before {
        content: "";
        position: absolute;
        inset: 0 0 auto;
        height: 4px;
        background: var(--accent, #0ea5e9);
    }
    .portfolio-price-card.market { --accent: #0ea5e9; }
    .portfolio-price-card.fair { --accent: #14b8a6; }
    .portfolio-price-card.signal.up { --accent: #059669; background: #f0fdf4; }
    .portfolio-price-card.signal.down { --accent: #dc2626; background: #fef2f2; }
    .portfolio-price-card.signal.flat { --accent: #f59e0b; background: #fffbeb; }
    .portfolio-price-label {
        color: #52657f;
        font-size: 0.76rem;
        font-weight: 950;
        text-transform: uppercase;
    }
    .portfolio-price-value {
        color: #0f172a;
        font-size: clamp(1.6rem, 3vw, 2.35rem);
        line-height: 1;
        font-weight: 950;
        margin-top: 12px;
        overflow-wrap: anywhere;
    }
    .portfolio-price-card.signal .portfolio-price-value {
        color: var(--accent);
    }
    .portfolio-price-note {
        color: #475569;
        font-size: 0.78rem;
        font-weight: 800;
        line-height: 1.28;
        margin-top: 10px;
    }
    .portfolio-price-note b {
        color: #0f172a;
        font-weight: 950;
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
        .portfolio-price-stage {
            grid-template-columns: 1fr;
        }
        .portfolio-price-card {
            min-height: 104px;
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
    .nora-sidebar-path {
        display: grid;
        gap: 8px;
        margin: 12px 0 14px;
    }
    .nora-sidebar-link {
        display: grid;
        grid-template-columns: 36px minmax(0, 1fr);
        align-items: center;
        gap: 10px;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(255, 255, 255, 0.62);
        text-decoration: none !important;
        color: #102033 !important;
        box-shadow: 0 10px 24px rgba(14, 116, 144, 0.08);
    }
    .nora-sidebar-link:hover,
    .nora-sidebar-link:focus {
        border-color: rgba(14, 165, 233, 0.44);
        background: rgba(240, 249, 255, 0.92);
    }
    .nora-sidebar-link.active {
        border-color: rgba(15, 118, 110, 0.52);
        background: linear-gradient(135deg, rgba(240, 253, 250, 0.96), rgba(224, 242, 254, 0.92));
    }
    .nora-sidebar-step {
        width: 34px;
        height: 34px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 950;
        font-size: 0.72rem;
        color: #063b44;
        background: rgba(103, 232, 249, 0.46);
        border: 1px solid rgba(14, 165, 233, 0.22);
    }
    .nora-sidebar-link b {
        display: block;
        color: #0f172a;
        font-size: 0.92rem;
        line-height: 1.1;
    }
    .nora-sidebar-link span:last-child {
        display: block;
        margin-top: 3px;
        color: #475569;
        font-size: 0.74rem;
        line-height: 1.2;
    }
    .nora-sidebar-goal {
        margin: 4px 0 12px;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid rgba(14, 165, 233, 0.22);
        background: rgba(255, 255, 255, 0.56);
        color: #334155;
        font-size: 0.82rem;
        line-height: 1.35;
    }
    .nora-sidebar-goal b {
        display: block;
        color: #0f172a;
        margin-bottom: 3px;
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
            linear-gradient(90deg, rgba(14,165,233,0.075) 1px, transparent 1px),
            linear-gradient(0deg, rgba(20,184,166,0.055) 1px, transparent 1px),
            linear-gradient(135deg, #f8fcff 0%, #eaf7ff 42%, #fff8e8 100%) !important;
        background-size: 58px 58px, 58px 58px, auto !important;
        color: #102033;
    }
    .stApp::before {
        display: none !important;
    }
    .stApp::after {
        display: none !important;
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
        background: #ffffff !important;
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
        grid-template-columns: 8px minmax(0, 1fr) auto;
        gap: 9px;
        align-items: center;
        margin: 4px 0 7px;
        padding: 8px 11px;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        background: #ffffff;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }
    html body .stApp .brand-header {
        min-height: 44px !important;
        padding: 6px 12px !important;
        margin: 0 0 7px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 9px !important;
        border-radius: 8px !important;
        background: #ffffff !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05) !important;
    }
    html body .stApp .brand-mark {
        gap: 8px !important;
    }
    html body .stApp .brand-icon {
        width: 28px !important;
        height: 28px !important;
        border-radius: 8px !important;
    }
    html body .stApp .brand-name {
        font-size: 1.14rem !important;
        line-height: 1 !important;
        letter-spacing: 0 !important;
    }
    html body .stApp .brand-subtitle {
        display: none !important;
    }
    html body .stApp .brand-badge {
        min-height: 32px !important;
        padding: 0 9px !important;
        border-radius: 8px !important;
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
        width: 8px;
        height: 34px;
        border-radius: 8px;
        background: var(--goal-color);
    }
    html body .stApp .goal-strategy-main b {
        display: block;
        color: #0f172a;
        font-size: 0.88rem;
        line-height: 1.15;
    }
    html body .stApp .goal-strategy-main span {
        display: block;
        margin-top: 2px;
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 650;
    }
    html body .stApp .goal-strategy-detail summary {
        min-height: 30px;
        padding: 0 10px;
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
    html body .stApp .rationality-gate {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto auto auto;
        gap: 9px;
        align-items: center;
        margin: 4px 0 7px;
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        background: #ffffff;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }
    html body .stApp .rationality-gate-main b {
        display: block;
        color: #0f172a;
        font-size: 0.84rem;
        line-height: 1.1;
        font-weight: 900;
    }
    html body .stApp .rationality-gate-main span {
        display: block;
        margin-top: 2px;
        color: #64748b;
        font-size: 0.70rem;
        line-height: 1.25;
        font-weight: 650;
    }
    html body .stApp .rationality-score {
        min-width: 74px;
        display: grid;
        grid-template-columns: auto auto;
        align-items: end;
        justify-content: center;
        column-gap: 2px;
        color: var(--rational-color);
    }
    html body .stApp .rationality-score strong {
        font-size: 1.08rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .rationality-score small {
        color: #64748b;
        font-size: 0.70rem;
        line-height: 1.1;
        font-weight: 800;
    }
    html body .stApp .rationality-score em {
        grid-column: 1 / -1;
        color: #475569;
        font-size: 0.68rem;
        line-height: 1.1;
        font-style: normal;
        font-weight: 850;
        text-align: center;
    }
    html body .stApp .rationality-nodes {
        display: flex;
        align-items: center;
        gap: 7px;
    }
    html body .stApp .rationality-node {
        --node-color: #d97706;
        width: 30px;
        height: 30px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        position: relative;
        background: conic-gradient(var(--node-color) var(--value), #e2e8f0 0);
        cursor: help;
    }
    html body .stApp .rationality-node.good { --node-color: #0f766e; }
    html body .stApp .rationality-node.mid { --node-color: #2563eb; }
    html body .stApp .rationality-node.watch { --node-color: #d97706; }
    html body .stApp .rationality-node::after {
        content: "";
        position: absolute;
        inset: 4px;
        border-radius: 7px;
        background: #ffffff;
    }
    html body .stApp .rationality-node b {
        position: relative;
        z-index: 1;
        color: #0f172a;
        font-size: 0.54rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .rationality-detail summary {
        min-height: 29px;
        padding: 0 10px;
        display: inline-flex;
        align-items: center;
        border-radius: 8px;
        color: #334155;
        background: #f8fafc;
        border: 1px solid rgba(148, 163, 184, 0.22);
        font-size: 0.76rem;
        font-weight: 780;
        cursor: pointer;
        list-style: none;
    }
    html body .stApp .rationality-detail summary::-webkit-details-marker {
        display: none;
    }
    html body .stApp .rationality-detail ul {
        min-width: min(520px, 82vw);
        margin: 9px 0 0;
        padding: 0;
        list-style: none;
    }
    html body .stApp .rationality-detail li {
        display: grid;
        grid-template-columns: 128px minmax(0, 1fr);
        gap: 10px;
        padding: 7px 0;
        border-top: 1px solid rgba(148, 163, 184, 0.16);
        color: #334155;
        font-size: 0.78rem;
        line-height: 1.35;
    }
    html body .stApp .rationality-detail li b {
        color: #0f172a;
        font-size: 0.76rem;
    }
    html body .stApp .nora-ontology {
        margin: 4px 0 8px !important;
        padding: 0 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        background: #ffffff !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05) !important;
    }
    html body .stApp .nora-ontology summary {
        min-height: 34px;
        padding: 0 11px;
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
        font-size: 0.78rem;
        font-weight: 860;
    }
    html body .stApp .nora-ontology summary span {
        color: #64748b;
        font-size: 0.70rem;
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
        margin: 4px 0 9px !important;
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
        grid-template-columns: repeat(auto-fit, minmax(84px, 1fr)) !important;
        gap: 7px !important;
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
        height: 32px !important;
        min-width: 0 !important;
        padding: 0 9px !important;
        display: inline-flex !important;
        justify-content: center !important;
        flex-direction: row !important;
        gap: 6px !important;
        border-radius: 8px !important;
        transform: none !important;
        color: #334155 !important;
        -webkit-text-fill-color: currentColor !important;
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
        font-size: 0.64rem !important;
        -webkit-text-fill-color: currentColor !important;
    }
    html body .stApp .desktop-orbit-center span,
    html body .stApp .desktop-orbit-item span {
        color: inherit !important;
        -webkit-text-fill-color: currentColor !important;
        font-size: 0.72rem !important;
        font-weight: 760 !important;
        line-height: 1 !important;
    }
    html body .stApp .desktop-orbit-item.active,
    html body .stApp .desktop-orbit-center.active {
        color: #ffffff !important;
        -webkit-text-fill-color: currentColor !important;
        background: #0f766e !important;
        border-color: #0f766e !important;
    }
    html body .stApp .portfolio-title-strip {
        width: min(1120px, 100%);
        margin: 4px auto 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        min-height: 36px;
        padding: 8px 10px;
        border-radius: 8px;
        color: #0f172a;
        background: #f8fafc;
        border: 1px solid rgba(148, 163, 184, 0.18);
    }
    html body .stApp .portfolio-title-strip b {
        color: #0f172a;
        font-size: 0.96rem;
        line-height: 1;
        font-weight: 900;
    }
    html body .stApp .portfolio-title-strip span {
        color: #64748b;
        font-size: 0.78rem;
        line-height: 1.15;
        font-weight: 760;
        text-align: right;
    }
    html body .stApp .portfolio-sr-header {
        width: min(1120px, 100%);
        margin: 4px auto 8px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 8px;
        color: #0f172a;
        background: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }
    html body .stApp .portfolio-sr-header span {
        width: 30px;
        height: 30px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        color: #ffffff;
        background: #0f766e;
        font-size: 0.72rem;
        font-weight: 950;
    }
    html body .stApp .portfolio-sr-header b {
        color: #0f172a;
        font-size: 0.92rem;
        line-height: 1;
        font-weight: 900;
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
        html body .stApp .rationality-gate {
            grid-template-columns: minmax(0, 1fr);
        }
        html body .stApp .rationality-score {
            justify-content: flex-start;
        }
        html body .stApp .rationality-detail li {
            grid-template-columns: 1fr;
            gap: 3px;
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
    html body .stApp .homepage-visual.has-home-image {
        position: relative !important;
        overflow: hidden !important;
        max-width: 1180px !important;
        min-height: 640px !important;
        background: #ffffff !important;
        border-color: rgba(14, 116, 144, 0.16) !important;
        box-shadow: 0 24px 64px rgba(15, 23, 42, 0.16) !important;
    }
    html body .stApp .homepage-visual.has-home-image .homepage-bg-img {
        position: absolute !important;
        inset: 0 !important;
        z-index: 0 !important;
        width: 100% !important;
        height: 100% !important;
        aspect-ratio: auto !important;
        object-fit: cover !important;
        object-position: center center !important;
        opacity: 0.88 !important;
    }
    html body .stApp .homepage-visual.has-home-image::before {
        content: "" !important;
        display: block !important;
        position: absolute !important;
        inset: 0 !important;
        z-index: 1 !important;
        pointer-events: none !important;
        opacity: 1 !important;
        background:
            linear-gradient(90deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.92) 34%, rgba(255, 255, 255, 0.62) 58%, rgba(255, 255, 255, 0.18) 100%),
            linear-gradient(180deg, rgba(248, 250, 252, 0.22), rgba(236, 253, 245, 0.20)) !important;
    }
    html body .stApp .homepage-visual.has-home-image::after {
        display: none !important;
    }
    html body .stApp .homepage-visual.has-home-image .home-nav,
    html body .stApp .homepage-visual.has-home-image .home-goal-layout {
        position: relative !important;
        z-index: 2 !important;
    }
    html body .stApp .homepage-visual.has-home-image .home-nav {
        display: flex !important;
        background: rgba(255, 255, 255, 0.76) !important;
        backdrop-filter: blur(16px);
    }
    html body .stApp .homepage-visual.has-home-image .home-goal-layout {
        grid-template-columns: minmax(0, 0.78fr) minmax(360px, 0.95fr) !important;
        gap: 34px !important;
        min-height: 548px !important;
        padding: 42px 38px 36px !important;
    }
    html body .stApp .homepage-visual.has-home-image .home-goal-card {
        background: rgba(255, 255, 255, 0.84) !important;
        border-color: rgba(148, 163, 184, 0.24) !important;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08) !important;
        backdrop-filter: blur(14px);
    }
    html body .stApp .homepage-visual.has-home-image .goal-compass {
        background: rgba(255, 255, 255, 0.74) !important;
        box-shadow: 0 18px 38px rgba(15, 23, 42, 0.08) !important;
        backdrop-filter: blur(12px);
    }
    html body .stApp .life-compact-panel.client-life-panel {
        position: relative !important;
        overflow: hidden !important;
        min-height: 280px !important;
        padding: 0 !important;
        background: #ffffff !important;
    }
    html body .stApp .life-compact-panel.client-life-panel::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: 1;
        background:
            linear-gradient(90deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 255, 255, 0.88) 42%, rgba(255, 255, 255, 0.36) 100%),
            linear-gradient(180deg, rgba(236, 253, 245, 0.10), rgba(219, 234, 254, 0.18));
    }
    html body .stApp .life-client-image {
        position: absolute;
        inset: 0;
        z-index: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center center;
        opacity: 0.86;
    }
    html body .stApp .life-compact-content {
        position: relative;
        z-index: 2;
        max-width: 760px;
        padding: 24px;
    }
    html body .stApp .life-compact-panel.client-life-panel .life-goal-board {
        max-width: 720px;
    }
    @media (max-width: 900px) {
        html body .stApp .homepage-visual.has-home-image {
            min-height: auto !important;
        }
        html body .stApp .homepage-visual.has-home-image .homepage-bg-img {
            object-position: 58% center !important;
        }
        html body .stApp .homepage-visual.has-home-image::before {
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.86) 56%, rgba(255, 255, 255, 0.48) 100%) !important;
        }
        html body .stApp .homepage-visual.has-home-image .home-goal-layout {
            grid-template-columns: 1fr !important;
            min-height: auto !important;
        }
    }
    @media (max-width: 680px) {
        html body .stApp .homepage-visual.has-home-image .home-goal-layout {
            padding: 24px 16px 18px !important;
        }
        html body .stApp .life-compact-content {
            padding: 18px;
        }
        html body .stApp .life-compact-panel.client-life-panel::before {
            background: rgba(255, 255, 255, 0.88);
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
US10Y_FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
US10Y_YAHOO_SYMBOL = "^TNX"
RISK_FREE_RATE = DEFAULT_RISK_FREE_RATE
EQUITY_RISK_PREMIUM = DEFAULT_EQUITY_RISK_PREMIUM


GUIDE_PDF_PATH = Path(__file__).with_name("LY-Scope-Ver.2_User_Guide.pdf")
GUIDE_SCREENSHOT_DIR = Path(__file__).with_name("guide_assets") / "screenshots"
HOMEPAGE_BG_PATH = Path(__file__).parent / "assets" / "homepage_life_design.jpg"
USE_HOMEPAGE_REFERENCE_IMAGE = True
HOMEPAGE_BG_EMBEDDED_MIME = "image/jpeg"
HOMEPAGE_BG_EMBEDDED_BASE64 = (
    '/9j/4AAQSkZJRgABAQAASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAAB'
    'AAEAAKACAAQAAAABAAAFoKADAAQAAAABAAADKgAAAAD/7QA4UGhvdG9zaG9wIDMuMAA4QklNBAQAAAAAAAA4QklN'
    'BCUAAAAAABDUHYzZjwCyBOmACZjs+EJ+/8AAEQgDKgWgAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAAB'
    'AgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNi'
    'coIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SV'
    'lpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8B'
    'AAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXET'
    'IjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpz'
    'dHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm'
    '5+jp6vLz9PX29/j5+v/bAEMAAgICAgICAwICAwQDAwMEBQQEBAQFBgUFBQUFBggGBgYGBgYICAgICAgICAkJCQkJ'
    'CQsLCwsLDAwMDAwMDAwMDP/bAEMBAgICAwMDBQMDBQwIBwgMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM'
    'DAwMDAwMDAwMDAwMDAwMDAwMDP/dAAQAWv/aAAwDAQACEQMRAD8A/ff9aXnrRz6UZ44oAp3v3F/3qtr90DPYVTvQ'
    'fLBz3q4v3QPYVC+Jmj+BC80mO9LkjjrSE84qyBQeelOzim0UAGciuQuM4kx7119chcH/AFnHrXHjPhR14Tdkuln/'
    'AEZM1T1Yn7Wf91auaX/x7JVHV/8Aj7P+6tefW/gr5HfS/jv5nEXvOoRfjXbWIxEK4u8/4/4vxrtbHHkg15mDX7yR'
    '6eKf7uJppgdanFQLU4Nesjx57i5xTQaOO1GKokUc896cCcU3A609ehpx3E9gBozQaPpWqMx3SkH1o+tH1oAeDS5p'
    'B04NKDzRcTQuTS0mRQW9KdxWDnFGf0pu400k0rj5STNIT6UzJpc45pXHYQ5ppJpzc0wUmUL196XHFApcjrQAwk0H'
    'PelJANNNNDEJOKTt1paM9hTQrDSfSgHseKPwxQPzouOwc0YIo78GjHNFyhPfOKUUYz1p2BjAp3ATPYUnPpRQSapA'
    'NPPWozwcVL0FQnHWqQACaRiR3ozikbFNMTGHJpuW6UtJ+lWiWJmomJ604nFRHmtEZMaTk4qE5J5NPIzTe3NUjNkb'
    'ZFNyelONJ7VojNjCeMUwmpO+Kaw7da1RLEBOOtMJ5607tUbdeKpbkEbZPSmnPfinnrUfNaxM5EZJGRUR6e9SsMda'
    'jNaIwkQEmkY05qjOK2RlMjz3pnXvTmz2ph9q0Rixh+tN5NPIptaIzkIOlLmikNMzbuNJzTBTqSqJYlMPT0p2KaaZ'
    'BGfWomzipTxxUbdKaE0RE1F61JzTTVkSRCc5puSamI96jIHancncBRyaTBApc4oEN3U0sadgUw9elBVhDkU3JPWn'
    'Ed6jz7U0hWHE9qYfelNH16UCsMIpp+tS546VCQaQhvU9aYSegp3WkIxQBEc45NB9KcRnk0hHekBEc0w5qVhTDwOa'
    'AISDio8c1YIphWmS0RfSmc9amxmmYxQSRtkjnrTecYqUioiaa1Aacioz7VI1MpMgixSY5qQimn1oQmiIjmkbpmpC'
    'KiPvQAw1ER3FSGkIzQiGQketN5zjNTEevNNrTchobz9ajYVL2xTGGeaEySI0cgUuMH1o/SqJeupE3PeozzxU5H41'
    'EfemQyAggcVEam45PamEVa2MmVWHvUZzVhlqIimSRjIpCOc0/bTTVpkiUw9Kf1NGBTIaIsUU84zmkB7UrkEZB61G'
    '1Tnn2phFMRX6U0g1MSOlRkdqAsQkYNJzUuMcU3Aqk0S5DMU3bipPrSHB61RDRXI/WlxxTyOeKTFACfhUTdasDikK'
    '+lNMkqkHqabz1qcrzzTNtMWpD9DQam28UYFK4mRAHFJzzU+B3pCvHNFwsQUhFSlRQF9qq5NiAx+lLtIFWtoxRgGl'
    'zBaxVK8UzZVwgdqZtB5o5hNFcoaNpzU+Kdto5gs0VClM2HoOtXttJ5fqKV7jSKYXnkU/ZVkoKbt9qAsVSlNKGru0'
    'Gm+WBVXFYoeWc03HarxTFVyoyaOYHEqkdzTCueRVsqCaYU9KOYjlKvvULKc1bKYFRFapMTiVSMU3Bqwy0zbkU+Yn'
    'lKxXmoip61cK0zbjIo5hOJUK1GVq6U71GVzTuTyFNk7k1Fj8KuGPJ6VH5dHMjNw1P//Q/fgj8KQYHWg5HFKMjpQM'
    'p3n+rX61aQZA+lVL44jX61bXhQenFSviZpL4EONID2oPNGaozHHpSds9KBzRjjHWgArjrnGJR9a7E+nSuMuScS59'
    '64sbsjrwm7LGkkfZUx6VT1YH7W3+4tXNJ/49I/pVTV/+Ps/7q/yrhrfwV8jvpfx38zhb0/8AExi9ea7aw/1QzXD3'
    'xzqUIHvXcWGREK8zB/HI9PF/w4moMdqnHTioBzUo6V6yPImO68daPYUZz9aXmqSIEx3Bp68jPpTDT14FVET2DrTu'
    '1HHpRVXIFxSZ55paQg00AZApc+lJzmlpBYCc0dKMd6TNMA60vek6daBSHYM80mecUvXmkOaA1A80fpQKMUh2EHWl'
    'zxSE4FITnigEgPr3pM5pKWgoTJ70hGadkCkzmmITinDA5pgweaXOenFLQAPXIpCDQKWgYDilJzRj1NHTrVgJSc07'
    '8KZz61aAQnimE+tKfypntVIBhNNpxFM96EIU00kdKXOelNPNURJjD0qOpGPFMrSJmxhxjFQ9alb/AOtUJrSJlIQ4'
    '7UmKOtI1aIzYhznpimt+dL24ppPNWkJjc5FR8ZqQ45qPvmrRJGxOaax/Cnng1GeetaozYhxioD1qRue9MxWiMJkD'
    'UzrT25pMADmtUYyICMGmmnnrSEGtEZSI8CmVNgVH1rVMzYw0e1OPFNFMzaGMKbUvU00rjmmiRmDTNtSewpCKoghI'
    'xxUR4NTNxUWM0xMiI54pp96kYU0infqT6keOKjPNTEGmFfSncmxHj0plSEdzTSKYWG5pDTuKb0NADM9s0w47U9s5'
    '4pMcU7iZHzinAA0pBwcmlAobCxGRTCMDmpiDjNMPtQDITSVIRUZzmgXKRkc0mKlI9qQg0gsQkVHtxVhhzTDjpSCx'
    'CeKY3T61KVpMUyWQgZHNMPtU7cVEQc0MViMgGoitTfSm+9CJasQY7VGRirBXmoyMdadybEeO9MYVLg+lIRRcViHB'
    'A9qiI5qcjmmEd6CWiA5puKlNJtpiaIjTelSlaaRTRBERTSMZqYioj1pksjx60zFSkfjSY4ppkMiIPcVGRmpmB70w'
    'gdashorMtNKkc1YxTCKaZDRXPNMIqYj0phFVcgrkUwjtU5HrxTCKdyGiEjFMIqYr60w01Ilq5CRTakNMxmi5DiNN'
    'GaCDTD70Ihi4pCvpSg0uRTvqLoRFT3ppWrHWjGKakK1ysUI6UwrVor2zTCOxquYLFUrim7asFQDTaOYixEB25owa'
    'lw2aUCjmHYh2+1JsPWrHSlwTijmFYqlKYUNXCKQpRzBylXbSYxz1q3tpNnPNHMHKU8UuDVkqKTYDRzByIg+gpcZq'
    'cp7Um3I4ouPlINueKNnGan2+1MIxRclxI9gFOCelNd0Rd0jBVHcnAqtf3y2NuZ1Acg468fn+lZ1K0acZSk9ioU3J'
    'qK6lzZtGT2/So1ntCHbzo8J975hx9a8X1P4mXlhHILhFdZgwCHqAcgkEdh715dceLJtduksNP3RDygjsBtUIg3Fn'
    'YHJP168Cvmq3EySUqNO/e+lvzPWhlFrqpP0t1PpCDxl4enuPsj3HlTZI2sp7Hrkdc9RWFq3j6002V02LKEQnKNkE'
    '8kHccflXzfe61baaDcWry/aChCyS8Mw/vD0/CvPLjxbrF8gbeBEG5LYAJHYZ6j1xXnQzrMMRyuLUUt3tf8zolgsN'
    'STTV2/wPqA/F/T28uJZts2dzF4mCE/8APMkf+hV2WlePdPv0QySIWkOW25CxAn+Ikc/hXyEusiOxc3+EmkH7vYAQ'
    '69+fUVj/APCRXgUQWTvHGvzYTPX1J64rphjcXKScJNW87pnLKnShH3knfy1R9r6r8Q/D2l3iW0kvmo6kiWP5l3Do'
    'v410+j6pYa5ai7sJA4wC6/xISM4YdjXwlYOWYi5lELPhvnJIP4dj6V6bpnxEbw9p01lpOIZpFy06j779A759uOK9'
    'Sjmk1J+028jglRX2VY+s3hIqPyzXzx4R+JCR3YvNRuXEV0SJ4ypcIVGFYMTnBPJwK9is/Gvh69sm1BbkR24l8lZJ'
    'PlDuTj5R1/SvTw+MjUjfYxnCztY6B4+1QlO1W0kjmQSRMroejKcg/QikKmurnI9mUSnrTDHxiru2kEZ7U+cXsyjs'
    'zTDGc8VomI4zTDEc0e0FyMzzH60zZir5U05YC/ah1BeybMzysmni3J7VrrboBk8mgoeijAqHWvsaLD23P//R/fft'
    'Sg+lHSkHtQNFK/H7tT/tVcXlR9KpX33Fz/eq6v3Rx2FQviZb+FDulJjvS5pOv1qyBeelHTqKQZ70c9KAYtcTdHiX'
    '8a7XoK4W7f8A12PVq4sa7RR2YNXbLmkH/RU+lVtXP+ln/dWp9GObOPnnFVtW/wCPs5/ur/KuGp/BR30v47+Zw17j'
    '+0oj7Gu6sD+5Arg73/kJRH2Nd1p5/civNwn8SR6WK/hxNUcU/rTB0qTPGK9ZHkSQ4HBpaj5pQT3qyCTI605QKYOf'
    'anLn60LcTH+xoptLzVCsLS9BRRTEJS+9J3oBosAtAA9aB/kUYpNjsIc0c96U49aaeKTY7BSUc9qWkMB60ZFIT+VJ'
    '9DQAGm5p/akAFACUmaMUme9AC9PekOPpRQfbmgA+hzSZpADTz14NABjIo6cUYpKpALx160ZpCMU36VSAU0h6UhoJ'
    'qgGHn2pKDgmmVQCE46VHyOacetIaaENzkc0lHSkJqzKTEb3pnf0px6VFnHWtEQ2NY1D7ipG9aYelaIyYnNManimk'
    'c8VpHcmw3txUX1qc8VERVom4wnjgUgpWxSVaJGEd6YTkcU40witImMhhqIj1qXJ6VGc1ojGZC1MOMU8jv3phzWqM'
    'pbEbetMPFSHpUfJq0zFic9aaQKcetJVpkSRG2KbnB4p5HrUZzVoli5pD1oFL060yBmDTTUhHpTDmqIkRN061EenW'
    'pj61E3J9qZLGHBppGKfSEGmiBh9KaRTz6Uz9KA9BhAphHpUhFMIp31ERk5phqXHamlaoCEj8aMZ5p5HakA4oGNFO'
    'IB6UYopXFYaaaRxUmPSm44ouBDgimmpSM03FAiPHOaQ5p3FHFJMZGcdTUZ61KRntTSvFFwITTTUhU03Ap3JsRN0z'
    'UXbBqYg0xqYrERHFN4p+KCM9KVxMhOajYVORSEA0yLFf2pOtS7RTGUZ4oDlIsUzb6VMBSMMCglorlRmkPtUpFMIp'
    '3JaITnqaQj1qUimYpohoiP51GR1qwV4phFO5DRBj1pMCpCKbimmRYjx60wjnNTEU3FO5LRAevoaYRmpyKiYHHNPm'
    'JkiBhmoiMdKnINREGquZuJETntTeKe3WmEU7k+o0imEYqYD1pjLSJcSt7U3rUzCozxz/ADp8xDTGEZqJqRrmADPm'
    'pj6iopopbgrGnyxn77HqR/dA9+59KzlV0fLqwVN3V9CCV2OAqMynq2cL7ZPp9KuRIAuNwY+3QVYSJAoXGcDHPpUi'
    'W244iXJPoP8ACiN78zJdvhRBtoK1MYJEO1yE5/iIFLm2QHdLuPoik/qcCrcyeVkJGBgUwr61Y+0Wi/didz/tOFH/'
    'AI6DTTegfcgiH1y38z/Sj2j7CfL1ZV2ZpCgzxVhr+5/hEa/SNf6g1C2oXx6SYHsqj+lPnb6Ec1Ndfw/4I3YT2pRH'
    'x6Uovb08ea36f4U8Xt3jHmZ+oX/ClzsTqU/P7v8AgjNlKEp32644zsb6ov8AhUgv+MPBE30BU/of6Ue08gVSn3/A'
    'j2U3yzU4vbQ/egdP9xw36MB/OnLNZScLMU9pEI/UZFL2halF7MqGMmk2EcVprbNJ/qWSX/cYE/l1qKSGRDiRSD6E'
    'Yq1UL9m9ynsHSl8rmrG0+lOCUcw+Qq+UM+1NMQq9syMYpDGccilzh7IoeXnmo5AI0L4LYBOByTWZrXiPTdEyl0w8'
    'zbuA6A+2ema5SX4haM8AZmaMSDA3cckHuOn1rzq+bYaDlBVFzI6KeBqu0nHRnBeMfE2prPJCSEtgwdFcbW4HTHcV'
    'xia3qlzarcPqLWsD7lSMcs4zycHjnoCam1nxFpM8zv5i+buKqcb41UjG5nbqT6dPWvMNS1Br920/TYhI8CNJLKhO'
    'SgP8I6Z/r0r87jPEVG5VJu73fkfTy9lFKMI6LoZHibUG84R2xkIjUK7sSxYqT8xx054xWrb6kPDmi28r+XFJcoTK'
    'rAtLIW5HPQKOwPeo9M8O6pc2bX0krWiykAqVJd1HIJX644Nc5rOgatqusrHdTMunxMP3rHDOBjOFz949K6/3N1R5'
    'lZb+f9M5b1Gue2r2Mu4vNQ8RalHbWgMrzEqoJwB3JJ7e56Vdg8M6VpcYm1e433mSoiRgUjBz377uuRUV1e6fpTSW'
    '+nwxRTxyMBLGWLlPTd09cms3Urd7wzSq7vHEqt+9wsgVuASAfX0r2adKdSKUfcj+P/DHmVasIv8AmZuXOqaREyCK'
    'NcxJsjBOcA9Rj+tQwana27Mwi8lplw6pwSPof5Vx8tusSW0sxKxkYeQc5YH5se4HaqiOv2x1NyRENzBiMsQOgA/v'
    'V1QwUFG1zlnXcnc7lr7T49yQ4f5cgvyS393PrWDNq8btlV8njaep59v8KycoreXCSwABJYYOTz/+utS3k024QLeR'
    'sz7/AL6EAqoHOF7tnnNbQoxjqZSqNjYbq6iUyjzML90nIP0/+vXQ6fqN5cptB8uFxlznqw657Aj2HNcvDcXsbDzF'
    'OFO1CxwSvb8+9b2l6tFZNKLi2Dlj90rnn0x71o5JXsYuF+p9f/BxJV0eaGc3AdNp2yj90E52mNu+e9esvNCsqwM6'
    'h3ztUnk7euB7V8U+HPirqWgbvsgj2svlJG+WVUBztAzWLqHxO1B9W/tNiY5Fm8xomdtpyQdoI5HTt24rso4xKKi0'
    'NrZI+9ggNPEeK4L4d+OY/GOjpeSxeXMCwfbyhC/xZ/hBzgA816WgR1DAZzzkd813KpdXQ1BMpFOKgdD2rX8oHtUL'
    'xAdKPaFeyZRjgB+ZutaMNqrdKbHGc8itWIYXAFZVKjOijRXUoyWiIOBkmmLZjFa7BQMkZxUBLnkDFYqqzeVGN9j/'
    '0v34xijBpuCT60uCelAyjfcRqP8Aaq6v3Rn0FUdQIEa8/wAVXlxgfSpXxMt/Ah2QfagUjDmgYqiRR09aABmlGcUm'
    'R6UABrz68bib/gVeg15zenif/gX864Mf8KOzBfEzR0I5soz7VDq7D7Wf91f5UugH/QI/pUOrn/Sz/ur/ACrin/AR'
    '301+/ZxN5/yEovoa7nTzmIfSuAvWP9pwj2Nd5p5/dCvOwvxyPQxP8OJsp0p9RIcCpQK9ZM8qe4ppaQYBpe1WQO9x'
    'TwcVHT8UEsXJpc96ZjmjoaBJkufSlJqMH1p3vTuOwuaU4pM9qSgA4FL0qPmlz70XCw7NB5oHTig5PFAWEpuR0peQ'
    'aMYpDEpQaDgHNJkmgBcj6UfrTRSE+lACkikpMnFHtQMO9Lk9DTfqKXFA2gHtSjgUe2KUe1MQDPagmjH40fWmmITj'
    'vSUpOaQ+tWrAJ7mo2qWozzVJgMxTTTz71Gx5pgxuDSGlJphPeqRnca1NoY96T3q0ZtiE0xjinGo3PHPNaJESYwnn'
    'NM60tNFaIzHD35owKXNN5q0S2I2MelQkVNzioz71aViSMgHmmEdqlP51GxqkS2RZ5pp607rTeprWJlIY3PNMPTpU'
    'h9ajrRGEkRMMio29alIxTG6cVomZvsQ03inH2ppPaqMbDcA039Kd9KQ81aZLIzTT6080nWrRmxnak607ijGOatMQ'
    '0/lTDUhHrUZ6VZDIz7VGR3qXmkINCJtchNNwakwO9H0oJsMK1GRk1OQaZj0oCxFimnNSkZ5ph+lMViLHPpTSvY1L'
    'SYoCxCVNNANWMU3FFyiLb603HNTcGgrSCxDTCMdamYEDNIRkU7k2Ien40z61MVqMjNAcow89qjYGpse9Nx70BYh7'
    'ZoOakI9ab7Uh2ImHFRGrBqIg5oJaIcU0ipsU00XEQlaZipxxRjNAWINuaaVqfaM0w8inchxK5FMK1Ow4puM07isQ'
    'Y4prDNWNtIRSuJopkYNNIqwy1GRTuQRY/CmlRUx4pu3ng00yGQEYpuKnZRTMY6U7ktEBFR7c+1WSDTAtCZFiDHNN'
    'YYqcqKiYVVxWIiKjIqcioiMmnchxKzAjOKjbFWGFQlfemmZtEOKTbUoFLiqJcSHA70hFSlaYRikZtFZuvFM27uoq'
    '4sTyNtjBYnsBmrX2WGEbrl8t/wA84+T+LdB+tKUl1JUG9TIFpG5AEak/7oP9Kk+zmGdYbgGMEbskZIHpgc/StGS7'
    'fGyBREv+z94/Vuv5YqmRkkmsrdtC1yrfX8hrGBM+Upc9i/H6D/GpILuSMFGJCnsp2/y/xqIr603GBTdnozNTcZcy'
    'GXIic5jXHuepqkYzzVw9aYVqlKxlN8zuU9nrRtqwVpNpp8xzuJBtHejYM1PtzS+X2pcxPLcrlfSm4q15fGaaUOOt'
    'LmJ5WVSD0pCPSrRiNN8v2qXMfKVCppu0/jV3yzSeUal1AUSsFINaEN7eRDaJCy/3X+ZfybP6VEIyOetP8ulzp7mk'
    'bx1TsXY7u3fi4iKH+9F0/wC+W/xq5HDFP/x6yq5/uH5W/I9fwrIVO1OMWeaSqM2VV/aVzTaFkbawwR1B4qJhiqE2'
    'qXGn2zz3D+ZDEhdlfLYVRk4PUfhXOWfjvR9RgaeN/JDKTHHIDkkDkFh/D/tY9q562Y0aclSm/eaO6jh5VYupFaI8'
    'V+IkGzVJ0xJtZ12h3DMScEnPQKK8xl1O10q8S6ndDFapgW4GWL87c5/Pmvdda019St7zUb0FPMI8gZyHOQckjI2/'
    'j1rwHxBpek6aRLeSLcy3D4G9iIxn+Igcn8fpX5rXUlW5KkX713brZv8AA+rjaUOaL26nnfiLxAdVj8sRrEu4vmPA'
    '3fj6DgfWup0/ULXw5oMSMyi8uP3jSBQWGcFUJ9AO3qatzxabFYRGJIXKfL935I1YZyO5JPr/AEryW8m1G+1PynkL'
    'xqx5XLKqg8n8P16V6OFhHExVHl5Yp6+ZxV26L9onds7rUvGzwNG0asWZFLsXwNzAkAY7ds159e65e3+Lcs0bOc5B'
    'zk54yexWku1hnk+yWrmXcxVSVwWGeOOcH+Vb9l4Wl8gahMRJg7djkr8xAALH0xzn0r26VDD4eKlJI86dSrWbjE5a'
    'WWGBCkUYZgfnkbli2eq9gKpXt5f3MbTHoy4XjCsV/hHqQSOK9KfwVd6rdIkUkbT3l0YFaLOwTZGUIxwGU7lI44Na'
    'cvw11LSk0pJtQiSLUtRjtxjkRFMlpgW4+Ugq3TOOa9SlSvG8dTjnDVpnk/8AZ0l1dXUapKsFoPMk3dU2bVkOOmS5'
    '2ioY9DNxqQgMgt4pHKF2+YRA5xnHbNemeHltTHNpotG1KZA1rEAz53TTGZpSB9/CqFHbJzWrf6XqV8b7UP7O34nk'
    'idQfKCXO0lEXaOsaruI6HBOa1vY53HseY2vhfUzpl1fgxzmMBWIf5hwWO0fxHauT6CuX8wqA0RJLAEHtjt/9avYU'
    'm0q0sZtMNw8X2i5AFw6naUjg2kxAH5jIzHOew5rE1bw1G5vr7SbGddNt7VXjdgVMWQFR5xzgsMuVB7iqSUloS4Nb'
    'nFw6lKIhG4xng554+hp32xo3G6QhdwOQe44/lVC3s5bjcbXzJkjQySMVIIVfvNj0X1rZcWElrFDHBtkVRvk3Fi7c'
    '5ODgKMY4HT1p+yRG2pW8yMu3lAgMeCTkg+ppI/KeRvtaiRXHL8krjoQOPxretNHfV43RJkikiVFQSERqwzgjccAE'
    'DnHU1WS2hEaWty0gdXYkhexGABnk80mtBpJansHhL4iwaX4Y/sGQ+UkLGSAIgXe54KzEEFhgnBPTvX1X4F8b+F9Y'
    'sbTTLG6d54rZDIXGFVyceWXPBfPQDtXwdpHhye9uLe3un+yR3EnlLM6tjd9B+Ar2T4R+DvEulfEGK11bS5J7VAJR'
    'KU3pH/CsqtnA5781VOpJaXKp35lofam1mOO1Sras3QVs2+nsxGetbEWnqOcVpOuketTwblucqlm/cYq9HanHSulN'
    'qijpVKYxRd65/buWx2fVYwV2ZX2QtTvsqj7xApZb0AHbxWbJesemapKbMZTpo//T/fgH0oz+dABP3aMEHmgZnaj9'
    'xP8Aeq+o+UH2qhqP3E/3qvj7ox6CpXxMuXwodz9KPxo470cnpVEMM0YOM0mfWloAOe9eZXr8Tj3b+Zr009K8rvT/'
    'AK/6t/M1wY/4Ud2A3ZqeHjmwi+lM1g4uz/ur/Km+HSTYRfSm6zxdHP8AdX+VcE3+5XyPQh/HfzODvW/4msI9jXoO'
    'nn90v0rzi9P/ABNYeexr0PTz+5WuDC/HI9DE/BE206VKGqBOlSjFetHY8mW5Jk0oPrTRnvS9feqM2Ppwpg6cU/PS'
    'miXsIDS5GaaeaO1UyCQUufTmoxin55pWHdjqOvWk46ClxmgaYnb19qTFLS9OaCriDIpMnpTsik9x3oFcbjvS849K'
    'TjvTT7Uhi0U3JPAoz6dqAHGm96PxpMUDFOO3Wj60mRSigaE5zQP1pc80HFAw7804A9KaOlLknr1oEL9KT3pc00/5'
    'FUiQ+tJxmkPSkyAKoBc005pCc0wsDWi0AGbmm96D+VNPpmmZtinjmoiaexwKiJ4qkiWxh60nPWlIpvPatEZtgT3N'
    'Qtg08n1FRnk4q4oiTGmlHTFNNO6VaM2xfpTSM0E+lN4Jq0IO1MyO1OPrTCRWhI0ntURJz1pxIPSmEU0Qxp68GmdK'
    'cSM4ptaxM5B1qI5zUlMatImMiInNMPFSHpTcVRmyJh36VCR61YKmosflVozaI+9KeOlOxScDpVEEZFNIqQ0zjoa0'
    'TIG+xpMZp/tSY5+lUSyI+9IeRUjc80w1SZL1IiKDT8Yph68UyNhhHpTRkVIRmm47VQNXGnrTSKeRSUroViM9KbT6'
    'byKAsNxmmkYNS5phHemIZTSKfQAaBpDAOM0VJjHamsOaTYWZG1NI9KkIzTSKLjSIiKaVqbHtTdtFw5Svjmk6cVMQ'
    'fWmEYOaSYiEio8YNTlaZt7kYobBkI5HpSVKQKTFHMIhIFMK81KRikxSTE0Qmm44qfaMe9MIqromxFg9OlNI9Klpp'
    '+lFxWIPY00r3qbFJjHFCYrEIA6UhGKmKimEUyWmQEVERVhqjoJaICvFNA61YIPamEelO5LRCRTDjNSsBmmnmmmZ2'
    'sQnrikxUmKbzRcGuxGRURBqfGe1MNUZkDVERVhhimEdqVyWiqRimbatFPSkELk4AOafMS4tlUJRs710On6O1z80x'
    '2jsO9aF14f2jMHpk5PH1J7VhLFQUuW5vHA1nDnS0OMxVgWihBLctsU9F6u30Hb6n9auMRZuREMyDjzCPu/7oPf3N'
    'UcFiSTkk8k960cm9nZHM4KL97VjjM4UxwqIkPUL94/Vup/lVTaKskHpTduRzSTS0RnK8tyoV56U0r6VcKdhTWQjt'
    'T5jJxKRFMI96tMlRFQKnmJaKzKKZirRX1phT0o5jOSK2O9PAHWphGad5dLnMuVlcLnpT8cVP5dPCZFJzGqZU2gjF'
    'Ls7Grgjz2p/k+gqHMr2ZQMftR5RNaAipRDUOoUqJm+VSeWD1rU8nNHlY6VHtS1RM0R89Kk8v2rQENP8AKyaXtS1S'
    'Mvy8Vn6jqdjpAiN/J5azEqrEfLkDOCa6Tyc/N6V4F8RtSvnSXThlwkqMnmx7dm7v/tc9PavKzfNPqtJOPxPRHbgc'
    'Aq1Sz2RY1zxhaWty8IuUuY5ow7RZGEDdQSO3YfXmvnTWvGH9lX32qGNVZJVZAp+RFHK7eeg7+9Ouoxby3V/dkxMF'
    'McCrwXkbqenReTn8K8q1Z4vJw4abOcljgAjp78nrXylKEqtb2s5N7f0j3aklCHs0rHqVx8VbtFYX7bFuvmzCfLPX'
    'JOwZQg+65NcxqYi8UyLNpjfafIQTu0S7ZYgSQd8R4YA4yUrjNJ8Na14rCXMSIYwSgZnVQoQgHIPQD1r0zTfD+h+F'
    '7ZNRuJBcXLfcAJCRhc5JHfnp610161Kk1K96nbdmVGNSacWrRPP77T7m10x2luD5xfhApC+WB3JwSTwcVzOmaFrF'
    '3LcXSBntyBudM7Hw2CDjowzyDg+ma6DxX4jGv3WyCUI2dmzPyPnjOex967vQ9Nt/DdpDewXk0V+yAGNiuGJPKkdH'
    'iPYmvQwmJ9lT5sUtZdDlxFD2krUOnUXQ/htHZXUuoapFIJbcxyW4BXymDKWEgbPzcY244PIIr0AeGh4huDLBdQ27'
    'QRSSHcuE2om4hEHXHXH9zJrgNR8QyX8FubvUUsjE52xJk42gkY/hTcflQN8vrXIXHxG1SDURJp7tbLblWVWIYiUZ'
    'DMeMHOSMdADjoBVyoVKlb29T4VsiqcoQpunHfqz3ewl0m10S71O0hS3vLOwsb63VmBJuLKbZcEknk/M3/ASK8W13'
    'VbM3kkRDGEu0iI5Py+cS5IGeOT1FcvqHiW/1Gw+xTuGjD+Ypx8wPcBuwPcVgxRXOoT29tJOIo/mCSyZ2JtBOM9ev'
    'HtmuxxnVaszjlp0O6tfFhsLm5mtEFtLKFVXhGCqBdm38jmiPxNqVwTZ28rObps7Dja00y+QGyTwxUkZJ45NcDpmo'
    'QQPN9vhe4mddkSA4Alb5cv36HgDvXp2n6DZXFqURvLSNBbPLJgK9xJ80rOcHbGoUov5963p0IQ9+UtTNuT91LQwt'
    'csEjinvr+GYxl2ggVSgjj2LtjjZwT9xVLPtHII5rOTWZhDeQW87FdQKGcFiQyxjainceSw5z2Xip9X8VS3FhFpzp'
    'EUt4vs6ShAHaJWyqlgOPTIGWHWkurrTtW0+0sbC1+xwabbSO8wUNLcXUnJMuCMBm+VQPurzXdFr7JyzjfQ6HwxB4'
    'aF1A+pWatbRwyRMkN0Fa/vMblEuSPLhXPYdsZJrntd8MXem28erxm2W2uSBEtvIHGepGCS/1YjmuUnW6iK+agZCu'
    '3Ax/D15HcZq5Bq99YwJFbOrKz+Y26MFkPQKWP3h39M1bmyXDuStLLZ3StBKHSJlZG27cnHXYffI5rrPEN/o2qWdr'
    'qyMItS3FbmBc7QgxsZTxjHTGSe9cC0zSMXcks3JJPUn1q1HIHiIkdTsACg/eOfT196nmZHL5H03ZafH8Q/Cuj2+i'
    'MRq9kyxvNMAFb0iCqDgDAO9+Ca+vtD0bQPCOk2mu+JpoV1YWwhuLkMRvJGWVIwcH8BX5u+DfElpoGqxagfM2RRsT'
    'HuOyWZQfKDgEYTd19K6TxB8SdR8QWCWl5tje3dpFZF6sw55zxx26d6Un2NqVWMHzNXZ+nlhqmiampbTbqK4KokhV'
    'GBIV/ukjqM1JPepECAMV+Yvw88dah/adtorXBtLae7ia6khYpNJHkLsLjkqOoA71+gC+INJm1T+wY7pZL1Iy5hBL'
    'OqJjJb0PI4JzURgnqz1KWPco7WN+bUJZDhelZcpdzuY5q8sRxmmmHnpW8bLYmpzT1bMkofrUJj61rmI1E0RHbNXz'
    'mLpH/9T9+BxxmkOTTunAoz+FAGZqPEaZ/vVopwo+grN1Q4jT/erSUZQfQVK+Jmj+FCk5NJzS4z1o6VRKExRtNHQ0'
    'vFANiHoa8lvWz5/1avWTwDXkF+3Fx9X/AK15+YfCjvwG7Njw2c6fF9Kj1pv9MP8Aur/Kl8MNnTIPpUOtnF4f9xf5'
    'V58/4CO+nrXfzOAvX/4msI9jXo+nH9yua8tvnP8AbEA6da9R07/ULXDhPjkehil7kTcQ5qYccVXQ1OD3r14nky3H'
    'DincfjTKM5qzNoeKkB4x1qHP5VInIprcmS0HnFLjt60lKKdjMOe1OApM0oGO9FgFx3o/GjPaik0AvFKfeo89qdmg'
    'BT70jUhNOVGkYKvU0JN6Id0iL6UuDV3y4ov9tv0pfNYdAB7AVoqXdke17IoYx0pRmrnnHuqn8KBIveNafsl3H7Ty'
    'KmO9H4VazEesf5HFLi3Ocqw+hqfYvuP2q7FP260hFW/Ltj3cfrSGGHtIfxFHspFKrEq4pasm3TtIv60gtm/hZT+N'
    'L2Uh+1j3KoxThjvU5tpvQfgRTGgnH8Bo5Jdg9pHuREkmm57CnlHHVSPwpmPanZod13EIpD6U6o2wKUb3AazYGKjz'
    'SGkNakyYpJ603ODmg8VGx5xTRApbNN3Gk60049atGbDNB4pMnvQeK0IbIm9KaTTjTOMYrRIzbG96XPHNN4zxTSfa'
    'mJjs9hRkCm9KaTVogVjnimlqTPbFNPPStBMSoz1p5OBUZ61SZLYhxSUH1puea0iZMcelMPPIp2c9KYT2q0ZNDG54'
    'pPYUpAFNJqzNiNTDinkmmVaIZHyaQinHjpxTaZDQhFRECpO+O1NPNUmS0Mo60p9qTiqTIEIzUZGKkPSm/wAjVJis'
    'Rnpik61JTSPSruKwwr6GkK0/tS4BouTYiI9KbgYqVgKZ7daQWI8cUwqfwqcDHWmn2ouBAV7imkVLjnFIVx1p3FYh'
    'waXGMZp5BBo47UXGJ9aCKdntS/hU3GiEjFMwSc1Pj8KbggYp3C1iLHFM2+lTYxTcCi4iE0wjI5qwVGKjK+tLmAgI'
    'o25p5XmgincCEpzxTCp+tWNtMwOlK4miuRk80wrVjbntTCtArEOKQjNS7aTbRcPUrkc005PHSrBGKjK07ktEBXpS'
    'EGpMYpCO1O5PKiIggcUypsVGRmi4nEiPWm4z2qXb3puKLktERBpmDVg0zB70+YmxWYY9KixnpVllqPHNPmJauRFa'
    'Zj0qbHc8UwjvT9CHEZ2JxURHFTU+OFpX2qOaXNYXLfSxRINWrazkuD02r6n+lXjYNGQW+b1FaSH5MfdrGrX0906K'
    'WG198zIbKNZSc529K2Le0TkgYJ7moVdIx0qUTkL5j8L/AAgdT/8AW965ZynI66cYQWpeSAxjexwo9P6VXurqVhsI'
    '2xqchfX3Pqaj/tDI+b/9VUp7reOcVChK+qNJ1I291lG7ljkzlRn1rDKc1fkJYnioNv4V1w91WPJr++9SrspCvrVn'
    'Z3ppWr5jkcCuVx0oxU2yjaKXMZuJTZDUJUmtDYM4qPyqXOQ4FEIaXy81dEYp/l1LmL2bKQiIpRGPSrwiHrThEM1D'
    'qDVIpeVSiPArQEPrS+UOwqHULVIoiM08Rc1dEWKeIqh1DWNEpeT7807yuK0BD7VIIfas3UNlhzNEB9OKcIc9K0vJ'
    'FL5QrN1C1hzP8kUGEVp+UKXyKXtUX9X7IyggHBriPE3h+x1IMqRF7iRhL8vXK4GST0UDitXxhraaFb72ZoiMNvAB'
    'AHPBB7HHWvB4viffSXZlS4WP7LHIGnZeJlY5VSvrjgV4GY5phXzUZwcrfh/wT0MNgasWpqVrmT438DuupQuRHKmV'
    'RbeN8S7CT8u3qPdq8Q1+20t9RttMuYjbhbjy5ovL2eXG2ADuzl89z+Nes3evatfi48R5Xz5m8lJDyIkH3398D5RX'
    'hOu6rdvqMkdy6zog4cc5Vh2I5B/lXzmEr+2ruFBWjFd9T0q1BQp81TVs6/WtVsfDdmLWygQbcpgDAG3rx3J7+teG'
    '6vrWp65dtJJujwNihc42jua6q8ln1KArZxsYYznDne6/8CPr1xXRaB4WKxrJeRb3mRZokUjIGcfOTwFx1HWvTwVG'
    'GGXPV1k+pyVuas+Wn8JneHvhrfQXw1OSWCe1t4jJNK4YQgSR8DLdTzwR0rC1NJobqaK+nC3SIAiq25JFzgBGHAGO'
    'ma9J1TR9a020KfaZEsp5AHt23BFeMbkWSM/w46Edq88vNBuL7V10uztHea8kV4Fi/edeXEeOucEgenFen7eFR+aM'
    'VhZR32OQktJZpArkqZOCT0B7A+xqPTLdV1ELdxjaFkRgwLDlCMnHOR2Prg16pqFtAkdu9lpXlSrHtYEM6PGgKtIA'
    'ed/cjP4Vz/iC5u4dTW91Ewah5MSKggAQSw7flfKDqO5PIIwa6qeKVrSRnPBtP3WM8P8AhuS8mn0ye3/eC2aZDIfL'
    'KovzGRA2NxK8r61QgzAqWce5LmyuGlQsMph1G0+Ww/vY3E8YNdXo3jNnvbk+In33abLnT9Rki8wxsi7RC4x80Lrh'
    'QB91uasQfYvE/iea7hMmmfb7JLeMwnzAl0AABIuMtFKw2+oyPSu+NSCScJbnJKjJuzR5Zpsc2reMTboPJka6IEjE'
    'Rok23bvcn5VTcck9q7gz62kVv4TijW6aMsY7eAg7p33Y3yry+Mlh2xWhBpCNr+oSa9bvbgT/APEwgt8RkFMb4xnI'
    'XLA9aoF7XSryPUtPkdmcyFlU4MabsKquOrlc/NXJVqU5zXN0ZcKcoxOLlsLlSlhPAy3dssv2gHJbcDk5HQBFwPxr'
    'Qs7QxxRkEbT8zbTyD6H09q7bTrW98RDUbuweJJb24CixGfNkRV3ffPSNe+TyetZukLf65IPDlnbxzTsJDGchAAvz'
    'OyDIBkOOpOAvQV1LFK+hjLCXVzZ1ayj1CJNG0NIbxFSOWSa3h2gSInzbWODtAzvJxuNchJozOLextYJ5Lq6ZfLUx'
    '43A8fIoyzZPQ4wRWsj6l4b1J57B1kezZTJszLblv4VfGFdc9jxmq994l8RXIhndjGbeRpRNbgQy7pOGBmHPA4UdB'
    '6VosWnuZvCtGDrfhm+0m5lt7qGSJo8gK4wWxweBnvxXPpYzMM7WDHOOwJHJ5PcV6fY6rf6ppktnIk72wcSfukEjR'
    'yDOxZJD8xB5JA6mn6j4SkSbGnzi+skAdZ1DCMFgC2Rj5SDwQatV0zOeHa1R5UiS7fnJIPK8fpU8d5NCuDxu+U/Sv'
    'Z4dH8LzWixBZri78lgBFlVSUyAKZWIIZducCMZ6Vk6/4G1bwusB8Q6d9lhvkaS2Ep/eOoH38KdwxweQAaftkYyw3'
    'U8402eK11C01K0SQPC48wsflL7sqVxyMdcHuK+zPhLZ+HLXU5PFHiDVnk1CO3e6WFSWHlnrJK2fmlP8Acr5Z17wl'
    '/wAI5ew2qXsV350EVw3kNkRtIoYRv23gHnHSvSPA/hzxBdwJf6XH9oXzGVkVlZlK9SyHBPHQDNCqdiVT5Z7Xsfon'
    'ZPBf2UF9bEtDOiyISCDhhkZB6GpGj61wvwtGqJ4Rg/tWSWWd5JCXmDByowoG1sFQMYAx0Ga9G8vPNacx68FzRTsZ'
    'hj9KYYj6VreRu6CnC0kbhRU+0S6m3sW+h//V/fgn15o69qSgfWgDM1X/AFSf79aSHCqPYVl6vxDGf9utVfuj6Cs1'
    '8TNH8CHGm4paD6mtCBPxpQOOaXINJnJoAaTwa8Z1Bx/pIHq/869mbocV4nfHm4z1y/8AM152Y7RPQy/dm14Xbbpc'
    'H0P86j1tv9MOf7i/ypPDR/4lkOfSoNcf/TDj+4tefUf7hfI9Cmv37+Z55fk/2xAR6GvUtMcmBe1eU3rf8TeHnsa9'
    'P01v3C1wYV+/I9DFL93E6VORUoOKrxHI5qbNexF6HlSRLmnCogfWpARiqTMw71NHUNSoRirRMtiUZp2PWmjFOGKd'
    'zJhz0pACKdQaYhDSe5oPvSVIC0Z/Gm/WjjNAxT71eCiGLH8b8k+gqlGN0ij1Iq3M2ZG9uPyrWlomzOe6RHnHNGc0'
    '36U4DiqJsLimc5p/NFAwH1pO/rSt7Uwn1oFYU0U0kdKXI+lAwznpSHFHT3pmTTQIXOOlJuYdDTcikzTG2SebIONx'
    '+maTz5B/F+fNMJxTMd6ExaExnfHQH6gUw3H96ND+FQse1RZ5qrslk/nQ94VP0JFJutT1jYfRqh+lNJoJuTN9jP8A'
    'z0X8jUXlWvaVh9UqI0yrsieZ9Sx9nibpOv0IIpptsfdkjP8AwKocc0nGadkDbJfssvba30YUxra4/uH8OajppYju'
    'atIltgYJl6o35Goijj+Ej8KmEsgPyu35mnfaJ1/jb8Tn+dUkTzFI8GmEZrQ+1S/xEEe6g/0ppuCeWjjP1X/A1SQr'
    'lGoz71oNcQnhreP6gkVHutD1hI+j/wCNWkS2UScdKDVxhZf3ZV/EGmFbQ9JXX6rn+VUJspZIphq4Ybc/dnH4qaiN'
    'sP4Joz+OP5irRDZWJ6U3t1qybSU/dKN9GFH2G6/uZ+mDVIgrZ4pKsG1uFzuicfgaiKuv3lI+oq0ZSImPFMzT25Hv'
    'TMZrRGbE5xTadjIpD0qkZtkbGm0/FNxxVCY0ikxTsUnQ00QJjHTpTCB1qSm4xVJiaIzwKT3p5GaZj2pkicU057U7'
    '8KTBzT2EMwaXnHvTjTaLgBFREHNS8Ckxmi4yLBHSk28VMRTcGncViIgZzRjIp2OaOtJsLEZHpxTAKmK0hHtTTFYi'
    'xQOtSFBim7aASExxSbeKkwKdjilcog20wjirBFR4NFwIcEUm2psGjGaVxFXZ6dKbj2qww9Kj2mgLEW3NJtqfbn2p'
    'uBSuOxX25pu2rGKaVpqRJBsNNK1YK4pmO9MXKViM1EVNW2FRMKOYmxWx7daaRxU5UjtTGGaLhykHWmle9TbcUbaO'
    'YmxAVppHpVjb6UzaaOYXKQhe9NZfSp8U3bTuS0VmQ9ajKirjLURU0KRLiVitN2VNtIqSOIyHAFHNYhRd7FLYfSr0'
    'CNH90Yq2tvtGD2qKQleKiVTm0N40uXVkjvkAZ5qIuMdag3Z9ackYIMkhwi9fUn0Huaz5EU6nYdgKvmP07D+8f8PW'
    'qbyO7FmOf8PapJXaRsnp2HYD0FRYp7GEnfYZyTTTnpUhxRxRclpkBBPWk2etT7aXGKLmbRVKZ7VGUPcVexkUwrmk'
    '5EOLKOyl24qzt9qXy89qlyI5CiUJ6Unlk9aveUewpfKbHSocxezKXlYNSCP0q6IT6U4RCocxqkU1i9RUqxc1dEYF'
    'SKme1ZuRtGkUhDT/ACe9XhHmpPL7YrN1LG8aJniGpBEfSr4jpwiPespVTWNEpiGphF2xVsR1L5XrWUqh0RoGeYqU'
    'Q89O1aXlU4Rn0rP2hoqJm+UaTy2HOK1PL9qXys1LqFqgfK3xF1Iyzy2EW6SFXMjs4JYEZBUZ/gB5xXz3rMd6dKdh'
    'bN5Jl3b9uGYDoD6gfpX3/rHhXS9QuJnvEYpLEFc7RtAz2b+9XjXjddMXdY2kcduYQI4yGD5CgYBTGAfpXw2MpVMP'
    'KVarbV6HuQhGslTjpZHyrd39zLoUFrHF5MaL5fy5yzZyS31NcBcaYIyHUglsnH+f1r6HtvCMl3b3006ymNFVwyBS'
    'ivuxl84+XHAK1zVh4UT7UWuYTcx7WO1TznHDLx2PXilQxHsI8yVubUiWD9rLlb20Oes9AFlplstsYiLxQ0yhg6u6'
    'nI56rjoR6108K3dhB59y1u09r5Zg24jmMSg/dyNsm3OCD83c8V1nhrwLqOrSCRYZEtlYq8kah8c9hxkj0rc8V6Ha'
    '2dmugJPbSxgebJIwIMpOdu1yuUYdGXNKFSrW/eT0R0/V4U1aCOC1PTNX8T28V19rkn0ySZQ1xMMrbyEBS0uz5kAH'
    'UHoORxW5H4V0z4e6pHPdSRahC8YaC6tJEM9ndq26KeIA52E9c8Fciuhtrk+BbeCXV7UiG4h2pd6fKjSMCPlW4hyU'
    'kU9mwPQkV5Dq+sJqYkt7eCJvKd5FnVdkphz/AKtlHBA6juK9v61ChFa+8cn1fnbdjuNP8Sadp2sXep3unxzQaiRL'
    'cxJgxxTvx9qtm5CpKSQ6HoTg8YrxzxZ4Vg8P+JDq8ELrpbyfOHjKHy5hg/IemVO5QOMg4rofD+iX2tTtPpXzqABK'
    'DyhEnBV88YfoPU4rrtX0LSb3whKZbu7l1TS7kW09rM5kRICwCuhPTb0578VtDMlVVpfI53gna6Pn++026k0WaeBk'
    'ubPSLkw5TAdUn5R8dfLbHHZTW3oCwWugya/YyGLVLSSOJIjyZYrnchdFPZMYJ7ZBFemeJfBy21he6pobQ3dhbwW1'
    'vcXEK+WrRTj5PNiPO9WGCw43VD4M1S00Nt3imJWsbzSbnShKEUtEI8vERgdQ/DHrg1v7ZR0TMY4bXVHkSaude1S7'
    't4bcxvqN8rKgcnGePLyx5G45JNdhYfDO71u9sNF0S7inu7lrqW5wd0NtHajrvH3ieentXoXwC8KaDdW+veINeEQt'
    'kEdl504ykIucl36HBIwAexrA8R+JpfCPi3U7Dwqght7eGTTLeTrIkTEM8gIxmR+eT2NaJ+9zS6kSpK2xBDZaF/wj'
    'cfh+cx6ddad502oXTH99LvO2G2tkU5d2HLehOTWv4P8AhVpWr2YOoXX2Zo5ftDwRRmS+EW3JBGQEjRc5OcbueldD'
    '8PP+EFt0tp7q3n1XXJZxLJ+5kKQIBkhS4Ck+pY9eld5a3ulzape+LvEcDAahcyWcNlHKISEjADvM4GfLVcA4B3Hg'
    'Vaq3epSoq17HhfizwZcaT9ludOt5ls9UWSa3s3lEkot4DtR5EUDg/wALH+LkVmap4ItWvYLG2uoJ7i6t4JY4bXdc'
    'LFI55hYr/wAtAOXPrX0ZfnRfFs1xc+HtPj0CwsbdnutfvjNOwijHEcUZOCSeEXGfasfwH4B1h7B9R0e4k065n3OH'
    'EHnai0TE4ZUwI7ZXHI3Hce+K0U2mZyoKWyPIvB1i/hXxLLNFqNno4jDwSXmpoD5LdGlSI5BlA4X5TjtV3UdR8EWU'
    '1xa6BNqeueaGPnXC/ZrSSQ8s5jHzOOpzgV00nhbRrG8vftwe4vs/u3uHE8hkzyWIyin6npWjNNcXlhNpDaejMwUx'
    '3KxKrLtxuztGCewIP4VUq91ZGX1e2hwmh6Lq9w9tcyRJFYgyMgjkW33MoyWL8sFHr2HFaPizwbcXWnQXEIuZ5rx0'
    'zdKskyGID/UxzSElgeenFOuPDOq6VIJZoJI1kGcODhg319e4719SfC7TL3VfCtzoupkNYHCwgNiWNiASFYcqg6ip'
    'hVbdhww6ejR8g+DPDMcl1d+H76yhU6mBbxSyoS1uwPyyLnkbv4sV6x4Y+E3iTwr4w0uSQNf2cL+YJoUISPJwy9sE'
    'j5snPAxXuupfCst4it9S012iTeGdy4bZtGVKqeeGHI75zXrFtZTxW0cdw6ySAfOyjapPqB2rpo1XHRill8W7tGLH'
    'aKigAdKux2inlhWwtqPSp1tiO1aSxCOqGFRmLbDoFqUQsBgLitILtPOKQyIAeawdRs39kkf/1v33xxk04c9BSHGK'
    'BxQMx9Y/1Mf+/WunCj6CsbWjiGL/AK6Cthfuj6Cs4/GzR/AhT1oOKBil6dq0Mw4HSk7UueKOooBjW+6a8O1A4+0/'
    'V/5mvcG4Q14VftxcfV/5mvNzF6I9DL92bXhk50yHvxVbXD/pp/3F/lU3hfB0uD6f1qrrxxen/cX+VedU/gI9Gn/H'
    'fzPPL0/8TeE+xr0/TG/0dMV5VfOBq8A9jXqWlnNuprz8K/fkejivgidRbsdtWetUoDhate4r2IPQ8mWhJmlBxTQR'
    '3oPtWiJaJARU8ZGKpg44qxGTiqTM5LQsA9qXnqKYMHmn7q0Mhc96duzTM56UoA7UXFZhnPSgmk6UDp60gFJzSdel'
    'KOfakPPSmBJD/rkxx8wqaX/WN9ahg/10f1FTTcSMPetYfCZz+IYMZxThgdKj5pQ3Y0BYkzzSdRTf85oNAAfWkznq'
    'Kbmn44zSAbjvQeKCfSm9aAFJx2pCRSZzRx3FMG7je9ITinUw4NFxDSc80E0jHHFRn1NNAxCT1pmfWl59KCB1qyQO'
    'B0ptGRTSffNNIhiE9qTGKBjNB45qxDTTTilPWmD0pokQ8U3Henc02rQmBNMJoppzVRRIEmkJoyMYNR7s81aIeo4+'
    'tNz3pc0xjjtVktitzURFO+lIapEsiPHApKcx4xTDgDpVpENhj1qIkjpT8nFNPStEZMaJZl+5Iw+hNPF3djpK/wCJ'
    'JqI4ppOeKuyM2yz9uuupYMPdVP8ASlF654eOJvqmP5YqlmlNHKuxHPLuW/tUR+9bxn6FhSGe1PBgI+jn+oqnnNIT'
    'iqUULnZbLWZPKSL9CDTNtk3/AC0kX6oD/I1V5pKdhc77FsQ2pOFuMf7yH+maPsifwXEZ+pI/mKrfSgnHJot5hfyL'
    'Js5D914z9HX/ABqM2N12TP0IP8qh6jNLVJPuTdPoK1ndKCWicY9jUHlyD7ykfhVkSSJwrsPoSKk+2XQ4Er/ic/zo'
    'uxe6Z5UjrTDxWn9tuD1Ib6qp/pUTXDNy6Rn/AIAP6U7sWnczzz7UY9av+dF/FAh+m4f1oL2jdYMH2c/1zRcnlXcz'
    '8UuMHirn+hn+GRfoyn+goC2pPDOPqoP8jQ2VbzKmO9IVq4IoG6TD8VYfyzS/ZkP3JYz9SR/MUcw9TPZefSkC1pfY'
    'ZD9xkb6Ov+NNNjdDnyyfpz/KjmQ+V9jPKYox2q21tcD70bD8DUJjZfvAj6indMTXkQbTTdp61Y28UgApXFYiCZFI'
    'RxVjbTSo7UXHZkGD3pu09qnK45pMelK4WRARQy5FTYPegqOmKVw5SsUx2qMrirW0jgUhWi4WK20U0r1qwVGDxTdg'
    'pcwWKxQ0bfepypFMIFO4rEO0/WmEcGrJU4qNloDlKpU0zbVgr61GRTuxWICnoc03aasdaCAOvNHMwsVdpPFNKYFW'
    'Tk9KYRSJ5SAjtSEVOVBNN2incVitjNNIPU1a2Z4pDHxRzCsU/YCk25q35R9KUQ45xQ5C5LlUQM3arcEbRDkVIinP'
    'HSrAXispz6GsKaWpWkxjOefSs+QBuuRWw0WarPbAniojNIcoNmfFD5jbRx3J9B61DPIGIRAQi8KD+pPua05YzCph'
    'Xqfvn37D8KpGKtVMwlC2hTpu09qseUaXyznNHN2M+UrbWpu09hVnYaCKlyFykAX1pwXFTbeaXGBUuQnEhx7Umypw'
    'KdtqHIOQqeXT9tT7fWkqHLuHIRhAads7dalAp4XvUORSpkIQZ4p3l561Oq1IE9qzlUNFSIBGOlSiKrKRj0qYJ2rG'
    'VU2jRKqx8U8R+laMNnLMfkUmtCLS3c4LKK5p10jsp4WTWiMHyvWpfK4rpW0ScJ5seHX26/lU0Xh29lwdgUH+8cVk'
    '6yZ0xwkuqOYWKpRFniuvn8OGBF2yB2PUelSRaAwPzuMeo5rF1TeOEfY5EQHNSeRXWHQuflcH8xStoUv/ACzBI9ah'
    '1TVYVnJiAU7yQK6U6NcqCSvNVJLNovvjFS6pf1byOcvLR7i2kgR/LZ1ID4zjPfFeR3Hwot7hpJ9RuXYhyVKZA2dT'
    'uz3/AJV7m0YzgCo5rZLiF4JBlZFKn6GuLFYWlXanUjdq9jSmpQ0TsfKXim20+yMOk6VGfI37g5+ZiT8pAbugPar/'
    'AIN8DzvqnmtcFZlUvGUGQuRyCTx+B617hF4C0t1d54137jsKjhV7AZ/zmtG+eLRdPKwoHKDADEIzccnceM+leBSw'
    'FWM3WxLslrp+R2uUX7tM8w8SWdn4fSOBZIIJpUkb7QqtGJGUj92VHykn3r5n8R6xqmm3sV4kBDk7keN1lRuTkNGw'
    'O73Dcj1rtfGd/LfatvDTSbmLFpZNz4J4TA+Xj1HUVU0zwNe6nEb/AMvdA2ApBA3E9AoJ/wAmvOq5i69VxpLRHXHC'
    'ckLyPI1/tLWpgyIbgyE5CZyM8kbOoHsK6TTfh5Nqdx5VxdQaVIBlWuCyh+2FIHJ9Qa+go/AGj6Pp9r9tV7LUd5aS'
    '4aMsqD+EKykFfc9a6qOwsLyIvbud9n92awkaZg3Qs6Sg/wBTjiu6lhXf969exk7NaI+f9H8Oaf4dum0S4a80G5uL'
    'Ywz3WVmtp/m3B9vGIm6g/wAJHWuZ8VaXqOhTtd2zpdW1/i1uZ7I70dG25cx/eRwPm5HOMg17rqNvJqNtLp2tyWuo'
    'mMFreeMraXcLdgY5NoYeo7+tZ3iMabqei+HdXSBdPvLe9is7xoQEYK2ArEZwwJAZSc8EiuyKp1ItLS39ehn7Nxa/'
    'r/gnmthPZ6voP/CIXELWmtWF/Fp6xHIS7imkyC/qp+8M/dyCK5fV/ANxp2o6hFqkUwh0EiS5gi+c+TcKUDqScFSS'
    'Pmr0X4i+Btb8PX9pqNvCyRNMkdvNkF1cHMak5PCt9w+nFd/458R6HFaxaxEwlvdS0O60jVbZxtmScIHiaRDjHz5G'
    'emMV0ulGV3N2cbfNGXI9OVXTPBfg7IdNin8Omd7e2luYtRu51AYG2sI2d4ShBB83gE1yC+GpvEFzqHiJh5azXLsp'
    'IJBkdjJtB9VWs/QtW1u3mksdECi41BF0/JALkXJCkKD69CR2r7F8Q+ENP8NaB4H8MRKq7tYhjuH7yM0bNKxPuf0r'
    '0JSbi2n0OSFFJpNFfwj8I9J0rS01HxPPLfTvEssnmuyxRLtzjaD2HUmvPPDtz4J1XxNqWvT27Xgkufs2laXAjSsY'
    'ocAytGueHPTdgdzXo3xR8Qal4h1I/DXwLm6uZhi/liOViTp5W7oOOXPYcV2vhz4bw+HPD8Om6a62N+YUW4vLdFMj'
    'OOWwXB4zxWqaT5YLYycW9WVNT0LxH42sYtNNlB4e0qN1kKSkSTyFeVHlRYRADzySa3LLStWspJYtRu5JbeCEBYYI'
    'RbwyEDGXKZZzxzz71u2mj6rbTLKdQeYFUV1dRg7epAGMFu9dRGNnWt1NvcXszxbUvB2meKrGa2SzSC+JKxuFKRuw'
    '5JU8FsDrmuAPw2uTDFaXCzTXaMQS2SAg4wx+6D6AZr6sRlJyQMg8HFWTCsyhXGQCCB7ip5U9wdK/Q8O0fwYb/T5P'
    'DWsxSiKGIFJFf/VPuyDk9WPYA4Aq54S+Hl54a1GS6W6ynmZJ5JmTHRhnCn869sFrntUy2qgc0+dLYtYc55bdiauL'
    'ZZ5Na3lRryKieaMDrT9o2X7GK3KX2eOMZYVSnuMfKq8VYlnQ9TWe8sPOeaqKb1ZMpJaIz5ZJG6Cq3lSE5JrSaWED'
    'pUBnjH3RW6bWyOeST3Z//9f9+B9KMim9ODS4zQBia5xBF/10FbKcov0FYmvH9xF/10FbafcX6Cs4/GzWXwIdRR1F'
    'JzWhmKKXIBzSDHSjgGgGJJyrfSvA9QPFzj1f+Zr3p/uH6V4BqT7Rc/V/5mvMzLZHo5duzd8KnOlQfSqniBv9PP8A'
    'uL/Kp/Cb50mDB7VS8QtjUG/3F/lXn1X+4XyPRo/7w/mec3p/4m8B9jXrOlkfZ0rx2+lH9sQL7GvXtKb/AEVPpXnY'
    'V+/I9HFr3InUQ8LwashqowthatAnqK9aOx5LWpNnNGfTmo91LmtESyTce9TxnNVutTwnGcVcWRPYsZ5p2T2NRg08'
    'YrS5kLnHejNNz60E0ASbs0bqZn2pfemhWHlqM5pufXmjOKLisTQH9/H9RUs5/ev9TUEB/fx/WpZ/9dIP9o1rD4TO'
    'XxDOlLUeaeDgZphYkzxmkOKQGlzmgOUMGgYH1pM9vWmEgcUBYcc55pOe9NzRnvQCHdvSm0daaSKYcwpqN27UM46C'
    'oiaCQPXNNHJpCaQGqQmx+ajJNKTmmk0yGwJOKZRzRVoi43qaaSacaaee9MQGm/WlJ96bVIQhPrTaCaT/ADiqJYH1'
    'qMmnMaacCtESxjHsDTOvNLnmkrRIT0F7ZqM46d6eTUXfNNEMXOKTPNNY/lSE5q7EX6CNz3pnFOPNM49aqJDYpx+N'
    'NY8cUpphq0ZsQ+tMOKcfbmmVRmxDSUUhJz6VVyGgpv40dqSqJD60dqXrTaYBS9aSk96BDulJTM5pc5pk3FBo6Uo9'
    'qD0p3CwnvSHB6UcnikwcUJiDFNxzyKeBSEU9AshtJTsUvUUNi5RmO9HSlxRS5gsMYc00ZqbBppHNPmGIskifddh+'
    'Jqdb24UYL717q/zD9agODTdtLR7j5mi28cU8Zlthgry8ZOSPdT3H6iq200sTvBIsqdVPTsR3B+oqzMqpJ8n3GAdf'
    'of8ADpUspSurlUig9Kk70mB0pXHYiIpu2pttNPtSuFiLHtSD6VIVNBHFFxpETAdqQCpMHpSYpFcpER2phFTd6Tb3'
    'pNhYgK0zbVjGOtIRmi4uUhxUZUVZ28Uwp60XDlKhWmFeKsleaYVouHKVdlIVIqxtpMA80cwuUrbd3WkK1axim7Rj'
    'k0uYOUq7Vpu09qtFU79aNuBkGlzhykG00bO4FTBc09Rg0uZjUSARmpRCO9O3Y7Ux2OM1LbHZIlCR9KCqDpVbcaNx'
    'qWg5l2LRXPTFPTCAynGRwv1/+tVNXYkKOc8USzZbavKrwP6mpsHOlqHlKc7jUbQA96PMI6ijzD3FLULx7Ef2X1Ip'
    'ptD6VZWTvnFTebgVLlJbFKEGZwtWzyBTjapnpzWgJ0P3hg1MjxZ5qJVJFqjB9TCNpKzfKhxSfY5R/DXUJJF2qZY1'
    'k5I6+tZPEyW6H9Ri9mckLaXOMVItrKDypP4V08iRxAkoePSqgv1H3UOan6w3shvBwj8TM1bEyL8yEGs6W2ZG2gZr'
    'oPt7g5IwKl8+yZcyLyTU+3le7RTw1OS0ZgwWnnEIqnce9bdtoBb/AFzYPtVqE233kGPxqwt5t6SD6muepVm37uht'
    'SwtJaz1Mm60d7Vd4O4VneWV6iuhuNSkb5Uxj1PP6VA+ors2qgBPU4GPypKrO2op0KV/ddipbWFzLhgh2+p4FaBtG'
    'tv7rk/jinxarJgLIoYdu1aEV3bSj97GR7isJ1JHRSo0+j1M3zpe549BwKsnUMYEahBjsMmrrx2gG4dD6mqgFk5IG'
    'Sf8APesHJPodKpyXUli1eeH5UbjPerKa7Op+dt34ViXCwq3yZH61UOTSuh800dY/iJTz5eWx17VB/bVyxwpVQfau'
    'cVORV6KFAMsfwqZSRSc5HU2urBOXkLH0ArQOrORuVGI9q5OKSKMH5cmp47uQHI4FZc9up0Rsac2pXkgIRdue/es0'
    'rI/LZP1q6t620DGfqBTWulz90ZqHMrkuVVti5wKPsoUnLAU9pS5zTCjv2NL2iYezsRM0S8ZzWdfWllqUJtryISxH'
    'qp6H61oNCfSm+TilJqS5ZK6BRa1R43c/DGCbUZJojHHbylkCH5jGjD7y5/izXUQ+FtP0vSnsLS084J9wu3LOf4hj'
    'pjjNdwYiKTaRXDRy7DU25QjqzadarJJNnmut+H/EV1p0bRXCzX20o4fBiC7fuqvTOQBu966HwjpMuk6UsV1CkEzn'
    'c6Id2D7t3NdOfvhe5H8qmCVvTwtOFX2ybvbqZSnKUeSxhXOgaPeSSS31rHctIMHzgJAB6KG6D6V5R44+FdlqOmSj'
    'wwfsU+M/ZsnyJccgAH7jA9COM17qV46VE0OeK2qU4TVrChKcWnc+SdY8fS634Mn8M67E9t4h0wxgo6/61rdhiRT0'
    'zgfMPxFdJ8UPDsXiXwVb+MrSMLci3iaRgP8AWRuuBu9SprtPib8PIdds31rTYwupWy7iyjBljXqD6kDp+Vc34X1y'
    'K/8AhHrOj3fNxpa7MHr5ckgKfkSRXmVZO84VX0uvkenQgvcqUu9mvXQ8G+A3hEap8QYLq7QMunQyXYz/AH1wqfkT'
    'mvT/AI1atLr3ijSPBOgBpr61lLOUONs0o2qM9iq8se1YHgLxDF4LTXdYiOy6ax+z2vAP76V/lODxgYz+FeofB/wn'
    'K6z+O9XBlvdRLiBn5YIT+8k57ueB7V1UaynTUY9Tlr0JQm5S6HfeA/BeleBtI+xWSiS7mw13ckfNJJ3APXaD0H4m'
    'u1IzzU0dsT+NcH41+JXgn4eXVlZ+K9RWzmvgWjTazkIDgu2Bwue5r0YyeiOBwvqdsV44FZWsm9ttJvruxUPcQWs0'
    'kKtyDIkZZAfbIrobZra5t4ry2kWWGdFljdTlXRxlWB9CDmvBfjL8TtS8KTw6D4fdYLmSHzp5yodlVuEVA3Ge5Jqa'
    '01GN5OxVGi5ySirngv7L3xI+Kni74ka7oPjW+/tHTk09735lRRazCQJGsZUD5XyV2n0zX34rxRjg1+RNn4/8SeCt'
    'Su9d8O3rWdzcti4ZFUrNl9wEiEYI3c4r9H/hd4wm8feB9L8USKEmuo2WdV6LNE2x8exOCB71vZ8sXLsjNyiqklBa'
    'Xdj1c3CDoage7xVPa/SneXxyanQd2xk1w5zis2RnJ9M1pmOo2hz1q1NLYzcWzGZWbrURj7VsGHPGKYYAa1VQzdMy'
    'fJNJ5GBzitXyaaYKftGT7NH/0P33P4Glye1IMeuKTP40DMLX8fZ4/wDroK205jXHoKxNf/494h/00FbacRr9BWcf'
    'jZpL4EPGPegcUg6cUVoZ6C0HB9qPejigBjkBG+lfPOqn5br6v/M19CSn9230r501Zji6x6v/ADNeZmWyPQy/dm94'
    'QP8AxKID7f1qn4kbGot/uJ/KrPg050a3PtVDxMcak3/XNf5V51X+AvkelR/3h/M8wvn/AOJ3b49DXs2kn/Rk+leI'
    'X7f8Tu3+hr2jR2zbJ9K87C/HI9HFfBE6uA8VZViOKoRHAq2pzXqxeh5ctyyDTulVw3PXin57VpcglBqaI9aqg44q'
    'aLPPPNWiZbFvPvinBsd6g3YFO3Vpcytcn3Ug4pgINLkdjTFYfuoDfnTQRS5HegQufWg4xRxRkdqYE1t/x8R/71Tz'
    '/wCuf6moLfi4jx/eFTXB/fP9TW0PhMZfGRDk0/PNR0fWqaKJD1pM4pucml4pCuOJz+NNxR7UUCGn0p3NMJI5ppk7'
    'igkexxUZb0phbPWmc5p2AD1puetJkml5qrCY33NGeaDimlsUyWxSfypuaaTSZ9aaIY/NIDjrUZJ7c0ZqkIceaQD3'
    'ppPamk1SuS30HE+lNJzTfzpuRViFJ/Gk600sM0hJzTVxMUkU1vrSZNMJOcVokSxM9qAcA+tFNqxMM/hTSRSHk8cU'
    'wmqRmL+NNJHTNBpn0NUiGxTTeh5pefpQatECHFMNOxTTVIhiH0puKUZzzRg1ZmyM0nU1J1ppHNMhjKbUlMxTQhep'
    'FB96AO9LjHNO4iM0hWpCDTenNMBuM0AAU6kINAmhen403ntR9KWgSQgHc0uKdS4FA7DSOOKZ9alxUqW8rqWVCVH8'
    'XQfnQKxV2ntS7Kt/ZZCPkAP0IP8AWnG1uB/yyb8qXMg5WUtvHFGMVa8mYDlGH4GoypUfMD+VO4crIMUwr61PxSE0'
    'CIMYpuT3qweelNIGckUxEZ9KuyZNpA3f51/AEEfzqpgdMVbYf6JAf9qT+lS2VDdlQ9aTpTyBSY5qdDRIKQ47U7FI'
    'fakOxGc9aTNPNNxSYxmSKTNOIxyOaSlzDsJtpuPenDNH4UXHYZRjin4NBHFS5DsREUmOMGnEHNMIovcLDStQHIOK'
    'tVEVP1qVISRCePxpMU8jmkxzmlcGhNoP1pAq07kUzBHNFwuGFpCQOlGCeaQiiwXGk+gphLdqlx2qNl53DOR29aL9'
    'iWNwTQRkc1EkrsxWSJowOhOMGp8ADcTgdc1N31E0QbaMdqZuadisYIj/AL/TP+7/AI0xLRQQxZi68Bieceh9aLvq'
    'KxYXKAuOv3R/U/lUJXvVmVNpCDnaMH6nrURBpXBroQ4J5o28c1JtNLj8qXMHKR7RS496eRS4pXHYjFSq2Oopu3NA'
    'XPapZSuTrLt+6Kd9rmzkNUQT3o24HFZuMepopz6MnNzO33zkelXIYopF+4B/Os3FTJIy9OKxnBW0NYVXfXUtSaQJ'
    'DuVyPYmgaKFwc5/Gmi4kHep0u2I+cn61g3OOzNkqUndxK5sDG2OlO+xEdGFXA4fvmnrEZOAPxrGVWS3NY0IPZGU1'
    'ud2Cc082TLyRke1bX9nkjIPNWo7NUA3GsJVn0No4RPc51IkzhjgVcWJE/j/KttbS2K7cbT68U8afahssWY1i6je5'
    '0rDqK0OZeNnY7Sce9NER79a7LybONcfJ+PWnKlhIdhAz6rU8z2H7Jb3OO8s0eV7V2/8AZlkecNUsel2wORzUPm6F'
    'xpxOKWBsZxU3lOO34V240+MfMFApGt7RTiXGfaolGZpGMDjUt5HOMVejsZGXgYrqBFbZzFtwOtSo0WP3alj6VKpO'
    '+rLvHojnotOkkO0cVaXRWPLnaK34tx6qFNTlCww7cVtHDpoh1bPRGLFo8cZ+bmra6cFO6MAfXmtDGz7rZ+tRvK/Q'
    'H64q/YU4q5PtZy2KD6RERnvWZPp4QHaMgVueYF+bkmqNxNI47AVjOMLaI1hz31MBo07Cq7R89MVqFeScVA2M+tck'
    'jqSuZnlfv17/ACsf5VYEQ71BNd28epQWzyKskkT7VJAJwR0FaY2mru7Iz5VqVfKFJ5dXQF7CpVjz0o1fUOUzTGcV'
    '8peN9AufC/iK+awLR2OqIC8YHysjMHK/8BccV9hiHjJrzP4n6VBcaGLh1+eIsAcc8jOPzry85g1h3VjvH8tmejlU'
    'kq6pvaX9I+NhpbalqsVhCf8AXTRx8ersF/TNffFlpMOm2cGnwLiO2jSJAPRBivlPwJo6v430tJV+UXSsc92UFh+o'
    'r7La3ccmqyiV6bkgzeNqiiZmwKM4xivz1/aPk8N+OPFUFxZTSGSygNlMxHyHY/3oz3GCc+9fffie5/szQb68ZtpS'
    'BwnuzDaoHvk1+eXjHQW06/kguMGUBS+DnDMAx59s1risX++hQ+f+X6mWCw9qc63y/wA/0Ps34ca/oPiPwnZJ4Yle'
    'S10+KKwKyDbJG0KBQHX3HIPcV8e/Ema78ReKPEWvuWFrb3iabacfK/lKQ+D/ALIBP410/wAMtW8VeFdPuNP8L2gu'
    '7nxSgitHz8tvc27FJC4/vKhz9Oa1fjHoV14J8J+HvD6eXMtpbXFzc3BP+uvZ3Hmt746AmtMZHnirPb83sZ4P3Ju6'
    '3/Jav/I+KtQit3ufIuWxGZl3/wC7uGT+Ar9Bv2X5P7O0vxF4BvCDNoGqsU/2obgcEexIB/GvzL1XUrqSeR2C4bPT'
    'ivvCP/hKvCGiXvxMt0+xp4u8PaZbRljtlXUFCpIQnXPlrvDV7VVOlTjzHiUWq1SXIX/hj8dvHvir446p4D16zgj0'
    'uMX4iSOIrJAbV8Rs7E8hgMHI6kYr7D+90HFfmFonifxB4Z8UDxjb3Ja9kdftcrgM9xDuBdHOOjAc/Sv1FtJIbu0g'
    'vYDuiuIkmjPqkih1P5Gs6jkkm/wLpyhJtRT07lfb2pfLP0q/sTNKVSs/aI25DN8qjyhWjtUHpSHaKftB8hn+VntS'
    'eSewq8zegphZqPaAqaP/0f326UHpkUD3o+lAzB8QHbbxf9dBW4hyi/QVgeIv+PeHH/PUVvr/AKtfoKzj8bNJfAhx'
    '+lA6UtFaGdw/lSdKX6UlAEc+PKY+1fNuqvxd/WT+Zr6Quf8AUP8ASvmbV2IW8+sn9a8zMtkell61Z1Pgs50W3/3a'
    'zPFTbdUYf9M0/lVzwKxOhW3+7WZ4tf8A4mzD/pkn8q82t/u6foehQ/3h/M8svmJ1u357H+de16Kf9FSvDLxs65B9'
    'DXuWif8AHolebhX78j0sV8ETqIzjmrStVNDgVYU16sdjypE+e3enZ9ai607dj3rRMgmyM1PGeDVQHmpo3IzVx3Jk'
    'WxSgmolfPWpAfStDMdntTsjpUWRnml5qhWJenSg9Kbk0hY+lMViTJAzRu461FupCaAsXLQ5uYuf4qtXB/fyf7xqh'
    'aMPtUX+8KuT486Q/7Rren8JjU0kMJpM+tJ0FRlvSrZNyXcKUN6VD70Zx0qR3uThqTcKh3CkyTTJHsc1HyBSmk7e1'
    'CAaelJ9aTNGaoVxenJppNKcdOtRk9hTJuKT6UwnNO4AzTTTRLY2koJpBVWJYGm0vWmk9+lOwhCwpue9DYHNM9qtE'
    'jiewpKTt60mcVQMaSAaMntSHBNJzVpENjmIphNBbimE4qkiGxSaaxNGaQ9aoTYhqP3p7Uwnt3q0QxpJHFJx+NB+t'
    'HuaaI3DjFL0pOtIc9KsQZApOvSjvzRTIYmKTHan8nmk561VyRhPpSCndOoox3qiBn603pT8UYoAYDS4z1o70uBTu'
    'TYbikxTsc0U7isMxzSFakAzRgmi4rEYH6Uu2pMcUuB+NHMCQwLxmnYFLSE80XY2hwMESS3N0dsFuhkkx1IHRR7k8'
    'V5dq/iG91eYmVjHAOEhQ4RB2GB1PqTXbeJnZPDk23jzLmFD9AGb+Yryl+ea9PA0o252tTyswqyUlTT03JfNZT8jk'
    'fQkU9dQvYvuXEq/R2H9apknrUZ5r0VFPc8vnaNhPEGsxH93ezj/gZP8AOph4v8Rqdv21z/vBW/mK57txTelV7Gm9'
    '4ol16qek397OpXxx4gXhpY3/AN6JT/hU6+PdWH+sgtZPrGR/I1xbdetJ2o+qUOsEH13ELabO9Hj6Y/63T7dv91nX'
    '/Gp18fWn/LXTCP8Acm/xFecYplT9RoP7P4sHmWJX2vwR6pF440Vz+8tLiM+zq3+Fab+L9ANrbk/aEVmk2/ICeozn'
    'BrxfHGavTPt0+1BH8Uv8xUSy2jpv95VPN8QuZu23bzR6uPFXhhvvXciezQt/Sp08Q+GX+7qUYP8AtI6/zFeHO5Y1'
    'A2al5RSf2n+H+RSzyt1ivx/zPoBdU0WT/VajbN9XC/zqwkltL/q7mB/92VT/AFr516e9IcHpwal5PHpNlrP59YL7'
    'z6S8h2HyhW+jA0fZpxzsb8q+fbW2vZSGiLIv97JH5V0tsl1Bhvtc5P8A10cD8s1zVMrUdqn4f8E66edOW9L8f+Ae'
    'tmKUclG+uDUbAVwSa1q8OPLvJh7Fsj9a6TSNdbU5Vsb/AGiduI5h8odv7rDpk9jXHVwNSMXJanfRzKlUkoPRmsVp'
    'oHbrUpUjgjGKMCuBs9KxFt4oIqXGOlJjIqWx2RD3pu0elTFfWmleKQcpHjnimFfWpsUmM1IisUzTDGw6Va24pMcU'
    '2IqbWHajHrVoio9opXFYh200irG3nimkegpXCxBtNJtzUxFN78UXDlIioPBGRVKO3xuDklCeEJzjHv6e1aJUmgp2'
    'pD5CDHHFOjT5wT0HJ/CpQlPC4Rj64H9TQ2CgU2BJLEUwrntVrBNJt4qeYfKVcEdqMZPSrBT0pNlLmHyEIXNLswOR'
    'U4TinbPxqeYpQK4U0oQ1ZEeKdsrNzK9kVtnHSl8s1aC54FO2dqylULjSuVAmKcE9quCIdScVZSOPgVjKqbRomV5Z'
    'PanCNvStjy489qlWGP1rF1TZUEYiowqZWlU8E1tLAnXil+zx9TisJVTaNDsZayzHqxI+tSgyDnJrQMEI7804JCvA'
    'esZVOxqqL6mdiQ9Caeqz9MmtINDjG4fjUgkhHoT9aydQ1jRMwQSHrk1bjtJSMgEVoLcW2MOAPpTvPt1H7vLfU1m5'
    '36msaVuhCkVzEMiQ1eiuJipXJZqoPMx5TFLHOyn53AqPaW6lqPSxrxR3UvLkgVaW1yPnOayo7wxg/MRUkd+7ggDL'
    'e9XGtTXxCdKp0NZbaJeg5p+NvKms6FrtiS2AKtrHKfvGt41k17sTJ02n70iU3BHFIJnPCjP4UghYnk1bRdlaU+eW'
    '+hEnFIpt5x/hqu0cnuPpWscGoWC1U6C7ijVfYw5kmUZDZqg5lPXNdG6+1VmgB5rhq0H0Z3U6y6owMN3rG1a+ns0V'
    'YE3O4PPXHbpXXtbCuQ8Rb7aSLYSCyN0HJ5FYwg1NcyubOSlGydjwbxbdXyavDdySMJkTIYH5h8/GPSvR/B3jefVb'
    'm30m+i3TSZCyrxnAJ+YevFeY+MZQuooGz/qxkenzGtT4fLv8U6e3T943/oDV9BXownhlKS1toeBQqyjiZRjLS59J'
    'iI1bjhqwsYq3FF7V40KDbPWnWsiBYsjGDXKeM7B59I8sDIL85/3TXfpEKytfhEliEP8AeJ/IVWY4PmwdRPsRgsU4'
    '4iD8z5d0DTnt/FdjKq8C8jP4FhX1XJCMn6141a2sUeu2smMbbiM8dPvCveZIhk/WvM4aouVGouz/AEPSz6tapTfk'
    'cdqujWWrRRwX8fmRxyLKFzgEr0z6j2r82Pi5fTJr96bXaoa4lOD6biABX6jy7FJzX52fEzwOLvxl4isbeZnTT7Sa'
    '8DAcll2kKR6ZbGarMcNGOIpVLaXd/u0/UWX4iUqNWnfWyt9+v6Hefsy3K3fhfU/ORXltdQDRswBZPNhAbae2cc0v'
    '7SunPLoVjfFj85kt9vYADfn8a6n9m7wsNL8Avqe8tLql5I7r2QQfu1UfXqa6L4/Wzj4XX7JEJDHPblmIyY1L4LD0'
    '9DXXUpqa5umjOWnNwduuqPym1Twy0JsAQSb+MOoA67pWjAH5V+qfxZ8N6SngP+078OT4d0txbRZxEJXhWEOy92Uc'
    'L6V8r+IdIitD8F7iC2V5rq3iyqrzIy3xf5uOcBj1r7L+LulnxN8PfEejJIYjPZTMrjqDF+9A/HbivQq1o1IKE/I8'
    'ylQlSlKcPM/NLwzqNvJ4t0m2vfLe3nu44JEfkFJj5bcf8C/Ov0+8GaTqeheF9N0LVZkubjToPsvnJkB0iJWInPfZ'
    'gH3r83vhV4Bubf4h/DLVL+3a5tPECzX8isMqotpHQH6DaGr9TlxgY6nr/WsMRBUkoQlcMvlUq806sbP+mQbGxgCk'
    '2N6Va4pjMv1rl52elyIriNu9BTtmpdwI4FMzzVXYrIZsH1o2U/eQaC5609RWP//S/fX6cUEYFA9KQ4oGYHiEk28P'
    '/XQVvofkXHoKwPEP/HtDj/noK31/1a/QVnH42aP4UP4Apfem559qWtDMPek6+9HtS59aAK1z/qH+lfMWsn5bz6yf'
    '1r6duh+4fjtXy9rH3bz6yfzNeZmWyPRwG7Oj8CvjQ7b/AHazfFzf8Tduf+WSfyq14HP/ABJbf6VneLm/4m7/APXK'
    'P+VeZX/3ePyPRof7w/meXXT/APE8t/of517roh/0Nc+leBXRzrtufY17zobf6Gn0rzcJ8cj0cV8ETp0IxVpTVKM8'
    'etWVPHNeomeYyyGFOyKr5PSjcelaohk+eeKkRvWqoapVbnFXHchloNUgeq4NP68VoQTh6lDDFVOaeCemaaE0Wcij'
    'cKgBxSljTuTYkJpM1FnPXil3elFx3LloQLqL/eFXLg/v3/3jWfZnN3F7sKtXTYuJf9410U/hMKvxDS9MJJFQluaN'
    '3Oa0sZtku40oaowQeTS5oC480v8AKmA96M5oAfn0oyelN4/+vRkimhXEyDSdKaTQTTJFJ/CkpAaDxTACaYTxQaYa'
    'aJ9QNNJxSMcDimZxVEj80zcTSE596aTxVJCYpNN7UmaM1QhTTSaTrS9atIkaTQTQeKaWNUiXYac00kn6UpPrTT2q'
    'kQxxOaaTQT+VM7Y60yb6Diaibrilppq0TIQ5FGfWgj1pOKZI40lJ9aDzVIkM80tJgCl6iqFYWk+tLig0CaG+1Lx0'
    '6Ud6Kq5DiHuabTuOvSkIPNUKw0g0mKk6c0h+lAhhGaMc9KfgdzRx2oAj5HQUdKd0o6c0BYQc0v6UUc96BWD60w9e'
    'KeaQLzTQmYnilc+HH7/6XD/6C1eWMpr1nxOP+Kcf/r7h/wDQWrythXs4H+H8zxMx/ir0KpBFMP0qwygVEy12o86R'
    'XbgUw+9TFe9MxitEYu5ERxzTDU2OaaV9apMTIiD/APXqPB61MVOKb0HSqTMmiM8Vcuf+Qfaf70381qJYXlYJGpLH'
    'gAck1fvrZ4dOs96lf3k45HoVo5lzJf1sKMHyyfl+qMBlxzUZzVr5OmaasbSuIoxuZjgAVumcuvQhSNpWCINzHgAd'
    'TXQWmkx2/wA9xh5P7v8ACv8Aiav2WnLZL/elYfM3p7Cru2uSriL6R2O+jhkveluRAcc0hPPFTbcigIQa5uZHU4kH'
    'JoAZGDpwyncp9xyKt7PbFKU4P0o5yeU9QuGDuJP+eiJIR7uoJ/Wq+KsSD5YvaGL/ANAFR4r5aW59nG7RH044pcU7'
    'GKXFQaJEZU00ipMd6MUmOzIcetN6VY2imlaLhZMh+tGB6U8jHFJ7Ur9hchCVpm01Z+lNIGM0rhylYrgZzTcVMcji'
    'jnHSlzD5SEACk4qc+4phANLmHykYoxTtueDRt5qXIfKN20rAhVHrk0/FLIMkeyiocmVylUgjiipdvc03b7UuZhys'
    'Z+FLj1qTB9KcB7UuYfIRYzSgVJS8Cpb6l8qIwMjFDHFSbhUcjAKT2rKUmNRR+bn7a/7THjz4XeI9N+H3gW5Gktc6'
    'emo3WoKqvOwlkZEii3AhQNhLHGTnFdp+w78cviB8YtM8S2Xji7i1A6GbP7Pc7Qk7+fv3BwoAYDaPm9a8h/bn8BeF'
    'fiR4j0C90fUjFr9hbyWt4yL5sLWm4vEh29JVct/wE819E/sVeAE8FeDtRmjeA292trFEEZTMWhDmR5QOVJZuFNVi'
    'oyhTpv2b1e/9dycHUp1KlWPtV7q26vb8up9k7GPUUDg81Z3oTjNYHinVIfD/AIb1XXpZFiWws5pw7/dDqh2Z/wCB'
    'YrjnPlTZ1Rp3dkbIkQyeSJE8zGdm4bseu3Oalw1fzjL8U/iZp/j278Q63rt6NZW6MhnEzja27cAozjZjGFxjFf0M'
    '+CvER8UeDNC8SSJsl1TTra6kXGMSSRgvgem7OKwqTcZKL6q6N4UlKLkns7M3xv7U7L55OalGKXCisZzZ0QpDMN0p'
    'ee9WEWM/xVZWKE4+cVzymdCgZ+0kcU4RMa1BBF/eqYQIMYYVk5GkYIxxBJU6wSntWl5YB9aUJ2yayZqkUPssuaeL'
    'WUCtFYyepNSLEnQ5NTYvmsZv2WU9x+dTLaTg8Y/OtRYYu9TpHHmrVG+5nLEW2KSR3y984q0gvzjoKvIqDtVpQD1r'
    'sp4VN/EzjniPJEMauQPMXJ9jUx24xtINOkkht4nnmYIiDLM3AAHcmlPPPWvSjSsjilUTZBx0Gaiea3j/ANbIq/Ug'
    'VbwM5rw3xNIyareFicCQ9/pVKk27IxrYlU1dnsf2uxLBBPGSeg3CpSgbpyPavmu81AQCJQxX73evafA9+s+gK7uX'
    'KyOMk5IGBxWdSjKOs1ZDw+LhU0g9TqjGtebePrpLNrXBwzJJjHXgiuy1DX4LJwh2kn3FeM/EfW4b1rGdMYTzUIBz'
    'ydp7fSsMLUo1MQqMdWdGM9rSw7rS0X/BPHPE919p1SNQesY6Y7Ma7v4c27f8JFp7HtKfr9xq8e1nVYbbVoJQM4ik'
    'Pc8grz+tdZ4I8cLF4n06PYDiUnkn+4wxzXr4+hWVJ2j7q1b8jw8uxtD23vT96WiXmz7cCCrUa9K8sTxruuAZfkiP'
    'UKM12dh4k025UBbhMnoCcH9a8LDYuhN6M+jrYaqlqjrFQVz+vSgR+XnopJ/GrM1w8i5il2jsQP61zeoR3LhiSspY'
    'c5ODVZliJSpOnTi3fqPBUUqinOR51fXcdtdmUcbHDD8Dmvaxq9pNZRXccgKTBMEHu3/168L1uO5gWSV7DftBOQC2'
    'cfSuJfxHfwWxX5oY4/uxoCAGJ7D1zXzOBxVbBOa5b83TzPdxlGliVD3vh/I+q5AHJGR+dfPGp2Omp458b/aWjUy6'
    'GWUsRyxUMce5wK4e+8XapFCJZbhzn+DeS2PU9hXlniDxatzvE8PmlupJ+b8+tevUqVa0o81G1nffya/U8xOnQjK1'
    'TdW280/0Ppn4Q3ml6P8ADzTYbq7hR5WnuGQuuV82QkAjscCn/Erxh4RbwRrtpd3Ud35lhOFt4mDSSPt/dhR67sGv'
    'z11e8voZmm0m5ltC3JVn+Un/AD6iuSufGuswMYdTjE2P41JXP4rxXZSweIqJRp2a7bP/ACPIrZtQptupdPvuv8z6'
    'E8O/ELRp9c+EcGt7LOHw9pd495czH5ElJZIkH+0SM19I6l8XPAD6ZeQi9N0Xt5Y/LjjZi5ZCu0cY5Jr84DrOm6qn'
    'lzSS2+7qrncn15yKzH0wQATaXfgEdAHKV1xy2TdqicPVafeeXUz5xT9nafz1+4+tfBfxK8I6VcfD2HVVe3/4RvRr'
    '62u3KcpcXDnZEB16HO7pXvz/AB38C4zaNPceyBf6mvy7n8S69ZtsuZDKo/56qHB/EjNZl14g+1sZDAkR/wCmWVFe'
    'm8hnW15ree/+R5i4pnSTUV8nofpZqX7SOhWbSiPRr6UJjYw2AN69+MVzFz+1doMany9Fui2eN7ovH61+en9u6ii4'
    'huZVH++akXxTqiJtlZZgP76Bj+daR4bcVraXzaOefFdeT918vyTPvaX9rXSA8Pk6Q6rk+aJHGTxwFI6c9c01v2sb'
    'FpG8vSgI8fLmTkH1PHNfBp1myuP9dZAE91b+nFNL2LgCPzEx0GR/KtVkVF6ShJfO5n/rLjb6VE/lY+72/axt1YEa'
    'XEFAOcyHk9j0qJv2trXKgaTGQB82JTyfbivgyS3L5xKAOwYEfyzWdJFIrYwWHqprVcPYd6XZm+Jseuq+5H//0/31'
    'FH60c4o7c0DOc8RnFtD/ANdRXQoR5a/QVz3iT/j2g/66iuhQ/u1HsKiPxs0fwIefbmjPb1oHHeirMwHFFH8qO1AF'
    'e6P+jvn0r5e1fG28+sn9a+oLr/j3fPXFfLOsPhLwj1k/ma8vMtkejgN2dD4JGNGtwPSsjxc23V3H/TJP5VpeBn3a'
    'JbMTzisnxgf+Jw//AFyT+VeZW/3dfI9Gj/vD+Z5fcnOtwH2Ne76DzaIPavn+5fGuQA+hr3rQG/0VD7V5+E+NnoYr'
    '4EdZGMCp8cZqtGcipwc16iPMuSA560pplLmrRLY8D3qVetQA1IpyaqO5MrWLIIqQH0qAE1IDWpk0S9s07jpmmA0h'
    'JphYk3elG7HBqLdilyKBEmRS5zwKj3Z4oz+lMResj/pcX++KluyPtEv+8ar2TH7ZCD/fFS3hxcS/75rqo/CYVfiK'
    '5bmg8c1H1p2eMVoZEvbijdzg1GrYGetKDn2oAk3GnBqiJApNwoHcnL03f6VDu54p2RTEOzmjJppIFJuoEPyBTdxp'
    'hYZpKpIhkneoye9G6oyR1qhAT+tNpCe5ppPpVJAxxPakzTc+tJ71ViRx4ptJnNHWqSJFzxQWpuTmkP51SAXPNIet'
    'JRmqREhvU0EUvApvSqICmngUpNNPrmgkSm07ORSYq0xMaTmkpxHrTQD3pksaaKUjjmjincQnelxRxR0p3FYdRRml'
    'HtTFYUHNN78cU7gUh4phYPpRScU7rQKwmDmk5pfakyaZLQHtSEUUZzTuKwdOtNpeKWi4WG89qSpMdBTe9O4rDeop'
    'RxS5pPpRcGjJ8Tj/AIpxx/09Q/8AoLV5cRmvVvEgB8Nyf9fcP/oLV5Wy4r18E/3fzPDzCP71ehEU9aiZeOlWcnpQ'
    'VBrt5jgcSicdKYVGeKsunpUBAHWr5jJoiIowTUy/NxipDA5GQtPmXUXI7aFTZmrdrpbTq1xM4gt0+9I3c/3VHc+w'
    'q/BYrAoutRBWM8xx5w0p9vRfU/gKjubuS7YbwFRBhEXhUHoB/M9TUubfwjVJL4/uA6sliQNHgEBXgTv80x9+eF/A'
    'fjV2bV9RbT7SSaUS+a8wYSKrA7SOxFYTRF+gq5PbXBsNPVVLgy3A2DqclenvU2hdX/rRlc1S0knpbp6oqy21nesA'
    'sRgmYgAxZZCT/snkfhmugtfD82koJLpQZHGQ45XH+yf51p6dpI07EsnzysOM9UB7H/a9a345H2GJ/njb7yNyPqPQ'
    '+4rnq4t/DB6HTRwKXvzVpHJ7QCeKaUz2rpW0uKTcbaT5v4Y2HzH1APQkVmNbspwQQRwRWSrJmzw7juZ/lY6CnbD3'
    'q55JqQQZ6ih1QVEoBM0MnHFaa2p9KcbUgH5T09KPaoPYM7iReIx/0yi/9AFQlc1bnHzJ/wBco/8A0AVXxg18/J6s'
    '+njHREe2gDtUoAHBpu2pLGEcUzbU46U0qD1obAi2k0m3NStxTSO+etS2UkmQlfWmlamIppFJyKUSErxTSD0qx9Kj'
    'YdjU8w+UrmnYqTaKNopcwcpERTSoqUj0pmfWpcg5SMim81L1pMVLY7DAM/jUjDLH60oHI+opWwWJPqalsaRFso2E'
    'dKfgZ5p2e1S2VYiww60EetScGm57UrjUSMim8561JTD9KlsfKRk44r41/aE+JGsWniKXwZpF29tb29pHJc+UdryS'
    'S5JUsOQAuOB619klkVsucAck+w61+TPxK8Rvr/xL1jU4iZEubm6wRyBEh2Rk+g4Ar08qgnUc5bL8zweIKzhQjTg7'
    'OT/BbnMS33+kMr/Mx5yeSc9629I8fax4PuDe6NfS2UoHJRvlb0DL0b8RXFFJGu4GP8W4H8DXN62ZN6xkbt9ygwPT'
    'Ne9WqLlfMtD5GhB8y5XqfsV8J/FV143+H+jeJrsg3N1EwuCowPNjdkbjtnGapfFXX/Co8K6t4W8Q3wt21G1aEpGP'
    'MmUPyrbB7jPOK85/ZF12K9+HN3o7EFtN1KRQPRJ1Eg/XNeDfEXxKuueP9Yc/MJpXWLv8kLeWoH4CvjamEi6tSnLb'
    '/M/RKONksNSqw+Jpfhv+J8T+MPB/hbWvijb2kZnS13QRyOoHmyKq43lCcbj3Gfav2g+D+o6JL4J0jQtO1Jb24061'
    'ELq42SgKTj5DzhQQBivzNHgezbxMPEKlvNB3FT03AYGK9++GGsyaZ4+0JixVRdIshBwCkh8og+x3Vx18DCEVOTd4'
    'qy9P6R6GHzCdSXIl8TvJ26/0z9DV44xUi7e4FRSgK5HcHFQl8dK4nFnpxL4CE9qkEaHtWYJmHSpVnPc4rGUWaxRo'
    'iEHnJqTyiOhNVI5ya0I3yM1zSubxQKrgdalAf1NOUoalytRqNjR5g71KGbrSBhTgRjNMhvyJVNTK2TioFIqYEDp1'
    'rSLMJItq+3rVlJF61lSzxW6GWdgqr1J4ArGu/FOmWjeWhM7Yz+76D8a7KMpydoq5y1eWOsmHj7UobXwxd2xkVJr7'
    'baQg95JWAH5Dk1v6Jq9pq+k29/DIpDKFbHZ0+Vh+BFfNHxC8UnXPFGj2Fr8kVpdW2QxH+sklXdn3C4FReEvE2p6X'
    'Z6hYRf6s3bEP12MSwIH1xmvoPq01Rj/M9fvdj5GGaRlj5r7Pw380r/rY+qzcR/wsDXgXjW9QanfIT/GefwFXfDPi'
    'Zl1Qtqd2fJ8ph85yu44xxXHeN5kuLvUbm3cMjZKsOh4FVhqE1W5Z7WN8xxVOWG54d/0OX1e6Zo4HUZJLA849K6TR'
    'vEb6ZpCCWbZCZHPBwS2Bx+FePa3qrxxW0e5gVkccA47ehpINRkutFhVySwaXOe+cA5/AV15jlnt6Cg3bX/M8TLs2'
    '9hXc47pf5Hea/wCOY5JtltKFIOCc8n6ZNctqGuXF7aIJHORKcfjH/wDWrybV5VuL6PaABFIMYOehFdrKrx26l8EF'
    '8jHzY+U9cd6WGyalha1Hk8/yDE5/XxlCup6JW/M43xDJLLqELbsjy5f5pU/hOVofEtgSTgTcnn+61U9YlzfQ55/c'
    'yckH+8v0o0ZXOr2zLkYfPH0PvXv4jD89CcO6f5HzOGxbjiac77SX5n0DPrT/AGpLcMdnkvJ/wINgfpWdq3ia+WSK'
    'PTsglSzEDOB2rk5Ll4bhWJziN1z7HJrCv9Ut72OCe3z0YNuGOn86+Xw/D9JqlzRTUb/ez7erxFVjKradm7f0j3rw'
    'z4y1eOAo07EqRnnK59q7qL4g4Xbex7h/eTg/lXzloOoCKwODjlvwAOa0DqRlTerFlIzn2rzquVyhiJunpG/yPbo5'
    'wpYeHPrKx9K2fiHT9TG6zmDkclTww+oq68el3kbW9/bI6yEZbaM4789fxr5Os9WmV1u7V2jdWyCOCMV774V15tb0'
    '0TygCaJvLlA6E9QR9RXoTwb5OWaMKGPU5aGHr3gOK7jaSxY25Ynar5K4Ho3WvnLxd4e1fQ2Zb23YRHO2VeUP4/48'
    '19tRrLeBLTeQMsyr23Y6e2a569sre6je2uY1ljcYZHGVI9waVOjFuzRnUlUmmmz86L63ecsI48se5GTXPS6VdsCb'
    'oKkYB4fAB/DrX0r8S/BJ8MOuo6SSthcttKdTFJ127uu09q8IuFdmY7FYnuxya7I4eT+Gx85iJunJqb1PPrnSEwGi'
    'KpnqGbj8KwS01rIVQ8A845U/0r0aaBACGt1J+v8AjWPcWAcGSKHYw7jkflXp0IyXuz1R49eUfijoznFvI5o/LuIg'
    'M9dvQ/gai+w6cW8yB/LPoc4ropYI2GLiIKw6FRtP4joaypLcZxHnHp3rro0Iq/KrHHOpJv3ncyJIoAxR1DD++tVz'
    'b2f+2fStV7ck5xg0w2vfHNdKpW6manfcyhbp1UlcetK0b7hxv+prWMAzwuP1p32VsZ21ooodzIWJ+hG2g27k8Pit'
    'U25zxmmm3NWqZHM+5//U/fXPHrijrR+lLxigZzviP/j2h4/5aiugTiNPoKwPEf8Ax7w5/wCeoreQZRcHsKiPxMt/'
    'Ah2eaBnrQBjkUDJqyUKOaOKQ9aXtTEVro/6M+fSvlHWjlLz6yfzNfV13/wAesn0r5N1n7t3j1k/ma8rMtkejgN2d'
    'D4E50O2x6Vk+MW/4nD/9ck/lWt4DB/sK2x6f1rF8ZZ/tlsf88k/lXmVv93j8j0aH+8S+Z5PcMTr0HPO0/wA69+0I'
    '/wChp9K+epz/AMVBb/Q/zr6D0Mj7GmK8/C/Gz0MU/cR1kTcc1aGKoQ/dzVxTkcmvTR5hOvWn5qEU89atEtjuM1Ip'
    '5qDrUy89KpbkSZMCM1IDVcE1IGrUglDUm6o+aXcKomw/PanZqMGjPNIZLmlz61Fn8aN3rTEaFic3cP8Avipb0/6T'
    'KP8AbNQWDH7bBj++Klvj/pM3++a66HwP1OWr8RULckUm78ajzQDkEGtbGdyVW7daA3zdaYCMYozn8KAuTFsk00mm'
    'Zoz2zQLmH5xTt1RZ9aM496dguSknGfSkzgZzmmFuOaaT2p2BskB70bh3OKhBx0oycdc1RA9m96jzzTSe9FUkA7di'
    'k603tQKom4A0maU0h+lNCHcUhpM00nvViDNLmm49KPagliEmilpp5q0QKTxijI6U3FNz3NMQ7vTGNKSM0N0zTRIg'
    'xRimCnCqE0FJmlNFBIn1oxS0lMBvQ0vbmjoOlGPWncQtL060UvTvmncAzmg56UcYpQadwGYpaU+vSkHWgmwdaMU4'
    'c0hzTCw2ggUvXijBoENwT2p2D2peAOtIM/SgLBxSdRS80nNArDT1pKdgYpeKYGbr/Ph5x/09Rf8AoLV5wY1I5Fek'
    'a9n/AIR+T/r6i/8AQWrzo9K9PCN8nzPIx6/eL0KzRY5FVmVs88VobfalKDGK7FOxwuncyyMVesdJe+PmMfLhU/NI'
    'e/so7mtK30pDia7yIzyEH3m/wHv+VarOTtUAKq8Kq8Ko9AKmdbS0SoYe+syOGG3thstYlUD+JgGY/Un+lXUktv8A'
    'l4t45MdBt28+5FVs80Y5zXK9dzrVlohl5p0OoymU3BSQjAEo4wOgBXgD2xWY3hi+ByrxFT3Ei4raUA1NjHAxVKtO'
    'OiZDoU5u8kU7HQLW0cTalMkwH/LGI5JOO7dAK3Fit0t4hBEsaoz7e5GcZ5PPNUMelaEQzbpn+839K56k5S1bOinC'
    'MVaKIzGDyBRswOKkwRxSjPQ1HMXykPSrg8m7YfaAQ548xRycf3h/Wp4I4PKLy5znGARk0zeFfMK7PfqfzqHI0jC2'
    '5Xm00xH5uh5B9aYttGvJGfrWgspxtc7lzzTpFX70Z3L6+n1FTzvqX7OO6KixA9gMUpUVJ24phouBu3a/vR/1zj/9'
    'BFVsetW7r/Wg/wCwn/oIqrjJ9a4WeokJgfWkIx0qSm8mpuNIj78ilwKeRSEVDkU4kRBpMU89RimNxU3HyjDimYP4'
    'U+l7UXHYippyfapSfzowCOalsqxXNB6+tSkYNMI9KXMHKRGoyPrU2OeKTHNS2FiIClxxUu0d6TFS2OxGo5H1pzD5'
    'j9aeVHGOtOkwpOTiobG4kOPSj36U/FMx71NyuUB1yaMUuPWlA70h2IyBUbDAqzjio254obKRk3kayW8ySrmNopA4'
    'BwSpU5wfpX5VaB4YvLqy8aeJrO4SDTtKiit5I5VLtKtxcgxxI/ZhsBJPUV+rt42bK5QYLGCXH/fDV+c+lWM1l8AL'
    '64YbH8R+JSM9zDYoT+W7Nb4OdT28KcXo3r8jzs1o0nQlVnHWKdvmfO13OAXlX+DKp7sTk/lTNBi/tnxdotrHtMd7'
    'dpbyFvuoLj91uY9gN2alv7WRXKpwBlVx2B6n6msS3S4069iubbKNE6uMeqkMP5V9RiYe0g4X3PgcFU9nVjNrY+uf'
    '2crTUfhx478X+HdeuSktjpl1G0QyImuLM7i5z1O0ZT2Nef2FnJfQ3Xia4Zt0FxDaIMcSPOkkshz6qFH516T8dHud'
    'G8SaV8R9M+WDxZpAM5HA8824SUH/AHlIP4VyXxk8Qt8H/h54K8ONZpc6hqoudTukY7SrFUVSSPQMF/A18fRlXq4j'
    'kk7u938kfodWnh6GGc4K0UtPVsiimtljPmMA7/dHTIxV2O2m0zRV8ZQMD9m1BLMqP4SI/PjckdAxDD8K+QJ/jfqP'
    'ml20eMHrnzScfTivqn4JeLh8VfCvjHwdLbxQ3Y01NWs1Q5Ly2T5I577GK/jW+ZYeqqfOo7GOVYqjKpyX3P0l0jV/'
    '7Z02y1YYAvbeK4wpyB5qBjg+mTWuPevHfhVrR1P4ceHrmFslbJIT9YSY/wCld0bm5PVzXlUMJOdOMm90fRVcTCMn'
    'FdDo5JIk+8wFQm9twMhs/SufJduTzQAe9bfU11ZmsY+iNptUfpCMe5py6rdAg7hx2rFGalX3qZYaPRFxxDe7N7+2'
    'LojCkD8KtRavcgjfhh3rnAwqObULa1XdLIB7dT+Vc0sJfSKOmOIS1bO8j1KOQeh9DU/2xduSQK8muPEwwBaISe7N'
    '0x7CsifUb67UedKdo/hHApwyirLVuyMauaUYq0dWesT+LdMtp2hkckoOq8gn0rm9Z8ayT2xh00NEzHDOTzj2rzWa'
    '6WNtvJPHT3qMzSjrgnPHbivToZRTi03r6nkV81lJNLQ7KTWb+9tLeC5lYiPd35b/AHvXFY9zqCWkUk8jYWJSx98f'
    '4msZryWZUWE7SmQSO+awdUOY/ILE7/mYH0HT8zzXpUMEttkeFmWZOlRlUWrtp69Djnkmur+2ubhiGlv7d2JPQmdT'
    '19q9v8Laba339t2KupJnYqQQdp3ttPFeE34Rb/SoUH+u1G2jYeoaRa9V+Gq2+la3rml2nMccrbTnJISUjr+NXnFT'
    'loynHok/xPm+ErPEQU9eaTT+cGc5rWqHS5ntWDC4VsFR/Djg5NVrrVbq4+1WzkbFTC+vIB5P412HxF0iNrmHVguB'
    'L+7kOP4h0P4j+VcAYxNKzKThwO2OgA/pXbgK9PEUIVY/P1OrM8PWw+InRb0W3pqVXtEuZWjmj83YdwBOBk/Tk1Gl'
    'iYoUgUeWB5hI7kkjpXUXFk8IaXZyF3YPsDj9a5/7He3IhlZyXUONwGOM+ldnMmvI444eSe2p5vdabONQbygcCXHH'
    '+8K6bTykxuYIslYp2ySMZLD/AOtXUWGlXMuoGSb5lRssMdfSrGl6MsEl0+R+9cP9OtauqvuMFgppaLc8/wBU00Pe'
    'Rt3ETjv3YelTaVZpFeQyPxsYk/TBrubzSHa4XYMnYeh96jg0OTJbHQHP5VcqycLXOeGCmqilY4W2vtQ1G9kK5VQp'
    'woUDAzxUTWUcTRwyOVJz8oGTyf0run8PTQqJU4XAGQeTTF011ljklXd5frjNR7SH2Njs+rz3nuZ9paNBZeVt5YlR'
    '+Jqx9jkhLxByVSPhT2yK2XtROQQpGCf1rWsfDmpX0haGIlXGC7cLz35rkaSu2elBSdopbHK2lgwHkpl23Y4HJJ9B'
    'Xu3hLRn0bTdk/E07+Y4/u8YCn3x1p2g+FLXStsrDz7ns2OAf9kf1rs0gjiPmXZwB/Av3mPp7fWvOq4unObhB6nuY'
    'TCypxU5lixbyM3snCRA4P95yMBR+eTXPSuSSat3l287BQAkafdReg/8Ar+prntT1Wx0q2a5v5RFGvTPUn0A7mlCm'
    '76HVUqJK72OC+LE0Y8HzwyY3zTRLGD1LBtxI+gr5OltWI6V6z448Rz+I76NgClvEp8qM9s/xH/aIrzySCVvumvUp'
    'UbRSZ8jj66q1XKOxzL2zgf6sH3IBqJzcAEbgMjGAAP6V0bWjH72DUJtygzgGuhQT6HmttbHDXcEjjc+WPvzWS9t6'
    'rXok0TMMYUD0AFZcliGPAzXVT03OapZu6ZxBtPQH+dJ9l74H5V15sCDwKZ9jIPSt7oy9TlRbcfdpfsueBxXSm1Pc'
    'c037MAfmFO6Jk+xzwszjpUbWZ/u103kDjimPCBxiqTMmz//V/fXr0/OgHHFA+tB60DOd8Rn/AEaH/rqK6BD+7X6C'
    'ue8Sk/ZYT/01FdAhyi/QVEfiZb+FDy1KDTe1HXrVkjiB3pM+lFJkUB5Fe8/493wO1fJesHi8+sn8zX1pd/8AHu/0'
    'r5L1vIW97ZMn8zXl5lsjvwGjbOj8Bn/iR2/+7/WsPxmf+Jy/H/LKP+Va/gEk6Fbf7v8AWsXxsca0/wD1yj/lXm1l'
    '/s8fkejh/wDeJfM8luCBr0H+6f5179oB/wBEWvnuc/8AE/t/91v519BaB/x6LXn4Re8z0MT8KOuh5FXF4FUoOnFW'
    'lz0r0keZImU0/IqL6U7PHNWTcdkZxUiNUGefWno1UiJPQsCnjioQaeDWhKZJ1NFMBFOHSnYTY/OKCab36U0ntRcV'
    'x2acGqLOBQPrTBmjYH/TYP8AfFS3rf6VN/vmoNO5vYP98U++/wCPqb/fNd2H+A5a795FUnHWkznjpTcnvSZrUwbJ'
    'N3NL2xUe7jilB96YiTdQW9KZnPFAOOKdgJM+tKc1GaN3agBxPrRmm5oJwMUAOpPcUgNFNIA+tJS0lWkS2xMnqKTO'
    'TSmmmgQ760/FM9zS54q7CGscHFN5NONN9+lMTYg69aX+lNJx70Z9KZD1FNIPTqabnPWjPpxVoAPHWk6UE038aCdw'
    'HXFFJjHNJyDVITFPFIDzRRkZoQh1FMyBTgc8UxNCgUUUmQaBWGn60DmnHAFJ0HFMBelIefpQfeigQvWne560zvTv'
    'pTuIU9M0deaPalH8qdwsJzTc9yKfkCkPrQmAgpc0mO9Lz1qgD6UUtHuaVwEPrSZpx6cU3r1piaE7UhpelLtBFBLR'
    'm68M+H5D6XUX/oLV55jmvRfEHHh6THe6i/8AQWrzlVdunJr0sK/3fzPIxy/er0DPOBWna26xfv5xuYfdQ9Pq3+FQ'
    'QxhCCOWHf0q7nPvW0pdEZQjbVkju7sXc5J6mm55ppoz+NQaEmaXOKauc+tSYqWwJQOPSplHFRr04qVazbLRLjirq'
    'cW6f7zf0qn2qyGxAg92/pUS1RrFC9KcOeaj3UqnAwahopIeGwafnNRA55zTwKllofmngkHj8femcYp1SUP4xuX8q'
    'YelPGf8A61IehpD3Nu7/ANYOP+Wcf/oIqDpxVi6/1oH+wn/oIqAYrhk+h6iWggzS8UHNIfas2yrCH8qTApfY00nt'
    'mpKSEphp54ppFK47ERFJUhHFJjtQ2OwzHrRjPAqT600j0NQ2FiMgjimVKR3qB2VOXIA9ScVFykgIpuMmse/17TrD'
    'h33seipya4/VPGc4m2afgIB1YZJNa06E57IyqYmnDdno7SRrwzqD6E4rltd8VWej/IMTTH+BTwB6k15Lf6jcXly9'
    'zPIcuckAkD8qzHxJl2JP1rsp4FXTmzzauYyd1BWPQ7nx/cSlVtYRGMDJbk59vauY1nX9Q1Aea9wys3zLGCQowccY'
    'rCQhJFfg4PSpvL3RrtXkMy5+vNdCoU47I5JYirP4maFh4q8SLPGkdyZOdoSTBFb8virxNFNvZBiIgvGE4I9CevNc'
    'YiiIljgMnIx+hFPm1meJGZZm8zGSWwRXDiqTvzUkmduGrLl5asmelR/EawkKh7eRSQN2OdrdxzXV6d4h0q/gjmWd'
    'YzIxQJIcNuHbFfNv9px6hLvfYkgGS6fdb3P+Nbo8q4tFdjsaMYLDo47Y9xXLJQ926tc66deb5mmnbbofSJYdqibJ'
    '5yB+NfPsGt6xE6SpdSMIiAATkDHY+td1p3jVWjH26I7i23cnTHc1M6fK7XNqeJUuh2t/A89ndW8MvlyzQyxpJjOx'
    'nQqG/AnNfCuseB/FngH4G6np/iXyXks9bjubQxv5hWOUeXK2egDnDAfWvtWPXtOnGUmUZ7NxXGfFK0tNd+G/iKyJ'
    'Vv8AQZJVORw8I8xf5VlUpf8ALyLaaTsbyr3pyotJqX6H5NXXiOVLuO2eLc0kgAIHDKfT0Oa6fTgJ7qGNwgeR1XGM'
    'gbiBUnhTwxbeIfE/2eRd8aafqNwB6PDaSSIePRgDW14G8OTat4r0bTI8tJdXkC4HZAwZ2PsAK4amMr+zb5395wUs'
    'DQ9pG0Fv2PsP4+/DHxL4j8K+D9G8IKbqPRR5E0CsqNvaNVjnJPVEIIYehzXyL+2rHrNv4q8JRakTK0egCJ5gPkkm'
    'Wb96V/HH6V+qMsB3Fs5GSR9M18LftyaU8ngrw/4hQAtYai9sxxzsuYiR+G5BXr4GgoV/a3d2rGua1nUwjpWVk77e'
    'Z+XUhWSURE5dlyAK+wP2KtOv0+L/AJ8RLxW+kagZIgceYrqqqg9SWIr5yi0yEeBm8WNGPMGtJpwb/ZNq8xH5gGv0'
    'B/YS0m1a08TeLZoFMomg0+3lYcoAplmCn3yufpXoYyqvZNd9Dw8rov6xH7z6N+A1tqreBBb3lr9k+zajfRRIcjMZ'
    'nZxjPXaWKZ6HFe3rp85H8P5itKBbNgEUxoB0UYAH4CryxQ/w7Tjrg5rxKMpU4Rg3ex9ZWUak3OKtfoYP9nXH+z+Y'
    'pDp1wOu3/voVvMkK8NgCq5Fp/erVVGzFwS6mR9guOvy/99CkNncKCwCkjsGGauvJZqfmcD64pI5bGTIVw2DyKfNL'
    't+AXW1/xOWuoNYmUokaxqfRhn86x/wCxNQ/jUH6sP8a9G22LfewfwqRbexJyFH5VSxLj9n8DKWF53dyPPE0W76FV'
    'H/AhUjaLcsMZUAf7Qr0T7PYkY2A/hUi2VqTxECvrS+vW1aH/AGffZnmv/CPSNydv/fQqT/hHJyM5X/voV6kmm2mO'
    'IRipv7Ms36xAUv7R/r+mS8s/q/8AwDyYeHZost8oHU/MK8xvbhJ7qWVPuliq/wC6vA/xr2z4gvbaLoh8gBbi7byY'
    'h3wfvt+Ar5/JPSvUwNSVSLmz4XiyrGnOGGh01f6GXfQmTWNBWLlzq1rt+u/Ir0nwjEtj471a1A2jfcrgcjhw39TX'
    'BW6ibxP4bjY/8xa14/4FivQ7IwQfELUJIxsja4uQB6dv5iuXNW3CpH+7+pnwxFL2dTr7Vf8ApJ6jqtjDqenS2jjJ'
    'Yblz2ZeQa8qbQihzuQY969SNxn7pyKyktY55pVIGR8w+jf8A168jh/GunOVCWz1XqfoOe4GNaMay3Wj9Dg5YHcMJ'
    'ZFyfeo44RDGscZXgEHOe/pXbyaXF/dqJdI38JET+FfWe2jbU+X+rzT0ONjjkDM0TgE9eO9QfYZ4g3lsPmOTXo9t4'
    'WvZSSkJAJ/i4/nW1D4NJA+0Sop9F+Y/pSeIgupLw0/tHkcNjeFvMU9sdO1dRp+iuVG4Z3da7r+z9H0y7jtZYZ52K'
    'gkgALzXeRLpNtGPIjA47Lk/rWFTFN6JF4anTnKUVK9tzym98PeVa2zpHuM5YYA6Ff8c1nL4NknOZWWMegG416o0w'
    'feJRvG8lRnAC9gQO9U5LxYfmUpFj0x/WuPDSrQum76nTRw8ZJuZyln4QsrQCRot5H8UvA/KtVo4Idm1w2DyqjAA9'
    'j0rL1PxJptuT9ouQzeg+Y/pXEX/jyBAfslu0h7FztH5cmuj2NWr8RrKvRpK10j05L2SIkQgJn2ycfWsfUNWsNPQy'
    '31wkQ6ne3J/DrXiGpeNdduAyxzCBemIxg/n1rg7y7nuHMk7tI5PViSf1rrw+WKLvscGIzqKVoK561rXxNt4t0OkQ'
    '+acY82ThR9F6n8a8f1LVb7V7o3OoTtKw5OfuqPRR0HtVIh5GwOvv0H1NZ8su4+Wh+Qd/7x9f8K9OFCEPhPCxGOqV'
    'vjenYkkl3sWxjP8ALtULYIphJPSmMDmr9kjkdUiYgVSkj3dKusDUZStFGxjOTZmNFUbRfjWoUHanCxlK+YyhE/vO'
    'do/M1fMZ2bMbYO1MeAEVrFtLgbMkjzkdVhGB/wB9N/TNV5NbjTizsoo/RpCZG/XA/StI0Zy2RhPE0ofFL7tTIa1c'
    'nCqWPsCaUaTfycpbuR7qQP1qWbXNVYECYoPSNVX+QzWLPc3cp/ezSt/vOx/rXTHBVHvJf19xx1Mwp392Lf4f5mo2'
    'i6gM5jxj1Zf8aoTafdRDc6cexB/kapJtBIZUOf7wzQbVo1LG3EiMeqE5H0xWrwluv9fecyzBN/Db5/8AAP/W/fXg'
    '0nFAAxzS/Tigdzm/Ev8Ax6w/9dVroE+4vbgVzvib/j1h/wCuq10aY2Ln0FRH4mW/gQ/j60h5pT7U3g81ZKYtAPrR'
    '70nGKAIboj7O/rivkvWh8t79ZP5mvrK75t3x6V8layflvfrJ/WvMzHZHdgepv+AeNEth7f1rE8cH/ieOP+mUf/oN'
    'bHgB92iW/wBP61h+OD/xPHz/AM8o/wCVebX/AN3R6OH/AN4l8zyCc/8AE/t8eh/nX0JoBBtF7cV87XL/APE/tl9j'
    '/OvojQP+PNfpXn4T42ehivgR10BAFXA1Z0LVdBz04r0jzGTg0E1GD60uaskeDg1Ih61BUsfenHcT2JwfSnCmDHQ0'
    '4H0rQy0H0uaaOlL9KBWDOKA3FM/Gk+hqhD884p2RUfsaXigLmjppxfQAH+Mf1p1+cXk/++ah00/8TC3/AOugp+on'
    '/TJ/+uhrvwy91nLX+JFTdzml69KizTs+lbWMB/OKMn1pvvRk/hSGPoDcVGKfkZzTAcTS0zJNLgjmmA/PH1opmeOK'
    'UVVhXsPGM07PFMop2Ak4703v0pM80lAhM80nWlxRVJEhR2paaSAOKoBpOKbmlz3ph68UCHfjSk56UmPeiqRAEUn4'
    '07PGDTTzVANPHNJ1pTTc00SJRn2oPNFNCENJwKd2603H40CEJzSg85oxnpRtOaYEgIxxR0pvTA7U+gQwdaU4paTH'
    'rTCwo96SjHrzS80BYTpTqSlFArBk4xSj/JpMZo7UB0FOM8UnNKM4pBQAp6U4Cj6dKXFO5IlHenYNG3mgBmKME/Sp'
    'MY4FGMmi4iPAHHWjbmpMCkoRLK9/atfaTc2qDLptnUDv5fUD3wTXneABtxxXpyO0bh1OGB4xWTfaFb3khntHWB25'
    'aN+Fz32nsPY11UK6iuWRyYig5WnHc4kD0p/Irf8A+Eb1AH5WiP8AwMUf8I7qYP3FP0dTXT7aHc5vY1P5WYQPY076'
    'Vtf2BqY6wE/QimnR9SUf8e0n5U/ax7idOfZmYi85NSjirTaffr963kH/AAE1H9mul6wuPqppOSYuWXVDVPNTLim+'
    'TIPvIw+oNPAIHIqHuUlqP5NTsP3KfVv6VW3gCpS2YU+rf0qWWuohYUgemZ9aaaY0y0rVNuGOaoq2DUu6oaLUi4GG'
    'OKeDVMMO9P8AOxx2qGi7loHHejtxUAcNU8CPPKsKDJY4+g7k/SgLm9cn94D/ALCf+gioOgpZ51eRio+XoPoOBVYz'
    'Y7V58k29j1VNdSf2pDVf7QB/CaT7SvQg1DgylNFjHpxTDVc3A6YNJ9pXuDS5H2KU49yxmiqxuFHY003IHQE1Ps5d'
    'h+0j3LJGaTGKrfa1/umqN5eXXllbVAGI+8SOPwoVKTE6sUtzYyB1OAKy7jWdNthh5lJx0HPSuXlTVZjmSQ7iMcNj'
    'j8Kzm0mfHQfmK1jhl9pnPLFP7KLl34zfIFpb8dy5/liuP1HUb7U5GedyFLblQH5V4xxW+2hzuMAD/voVG2i3HTC/'
    '99CuiEIR+FHJUnUnpJnHsjDGOarSI0hI6Adcf412UmjXGOi/99CqDaPMi7G2Y7/MOa1Umc7izhpJUjICoZDnr2xU'
    'crt1x5a5A+bgnPQV2U2jzNGxjMSuR8uWGBWHeaJc4TzJ4AVyTmUAEnv+VS5yWyI9mczLqSISinLA8AD5Tzg81mX9'
    '7fGNPI+VWw5x1yCR+VdA2h3DzIbae0IXIKCUEnPp9Kii0g3CBUvbFpIvlcGYDnJNctWU2mmiox1uihYXsqRbpojN'
    'KvX1ZD1K+464q35EV4pMDBlYHHuD1q0NNnjgltmvLNS/R0mUMvOcA0thotzAqslxaNu+8FnX7395fTPcVyQdWk9I'
    'uzOnSSSkzJSIabJviQB1BRlIyNp7EelaVreLMPKeMRxgEAjJVSf5CrV9oeslkKm23g5YtIp3JjgEevvVWLQfEJlM'
    'qNbjOBgSDGAOlVKiqnvJWZcajg+XoKqyFPMi+ZTkBlPXtVmGWa3ULyArBgp6Z6VsweHtaSHy1EXzqc/vBwT3GKup'
    '4c1uRAkhi46/OOfc1DjUlpOJtFxWsWZQYSPvjUDJBAHpj09RWdrX7vQtTVsvG9pMJEOcOuw5B+vQ13EPhe/RRtVM'
    'jvvHWi88M6jcWtxbOsbC4ikjOCP4lIrGdOVuW2h0J397qfEX7O/hiC68Y6pNeytHFb6RegIPu7J42ifk9lVsipvg'
    'hay23jz7Zbuwa1trl1YjduAG0A56ZznIrS+HIutKvvFGxWEkOkXkTYH3eQhzXX/AfRW1C41bUreP54oVgUngASNl'
    'vx+WvIjUjJOC3ckl+B2qi48suii2/wAT6WtdfuW3G4kPAzwK+d/2trvTtT+DF4srl5Yr6zkgC/8APTzNvze20tXv'
    'x8Oaq44CDn+92ryX48eAL7UfhRrWFVjb+Rc4U5OIpVJP4AmvoqdWcXqtDyqsFKDsfBlp4BnT9lqfxBITm88XRTQq'
    '3Ty4rd7c7fcsxznsK+1/2V9J/wCEe+EdksRG69urm6m3LtIcsI9vuAqjBrwvTbSa5/Z8sfDoyUi8SSMVPT5od4/m'
    'a+1fh94Nn0vwHotqNvNosuOmPNJfp9DUSrqdSMPV/kv1Cjh3ThKquyX5/wCR0bzrtJZlyTnOahh1qSwdpbeQZxyM'
    '8Ee9R3Xhq7dGUMBn35rBm8L6o54kUD07V08lzKWIkuh2UPjOwulzM2xgMkE8H6Grg8QWR6bvyrzGXwjfbMb1HtzV'
    'q28Oa1Co8uYnHYgsMV006MLanBPG177HYy6jbSNuYsfrSpqsUZGzOPasX+wNVcgx28v1CtT08Ma+pPysM/3xiuj2'
    'dO1rnNLF1o68rOkTxBD3VqvReILcYyre9c1D4V1t+GliUe5/wrbtfAupvgyXUeD6A1z1MPQ6s3wuZYipK0Fc108Q'
    '2bo21thA43dK0NM1aIllmlBzgisi5+HbC18+5vSkaOhYohPU4A/Oum0/wXYzwwrPcStuDRghdroV+ZWOOORxz1rl'
    'nhaHI7MyxGcZhTxsKMaV1buurttc24by0YZWRfzq0Z4MZEq5+oqGDwho9pzJLLJj++4X+VV/EXhvQNU0aXT4pmtJ'
    '2w0U8chLxyLyrY6EeoPWvLnhadnaR9XSxeIaV4L7zxL4lLrWra9FFZ2U09tZxBVdFyrPJy2D3xwK4T/hHfE0qgx6'
    'XcnPcIa8h8Y/FT4leAfEV14c1fUkZ7N8J5kMeyWI/ckXhSVYf4Vj+GP2gvFehx29tb30ZtrfzCINm5SZGLncWZm4'
    'J4AIA6V7WFoYqFOMYcrXqz89zSpllfFVKleVSMm9VZWVtD0XV7+z8CeJ/Dd748kfRrR9RidJZlI3eUdzY+nf0Fer'
    'ag2q63r954l8O6PdPY3Tbrd1hYK6FQA44/jxuH1r5G+I/wAVrf4kLap4vjhvY7KTzYIygVEbjOACCdw4YE8ihP2m'
    '/FunRR2en6pLFBAqxxRDy9iIg2qqgjgAAADNViMDWqWlZXtZ66Bl+MwOFg6dOUnHm5k7K97W9D6btvGGt3r3Nrpt'
    'nPczWUhhuI4oyzxSDgq69jmtfQtS8bJrdnfXmiXrWqybZg0RA8puGOPbr+FfE9h8cNQtNUvdasr5LK91Ak3UsewG'
    'Ult5LA5Gd3PAroIv2hfFtyy21trdxcSudqRwojOxPGFwuSfpWayupB80IRX3nX/blF2VSrUflpY/UiO3Gf3cK/UC'
    'llhnUZ3CP8QK+evhvpviPQoW1/xfq91e6lfQKn2aSQmO1RiH2gcDf/eOPYV6LJrAnPGW+vNL6vJ/Ez3o46Djflt6'
    'ncLLbRNvuLlWx1GSf5UkmvabACIySfZf8a81uL8rk4PFY02qSnOxGP0FaxwcW+Y5quNpt3aPR7rxNDkskTE+rECs'
    'W48VXR4jRV+vNcBNqFwMgq2fQmsmXVnBIYMCK6oYO5x1s2ila9jt7rxHqMuR5pX/AHeK5O8u7icnzJGY+5JrGl1N'
    'xyVfHeqT6puViFYY6muiGHcehwTzGE9OYsTK561lTI1OlvWQBpPlDjIyQMj6ZrOe8V+c8VvGmznlXg9ipPG2CKzm'
    't2bPtyT2AraUh0aVztRRyT/IeprKuZvOOyMbU9D1Pua1Unsc0knqzMuHUr5cIIQ9T3b/AOtWaY/StVo8VGU4qjBm'
    'YYz6Um01olB1NWIdOeVDM5EUI6yP0J9AOpPsKewrX2MTyx6VfSwEa+ZfSC3Uc7TzI3+6nWrMlzHbLiwTDj/ls/Ln'
    '/dHRfr1+lYsrM5ZnJZj1J6k/Wt4UXJa6HLVrxholf8h8+oRW+V0+EJ/01lAeT8B91f1rAuXlnYyTuzse7HNaDLmq'
    'ki9jXbThGOyPPrVpS+JmYy1A68VfdMHmoGXit0cc2rmYwNVXWtRk9aqunOetbxMJPuZrjHQU1JXjbcrEH2q0y1Wd'
    'e9anNLRn/9f99BRzRmkNAzm/E/FrAT/z2WuiTOxfoK5rxUcWkH/XZa6SP7if7oqI/Ey38KJPrRSk4HFM7ZqyB3J6'
    'UcdDSDngUv6mgZXu8fZn+lfI2tEbb36yf1r63vP+Pd/pXyJrH3bz6yf1rzMx6HbgupufD4k6Hb59P61keOP+Q2+f'
    '+eUf8q2Ph8P+JHbe6/1rE8dH/ieSD/plH/KvOrL9xH5Ho4d/v38zxa6bHiW1/wB1v519HeH3zZr9BXzdd5/4SO1/'
    '3W/nX0T4db/Q1rzsL8bPQxPwI7GDn3q+O1Z0B45q6p44r01ueXLcnHFOJqIHHWlJ5p+YkySpYyeaqlqngOQaqO5M'
    'mWc4607OKizmlBPetEZEu6kzxTN1GTimgbHE5pvJpDxQD270xDjQGxTaaT2poXMael/8hC3/AOug/rT9Q/4/bj/r'
    'oah0r/kIW/P/AC0FSaif9NuP+uhrvwvws5a71RSzg8UbvSoiaN2K3sY3J93vS5qDOR70u6kO6JuO1OzjioMnFSKe'
    'OKAH5NLkUw0vFNagPzR+NMJoB9aoB+aM0lLxgZoFoKD2p3FM6cikye1NCH9aM03mjNVYQ7OBTaBzSUxXENJkdKGP'
    'pSAcdapIBccUtNNH41SJYZAoJ9KT6UFhQSIabnHNPpODTJ2EpKX+VFO4DRSY/KnUYouIOlKM0fWlGAadwEx2pR1o'
    '+tH60AFFAzmnfWgBvFLTqQ+1ACDrRS49KOc0XABzRilxmndqYhBnvR9aUAmnqMUIQ0IafjFLinYNCJbGdaMU/tjF'
    'GDTAjwKX2p1HNAhtJ9acRQeOKAGBe9JipCBTSKQrCYFGOaXBHpS8UDsN70uW9T+dLjnmjFAkIZJR0dvzNKJ7gdJX'
    '/wC+j/jRjPaniFgMthR70XK16DftVzj/AFjfjzSiedurA/VVP9Kd5cQ6tn6Co2KD7oP40XBvuyQSN/EsZ+qL/hT5'
    'ZEWCNvJhJLNnKDtiqu9umammGbeL/ef+lFxJpkBlibrbQf8AfH/16jYW55NrD+AI/rQcd6afand9wsuw3y7M9bZP'
    'wLD+tHk6f3t8Y9HNITmmcnrRzPuS1HsO8jTcZ8lxn0f/AOtSfZtNP/LOUf8AAh/hQeKaTT533FyrsONtp45Hmj8R'
    'UiyRxIY7ddgb7xJyzD0z6VVJpPrScm92NRitUifIxTDUfFMPsakfMiQgU3A6HFQZJ6mkJOeKLBzE2AfamEL3qMk5'
    '5qCSUKOeaLBzFg46VAxXBwR+dZss7nrwPQVWLgHgmrUDOVVGpvx3X86hkmLH7y/nWbwR3qJ156NVKC7kOoy4+Tzu'
    'X86rOrkfeH51SZgjclvpUTTLu4YhfpmtVEylULTGUdCPzqB/NP8AEM/WoGuIicBiPQ7artcBeQxJ+nFUjNyQSwSy'
    'DBcY+tZ8trg/eqR72VDnaCfpVWS9lYgtGOfQdatJnPKcSu9uf79Z82i2twxaU5Y96tz3LsQUQqtRCds/xD8qu5i5'
    'LsU4PC9ks6OpIIYEY+tJJ4X01ZHO0AliTx3rZS4hwCTID9B1qG5aTzDywPoBUO7epV4qOhiHwxphbLKPyFX7fw5p'
    'EXIRf0pwFwzcMx/Crf2W6b5uV7nrUSmla7Khs2kKdO08HJCt9QCa0IjDGoCkAD0AqnDaOSWJABOcsSKvQ28bAneD'
    'g445rkli4Xtc6IQm9bF1LoAYDfoKtpdc/f8A5VVihj6cE1p2dk9zKIoo97HsBmuZ4uF7I64U5lmCYt/Ef0rRT5yA'
    'Cc5GK27TwjcMoaZ1jB/hHJrci0fStKT7ReuNqckyNgce1ZSq3O2nSlbU+FkSCz8X/EXS9Nt90Emn3G+Rh+8WTzFL'
    '7f8AY3MRj0Fe1/BT4fjQPBsUwdZZdRc3DMnI2jIVfqO9cvJp0Z8d+ONRt4yLLVrWeG1lAwrSTBCoA6/eBzxXvXwi'
    '07WvD/h9rXVigifDQIOXXJbcT6AgjAr5ylTlHFRlbS8vl2PoZuMsO431tH/gmouhXGOImP4f41R1bwz9u0q8sL6M'
    'C2uIJI5txGAjKQx/Ac16NcajbxAvLIEA9TXG6r4l097W4gSJ7kPG6so4UqwwcnsMGvalVdtDzFRj1PhHQ9J0++8F'
    '6b4VjCxwJ4lk8yYAZcSIsatn2XNffEHhSKKNLeOQiOJRGoAGAqDAH5CvmHwn8Pr6+0+38O20iosOqPfmZF/1cLIF'
    '2szdWBAIr7KST7NGpeQLtH3mIycd+fWvFy5YiE5Sq+SPWxyozjGNPbVnO/8ACI2Q+aTc341KvhzTouPs4z/t/wD1'
    '6mvPFFjD8rSGUjso/rXJX/jU5P2aEfVzn+Ve/TnUkeJU9lDex1w0mxiIO2BPwB/lSE2MQ/eShR/srj+deOX/AIq1'
    'WX703lj0UAfrXI3OtSSsTNcM31au6nQk9zz6mPpw2R73d+IPDtqCsk2W7ZcfyWuZuvF/htEZCTIW/i4GPpXjLXdu'
    '3IKuT23D+tVLsxzAGBTu7gOvH612U8LHqePis4nZpJHqp8ZaLG+2GNfUbmJqd/iHsj/d+WoHTCj+dfOlyJUmLS21'
    'w2OAUdcVRZ4yRGYLzLHhSRn8OK6lgabWrPnln9Wk2oRS+X/APoSb4mzx5Vp22+gA/lVBPiVHs2LI5GTkdK8TttKt'
    '7gyMFvAE++rdBXV2vgi3v4/NjjZeOC8yAn6jNY1MPho6SZrSzjMKutOKf3/5Hcn4l2Gd5kJ7dRn+dalr470m5zzI'
    'x64AU/1ryx/AMcQ2xRLIw6hZlJHvxTYvD2qacqPb6XKVbq0kjYP0wMVjPCYZ/C/yOulnGZRf7yCt6M8Q/aOeT4gz'
    'jTbjT4EsbRgba+VT9rxxuUvxhSf4eRXyTD8MbAzCBbqdC3RizY/Sv0Z13Qr/AFe3Ed5ZCKMMC5M2FOOgO4VyUfga'
    'GO4Mwgj/AHYyDHIrjP0IrvoewhT5Uj5nM45jWxUqnO2n5W+Wx8J3Pww05p1tDeSyM3uw/mas6D8DNH1W4ZJp7yTd'
    'kRpABknPUsQQK998Z6KIr77RCWLq+3ayIgHPqvb8K7b4cm40/Ulhntbe5jK/fRw+0/8AAuMVri42ouVNa2PNyevW'
    'njY069R8t7M+Y779mnVNNt/tca3ciFtuFZWI4yMhR+Zr0j4W+CPGnw+uptU8N6a0s8oG6W8tRMU2/wDPN2A2e5B5'
    'r7JvPEstnYixtpoxh9/lwqjBRjkFuFH515P4j8cX6u1uGRSed0pWfH/AVO0fka5cvlia0eWcE/Xt6H0OcxwOFn7S'
    'nWkvS2/qexaYfEV1p1re6z4hs4ZJolklt1tMyxluq4BI49c1W1/4jQaDAiaXDDfzqOQylASB1dsjGfQCvmU67cSy'
    'MbjVnQOcnbCQo/BelaMN5ZSxrv8AEEZdeivAM4x3LYya9OOWRTvUd/K1v0PMqcSznFwoKz7uSb/F2PQ2+NXji7mx'
    'Ho+mQxs3zbA28jPI3luD74rTPj9Jo3fUNLETFMqsd1JIzN6cDA+przKGwviwnhuFlWQnlIUbPp0zWbcW11HkG6n3'
    'lsH5SOfeulYShf3Y2+887+1cdGN6k3L15f8AI9JvPHU9y3+i6bNEpQAIs24kKMZ6Zqh/wk0BEZ+xSq6tlgwLHOeh'
    'OeRXm5kuY2DNPcjtuG4fh1rUheQoQjynHXJOefxrdYeEVojleNrVJe8/wX6Ho0niqO6ne7uLZ0LfMyqm1cDsADwK'
    'p3fi+w8xzDbMqsBjnPbpXHR2sl4jkPIwUfMCW/I09NNOAVUFemTwPyrN0afU7YYjENadTafWBc/MVaPPIyRVm2uo'
    'n/eHLbT0XgZ9z/hVC1sI4cFUBP5c+1XhCBwV6+hrKTjsjuoqpe8y+9+0p+b8AOAPoKjM27oKg2Y6VKFNY2R288mK'
    'Bu60nltI4jjBZicBQMkn2FXrKyuL+YQW65PUsThVA6sxPAAradrewQwaed0h4e5I5b1EY/hX36mpe+hpFfab0MsW'
    'kFgN17iWftAD8qf9dGHf/ZH4mqF1PNdyeZO2ccKAMKo9FA4Aq26VVZK1glHXqY1JuWmyM2ROM1SZM1qSR56VXKdj'
    'WyZyTRkvHjpVVkJrXeOq7xitoyOWcTHdKrPHjmtZ17VVdPatlI55Q6GUyCqjpzWpIuKpuma2jIwlHozMdfaqzp+N'
    'abrkVWePvWqkc0lbc//Q/fPPak5xR6UHJoGct4rx9ihx/wA9lrpk+4v+6K5nxZj7FD/12WunjwY1P+yKzj8bLfwo'
    'cST1o49KUH2o5rQiwdBmjPtRnIxQBQBUvji1fI7V8h6w423mPWT+tfXOocWkn0r491hsR3n1k/ma8zMeh34LqdR8'
    'P/8AkB2p6/LWJ45Odccj/nlH/Ktb4eOToNr/ALv9axfHTf8AE7f/AK5R/wAq86t/AXyO+h/HfzPGrnH/AAkNt/ut'
    '/OvoLw+f9EX6V873Lf8AFRW3+6386+hfDufsin2rzsL8bPQxHwo7CA8Zq8GrPh96vLXpI82W5YyPypWOajHFNZue'
    'KokfnHAqzAeD9ao5q1b8hj71cSZWsW8+nNHPamdDSZwfrWhkTZpPrmmZxxQWpoQ/OKN/Y1GXz0FRk/jTBk270NNJ'
    'qHdS7/XrVIDV0g51G2HT94P5GpdSOL24/wCujfzqvpDZ1O2/66D+RqTUmxfXAP8Az0b+dd+G+FnHiPiRSYjtTKYz'
    'nOKQGtzC5KCelPzmoM8+lPzmk0O5JnFSKar9T9KlU7eRRbuVcnDUtRg96dmmK4/HrR0pvWkz+FAiTOOKN1MJo7cU'
    '0A/PHFKOajAqXI6U7CDPpRig0dOaaAPxoo+tJTEFJTu1HaqRLYzgdaDxzSn1pvHSqEHajt6UuPekwc80EvzCk5zT'
    'sUnamITmjApc0UCE9qB9KXHNOApoBuM02nkUmO1CAQZpwpvSnjFNDGA+tAPFKaQcUhDgMinDjimjnkUo5osAfSlB'
    'HagDnNO2inYAAzT1XHJop/NFhXDikwacR60lBIgHNSikHTpTsZ9qAExxSHnvS8A0HFMQw9KbT+lN60AJxSfWl+lG'
    'aAEpaKPpQAlL1pQKmSD5fMmPlp29W+goAhAzU3kOBl8D60hn2jbCNg9erfnVY7idxJz70rk8yJzvHEZVB655/Oof'
    'JkzyQfxpue1HGOaAch3ly9MfrTvLf0qEjPSpEhwvmOSFzgY6sR6UE3E2460Tki2i/wB5/wClTCdAMeUD9SSaU3Eb'
    'IqPApAJI5PfrSbKTXczMnvS44ya0PMtv+eA/76NNL2xHMJ/77/8ArU7j07lDryaaSTVxjbEf6th/wKm7bTukg/EU'
    'Eu3cpGmNV/ZZ/wDTT9KTy7PH35PyH+NAfMocAc1GzgVfMdmRjzHHvtrPuraSJfMRg8ZONw7H0I7U0Jsga4UcU4OG'
    '7cetZUxRc8jdTjexQRKCdzY5Ap6GfOru5os6IMscVB9pUj5P1rn5Lxpps/dXP5CrqygEAUkT7RPYsPLI2ck1TdmI'
    '4zS3FykaEmq8U6y/d/KtFJbEueth48zvmlO/3pt1eWWnwm41G4jt41GS0jBR+teW6n8ZPB9jepbQGa7j3YkniX5V'
    '9xnlvwrWKlLZGFbE0qX8SSR6hmQdM0w+YTzk1l6N4l0DxFEJdHvYrjPJUHDj2KnkVrXLrAvJ2k9M1Dlbc0UlJc0X'
    'dEZUk525qFgB1TFLFdLLxnDdx3FR3eoW9mgeboTjHep59Lg7dyN3K8BRUDl5D12j0xWjaXdhfFxC4JXrn+Y9qSVr'
    'ZORgggkEcjjrQqqJcOtzK+y7zy2PzNMFkC2S2cei5q016gTzQVEZ+76mod1ySzFgEbBTHUCp9u7kOEH0IHswRuU9'
    'PUAVB9jBbcpOT14FSyMUXJI/Guf1DxAmmttP7wlS3yc49M0OuluzKUYrc6H7C3fv7CpGs13Hf1znp1zXlNz4lvLy'
    'aKZiVMeDwcDg5Bx/OtO+8aX89uyqQhI5KDn8+1c88aoptoceV6I9Ei+xKWZZEJQ4bB6fXFc1N4xEZlkhCrFG205G'
    'W9P1ryITXi3SywuwEvLAE8+uaV55WeSJ+CSMY7+lebWx8muZLU1hLSx32peJJtQe3mSTbENw29OT3IrOttRvVBjM'
    '5xk9+1cxJY3kiiYfKB/fOBWZLDqpWSQOrQRLlijdW/uD1NeVWzB3TkjeFOT2PTLTWoomVzchiD0z3r6O0PWtAttD'
    'gnt5VZnQGTHLlz1yOuK+EbFy9m93IvkqH2kA5LN6Z7e9dUNTvleBoJ2j8uJVTaSOBz+PNc0M0UJ6R0PSw8XFXZ9c'
    'XPjO6kPlWEYQf3m5NZSWtxqs4udTdniVgXyclhn7qj3rxLRPHOpwtsu4FuVB+991sfhwa9m8P+IrHVZI4yGhb0Yc'
    'c+4rted4W1nKz8z0KGEqVNUro2tE8KWz38mqSxBU3kxR9Qvp+Va+s6wsKNbWRO7GN69j7V3aWMDacY/MCblyCCOl'
    'cpJFZWJ/cx+dL/eYfKD7Dv8AjWiU5TXLs9Tobios4UabfTxi7umYKx4MhwT9AetakenNdW505VMSTMu7jGQDnLMe'
    'oHYDitlrO4v5POuHJJ9fT0A7CtcXBjiWKb94I+FJ4YY9DXXVptQumc1Nrm1RNZabY6PZGDToxuVS3PV2x1Jrz7UL'
    'y4mkLTuzHPQnp+Fehxusyhw+3tz/AIiqt3o9tfKTLGGb+/GcGowdT2rd1sXioOKVmeS3EpyRWLcSE9K9Ju/BpPME'
    '5Hs6/wBRXN3XhTVY87EWUf7J5/KvXppI8OtCfY4ScNIckj8qyZreJuNua6q80rUIeJraRffaf6VgTW5GQwI+vFdk'
    'JHk1oO+qOffSPNOVUDPq4qrcaDCp3SkLgfwvk/kK1pbHuaqPYkg9K7IVGup5NbCwlvE582mkRn555Dz0G6klXQjk'
    'r9odh77T+BJzWx/Y4c5Y/oTVhdCRwAU3Z7kdq0liUt2ea8vbulFHELDZqTJGLpCT8u255P4Crd3bQ3dtGLe5u7Wc'
    'f3n3g+uTjmvQrPw5jiNAB6AVs/8ACNPgZQY91BriqY+HOnc1pZRU5GrbniieGLOBvOXULuOXqXWPJ578HrRJDq8U'
    'Yi0jVDKF+8k8jR/gFJr1S98NvI4JUArwMDH8sVhy+F7hyVPIPQMof+dddLGqWsmcdXKJQ92Ebejf+Z5W+m65LIft'
    'TuQx5CTK4/Vq6zTvDvnIC/2hiB90hAR+RrpH8M6fpyCe+EO8dECYc49gT/SsLVbl7lVWB5IlUYAPPA7e3610yrOp'
    'ZQdl6HBHL/YXlUTb7N3MLX9DihdUgsftrgFiheLjHZjg4rmbjUEtI0WSzf3htSqoo9CerH8KsatYX9zGEimZgDkj'
    'cQp9iBiqkHhqSZgZUaIj+42ea3jTV06kr/16kNNpqhDlb9P8jl7zVYr+VmnjuFXPEZAKqPQf/qqxANKk+6kg46bV'
    'FdOfDEkDEuQQee4P9RUzaEzt/orrLt6hgFPvgjiuxYiCSjHY8x5XXcnOerOYjXSPmSa1mc4zuDqBWXPp+h3CBUWd'
    'W/iDAMPoK72HQYJHxMki56Kdh5+pNatvpOmRlWhuDG8f3vkH5YxU/WUnpc3jlVSas7W+R5LFo1hA5jhS4J7FGEYB'
    '+tXhpcMSos8crtweXyPxavW2M0hKW9vA46AmPqPcmqaaI0g3TiJPZeaPrfc0WSro7/I4e306Fc5VYwf9tm/kea0n'
    '0uyjRZHJyemAf5ZrrBpFuoCpsGP9mnrp0QPB5qHiL63OuGXKOjictHZRkgqjHHTJx+grXjgk27TGUHsa3Et1Ucdq'
    'eUA5rGVa+h208Ko6mOtvj3+tSCDIrQwD2pu30rPnZ0Kmit5QFXLTTpLx2IIjijAMkjfdUf1J7Dqa19N0SW8JmnPk'
    '20QzLIR90egHdj2HetC6lSRUtrVPJtoj8idy3d3Pdj+nQVm6l9EbKmkuaX/DlKV0SAWdmpjgByf70jf3nP8AIdBW'
    'e8Zwc1pbBiozHVKaRjJN6syGjqEx4961HixzVV19K1jMzcDKkTn1qo0fetV0/OqroO/WrUuxhOJlsDnmqzx88CtN'
    '46rGPmtVI5pQMt4+vrVORD0rXkSqckeea2hI5pRMeRaqMnpWq8eKqumBx1rdSOeUTLZOarvHnoK0nSoGTPetVK5y'
    'yi1uf//R/fEe9BHc0tGM9aYzlvFvFlDj/nstdLFgxp/uiuW8XH/Qof8ArstWptWW1Ch+gArDmSk2zTlbirHR0D2r'
    'nYddtpDy2K1I76GTGGzmrVSL2FysvnPekz+tNDA8g8U7r1qyClqP/HnJ9K+OtZOY7we8n9a+xdSA+xS49K+NNZfE'
    'V4c95P5mvMzHod+C6nT/AA7/AOQDa5/u/wBaxfHhxrb/APXGP+VbHw5cHw/bH2/rWH4+IOuSH/pjH/6DXm1/4C+R'
    '30P47+Z4xcEf8JBbf7rfzr6I8On/AENcelfONww/4SG2B/ut/Ovorw4f9EXHpXn4X42ehiPhR2UNX1OKzYjxxV9S'
    'MV6SPNlqT5qNzzxShs0x+fwqiUANWrdvlNUQfWrMB4NVEiRc3ZNGe9RA4PNG4dq1MyXd3pd3HNQZo3evNUBLuNML'
    'Z4NM3jNNZu9AiXOfejK45qHcBSbxVCZs6M3/ABNLb08wfyp+qHN/c/8AXRv51X0Ug6pagf8APQfyNP1Un7fcj/pq'
    '1ehhPhZxYj4kUSaXd6VBuyeKcDW7MbkwPalBx0qLPan7qQyRTz61ICKgHX0qTI7GgLk4NODetQbwOKduGKAJs0mc'
    '9Kj/ABpwOBQMkBp61ED607NPcRJQOtMzjpSjFV5ASfWlzTPpT8nFMTDpxSUZpM0CuLmlz7UzmnDpTRIhptOzikqx'
    'Nhml69KaOKXNBNxeKXHel4HFITQIbSdelOxSUwFozTc+lGc0XAfmjpTaUEd+aYAaQYpc80n0o2AX6U3NBPamii4D'
    '81IoB/CmqBTx6UEtjunSlFIKcPypgAxTxzTeBRQIcT60tIKUUDsHIp3BptKRjpQIO+BS/Sm0daAFwccUnXg0pOOl'
    'NI70ABAB6UnFL05pKADtzTgD0oHXAFWztswCeZyOB2Qep96GwGFVtQDIA0h5C9l92/wqtJJJK2+Q5NRsxZsnJJ6m'
    'kwKLGblcUc9aTjsaUYxikzzzSEHWmnmndabxjPamJidBzVq5JDiMdI1Cj8sk/iaqnocVYu/9e34fyFDDWxWzmjnH'
    'FKaTPFSCGnjpRweaTPPWgnjFNId7BxTScdaGNRGmS2KzLUW/ORSHOaTj1pki4z1qWGRUbEg3I42uPVT/AIdqhyOt'
    'MZwVNFgvbU5jUInt7uWBuTGxGfUdj+IrMIJJzWrr86x6nKC3JCcf8AFYT6hCkgQgnjP4+lBzTfvMsLF3pt3cW9rE'
    'ZruZIlA+87BelW1BkRZF5BFYutaJp2uW5tdTgWdRnbngrnupHSmrX1Ik3yvlWp5/r3xK0GzXbbytdyLniIcfix4r'
    'zK9+K3iCXKaaqWKnjcBvf8zwK6TXvhNBbQTX+lXyrHCpdorkgAKOTh+n515NrGialogzqdu9uhOFdh8pOM4B6V20'
    'Y0G9NX5nzGOrY6N5TXKvL/MydW1jUdVmNxqVxJcOe8jFh+A6D8qxQk0wLIrOF6kAkCq1zqCB9sK5P95un5VTS7vk'
    'uIbqK5lieBi8YjbauSMHcvRuOOc8V3PmS9w8T2ycrzbNKK8nsZVntpHilU5DoxVhj3Fd1pfxi8UadKv2+QajEvGJ'
    'uHA9nH9a4SbUYL8/8TC0Ac/8trbCN9WjPyn8CKktfDNzqMgXRXF8Tz5S/LMoHdo25x7jiuecoPSqrfl9524edVO+'
    'Gnf03+7/AIc+hdF+KuiarOXMjWN04CiOXAX/AIC3Q128l0L9RKz+YNvDAgjp7V89aX8NJFmA1y5SBfKEpji+Zzlt'
    'pTJ4BHc813aXGjeELFotOR0ViBKZHaRseuOn5CvCxmKw1O/s5a/11Po8LLEOKddKz+/7j0KG7FhKhWQBj0Ge3v7V'
    'prqV3HblYfuvk59N3UCvnG58V3k05OQUDkqcc7c8CvRtA8ciNEsW3IjjII5JfHqe1ebSzKSnyzWjOunUg9Ezrp7u'
    'WFQ7EhR0z0rPOq3Q3SRSN8w29eMH0rC1fxab2J7X5xjltwAxj0IrHbXEv4Qt0G8xdoUqcDA4PT1Fem6q7oydaCla'
    '5tjxJeXRSzDMWRtpJ7+xqVIZbg+XcOkbtn7zDH6VzL30COEcyPAFIBx8wYg4YjuAa506vc2HlyKRcjJJGcDjghvQ'
    '1jUlzfDJBCpTWs9T0GaxhiypnQgf3cmscXdl9r+wySgY9ThSewJrmLe81i9tLi9EMrpCeDGm4bzztPoAOtYyaTrW'
    'oac15FasfNJPn84UA444/WuSre3xXNfaRvHkgekWWp6Tdam9pLKsXkHawDjaxHo3pS6j4k0jT0ufsUKtPEwRSemT'
    '/ET6V5TbaNqGnW8rXcJZ35UkEg+hzVSP7RcR3bXTFp5gMnGMlcHj0xivOxHvwaUi4V2vs2O2/wCEs1Rf9ZsmZJMs'
    'gAy645X2B6isfTY4bLTpFO43lw7ycsSIlOSFAzjOO9Ps7dYWT5CX8tcntuPrWtY6YksoCnDA7ju7n2rw6rUFytno'
    '0YubTL9uYptItrWFcdCfr3rYjtjOqhBwgAB962tA8C6xqCma1j2wR8M8h2IueeSa9JsNE0Hw8u+/kGoTDny0JEIP'
    'u3VvoPzrh95uyR7uHw90nI53w54bvdTf9zGdv8Ttwo9yTxXrtjaaF4bRZZJBeXCjovEYP16t+HFcDe+KpbgeUjLF'
    'Cv3Y0G1B+Arm7vW23AB8jGTz1ojl7nLVX/r+tz1o4mFKNkz1rVfHdxdElmCgAABeAAOgFcbL431CFz5Ny4x6nP8A'
    'PNeaXOrgpuLYLc1nL9qu9xhXfx1U8frXs4XBTptybd31OKvjudKKWiPX4PifrcLBWaOUE4+ZcH9K04Pi3ECY7y0V'
    'ucZjfH6GvnqW6kSQpnbg4ODk8cdqovIwO5WUZ/vHn8q9ilzreR5lTEpbI+sLf4u+HPLxLFPFg9cBh+hresviZ4Pu'
    'jgagkbHtJlD+tfE8t6EQjzhu9AM9ay5btyMIGY+p4FddOo1qkctTGn6K23inTLkD7NfwSjsBIp/mavf2ikhztjfP'
    'p/8AWr81DO+V6qx6Ecc/UVtWHiHW9OIMd1MgHpKwI/WuuFaL0loc7xzX2T9EzJby8MjLn0bj8jVOaw0yf/WIrf76'
    'A/yr400z4m+LLcA2+ovIB/DKA/8APn9a7Wx+M3iGLH2y1t7geo3Rn+orrUG1eLD6/SfxI+gpvCei3Of3UZ/3SVrN'
    'l+HulMcx+YnpghhXBaf8atJmIXULGaA+qEOP8a7zTvHvhfUwPIvkjY/wyfIf1xTtNFKWGqdii/w+RP8AVT8+jril'
    'TwNeqRtKOPY/4139tdCRQ8MgdD0KsCK24J8Y3AGuatUlbc1jgqL1SOCtPDMtrg3Me0etX5dNh2gBNuRwfXFd5cxp'
    'eWxjQ7GByOeCaotb3c0cUNwqqsXRh1PavkMxjivrF6TdrK1lo3fVPtoe7hKVCNLlkl533+R5jeaXCAWYZ9hXI30c'
    'keVjwg6fL1/PrXuN9pNjMp4KE91P9DXBar4YmIZrWRZP9luD/hX0+Gc1ufP43Cpr3EeKXkGWIYZz6isKTTrZ/vKR'
    '9K7nVbG5tH2XMTRntuHB+hrnJMAnNfQUqjsfNVaEb2aObn0a1lYNg4HbgZp/2GKKMLCmGHc8itlsHpUbKcYWteeT'
    '3ZzuhBbIxWh2nLYAI4AHf8ag8leSsaZPG4DmtlrYuck5phtCM1SnqQ6XkYX9l2W8StgNj61KIbaM5Clj71oG0YHp'
    'TRARxg1XO+5Hs10RT2KSeAB7cVE0K9RV9ouajMftQpicGZzRGm+VjnFX/LxyKjZD1q+ch0yiVwPSmCMscDmta002'
    '6v3K26cL95zwq/U12NlpNtYAOo82YdZGHT/dH9aznWjH1NaeGctehyFtoN1MBJN+6Q926n6Ct210e2iGVA+UZaR+'
    'cD1/wFdFFbvcS7RyTySewHUk+gqpfFHxbw/6tTknu7f3j7elczrSk7HUqEIq9jHvbj7Si20AKW0Zyqdye7t6sf06'
    'Cs7yMdq3UtWc4VST7VXnNlbZ+1XEcZH8Oct+Qq41UlYwnSbfMzIMWO1MMWOlLca5pEOfLWacj0AUf+PVjzeJkwfK'
    'swPdpCf5D+taKqc03BfaL0kZ6Yqk8fJ/nWbJ4nmI4toh+LVD/wAJNx89mjf7rsP5irVUwcqb6l14waqMnWkGv6a/'
    '+tgmiz/dIcf0NPF5p0/+puUB/uv8p/Wto1UZuMXs7lRo/SoGjrUaF8b8fKe45FV2XFbqfYwnTsZLx5zVKRMdq2JF'
    '61SkXI5reL6nNViY0ifjVR1FazrtNUb6Wz0uIT6ixBbmOBP9bIOx5+6v+0fwreMuhxThe/YprbNIGfhUQZZ2O1VH'
    'qSeK5zUPElrZKYdKjWeU9biUfIv/AFzTv/vN+ArO1XV7vVCFkxFAp+SFPuL/APFH3Nc5MvFdUKXWZ51fEWVqf3/5'
    'H//S/fH3pc9xSEZ5o5oGcp4uANlAP+m6VLqWniW3BA6qKi8W/wDHnb4/57rXS7BJCqn+6P5VjyqUpJmt7RVjxuSO'
    'SCQoTgirEV7cQ42txW/rumkMZUHSuVGehrgmnF2OhWaOutNf2KBIa7Gxu1u4wyGvI8YGK7jwxM3kkE8A10Yeq78r'
    'MqkVa50erNssZc+lfF2tv+6vfrL/ADNfYOsXiNbtCDksa+OdeYeVegesn8zXPmDu0dGC63Op+Gzf8U/bZ9P61keP'
    'GH9uSf8AXKP/ANBq58OHxoNsPb+tZXjts65J/wBco/8A0GuCt/BXyO6h/HfzPFbyTHiO2HThv519H+G2/wBDT6V8'
    '1XYz4itm9m/nX0h4ZINmn0rzsP8AGz0K/wAKO2gOVq6rYqhD93irQNelE82W5ZDc0M1Qg0ZI96szHFhmrFuQQfrV'
    'HOTirELcH61UdxS2LpOelITUeaTcK0IH59KQnvTc9qbmmIXdRmmZppPencB5ak3VFmk3fjTQG3obY1e0z/z0H8jV'
    'jVv+QhdH/pq386p6Ec6vaf8AXUfyNWNWP/Exuv8Arq3869LCfCzgxXxIzifSgGo880bq6DnJwadnNQBqeCD3oaC5'
    'YBNPB/GoA3FP3HtUFJk2aXIFR59KUH1oGPB4p4NRr7U8GgCQHPNScmouhpQ3NAEv1pwpo5HNOFVfuIUe1PyR1pnN'
    'OB45qhMTrzRntTqaRjmmhbgOCacPWk60tADSeppo9SaD+lJQQwJpwNJilqiR2aXg036Uvt0pgFJ707gHFNpgIaSn'
    'U3igAzS5ox3FJTAKTNGKPpR6gKKcq9zSYAp4oJbHcUClA9aOQaLEijilopRimUGeKdSY70oxQIUHmnj1pgHPNL0o'
    'sA737Uv1pKWmA3Hek6Cl6UtIY0Cl57UfhQTnrQIbilxg0Y5zV2JEij+1TDIH3F/vMP6Ci4BxaRiZ8ec4+RT/AAj+'
    '8f6VmkkkljknkmnyyPK5kk5LH/OKjFBEpXF70fjR+NFJ9yQoPPSkNNz6UAKT2puc0hNNzTESZ+U1Pd/8fD59v5Cq'
    'ueKs3mftDj6fyFDC+hV5HNL1AqMkmnFuBRYVwz2oB3HAHNKsbSNhPx9B7mpjMkC4gOX7v/8AEj+tAvNiPFFH8s7E'
    'Oey87fdv8KqzRPCQG5BGVI6EeoNMY5ySc5p8dxsXypRviPbuD6qe1AOS6lYkd6jLVYuIAgEsbb4m6MP5H0NUy4HF'
    'MmTtoO3GmMGPSoy/HFMaQrzQQcd4suobbWZwTmQbOB/uCuVvNRgeESjCuh+b6Va8dXDf29cxqMEhCW/7ZivOH1AP'
    'G0Ei7s9W/oPasHUtozirVLSaR6JoniFrhzbAbkGTnuPwqzdavIZfLUFATgZHWvJrWSWwuo7hdwwdykcVp634pWeM'
    'PKyxBecDuR61jKvyQ1MlX01ZP45vLh/DV1aRtte4McW0Hkh5FB/CvMvjdJLqHhu2tIJzGwvQ25DggojY6fWqms+K'
    'hcRBYAzN58JYHv8AvByKxfGM17rmnwR2KqTE7SEZxuJGOK5MNmf+1xjU0Wn6mOYx5sBzw1cm193KeAi/1zSHC3qL'
    'ew/3x8rj8uP0q63jbQIrZ55i8bp/yyK/OT7Y4qxd/aoHMN1G0bDqGGK5K90u1uZxK0YJH5H619hGXu3iz4e2tpjm'
    '8cX+qOYtLt/s0f8Az0kGW/wFepfCi4/s/WNS1O9leWSOxyHYklS00anb6ZBxxXlcVkUYJEhLHoFGf5V6r4Qt59IN'
    'zcahGI0u7YwqrH5sh1cNj0yteXm9ZQwtSLlZtOx6GXp+3hOC0TPWjrz3wuNhLOicn+4vmAE/yzWJc6tbWQL3W+UO'
    'p2ofXGMknt9K4rS3ux4ubWLZj9gt7J0kAPG+V+hXv6/QVq+Kb2DVwJMqskUf7tYdoHQcYHTHUmvgbqU1GTve1/LT'
    'Y+tqNqhTa03t5+8zEm1hftCyQjkcD0zXUaXrNxbgG6YLMpGzKgkj39K8gM8hl8vd34rrtG10WmGCCYR8/vB8zY6k'
    'E10Y3DNw91HBRr8r1Z9NafZHU4k36f5rsm5XyqKwxk9T1/Cq813o+mTeTe2C4T5W2yqSpzjsOvtXlen+M7j/AISK'
    'zvLEMg3IBHk4zjDcdOR1o8T6ndzCKF33ZcyKw6EqSQrY/MGsaGLrrkpSim+56Tq0nBzW68ke5wWmnXFgmowWGYpV'
    '3L+9AJHTkY61nNFpVjZl7zSpHfe7RxoQ4IboS3AH0rJ0XWtX0/QraKSQ7BEMDqQDyK0NH8eX9lcXTXUaTWp2hFfg'
    'pt4Y5x39K0pZzTbcZQtY9BUKdlrbTsjmbK4vrMyraaaLaJ3aQbHZmJZSoVgeMc1v2moXI0Q6M9u8YaMozpkHBbcc'
    'dOvSvaNHv9B8S6fFKfLinkUl4gVJXBx3HerT+FdKmfZGNzHsB/hXQ1Xn+8ozVjphg3ypKWh4Vr+p32rW39mxQ7YC'
    'sa79uHBXqPb61sxzwvFawtYx/uo1jkHkoTKw43E4yM16ZL4Q8PWj5u7jy2B5SMbm+nXj8auR3GmadA8OjokbOf8A'
    'XSqHlH+63RR9BmuKVHGSklJq33nRTocrd2cz4Z0PT7VGn8TWcCwsWaJ5PkYqegCD5jjp0p0t34XsJmfSrCNnByrz'
    'DcF/3U/xqtf2slyzSvP5jHlixJJ/E1hSaU5y6kY+tRTymKnzdTqeK5Y8qSL97q8967TvKcnqOg46YAwB+ArKuZ7i'
    'WRgXyOBgn2qWLRpWkQNjlhn6VI2lTFmk45JP516lPAW1OSWLk2Yrw3HXACn3qjNBO7t8vsMHt2rdfS5h3FZ1xFcW'
    '6ssLKZDxnH3fp711Rw7WiMJ4l9THurIRhY5SA7D5QT/P0FZE0eqJlEYFSOinA/Krj2F27FpG3E8kk1GbCcHOeR71'
    'v9UfVnNLFS2Rztwt+oYOh/D/AOtWYxZVAcMp4zgV17QXYyNvHuapTWlw/VRx7VtGm47o5pVXLc5vYW4jRjnu3FTr'
    'ZSk7hKFH+1/nFaX2S56EY/CplsJSeVyavkuRzmUtgmQ0k+T7VN9ktujMzfhn+dbEemzEgEYrQj0t+n9KtUmTKfkc'
    '8kSgDy8jFXod54O5ga3k0c9Tk/WtKHSht6VpClZ3Ri02YEcBY8ggVu2cTIcdq04dLOQAMn0ArqdO8Jate4Nvavj+'
    '8w2j8zXXGXcUacm7JDdE1XUtNcPZTvHjsDlT9R0r6J8J69JrWmme4TbNE2xyPutxnI/rXnukfDp1w+pzgDvHHyf+'
    '+v8A61eo2dra6dbpa2iCONOgHc+pPc1jUtI9rA06sNZbHQx3OKtx3ZyB1zxj61ixxySfN91fVuBU32mO35iO+QdG'
    '7D6CuR0Fc9RVdC1dSBZXTOdpxWTI2c+9RvOW56k96gLk1rGnYynMhurWC7jaC5QSI3Zh/L0rwTxXph0PUjBEd0Mq'
    '+ZHnqB0IP0Ne16pq9lpUJmvZQnBwv8TewFfP2v65Lr2qyXLrsjVQsaeij1Pqetd+HjK/keNmU4cqX2irFKj9eD71'
    'b8sEVjDk1ajnkj6c+xrqaPGUu5c2YppWhLlHwG+U1PtB5HSouWlchK8ComQHqKt7DSFcjmjmFyme0QNQNF6VpmOr'
    'Vro9zd/OMRxd3bp+A70+dLVh7JvRI57yCxAA3E+lb9n4fzibUCVXqI14Y/U9v510trY2tioaEbpMcyMOf+AjtUrD'
    'JrnqYi+kTop4ZLWRR8tUURxKI416IowBSJDJK4RBuYnAA6kmrgiZyFQEsegFQXmrWehCSID7TeshXarYSHPXcwzl'
    'scYHT1rn5zZwW8noE4EatbxMAg/10ucKSOwP90fqa5W81uzttyWy/aHH8R4T/E1kahqF5qLj7Q/yD7sajai/RR/M'
    '81mMmavmOGtV/lQt5quo3YKSylUP8CfIv6dfxrGdK0inY1A8VXGRwTUpatmQ45xVZ0PNarx596rNF1rRSOaUDJaL'
    'PWqzxVrNFUDp2NaqRk4GO0Yqo6DHqa2XizVSSPjmtFIxcCjDc3NscwSvH7A8fl0rXi16T7t5Esn+2nyt+I6H9Kyn'
    'QCqz5raMjFuUep1QvLK4UmGTDf3G4b/69QMylsDk+lcuIJZ5VihUs7nAAqW71Q6ShtLKXz7jo8/VYvVYj3I/v/kO'
    '9dVGcpO1jOdTS8tEX9V1aDSMxR7Zr3HQ8pCf9ofxN/s9B39K80u5Zrud7i5dpZXOWdjkk+9XSFcE5wff/GoWhI5r'
    '0oWj6nl1qjnp07Gc0ZxVOWH5TW0Y6gkjyDXQpnDOFz//0/3vp3BFGaBQM5XxZj7Hb+0610ycIv0H8q5nxbj7HBj/'
    'AJ7rXTpnYuB2FZx+Nlv4UVLu3WdCCM15/qOkyROXjHHWvTfrUEtukoORU1aSmEJ8p444ZeCCPrVy01J7KJlXvXd3'
    'Oiwy84rj9ZsFtCrJ071xzpShqdCmpaEVncy3l1+9P8LH8q+cNaX5L056mT+Zr6F0vP2okf3Gr541nO29/wB6T+Zr'
    'jxGsVc6qFrs6D4efLoluD2FY3jls65J/1yj/APQa0/AL40a39x/Wsfxuc63J/wBco/8A0Guet/BR00F+/Z4vdt/x'
    'UNv9G/nX0h4Y/wCPNPpXzTeH/iorf6NX0n4YObJMegrgw3xs78R8CO4iOBVoHHNUo+RVpfQ16CPOkTg0jHFNBFNL'
    'c1rczAk54qzByDn1qkxx9KngbKn604biexbpMk0wnPWgmtbkDs0hbmoyabmkBIWppPNNpO9UgHGkzim57UhPFWhG'
    '3oP/ACGbPH/PUfyNWtXGNSu/+urfzql4eP8AxOrP/rqP5GresN/xMbr/AK6tXo4T4WefitJIyCaAaYaaD6V0mBOD'
    'SjrUWacuaTAsCng1CB3qUHFSMmBxTh1yKiFPHHJpDQ+n/Sow1KDg0DJx704VGM1IDxQgJFPan+4qMEU5aoCQc8Ht'
    'QM9aQUvvR6CHdadmozRk4qhWHtTc+lJ+tGe1AmLSHr60tJzTRIDNFGOKKokKXNJSHOMimIdR14ptLTAWkNL2ppP6'
    'UgE5H0pCPenZzQOPY0xCHinrjrSAGjNMH5DjS4PGKbj1qQe1IkWlHrRS4NUAUo60nSlxzQA7tTcYpc07b60wWgmf'
    'wpwpo9qco4yaTHa47FFKBmigSD60n60tJQAje1JnNO/CpYIHnk2Lx3JPQD1NLoAtvAHzNKdsMfLH19h71DPO077y'
    'NqgYUdgB0FT3cyPi3h4hj6f7R7saonGKfmD7DSaKMetJTMmxc84puaDTM0mA+kJwKZmm5pJCHEk0lJQTxTRLY4HF'
    'T3rYupPqP5Cqoqe+IN1Jj1H8hQ2HQrk4NWYITcEDcFUZJJOOKo5pT9wfjSEn3LNxIVJt0XYFPI7n6mqRYjrU922L'
    'mTtz/QVVLg0IUtxxfAqsz5q6tnNKgdQBu+6CcFvpWY+UYq3ykcEGnciSaV2Wobl4DlcMp+8p6MPf/GrF3Y7ITcp8'
    'qcEqxG4bun1FYkkoCt9DVnUpT9rcdBtT/wBAFFtSedcupAXC9OaiaQ456VFvpjEEHPFOzIcjyzx/ewweKL1GJJAi'
    'AHb/AFS15k915LO7Ebclvz7V6d490R7rxLdXI3FXER4/65LXnMvhq8nDZDgZ6Y7VxzqJaW/A8+tGbqSdurOTv9el'
    'Eb8kH+Ba4a41C7kkIl3Oz9B65r03VPDLPEFggl85EAycbSwPJP4VzV14S1O6aJ3MkXkRgKFA+8DkkH61yydzhqQq'
    'SepxjzvZFWkfYcgkFckgHIGD0INTnxHZwWYWBQrIMLu5/wA5NXZPh94n1K7M9xIh3cFmbJx24pW+H2v2NhKgiilm'
    'kYYYkcKB0GfU9a5JYRTd5IfPW5ORX5VeyOQ1fxHbvpxuLqIOGYAsQOnTj6msO3tNGu7RNUAZUJ2mNTgbs9PatfUv'
    'hx4t1LA8uFE3FthkAVfoK0o/Al3ZaMmm+fbiQyb5MvwB6CrSdBL2dSzb6Poc06TnrOF/VHPvr2l6datHZQKk2eGT'
    'kldvcnuDWTHrMmqlDqDESRnYzIMFkJHQetbS+Bgl0n2rUbZIcjftJJK9x9a2vDFloMb3cmoQlpIVlEEAQsjMThCW'
    '7gDmuPEKm3zJuUvvZtTp1tIySijR0rwpK9tLcQ6gsEF1ECwZCzGJTuDHHSpNR8AwWWnnVRqiPEykHYuG80lQFIPY'
    'gk59q3bK/v8A7NNaaFpc0kcieUTIp+UEEHbntz0rDvND8VzrBay23liVwEVnA5Azz7cVw0Y1oyvOSir+V7HZPllF'
    'JQcretkQyeAdJsPEGlafdXxngvBcB2jwMGNSY9p9Ca3NO8J+H4WFxk3drHCiMQ4G+did3PYKOCKzH8EeJ5pYpJRG'
    'giJwRLyAeuK0LbwFrCxeSkiKuc7fM4z64p1pt2Srfd6m1KKTb+r/AH+h3Ym0WIro0McMM0EQZSqhn8s+j+vrVKw0'
    'vwhdahJYS586BElYO5A2uTtIptn4DvY5xeMiPKqbQWkzxitiDwNqslx5kOnpLK+FLK+WwOgJ9K8yWHlF3pyf/BPT'
    'hU51adNafkdcml6bNGkMVyqADagBB49KxbnwRPPfmytDPctcBXUKMqM8HJ6DB9a6jS/B1pYAPrGGkXnyIjkD/ef/'
    'AArvxqxihFtaKIYgu3Ygxx6E9T+dXh8prP3pO3y1O/8AdSXvRscro/w+0zQXWfXrtnkHK21s/OR/fkHH4CusvfEE'
    '3lLb2SC2iQYCoPmI/wBpuprKeQO2WBzUIOTweK9/C4V042jEbqQirRZmzPM7mRieTk//AF6jXzWPWttYGb0qZLNs'
    '8AV6NOg39k5qlZ9zGWCRzxWjbabJJjA4robTTd5wRXY2Gkj5QVruhRUUc7k2cha6K5Ibb0z/ACps+jsoC7cYr0/f'
    'bW2EjjDEcc1G8MN0p2LtYdQRXQ6DSvY5IYynKp7NS1PFruwZQVQc+tctPpjgkmvd7nQZpPuRMfoKxn8IalKTthP4'
    '8Vnyo6vYyex4jJYH+7VY2LKPu17mfAd+33/LT8aE+He/ma5Cj/ZGaaSF9XqdEeDG0Y8FaBp2RnFfREPw70hP9dLK'
    '/wCQFbNv4J0CLpbeZ/vEmnoUsHUe58vjTFzjbn6VaTRZmP7qB2+ik/0r6vh8P6ZAAYbONffaP61dFmkXRY48fQUX'
    'RosA+rPli28Jazc4EdlLz3K4H610tp8N9cl++iRD/ab/AAr6F2R/xSflzSg2qf32P5UcxawEFuzxy1+GBGPtd2B6'
    'hF/xrpbT4faFAQZBJMR/ePH5Cu9aaIfdiH4nNN+0yD7uB9BS5maxwtJdCja6FptoALa0jQ9AdoJ/M1pi3wPmKqP8'
    '+lV3nxzK+P8AeOP51l3Wv6LZ/wDHzewofTeCf0o1Nlyx8jbP2dOrFsdhxR9pC8RoF9zya4C5+IXheIlUnaUj+4v9'
    'azZviNp64MEDOvclhn8qT93Vke2h0kj015WfqxNUbieOAZldUA7sQP515HfeOzdAra3Yts/7BB/OuUmln1Btz3yz'
    'k9ncj+dXDkejZz1cS18EbnsV74u0azyPO85x/DHz+vSuM1Lx7fzgx2EYt16bjy9cgNLvEXcsZdfVMMP0qtLG0eQ4'
    'Kn3BH866FGHTU8+riazXYr3t1cXUhluZGkc9SxzWbGhMr59BWgV3dKakR3tkelbqeh50otu7IlQDtTitSleaULni'
    'k6guUrbSeKuW29WxnipI7aWU/u0Zj04Ga2LTQ7tpAZsRKfXk/kKznVS3ZrToyb0RWVSavW+n3Fx/q147seB+ddLB'
    'ptpAAwXzXHdug+gq4wJ69B26CuaeKXQ7YYXrIx7bTLa3O5wJnHr90fQd6tsC3B/D0q5spPKJ4A5rmlWvudMaVtEj'
    'P2GlSCSV9qDJ/LHufQVfaFI1MtxIsSIMknrj6Vy2paq1yptrMGKA/eP8cn+8fT2qHVCcFFXkN1bVkgRrLTWy/SWc'
    'f+gx+3qe9cU6ZyTzmtRkPSq7RGqjURw1byZltHURjrSdDULJxitYzOSUDMKmozHmtIx1GYsVopHPKmZDRHNQPH1y'
    'K2GT1qo8fXFWpGLpmO8ftVd461HQ1UdCTWqkZSpmZIhzxVOSMmthk9qqSJitoyOeUTFePOagW2lmkWGFSzscAD/P'
    '61sCBpXCKCzMcADqTVTU7xLGF9PsWDTSDbcTL2H/ADyQ+n94jr0ropxcnZHNOKSvLYxdQvY7ONtPsW3SHiede+Os'
    'cZ/ujue/0rmTHir/AJWDgCmsnrXr04xirI82reb1Mt4uOKjCsp9K0Xjx2quy1pc5ZUyv5h6MAffpVeQrnuPwqZ1z'
    'VViVrRX6HPKHkf/U/fGk4+tLkY6UDOKCmcp4sGLOD/r4SuojPyj6D+Vcx4sH+h2//XwldQgAUc9hWcfikXL4UKaD'
    'yKOnSgDmtCBrDg1yWuWT3CkCuwxgVG0aOMMKicOZWHGVtTya1t5befLjgAj86+d9bXKXvH8Un8zX2Xe2ERhdgADX'
    'x74gTCXw9Gk/ma8jGU3GyPQw0r3ZL4EONGt/Yf1rJ8bf8hlz/wBMo/8A0GtXwMM6Nb/Q/wA6x/GeTrMn/XKP+VcV'
    'b+Cjsofxn8zxa8/5GK2+jfzr6U8LH/Q0HtXzXdjHiG3+jfzr6R8L/wDHkn0rgw/xs76/wHcRdPSrSnGM1RjNWgwr'
    '0UefImz1qMsKTPPNMJxV2uZgx5xVi3+6R71Uz61YgJ2n61cRS7FvNGQelMzxxRnPFaENWHZ9KbnFNJxTM5pokmJp'
    'hPFJnik+tUAueOlIDkUU3PFO4G34f/5DVn/11H8jU2tHGp3f/XVv51X8O861Z/8AXUfyNS62cand/wDXVv516ODf'
    'uM4MX8SM0MO9Jmogc9+tPFdRzDwc1IDUPQ0/NICyDnvTwT3qqrGpQcVJSLI5pQfWogc80/PNIofnHFPBwKjBz1p1'
    'AEqk1KDVcYzUme9AicHHNPB71ADmpATTGS5PSng1CeKUGhCJc0Hp600U7PYVaYAKXigHtRjvQSxeMcUZpvel5pol'
    'gelGeMikyKQntVEjhS49f0pox2pwpiDFIeKcc0jUCuNzSYzS80HmmDG45pwyD7Ume3WmkkUIm5JnNA9TUYz2p4p2'
    'ESUopO1FAx1P7c1HThxTuA6lzxmm5pRmgQ/jrSjkU3NO/Si4B04qRRkVGCaeM0myrj+BSYzRn1ooEGKMYpRnpQOe'
    'Bkn0pg11BI2kcRxjLMcAVauJBbRmzhOT/wAtWHc/3R7CrDY0+HaP+PmQcn+4vp9TWMTk0txvQQmmdaG5OKbz0pmT'
    'Y7P4YqMnJ+lPI71ESDQIDyabnn3o9aTFLcQvTk03dikPApM+tMLj6aeKbk5o7UEC9+KnvT/pUn1H8qrbuaffyYup'
    'B7j+VAP4SBmzTTIip8x45qlJcbenJqnLI0ijd054p2MZVEjY1GUC8lC84I/kKzY5czxq3RnUH8SBU+pxXAvJWVGK'
    'kgggf7IrJggvDdQ5jbHmJ2P94UKOhM5PmtYsXl3K9zIzMflYgc9ADgAUk908iQySHczIQW7naxAJ98VUmU+dJn++'
    '38zT5YZGggMaMw2vkgE/xVVkYc7vIjeQ7GPbBq5q1wFvXAHO2P8A9AFZUkc6q26NxgHsfSrOuSqNRlHQgRj/AMcF'
    'VbUTqNRfy/UptcOT6e1RecQCTVXzKjdtykmrUTllVZyPjfUJU8Q3Cp0CQ/8Aopa4saxPEcj/AOtXV+NXA8QXC/7E'
    'Pv8A8slriX2kdBXRGHuo4a1aSqS16sZeairOZE3IGGWyeAfw7VFGLu4XfbzI6nuDVSfyE5LBSR2/wrlZryXTLoXN'
    'kdo/5aIchX/DtXFVwqWttCPrGup6NFp2onlZwv40kujajIQHuhj6k1h2fjLT7iBsZinVSQj8ZI9DWjpOvNdqsdyN'
    'j7RhuzetZfU6Unu/vNo14vQkPhSKU7ru9k2/3V4FXU0Tw9bxCIWscjdd0hyT9avm4AHao8Qy4OQDTjldOPwq/qbq'
    'rGOyMO7sNJijLRWlvuPAxHn8TTbSC3jgkKrHuO3G2NVxzXQfZIiuAQfwposMhkQA554X09a1p4CnH7KIniJX1M/E'
    'ewAyFD/dU/4VXe3jk+9Ju9yAf1rUaxdhnA/KoPsEp4Kg/hQ8uoPVxRSxM7aMqLCRwrqfrirEVpducQYdvQLk1tWn'
    'hGe4Vbm4Igiz9WYf7K/1rs7O3SyiNrpsJRTwz/ekb6nt+FZTy+h0ib0qtR/EYtjoslsA2sS+XxnyY8GQj3PQVtya'
    'gqxC3s4/IiHGE6n/AHm6mr8Ph/VLj/V27nPOSMfzrctfBOpOQZgkY9zk/kKmOEow6HbB1XpFHAM5J5BNOVmI9K9Y'
    'h8C23BnmJ9lFbEHhHRYesJkI/vGh0qXY3jQrdTxpIHkxwa0oNKuJfuRO2fQGvbINMsIMCK3jX6LzWiluSMImB7DF'
    'LliuhusLJ7yPILfw1qEi/wCpKj34rctfCVyceYyr+tej/ZSoG9lX6mpUjgXq+foKrm7GiwsVuc1Y+F4o/wDWSk/Q'
    'V1cOj2cMLH5iQpxn1xUqPCPugn6mriSgjHSs22axpU7WPN7C8htL1JbpdwB5BH6811Fq8eo6wLi1j2wquGOODWpc'
    '6Ppt6Q1xHuOc56fyq0q29lH5cChFHYVtOupbbni4TK6tKXLOS5E7+ZLOgX5VKisiYR5O5/yFRXmp2seTLMi8d2Fc'
    'jeeKtItifMnDf7ozWUYSPalWgt2dI3knqWP6VEWiHITP1Ned3fxE0aD/AFccsh/KuSvfixLhxZWqLt7u2TVchnLF'
    '011Pa2uMHhVH4VC13KeN2PpxXzHqPxN1y4iaVbkQqOuxelcff+M9Zba9xqciq23kvgEMcDioqThTV5MweYRekU2f'
    'YE1/BEM3FwqD/acD+tYlz4q8OW2TLqEWR2U7j+lfJ76sZl8yScygjOSxPUfWufl8S6XFM0HnDfnpnPOcEfXms62L'
    'oUlec7ELF1JfDA+qrv4n+GLY4ieWYj+6mB+tc7c/F+3BIs7Fn9C7Y/lXzmus2pkVMlvNJVSOfmGcg46dKzRrs6St'
    'HNEEZWx36VzSzXDxSktSXPES8j6Dl+LWtTAiC3hi564LGsK78e+K7rObwxj0jAWvJ4/EVuNy7WDhiMZzz3ok8TQ8'
    'PjdEflJHO1unPtWTznDrqTyV5bs7WfV9Wuj/AKTeTSZ9XNUwGduWJY+vNYKa3YsSJCUIAxjn8K17C/sblgsUo3f3'
    'Twa0jmEprmhsZOi/tF8RHHB5prxtjqfwq8qk8H5snjFWv7IvZZDCYWRuyv8AKSPYd6UsfTXxzS+ZcMHUn8EGznXE'
    'vA3E0+PzFOdxrt7HwVe3Q3PIFx1VVLGt5fBMVrEZblgEUZZ5SEUAdc+lZSzShspX9Drp5Lipa8tvU88t7u9TAhd1'
    'P+yxFaceqa2pw0pcf7YDfzFc3qHjvwiutw6Fptws0jSeWZEXEXHUq5+8Qe1d1HZbutV9ZulJImeFnCXI2Mg1Odj+'
    '+t4H9flx/Ktq2u7NgTJYxHOOjMKy5YrS0jaWeVUCHB9c+mPWuYk8a6NBcm3hzIflwW46/ez9PSsJZtTi3Fz1RrHB'
    'zspNafI9BEmmk82K/wDfbVetpdHRudPUeh3Fv0Ncda+KvD1xdJZw3CmV3WMjphm5AP8AWuvs2tLtDJaypKqkqSpy'
    'MjqK1jmKnpGQ1hUteVHQieCVVVJliUDATZsx+VPEUa8iSM++6slYsVL5eR0qfbs1dNM1wkYPMifnSM9uo+/n6DNZ'
    'gi9BT9uBT9sL2aXQne8iU/Ihb6nH8qqyXs7AkMI0HXaMU1wqjc3AHU1lTyGU7eijoKOdvcmXuop3k7zsQCdvvzn3'
    'NZxHODWgyc1CVqlJHHON3dlNkqBo60CoqNl9q0UjCVMy2jqs0fNarJmoClaRlYwcDNMZFMKetaRjyOlROntWsZMy'
    'cDNZAOKqugrUdM1nTyRxH5zz6VtGb2OecEldlCWOs6Xap5NTT3TPwvArJkckkmuuEH1OCpWj0JHdE6mqTzB2CICS'
    'eAByST0AqNnBOCvWr0zDSY8J/wAfzjg/88FP/s5H5D3ropwbfKjklJvbYp39x/Z0Ztoj/pcgxKwP+pU9UB/vH+I9'
    'ulcky56VoPGSctkknqTUDR16tNKCsjjqty3WhQKAGo2jzV8x8YIqMxkVrzHNKn1Mt0NU2XtWxJGKpunNXGZhKBkO'
    'nNVJE9q2HjzVWSIVakYyif/V/e+l3ZGKZyKrTyGNc0noUjB8WN/olt/18JXULyq59BivO/EWoCaGGM9VmU/rXWy6'
    'pDDEpJ/hFYRqLmkzWUXypGxkClHsa4efxKqt8pqa08RJK4Vj1prERbsHsnY7Q8c0A561BDOsyhhUpOK3uZWIboZg'
    'YdK+LfEecahgfxy/zNfaFycwsBXxl4iOF1D13y/zNeVmPQ7sGnqa/wAMLT7bpUUXcRk/rXKePIWg1+aJuCI4/wCV'
    'ehfBQCS2iB/55H+dct8W4xH4wuVXp5MJ/Na8ytf2SPQofxWfPN2T/wAJDbf7rfzr6P8ADPFknbivmy6P/FR2o9m/'
    'nX0p4c4skz6Vw4b42d1f4DrozVtDnpVBfWrSNXoo85lqoGPOM1KG4qsx7GtEQgzzVuA8H0zVHPOKtQHCsPeqT1B3'
    'LYNOz7VFupdxqzIUmk4qMsaN3SgLEmeeO9JuphINJnt0q0wH5ppI6U3dTcigDd8On/id2X/XUfyNWNbGdTu8f89W'
    '/nVPw6c65ZY/56j+Rq5rf/ISux/01f8AnXp4P4Wefi/iRiZ5pQ3HNIaYDiuo5ifdnrTgfeoB61ItJsZMM5qQHj3q'
    'IHNP9BUsZMGxUgPcVEKcOKQyVSafmoQcVIDmgETA+lOBqMGn7sUDJBnrUoNQinigRODxRUaNUmad7DHAkU8HvUfa'
    'lB7Yp+YmPz2pc9qafaiqJY76UlICKdn1pk+o2jIpCaPegkd70uaZTsVYEm71pmc0e1N560EsdTc0UY4p2ExvSilP'
    'vRjFVYkOacPejFAHegQ4dKUU3NPoHcdTqaKdigYtAJpKTpSEPzinCmckU7NMB2RThmmVKB3qW7alKI4AkYpwWobq'
    '9s9PtHvb2QRxJxnuzHoqjuTXGH4h2CybRZSGPpu3jd+VfO5rxTluXVFSxdZRk+mrdu7tex7WAyPF4uLnQptpdf8A'
    'hzutp7VoxKthH9olGZW+4p7e5qno+o6bf2f9p27F1HAjYYZW/wBr/HvUc8zzymSQ8mvYw2Kp4inGrRkpReqa6nnY'
    'jDzozcKis10ZC8jOxdzljyahp568cUhGK60cjYw0zOOlPNRGgzEzTCeaXOaQ+1DAbnmjOKPWm96YmKegpOtO7UhA'
    'FBAcCmnr70pIAyTiqcs2RhPzouJtIld1Xgmq2puzXkuOmR/IVAWOeadqDYvZhz1H8hQZTneJR6VG/KqB71ITkYNM'
    'cYRfxqkczF8+4x/rXx9TTHvbhekrfnUDPVdm7mqsS5NbMc8rMeTSC/u4V8uKVlUHOAeOagJ54NQuTVpGEpPdE02p'
    '3rZXz3x3561nyTSSuZZmLs3UnqaG6nFRH0FaJIylOT3Yu4mkbJUj2pM57UFsjHtVIzZxfjggeI7kd9kP/opa4l8/'
    'hXaeORnxHcf7kH/opa4tlPaumHwo8zEP97P1ZVZQ44w2K5nVdPvLpML0Bzt6V05jGT7+lNMLk8ZpO5i1dHmV1Zag'
    '8exLcKwPB64x71f00X8aBL55FI6YHH4mu7+yOTjFXIrGQrgqD+FRKnF62CFN3M+wvndRGXD445PNbsUTMwK9++an'
    's9DlnkCwwl3PZRk/pXp2jfDzVrpAZ0Fsh7v1/KqU1BandRoVamkU2cNawbmAbHUVmXUusa3qp0vw+jkoSiRw/ebb'
    '95ia+g7f4d6baKHupHnI6gHateF2V9rPw48U3NysAZ/3yIXBKvFIeCDXbgpwnzOCvJLRM+U4xhXw6w8K0pQpSl70'
    'o7paf8Es+FG1LU9UPhy/jCahGWX5/lLBOob3H617npvgK0gYTX0qySAcKo4B9TnrivI/BlnqOu+KT4tvVaNUkMu8'
    'jG+RuMD2x1r6Ns/MkG4ggep4rizKSVT3NNNfU+g4FnOtgn9ZvK0mot7uPRvzKlv4c0uA7mjMjernP6VrpaW0IxFC'
    'i/RRVkGJPvtn6Uv2mJPuIPqa8lybP0KMIRWiGLE7cID+FSi1cfewv1NQtdyN/FgenSoDOc5NLUq6ReMcC/efP0pj'
    'SwJyqZ/3jWe03fpWRea7pVkp+1XMakfwg5P5Cmotkuqlq9DovtbD7oUfQUw3EjdWP515nefELTYci1ikmPqflFcb'
    'f/EvVCxWBY4AfQZIH1NaexdtUcs8fSj1ue9luMk/nVGXV9PtuJ7mNPbdk/pXy8PiDdatE0kl0/8ArDEFLYyR9O1W'
    '4tQEqCQtnPc0U1GS0kcc80/lifQ0njPRLb7kjSn/AGR/jVBviDHnEFvx6ua8FudXjt4WfBcqpYKvU47Cqej+JrfV'
    'yI4AwfGSp7Y60+WmpKMnuYzzGo/hZ79N43vXHysE+grn77xDeXIO+dufciuNjlJxuOK4K/8AFxTX1tYtzwqxiZB1'
    'LA4JHrntRN06drnO69WSvJnpMtw8rZZyfqayry4iijeSRlCICWJPAx6msPV9et9O06W8Rg0ioSkeRuLdhivnG/8A'
    'Fd7sni1OV44LlwxhByzc5yB2FZ18Sqdla5UG5PlR0njz4gRw3cdlpshQR/NJJ7noo/DmvP7Px1qAUjzC6BsksvJB'
    'Hf2712Ol3HgbVbW3g160kRoiQJQ3DbjnL96q31r4CiklgtrS6KhsBlkAUgDhhXiVp1JTc0md6wNRq/MjT0vxpYSW'
    'z/aov3iEYVMHzNx7A/rXMeJdXsb2cNaSeWu0CUEZIbPAC+varqzeG7SbzIbRQFAC5Ulu3OapXs/hS7mEslviU43k'
    'AjP5d6xr1MTVgoyia0sE431RzKX89vameK92TOSjBhx5ZXg/XIx7Vzl5PeNKP3gJzuO0Y+i5+nNdXLpeiziQQyzI'
    'G6KRnAx0+lZsui2iuNlwwUDHzDr+VefLA1ZdDVUZI0fDvii902JoZEikiJ3nnJwBgkN15r0iPVfDOpGO4ujLHtQA'
    'KmCDjk8j8q8VXQ2LlPtCBTjb15Huv17V694L+EWu6wY7id2srE8+ZICDJ/uJ1/GokquHhaT07M68PhKtWXLGJOdJ'
    '0S7ZI7G+YzuW4WJizbmyOnoOM102j/CvV7uDzYw6RBuWlGwYA5OD/nNe++GfCWkeGoQtlbfvyNrTOAzt+P8AD9BX'
    'ZklkMYHyjGBjv1Ga82eL5rtRSPpKOSQjZ1Xf0PFrP4P2iJt1G9iTgAEKWIJ9K6+y+GPgu1Fv5zy3M0fLso2hzng4'
    '7f1rs3gNyRiNiUIJJ4A6Z/PFTfZzGA4YEkluB09v89KyeLrWcU9DvhluGi78pVGj6Lbxsq2oYN8uGbtjnpVqJIzJ'
    'GyQIXiUJEduSq9gpPNRyyvw0pVI15yeB+JPA9vWvFvGHxls9KeXR/D3+k3Y3K04+6h6cf5zWdCg6k7QWp0Vpxpwv'
    'LY9N8UeNNO8J20k1/OqzAY8sEZOemcdP518VfEDx34s8axTW1rcPZ2ZyFVMgsPf2/WtGeK71qU3usTNPIzFsMeAT'
    '3xUg0yIjGMCveoYHkV3qzxK2P5tIaI+XLOTVNCvPsuoM7wM24Nk7lb+8jdjX2l4B8eNruivp15KG1S2QGN1wBcw9'
    'BIue69HXqOvSvHfE/hSC6tWKL8w5BA5FeF6b4j1HwnrSWN3I0QWTfbXA/wCWb9M+4YcMO4qlFpOjN6Pr2OaqlUSq'
    'Jao+xNf1rTESeS5nd2LksEkwQ442g9K8C1DWZ571Xefam773PT3x6Va1O4bWNNW+tVVEt2Z72JT/AKrdyJVPeJux'
    '7Hg1h+D72wu9UF/LZfbbO23SPCxxvABwzH6849Kwo4H2HM5as8XF15VJKL0Ru3moX2mtukd4CwV0JBDEEZVgfcc5'
    'r2L4TajrOoakl2JwmnxMBO5faN/ULtPUn2rxnX/Ef9t3q3d1ANqDaqL90IuAqj2GOlMs/E88L/Zrf9zHuDFI+ACO'
    'hHuM12KhN0lePvfkcccVThUum7H3TqHj/wAOabOlvJN5jNnOzkLj1ruLKWC/tIr21bfDMu5GxjivjezXw4tva3kt'
    '0Lu4PMu35R0+XluSQetfRmhfEPQoNNtNOkYm4UbABgggng8dMZrzKeZxVSUas/wse1SpymrpW+Z6PtA4NRuURdzf'
    'gO5rirj4g6Pa3slndh4WEoijZsbXB6vnsorobe8h1CFbqCQSxuMqynII9q9KjiadT4HcU4OO42ZmlPzcDsPSqpQ1'
    'fK1EVFdPMc0omcyelMKe1XmTJqMx1akYyplAqKjKnFXCtRlM1akZSgUWXNQMtaBTnioinXNaqRhKBSKVE6ADJPSn'
    '3M8dsDuOT6d6526vJLj5fur6D+tdVOm5HFWqRiF7fD/Vwfi3+Fc9JvYkk1oMKhZK76aUVZHk1XKb1Mh0bOe1VZY2'
    'PtW00frVgxrYIs0gDTsN0aH+EdnYfyH41vBtuyOV0TFEY0pBNIM3jjKIefJB6Mw/vEdB261jMrsSzksT1J5JzWrK'
    'rSOZHJZmOST1JNQmHHFehBcq0MZRMtoxUBirXaHiq7REVpzGbgZjJ7VXZPStVk9aqsgPTirUjGdMy5I6rMntWsye'
    'tVmi4rRSOecDJeOqjp7VrugPJqrImatSMZQ7n//W/eWK5WXgGpmQOCDXnek6yrMFZua76C5jlUEHrWVOopI1lCzO'
    'E8XWYtoYZV/imUVi6lcSgbTkcV1vjUhrG1Hrcx1Brek+dFvQc7a5a0HeXKbQlornnW859auQZ3rg85rPlV7eQo45'
    'FWrSUCZS3QGuNbmjPW9HdhbruPathpU7muNi1OKG2BDDpXP3niZw5CGvQ9qoxSMHBtnpM8qFMKa+NfErfJqOP78v'
    '8zX0hoWqy394IZDxtY/lXzZ4hIK6iP8Aal/ma4cbPmSaOzCRs2jsfgad1tD/ANcj/Oue+MA/4rO5/wCuEH/oFdD8'
    'CseRAP8Apk386xfi+v8AxWlz/wBcYP8A0CuCv/AXr+h2UP479D5ouxjxJa59G/nX0r4cx9jT6Cvm+/GPEdt9G/nX'
    '0V4db/Q0+lcOF+NndiPhO8toDLEWA6GmFSh5rf8ADsKz2km4dG/pS3thgnaK9FHA0YKvULHPNSyQvGc9ar96pPsR'
    'Yd71ctSSrfWqO7FXLQkhvrVrRkvYt4zThGTzSg8+1WV56CrbJKLKQaZir7J7VUZMGhMRCSaaWpxyelRNkc1SEOJF'
    'IWzTenFIaasI3PDbD+3bH/rqP5Gr+t4/tK6/66v/ADrM8Of8h2x7fvh/I1oa2f8AiZXY/wCmr/zr08H8LODF/EjG'
    'PWmj3oPvR1FdTOZBmpFJ6DimAZpw5qQROp/SpAaiGakX9KQ0yUGng81FTuKBjxnNPBxUWakBzQBODxT6gU1IDigN'
    '0TA8U7JqLPen0ASj1FSg5qDPpUgNAyTP5UuRTaAaaYD84NLn0pmaMnimtyWh+KdzTM98U8cjiqIsJ2zSU6m/ypiD'
    'H5UtN9hS44wKaZLHbsdaTdTTkmiqEx3FGTSCgUyBeopQKSlBpiTFxRR2opjFzQDik69OKcM0CRJwaUe1MpQaL6An'
    'cfS9803IJpRR5AmO7UopKUNz0oGOFShSeKjyc8VKuR9aiexpB6nnPxEWbztPtQSIhAZcdi7Ngn8AK5mz0dE0uXVt'
    'QcRxJxBEeGnbPIHsPWvZ9a0BdYsYJbkfvLZy0QJx5inkxk9gT3rxnVLXxHfXrLdWcqtnakaqdiL2VccYr+deOsor'
    'YbNK2Oq0pVFU+CybWyWtv5Xsuvpv+u8NZhCtgaeFhNQ5Piva+99PXq+ht+B9Rlk12WEn93cW8m9R90eXgoQPbpXp'
    'zEda5jwr4bOh28lzeY+2XAC7Qc+XH1x9SetdI3Xiv1Hw9y/F4TKIQxukpNys90nsn+dvM+I4txmHr46Tw+qSSv3a'
    '/q3yE7UEg0nvTCcivu9D5TzFJz0qFqcTgUwmnfoQxo9qQ049KaaTFuB64pvGKXijtigTYYprkKMmkdwgzWe8jOea'
    'ZEpWFklLcdBVcmpSM8ComU0kzF6iHnpT9TDfbXfHEgVx9GUUwBycKpP0Bq8sEl7CtuwKSxg+WWBAZf7pPt2p31Dl'
    '5otGEWpsjZVfxqeexvYmKvBICP8AZNQG3uiqjyZOM/wn1+lUmc0oyV1YqtknioGHY1fNrdd4pB/wE/4VA1tc45ik'
    '/wC+TVozcWUzUDnmrhtbk/8ALKT/AL5NR/ZLr/njJ/3yapMhxfYosKjI5q61rc/88ZP++TTPstyf+WMn/fJq00ZO'
    'D7FFuKYSeg6ngfjV02V0ekT/APfJ/wAKSWWLRI/7QvsGReYLfILPJ/CWHZQeTnrVKRDpvrocL4zAfxJdqD9zy4z9'
    'UjUH9a5b7PnpV2Qz3E7zzks8jFmY9SxOTVqK3L8CunmsrHBOPPNy7sxxbZPStG300v2610dlo8tw6xwoXcngKM16'
    'tongZIQs2p8ng+UP6msZ10jsw2XyqOyR5dpvhW7v3CW0Jc9zjgfU16RpPw4tY8Sam+8/8804H4mvToLeG3jEUCBF'
    'HZRipgma5JV5PY96hlVKGs9WZ9hpWn6egSygSIDuBkn6nrWoseaeqcDNXIoifmY7VHc1g5dT04xSVkit9nDDBGc9'
    'qp3Ph7SrrBvYEcjoCAT/APWrZedEG2Lgevc1TeUE0KUlszKtQpTVqkU/Uz/7MtbdPLtI1jVeBgDj6VT+zOjZZy31'
    'NajzY6ms+WXPAq1NnP8AVqaacVawxiR3quzOT8tZOra5Y6RGZLpxu7IvLH8K8h1/4kXEgMUB+zxk4wp+Y/U1ai2Z'
    'V8XTpL3mevah4g0zSl/06cKw/hHLfkK4HVPifFEpGnQAY43yn+grxS88QwTea80uSgJYk5NcH4q1aSHToJrZtyTN'
    'uLD0GCAfrTm4Qg5N3seTVzSo3aGh69qXjrU9VKpJelfMLBY0+QHb14HpXn2qeMJNKvlEwEkLIAe53E9c15LpuuT+'
    'eXlJmLNuUE/NHnO45/kO9dX4k0RL7ToLyCQFlToQSXB5GMd65vrUpU3yLVHBKtOTu2eoxat9tt/MtCCxUNtJ6Z6Z'
    'rI1hLn7J58zspYFUROWfI5z6CvLdAXxLYzrLJEqQFlDbmwAg6FvYfz4rtdW8QWtyWe2lJlhChFDYBUdePeuatmsF'
    '7lXRhFTa5jBgaa0dSx8sBv59TzV/XvFV3Ev2azbZJbtlz0DLjjAPSrWmX1r4gn+yxlA6jcBKO46gfSsDWfCS+adR'
    '1G/BiUkuqA8qvXGemBUYqpTw2FddVPdf9feXRjUqz5IRuym3jG7vLSO0MrCZcsXHG7POAfYUaP4rfQpV3uXDkMyq'
    'QCwzkjPvWJFZWoEN9p4lmhuJJIRkgqg6DJ9T2rlL9Fti6ZZfJfaVfhvwPevFp5zGvK0G7rudU8HUprnke2SfEbUr'
    '6b/RWEfzFlVRnOf4fwrEmj1O6mfUJGEC7y+cjfuJzwoOa8y03UWhkldgOMEY4GPQH1NWX03w/NKt2YZA8x+fbK/T'
    'PJIz2Ndrxia99sdCMZO9Rnol/cXt95SW658tcF3K7ix64GeK5ubw5cuxml2lieWaRCf51hyeDrS/imbRVUyRnBWa'
    'SRQwxyQc15JrHwf8dBpJIp2KEkhVkY4BOQOvaqp42nPW59Bh8LCSvBHsNxp0sWQxXA6DzEH9arxhlyHdF44zKn+N'
    'fIuu+FfEejXaWl/9oDOhYEu44Bx61Fo3g/VtY8/YX/cbQxaZsfMDjFdKk3HmS0KlyQlyylqfZiJbOV3XMKn3mj/x'
    'qOWCyQ5a8thk8kzJgD86+XdN+Ges3UKTrLEu7J+d3JGGI/pVC40K9sZrqCYxsbVipxk52jORmr5J20iQ8TQWnOfU'
    '0t5o0BHmapZrt/6bKT+OKx5vF3gu2k26lr9tbRA/MY8yuRnoMcCvna00O6uYTKrRx/MV4jB6fWtS30SGPQ9WS8jS'
    '4KvbsrsgyoJYED8qyqKpCPM0aUsRSlLlg7s+m9H+M/wP8OSpe2qzavdx4KNPxECP4toHJFetL+1/8M1RN32yQkDc'
    'sNuFHToGY1+WNzaQfbJbaKDAQ4znGfwrh9YtLy3uzFDI6KZFxyeAQK5I4OlWfvXfqz0FmNSl7sWl6I/Xa8/bH8H9'
    'dM0O8mK52mWVEHJ9B61w97+2TrLbhpnh+BOesru5r4PsPDmo20e43jAKyryM9cVU8R61caM0iWsgchV5K889a5Y4'
    'KjJ2pxT+83lmdVfHNo+0Lj9sT4iNuEdpZW6+0Wf5mqD/ALVPxcvSnlXECCXlAkKjIr5B8G3U3iGYjWAWt1LqPJXD'
    'kqoIz7V9KeHPC2mtd2JdJEhaB5ArjkgNtBFZVaSpyUFBX9DWGK505Obel9zXu/jH8XfFbwWV5qBa3hkEzRABFfbk'
    'YYrz34r0rw9AP7Gj1O/QJIFZ5sZbkHqCeTWQuh6ZDMn2NeSCCfwr0vwhaxxXWlR3ah7c3MQkVhlShk5DD09a6qcZ'
    'KLk1sc0qsZSSXUyY9c0RSEN0in0Y4q/FqNpP/qJEcf7JBr23VfBPgzWPHcdvcabbG2GjSylYxhTJ9qCK3HcKMV5c'
    '3wq8H3PjDXdOhV7S2tobNoBFIwKvKhLnOfUdK5aeY05RcmmrK52VMvqRdk09bGM+yZCp71438QPAsesWbtCmJByr'
    'Dgg16Ro/w+kudc8QaX/aN6kOjyqkUiOSXDf3qsaLZXAvNU0m5uXuktXhETygbtskZYg4967PZKrHmizhjWdOdmj5'
    'O8M69qOg3Jsb9iXtSYmB53I3BUg8FWHUHrXtH2O2bR/tvg6IfY79DHMi9VkHLBCeh/2TyB0zSeMPh9Yz6zPqUs0V'
    'siQIWz96Q5PAUfoawItKvfDVteQaXeyIkixuOQUl3DKgIf4h61lGsoe5M4cbUpT16mn4Qs7K5uroaiiyrEm0JISu'
    'HJxyB39PSrUuk+HbXzbmO5dZJHPlxqQ2zB5HvXnM17q1rejdMZGuM75GG0bjgZb6VAslxaPNLnz4ICgkc5xlyQpH'
    '1I/Kuar7epVbhKyZ5MZ04QS5b2PRNduor5YHtZFt4kQRq3TPoT61g6N4pvdEvJG3NLIh2oxyBz3I/lWVpy2dxO8G'
    't3JtlKFo9o3hXYZUMAeMj8anuYpZjHdk/wCj58jeOT8vcr1yBVU8rjGDjUd0ZSzCXNzR0Z0b+MLi7kl3ysz796jO'
    'Rkn5voPavpb4K65rWo3X2R0klsBEQjAjbCw5JcdcnoK+V7TQNNuIhcWF6Rco3BI+QgHow7Zr6y8B+P8Aw54U0dFu'
    'IUgM0YjTaAT5sa/Ozt6E44rjvh6dVRjoz08HKrJ885aH0Q0JxzUO3HavCIvjrDP4gs9LmhRopf3UjQ85lcgLtJ/h'
    '9a9+UBxuB68jHevRU7nfCpCpfkZWKCo2Sr+BURTJq1IbplAxg8VXaM9K0imKp3U0VtEZZWwAOB3P0rSMuhjKHVlB'
    '5YoyqucbztH1rLvLxUzHBye7en0rjNb1Ge4uVeMldjfKAeBVnTrlp4dshy69c16FKiklJnjVsTeThEtS/OSWOSe5'
    'qqY81oMg/Oqk7CJdxBIzziuyMuxwTj3KpTFRMnXirgIYAryDVgRragTyjLnlEPb/AGm/oK2jduyMHEorGlnGLiYB'
    'pWGYozyB/tsPT0HesebfK7SSEszEkk9zWpLulcu53E8kmqrxHqK76cVFaGE432MopTfLq+ye1N2DFaqRlymeydsV'
    'WeOtUoarslNSIcDIkjOKrNF6VrPHniq7R1akZSgZLJioGj71qtHVdkx2rRSMZU7mQ6D0qq0dasicniq5XHUVpzHP'
    'KnY//9f9aVkeBgy9a6PT/EskOFfJFZk+nykgKpzV+y8NTT4ZsivHipp+6d7t1NXW9Wjv7O32/wANxGx/A16Mrw3M'
    'AII6V5hrGlHT7OM/3pVWtrTbqe2l8uU/KcV0wqNP3kZyimtCPXdD81/MiGDXOy6JPDFv7jmvV/3U0YbOeKxNQkgV'
    'TESAac6MdyVN2seTSy3P+pyRjirdjZCZsyGtmbTDJIWQcmoHsrq1+bHFcyjbcts6TRrOK2ulZDzhh+lfLviFiBqI'
    'P96X+Zr6W8PyO99hz0Rq+avEeCuo4/vS/wAzWWJs4qx04V6s6/4FzKqWoJ+9Gw/Wqnxe48Z3X/XGH/0Csv4P3Jto'
    'bKTp2/WtP4skSeL7l/WGH/0CuOv/AAF8jrofxn8z5q1A48R230b+dfQnh9sWSH6V87aoceJbX6N/OvoPw+3+hJXB'
    'h3753Yj4D2TwrJi0kGf4v6V0josnUVyHhdv9Fl/3v6V1UbnNegmeeypc2CtGWA6VxM67JGU+telzEeQ2a81vD+/b'
    '0zV7PQV9CvVu3+6frVIHFXLcZViPWqjuS9i9Hya04hkVkxNg5q/HLVsktSDAxWdJx1qw8vFVC240IGyLk/SoyD0q'
    '75YNRtFg1SZNioRioyO5qcjHWomqtCDX8N/8h2x/66j+RrQ1v/kJ3f8A12f+dUPDmP7dsc/89h/I1d1s/wDEyux/'
    '01f+deng/hZw4v4kYp60tICKXOeOldLOdIcD2pwpgzmnggdOtAupIOakHSowe4pwNIq2hJ1/CnCmDI5p+OaAWwue'
    '9SjrUdSDHelcLDxwalB9Ki6U8NSbDzJenFAPem5FKDTAlzUtQjpxUgz3oTAk9qORSdDTgO5pgG6nZ4pjDvThyKAY'
    'oPapAaiIx0ozjmqRFibNNzSZBFLiqEIPzpSOwpR7UoOee9WiGJim4qQimtTIY2l6UnSj6U0IXJpRSCl5pk3HUZpM'
    '5o96BoXNLTcE9aWjYNhwPanZqMetOWgXmPpwNMpwpjHU4cmkxk1MiEsAo3E9hQ2DFQYrahto7dBc3Y91TufrSRQR'
    'WC+dcYaX+GPsPc1QuLp5nLyHJPT2rJu+xsrJEl1dvO+5z06DsBUX2hwMbjVQtk5NNJA5FLkQc5I75qHdQT+NN96t'
    'JIycgPPFMz6U4dajOPxp3IbHE8VGTQWooExPrSYp2PWm80CuBpjMFBYnFW4baa4bES5x1PQD6mqN7f6Rp+UdjeTj'
    '+BDiMH3PeplNLcl93oMjinu3/coW9MCny2UFqN19cxw/7IO5vyFczeeI9Suh5aMLeLskXy8e571i+aXO5iSfUnms'
    'JV30OaVWHRXOwfWdEtjiGKW6I7sdi/lULeJ2xiC1hi9Djcf1rlCB1qHODWbqSfUj28lsX9b8S6vHZl4LgxsWABQA'
    'cVwb+I9fdsvfTH/gVa2ttm0X/fFcrt3deK6qPw3Z5uKqzc7cxuReJ9fUY+3T4/3jU2p+Itd+xWciX0yszTZIbGcF'
    'cZrACEVZv8/YLEf7U/8ANa6aSXMjnVWpZpyf9Mr/APCTeIQedQn/AO+zUi+JNfI5v5/++zWOyAnNNHpXYrdjH2s/'
    '5mbv/CR672vp/wDvs0n/AAkevdPt0/8A32ayFGakCDii0ew1Un/M/vNYeINc/wCf6b/vo1Ide1s/8vs3/fRrHA5q'
    'ZVxT07D55/zMvNrestw17Ng9RuNUi7ysWkJZj1LHJoIA6dKsQw7mHFJuwc0no2Rx2pY8Cup0XQrnULhYIF56knoB'
    '3JNT6ZpxmdVUZZiAB7mvadJ0uHS7YRRgFzzI3qfT6CuepVtsergsDzu72I9I0W00iELCA0hHzSEcn6egrYxilwKU'
    'D8q5W76s+jhFQXLEQcnFTouaRBmpwpJCjvUt2KuTwxZBkk4Rf19hUc9wX9lHQDoKsXREeIF6IOfr3rGlkpLXUTdg'
    'kmqs03NRO5qsWyau1zJsmaUtXn3i3xhHo6tZ2ZBuMfO3UJkfzrovEGp/2TpFxfL99V2p/vtwPy618t6zqDyFpJmJ'
    'JOST3JrSKSV2eZj8X7Jcsd2Tav4iluSzyyEsx5YnJNcZqM6TQuS+BjJOf1rM1e52APu+TIz/AErjLu9ZWctPhWBG'
    'wc8VzVsWoOzPnajlPUq3UlxJfSRwzkxy4YEjrxzn8KpXV3LerDZyy7baPJz65PXHqe1VXnW3dHjdZSclfQcY5FU9'
    'QuIJyEZsOOSFG3k/1ry5Tc1daGW2jOp020sWtXa2Vg7t5cchOQeOcj61oSX2q2MSMzNItuMFMdFHfj2rytbyezWL'
    'y5irq5YqpyFH+JruPDus3eparDHJKJAD5sjY4EUQ8xwfbC15VSeOhNcjTT+Vjpj7CWj0Z0uu67t0pdNK+Vcz7ZpR'
    '3XjMaH3wdxHqfavPxDe3Th44mDg8svT/AAqxq8kl/eSXRVmlkcyvn3Of/rfStuWw1S30qVZZI3Mio0flHGzHJBHc'
    'Edayx+ZQp2cuumpvRwkq0mley7GroaxWd4JZgYWjXczk/e+nuaf4v1S41WCZLPYokG10ZsBR1+X3NeWa94tt4rVd'
    'JMpnZGy0g+UgjoFPtWJ4ejvr+9kbVr8xwTt+5iXLOygc5x90V4mNxeIr2nWdoR2Vt/P+tj18NSp04unTV293fYsX'
    'WsXVpdQ6cjv9kJDS7Dt3levTsK6bT7rSfEd012rBhGdkkGcKI8YDKT3z3rP8ZXEFrpME9hHGYLhDG+F5VR90huoJ'
    'wQa8UttSuYpWt7LK+aexxuA7Zq6VF4il7aHuvb/O5jOt7Cp7KXvL+rHst1o15pMqTXpVbWSQgMr79noG98VIL+0W'
    'YqXwG4DDoCOoNczBrV9qmlpZRg+chJnGCxJ6Dj371t6L4F8Q63ZS3NtGI9r+WRMSnXqwB68cV6ODhXnG1TV+RlUh'
    'Fz/crcuWniAW1wWaRjAT82OrKP8A69fSEMYnhhmAykkaOv0ZQRXz2Phd4tMPBtlIOdu/J6Y619OQIlvpdvDgGSG3'
    'jj2g9WRApGfrXsYLDOM3Jo78BGpDm5kfN3xesYW1S3YqPlsWP5uf8K848J2sCDUSp58xBgeymvdfH3hTWfEt2k1t'
    'GsSC28htzjIJcnI/A159pfw01/TpJiroBMwZsuDyBXuxkuRJszq0pucmkZekrIbWM/73/oxq8v1oH7dq7Hn95J/6'
    'DX0Vpnw/1mOKOF71EWMEEDB3EsW/rWbL8Fb29kuZH1FR9pZmICAkbhjrWvtIW3OOODq3b5Tw3S7q2GnNuIB8yTGf'
    'wrds1hu9E1aFfmdnt8ccYBbP616lD8ApEQRvqrkdeEHesrxR4SsfAdglsl08814SW34XAXhSPzNZVuSpBxTNqOHr'
    'U5c9tj5vuPD88epXEnlkqWyOPauJ1+yjjvS8isu1kPT6dq9juH0+UGOaXJHTDtkH/gIrjbrRxdS75b2Mj3RzwOna'
    'ssPhXF3Y5V5ybbR0cYjvoJBHwEkB/AAGvHvFlusmozoBhAi9R9K9bsorXT7Z/Ovdzu3CrE+D0xmubutBsry6eea+'
    'JMnUCJuOmP5VOHwjpXsXWxDqSu9jJ+HTRxs0WDzI+0YwTlBX1toz/aobARo6m2gkhYsMfN5mcD6etfO2haPp+jzB'
    '4Z5JSGL5MZHUYxzXo8PiyHT02xCfPJ49aKmAVSSm907/AIWNIY1wuk9Grfie5W8TLPHu45P8q9L8PzQQzWLuAwjm'
    'jYqe4VwcfjXyOvxDkH/PbI78ZFeleHdavtc0hbiEylcspPQ8H1FbrCWVio429rH2BfeIU1Hx8smnwrbLJo0qEHp8'
    'lyHzgfWvOUa9uvGuuxmXaUjtN7LxuwpArye212+sLkXcXmpOqGMPlidp5K89jU1v4nuYL2a/Al+03ShZWOfmC9M+'
    '4rijlUY/Culj0JZvKdlLvc9d+G+oXVvqXii3eUMrybiWUFj+9K9evSuY0eOKbxBrrp/ftf8A0Wa4Gx1q506WWeJp'
    'lafPmHnLZbdz+NXNB8SQaVqF9dTq8pvmiY8Y2+Wu3FdEcJyXaW5yyxnNy36XPOfjDqc2meJ4YUH+stUyTk4G49B3'
    'NeXSeIS6xt83nJw7s2QcdAvoMfrXrfxN02bxtq8Go6W0cSpbrCRIcHIYnIryl/AGv2xZFSGdSOCsg+U+tYzwMXLn'
    'aPJxNScptRWg+71hbz7N5oa4hiG+RPu9PQj07mhIry9hEtuXaEbTM2MRqSSqZPTIzxUJ0LxHocLXEsYRJVNuzjDA'
    'LJ8rZ9Bitv8Atu80fTn0EgPaAAKCuA5zkSep56e1YTpqm0oxOd81vfdjoND+HFjqYto9P1RWuHhkupo5Pk2oisQo'
    'Ynl+OfTNcRc/btLniuYXWRmLHy1O7Gw4wwHHNaMOpWavDG8XyrHtkYMcu7ZyxI9OmKie3mW1u7izBaGJPMm2kZVC'
    'cDn/AArNNuXvCnKFvdWvkZdtq2oXF0QJRbea3zY4UfUVsrcaq9vIrSebFF12nPJHUCuCluQ8m6EbF9M5NdB4fvdS'
    'srlbm1GZUIZQRkcex4I7Yp1sPFe9YwpV3e19D2r4b+GNR1q6sdThj+1Qi68ueHByNpBOT2BHftX6J2saxwpDGNqo'
    'oUD0AGAK+QPhX8UrfSNLvF1O0t4rgK8qIiCMPJkZ3EetT3fxw1MatHe2u5YRIrNb/wAOBnKZ9DXC7Nux9LhMTQo0'
    'k5PVn1+UIpCo4rIt/EdhcaZa6gHDG4jR9qc4LAEj6Co5tZgE4gQ8suVPvQoy7HrOcN7jtS1FbMrGBuY8ke1cNd3E'
    's0heY5J6Dt9K07lme5KyNuOAcmqE/lMTFkbx2rvoxSSsePiasptq+hy9/B828A8kH2FQ2chhufnJGev0rZuxiIg9'
    'cj+fWsMTRpMWkj389Sa9CjdxseTW92VzqV+YZHSq1zFvjK1ZtJY7iPdEOBxj/CtcIlmBJIoaf+FDyE9z7+gpwi+a'
    'yKklJGLa2P8AZ6eZc/NK3McR6KD/ABN/QVFKGkYu5yWPJq/IxkYu5yW5JPeqzLXfCyMOToigyelQtH6VoNGCahaM'
    '5wK1UjNxM4xjrURj79q0GjPUjNQspqlIhwKJX0qu0fetBlxUDLmquZuBnun51WeOtJ0qs68VomZOJmOhqEpxmtB1'
    '4qs61SZk4mbIlUXTArVdc8iqjpnOa1UjCUD/0P3U/s6EfNtFRz3UFkh6DFaV02yMkV5D4g1CdpWiBOK5a01TWh0U'
    '433NPX9aivLdY1OfLlVvyNUL3XI5RlBtI6GuPDOIpC3cr/Onvk9K4XVb1N7JHVW3imZI9hbpVGbVZ7i4DlyRnpWB'
    'HYzzcotdT4f0nfcBLgfnTjKT0JstzqNOu4gFaT86n1rUrKO1bBGa25dBtvJBQbTivM9c0i4Em1WJXPSuiacY2ITT'
    'Zd8N3DT37Ov3djV88a+3yagP9qX+Zr6L8OWUtlN5knAKEV836+SVv8f3pf5muHEL3UdeG3Za+GzbNMtH6Y/xrZ+J'
    'Enm+I5JPWCH/ANArA+HII0i2J9P6mtPx2+7WGb1gi/8AQa48T/BR14X+Mz561Vv+Kntfo386+gtA4sk/CvnbVm/4'
    'qi1z6N/OvobQP+PFPwrgw3xs78R8KPX/AAqM2kn+9XU4ArmfCIP2SU/7X9K6xlFekrWPOkRysfIbPpXnt0f37fWu'
    '/mB8luMVwVz/AK5vrVdQRVNbml2/nRMcZyaxCR0rtvC8YkiOefmNAOxkT2jx846VV3leK9EurFSCcVxuoWwjYkcV'
    'd+jI5exlGQ96crjNVGfnFND4OetUmQa6MPWlkORmqKSZqxncOKAsQMagbOeasvGw+lVmXnmquBseHB/xPbH/AK7D'
    '+Rq5rmf7Tu+f+Wz/AM6qeHP+Q7Y/9dh/I1c1wf8AEzuz/wBNn/nXqYL4GedjPjRiL1pRSHA5NKK6mcz3Fzn2pwyK'
    'Fxmn446Ug3Hr61ItRDNPHWk2CJce9PzUYp46UIaHDrxT+nWmCnfypXAkzkU6mDHelouMlFSDpUQqZfShMRIpOcU8'
    'CmCn0xjucCpB7VHnjinDii4h9JwKSimDD6Uu2nDGac7DbgVRI1aXIzjrTEBXknrSkgmqRDH/AEp2cVF2pSe9UiWS'
    'bqaT60zPrRnPWqJaHd6D7UnBo6dKCWhc8UvbrSUnSgXUf0pfamkg0A07gO6c04YpmaUYoAd06Uc5pee1OUUxoUYp'
    '4GelOVK17XTWdfOuj5UQ5yep+lJysNRu9ClbWstw4SJcnv6CtUmHTlKRYknxy/ZfpSXF8qJ5FkPLjHVu7Vjs5NZ3'
    'bKvbYfLK7ks5JJ6k1XznpSmmE1RLYE5pO/FITS5Apkid8UmKXGeaDRcVxCcDNMNOJppGaEKw3FJjPFS7T+FSwwST'
    'OEjUsfbt9aLiK6qc1bnS002EXOpvtzykS/ff/AVUv9WtNJzFaFbi76F+qR/T1NcLdXU93KZrhzI7dSTWM6utkZzq'
    'KOm7NXU/EV3fAww/6Pb9o04yP9o965tvmOKeRyabXNK97s4pylJ3bIjxTKmxTCMdKRAzJpCc0pB60mKBMoahAZ7V'
    'lHUEEfhXJLG2/Zg5zjAHeu8K7htI4NEkEemRqIwDczrvZyOUQ/dUehI5JrrozsrHNVoczuYMeh6kyB/IbkZ5wD/O'
    'l1HRtUktLVY4CSrS5AI4yVx+dXC0h6s35mmjdxlj+ZraM7O6I9lCzWpzg8P6zn/j2bn3FPXw5rH/AD7N+Y/xrocs'
    'e5/M03LD+JvzNbfWJEewgu5iDw5rA/5dm/Nf8akHh7Vz1t2/Mf41sbnP8TfmaNzDGGP5mqVZj9hDzMweHtWUZNs3'
    '5j/GkOhat2t2/Mf41qFnP8TH8TSZY/xH8z/jR7Vh7Gn5/wBfIzk0DVjk/Z2/MUJazW8nlzIyOOzDFaGW7MR+JrSs'
    '5hKVtL0lonOFc8tGx6MD6Z6j0p+1vuEaMb2R1nhC08y6EzDIiUt+J4FekcVxPhUmF7iFxh1AU/VTzXYGTNYT3Ppc'
    'GlGkiTOOtODdqh3U4GoOq9yyh556VftiPOTP94VlK+KtRORhh1HNJodyxdsTK/1NY81b12u4idfuyD9e9Y0yn0pR'
    'FJGdJ061X6nirMi1ARitEYM4vx3HI/h92TkRyxs2PTJH9a+ZNXtJrmQbOAPXtX2Nc20V3BJbXAzHKpRh7EV89+I/'
    'D0+j3TQSKTGxJjkHRh/j605xUo2Z4mZ0ZNqa2PBNS0+VnAkclSSPpiuautNtoZVdVdwOuR1+lezXNhk9KyJrNFOC'
    'MkVxVKMb3uePyvseF3unCFhJHG65GSfQ1nnSry4wBGxM2SvqcdcV7pKLbaRhSemMVkzQLPjahHlH5cDGK8+vUpwX'
    'xCWGcnc8Qbw/qCsx8lygGW4PStnRoJbKz1S7gBVmtktEPTD3L4P/AI4jfnXp7eYx27iiYwQf4vUk1rSaRpA0Fotg'
    'H2m73kjuYYsAj2yxryZZi9VY66eW7NSPO7G6ubG1kiuTH5wjYptwZCwPAJ6YArGufEQu5GMreVKEIAQ4yMdMVr3M'
    'HlJPb2abt24IZOCCeMj/AArzC98PaimopfTK+2IckdOOmfrXi08Gqk5Tr/I9T2kqcYxgzl9USytdQa6l2yoFLLGe'
    'cyN0B+nU1U8NTXOmTtqF5K8ZngdomHQBjj9egr0W98E2x0/7ZeziGWb94iP0y3OD71iy2VhFYggmSSOQOQfuFANp'
    'Rf512L2dWm0ru+jM+ScHr6nNan4iurnTjbTPmAADAAGQOma4aV4I5VeMlkwM54Oa0r2KUySqgyoJYL7ZqrpOizav'
    'NIWkSCGKNpG8xsFgozsX1Y9q9KFKnRpt7I5nTlUktbs9B8E/EKPwrf3GqxadFcy3CCP94x+RR97aPVu9eyQ/Glpr'
    'KS9n0xGAAKR28oLY77sjjFfKWpWsmlzC3tnDxyDqfvj2Poa6fwnBaF5llk3SGFtseDkPx19RWlCs4qPL8J2Uas4e'
    '4me9aN8dbbVNYt9FXQ7lJ7uTy0JkXbkjPJ9K9mvfGelaNCp1SCZH8pZWCLvC7hnAPfFfJnheKKPx3o/yjifP5Ka+'
    'ifFkC3UkRHQ28f8AKvakly80T0MNVlK/OYF1+0B8OFdoHluA/TaYDmm2nxp8BX8zWtu1zJKo3GNbZi4XsSAOleCa'
    't4et38ZySugIjii4xxnBrrfh34i0Xwh8Q9cvdRULHNp1pDGQoOG3bj+YFcGIxUqak4q7SuepSw8JKLlKybseyL8W'
    'vBaS+QEvPNADGMWj7gDwDjGcVci+L/gp5TCr3CyKMsht3DDnuMVk2HxL8N2nxD1LVJCrwXOkWcUTBAcsk0hYAY96'
    '8xk8Uw3HxD1HU4ogYryNxggAqA6kfjxXnRzio0/3fS52yyynGzVS93Y+kfD3jjw34juXtNNldpY08xleNkwvA6nj'
    'vXi37QNtc3DWMljctDvt5ImVcc4bO7p1GcCtT4YLJN4g1mQEsrxwsoPb5m6VZ+Llk8sun7gTtST/ANCFerh8RKpS'
    '59jhrUY06ltz4IudP8S2V06x6nKVB4yBnn8KnS98SKqhLhpGH5n8K9a1PS085iV6gfyqsumW4hRNo3YTBA5GBn/C'
    'tKmJqwSdzhhh6VSTVjzqHVtelBMjsyocH0BqC51u+jIXYXZuBjP9K9K0rTBPpN4EXPzHPt8oqWb4e6v4bv7G51Qw'
    'MlyytGIpFk4w2c4zik8dJN8z1Gsvi7cvU8oOp6qoEiwMSeQPm5wM8V3FpaXFybRJlw1yoYgZyuRu716Bo+mpNNCr'
    'RhtkUpAAyfuY6VuW+iga1p8IUHjH/jlYyxNSclFNr5mscNTppyav8jnLHwRaykb1Y5710kGhX+mw/ZtOvJ7eME4R'
    'GIGSefzr1Oz0UxY47VfOjliMLzkGtVGo95Mim4Ju0UeCt/acjkJq052MVbJPBBwRV60fUhljq0h29SW6fpXZ2ukX'
    'MF7dJ5ROXlYDH+31q7ofhe61ePU/LMUIiuW3eYMEjYCcVpNwpw5pVDmhOpUqckIHMR3d+EGNXJBGeoP9KWOLxDdE'
    'taahvUHBICnn0yK7Twv4WsLXw3bTyBZJHR3OVzjLNxS/D3So4NMunK/eu5OPYACtaL9pzcsnoFS8OXmitVc8/Y+N'
    'RczQRXSFIwh+ZBn5s1z994t17R737FfPE0oRXP7sYw3Svoj7Fbm/uSAMkRfyNeCePvD7X3i0rbsFJhiB9uvNdNuV'
    'Xm9EcGJqtRvHcSL4h6jLFJB9ltp1MbFw0fGwdSea5a8uf7RuPMVGK7QETJbaAPur7A5xV+fw/bRuiWbFHKnzSxyC'
    'O2Pr1/Gpba1n0/UIJVwYmkTJx0YHH5MMiuZVoVbNHmVZyk+WTObiO6LCrs2HBJ757/hWnNaG31GSzS4NxbBgpeLO'
    '2VQAzAewPHPpXaeRYvYXWjWtqv2uW5k824f7sKIxxs9yBiuo0vTPC0d8kao8ltHbiNgz7PNlyCZHP8KDoAOeKp01'
    'uJQW1zh3t/CknltZQSQT/wASdV/XvUCW7qx2rtWPnI44rqNW8Pxi4afS4zsllOzcPLT5idqxqecDsTXOT2d9bzPF'
    'MOUO04ORke9T7M5K3Mnt9x0VrNYvbBEDG5Zhkk/Lt9vfNdlo2gaMDFqmoagi2+R5sAGZVUkg4/2h2rzy2Q8FVwTX'
    'R2Nq4wHVip7d6x+rpXKp13dNo+u/D+p6bqGnRPpXMEa7FB4IC8citYDdIHYknPNcX8PdPTT9Cjbywry/MWDbtw7f'
    'THpXdMAe1aRjoe3CrKUU5E+1Wy6ZJAAznpWbdQEyeb0Gck+lWfnTlTjFK04KkOtCi4vQ05lJWZhXEbOVYtklsH6V'
    'nNazXNz9lgjLsegFdXJaG6aORP3aZ5Y/0HepiPLQxWqbFP3m/jf6n09q66NzmqUk3qUtMVNMUxBhJID97+FD32+p'
    '960GBf5m5zWP5bxMcjgmtiPlBgYrp22FBdCIxjpUZjNW8Zo2mi5TgUWjPpULJ2xWoVzyagZB1pqYuQzWQZqBk7mr'
    'rvEG2swB9M81EcHoatMzcCgyCq5X2rRZM9ahZNv0rRSMnAz2jzVV1PetNl/Kq7rxVKRjKJkyJiqrrWnKnoKqOmBW'
    'ikYygZrrnpVZk9a1GUVXZMVopGLgf//R/eWdPMTbXG32gJcSFsCu4ppjHWs501Lc0jOx4zr2i/2fZrJj78qJ+ZqP'
    '+w594UDiu28bIv2C2AH/AC9R/wA66gWURw2B0Fcjw/vNI39r7qbOX0vRUgh+dc0l5Atk32hOMGu2SJVXaBWJq9iL'
    'iB0HpWsqVo6ERndmFN4nSODk8gVxN7rktzIXxgdqr6haTwOY5M4FZ8FtLK20A1xzqyk7GiikdHoeoXF3eeVJ90Iz'
    'flXzprcmEv8AjPzS/wAzX01odh9nutxHVGFfLniA4F+B/el/ma58Qmoq51Yfdml8OjnR7c+x/mateNT/AMTQ+vkx'
    '/wAqz/hswOi230/qau+NWA1M/wDXGP8AlXHiX+5R1YZfvmfPOrN/xU9oPZv519D+HyfsKfhXzpqxz4ntPo386+if'
    'D3/HigHpXBhn77PQxC9xHtPg3m0mz/f/AKV2e2uL8FnNrP8A7/8ASu4HSvUR5ktypcL+5bNec3RxOwr0y4/1TV5j'
    'ej/SX+tD3HHYrE13vg8jy/8AgRrgTXdeE+Bj3NOOjQSWh3FwyiM5rzvWZeTj1r0KePehFcbqliWyQKuRnHY4ZiTz'
    'Sq3arMlq6nbgmp4bBmHSjmKsQRKScitKJCOtNW2aE8jitOAIyjNO5PKVzDuHFVZLcDpWu6gdKoysM0JifmSeH4yN'
    'dsfaYfyNWNcz/ad2P+mz/wA6doODrdkR/wA9R/I0zXRnU7s/9Nn/AJ16+B+BnmYxe8jCJOacGqM8UdOa6mc9yTPN'
    'S7qgBwakFIFuTA07OelRg04HNTcEiVSTUwAHWoF61OPXFIFuL1pc033FKKBko55p496jXIp2c/SgZKOKkDVF2p4P'
    'akBMD+FPH1qAZp4NO4E9L9aYCMU6qQmSdaU00HmlzQmAhPFAPOaT60HmqRA4tScU3FOA5q0yReaPr1pdwpM8U0xB'
    'RS+1FUIMccU4cUnSloJkhT7UlHenYzTJsNHvS8dKcBmnbSf/ANVArDRg96cF71KsR71bht2kbailifSjmBIrKtXb'
    'e0luG2xLn37CtSPTYrdRJetj/YHWia/ITybZRFH7dfxNQ6hooW1Y9Y7TT+XxLKO3YVn3N5LcNmQ8dgOgqB3JqA57'
    '1K7sblpZCs2fpUe6g9aTFXczF4ph5NLzRimAn1oFDCkpXFYWk5pwXinhQKLiZHtpQoFW4raa4OI1yB1Y8AfU1Dca'
    'lp2lgrHi7uB/37U/1qXO24tld7E626pF9pvHEMA/ibqfYCub1TxEZUNppqmCDozfxv8AU9s1lX+o3eoSmW5csey9'
    'FH0FZhBzxXPKo2Yzq3VojG5qLFWMcc1GVzUnM0Q+1N21OV5pMUyWiEg00jNWCuabt9KLE8pXxRsqxtpCKaQ7Ir7R'
    'TdWyNQmB6AgD6ADFWCvFM1dM6jOf9ofyFawRnP4DJxmmFKnK4FOCg1rFWMeUq47U7AqyIwasQafc3OTEnyjqx4Uf'
    'UmqFyyvoZ5QYphUAZNbwi0u0G2ctdOeDsO1VHse5qNtOjnBk06Tzh3jbiVfw7/UVSL5L6Lcw8UpXirRhYMQwII6g'
    '8Y+tN8uqI5WQhe1Oxj2qXbikK9aLCsdtpd6sWtTA9H25/FBn9a7r6V47NObbW3OccR/+i1r0bTdRWaJUc/Q/0onH'
    'ZnsYOre8X3NwEdKQnFQFjSbjjNRY7blpX5q3EwrLEh9KlSU0NDTOigmXaYpOUP6H1qvc25XryD0I6GqCTEVoRXWB'
    '5b/Mh6g9vpU2NDJljqmykGuhkthIN8HzDuO4+tZcsWCeKaZnKJnYNUNQsLXU7Y214gdD09QfUVqsh7VEUNUmZSit'
    'meF+IfBt5p+Z7VTPBnqo+ZfqP615lcaa5Zjzn37V9fbcjnmud1TwjpOq5cxeTKf404z9RXPXpXXunnVcvTd4fcfK'
    'UOkEEsRkjleOPqa1otIDr+9Gcj6Zr2afwHe2zZRRKg/iX+opkXh4RMNycjsa+XxcJxfvIulhGt0eQx+GEdRuXOOn'
    'FX28Lxx2cMewkfvG6dy3/wBavbrTw+rfdTr6CtO58NMsKkxkBQe3vmvNdNtNnXHDI+YrjwzZptMkO5hz0rPk8ORz'
    'AxpAPm4Ax2r3DVdLaBSdoyK821Z9QWN44Bt9wcGvPlF7GqorseVa98PI724h+23yQlzsVeoUV5m/hXTpra5gkvIo'
    'DFOUSRgTv2cfKB2Nen6xb61fyh5ATgYwK85v9F1hMssErBCSAFJ5PWuqjOcUlFkSow5ruFzz2x8IQ32pX0F/I0Ec'
    'DFEaIBjJKP4QPTHNc34y0W28P7RbTrPGJFTI4kUMufmA9+mK6/VNL1+R7hrS3nWXz1kDKrA4K4NQP4MZLN9Q1OGV'
    '94RAJsrmR2wMZ6kDmvWVRys29OxnWw8EuSEde54ddTNqE5W1iY7FJz3IHvV3TTdWBS9kBAGdy5wSvQj6Gu5vdB1L'
    'zJTZWZWIEhdmB8oOKxIdLvJmeO+WWNgxVQqZOB1LHtXp0vZKHvHHHCJe9JnV+Ftcs7nxNp19cQxwLDISShPO5SBn'
    'Nep+N/GP2a1E1tsTbEiKx5HGc9O9eLaNpGn6ZMt7czySRQnd5RT7x7Dj9RXSXGp6JrenXWmYlNwVaSIlPulcHAx/'
    'DjtWFStzWo0Lpd/+HNEnZpPU5GbxLcS3j3Z5aZUBfH93+VYpnN5qk1wvzGVI1PuFBrb/AOEWLOgmnZeAdoRh8ufU'
    '8Zq7d+GoboKNAkS1lhRVn8xjhmxwwJHU96uGFcU7y1Y17Tk5bnOM91HeotsVDhQCzDJC5yAK0fD73D6zJIEQgRsJ'
    'GfsCRyPfNdXa+CbVbeKa+1SNLkKTJt5XOex+lKvg7TYlEo1qISM6sAoOAgznd9e1ZVcPTdNxW/odNLEYiElKT09U'
    'd54U8QJ4Yee9llRDMEjLY3ZC5c4966vxj4msdb0eHWoDujRHxu7HcODXkskWnCRLCN1uIjGc4Yly+OSPoOK5fW9V'
    '1fTrQaVb2zCyP3fMU/MM5rXBUJxjy3JxGLqTbZfv3iukNxHjpg46cA1itcf2eC2R5jjGwjPRQcVXtb3VXtoo7S1e'
    'RZWZjsTODnAXP613umeBdV8Q6et1I4g/euxjljIYN069xiu+GHcoqM2c1GrNPR6nEeHJP+JTfo/Bc5/Na1YUHmae'
    'GydigD6bmru7X4bXVlbSwrcRnzCOx4xxinp4H1FJICGRhCBk8jOCSat4RNyff/I9CniHFJPoU/C1uFv45c7SsM5z'
    '6fuzWlCw/t/TnHQZz7/IKpR6NrtnN/o0YY+WyH0+cYNQQpfw6rBPLC2yD5W4PXgU6eEs+axyYjFNrlR7dbhHAIrZ'
    'EcaJv4BwDz06Vwttr0VtaPNcRn5cbR0JJ7c1e1HxJp7adCQC4uIsuoP3QRggkd61do/EYxrpJ6nItrl6Lh5ZJYxL'
    '+9jJ4wQr9qrLq/2SK5UsXaaRmynclQKyX0m2mjExkZELnavUgMf6VsxaLarEYBOSxO9mIHGaSoYZ7HJHF1lsyxpu'
    's/ZtOgsnUkrGOnuT2/GtzwSrDTp1bj/SpT/KuZ+yW1s6zI/nNsCqCcDjgHFJaajqVnD/AKCMZLHJ5GWPPFaUqcaX'
    'M11Jli5ya53sdbfXUVpezkgkt5YAHspNeZa5eRy6q1yV4ZIzgj5iMdDXQzyanfSCdQFlOFbPAI9RUTeGZ76cTXDq'
    'rlRux0wOlEoyqXjJaGFScp6I5lore+JZV2yHGMdMelbdj4H1S/h3rEwilBCNjjcASD+Y61asNLEU8WE+YN36fLzz'
    'Xo0Wt3SoYY2AZVCgDoACcED8TXJXvQcYQQqcYN3qfgeYaXYTWs15qd7Y+fbQ/LclmCgTMm0DHUnd0Fd54d+F73WL'
    'm5dlniRZGDj5Fkl+ZVAPXA61yQ+1z6yzThmRLg3br/A7jlcjoQDzivUU8a64UYnBwP4Uxz2qa9dxdkXD2N/fWxWf'
    'QJLu7l0aBP7RckBnkG0Qc/Nl/wAOMcippvhcuo3cVjJcM0duuJtqgYyuUOf4iTn8K6jS9eisYLaO1TAIV5iw+aR2'
    '5csfXPArvRrenANIjbWPXjrgetOFW5p7KlLc8ft/g28L3EfmqqoV8iQ9W5BOR29K7Wz8B2NrqCXEqLLH5W0g9fM/'
    'vfjXXW+v2cqgSNtPp1rQW/sZFyJFGTjmtOfzKjh6S+EhitIoI1iiUKqjAA6VJ5eKlVhK22D5yf7vNX0sipU3TYz/'
    'AAL1/E9qpa7G3LfYylhkkbagLGrQsY4m3z4dv7vb8TWuNqr5cShE9B1P1NRPGGGD0raMEtx8ljPnUuFPoRj0H0pq'
    'xgqD3qzLH0HuKYBgY9K2E0UpIlI5xTQ6AhSQOwp964gt3kzggYH1PSvPJ5bpJRlmzncDn9a0hFy6mFWqqb2O5vby'
    'CyQM3zM3RRVWz1i1upFhwUZjgZ6E+lZMFjLqSGeaba4X+L09hXMSSPBIWjJDKeCPUd6uEE7x6mVWvKNpW0Z6uYsd'
    'TVdwAOOa83g1zWi+xJt3pu/xrq7bVg8QW4YLIF5Jwcn8KidNx0ZrTrxqK6Rg62JTcOEO3bg8dc461h/2vfWfIO/J'
    'H3q7BlN1GbiVcs3Xb7Vx+sQbZCAOh/pWlKSb5WcmIpyS54s3rDxDbXsy20iGORuhPTNbzIMeteSFNpDDIIPHsa7P'
    'Stcj3raTM7lyApbscdPpW06dtYmdHE392ozedSPpVeRM8g1oHBNQvF6Vjc65RuZTpVZ0BNarxgdarMvqKpTMZUzK'
    'dKquprWePt61VaPPUVopoylTZ//S/evAp3FAOKOnSgo4rxtxY2nvdRiu3jX5R9BXDeOeNPtD/wBPcf8AOuxaUJEC'
    'eOBWSfvy+RcvhQ6WUR96y5L6Jm8vIOa5zW9aEAKKea4Ma7N528txmsKmIs7IuFPTU9H1TT47mPfjn1rnI7eK3Usc'
    'ZFWofEMcloVJ+bFc29y8spL8KTWEpRvdGiT6nQabd+bfeWOgVv5V8l+IW+TUPXdL/M19U6P5Rv1EZydj/wAq+UvE'
    'CHZqGf70v8zXLiW+VHThd2XvhoxOi2/Xof5mr/jNs6of+uKfyrP+GY/4klv9D/OrnjM/8TNh/wBMU/lXHif4KOzD'
    'fxmfP2rf8jNa/Rv519DeHj/oK/SvnfVWH/CSWo9m/nX0H4d/48kHsK87DP3z0K/wI9v8EnNrOP8Ab/pXdiuB8EnF'
    'tP8A74/lXeKa9SOx5dTcZcf6lq8wvDi5f616dcH9y30ry69b/SXHvTe4Q2IdwzXbeEs559TXCFsV2/hA5P4mmt0O'
    'S0PS9oPFU7m0WUdKug0481u1c5k7HJvpCFiSKnj0tFHTFdHtU9qdtAU1PKV7Q469skRelcpMzQuQDXa6vOIwQa86'
    'vLtWc881NtbF9C419xjNQiUyHrWWD3JqxDJ82DVWsSdZ4ejP9sWbY/5aj+Rpuuxn+0rs/wDTV/51b8NuDqdr/wBd'
    'P6Gp9ZQG+uf+ujfzr08HL3GcOLXvI4tuOtIDnpVuaLnNViMcdK7LnG9xvOalB9KjzTx2oAlFOqNak681Ax4/WpkN'
    'QjFSA88UgJM54NLTQaePagQ4HBqQVGKeD3plEn1pwptKBg5NIRIM1IOtQipaBj+1PHSmcHpT/pVJgPFOFNp3pTEw'
    '+lLij2pcEUyRgz3pe9LijvzTQgxR0PHNGaQA9qoVhQSDzQM/nTguRxUgXHvTuSxmPrTwtPCE1MkRNHMJorhfapBG'
    'c9KvJbnqavQ2TynEa5/lSdRAoGQkJNWorZ5G2xqWPtW+mnwQc3T5P91f61I135Y8u2URr7dah1C1SKkemJEBJeuE'
    'H90dae14kS7LNAg/vH7xqtJvc5Y5NQlSOtTz3K5bbDXldyWckmq7HNWNmaZ5RNUpGdmVjzxTSverPlgUhTFVzCaZ'
    'W20BfWrGypFidvuqT+FHOS0+xU2dsUhXtitRbK5fpGR9eKU2XljM8scY92H8qfOHKzL2cdKQLzirMl5otv8A6ydp'
    'mHaMcfnWdL4jjjyLC2VP9p/mNQ6iRDcVuzQjsriQbsbE7s/yj9ainvtKsOGY3Uo/hT7g+prmLvUr29P+kSsw9Og/'
    'Ksw1m6rexm6v8qNm/wBcvLweWGEUX9yPgfj61hGn4PagjioMZNvVkBU0mDVjHGKaQOnSnYmxX29jTcYFWdopm2qJ'
    '5SHaTTdhqxso2CgViuQaAKsbaNtWTYr7aaUzVnbmk20WFYrbe1Gpr/xMJs/3h/IVa2cVFqSf6dMevP8AQVrFESXu'
    'mUYxilhtbi5cJAhb1PQD6mpgtalpeSW8TwAK8MuN6N0bHT6VaViIxTepDHDY2J/fkXUw/hU/u1Pue/4Ulxez3SiN'
    'mAQdEX5VH4Cnvp1veB3s38lkAZo5D8oGccN9fWqrhtOcI0JaTs8n3f8AgIHBp2KldLshE0y6uAWjT5VGcscA+wzj'
    'NZpSaGXBDRupyOxH0NaUk1xdENcOW9B2H0FXI7xkTy5UWdegVxn8j1qtSOWL20KiXYm+XUY/NB48wcSD8e/40S6a'
    'dvm2T/aI/bhx9V6/lW0ulw3LROzG1WU/6t+W9flA6j61WGoQWZI0yIowyPOflz24HQUX7GnL/O/8znthxzSFflOP'
    'SrhHUnvUTAkGqMWjK15mj1mX2Ef/AKLWtrSr8hVBNY3iNP8Aicz/AO7F/wCi1qtZyFCF6YNbtXih05ONVnrNrqCl'
    'QrncPXuP/rVrBgwypyK8uS/aMjBxXQ2GrDoDgnqOxrBo9WFZPQ67caUMepqlDdxSABjtY+vT86tGg6FIspJg1Osx'
    'zWaMGpVYjvU2Hc2Yp2Q7lOD7Vd82GYYmHP8AeHWsBZOOanWapaLUjTexyC0LBx7dfyqi8BHGMfWpY7jaQQ2KuC8D'
    '8TqHHr0NQ20OyZliLmpkh46VohLWTmN9p9G/xqQ20ijOMj1BzWcpMFTK0SDPFTNpdrdHMkak+oGDUqR4OamdnSN/'
    'L+9tbH1wcVy1LNe8rmqRxt3OLaVrXTzhUJBfqSfT6CsyfUtVtMeY7FT2ccEVBpl2gvYvtPCbxvz9ea7HxY9hPpo2'
    'uhkyDHtxnHf8MV8peVanUrQnbl6Hnwk6ilK9rHnupCG+gFwi4JOGX0auEv8ATd2TjH0FeseGbEXE1xFOoePYpwfX'
    'PFbd14U024BK5iPt0/KnRwVXEUlVVtTuoPmgmz5eurG5H+q3DnrgVhXNlfKjKZWGfTGa+h9U8C3Rz9klWQeh+U15'
    '5qPg/Vo2YNEVx3xkfpWby2ut4mrdup4tLZalEcR3LDP0rmdY0G71dUS9undYm3oOBtb1Fewz+DtSmY7d2fYVX/4Q'
    'LWCvJA/3q1jluJ3iZSd1Y8HXwbfRDZbahJGo6KQp/mKQ+FdSiyftgdicliig/wAq90fwFqeMG5RM9cc1XHw3vJDh'
    '9SwPYVo8qxct5GSiux4sNFlC7ZxE3v5a/wCFUx4VhM3nJHDG5/iCgHFe/wAHwrsOftOoztnkhcCtq2+HvhWzwzxy'
    'Tn/po5OfwrSOSYhrWoHJ/dPnWPTEt0y06MFOPuqefSp0020mOLi2EofjiPnn3Ar6Zj0Lw7bjbHp8IGc/dBP61ejN'
    'nb48i3RcdMKBitY5JUjvVZapxe58p3XgCxvsqunXIB/uo2D+lZw+BL3oD20F5ED68fzr7KGurboZbgpDGn3ndgqg'
    'e5OB+tTWPjDSr/nTr23utvXyZEf9Ac11UssqRelaREsNRfxRTPjq3/Zx1HcJIri4hcdCRnFdMv7O2oyWyJd33mkc'
    'ASZGPpX0fqvje0spobWefy3uWKRk4C7gM4LdBkdKyLrxFbxoZri7jjQcl3kVVH1JOBXZTwc9pVX+Bk8NQW0PxZ4Z'
    'ZfAbWNJytnfxpGTuK9Rn1rqtO+HN7aRsl/OJWz8pTIGMd66y08Z6BqE/2ex1qxuJc42R3UbNn0xmusitdRnG5eh6'
    'Eng/jXbRw7hqp3IVGlHaLPOR4DiXuSc9SaefAccnb/x6u9ubLVVHysq/jWN9n1wFv3q4KkD1B7EV03a6g4R25Wcj'
    'e+B9Ms1DXNwsBYZGX5/KuA1PTdHsiPs0s1xk4PlgYH5+td5d+Fb66k8y4nldz1LHNUZvBl3t/dy5+uRXLUrYhv3U'
    'cdSMm9IniHiHRjrUkQiS4RIVIAAHJPc4rCh8LXtsu0i4K5yPlFe7t4Z1iAZRQ2PQ1Xa21eI7XiPH61h7Wv8Aajc5'
    'JUbu8rnjkWkbGBdZzjsRVqPS2Ul1E2Txg167G1wjDzoOvqK0Iri3x89uPyFUq81/y7EqEH9o8Pi0HY24LNntntVy'
    'LSHVfLCS464r3BJ9OJw0IH4Cr8a6M+Mpj8Kr63PrEFhY9JI8Rg0UsVLxvkc8txWtDpALAlAT/tMa9ojs9El6EAn1'
    'pzaLpzf6srn2NH1ySK+qPueUNpkgA8uOEHue9TRWE0I3iOJm9cc16U2gWp5pyeH7duM/rSeJ5tZB7CSZ5bpiMt5c'
    'rPErxx9FwOp5612NnbabOgPkqnPINdCvhhNxMKkluuB1/Knt4VnA3S7YlHd2AP5daJWm7pBGnJbq5RFhYqPlhWp4'
    '7ezyF8kVrwWun264lnecj+FV2j/vo1Y+1rEuLSJIj64ycf7xq1Qky7xIYvD4uU8wQrGv95vlpZtDsLZRK5MpH8Kn'
    'A/PrVo3k9xH5ZXB9jyauWluFw9xz6D/GtFSSDR7IWyilSMMgEEZHCKME/U9aunintIjDAqEkD6VpY0SsScetGRjr'
    'WNcTeX5pDAkjI/HisYX9wiNGH4PHP9KuNO5Eqqi7HQXN2qOFXBGCTjtiuUe7nFy1xGzBR8xB/lTCxDbsnkGq7n7w'
    '6CtoxsctSo2WWvZplZZsyBh2rPljjZQ21ge7UgldBhSRxS/bbiMYDZHoea0SZm5JrUfB5BAj3OHGR9ayprMshZDk'
    'k8r3pTPcmUAFie2Knha7lkdSWXyyM8etNe7rczdpqzRhPazfMoUhlAOPY1VW2uM8A8DNdZMP3txIOD5Y/lWDJK6g'
    'MGPCkH6GtbtnPyJM39Fuo3j+zSlsgFs57elX7uztLi1dIt3mAEoxI+YiuMspwkxx/wA8zWjb6soi5U9++cZ9KxlS'
    '1ujrhXXJaRmNaupDsuASRn1IpChj+eMAMvKn0IrVmuIjaxAn+Jj/AEFTgQyrtaMKQOo78elaOTRyqitkzI0fVr6a'
    '+ijuZCyscGuzuryC32hmBLHAAOSa88W1eMGdTwATkVSaSWORZd3zLyParlTjJ6Dp15Uo2lqeoYDCoGSua0LWGnla'
    'GY5BGck9CP8AGuqLKea5pwcXZnZTqxqR5olYoCKqug7Vf4PSq0iZpJikj//T/ev3petFJ+FIs4rxzzp9rj/n7j/n'
    'XS3QbycD+6K5bx2+3T7Un/n7i/nXaHbIgBHYVileUr+Rf2UeK6+kizNuziuTLcnNeza3pC3CEgc15Xd2DxSlCO9e'
    'dVg4yNk7q6JNIgknuAuTj0rsdR0hks96DkDNL4Y0zGJGHNd5c26GAqw7VrTpXiDnY8s8GiRtXdZTkrG9fNviQgJq'
    'H+9L/M19WadbGz1sugwrq4/SvkfxFP8Au9Qz13S/zNceI0ikdOGWrND4aMDo1uD7/wAzVrx2dusMo6eTH+orN+GT'
    '7tFtj9f51c8dvnW2/wCuEQ/8drkxL/co7cMv3z+Z4BqZz4ltf+Bfzr6K8Oj/AEJfoK+dNTx/wklqR6N/Ovo3w0c2'
    'afQVwYf4zvrv3D2jwUcW83+8K7rOK4XwaP3E2P7wruM8c9q9NbHmTWoydv3LfSvML5h9pf616ZPnym+leXX5/wBI'
    'f60PcILQqs1d14QcKDn+8a4HnNdd4duPJ6epp+Y2etBhTxIOnSuZfVkVeWqpJrqL0atVNGHsztMrTHfahriV8Qpu'
    '5PetFNXjlXGetNTQvZMytdkY5xXAmKR2JPevRriJbxuOaSPQh1K1OtzR2PP1t5O4pWVkr0Y6OMYxWPeaUqjIFO7Q'
    'rJlHwzO/9tWSn/nqP5GtrVZf+JhdA/8APV/51laFbeVrtke3nD+RqfWJMapdj/ps/wDOvUwavBnnYv4kVHAbmqjx'
    'Gp1kB4qUKGroOZmcY+4oC1fZB0xUDKKq4tiHGOKcKUjvSdOaQdB1PFMFKOeKQEy1KKrg46VKpzQJolHvUo6VCDT8'
    '0DuS5opm70pwoAeDzUq1EOtSLQMk69Kcppo5+lPC4oAePepBUfSngVaYh2KdzTRT/egljTxzSdaXr+NSKmaq4mMC'
    '+tSCOpVSrEcJNS5BYrCOp0hJ6Vox2w645rVt9OklHC7R6mpc+w1HQxEtuea1INNlk5C4X1NbYgs7Jd8pGR3b/Cs6'
    '416xTIXdMR6cColNR+JlWRMtpbQnnMreg6VY/wBIYbUTYvtxXL3HiO5YEQKsY+mTWJPqt9N9+ZyD74rCWJj0FzJH'
    'cyQqvM0qJ9WqlJcaVGf3l0pP+yM1wTzMxyzE/U5qAtk+1R7dvZEOody+q6Kn/LSR/oKhOuaUp4ikb68VxXFNzxT9'
    'rIj2rOyPiHT16WrH6tUJ8SWo+7ZA/Vq5LrTCOar2k+5nKtLodW3iiP8Ahs0/EmmHxQ/VbSIVyxFNxR7SXch1Z9zp'
    'T4pvj9yKJfotV28R6q3AlC/7qgVh4/OjFUpS7k88n1L8mqahPnzLhz+NVDI7ffYk+5pmMUo9qpC3A00CpMZpMc4q'
    'kieVEeKAnORUm05xS7TnrTsKxDtoINTFaTaDTSCxCVo21MV6UpWnYlog20mw4qzt5pNtVYVirtHpS7OelWNozSgU'
    '7C5SsY6AuKs7PWk2ZNVYXKittFLszU+wDrS7aaQ+XuVtvao9SX/Tpv8Ae/oKu7Kg1Jc302OPm/oKuJEl7pllc9qZ'
    'hgRjirHlkUbSeaszsS2+TbXYPeJR+biooZpYRsJ8xD1R/mX9elXrPyQs0MzFBKgUMBnBDA81JJpcyJ5qYlj/AL8f'
    'I/HuKY+RtJorxjT7hud1qe4+8p+lTG5gtwVs48H/AJ6Py5+nYVQKbc4pEhmnbZCpY+1NITk1p1NGxdX1CF5CSd+S'
    'Tz2NYzqNx28jPBrWhhis5klnl3OufkTkDII5P41m7DjBpoUk7WINpNO8vINWFTFOKEg8UC5TD8QKP7WmI54j/wDR'
    'a1kJlTu9K3ddGdUl+kf/AKAtY23JrZPRGc4+8xzsQalhmZWyDTQu5ce1N2FaRave5vW+pOuATkehrettVwMBuPRu'
    'lcMAQeKeJHHGalxOiNZo9RhvopPv/IfXqPzq8MHkHI9q8thvposYY/Stu21orxnafb/CpszpjiE9zut1ODGsG21h'
    'JeG5914P5VqR3EMv3GBPoeDUs3jJF9Xz3qwjc1n9KmRyKlq5aZqI2OKvQzMvCkg1ko9WkbiuecWaJm6k5biQBvfv'
    'U2I25GVrIjk96uJIaxd+pqjldW8MSvO1zpxUhzlk6EHvisiPw7qsrhZEMY9WPFelAhuTUgcqMA/nXkVcnw85uequ'
    'c8sHBy5jJ0zTotMt/LQ7nY5dvU/4VbdhVlpE/iUH6VCywv8Adfb7GvSpUY04qENkdUYqKsjOlPHFUXGa1ZLaTBKj'
    'cPbms91wcEYreKtuQzKmtYJfvoDn8P5VkT6FbPny2ZM/jXRMO1QsK3VmRJ2OGu/D14ObfY4+uDXPz6VqUH+siYD1'
    'Az/KvVMGmNkdavkRk2+542yyxkh8/wAqpSylc5wMepr2Ke1tZ+Jolb6isWfwxpM5J8rYT/dNPkM5udtDy9ps4Ocf'
    'jXOaz4u0jRMw3E6PdbQywBgGO47V4/2icAdTXql/4Tt7a3lulnCxwo0j7x0VAWPP0Ffj58W/GF1oviXTvFOpNLco'
    'Znu53hJ+QXTSpFtH/TIKoGeh9687Ma06dP8AdL3nsdWXUlVq/vnoir+1H8VvGF14o+zCUrZJKttZ6bE7GNjsV3kk'
    'C8sxLAY7Zr5A0/xJ8UEa58TaTfXGnw6NJHDJMsjRt5jy4OQDhmHVhjha7HS/EXjfxV4nm161SPZY3738V5cACKFn'
    'Xy2BZ+CCApx2IrmPHPjm2tpbvRba6S7ivSZLiKwTZAJjw7AnkkgDJryqE6zag9ZdX/Xke7WpUlea0j0R67qXxB+J'
    'uu6fcv438Wyf2fYQx3U8ERCu9xJGTBFE465JBJHQE1x2jb/FNvP/AGz4ou3t7CxF3cI0z7ZZGV5CqKTyqKoDH+82'
    'K+edQu9Y0y3htbhX8u+i3xwSklymdiMR1GTwp/KuV0zX9Wt5XEY3xR7o2AJwATypPpXbHAzmnJ1DneLpwtFU9D6G'
    '1XxLYeHnNroChpE2L5+W3M5QO7LgjCruAHrWp4P/AGrfjd8PbpDoXiGae1Rsm0u2+0QsB1Uh8kD6Gvli41eZ5GZm'
    'ZQwKYznAPTn2qktwSNhO3rvPc46AV6NDBRgtNzz6+KlN+8fux8HP25vDvxGuF0jxHYDT78oCWgfcmR94lGwffjtX'
    '2raavb3sEd1BtlhmQPHIhDK6MMhgR1Br+WrTbnyJFmtyYpAcqyMVce+4c1+jP7LP7Tb+FrN/CPi/UpZbC2ijNvHP'
    'lzzKRMYn/h2owcKeDhhWrXLucs72vE/Yf7Za91IppuLZunH1rjLSddUs4dS0qZLu0uF3w3ELB45FPdWHH+FXFtL1'
    '+zfnQcP1p7cp0f7h+mDR9jtnHKA5rCh07UHztjc454FaNrpGtSZaCOY/8BOP1ougVW/2Sd9Is2H3AKy7jw7YydOP'
    'pxXQLpmpx8XM0MJ9HYFvyHNaNrpJeXZczgKATuVe/oMmq0sU+WWljzx/CURbMbkex5qjP4ZniGUIOPQ17KLfTLZw'
    'siSyDu2QB+lOuLzTYbWWSzhg82NhtEuWLA9wOlKy7Eyo0jwkaVebgiI5J9ATWzaaBqrkFreQg9yCv6mutuda1GXP'
    'KxjsI1C4rJk1G/cBJ55HA6AscCh0ovocslCL6k50CS1YC8mCcZ2qd7fpxVkm0ssFIg59ZG4/IVSSVnXhqY6s3DDN'
    'KNGEegOpp7qNN9TuZIfKjYRgZwEG3r+v61isJM5m+Zj3zmrKKQuB2qZIJJjhFJ+lXZIzk3PcyvL56daVY8nA4HvW'
    'wNOlU/OvFSfZWUY2jFHNqJUn1RSjMcX3Tz61J5oPep/srk8IDViPTJpBxHihzitzVUpvRIyndhna2PTmql3dyBTG'
    'mTkYJrozoh/5auEH5mpk0a1I53Pj14FR9Ypo1WDqvyOA81hyVyelMEckhJCnn0r0P+ybAHICZ/Oh7OWMfuGX8ABS'
    '+txb0QPL5W1Zwqafdyfdib8RipRo1yVwwCnvlhXUzW02xjczbR9c1RtoU3Hy8u3q3QCm8Q7XQlhIrSSZhHRGAyzI'
    'o6dasReHomwZX/LmukjtkX5m+ZvU/wBKlxg4rGWJnsmaxwdPexnw6VaQqfLQBsEbjyRxT7XSba1RVBZsEls4+Ynr'
    'mtFR3pc9q53Uk92dKpRWyMq/0PTbsl0Y27uuxsDKn3xXFX3gyeJHW1uUmJBADAqa9GbpxWdcu0T7z82Fzt9cGtoY'
    'mrHSLMauDoz1lE8TfT7/AE6Z/t0TRfIVBPQk+hplj5SkC5yV77a+gmtLa6hEVzGssZAO1hnr6Vzl54P0GUN5O61f'
    '25XP0rrhmEZaT0PPq5NOOtJ3XmeYTy2RYLCCEX7ufeg3CkBkbBHvV3UdGSwm8szqwPQgMQfxHFYU8ccfBlQV1wnC'
    'WzPPqUqkL80Se3ljhiaGZgw9j2qpIljI3DYXHrTVghk6TKc+lP8Ascf97Napo5pKT3RRMUdu5MDbge+as3mqXU1q'
    'sS8OpHIPXFTfZYsZxmo2tkP8NNyT3JUHFO3U09P1+KO0AvmPmKccDOR2p7+JtM7lvyrCe1Qfw/pVGS2T+4PypckH'
    'qV7aolY//9T9b/8AhaOs9fIjo/4WlrA/5YRfrXZj4a6AT1l/OnD4Z+Hv+mv/AH1XmOnif5j0faUOx5prfjXUddgi'
    'gmRI1ilWUFe5XpWifiXra8CKI4GK7h/hvoCkbfM/76qC58AaJEhKK5Pual0sRq7j9pR2SON/4WVq7jEkMVY134wu'
    'JWMjQRbq6O48NaXAxUxt+daGm+DtDvuJo2/OsuWs9LjU6PY4mD4iavbcQxwqB7VpD4pa6y4kSE/8Brtp/hpoSqTG'
    'jZ+tc+PA2mwXGyWIlCfU0ezxEXqxc9J9Dlbr4j6qTvjjhRh0IFeF66yPa3TMeXDsfqeTX094r8B6SmhNJpcWy4LK'
    'AxJPHevlrVoHSxnjY5KB1P4ZrDERmviN6Dg/hNL4aNs0W3X6/wA6veMzv1Z2/wCmSfyrE8AM0ej2/wBD/Or3imfd'
    'fsT18tP5Vy1rOikdOH/itnieqN/xUdqfZq+ifDLf6EmfQV83ao//ABUVsfZq+iPC75tUGewrhoaTO6t8B7h4PbEM'
    '3+8K7sMCK8w8O36WhaN/4zXosFxHKuQRXoJ9Dz5rqiacfum+leW3/Fy/1r1Ccjym+leW35H2uQD1q92THYpGun8P'
    'xGQ4965bdzXb+ExuY/71NoovahZyIpK5rjpvNVyGJBr2K6thJGQa8+1ew2sWAoejJTujmA7+pq7b3ckbYJJFUeVN'
    'OFUkSei6Ncq+NxrvYPLdBxmvFNPvTbuMnivQtO1dGUAmri7aMmSvsda8abT2rnb8RgGrkt+hTrXLajfr0BpzkmTC'
    'LW5LpgQ61aY5Pmj+RrF1w/8AE0vP+uz/AM6k0K58zXrJPWUfyNJrsR/tO7I/57P/ADr08DpTZwYx++jGjcg1cV+9'
    'UMYNODYrraOVmp5mRTG571TWTsalDkipaC9x5FMxS5z0pOtCBCcdqcB3pPanLxzQwY4Uo4PWk96VeaQPYmX3p+cV'
    'EDT/AK0CRLmlB7VEOvpTxyaB+ROMDrUgGaiXGOalWgZKvSpAaiyBTh7UASg4NOB55qMZp4zTAk5FP68CmDmpkQ9u'
    'KaZLQipkYq1HExqaKHOK3LXT5nGW+RPU8VNwsZkdv0yK2LbTpZOSNo9TWmkdpaR+a5GB/E39BXP3+uvLmK2+ROme'
    '5/wrOc4xV5D2NWSbT9PHzt5kg7Dmsa78QXMg2w4iX261z8k+TzzVNpMnNckq83otEJstzXMkh3SMWPvzVRn9KjLU'
    'wkZrLlIb7jmYnIqMnNBJphOK0UTOTGGgUH2owaqxNxDRj2opccVdiLDDRyakC5pNuDiqsFiPApdoNOxRtAq0ibDc'
    'A0Yz9KdinbadhWIwuKXH4VLtoKirUQIsd6Xv0p2KD6k1XKL0EA9eKSo2nRRxyfaqcl1J0QAVpGk2ZyqRW7L+DTtp'
    'rCaaZurmoWkkzw7fnXRHD36mDxKXQ6LBHFOxkZrmRcXCdJGq3FqU68PhvrVvCS6CWKj1RtbaNtVYr+F+JMofzFXw'
    'FcbkbcD3FYypOO6N4VIy+FkYWnhfWn7eaXHSpsWMZc9BTMdqnK8UmPanYTRBjFLUu3PNIV4p2CxERUGpL/p02P73'
    '9BVwLUd+P9Mlz6j+QqkkRNaGVtNO28Cpio7U0jFMz5SLbjpTkmmiOYnZD7HFP2nGaTbQCRMb1nwZ4o5SOhIwfxx1'
    'qGW6nlG3Oxf7qDAo8vvRsxVA7vcrbDRggVOQaMDPNMXKQgZ7VJtFOA9qUjIwOTQFjG11P+JlKcdk/wDQBWRsrc1l'
    'g+ozFecFVP1VQDWaFzV30JlH3mQBcc4p+wNU2z0o2d6H3FYg2e1MZDVzbn2p2zjBo5h2MwqR0pMntVt021WK4OaV'
    'ybDopXj5BrUi1KQYDHNZI54PHvSlCppblxk1sdTBrMkRGHP0PIrct9djbiRevdf8K853MOtSLKw7mk0jaOIkj1u3'
    '1Gzm+7IAfQ8GtVGyMryK8XS7Zeta9rrE8P8Aq5GX2zx+VQ4XOiGIXU9ZRyOhq0kvTNcHa+I3OBMqt7jg1sxa5ZP9'
    '4lD71hKmdUKqfU61ZQeakM3HFYcNzHIN0Thh7GpjIelZezZtzmg04Ixmq5mFUzJkY6VEzZ5zVRpkuZfFyyn5WI+h'
    'p/289JQsg9xz+dZW7HOaZvArRQJczZ32MvUNEfUcimGyVxmCRH9s4NZPmDrSebznJq1Enmvui5LaTR/eQj8KostW'
    'Evp4xw5+h5qQ3qPxNEp9xwatXI0MsqaTb61on7HIflZkJ/vDIqJrWXrEyyD/AGTz+VNMGjC1Sw/tHTbuxzt+0wSR'
    'Z9C6lQa/Lr46/s/eOLy6+0eGI48WouJ18xgojglPmTQSK3yuEky8R7q2O1fqvIJVO1lKn3GK+Tv2p/HX/CK+E/7I'
    '89LabU4ZBHM5AXcAQqk9hnGfavPzWUIUJVJLVbep15bGcq8YR67+h+LvjLwvqD3uneDLS6e51N3NxesW2QRpICYo'
    '/LXA4RWkPc15uI/DOmaTq2pH9492tnHa7wN3knfJcuPQkwlf+BV2euy6lBqmoatfXMlrqL3kd2lwylo2CRhEQEdD'
    'GcqR0KmvmfV9SljuDaTMXiVm8uRfuhWJJXHp7V5eWU5VY2b7f5s9nMa0abukaeq+LrvW9X1LxBMq+fOzeWAPliVE'
    'Kwog7BARj6Vg6jcKNKsdPT5I4EG8LwGdzvZ3PUnkKPpWWrLHLIgOVk5U++MEUy/kbavHDFQ34V9HCjC6SR4DrSab'
    'b3AXEcaBSox2zyTUqWbXaGWNPLI9+vpVIQF5o3P8QJ/LpUl5dvBELe3YhpM9PQcVta2kTO/coRyy20xQ4zuwSfWu'
    'l07Vb/TbqPUdOcpNCc5U5x6gg8EHvXN3NubWzVH+aSVg2fp1/nirdizsdv3Zo/8Ax4DtUzV1ccXZ2P1O/Yd/aN1K'
    'w8d/8INrkkcGja6gCIT+5t79f9XMitxGs3+rdRxuKmv2W/tVYRiRQGHUCNK/lu+H3iX/AIRDxTZa6wV4IXC3KFdw'
    'MEvyy4H94KdyHswBr+hz4U+Nbbx58PtL8RxTi53q1u8w6SGE7Q/1ZcMazhbY5cXFxfOup7LP4nuUbECnHqdo/kKx'
    'LnXdVuFZHkcK2eAxH8sVVBB6U4pWlkcDnJ9TGAkVt5J3euefzqYTTNy7sfqSastFx61CyY5oM1oRNPMOFdh+JqAX'
    'M4Jw7fjzU3lknNJ5BNAO5JHdFuHAz61I7o3VQfpSJbHq3ArQjFrGuPLLt6k4FLbYau92ZkcEsjfulJ+lbNvZTMP3'
    '2F/nTWnkz8mFx2HFRNczMMFjj8qHqVFRXmaqWtvFyeT71pxPFEFGAob0GK5Lz5F6MalW/Zjtk5x0NZSptm0Kqjsj'
    'rDLbnOCKga5tQ21sGvMPHnjzTvAXhS/8Wamjy29ggZkj+8xZgqj25Iye1fnTrP7b+p3Wj6nbLZ+VdXQdbWSM7DbI'
    'Rwf9ps9DXDXq06cuVt3PTw9GtWjzQjofqWnjTwj/AG0/hpNTtP7WjUO1nvHnhSAQdnXoQa8v8c/tBfDnwJq0ei69'
    'qyRXUkTTbF+YKiqW5YcZODgdc1+HfjL4oa/r3iM+Oob6eHVZiWWVSY5B5aCIFHHoBz6mvHNR8favfQmPW7iW4dyc'
    'mQl5ADnnJ5Bzk1hGcp/DE9F4RQtzT+4/oy8JfGr4deNNGOu6Nrdubdd+9ZmEcq+Wu9so3PC88VBpPx4+FviPUhom'
    'k6/bSXb4EasdglJOP3bHAbnj61/OhZ+KNc0mCM6cbkRMrSb8lSUIwSOelSaf41uftUNxFI6SWpBjYtgpht2EI6c8'
    '1tyztdI55UI7cx/TjHISxZDnH41M80xGM1/P7o/7UfxMsPE8Piv+27mS9ilVmQyZgljUbfLeLpgjj9a/V74XftTe'
    'GfiBo0sl5FHDq1uqySWdm4ldoDGHeVVOCdhOGUc0PRXkjndGUdEz6GMs0tyEkJCMcc1u28aInHFc7oOu6T4l0+11'
    'vR5ku7K6USwTJ0Zen4EHgg9DXVCZMY2jiic7pWRlTpWbuxwTPFIYvQ003SA9MCs251SZVwiYycA9/rUJN7I2bUVq'
    'XyyIcMwBNKGjzjPPeuAk8QTtOoljRznaMjBFdJo10JArv/y1BJPoa2lQ5Y3ZzU8Spy5UbTkLznFc5qdwGnS3Ugb1'
    'Pzk8Dmulke2YbSciudvbWzubhI1G7Ixj0qIbl1k+XQvLqlrEqx+cvCjBJ644NVptYtMZaRD+NZX9gl2IIBAJAz6d'
    'apah4ZglUMj+TInORyCO+RTdGm+pH1mrb4Tndb1yXTrvztHuG2yHLwFQ8YPqM9PpWhPeeFNSsbebxPCbOaQbfOjG'
    'wFgM844zWja6FYyIske2YH+Icg1LrPhy31HRrmxaEOWQ7B0+YdCD61rG2iTMbSd20mn0OUf4faPdwrqeh6t51rIx'
    'VWAzhh/Ccd6xZ/CV/Axjtb6KYj+Hdtb8jTItF1/wvYC2sIbie2WUysquN25gBvAHPArXa6uNU23Fze2e5EC7ZCEd'
    'QOzY5z611QqTXW559ShRltCzOWubPxBpqlpo3CjuPmFZZ1e/Gfm5A6EV3kd1DFbNPdXiRxg7QyvuRvoDWBr+paLp'
    'awG9WOY3BGDGNrBTj5yPSuiNR9UcNXDNawlb1MVdaugmGUsfWmf2y/8Ay0Q16BbeENPvYVntrpdrjI/GopvA+Cf9'
    'LjA9war2sDP6rieiuf/V/d1Jlc8GrIbA4ri9N1JZD97NdZFIGXIOa54T5jaUbCXMmwqfWpmiWROfSs3U3ZFjIPet'
    'SPPlr9BVp6tCtpc5y/0iOZiQKp2llJaS/L0zXVzyIgy3FZLalZBtryLurKUYp3KTZsQ7XUbvSmTWkbfMQKghuYmG'
    '5GDD2qvqV80MJZfTircla7Fyu5Q1iJDaiIcjcP5V8M+IZAqXwHZ5f5mvr+11Ca+vTE/3cMfyFfG+ugsNQDf35f5m'
    'vKxUuazR34ZbkvgUbtBt39j/ADpPE5zet/uL/KtH4cQq2iQKRng/zNUPGC+Tqkkf/TNP5VwVl+7udlB/vDw3VM/8'
    'JDbE/wC1X0N4XJFsn0r541A58QWufevozwyv+ip9K4qa947qr907+FzjPQ10enapJCwV24rm4R8tWc8YHFeglocD'
    'Z6al+k0Jwe1efX5H2lz60QXksXy54qvM5kcvjk1STE32ISeea7rwg3zH/erhODXa+FX2sf8AepgepPjZzXMarbqy'
    'mt8S5FUruLeppy1M4nllxFslIqtgCusvNJd3LAHms06TKOoNCaKaMZa2NPllBwKVNKfcMjNdBY6aVAyKbl0Qra3K'
    '8t1Mic1z1zdSO2M8mu3vbEeX0rg7tDDKeKIhJmz4ZVjr1ix/56j+RrpdYg33tyT/AM9G/nXNeF5h/btiPWUD9DXS'
    '6ncL/aFyv/TVh+tethPgZ5mKtzI5aWEqTxUOytpgjkk0i227oK6rnK0YoUjipBwK1XtG9KoyRMp6UcwWsRD1FPqM'
    'ZzT89qATFpQcHim8UtILjyTjNKpqPNKM5oFfoSjNPXrTF9SaePWgVyQZp49aYPWnDtQUtSUHGKlU1AKlBoBEwOBT'
    '1qIe9SJzQBKozUyqcAClijJ96vw27SMERSzHsKVwIY4s81r2enzXJygwo6selaEOnQWiiS9OW7Rqc/nipZbt5QI4'
    'xsToFFDBFiOKzsuEHmyjv2FPubtIEE14ck/cjHf6+1UZrmLTY90uHnYfKnp7muVnuZbiQyyMWY1lVq8ui3G3Yt32'
    'ozXb7pDgDoo6AVkNIT0pWPrUJPFctr6szbELEmozTieeKYe/NNRE2Jz3ooNJjNUokCGmfWn7aTFVykjKOtOIxTeK'
    'rlJsFOHpTc+lAJzg1aiDJelNPJzS8UcmqSATH401utP20m3mnYljAakFHtRmrURDh+VI3FN3VE5J/CtYwIbsKz9c'
    'VXYljyafgnrQU71tGKWxjJtlVl9KgZcnmrjAnjHFQla2iYSRTaPFRlPWrpQ0zZmtkYOJRZD2pmMdqvmLnioih5ra'
    'MiHAr4PSpIriW3bcjY9u1KymoWBzVaNamdnF3TOktdQhn+SQ7H9+hrQIHUVxQQk9K0ra9uICFY71HY1zVMMt4HdR'
    'xXSZ0eM80m01XhvreXqwQ+h/xq5lSMqQRXM4taNHbGUXqmNA7UEUv40YzU2CwmAabcRG5UTR/wCsUBXXuQOAw/Dr'
    'Tyr9gfwoCyAggEH6GmkS10M0ofT9KaVIPIrZDy59/pVDV7qeCCBom2MzSA8dcYx2p2JcUlcq7W9D+VOEZPQGsY6j'
    'f/8APU/pQNQv+8zUWIvE2hE3ofyo8mT+6fyrHF/e/wDPZ/zo+2Xh6zP+dA7xNVreTqFP5VH9mm7IfyrN+13XeZ/z'
    'qM3NyePMY/jRZivE1xbzgcIaR5Y7EeZIQ0w+4nXB7Fvp6Vkh5m4MjY+pqBk5yefeqSJbtsQN8xLMck8kn1poUmmz'
    'ExqWPAHUmvk346/FHV9J0e7tdIuTp0EXE1wTtZgeNo789FVfmbtXnZpm9DBRXtNZPZLdno5Xk+Ix0mqekVu3sj0v'
    '4jfH34bfDFGTXdRE92o4tbX95KT6HHAr498Tf8FDLSzkdNA8L7kBO17qfkjtlV6V+efi2+1fW9YvL7VJJbS0tmzN'
    'Lc/6wE8gFeoduyfeHfFeP6zrEUg2WCGOM5Cl+ZHA/iPoK58Lia+I1k7eS6fM9TEZdhsNolzeb6/LsfppY/8ABRvx'
    'IbxUm8LWU0THGyOR9/4e9fbfwi/aY8F/FfSprhYJ9Gv7XHnWlypOcjOYmA+YDuOor+ejQfEreHbg6lbIr3oGIWf5'
    'ghJ5bHTjtXW6Z8VfG9l5stprFzbyvKJA0bbSGIwenr3rv5asfhd/U86dOlPTlt6H9LGma9pOuiT+y7mOcxHEiqfn'
    'Q+jKeRWqYT1r+drw3+0t8UfCviNvEVnqksk0hVZy5yWAxjd6iv1E+AH7anhb4iTReGfHrx6JrEpCW9zIdttcE9FZ'
    '+iMe2cA/Wqp1pbVFZ/gc1XBpLmpu6/E+3jGDQEA4PSrYUex+hzQEroucVio0RxkciqzIQK2VC4w3HoaR4kZdpGD2'
    'P/16Oo+TsY2DTlyBV025Ham+UfSmTyjVmZec1YW7cd6gMR+lJ5Td6LDTaNKK+kXlWIx6HFasfiC+i+7JuA7MM1zQ'
    'UjjFBz9KnlRqq0rHbw+K06XMf4of6VqQ61YXPCShSezcV5gc5xQMnihpFrES6nrwk3jchDD1Bpu415bDdXUB/cys'
    'v48Vt23iC8TiULIPfg0WNViI9Udtn1oPWsKHxBZvjz1aP9R+lacV3a3IzBKre2efyNI0U09iwTSbvWlIOaMU0MTN'
    'My2cgkfSnbQacEppiI7jWX0y1mvbqZUtreN5pZJfupHGNzMxPQADJr8zf27NUj8Y6RomqRJv0wJKiTQ8BZGRZIHP'
    'ba4yOe1fpdqFrpt/pl5p2rxedZXVvLDcx4Lb4ZEKyLgcnKkjA5r4J+N1hplr8ItVM8DS2lsbcWqupVjHE4SM4YZB'
    '8vggjjvXzef1pwdGKWjevr0PocipRmqze6Wn6n5A+Kpml0KC101poZRGPOknBHIx8qgZH414JcLttpYJUDSO+VPB'
    '+uD/ACr6mjsn8X/2pp3gmzkvHsYGuJRvRVhi3BeTIRkljhVXJY9BXzHfLE80kEg2Opww6EMPUdq68rlFKUOq18zD'
    'MacrRqdNvI5RVLZjAwR1DVWvFEeBKfkf05wexrXmkkLfMM7TtJ/i49fWse+mWSQIUwV6kDgg969tNtnkbDVlGFX+'
    'NePqD3FVF+bdcHkxqVB9wTSTQsiKc/KThDnkd/yqBWKbopOA+Qf8avlDmJbtzNLFMxygRf8A9VX5k8v/AEtDzhf5'
    '9fyqlGkbQrBIeQ3P0FTTzqMg/cC/r2FJ+Q/U0kuGS5wThHUIfbuK/bn/AIJrXmpaj8JfEmk35820sNYhlsyTu2rd'
    'QfvEHoAyZx71+G4cOZPUlfzxX78f8E3dG1PS/wBnY6nfxokOsa1ezWZUDc8MTCJmc9T+8DBQegFZr4hVknDU+3zo'
    '1s2SAUPtVaXSpFzsIcfrXRmmMOOK0aOBwicfJbFDh1Iqm0A5xXbOisMMA31rPlsImyY/lP6VPKRKn0OWFvnrxUoi'
    'VBgDJrSktJUPIyPUVEIiKViOWxR2EU3ZWgY++KaYuelAuUpbD2pjp3FWyhFHagLIzWQ15h47+IegeFFudHvNSh07'
    'VJrCWe0acfuw21ghJ9dw4FeusY1BZ+MAn8hmvyY/ab+Knhzx5r0L2EMtpNpsUlrcPMfldY5MoyDqDkkHNcWOxXsY'
    'XW7O/LcD9YqW6Lc8X8UfGLxS+g3Oi6xrV3dQTyGa4jmbejFsdQe3GcV8y3+tQ30V7e2VqymaRVjc8jpzgf5xXWT6'
    'bDq9hPqt1diRb2QwRwbvLZFjIZmZm457YrzvVdZe31VNP0G2DFAYljjyQRj7v4Z5NeVhablK+7/A+qxMlCNtl+Op'
    'p65cRWFjaWTvJeXrwt5inhYS+CgQDup6+9cbA32S7zdqvmQsysJOctyOfpTpLbxHNbXPiKZfKRWaEu7BTlcAooPJ'
    '28dK5iRbiUK5cu7k5Hf6mvaoUkk43Xn6nj16jupWfkdNqGpaqIfsTcRxxhQAcfJjKj6c1yxvZGAQIA2cZ7mp55ZD'
    's2Ak5AOTnPHFTuUAImUB8fLjqDXVCmoqyRz1JuTu2IIZ4imZDubrjoK29K1/W9Iu0udPuJrWeMnbJC5RhkYOGXmu'
    'eYXIi3vlFHc1VSecL5sgO0Hg+lOVJSWpCm0fqR+yh+07qOh6zZ+AdbtzcaZqcwCujEtaPtO6RR3RsZYDvzX66Yjd'
    'Q3mttPQiv5btA8Tajod/DqOnStFcQnckiHDA/Ue1fqb+yZ+1J4n8Y+ObT4ea+GvItTinkaTad8M8Sb/MDDjY4GGH'
    'YkVwTo8r0WgqtmuY/UdbO0lxvu2X8a1odN0hgFMju/rurkkltWwWZl/WrcbQ5+SfH14qbOxgpovz+GtID7kVs5z9'
    '7vTE02K2AWBioXp7VH5so484H05Bqm94wlETMST3HSpvJ7sluC1tYvSWl0TuSQ8+1Zosr9Z2dnBwcrxVkzkDqarz'
    '3qW8Mk8km1EUscnsKa0HJRdmadvc3iRkSIhbJ79qr6nNK2n3LpGrTeU+xQ2MtjgV5Rr3iGTVoYINHvJrebzQTsVg'
    'zD0zjGB78Vq3mr3dujRElpNp475A79hQox3Rm66d0jF8N6h4i0nw2bdIAZIpMoSQchz8wH+6a0j4u8RrbLDJbr5m'
    'ctITjPtiuV8OXdyUnhuzsLTFlQnOOfXpXXeQjD5hzjvWsIrqjljNuK5Wcpqvi/X2icSjyAQwVk6hj90//WrzS5tb'
    'm/kNzKNspOSwGCx9TXpWsr9mmjjVQxwZFzyDjj/9dc3qOr3cNzBb20EbNIN7jHRc4zRCUXNwitUctVyl8b0Rz8i3'
    'eova6dcOYkjJYqO+OTt9zjAqPUIlvNQa7mLSMxHDdgOAAPQVuw3r3V5BDMLfbJJ+7DMsckYxncrE8ADrmn6r5sWi'
    'S61psKXipKqsV+9EjdXkjHzD2YDbznNbJtPU5akN7My7Tx3q1lNm2bKRqURD90dgfwqmnjrxTDJxM7hufmGRVfS9'
    'Z0u6Ei3ccFs0YzwevXt61ck1DS5DGIJo383OMEDoM8g1fs77nBKpUS92Z//W/WzS794ZwpPGa9b0u6WaIEcmvBJb'
    'v7PP8o6GvTvDOrRMio5xmvBwWIXws9KrC6O21FQyoT61rJ/q1x6Cs262TLGVNacX3QD6V68XqzkexzGvzSJAxTOR'
    'XgmpX18LonzCADX0jqlsssTA88V4lrmhSvKzRqcZ7VwYy6dzWlZo0/C2uylNkz5x6mu3vdRt3tjkjJFeR6fbvYOS'
    '/f14rpLUG+lCFsKK5qeK15DSUVuamkMDflk6bX/lXyRroP8Ap/8Avy/zNfZ1laRW0oK9cH+VfGevSKf7QA7PL/M0'
    '8R8KNsPuzZ+GihtGt8en9TWT8Qvk16QY/wCWMf8A6DWx8LWB0W3+n9ayfiV8viFx/wBMI/5Vy1v4SOmh/FZ4HenP'
    'iC1+rV9JeGQDapXzZe5/t+0I/wBqvpDww/8AoyfSuKivfO2s/cPRLaJ3XK9qmKEHBqbSHB3A9607i1BG9a7b62OJ'
    'x7GJjFL2qVl2nkc1CxArQzaA9a6vw2Qr8/3q5HeOlaOnXzWr57ZpSKiexK9TK6k4rl7PVVmAGa24n3YIpxlcTRp+'
    'SjjpUL2CnoKtRNwM1ZGKdkyOZoyksBnmrsdsFHpVscdqDzVJIlzbKV1AGQ4rz7WLAnLAV6U43cVmXVmsq80pR7Fx'
    'l3PO/DMDp4gsc8fvh/I1r6ySmqXf/XZ/51t6dpwi1i0lAxtlB/nVHXbcnULpvWRj+tepgZfu3c8/GL3lYxIpx0Nb'
    'lq6kVzBRozV2C5IGBXW1dHKdQVRhgc1l3UajIFVxeNnio5JS4NSkNsouvcdqj4qVs1DtzyKpEi9adTQOKdQJsQGn'
    'r0pvPWnikSPGKlHIwKiFPU4oGS4xThTAc1KtADgPWngHvSdqkVSaATHDJAxVyJM1HHH0rqrHSVijF1qOUT+GP+Jv'
    'rS3KZBp+ny3Pzj5Il+856fhW359var5VmvPeQ9TVWe8Mw8tFCRrwFHFVx7UbbAPLMzZYkk1PcXMWlxB2G65cZVf7'
    'o9TTXkj0+D7XN80jf6pD3P8AeI9BXIzzyXEjSyNudjkk1nKXL6g2OlneaRpJWJZuSTUQaosnPNLWHKQOaoyewp1N'
    'HpT5RXEIzxTP6U80n0qlEkSg0fzoH61VhDWOKZ05p5PpTOgp2Aacd6bTjTTVJEsMim554pM8YpDmqSJJQakBzwaq'
    '5JpQzCqsBbxijB7UxJgOHFWlKkZXFA0iuQe1MIP4VeAFKFquYOS5QHFJ1HFaYTJ5qwkaelWqlugvY3MUJz0oMZ9K'
    '6VUQdhVgRoRyo/KqVXyG8LfqcgIHbopP4VG0RHUHj2ruFjUDgYp3loRyB+VP2/kT9TXc8/KUzy/Su5Om2pJzGPmq'
    'FdDtg24ltvpW8cTDqYPBT6HFbBTDGT712t1oULDNs21gPunkVzkltJbsUkGCK1p1Yz2MauHlD4tjNWB5XEa9ffgA'
    'DqSfQVmz3kMT7LRBLjrJIOCf9lfT61rXp8uxnZDguUjz/sk5I/HFcuEIHFd1GF1dnmYmbjaMS3/aNwD9yL/vhaDq'
    'tx/djH/AF/wqrtOeRSiHnit+SC6HL7Wp3Jv7UvD90R/98L/hU0erahHyrKp9lH+FVfLIq3BbK6STS52R8YBwWJ7D'
    '6Dk03CFtUCqVb6SZMmvahnDNkeoAFWhqs7DPnMDWXPaiJxsO6N+VbGOPQ+471GI8CpdGm9UjRV6q0cjWbVLof8tm'
    'P41CdSuz1kb86z9pFKKFSj2Jdafc6OK4kuIQ24gjg807UAWsbUuckSS9fTC1U07cY5VHtV+9iY2Nvnp5kv8AJa4s'
    'TFLQ9DDTcld9v1MLHpQBU/lDNO8sYrjOqzIMUFan2dqNh60rFWICARim7PerXlE9AalW0kboCaELl7FLBHWlIBrS'
    'Fk2PmzXlnxd8XW3gLwncai0oS4kRhHk8gd2H8vzrnxmLhhqMq09l+PZfM6cJgqmIqxowWr/r8DkvH3xU0fw0s3ny'
    'RiC2DNI7Nhfl5JJ9Bgmvyw+MPx6tNY1VNWtDmeTdNpNtMuUtozkHUrlOhkb/AJYRkfKvzHnFYvxk+JF1qZj0fUZG'
    '8mSIajqa5+byT81vbfWUhS/sQK+OL/VLjULifWb75p5nM0npgfcjA7KOAB6CvjMvwE8ZUeMxerey6Jdv66ep99is'
    'TDBUlhcLolu/Pv8A119Cbxb4nm1e5FojP5EbNK+45eWeT5nkkPdz+nSuDlly7BepG36euKsksQZpTliS7E9yeTVN'
    'Rj5m+8RkfSvtqNKNOKjHofI1akpycpMFRRxjn1p5O0cdaazbRmjdyK1uZJmpBPulZW6EY/St6ASgAq2Bx0OOv+Bx'
    'XKxNifd2wf8A61dLbzhoMD7wXj/gNYVEaRP1M/ZE/at1FtRtvhl8TL/zLdoFi0m+lGZNycLDK+eRjgE+lfqinIDA'
    '5B5BHQiv5c/t9zazRXdmxjmgYSROpwQ6kMtf0afs7+Ir3x58F/C3ia9Jae4slSQnqWj+XPPtRQm/hZx4yir88T10'
    'Yp2dvB6elTGHbwRzURQ966GcSTHrsfhevoelNMLA8jHtQI+9X4JwuI5lDL6nrS9DRLuZ/lj0pfJH8JB9q3Vs7ebl'
    'GIofSD1icE+9LmNPZM50qKZsU1tyaRdk5wCfrTV0a5zlsD8afMiXTl2MTyvSk8oCukOjsMFSCTR/YxPLNj6Urh7J'
    '9jnREO1TLFnhRk1rtYpE33GIHc00DkgDH0qrh7MoCzlbqAv1NWE0wAhmcg/7NaEEbZ+YVbAouUqcSa0le3QKGZwP'
    '75zWgl7Gf9YuPcVlAGpAKm5om1sbKyQyfccfQ8GpMGsL6VPHcTRnAOVHY0WHz9zTmeOCF55OiAmvy7/bh+JUVr8P'
    'b7TNGlPnfaYRM6e7/P07DpX6OeML4xeFdRliysiQkjH1r8ZPjXu1AvYXY8xJixcNyDk96+N4hxjjjKNFrRe9+P8A'
    'wD7Th3Bxnha1ZPV+7+B4V+z74EvNTsj4ikmeF5byG92ZwHt7FjIVYd9zcge1fMfxN0e4HiPUNWtBjYweUL02sRz+'
    'Ga/QjSNBvdF+GWl+LbOdLa10y9lV4eQ1xIYHjhRf9hNzSP8ARa+YbbRINZttXd/n+1RPGCfQLxj8a8vB5lOGNnXe'
    '3/B/yPqcTllOeVrDdf1Svf72fKKTFhuYfMVxn3HIzVSRo5GPJz2+h6j8KnukNvIYORtyD25HFUGUKFJzk8/hmv0y'
    'Nnqj8mkmnZlaVzgI/wDDnB9/Sqkkm75mOT3pZ3YMQfU4FU+Tkf3q2SsQyYSNkY69Kmb96giB7gk/Sqqn5to6Vowo'
    'CWX+Ace5NKTSGrs07GCW5mjgtkMs0siLGg6u7EBEHuzECv6lfgF8NG+EXwZ8I/DyVt9zpenq943Y3l0xuLjHsJHI'
    'H0r8f/8Agn5+zXL8TvHkfxS8SQ48K+DruOZVZeL/AFNPnigGeqRHEkh9lX1r9+byDepvIgSrklscgE/y/GuSL95s'
    'qtskjAKkU0jvVhl7ioypIrS5ylYjB9qiI7VYPTmozzVJisQlageBSORg+1XNtNKg80risZTW7DkciozEOh61rbc9'
    'Ka0SsORzUyiJxMhoRUZhFabxdRVdoyOtQ7kWRg6lbXZsLk6bsN4InNuJPuGXB2bvbPWvw+/aG8AeMvD/AIzvbnX7'
    'aLbds0/mxsoDM7ZdinZSTwOwFfus6EGvyE/b0t9fg8YwBZJWjuIQYpWTYmzgmGJhwwXqxPPNefmFJSjGT7nrZPWc'
    'Kjilo1+R+f8ArFzqF7YrNp1uWt9NKo5A+QOf4QOrE9fWuT0u1lhhuNaS5RJkRi6E4dQ5wF56568dK9B16f8A4R/w'
    'hZ6at5JGzK2oLIi4DTN8jqcjPC42e2a+fob64luDLOzlWcGRu5B6n64qsCnOnKK0V/vPQxkuWpGT1bX3Gjf6rd3Q'
    '+ySOzRJIzopPAZupx0yaox3bwEFePlK/n3rZu7O3lvQbM7YZPniBO4le2fc9xWZMlsd5mbLE4AXjGP6161PlsrI8'
    'uakm7spi7/elweMYyeeafHduJhI3VTx71Xhjd90SkBR8xJpdhkb/AHR17YFapK5nfQ1ri7eeHaOFJycmoo5WDeTI'
    'OCOfcVRe4VY1RR8zHk0sqzxBZD0PA7mlyq1gb6l+BZGOYgD5fB9cV9TfsxfFaw+Dnj3+3Z9F/tibULZrBQsojkhE'
    'hDExk/LubaAc9q+Wbd8ROwx5nrWhoaajq9/bWlpGWuJJkjjRTje7NtVQeMZJABrGpG9x20sz+lvwx420nxfoFj4j'
    '0mMta6hCJUEg2uvZkcdmUggit/8AtCIc+QPzNeT/AAg8HyeDPhvoehXTNJeRW/m3bMcn7RKd8o/4CTj8K9JYLis0'
    'loeI6s1JpMuDUrYE77cnPo5FPS907dv8hwR6PWJMyoCfQE4+lVUlDqJF7jOKlqI44iWzNO/1bSVuAkj3MZYZO1gQ'
    'PTim3Njpeq2xgivJHWYYwT19RXA6u11HIHuHXd/CRyQPTAqiur6nozqLOUKcFvmAZQW6gZ4zjrXC6rTtKOhLr6vm'
    '2LV3pQ0i5CRXMO9nCJ5k5hIbGegzzj6Cuum17TZGTTNSt0ilih3yCSUgEAddxxkd+a8I1e+muLuW9fdLPI+4S9w/'
    'TcfXA6DpVTU9QuLuVbr7OYpVT94zsW3t3ODkD2zVXhGLkjk+uOL5Yo9nuvEegWPlyw2uYWPM0ZDInoSazvE2v3Vt'
    'bvexmaGJUQ280DoY3LddwPXPQV43eXU97FDEt1kYLFuAIyedoHTOepPFZ1zdXaWRszePcRA5CuwO0gfwgcV0RalG'
    '0WZSxk10PQbrxDPq8zXcLPIsYYwq21Ap2jHA5bB6+vSuM17xFtldcBZzFHGyxAjao5ZSTnDMeSB0q7pnnao0dw7i'
    '0gtlCRqnBLDqRn8zVRtatbLzFsrdHYsf38g3OxJ5OT60qSkpO5zVa8rXctzl/wB1fy+Tbys4ZU3O/B3Y+Y+wA496'
    '01v0s08nTppo5ArI0gkOHjP3QV7e46YquriS5a8lZWeQHIUY6+wqpEkXmeY8nlnJAUDk/wD1q6+aMnY41Xd2UxNF'
    'eS5mHlsODKo4/wCBgfzoktJopThg2O6nI/SnzWklvcOYgXRh0AyCp9ahgiaMqpdonI+XIypHoa0tbY55yTP/1/1U'
    'l0t5pG28c1p6ej2Iy4O1e9cD4i8cpCzWdi4E3cjtW/4Q8e2+py2ugz2rvczMse7jaSe/5V8TQxuH9q6UZa/qetPT'
    'U7y+8YpAka2/zAda7jRPFFpqcagHa4AyDXB+L/C1rpsKXltxk4ZT057iuN0m4mEb3EcoEasVDDjJHXFdv1zE0a3J'
    'URjaMlofRN1dRFcBhzVT7LbTRZIBJrxW21S+uJGjikZtvfrTj4l1O0cowPpmuuGYRqLncdBeyaWhs+LVgs+EwDXD'
    'W2rz2x8xOlXby5udYkAkzk9BTm0S4t4RvT5fWuGUueblFaDUTovDeuzalemF+gR2/IV8ta6p/wCJh/vS/wAzX014'
    'Vs/s2otIw48txXzrr0YxqH+9L/M10NtwVzehuzQ+FHzaPbfT+pql8VQE8TOv/TtD/wCg1f8AhVlNKt8en9axvi5O'
    'v/CVOP8Ap2h/9BqK38JHRQf708EvnH9u2vP96vobwzL/AKMn0r5svC5121P+9X0X4aDLaKSOwrio/Gddd+6et6Kw'
    'ZW5rp4342muS8PYIeuoyB1rqe5y9CO5t1KkisGXCtiul80MpDelcndSr5hAPetIoTEJ+bAqxEQay/MyeK0rVPNjY'
    'ryQap6E+hqWt01uwI6V2unaoGABNecByDg9fSrtvO8TBgaTXVDT7ntNvMJAMGtGM+tec6bqo4BNdra3iSgYOaaaJ'
    'lE2BQaiRwe9SZ4wa0MWhSOKaVzwaX9aUe9AgtoQLqJsdGBrM1O3WS4nJHO9q27XBuI+3zCqV6P8ASpv9816OEXuM'
    '5MS/eRwV5Z4zgVkKhDYrubmANmsKS2CvnFdaehyyjqVYLffjNaX2RMZxT4FC9a1IwvagDn5LQY4rNlhKGuykiB7V'
    'nTWwOaAOXKkUvGM1pS2x5xVRoitMhog6U4evpSlcc0lArDxinjvTR608etIBw7U8GmqM1YRKAuOXtWjbW8kzCKNd'
    'zN0Ap+n6dcXkojhXgfeY9APeurDWulxGCy+eU/flP8hRYcUJb2drpKiS4AlueoX+FKqz3Mtw5klbcT+lVmdnO48k'
    '96TcM80yyUN6VftxGkTXlxxDF/483ZRVS3ha4mES9+p9B3NUNXvBPILa3/494eFx/Ee7H61MnZXAqXt7LfTGaTjP'
    'Cr2VewFU+tBGB70h6YrG19SGwPvRmkA7Ue1VykiZNGaX6U2iyJ1Ckz2paXtxTsA2mk+lKc9TTT7U+UENphzmnkYp'
    'SKqwMjpMelSbePWgDuKaQiIj1pMVNil207CsQFc0Bamx6daNtNILEW30p67lORTwpp4QVQWJ45VIw3Bqzgdqo7Kl'
    'QunPb0pcnYtMuqKmVahjkVuowasKM4xzU2LiTKO9W0xjNVl96sgcdaOhQ8UuOaQVKAKCrAvXmpQfamc0oOaQFa68'
    'wFXg6gj6YpZ7WK5TEy5OOvepiuTmpVYA4aqUmrWE4p3ucrqHh8vaMkTjLOh+b2zXJXOj3VmQHTIPccivVrmRPs5x'
    '/fX+tZxkUg120cVUS11PPr4ClN32Z5Q0aqcY5oEfNdtdxaSdytGN2eexz9axBZRsWZH+Revcj04716lKspLax4tb'
    'CuDsmmUILVpjtUfUnoPrWh5cayJZx/MiLIGb+8zKdx/DgVdY/ZrctbqhQDIfq2emT6Edh0FZNoSblR/vf+gmtL3T'
    'Zi0otR7kCPtTy5FDxtgkd8+qnsaY1mX+a3O9fTow+o/qKtRxtJhVGSeMVoQ2scW4uwLopbYp9PUinKViYQct9jDW'
    'yuCxURtx1yMAfialFlt+8y59BzWldTPL8nRR0A6VQx6UJvdicYrRanQ6JZRtHKcbiCvJ/GtW8sk8iFGxgM5498VB'
    '4a5SfPqv9a29QwI4sf3n/pXmYmT52j3MJBexTS/q5zgsLc9Vpwsbbsgq4cU0VznQooq/Yrb+4KZ9kt8/cxV3HOaM'
    'U72FYqCzg7AiphbKBwamoJxSGml0EW3jUEyEBRyT6D1r8gv2qPi1D4q8Zf2JaykadFIyMAf+Xa35lb6v938a/Tn4'
    'q+IX8MfD/W9Xjba8do6IfRnG0H8M1/O/4116W+vte1R2JEUUdnCe5eVjI/4nivl87br16eGjsrN+rdl9259VkEY0'
    'qVTEyXkvRK7/AMjzPX9XuPEGpahfXEhc3krXUx7AZxHHj0QbQBXEX+T/AKMRty5J9gvAH9a6m3MFnocrsMyzyooP'
    '+xH85/M4riZ7gPI248vJgn2HJr1cLTUXypaI4cTUcld9SjdqFVVHfr9BVJh1b04q1dv5k5A6ADJ9upqpKchV9ix/'
    'HpXpLY8+SKsr/MB6UI2cE1WkY5Y9h/SpIzhFGegzVtGaRfjYfNntV6KfYyj1DD86yU3LGfViPzJqbB8w46Dj8aho'
    '0Wh2CzA2yv1wq/8AoNf0P/sN3Ut7+zL4Qm2sCsM8TZ53eXO6gj04wPwr+d6xgC6dChPzSOW/4Co/+vX9H/7GkMOm'
    'fs5+D7CJldo7LMuw52SySvIyN/tAMMisaT96w6y9y59MG1WXmRfzFRNp0J9qu780u4Yrc5LIyH0xM/LnFMGlbv4s'
    'fUVtdaXOOhpeguSPUzrexMOd5z6EVa2sp4qfIbrwfangA8Hmlr1LSSWhErEDk1KcMO1NZCOnNQkkHFHLcfNbckK5'
    'pdlSR4Y/NnHtT3Maj5WH9aY3Fbldl9aqtAM5A61YMg9qhLk0WIbRA0ZU0zmrAJNIcUyeXsQ9OtOFFOAFBFgUU7GK'
    'cBS5FMVjG16NJNEvlk5XyHJB74Ga/Mv44+G7KOCTUY41wEyD0xgnIP4V+n+pQfaNOu4QOZIJFH1KnFflR8fNdSKx'
    'S0dvmYn5SeuODx7V8LxZD/aqMlu01+P/AAT73hKf7irF9Gn+B4h4n1e/8S/DvSvB+nSJbQWRmMhA+aQyybySfXGB'
    '9BXLN4Vl8J6VbRTbW8+MMrjoc1zfhrW3uNQfT++eB9TXtvxNs3jgs7FePJhQEe+BmvmpKVOfs5PfU+1hVVWkpRW2'
    'h+YPjO3lg8QXgc5DOzZIxnJ9Ow7VyXmEsA3Xse1fQPxL8Gz3N2+p2yjYq5kwPmLdzXhctjc5McUbMF64BI/E1+q5'
    'XioVsPGSZ+T5rhJUcRKLW5Tez8w7s8Bck+55rMaMq20itKW5aNQrDvz+Haqv2lHbc4zj7o969RNo8tohVGBBVeQf'
    '1/8ArV6L8NPAniD4keMtH8C+Gbc3OrazcrbwJjKpu5eV8dEjXLuewFcfBLHK4UYyP61+7n/BOH9n7TfCnw2/4Xhq'
    '0aza74u86HT2YAm00uGUxnZ6NO6FmPXaAKwqybdjSPurmZ90/B/4X6H8GPhtonw18ON5lrpEJE1wRhrq6kO+e4Ye'
    'ruT9BgV6fBcy20geI49QeQR6EVXVSvFOxzUaLQw5m3c1riyttRjN1YDy3UZlh/8AZl9q5uSJoyQRgj1rRgnltpBL'
    'E21geDWxKltqK+egCv1kjHUHuyeo9RRsDSlr1OOYe1RsCK0p4hG5VfmAOMjoapuKpMya1sQGkOKf9c0nagTGUhGR'
    'nFSD2FOx3oEim61XZAa0mA6VUkBGQaQmjPePI4r8vP24fDHjrV9Y+1iWN9MghgbR4gvKOEIu2kPYlsAZ6giv1Gc7'
    'DkdK8L+KvhHwxqX2zW9XnlVriwNpLCWzCSpJikCno4yRkdR16V5ecVfZYWVRdLP8T08hpe0xsaT63X4H86dzp7z6'
    'eLjXriQbpDDEn3ggQ87h2APGKxbrRtP0/SJZkxNPHKwchsoUKjZgdcg5ya9Q+JWjr4K1bVdMslk8uO4LQmXBGGY8'
    'j1yOc15ZdaRc6Vp9lqfnLeQ30LOyAMPKfujg9x1BHB7VrhK8ZRjK+ktvzO/E0JRlKKV3Fa/kcnItwES4jBVACQw4'
    'Ax1H51QjnjWNyVzIx4J9P8avz5W1ILDhsBM8jPOcehrOuFiSCPb99uW9vavZikeQ7kkCMimUkAMOh5zVZ3bYUU5B'
    'PIxSRmWVRDvxt6ZNC74mJPPp/jVX1JYsMa+dslBOOeO1Wp5SS0MfJxmqqTOWIHBPeo4kcy/N3z9SBSs7j0sXEk8t'
    'V3ghX+8ff0ro9JuikqFTsIIKkcEEHjpzXMqY8MzcspwBXXeF5bi11ax1G2IEllMlz93cMQsH5GDwcY545rKo7IZ+'
    '/f7Or+Mf+FWadB42geG5hZ47QzY86Sz4MTy4P3jk8nkjGa9mmHlruK5HtXNeEL+71vw3pOsS27WrX1nBcGAncY/M'
    'QNszgdPpXXNbOQPMDH2HH5muebajpuePPVnKat8iCZSwLArx0wexBrnlvpYIHRTljgBz0GOp/KvRZ4bNljjc71Y4'
    'OT8q/U1zOr6bHKGfTSIiozkYCsPfsK5XSk25J6mVWOl0cF9vdoZGmDOYm+Z1/u+nPPPelgFvrETPcJ5UaHA5x09/'
    'arEtuDGFn3JcO3LNgKAPQjrUFwoSMJldqY+b+HJ78dahOSfvK9jkk13Mi9s7HypIrdiEyN8zAn6AelYV/HbSQpsY'
    'sxcbg3Ugd2rpp3gaBrOFg2RksehI5rGj05ZoHmJJI4VR3PvTpx5vekranNVdnZHJPDiaZnjMb7QEUjAzn7zetSzW'
    'lr8jzRrGVjGQOSx9Qa6O9s5pFV5HDEDAQdQKzGtprgMzgDao7dABgCuxU+qOZy6GXFcGKOQIMLhu3QkYwKzZ4Yo4'
    'SACJDjg8jHc12P2F4rERyJuGeFPbPc1kXVkWJIwSOuKqm1dnPUbdkc0YDldr4ZumO2aQ2skeS4Gc4I/irWFs8apK'
    'o/iwCOxqtdym0uWcA4Axk9eR1rZWvoRyjBIyQhFbqfm+naqU7wliGUn0IPSq7XjBw/QZqUbbjDEDJ69vxqZUne6M'
    '2u5//9D9Yv8AhVOk2l2b24k8xycndXnfiHUdK0DUh4gsp4oINJcx/uF3TTSkZ2/3QB6mvj3wx8e/iB4Xb7HPfPqN'
    'lJw8F1mTAPUo/wB5T9DX0J4e8UeBtc0dbDW7SVfOnQRtbSPcJdSOMgLHxIGHQgjA9a/N44zDVIctCChJ9+/TU9JX'
    'erZS8VftAa74yvIbGKEafZqwBAOWYnjc7e3XAr3TR9AvJNKto4Llbi3dQVmj+62epH41yc3wp8MwyQXTaTHFG00a'
    'sodmcRsQCWOcAn0HSvonTNItNL06LTrJBHb26hI0H8KjoK7sBg8RUqTnip8wrqOxh6N4bh0yLIdpJCOS3vVfWdKX'
    'yGkA6V28EQB+dgo9zj+dY+vkrauqc5Br3VRpwp8sVZDUnc4LQvs32rbIw3A969ebTIrix6A5FfObQ3Ud15ilgc9q'
    '9h8KazdSQi2nJIAxk1OHnTi+RrciXMyvaWT2l+69grYr5H1+62DUSR0aX+Zr7tlskMglPfP8q+HvE+nqYtTYH+Kb'
    '+ZoxFNxirHRh2ru53nwv8HeIo/Dun6gbYNDcRCRNrAnaxyMim+N/hf4i1/xpFMbGYWEkcMck6AHbgYY49q+jvANl'
    '9i8E6FCeCljD+q5rvI5WC4JrpWEhOCjLyMXiJRm5RPje+/Zf0v7ZHexazMpi6K0QrpdP+Fg09WgfUFlXbhONjA+v'
    'vX1I7bgQa4LxLZSBfPgXkdcU54OnH3ooI4qclaTPHIvAOt2cjPY6gQD2Kq1A8N+MEyHuUkGeP3X+Br0fRr2Ld5d2'
    'oJ/KvQ7ax0+ZVdc4P+1UrDqQe3sfPCaB4mBw7RnP+yRTP+EJ16QlzLCc9skVBL8ZbvSfFb6bqTW8elw3rwySsvzJ'
    'EGIzmuV+LXjmLUNXsrrw1fkweQQTESATnvXJKpShFyWtjqUZyaTRv6n4Z1jSY/NuvKjVuhZwAfpms/TdRjshIt7L'
    'GuSMEODXnGq/Fez8ZeGovDLB11DSZ0jkdjnzAAckH8q868Q6j/YmgX2tAeYbKFp9p6Ns5wa5auJTkoRWjsdFPD2g'
    '5yequfUyCG+V57Q7whw23tUmwoOQRiviPw3+0rqMc9vp1lbpbzX7YJAyBhc963tW+J3jDUY3D3bIrZ4QBf5Vnisd'
    'HDy5JRbZpgsHLFQdSElY+ulujG2VOK6vSdXyQrHGK8K8OeJ7O70uyWacecIIw+7uwXnmu4tr0Eh4nB+hrrtzq6Ob'
    '4W0e1x6wgHWtO31SKTHIrxYX0zD7xrQtdSmiIyciqSkiXY9tSVXHynrUorgdO1sMAGauutr1JR15qkyJQtsbNqf9'
    'IjH+0Kq3fNzL3+c1YtGBuYvdhUN3j7VN/vmvSwfwP1PPxO6M50/Osq5Tbz3rZbnrVG6QEZrrMDBMu01owXAJxWPc'
    'ggmoIp2U0zO+tjrg4bpTGUGsuC6z1NX1kBFBRWljzkGqUkPGK2CA2c1BIgNAGE8VVmjx0FbMkY7VRdOaESyjz1NS'
    'KMin+Xz7VZjiWgzeo2NMc1vaZpMl6TI58qBOWc9PoPerenaOuwXmoHZD1C9Gf6e1Xru9M4EUYEcKfdReBgetNR7l'
    'Jaakk93HFELSxXy4l6n+Jj6k1mk5ptKKdirh+NOA96TtVu2EcYa7mGY4ecf3m/hWiwgu5vsFr5CnE9wMv6qnYfjX'
    'Ok8+lPuJ5LiZ55DlnOTUXTmsZasGxxpMCne1JQkIbxRinYpcU+UCIjPAphBH0qximbQTjNUkFiPGaUjmpAMClxT5'
    'RWISKZjmrBWmYosFiLGaXbUoX1pcVfKKxFt/CnBPWn4xTgCafKFiLYKTZ6frVgLRjNPlF6FfYCaXaM4qfZmgLRYe'
    'pEFGaUJzxxU4XtTlTmmKxEF4pwT1qcLTwlAiuE5qePcvSpFQVKFXvTtcokST1qZZR6VEFSnjZnHNTyDUmTrIp5IN'
    'TAqBnOKrq6DjBpd8eMYNL2ZfMOadeAMmpldduTVbMR42mjy4jz1q+RdiOd9wkvEXIUZIqlJdXD/dGKvBIRxihliB'
    '4qoqK6EScn1Me6muvsTdm8xMfQ5rEf7Y3JfH0NdLqGDZvtB+VlY/TpXPZz1JxXdR+G6R52J+KzZTNvIcs7c1PA62'
    'hLdWPp+n60j1BjdXWtdGebNqLvEdGJlG903h+4PPv0/rViKGVCTHCik552HNVlVlOVJB9QcVMZ7rGPOfH+8apxvs'
    'RGaW5I/2oghSgHsMf0qtGhtvML8l0KgDtnvUwknY/NIx/E1LsL/fJY+5zStZDvzO6M8gE5FKIgauGHjigRY4zS5i'
    'lSfU29Aj2pP9V/ka09RwI4vcv/SqeighJfTK1d1RhiCIdQpY/wDAjx+grzq799ns4ZWpIySc8UucdKbR9TWRsP4p'
    'OO9AFKBQQw/SjYWH61HNNHbxtNKcKoyT/nuegFeV+NPix4T8JW80esX0X2kKfL06NwZGbsZyPugdSv51y4rGUsPB'
    'zquyOnC4SpiJqFNXZ5H+1j4hNl8NbywRwBdLlcdSidW+hPT1wTX4LeKbtoPDunll+bU7m4uj6lFPlx5/AE1+l/xM'
    '8e6n8abXVLC3lJku5ksLaRB8hz/rSgH8ESDrX5xfGqxiHiWHw/oAZ4bSJLG1A5LgHYWH+8Qf518VluP+t4+dSStd'
    '316JLT8X+DPt8ZgPquAjTTvZdO7f/AseVXl6WtbeIdCMj8TXKTSDfn3c/wBK7HWbJNOnMAbe1uoiz23oPnx7A8Vw'
    'O5nCr1IBB+pavtsNaUeZHyWIvF8rLiRl1J6lyF/qaqTyBZnH90D9K0H/AHaBQcFQSfrXNRu0xkc/xvjPtmuqOt2c'
    '70LYiZkUEfewT+NLjLEDpnH4CtCVRBArnBdiNo9qrrGEG5z0ySffvRfqO3QUkK6g9IwWP9Kltw0rAdFA3O3YDvVa'
    'VTIRbqfv/M59BXRafZi4ZYhGXh7oDgvj1P8AnArOpLljcqEeaVjpvAOi3/jnxdpfh7S1LG8uYYc9AqFwo59yf1r+'
    'mP4DeGdD8KfDax0Hw6ZZLOznuIzcyDH2qZXxLPH6xMwIQ+i1+C/7KaWWnfFfRdV1CNBbRavYb0x8oTzwGGPQZr+k'
    'WPEIFtAixxxfIqIAqqF4AAHAFcWFmp16iT+Gy+/U2xtN06FNv7V392n9epaxxjNJSDcaftPQ16LPNTG5OaBkjFPC'
    '0/Z7igYirmpNuOtQSTqownUd6pySyv1JpWFzJGn0PPINMdVGaydzA8E1YS4YDa/zccUWGpIWSeVzg8AdAKYCfrR5'
    'qt1GKUFfWqRDV+on1pM4FS4U0m0Hp0oFZkYY4o607bSHikFgAJqULUZzngU4N60JB6kuBUcvyKXbgLySen50ocV8'
    'qfH/AOLV/wCF0js9Al2Ss0kDuRlV8sfOQvTOTjJrzM1zOGBpKpNXvokenlOVVMfW9lTdratnmf7Rnx2ubPUrbwro'
    'k5trOK5g+03CttLnzFzz2Va+EPjv4v8A7U8Qz2tuC3kyyqfQncentjv3FY/xD1+/8U6zBpCMbvVNUkwiZ5OTjcT2'
    'APU+gzXofxh+BUWk6vp1j4Y1b7XNbaTb/wBqSTsXVr1dyylDwVT5cgHoMV8DCUq03jsTLd9fwt5I/S61Gnh4QwGE'
    'jstbfjd92eWfBjw6mv8AjXR7AjD3t5EkhPXbuyf0Br174ozXN54pm0zTopLmeWZo4YIVLyOckAKo5P8ASuS/Zn0z'
    'XJPjbo+l20A1CKzkkuLmaA/JDDGhDSOT0AYgD1PSvu/W/Dfhn4TadeeM5IGv9WnDFWx87kknG48Ig/ur175qpYOW'
    'IrqX2e5zTzSngqDjJe92/wAz85/EXgbVdDxF4peGxnlXJtSwlnAI/jVflX6E15bfeHtLG+OMgKeuEAzXoPjzxhrv'
    'jTXJ9e1ZUhLEqkYKgIg6DivPprnJwXXP+8K+vwuV0acFda+p+fY3iHF1ajcWkvT/ADuec6x8PNMv0MSzPEOo2qK4'
    '3/hUcMbEi/Zx2BTGPyNe47hI2Ny/TIqUWjPzjNenFuEeWLseVLFVZSUpu5z/AMB/2d/D/j74naf4f8X+J7XQNHLL'
    'LLJPw10VkUG0iY4CPKCQGY4H1r+ljw9pGkeF9EsfDOg2kdjpmmQJbWltEMJFDGMKq/zJ7nmv5yo9NYncymv2P/Y+'
    '+MMXjzwWvgXxDcmTxH4eixE8rZkvLAHCPk8s8PCP3xg1rRq68rKlVc32Pr8sMcVGW5FKwGeKbXTYjyE3EU5JJI3E'
    'iEhlOQRUZOOKdRYVzQJivY2DriYZYEdCO/61jyRkH6VdgmNvKsoGdvUeo7ipNQtWjbz4vmhk5VvTPY0ttC37yuYr'
    'cdaTGKssoP3hz60wxnPoKohxIMU4UpGDSbeKRNhpxg1SuSN20Vac7AS3as1mJ+Zupo6iY11zXwP+1Z49utCvxols'
    'SAFDEDuSo/xr7wluFTjNfAv7W/g6bVdX0/XLdSYrmAox/wCmkJwR+KkGvm+KIt4SMuikm/TVfmfT8Hzise4veUWl'
    '66P8kz8y/F1vJ4kvYZrw7kLgyKed2Pu5ritfsLFbLWtM8tmubG1spEm3fIolZsIF6ZwCc16X4ihewdogvzJml+I9'
    'zpz+HNG0rQ1E0lzawvcSLtL7toeQORz/AKxmVQeij3rxMNi5J04rbp5dfyPs8Rg4NVJW16+elvzPjmdJDA0DxYkL'
    '/fPoO1ReRE8KO0WCvDL3OO4r2DxN4XMWlW9xFG26NP3gB4Bz1IryhiGKxhgrqCmT3Hb8RX3WDxKr0+aJ+fY7Cyw9'
    'TkkYlwFSDITYS3HriqomJXa3GBgHFX79biNQzvuKnbj04rLcNgOe9ehHY4GKjN8zAfMMYqSLe7l3bGFPJqBehLcE'
    'dPepi+diHt1HamIuW0InRiFO4nk+tfof+w58I9L8Va9qHiLxCjtHpsSPHbuFMVzFPlAWz2V1PHevkn4VfC3xR8Wf'
    'EEfh7wrCjSDmWSRvLijGCRub1IBwOvWv28+B3wZ0v4PeGV0yzLTahdJH9uuNxIdkBwkYPRFJOPXqa5JzV9THFVFG'
    'HKt2e/QTRwIIodqKgCgDAAAHAA+lZ0mqyzGSPO3HBB4z7D3NU7xSY1RI280HJI7D396onc8glkXLR8jPqPWuSrJz'
    'dkeW7kVxdlJAkbfMeCPT61VmldrfCtvjL5x6H6elX7hv3RGEBk7gcnPWsqSEwYeQ54+UDkVn7FJNJmcm+o4w29zl'
    'rwkIFwvHU+vtWDfaZIIwlpJ5kDZODxjFXnmlYEbjg9RVVmd1Eecqvb61tSi47nNOz3OYW3HIHHaryBIv3DEhMklw'
    'Ov8AhWybeM2pdlKgntjqO9Zl2+E8pOUXvjkmt9zmnEo3JQOgC4XqFHp9fWq4jiZlCEjeQfmORgcgfnWjbWwkVg6k'
    'nGVHb6k1PFpojYhyMlVYE9ieD+VKVRJMzjSbZkTrMVOMlXPzHjg9eM1l3EBCblGMnbg9TW3MRE8gm/eFXI6859RV'
    'HKux8xgVByvXd9BTjJWIlRuYPkoYSmcE9vTFZb6a1wwLfdOTz7da677JG++bbt8snKn+8egqMRGyjWSZDuc43EZA'
    'quYl0rLU4iTRXlcKFwqnjHGadJpMy7F29Tgf/XrrHuuWBAYHgECmrIojCFfmB49cehrT2kjGVJH/0ez1/QLK1kM1'
    'lL9ohc8HGGX0DD+taXgnXbvwrrOk+JbeUma0uQrI4yoiJ2vx6FSffNdr8YPh9e/DXV1dDLPo90T5MrYbI43Rs2OG'
    'Hb1ryuy0jVtSt77U9DU39tp0PnlAPnYk4VGT1zyexAr8irYCrTrKVLSz27dTv5t7n6d+LfEWm6R4YvfEdnLFqFra'
    'qWHkSq6uwIATcpIzkjI6ivBpf2pL59MSGz0yKC/bf5hdyyRqDhDzjJI5I7V87/DbxRY6V4Q8TeHNUv2826WKW1i4'
    'Nv8AaI+ZWH8RIyFBHBPPavPb2exWVTETtH3nfq5J5OOw9Bz7mujH5rXc17GfKmtbW3uUrW1R9J+HvG/iP4ja6ltd'
    '63LDLI2MgOI1XuF6Ln0r7JgNromhKl5dFobWItLPO2flUZZ2NfDHw31fwJ4Z1WPVdRvYpIWhJh2h3m3dAWT7qnjG'
    'K6Hxt8ZtT8WwTeFNAsALTUM2xY5ed1Y4G0DoT6c10YGvRwdOVSrPmm/Ntg2fWGiz6N4iU3mkXUN5BnG+FgwB9Djo'
    'a37mGTT032vDCvIfgb8P9b8DeHJINVPlzXs/2gxHrGu0Kqt74GT6V7HqOeMngda+kws5zoxqVY2k+gXvsWNB1q91'
    'C4+zzZ+RWPPsK+XfEc2Yr2P+J5WUf8CfFfU+hmCOcSRj5irA/lXzRd2P2/Vo7Y/8tr9Fx9ZRXTNt01rc0w61dz66'
    '02c2Vtp9meI1tYk/EIK3w205zhapz2O+JQvWPGPwqte6vY6ZZNNqB2quAB3LdgPevRi7fEcstdUbxdEXMjqgwTyQ'
    'KpW0X2+xWZ2D785xjHWvO4A15c3Gt6xN5aFCIImcBUTscE9a0tMvF0i9hCyZs7gbGAOVDdmFCqpvXYXI0tDH8RaX'
    'JazGa0GCPSqOl+IruH5JGI2A5B9hXq2oWMd0p6HIryjxDpLWEFzeoMLHE7H6BTUzTVyo2Pz3+JGpzXFnqU7Eq012'
    'vzeu+auq0q2D2VoXbO6MHBryjx1qFxNomyUg7tQhC8Y45fFeiWd1NHaaYqNtyibhtzkY9e1fPNJs9pSsjhfC8iDx'
    'tq8WeBczcf7qitv4i6gY/hz4jaVlLLYzcr0xjiuC8GPNd/ELWsfdN9coPwArr/ijpd1b/DDxKbgLuNjKBtPrWLjL'
    '2yttobqSWHlfzPkjRL2P/hI/DRB275MHtnMdfVDuz2ryRruWMgM2fugjjjvXyPcLFZap4TmUFdlzGGyR0MeMV9e2'
    '9nA+myyDeJCAcgfIV9/ejN4c1SL8h5DLloyj5mToPia483yw5G1tvX0OK+hfDesXLRoyyH86+N9DugNTmizjZMw/'
    'WvpvwpcZjRa6IytZeRhOF3Kx9F6XffaR8w5rfXA5rhPDznzcdciu6VSODXdB3VzjmrMsxyMhyp5rpNM1V0YKzYrl'
    'hU8RO4Yqmrkp2PaNGvhNdQDOcuKvXjf6XMPRzXm2i6g1tcwyvnCOpP0zzXd64/2fUXb+CYCRT6hq9DBP3GjjxiXM'
    'mTZBpjrkYrPhulJ5NX0kVhwa7DjMW8ts5bFc/LGyHgcV2sqBxmsa4tc9KE7CauYSTFD1rThuT61RltmU5FMQMpxV'
    'WJ2OkSXdUmQayonYY9avqxYUihWXNVniz2q6BnmrNvZTXj+XAuT3PYfWhJiuYgt2ZgiKWYngAZJrqLTS4NOQXGoA'
    'PMRlIew/3quRLa6WCIMS3HQyEcD/AHaoSO0rF2YknqTV2Ish9zcy3L75TnHQDoB6CqlP60wimAmM8GnACjHSloSC'
    'w5UaRgijJJwBVfUZ1JFpCcxRE5P95+7f0FXTJ9lgLKf3soIX/ZXufqe1YpQ1MuwyHBNKFNP2nNLt9qmwWQ3GKMU8'
    'D1pcU+ULEQBp4Ge1P244p230p8oWIytJgZqTYaNvpVWERYIpdtSbTSYNHKwGY9aTaKkwepo2mnyiI8eoox3qTb2p'
    'NpqrBYZilA/Cn7DTwvalYRFtNO2+tSBfWnY9BTGMC+lO2inBe9LjB9aCbjAhqQL7UcE1Io9KdgFCZHPFO2+lKPep'
    'guRRbuBCFPapFjx1qULinhfWmDZFt56VII/apcY6UYOaBEewelKFFSBfWnAcVQm7Ee0elJgDpTjkdKbweKAADNNI'
    'Bp/TpSZHWgXUVMDggEEYIPIIPaufvdOaNi9vlkP8Pdfb3rf605UbPQ1pTquDuZ1aCqKzOM+yzH+BvyNSx2DseY2r'
    'tdkhHCsfwNO8mY/wN+RrZ4p9jmWXx7nNQ6bGeXRvzq2um2ueU/M1tfZZz/AaT7LN3XH4j/GsnXl3N44SC+yZq6da'
    'D/lmDUn2K2HPlLV/yHHdf++h/jS+Ue7oP+BCp9rLuWqEVtEofZrbP+qX8qX7Jbf881/KrmxB/wAtI/8AvqozJbR8'
    'vJnHZBn9aTm+4/ZrsLDDFGCThI15Yj0/xNYlxKZ5mlPG48D0A6D8qs3V4048tBsjHRfU+p9TWeRntS8xu2yDHNKB'
    'jtQBTwPWkKzAepp2VPekIzxTPKLkAd+KAaPlz9oX4q3Hhy807wL4ZuIodWvo3up55GCpawIOJGOeCBl/XgY5xX5g'
    '+LtJ8SajqNxdaxcz2WmLLl57klLm6z827Yx3KG6gHoDzXsH7Q3imfw3+0NF4kvQkq2FiL0RygOhYhhCrKeDg7Tg+'
    'lfGPjn4naz4mmuLzUJGaR5CwWQk7ixyZJD3HfH8RwOgr4PMefE12473+SW33n32VxhhsOk9rXfdv/I7TxZ8U4fC+'
    'mw+H/CSN9qmHkweVzI2/AITuAR1b+I+1cZqFlF4Sso9d1LF34m1JG8iMfOljB0eQZ7jgbz/EcCuQ8I39nb6lPrOo'
    'It1NDEXYufmGemT/AAg98dB061yPxC8dTaorQW/S7KtLMBhpFThEH92Nf4UH1PNXhMrkpqjTWn2n38vT8wxOYxcH'
    'Vm/8K7efr+Rwms3cct3JHE4cDgleR64B7+59a5CzUvdOeuHrdstMurxwsa443Fm4UKOpY+lD28VsfKt8kMTukxyx'
    '7kegr7Ok4xjyJnx81KT5mZd2dzGJOS3DH09hVa1gXzsAfJF19M1pPCoHoRnAFRMogh7c9R6mtebSyItrqUriTzrl'
    'c/dXLAew4H60zLSNzwi8t/QURKrMxByznkjsOwHtWlFDGicgKvXnkn6ChtISuzLjilkzKcr5hyc8cenNeu+HNJU2'
    'CSxOHnnOAB0Cg/d9h6nvXlMlzumCQjcBn5j7ele+fDuxkm0mGQDLyOfyBPH0ry84quFDm8z1snpKdbl8j2j4XeGm'
    'g160s7IF7mW4tI4wv3mleUYx7ljX9E7xpGxUckcE+44P61+SX7G3wsu/EXxBfxlqEZ/s3w4ElUsOJLxgwgUeuzlz'
    '6YFfrOoxwTzXLw/SnyVK838TX4FcSVoOdPDwXwJ/iSrnrQTQPajHevoLHzdhc80HOOKXB9adsOelILMpeU7ZwDTf'
    'KYdetaPzdqjZc/ephylAxsKjwQa0DGKY0QphylTGaNpqzsI9xShDSCxUIYUqlx2Iq8qgjBFHlCnzBy9imCT60/nv'
    'xVjywe1ATHNHMKzIgtO2elS7T2qGaeC2UvPIsa+rED+dDkkrsaj0E2ZYD3Ffnl+1FcWY1CDT4FVWUyzOe5Mjk8/z'
    'r7K8UfFnwZ4Rt/tF5dfaZCdojt8O2fz6V8T+LNZ0Hx94hGqPpzF5XC+ZfE+RGgPB8pSNx9mOPavj+JI/W1Tp0mtG'
    '22fVcNYqngalSrWvqkkj4x8N+HNR1jxbDcaBYTahqSPiMW8ZkkUYI6gYUYJzkgV6Z8SvAXirSzb/APCaao1nf6s5'
    '8vT7Efa7+Uued+CETJPcn6V9oaX4+8IeAtFNnpa28coB3NBFFCWY9ciMACvnLxb8TNDvNcPiBIQ2opxHcMQzJgcF'
    'AeAR69a8vCZdDRz95r7j1cw4nnqqCUF36s9G8HQfDH9lnwbdm9unuNc1dFkuw7I185K5SD5OEWPJ9g2TzXyT49+N'
    'LeObl0m0mGS06Rx3Ms1w2M92Z+v0Fc14p1K017UZb/UHaeRySS7EmuU+321mpFrbofTjmvpMNhlCKutfyPicZj6l'
    'aTbZl6kum6qoT/hH7SPAxmGNk/Hg8n3rlP8AhEdOVt72rxc56Z/nXZy+JNWbAjRUUdAq1mz65q7gh/5V3xlJaI85'
    'owv+Ea0kKSp2sOm5f8KgOhW6ci4QD6MP5GkuZb6djvJ/CsloLyT7xOM1om+4uU0Zbe2twNupyQkf882Y/ocitXwr'
    '458U+B/Edn4l8La5JDfWEgkglMPze6sVI3Kw4YEYIrBi0YuQZfrzW7bWNnDy659qmUrFLQ/UTw7+3v4Hu4LJfEuh'
    '6jZ3DxoLua1CSQLLj52jjJ37M8gda+yfBXjvwv8AEPSU1zwfqMWp2r43eWcSRMf4ZYzhkP1HPavwQt305ODHXofg'
    '/wAbaj4RuJJvDl9cac04xI1vIYycdD8vpVLFST1Q7n7vBDnGD+NPCeor81/hj+1n4u8P7NO8YkeJdOzxOxCX0Q9A'
    '/wB2QD0bn3r7v8HfE/wP4+tI7nw5qcTSvjNpcFYblGP8JjY/N/wEmt4V4y0TNErnckVq2NyhQ2k+CjDAz0+lZTAj'
    'KsMEHkGlUgcitbExlZ3Q6eEwSmPquflJ/lUYYKMEZB7ValmEibjzjhv6Gs9mA9x2pjk+xG6jPqOxpoWkaRVBJPFY'
    'd3qEvKRZUevehysS5WRYvZ0Q7WIAHbuaw57lpOE+UVA5ZzuJz9abjHWpuYSlcjO7vzXm/wAWdDXWvBdyyxeZLYn7'
    'QgAycAYfH4GvSjTJY/NhkhOD5iMmD0O4Ec1yY7Dxr4epRl9pNHRgMS8NiadeO8Wmfhh8QbZE1GQbccmvJJIDvDxg'
    'jBr3z4kwtH4qv9Lu4mt5rWZo5I5F2spBPY449D3FeazWMPCxEE1+dYSpKEFGS1P2fEcs3zRehzXiKFhYpDMm5JVG'
    'Qeh44r5x13Srmxkdyo2MN2V6c9hX2f4r0bPhjT9TK4DKUb6qcV4FqkEE0bJIoZfQ17+TZi6adtrnz+d5cqtm9zwI'
    'yIsb+aSykAgHrmqUgV4/MBAAOMV6angufWLs2ukW0t1M3IjhUsQPU46D3NdVD+zz4zni8yVYbNSc7ZZMuPwUH+df'
    'XLNMOlecrHxc8BWTta58/tET82c56Ct3RNFu9b1nT9Jto3eW+uIbdFjXc5MrhPlUdSM5r22L9n7U4yBcanGG/wBi'
    'Mkfqa+9vg7qnw78AWehCXwXaT6vpVrDBNqybfOllQYadVYcM2T3rKrm+G6TM3g66Tageqfs8fsqW/wAEtZvPEF1q'
    '76pdTBUgXZ5SRoAeWQEgv8xGewr7CCGQsTnKDoP89Kdps9rq9jb6pZMJra6jWWJx3VufwI6H3q99nd3DMevHA/St'
    'GlLU8Co5uXv7leFHCgxrkgn73Qn6+1YtxcTeaYwozu+ZvU966aXeg2phVUYz1rAW1fzC7LuGc81PLYib0sZ8tqSx'
    '2hpNx4OOAKh/s15WZAuSMcsfuit1oJYQqxEknn6VG0siBkYcnknv7UJsyce5y8+neQzCU9Pu7f4qpraTE52dD6fz'
    'rqtzO+91yAevf86gdv3TRbeTzkH+dVzMzlBdDm7pWwY2PykcVmRqBIBL9zofpW/cwea2YVOAAOB+tV5rGTHnEDBz'
    '+netU1Yw5G2ZvmJDlo+MkjHtngVQu5mMgeLKcY4rSkh2ZP3sisxlKj9KSSCUbGQ0BkkO8n3NXrayRbSe5bkoNq59'
    'T0rRtrffPCr4271BHfBPf2omgby50jOIlkLAeuDwKJChFXuYyxPHDbm5lIy5bbjPygdT/SqF+5upQBkqhwB6Dua2'
    'JIBMXlkPQZx06DgCora1WRsZ+/ksTxhRyR+NOLSVyJxuzKOnRqiMxxu5wOoqtJAqZMZySSeeTiuiFtcXDkoAFUHv'
    '2HvWNOoBG0Y/X9aIyZlKmj//0v0Qf4l/DL4pxR+Hr7VYb+K7JzZCHy5CV5z8/II6gq2fSvmTWPhZrvhDxebbwJet'
    'd6NrQeySYsQ8BnQr5N0uMjB+6xHPHevk+GBoLoMHZGRuoJDAj3HSvtS78E3Fr8KY/H3gvXL28u9PtY9QuPNkJ3wo'
    'xL4TJ2mIgnB6gGvzWWKWJg2o6x10etvI7Y1P5j5s0nS7j7Rc3NykkdvpkZaZgDxIDsjjzjGWfjHcA1napcy3shkl'
    '5kb+6dvPsK+t9L8I39v+z/fz6tDE+q+Nruxv9PUEb3Vpolj44+b53YqOxzXF+J/AcHwp8Nf8JPr9o9z9qkS0Wznn'
    'CkM+WVpFiUbgcEhQ+FGM5rzVlU4xjNdrvyvt+FhtXPIvDnhnVtfsYYfD+mX1zqUcxWUxqXhMbDIJOBsYHjBOMV9x'
    '/CrQfCvw00aHVfF0Sx+IpGkV94MrxqrYHlKB8oI/i6n1r4u0T48+L/C9ysnhowWlsfvW6QKIn4x86dz79fesjWfi'
    'D4r1vXLrUtX1CaK5mctJGCUEe7kIE/hA9K0hUhRtWpxvNd1p6+oo26n6uaH8QfC/iW9bTtLuHkuUQyFWjK4VTgnJ'
    'PvWzeBXJINfl58P9e+IqX93q/hFrm5ks4fMu5UTzQkOc/vCeNp9K9p0f9pTxGut2sXie0tRprssc7QIVdAeDIDk5'
    'x1I9K9vCZ2500sSrPyWhWm6PtTw8yrqLxntG5rxnQrf7X41sIT937fuI/wBwlv6V7P4a+zX06X1pIs0M0O5JEOVZ'
    'WGQQR6ivLvDCLD4tNyMf6O00n81/rXvRV4w7XNYOyk/I+poJctgng14742uVvfGVho7Z+zWyieRR0Lt93NdpYaut'
    'xIAjVysthJd+Ir/UnGTuWNT6BVArtqSvGyOJ6HknxSvpvs0iwll8yVEBGR8imvSNOsduiW8aM2RCsvXoTXSa74C0'
    '/X4AJT0QAD3HetB9Lh0vR5zJ/wAs4Qob0CDgVgqTTcmdKnpynR+H9Uh1bSILqM5O3Y/sy8GsLx+Y7fwdrM56rZy4'
    '/EYrgfAzajo2nReeTsuZHmAPZXPH6VvfFq7Efw51WdT/AK2JYx/wNgK6JVG6Tb7ERjaol5n5V/EeeKPT9Hhi486/'
    'y3bOyM16/Yvi2slRcr5S7ie3FeE/EZiup+HtNf73nTy49sACvfbGAfZrTHaNP5V87LSx7S1bPE/hhMsnj3WGx/zE'
    'r4c+xxXe/Flmt/hx4mG5mD2kh57dOBXnHwgdZvFerz55/ta//wDQyK7/AOLtzG/w58UAqRtspQCe/TkVTT9qvVAn'
    '+5foz4e8VNNFP4dbKn/SojlSePk7+9feWlq48I2UoOBJCNw9c/1r4A8WXLR22hs3a5hxx/0zNffXh26RvBWlgxmR'
    'ngUDH8Jx1qc0VuX5jyTWM/VHzXp0/l+Jb6L+7dOP/Hq+ovCMmVjr5L3GHxtqMeel0/6mvqfwc52RE0p/ZNI7yPoj'
    'w8+JlNemoAU9a8o0WTEiGvUrY7owR6V6FHY86stR5Q9QKWNtpzWhbRK7bT3qzcaYQm9K1ejIWquJbzxkc8V6Tayp'
    '4g0ZYFOb2wXgd3j9q8eO+JiDxitDTtVurC6S6tnKOhyPf2PtW1Co6cr9DOtD2kbHXgsh79ec1fguyDyauW+oaJ4i'
    '/wBYwsr443Z/1bn2+tOk8O6jGcxoJV7FCCK9VOMleJ5coSi7NFqOUSClaMMKbBpeqJ1gYfXFayadfEfNHj8RTswZ'
    'zs1rkcVmvalTxXbf2Xcngqv4sBUEmlS5wWjB93FNCtc5WK3IIrQji5AUZz2rYTTMNiSeFF7neDWrGtjZj/RpoS/e'
    'R3B/IU7LqxJNmdBpIVPPvm8pOoX+Nqkluvk+z2q+VEOw6n6mnSmGRi8t7CSf9qoCbBet5F+tVeK6hyt7IrEGm4qz'
    '5mlgZa9T/vk0nn6OOt5+SGlzw7h7OXYrbfWjbxzVg3eiD/l4c/RKQ3uidfMlP/AcUnUh1Y/Zy7EOwA1JHGOZH+4n'
    'J9/QfjTTqehqP+Wx/L/GmSa5o7RiJY5toOeo5NHtYdGCpS6ladmmkMjcZ7DsOwFV8VM2raR0EEv/AH2KjOr6WOlo'
    'x+r1HtIdx8khNtLsBpo1uwXpY5+rml/t+1HK2Kfixo9rHuHs5C7RRsFMPiJP4bGH9TUZ8Ryfw2sA/wCA0e1gDpSL'
    'GPxpwX0qifEt1/DBAP8AgFN/4SbUf4VhH0jFP20Q9lIv7T0pwjbsCfpWWfFGrdnQH2Rf8KhfxNrPafH0Vf8ACn7e'
    'PYPYvubQikPSNj+B/wAKf9nnP/LNj/wE1zTeI9ax/wAfLfkB/SoDrusNybuT86Pbx7B7F9zrfsd0ekL4/wB008WF'
    '32gf8q4ltX1RvvXUv/fRqu+oXz/euZf++jR7ddg9k+56CNNvmH+pb9B/Wl/sy9zygH1Yf415x9puj1lkP/AjSGaZ'
    'ursfxNP23kHs/M9H/s65HLFB9XX/ABppsnHWWAfWVa82Lue5/Ok/P86PbeQvZ+Z6QbeNfvXVuP8AtoKbttF63tuP'
    '+BZ/pXnOM5pQMdqn2rH7JHom7T8c30I+m4/0qMz6Up+a+T8FauB20Yo9sw9lE7z7Zoy9bwn6RmnDUdFH/LxIfpH/'
    'APXrgQuakC0OsxqlE7v+1tEHSSY/8AH+NJ/bmkDgLOfwUVxagd6dt56UvayD2cTsDr2mj7sUxHuQP6U3/hIrLtbP'
    '+LD/AArkgvNOx7Ue1kHJHsdUfEluOlofxc04eJYscWa593JrlCvNShcUe1kHLHsdN/wkp/htIx9Sxpn/AAkknO22'
    'iH5/41z2KFUk0lUfcFFdjoD4juT0ghH/AAGm/wDCQ3p6JCP+ACsQJzzT9nTiq5mHKjY/t6/P/PMfRF/wpp1vUT0k'
    'A+ir/hWXtpQtHM+4WXQ0f7X1I9Zj+AAoOqagRzO/51SC96cFFF2BZ+33x4Mz/wDfRpPtdweDK5/4EahxRgGquK5K'
    'Z5j1dvzNAeQn7xP40zHFSKPwppisTAk9zTxmmLyalUVaZi0PHY04kY5pBzT6tSG1YipTUu0+lJsp3JsMUZFSbaQD'
    'HFPz2FK4mhCvpSrkEY9RUck8ER2u6q2M4J5x64rn9V16ztIjGHOZPlZkBOxf4m5wM46c9azq1owi5SZdOlKbSSPx'
    '3/bB0iLS/i7pd/fRs1rqkUd1IMn5ovOYbR7YGK/PrxndrFK7oADczM+3sMklR9FGAK/UH9su4h8Y63Z6lpnl+R4d'
    'tWhO0hhgkuqbh1KgDP1r8q/HEUv2aC5HJ3fy/wDrV8tgp06mKag7q9v1PrsRGpTwkeZWbRwtrqV2kElkkh/02ZFl'
    'Pcqp6fTvXTf2el9e7WUbEwqg8AKo5JPoOprioTi+T2l3fnzXZzXXl6XfPGcSbCufQZ/rX0lRWa5ev6nzsHdPm6FP'
    'U9YtY4jaWbbYc/M3QyEdM+w7CsBL2S6J8oYReC5/pXPwRyX14Ij90dfYDrW/dyx2tusUY2dSo7kY6n3NbOnGFox3'
    'Zn7Ry1ZWuLpIc45b3rBubqViS52jHTuagmmYRmZzkscLVe2ja5k3yAlRyTXTGmkrswlNt2R0+lW+YhK3Oeg/rVm6'
    '+7sdgN3BxycegFVPtJSPLHy4+mB1/Oq6ymUZi+VPX+I/SsWm25M16WRrWdmpUsFwoIGT1OfWvp34NWc2rSado+nx'
    'Ga5u5FhhjHVpHfao/MivHPCfhfVta07fYWFzc7pH2eTE77/LQs2CAclRyfQV95/sQfDDXf8AhOdC8a6nZumkWbzt'
    'bSSABZ7hHELBR1/dGTdkjqMV4mZU5YpKiu6+7qevl1eOFk6z7P7+h+v3ww8Faf8ADXwXYeErEBpYl8y7nA5lupAD'
    'K/0B+VR/dAr5p/Zk+M/izW/in8Rvgr8UNRa88RaJqEt7YPIAm+zDeW8UagAbUHlyKB2c+lfbhsCrkehr8zv2uNMv'
    'fgT8fPAf7UOiRBbOWVNN1pUQnzSgZHVyP+e1szAE90r1/ZRpxgoaKOnyPC9rKrKTqauWvzP09VeMU4r+FVtP1C01'
    'awtdV02QTWl7DHc28g6PDMgeNvxUir23t0rYy5WMUDHtT8elLtp/l4oHYi24pNnNT7DR5ZouHKVtnp3pNnarfln0'
    '4pNvtRcOUp+XwRRswKubAaTywfSgOUqbB70uznrVnZnj0oKcdqBWZXA7Vk6nrOnaSMXUgD43CMfeI9fpV/ULyDTr'
    'WS8uGVEQdScDJ6DmvhL4+/EefR7uDV7CYE2+YLglsII7j5VJA+8ysAVFedjcY6bVOn8TOmhRTTqT+FH0H4k+L2m6'
    'ZGwkuI7VQDznLY/Gvm/xD8cfCV5K8dzqbyjncASQfavgHxL451zXbmR728eVSTjsMfQVx3nTFss2M+pxXBLByq61'
    'pthLMFDSjFI+yNY+LHgOAn7BbGRuoIXv9TmvKNb+Kz3isljB5QPQk814cL2BfuEyvnooyMepPT+dQNc3OeAsY7Z+'
    'Y/4VpDA0lurnLPG1ZdbHV3/ibVbwnMhAY4wK5S5vLpyd8hyTg5NUZJZn3NLKzZO7j5RkdOBiqUiQDDMuSepPNdcY'
    'RjokcrlJ7ssvcjcVaRf++hUBuIgf9cB/wIUwPEvRFyPapBPngKvX0FWwFTVRHwJF49we1X49cG35443GeuBWNLOq'
    '9Y1I+gpq6hYg4e3TGfSp5fIo6D+07F2CvbLyM5FHm6ac5g/z+VYovtJIAaBR9OKlMukcBNwV+p3HI/WlYDUMumDr'
    'GR9KA2mZAVG59awZm0xH2vvI6/fPP61RN7ZlvLjRto/2zS5bgdS32TosZqEsmflBXFZUb2kuC6N/30f8asCOzbDb'
    'CO33jRyiNi1vpYsYJwK7nSfGV3p7Jk8rgjnBHoQetebRQ2wzjePoxqywP8EzAkcZANZSgmWpNM+5fh9+1V4p0CJL'
    'C+nXUrRMBYrwlnUeiy53fnmvtDwJ8efA3jWNIWul0y9bAMFww2Mf9iXp+BxX4mRyXMZAwsmOu07Tj6HitzTdektJ'
    'ABK9u4PG7gfn0pwq1IP3XddmaXi90fv/AOaMBk+dWHBBypB7gjrTDyK/Jv4eftIeOfArxWzzjUtNBG61uDuXb32N'
    '1U/Sv0N+HPxc8MfFPRZNS8Ou0c9sVW8tJcedAzdCQPvI38Ljr0616FKup6bMiUUtUeh3b5yi9O9ZUi7+tWNxY0hB'
    'IxWzZk1coGIg5xTWXAq6VyMYquyuDzgiobSJcSi42jrUZz3NWZBnkcVAQD1FIho5LWfB/hTxDP8AaNc0axv5QMCS'
    '4gSR8f7xGa59/hP8NXBEnhnTNp4OLaMcfUCvSyo9MUxkBGKxnThJ6xX3Gka9WOkZtfNn5x/Hb4Y6f4R0zUNI0xD/'
    'AGc8n2yxDHJRJP8AWRZP9x8ge2K+PPh18E/EXxW1qay0qF4tNsmU397j5Yg5wsadmmfoi/ieK/Yj4ufDe/8AHvhp'
    'dP0hA18JlWMt0CSnY5J9F4Y/Sul8BfDPS/hvpFn4W8OxIYLFS888pCJNduP3tzK3VmY/dUdF4GK+JxNCeFxVSMI2'
    'i9V8/wDJn6Pg8zjicBTlN3mrp/Lr81Y/O3/hXemeA7Z9B0Wy+yrASszkbppXHBaR+pOfwHauL1CNY5DHvA9QxHH6'
    '19j/ABe0XStP1yWyv7iS9e6QzsbdxGkbOT8u1Oo/3iTXzRdeF9OUlmtkKn+Lbz+Ncjk7tzMnboeXm3gYlpJIxz3d'
    'f8atW82m2zZN3AMf9NF/xrrJvD+nxjC2kbr6bRWG2iaKjkfZUQnqNoqoyvuyGrH0N8C/jJoOnXi+CdT1CKWC7mVL'
    'MofMMM8hxsIXOFc/ka+0JVVARjBzivy1s7ax0+TzbOFY33btyqAcjocjvXqvhz4geJ9JuEuYL6VgDgxzMXRh6ENn'
    'rXuYLOFSiqc02jw8dlDqydSm0mfcrkMflHzVHKgRQTw2c/hXmXhr4t6Fq4SDVYjp9wcDd96In69V/HNepuYbmJJb'
    'd1eMjKshBB/EV9DQxVKsr05XPm6+Fq0dKkbGaWO8kdMDFV2i+0Mc5471rLbK33gee4qLGzcoOQeMgVtdI5mjCuso'
    'ixYHy9x3rOkGfrW/PBGcAdD+dUGt0UMuN2ejDtTTMnEylJXcueGHWq5LvEUHQE4rZitVYkY3sCPlHX6mqjwiJnRl'
    'xzwD2p3SM3ExRamUbc4warR2ZKlVO5ixzGf9n1NdJbWM2WA2ke9UvKMdxJgE7s/XPenzE8hnCOAyxnAVnYeZGOgx'
    '0wazJE2iXH8THA9s10UsP7lsja8Qz+XesuKJxGZAAQM5z/SnciVPsczKrc80z5ljCOmB69622hRpVIPDDLcdKqTK'
    'GlJT7idz601qZShbUqRySJGY93DEbh7CqtyZJn3IgVRwAKtOpIzikEcrLnsKZi4n/9PmJ9Q8O3dnJPDJcWt+ZMgS'
    'BXtnUnpnh1I/EV6/8F/ii9ppXiXwAIXutR1+y+x2C71EKvKrRYfd0BMm4HvjFeMPP4Ov/CEGmCye21+2ui/22F8x'
    '3Fs+SyzIf40IAUj1r0nUfh94x8AaBp+qyw2l5pwuILwXVlIks0EsgXaszp8wXoOu0NX5bRUaU+an2/M7Frdn1LLo'
    's17cahp3ipftVn8ONMGj6Lp8DkfabuS2Aa5dh/y02soUdFOPSvi/U/FWu6hapo2sajdXVnatiOC5kaQRsuVHDfxA'
    'cV7NoPxGvZI73UtTYm41bULq7lwepd9ox9FUVR8VeFvDniKyvPEMkn9n3aJGtusaF2vbiRsiLyl5ZyuSSOnU16OY'
    '4N1KcZ0J7LXz/pWRKbehx6ap4O1rTTY/2DDYX/lhY72zkZEVlH35IWypHdsYrqtN+H3hbxh/aHiK68TeVeITNcWl'
    'tavOyoqhTL6lWxk9l71zdhP4fg1q10qz0a6DWijFvKwklvbhud02wcIqjKRJx1yTWDYzav4U1xtVtZWtLyCR22BS'
    'n3slo3Q4+Rh8pXpiuCjQrTi3dN+lvysW7Rtc/QD4H2jeD/DcEelLeXulaiGm2ywQwLJvOPMkzl2BA+UHtXX+JfBH'
    'w38Qyi9u/D0Ec8TAs0T7FfvtkVSAQa+J5vjH441rQp9astRktoLGMh7dAI/KMeB5YAGDjcp9xXgw8fa9czzGa+uJ'
    'JS+Svmv8zNzkjNevBxoYdRmub7vwL91bn65Q+LZPDmnQado2nQW1vax+XAiIAqIOgHNcR4R1WWXUdTvPLGERUbvz'
    'I2T/ACr5H+DfirV01cjU71porxfLNvNLli38LqGOFIr9Afh58PrkaPqF/qRFudQljaEDDny488naSOc8c16OArfW'
    'eWS0t07FuUVTbXUz7TVDbXqXYby4oxukBPAUdTXYeDPH3hjxF4jvPD9m26VovtKSZ4kxw4HuOtYPizRLOysZre1k'
    'y8sZRmfpyPT0r5q0a2uPBPiSHxBZyJHJBkAAnBB6jHoRXZUqypzVtjOEIyjrufetzcLYod5wNrEf0ri7ue91WMaS'
    'hLfa3AP+zHnJP5VgeFvihoviuVNK1NFt7qTiPJzHI3oD2PpXrdjp1rZTmfO5yMfSt4tVPhehMk4bmfqWjxraJHCu'
    'BEoVfoBgV4t8X7+RPAJsZDzLdRxn3C5NfRNxcIyFcZFfNPx+lii0XTIU4MlzI5H+6v8A9eniko0pNF4Z3qRTPzI+'
    'IEjP8TtF09clYrN5P++3x/SvpSzQCC1J6rGMflXzH4kkS6+NqxZ5t7CJcehbJr6hgKrbweyDj6CvAmtr9j1e9u58'
    'y/BGYnxNrUbH/mLX2P8Avs16T8YFc/DXxPnqLOTH5ivHfgRdCfxPrMi9tWvv/QzXr/xllz8NfEuzn/Qnz+Yqp6V0'
    'vNFQ1wzfkz4a+IN9nRtAyVKx3EPIGD9zHNfb/gfU8+ArCdDlliCgDvX5/fEORh4c0puhWeL/ANBr7P8AhbqZHgu1'
    'GA4K7ee2QOa2ziC5IPzZjkdRuU16Hj+pyPD8Qr9m43zB/wDvoA19VeCpQ8URHpXyh4wIt/iC56easbfpivp/wE++'
    '3hOfSuZ604PyR2LSpNebPpTSD8yGvVbA5jB9q8m0rIVD7V6npr5hXFejQ2POrHS2f3xXVwgPHtNcjanDV1Vs4wOa'
    '1qRM4MxNU0853qK5vYQ2O9eiTski7a5i7swGLrUxvsNmfbgibjtivQdLuJQgAkYcdia4W1Uec34V2ViSoHatI3RE'
    'tjoXMrrzK/8A30awbuC6YHbNJ/30a21Y7ahbB681rqzLQ4W4S9jPLuf+BGs1pJs/Ozfma9BmhSRelYdzp6nkCmm+'
    'oaPY5+KZwRkmtWK4z3qq9ky9KSOJ0NVclxNhXDVIAOlZ6bhVxDxQSyYgZ4pR0puTTx7UCE+tBOOKWm00Awmo8n0q'
    'UimEUXAj+lFSbeOKbjvVIiwzoaYfWpKafpTCwzJHFAoNOpjG4pKdTacWLQaRULAng1MT+FRsARVCIvek4x1pfekx'
    'xxQA3Gabjin89qB70xNEeMUpzTsYoIwapMTiN5paXB70oB9OKZNgHXFLijHenUh+gvIowDTsU4CmFhuMDFOUU4DP'
    'AqQL2pB6AAe1PxTguBRQIbgZqQLzSgHOKlAphbuM2AU8KKdjJp1AuozaAaMZ604CnBc8GgGIq+lSYOacFB608Lnt'
    'TFcZt96cQKf2xSY5poVhADj2p4FKvHWlPrVgxMUbT6U/BqTFPYRFinhTT8U5elAhQKco7UAU8VQNCinimc04DoRV'
    'Jk2TJaQ07qKM8VVydxlcx4t8R2vhbQ7jWLqSONYgFVpW2xh24Bc/3R1PsK6k89BXwH/wUB1fU9I+Hfh62tJmhttT'
    '1mO1uNh+bBjZtw9cAHA9a5sXWdOk5R3OjCUFUrRjLY8/8c/tmnStVm0v4b2VxrTrOIZLsozCec8nYuDyeqgnhe1e'
    'Wa98Ufip46DL4k1RdFglx5kcbZl2+hI4X6Zqh4w8ZeEv2ddBh0Dw/Z2+oeIprVJL+WTDrbyzqJGhXOfuBlEj/eZ+'
    'OAMV8XX/AI9+JvxGvJLuxhFvaqxEkwAjhX1+Y4H4CvisVDE4rTn5YLdt/ktj7fByw2GV3C8nsktfmz6q8b6zpl34'
    'WbwxoD/aZNpiLscvJKwySx7tjLMO3Ar4i+KenNpdz/ZFrHxHHEHAOf3qr+9P4scV6r4Q1+x0DX7O41fV4r2a1Y+X'
    'bIP3W84yXb0zyx5JAxVP4sabYWOrXXiq/nX7JHEklvbIP3krSfNvk/uB3OQn3iB2qMppPCYiNPVp637svNKqxWHc'
    '7Wa032R8sanajTVLS4Eqqq4/2yOfyq9HL9rtHZP+XiDOP9pRyP0rnL68ufEF4So2pksxPQZOST7ntWzGk1jbKXBi'
    'iT/Vg/eY+uPevvpq0EnufCwd5NrYr2EUen2klzKvzv2747CsXUZHmlEz8B04HpW/LGbmOBC2FYlifYVlX0bTf6pS'
    'FBHPTgcVtT+LmZnNacqOee2e4khhToo3N7VrNEkKBANoUZbH6CrtnEpDOp69T2AHYVUvSrbh0Qd/Wrc7vlJUbame'
    'h+0zfPyB0XsPrXaaZokt5bTSwRmQW6hpWUcICdq5+pIFcXEuCDnyl9e5r7X+AOgeFL/wZ4kfX7kWySQRxxSnJWOV'
    'ZUdpnx/DGmcA/edlArmxM5K0Ym1GK1lI/Sn9kb4W6f4a+CeieM9WdZDbW11dksoCW6lZXdcn7xOQzt6ALXU/sl2M'
    '+t+HtOvIoz9hsnvZC2MDdPfNLgf9+0H5+lZGu+Np/Gngiz+Fnw+ibQ/COnabEb+8kX/Sp7MBeEiHMYmk4QH5pG/2'
    'a+0fhL4NtPAngPTNCSBLeYRCSaNP+WbMMiPPfYvBPc5PeimvwMKnV9z0GORmOWFeUfHz4cad8XfhH4j8C3mxZby0'
    'aSzlfGIryD95bvk9PnG0+xIr1eQ8fLXyT8cfH+uPrK/DPSreW1a9ERN6Q2HDgsAoA+4CBuOeMVy5pmFPB4d1qiv0'
    'S7t7Hbk+WVMdiFRpu1tW30S3fmedfsVfHnSLj4RRfD/x/fJp3iHwTdy6JLFc7gzQRHMBzg/cGYzn+7X3FpPifw7r'
    'snk6TqVrdyYLbIpVZiB1O3rX8+njmbUvBXiyfxfZ3jQLrDiO+YHrdDJjlbsQ5yGPufWvf/Dni29GiaD480O5e3vl'
    'kJby2xie2Ybhx/CwxkdMGvnHxLVh7OpyJ05W73Xddj6n/VSlKM4Oo1UjftZ9n3P2vEeRmngEVjeHfEVl4n0DTvEW'
    'mMJLbUraO4jK8/fXLKfdWypHqK2wO5r7GM4ySktmfESg4txluhuccCl+tP2jvTtozT0IsRA0hBNTbaCuOaEOxDtz'
    'SYqfbxmm98U/QCLBPTml254AyT2qXFMmlS2he4c4Ealj+FJysm2NRvoj5Q+IWvXmv+LLkXchi8OeHXMcEKnH27UF'
    'H76V/WOHhEHQtk9q/M/4s+JpvFM+pxpKZFkuPJtEX+OUHdLL9EUCNfxNfX/7QvjVdE0q7+zfu5J2eOMDjBkJJP6k'
    '1+dlxeNDZyzp/rWBhiPdd/LsPfFfO4e9WrKvLvob4ySpxVFfM5eW+kNtEbdMscK7ngb+mB3NIuWuW+0OZWjTc2fu'
    'g+gFVI4zb3EqSE+WjCVeeOnCgdSfehfkt5LiTIadsAeteueQ9zRjuGlI7ADtUPns3B7cVbhtmj003bf3to/Ks5OW'
    'OTjnikrCCT5WOKh/hNTSAg+1RDpTAidSeRTA3zAc1Z2gketMaIZ9Kls0RMipKu1hxTJtLR87R9KjDNHWrbXAYY4P'
    '1qLvdDsctNpsyk47VnPbTrjBPWvSdsMnBAqrcWMbIxUAYGaftO4LscKthLKy7mJq4mm7W54Ndb9jVVDDHbp70pgj'
    'UButLnJMOK2YDBq2kJxtNWmdFz2IqPzMkhcDvRzAMztHNMLn3zQ2Sd3c80FSep6igqwhlZXyDWglxGyhZQGB65Ga'
    'yJjgj880xZcrgf8A6qhoInRAvbc2Um0f8835Q/T0/CvVPhD8UZPht490zxNLujtg/wBn1KDPE1nN8snThjGSJF7g'
    'ivFDMwgEp/hP5jvT5WjuYJIX+YBcj15GQRUp8rTNErn9AsbwSIk1u4kikVXjdejI4DKw9iCCKcfbmvnb9l3x4/jv'
    '4P6S90+++0XOk3J7sIADC5/3oyB+FfRQX3r1FK6TMmrOxEc9/wAqhYE9quY9qhcGkTa5RdQOlQFB2q4w5qa3S2RP'
    'tN9IscQO1dzBd7egJ4wO5rGtUjTjzSehVOhKpLkgtSjFbyyjcBgA/ePA/Os3VdS0fQ4zJf3Csw/gQgGvL/ip8V10'
    'e2FhopQsxZfOjYMqYO04x75GfUGvkHVvGmpXcjSXNw0hPctXzOLzqo3y0tF+J9LhckpRV6vvP8D6R8V/EvXrxzba'
    'HeJp9qCeYx+9b/eavJbvXb+TP23VZpj3y7c15BN4muGyCxH41kS6zJIeW614sq05u8nc9eNKMFaKsj1C51G0Zy7s'
    'ZCe7HP8AOsO71OFwUTGK4M30rHGfpT1mkbr/AD4qQSNssrnA6Go5NMjuF55Pb1FZ6Xccf3jn6cmrwvEaPKCXdjsK'
    'kLFB9HeNvl5AqRLaRRila8uT8oSQsehwP1qNru6AVGgIZzgcgDOM1QmmaUDyxH73Su88M+O9X0GcfY5zszzE/Mbe'
    'xBryp7uXG0oA3f5qi+0urBi6rj0Gf51pTlKEuaLszOpCMk4y1R99+FfHGm+KoNgxDeouWgJ4IH8Seo9uoroZAQPl'
    'GDXwdomuX1tPHcWNyYriBg0bdCCPpX2R4K8UW/jDR0veI7uAiK8hH8EgGdw/2X+8v5V9XluY+2Xs6nxL8T5PMsu9'
    'k/aU/h/I6DYzHgZpvlyMC6dvStaVRsCg4DYGf61WMUkYOB0Ocj07ivWbPJ5TKeN12XDnIY4YjqDQBFHO+/5wwG09'
    'a2fLjeMhMbTyR1rFlUwsO+Dw3qPQ+9K9yXAiE8du7eVyj/wnsfaqG3zjIV4cHcv1FXbqMunmL25NZynDBh2qtjPk'
    'ZDeP5keccldrD0x2qns22TDpuGPzrSv4uVde/WqLB3iEfAGQBTTFKBWit/LV5mIQNgL9AKzXtlMLHGPm5PqT0xXQ'
    'XAAgwwyew96rLbo21U4CDJPqTTTMZR6HPmNBhSMqKdLJEF2x9KtXKSFiowdvHFZckZHA5Pf2pmTgf//U+ctO8Q3O'
    'p6rcXckCQFkB8qEFUUoAvA98ZPua+iNEM7fD5tTt9SeNtUjayWzV/wDWTGTb5eznjA3luwFdlF8P/CPxIbVr/QII'
    '9H1aztbFrNRhYLlGLpL5oA6sygBx0OM5rP8Ah38KdavILm91SZNOTSHubKGIruLyo5NxIzdNmRsDDkgelfnFTCJu'
    '6WjPQhTknoes+HPAegaL4Nk12+1Cwv3GnTLNZSPtuLQHG2WPsZF4JHoTivFdQ8QO2m22rWEri8ikMVkeNscO0iaY'
    'Dr5jvgD0UV0Pi3w74n0zw5ca/JbmPSvJLeZn5ipwqsU64JIrhNLtbSe68O6RqNu+nxXKI87TnaZIwMsefuhsED/e'
    'NTGnUjCSLlTd1yo774baJq9zK3jy6v5LO6LSJb4iVzIhADyDd0yeEx2rvPiV4duPI0vxPf3r6hL9pgtZt6KpWGbO'
    '3O0c4fA59a6yK9sQkaWiI0SKqosRG1VUYUDHGAOgrivHWsX+sWiaDpOWka4jdzH8zK0B8wBcd1OC3p0rtfs6FCzf'
    '/Dm8sMuU8s1mO503S9V8LxRrEl1cxzuGH71SgxgYPRhjOfSvLLOxaGZmk3ruPziMAFiOnzGvouz8K6kITd+JPscF'
    'qW8yd5Bmd8nJLSE9T9c1k6j4J0+8lMvhhpIoG+/9pH7r6pn5zXmSrYuMW46rt1M1hJPY4rRtAv7+zur7SVR3s9uY'
    'WlAmO/8AiRf4sd+a7PRvid408LBItM1e9szDj900jcY7bW4x9RR4S8JeLP7ebS7C2jeW5RooikgAYj5+CfpwDVjx'
    'F4H8QXUklzd2MwnQbZASCxIOOCOCfbgV50p1+ZVJJrzRr9WlbbU+gfDv7QU3jPR5bDWUSPVoF/1iDas6f3tvZh3H'
    'TvXGa94guJgShLAcfia8F0vw5qOnTi/ty8ckLdCCpB/uup5Fetw+RLZJcyErLKMsh7H2r3cNmiqrllK7RpTwsuiN'
    'HSNVvftkLROyurBlIOMFeQa+jofjLrkFxB5t1u8xFOGHGRwa+UJboW6l0baQe3auZ1XxVK11FFE/MYOT9e1ephMY'
    'lOyHiMI1C8j9XfBfj7TfFduISyx3ijlM/e91rxr9oW/EUmlWwAJCSvj6kCvmD4f+LL9LmGe3lZJY2BVgccivUvin'
    'rtx4jvNPu5/vR2qRsB3ctyce9d+IxPNRZzYahy1UfDEM4v8A496scAiNIowP92MV9RbvkhduCsbAfiK+N/A11Le/'
    'HfxBI5yFvZI/wUYx+lfWOo3csd0kSL+5ETlmPYgcVwVNJJPsjrhrFvzZ8wfs7fNrusN66pfH/wAiNXtHxkcJ8N/E'
    '5B5NjIcfSvnb9nC8f+29VOTg6het+crV7b8VLW4/4RHxXc3U6tFLpcgijBzjA5OKmtpiV6o1o64Z+jPg74mXTf8A'
    'CK6W3GDNEf8Axw19WfBq+M/gyNWOSjAY+oFfLnxTt44fBOjyMwO+SMj/AL917l8Fb9/+EdnggyzrGsiqO+BXbnMf'
    '9ni/NnHw/L97L0Q74jx+R4vsrroJYQP++Wr6H+Hdzugh+gr5p+KVxP5+lXsqFHDmNs9s4Ne3/DPUEa1hJbnArzof'
    '7vBnpVdMRJH2JpkvyIK9R0lw0ArxbS7jdGjA9hXq+hzbol5r0cOefWW53FsSWrdhnZRj1rn7Y8itQNgV1tXOZM0T'
    'N71VllBBBquWqNmzxTUEDZnJKYrpyOmRXb6ZcxyqM4zXBP8A6+T8KuW1y9uwKmhR7BfoeoZ446VGTn2rFsdSWVQC'
    'a18hue1WjOQ0jPSomTNSkgdKZnvTEU3hHINVjbrmtE81CRRYXMUDDjpTdpFX8DFRsgp2C5WBOeakB96R1qLmgVif'
    'ORSHFRg07OaADtSZzxSE8U3NMTFJxQelJmg8nFCYrCcYphWnUlUFhmKDTjjFIR2poT3G5FMYU6mtQu4iPJzyaTNI'
    'fpRiqBiEY5pD0pWyaQCmIbikxxUuB+NRkHOaYDKWlwBS/pTQCCnUD3FL+lABz1pQMml9qUZoJF+lKBilx2pcVQXH'
    'AVKopijnkVKopBcd0oxnrSgHNPA70CegoGO9Owe3FJgU4fnTCwtLtzSgY4xUgpWEMAxT1FOwB9aUc0waFA9Kdtpc'
    'D0o6UEgBntT9macoyKf2wKdxMZjtRtNSAUoBY1SY0RjHen4p+0elLimncVhu2nDjpT9ooqtwDFOAI60AU+qEJjPW'
    'pAKaOelSAdKYWF7UYp/0pdpp36E2GqgJ56DrXwH+31A8vhfwXdeSJ4rHxJDcyhj8gWKIuA3sWwPpX327+WnpwWP9'
    'K+Ff21DJq/wj1OSABpNMkguyO/l7zG2B7gkfnXh5nW5ouCPYyynyzjNn4teIr6+8Z+J59V1i5Zbe4uneWZgSdhcl'
    'mA7k87V9MVc8c/EGyv1/sDw0i6fottAkcUbqPMOwfO4K45bqSad8StLOgtZ2NlJvZ7WCRj/CZJYxJIfpuP5ACvDX'
    'ilEjPKTJK33mb+Vc+Cw8K6jVlstl+p3YzEToOVOO73f6EAv5/tST2TGIRMHV/wCL5TkH/wCtXdeLtV1TxHp+macX'
    'BAVVmLtkvITnzD647k/QV54qSyy+WnCKfmPQVuxalGttPIuGblAx6jYMgD2zXsVqEeeE4rVHkUa8uWUG9Ga1npWl'
    '6XZtdKQ6QOUX1kkA5J/w7VwOt6jJPOzyNuZug7AfSrQ1mT7MsAbKmN3C/wC2zdfrWcdKeRlmvGILnIT+I11UKPI3'
    'Oo7s5qtXnio01ZE+nPLLbmRj0+RSegHc1Vu5llDwocRqwBPr6/maS7n2sbaD5Y4+Dt7mlsrZ2P2iUYA5VT6+prob'
    'suZmS/lFkf7ParEo+ZuSKyJmYHLnHHTqRWq4a6mwgJVfvP2+goZIYss4Ue5qFaL1Kepk28LztkgqPU9TXu3wYlsI'
    'vFthpHifUryx8L3N3BJqhtEErlYiSjeWeGw2OD9a8hsLebULlYrdS24gDjC9a+lPAHg4NfRWiqZBDKst5MVIX5OU'
    'hTPqeW9sVyY7FRpx8zfDUHN67H77/DP4b+Ff7Ostd0VY20kst1bJ5gmkuZduEuL2QfedR/q4+Fj9M17/ABqAPWvy'
    'N8AfEXxx4Pukfw7fSW9sceZC/wA0Mn1jPH4191eAfj7pOuGKx8UxLpl02AJ0ybdz7g8p+orlwmb0p+7P3X+AYnLq'
    'kfejqj6SWJW69K+XPjz8TLfw1rGneFdMgjku55LYXUxUF0hmkC+WhxkblJ3Edq+o7eSC7gSe0lWWJxlJI2DKwPcE'
    'cGvlv9pzw1rV9YaFc+GtHe91CW+RZru3h8yaOGMqVRiBkIxJ59qx4h9rLAzdF66ed1fod/DCorMIKutHfd2Sdt3/'
    'AJdz80PjbpS6bLrUVrDFM9hJcPEk0YlQmB2Kgo3ByBXD/CO1vG+GcWoXvmb9RvHubaMjbFHAo8tmT1Ejg49Ate1f'
    'FZY38a6zbzgPG91OGXqCGZsj6HNcteeJPtdna2SQx28dhbpaRJCoRFiiG1AFHAwK/PnX/wBmVCK+1f5H6POC9v7e'
    'T+zb56H1h+zT8eNK8Exz+CvGMzRaW8pmtpyC32WR8BwR/wA826nHQ5Pev0jyjqrxMGR1DKRyCGGQR9RX4P6RZS39'
    '5F9njM80kqJHGBku7MAqADruJAr917G3uILK1juUEcqQRLJGvKo4QBlHsDxX2fDOLqVKc6U9o2t876HwfEuFpQqR'
    'qwWsr3/DUtKtO2ijmnLnvX1Fz5mw3Hanc04j0pMe1BVhCMnNJj2qTFNwDRdk6DMYFcR481T+ztFMKnD3Jx77V5P+'
    'Fd0FOea+Ufjx46ttK8S2fhO1cPqVzANiZ/1MQBeWZh9OF964sxm40Go7s2w8V7RNn5z/ALQniRta8VJpEMm6OyyX'
    'weDI/wDgBXz7fqVCQ9l5/E1va9qSap4n1C8VywkuX2k85UMQP5VzRMt/qSwRchnC/hXPh4KEFHsefiJ89SUmUdbg'
    'hsrmw+Ub5rcK2eTuZuCPwrFu5xPerEo+VcBR7Vf8TT/bLyRoW3PbTrCcfwqBgVStbOVr1XkA3NtOPQHoK6o7XZiz'
    'qNVb7LoltGOpYtiucsyZG3HkntW/4zdYWtLBMbliBb6ms3TrcL8zcnFEdtSWMkUDAPrVFzj8KsXUhV2XpzWazFj3'
    'yatIROJiD0p/mZOSeaqIDnnpTGfnjNJq5a0LTyAiq4nKH5Tg+lNUlh1pGi5JAqVoXfQ0YdQYPyavrfoyld2eorkp'
    'A6HIzUQnlXnpmk4JiZ2QvMoNpzwKrNdybeSRzXORXhGVJ6VbScKuS2c0ctiTUWQlufm4pyHHPpWSLnaRtNSCdiT7'
    '0WA0ncDiofOwRiq4JOSfxqCVsD3zSaGmixI5PHXmmp/Oqit1yaso3y57ipZaLZO21dW/gIce46GokmVGWMH541yv'
    '/TSI9R+HUU0yF7N7iAh9mQ6H0rFtLj7dp6zISJrSTGR12mpsXbqfoh+wd4k8nV/EvhGV/lu7SHUIVz/HbO0UmPqj'
    'jP0r9KscV+KX7KPiOTQfjf4TleTEOqT3GlzHpkXSFVB/4GBX7ZgDHPHr9a7KL92xE1qQlTiomHarZA7VC68VozNo'
    'wtY1Sy0XTrnVdQbZb2sbSyHvgdh7k8Cvn/WLjVrrTG8f+LyYjMjLoekMSI7eNuPtMy/xOeqg9+T2r6A17SrLULFP'
    '7TXfZwzJNLCf+Wxj+ZI/oWwT7CvjL40+LrzUtWe1kl+6ACifdQAYVAPYV8lnlaUqvJfRfmfV5JRUaLm1q/yPEtf1'
    'lmuNkbFiflb/AHfTPqe59zXDXVyA25DlW6fh94fQHirN/Lgkt1FcbcXRSQjdjcevp/8AWrx1C568pWNaSfdUkZH/'
    'AC0O3PQnv9B1NZH2rYB5Sjcert2+i+v1qaKYBidxZ+7Hk1ajZGbepti4YD5F2kHgtzkfTtTXmZjz831NZYlLZ5py'
    'y+nWjl0JbNUSsQMcfSr1vclTyaxY5sjmrMbg81m4iudBKpnUGJtrDkGsW7l1CJGSZdynow6qRyCPoakSeSL5kPIr'
    'Vt722u/3NwAretCdhtHLpdNcx+f9184kX0Ydf8akyOpbmtS/0aS3nFzbfNFIMSADt2P4VnSWk8Zz2FaXXQhotWk7'
    'wyBh617X8MfFZ0LxVaSu2LW/xZ3QPTDn92/1Ru/oTXgoYgZNathdlTsZiPQg8/59K1oVHTmproYVoKpFwfU/TN1A'
    'k2yAlRkVXyeFXqpyPce9cR8K/FT+K/CUEtywe8sG+y3WeSxUfu5D/vrj8RXoTQgAEDBPIzyD9DX21OopxU47M+Lq'
    '05Qk4S3RkKxidozwrdD6e1MuIlIC+prUliSSIuF+YdvWs9otyeZn7uOK0M+UqRxK6+WzFG7+9Zd1aNG5B59xWzIg'
    'LFOeD264Pem7PvK+DjHPrnpSYOJjzrutVbqQQKzAShBxuxWo0bIksf8AdbNRJEpLbh0wKdzKSM93EpC4wPSpZgIY'
    'QEHJ4AqWOEK7v1K8Ae9Vm3CXdLzt6AdKbZLhczrm1McYwfmY9B61nzL5eFxkjpzW5MWd2x34+gqt9l43OOajmM3A'
    '/9XtPB13Y6DY+HdWaUxx3el3FrM7AgGeG6BCZ7kK3612/iHxvbWWmDSYGVZdTkMI2/eO/wCaQqB1Zs4981T1XWPA'
    'uteEh4M8Pbrmw0LxfprWlw5KySWOsuILgEjkBZkCg+mK5X4wabP8Ivjvpk15o7RWNna3cuh229poZrpyLe3cM3Jw'
    '7ByDyCMV+fyk/ZyUH8/vPWh0SOp1nx/rl3o40rXbaOSzh8lfK8vYSIWUqrk/TkV5b4zk07xdqB1N5WgECiGCMYzt'
    'zlmbtycjHbFfbX7Tml6T4S+CzQwQRRX15d6ZZrJgCRmeZGmbJ55Cnca+b/Hvij4SNPp2gzRQQ3tubwapqOlRbgpj'
    'Qm08vna4YkCT6Vx1aOIhF05VLvTf8jqjXjFWex5BaeLX8PJJomgBi04G+cksVbHVB644z2r6w8DeEPs3hSLXEVIo'
    'pbFW+0zkD92f3k0zHsCe5PQV5P8AFfRvANv4R8NReF2h0bUYNOkvr5LpwbqaK5wYN0kYIeWQAskYwFU84rwXTvi3'
    '4s0PS7bw7b3AuNKs7hrmOyuBviZjgqsgzlo0YbhGTtz1BrKCdOpy1ne21jGOKtJykfYVn4T8TfEC6he2tJf7HjJe'
    'GaRfKSXHCuN+Cxb+HAwBXYn4QeJlBWC2jAHAJlBr5ys/2vPiGdMtrMWln9qjkYzXPl4DxfwRiMYVdvc9T7V9V/D3'
    '40J490mOdp7a01GJdtxaYbgj/lohzyh/Q8V6EK1CT5ebU3o4xNmBpvwu8d6Tqlrqlktuk1rKsqbpOpU5weO4yK7r'
    'xrp8uj3Ul9coPs9yd4YEFQW5Kk+oP51vXeq3mBJO6bD3BbH86r3PgC58Wad9taSZ7eXIIjlIHHtTcFKLhTTZ6Ea0'
    'ZNOTR89a14j0I3Ut0yR+ayBXPHzBRgZHt0rye/8AEumI7lZFRckhQeB7fSvcde/Zh8LXbu093qluzZz5cxwPzFeZ'
    'XX7IPhSWQn+3tWUf3WbP8q85YWEZc0nZnZHl3hH8Tye58QXOrzNY6Sv2iQKW2x4JwOpNcTJriwXHlX0E8Lg/Mzxs'
    'AT/hX1h4Y/ZX8P6Jciew1i4DtgMWJBI9DXsv/DO0DoshY3CkZzwc/pXqYS0buKucmLXPZSdj5Y+H2v6UZIwlzHkk'
    'cFgD+Rr2XxTrdvHPG5njRY1TksMV6Va/ALSoZFE1gGGeTsX+dXdY+DvhEOIrjSpHAGOvFdNSs+WzRzU6K5rpn5T/'
    'AAu8R2EfxP1q/uZQnn6jdEM3APzHHOK+mtS8aaXFO6vdB1kUhQoLY49q+grT4O/D+K/b/iSzQ/MfmUf/AFq60fCb'
    '4chG8y1uBwew/wAKyniueTko/iaQwnJFRcvwPy5+AuqDRtX1Eana3MKPcXLKxibDB5CRjjvmva/iDeR6t4S1qw0q'
    'CeW4vbGWCICMgbip2jJ6V9e2/wAKPhzDKTB9qVs91H+Fbi/DrwYkMi+ZcjKEL8o6+/FTPEylU57L7zSGHhGnyOT+'
    '4/Frxd4R+IPibw9pmjro7xSWrruZnGGwu3gV7j8JfDXjHwpApu9MLusewgMMHjFfoZcfDrwgdoWW4JQ5Hyd6vW/g'
    'O18s/Zo3ZexK4rbE4yrWp+zklYyweEpYefPFu58D+N/DfibxTBBC1mlqY5Q4LNuPH0FdF4M8MeJ9LESSRhgvdSa+'
    'x7vwHKHXFu5x3CmtKx8JGDBa3YY9VxXPS9oo+zWx01XCU+d7nFaHeSQW6JcRuGHtmvZvDl7E8QwwH1qvbeHoyMeX'
    '+YrpbLQ4I0G4Kv1Ir1MPKUdzza0Iu9jqLR84IIrWR/WuYitbWBsiZV/4GBVwXdsnAvE/Fga7/axOJ0pdDe6800is'
    'P+2LWL711C3/AAKoZfFWjQKzS3C4UEnHPSq9rDuL2U+xdcfv5PwppPOKz7PVtP1aMXmnzLNFJyrL3q9n1q4tNaEu'
    '60Zat53hYFT9a7Gx1BZFAJ7Vw2RjNWoJ2iYEU7Eno2QRTc96ybK9EqgMa1M5HFCZLvsBNNY+lBPpTOMc1diRvIPP'
    'NNJNKfekPSi/YQw9OagI5qZjgVH+FSxke05Jo5HWpajI5oH0G9RSEClzSHrmixIdqSlNAFNsBKTvTzmozx1poAOK'
    'Q8CjpQeeaoTG57Ypp9qdjuaKokYVqI81Mc1EVJpgMFHNL9KXoMUAJ0pCPWnYpuKYhtGO9Ox6UY9TTEwwKUClHSnA'
    'A09wQ3HNO4pQOacMCgGxQBingGgCngGkwEA9qkAyaQY6dakAApAl1FxxzTgKTrThVCYoFPUUgIFPBFK42HHSn4A5'
    'pMA1IOtUT0EFPHPWjFO9BQDDOKAA1LtFP7UCEGRxTgccUg57U8DmgXqOAp+B2opR61QgpwHPNKBxS1VwDGelLtNP'
    'UCn/AEpoH2GYxRjIp+Cadt4qxDAO1S4pcU6gQgp2CKcB6VV1K7TT9PuL1+BBGz8+w4H51MpcqchpXaRQups280oP'
    '3m2L9F4/nXyv8YdHtvEPh3VtEmOWv7SS2J7AEEoPwbBr6KmuZf8AhHrSd/vyQiVgPVxn+tfLfi3X4jqLWtzKquU3'
    'qCcZGcHGfT0r5bFzutep72GjyvQ/FL4mvdwa5FpNwp+0xJFAwPYoduPxIH4VwPiCxtYtRGm22fMUIk3cmXGXxjt6'
    'V9LftFaPa2/jSfUrfYFlu4pkYMCW/d5dQB2Vh+tfLuoQalpl5Lql4pSS6hE0JbqRPzvH4dK3y6paEEnsn82aY6HN'
    'KTl1t9xzmqGKFmtLbCiPiRvf0Hv61zttwZIT0bDflwf0q7bK+oXL+blbeIF2buff6miYKY3mgjCIvGep5r6SCSXK'
    '9TwZu75kc1bK9tdlcbvLyBn1zwa62GMki9mbIVCWZv73YD6U2GygeSO+lHysvzKOrMOMD61W1O6MZIbqB8sY6KO3'
    '41pOfM0kjOMeVXZCYY4/njXe7AMc9F+vvUBnLqLZDukkbkj09Kq3N65iFtFnLfePck9aSwUWwe4c8/cB9CeuPeqc'
    'bK4J6l6QrZQ4JJ5xjjk1i+YbuTY3Q9AKC0t3OqHJJOFX2rsX8PT6RHYanPFiGeXym68huAT9eamUowXvbsai5arY'
    '9V+HfhWBtDlv5Rukd440VOGJLBuD+AFfY/gzw/Dp1knmqrSyEySEd3Y5P5dBXzn8Jc3Fqli6/NDMxJ/655T+eDX1'
    'haEQQqoz0r4zMKs/aSTZ9BhoLkTR1duYkXbxzW3a3wgxgggVwZu9uMcU+K9lc+Wp59fQdea83U69D6d8A/GLVPBs'
    '6LbyGWzdh5toxJRh3KddrY7j8a+4vDnjGx8Y6INb0KQyQsHQqRh45EHzRuOxGR+HNfj8motM3koxUI3Xpn0P/wBb'
    'tX3J+yn4o0q0v77w9cSFZNT2yxox+UzxA5wD0LJ+eBXsZTjpqoqE37r/AAPOzDCRdN1YrVHxh8U9LnHiW7vGXHmT'
    'Ox/Fia8gmiKsR6199/tH+AU0zVLq8sl3QzkzIMdA+T+QPFfA9+sqXYjxzuxXxUoTpV54eW8W0foCnGvh4V4bSSPp'
    'r9lXwkdf+J9hdXKb7bRUfUpAenmR/LAD/wADYN/wGv1mWQyDJ6mvi/8AYx8Li18Jaz4omXEt9eLZxkj/AJZW6B2x'
    '/wADf9K+0lVV4r9G4eoezwak95Nv9EfnWf1ufGSito2QYPagCnZ7U4cV7d0eNoNxQc08Y+lJtzSDUaOetGPSnMCO'
    'aiaQKMCqYrDmlWJWkxuKqzBR32gnH49K/G7UfEmveINS8d/GnxKCknkvZ2at0V5W8tI0Hoi8fXNfsPPLHb28t5M2'
    '1IULsfZRmvyY/aY1KysfCdrpVhGttDqV/NciJOMohznHuxJry8xndwprqa042i6j6fmfE+l2juHuG/hBJ+tamiRR'
    '2aXeqS/dtomcf7x4FEciWmktj70hx+FZWq37Wnhl4zw12+P+Ar1oi76HmONtzgNIl+1XV+GPzSKZD7lTuz9cV3Oh'
    '20LXULsfkhG5yeOF55rg/B0Dz6s+ejRSZ/Fa6a4u/sWmi3tSBLdsEbGThR978Sa6572M2V9VujqutTXzZK5wg9h0'
    'rc06zlly5GFAz7Vmadpk014YgDhcbm/nXZ319p2m2TWkUgMpQjA5NTJ9EI81vJwbtlHY4qPjmqUj+ZOSO5q1g/jW'
    'tgY5SN/qKc8QIDLVYkg1ZSTPFJMb2I9u0ZxU6nse9ByQewpg+XHPNRIIvoSNCrqTxWfcW23tjvV4Owz6UrHevIzx'
    'U3LZz5jIcgdx/WpUROAc8+taTRAshXnqMU0xsp+YDFXckbFAhCmrXlop+9SJyMYqTaueetJgV3dRkD0qhJN1rQdM'
    'EnbWXOuMjHWpGhA5z35rStiSNp6VjKwB681q200SkMzgUpI1THWoa0vWjc5huBsb2z0P4Vz2kstjq95pkpx5iMMf'
    '7S8iuxvLVru3F1ZkMV+8o5I9xXnPiE3EOt2d+OGmXn/eThvzFKCu2mNPQ9C8G+IH8P8Ai7RdS3/Npd9Z3wI4wonB'
    'P6V/RGJI58XEJzHMBKh/2ZBvX9DX81tnGLi+NxGcrcW6H2GGxxX9I2ggL4f0pW5YafZgn1P2dK2o7tClrqaAU9aU'
    '4PWn47CoyAXUHpnn6DmtJSsm30FGN2kjhPiDrsGieH5b6bjYGCL3LHgH6n+VfnN4puZRv1zVm8v7W7GIH70nqVB7'
    'D16V9XfGj4h6DoimG/QajqIy0Fhn91Hn7rz4/RPzr4bu59Y8d65Jfak+9j0UDbHGg6BVHCqB2FfAV8R7Wo5s+8oU'
    'VSpqKOcvNQ81Gl27Yx3Peuet4/tc7TP9xeg9+1bevLC9yLCy5iiOMj+I9zVO5iNlarDH99+P/r1cNiZrUzpC0krK'
    'vTO7jvjANOiYpM2fpSoRGBH2Xpjuff8ArS6fEZ5/n5y3071dtzJssCUrgEY+tKZCBmpdQCRXJVTntUDoRDv96VkL'
    'mJEkIIINaUUoABNYKNnrV2KQAc0mht3RvrLnBFNkTPzx9az45Qj89K1ImVuhrPlsCl3JbTXpbYhJckDsa1DdW9wr'
    'ImDtOR/unkfl0rm7+zEkZZOe/HWsiO4kjG0HDL8v9R/hRyp7Etm/dJknaMCqEblJBjtVZbq4POc5FJvJO7BzWiTM'
    '2fRnwP8AFv8AYnjW10u5fbaa6htXyeBOgLwn8Tlfxr7hkCKO4+n+Ffk7dXlxZ2H9p2jFbjTpI7yJlPOYmBP8q/Uz'
    'Q9Zj1vRtP1mMgpf2sN0pHT96gY/qTX0mU1b03T7Hz2aUUpqp3LDuQQeg/Ss6UHD7R8rHPHTNa55BVEBB656VTePy'
    '1KEZB6H3r1bnlNGcxbKyEZJG0+9RLtLnf91gf/rVfVN8ZTuDkVRYYkDdgefY0r9RJFK5Ty2JPRxiq8WGcsx+Vcsa'
    '0bxAyc8jmszlY2UfxED8KfMQ0VgZEBwPvHP51GF3MAy8VeJVsH06irIjAG49TSEY4iwd23vS7N/JGMVo+UzHd0FM'
    'aDpzSJaP/9bjPDvhjWrkaHL4bv1Gp6pqK2U9lcERRrJDItzaybzxsLR5yejD3r6/+LvxV0Px58f/AIaxqbGKXRII'
    '5r0Xx3WtveSFpZlmYHlY2Qcg88V80+Nf7I0rSotRhvoorhHW5tow3zSmBwJAmO4DEfWvNY4bW/8AjVpaLKJrTUoo'
    '58qc7o2hJIOPcc1+XZbipyi01pv93/DnsUKcXNRf9XPtD4w/FLwz8R41s9Rtsf2deC/utSaYtDNb2PzeTZxsAQJ2'
    'wozzg5rzjxJoPw5+IXx60qeS4fw/4UlsLaTUJzF5UYeNM/Z1K8KXHyl/UGvOvirNojeIfDfh9pEtLW6nH2p+ipCG'
    'UEt6DrXmHjXxjcQ61rUGmz+ZYXQis4ADlXLkjep/2YlJz75710+1qTqKyTvr+JtiqVKE3Hov8j6b8MeC/DGreDPE'
    '3iH+0lnlvZ7nTPD2nMRJK1vHLsjuJS2SmEHytwcA+tfHWvwXXh/XLnRL/Hn20hQkfdI7MD6EdK9Y+HGqHVg1qEkT'
    'S4ojEzRZWR5G+9MhHTZgBB6ZPeoPFvw88U6xfHxBdzfbobmT7El2ELSxyxL+4imiUbsyAAIw4PWolSSdnZGdbDqU'
    'E6KuzkfCOjar4n1QaRpUXmTlTIQSFARSASxJ6DIr6g8G/BHxDYOusz+K7LQ54zmML5s0ufcIAAPxNed6b4SuvhB4'
    'YbxLeywXHidlUmyeQB4opDyqqOSw4JPftWprHjyym1e0li1S8vbFreGWQxMItkzZLxlCBwnQ/oa4pwd20roqnh6V'
    'NJV37x+jfgLxb4KtPCtppHjG6tbrUbQGO4niicx3BDcSqGGVLDGR2PSvQx8T/hpY2n2OyuGWIdFjiYAfSvzen1H+'
    '0bCO+8NSMYWyQ6HJY91buCPQ1oaNrWsphNYRdp6PkBvxFdFDOKtNKDiu17HfSwlGUlo7dz7zm+K/gIjafPlH/XP/'
    'ABNZ8vxN+HjLn7JcMf8AdUf1r5OS/tCMmeMf8CFD6np6ctdRj/gQrZ4+q90vuPXWX0ls3959Ny/EzwPGd0WnXDfi'
    'oq+nxz0S3jEdvpcxCjAy4/wr5ObWtLAwbmP8DmkGt6X2nBPsGP8ASoWNrL4fyKeBoPSWvzPrL/hfVrjKaSfxk/8A'
    'rVl3fxyeYlo9Ji/4ExNfMo1zTz/Gx+kbn+lSf21aHokzfSJqHi8RLd/gCweGWy/E98l+MV6xJTTLYH3yazJvi5rM'
    'gIjs7Rc/7Ga8WOrKfuWty30jP9ag/tO43Yj026b/AICB/Wl7Su+4/ZYddEevf8LK11jkRWqfSFajf4j+Ick5txkY'
    '/wBSn+FeW/a9VYZj0qf/AIEyioHk8RORs0o4/wBqQCmvb+Yn7Dsj0tvH/iR2/wBbEPpCn+FTp458TMMfasf7qKP6'
    'V5lEnig9NPjX/ekq8tr4sYcW9sn1ZjVqFbzIc6PRHoZ8ZeIZBhrx+foKgOt6rOcSXUhz6tXErpfi9/4rZPwJqb+x'
    '/GOCVuoAe37utY0qr3M5VKa2R2Bu70/enkP/AAI0pupj1kY/ia4b+yfGWP396B/uIBTToHiKU5bUZB9AK6Y0Z9zm'
    'lXgdyzMwzuP51CzFcsTXEHwprbctqU/4Go28FX8/yNf3Bz/tGtlRZg8RE7KS8C4y4H41RuLuBopQzjlW7+1ck/wr'
    'Nq8Wq3F/ct5Msb7DIdp+ccEe9d1e6bZ+XMyxrwrfyolSa3ZUKyktEXfg87jSljYkoWcjP+8a90VuMZrxP4abU0yD'
    'AwOf5mvZ06V7GFf7tI8rEazZZGM8VKBUKmpwa6jmZat52iYY6V1VleCRBk1xwIqzDM0LZB4707dSbnbk0zNZ1reL'
    'IoBNXdwNO5LQ7ODzTSxxkUwmjOOaNgEY9xSZozTCaNxC7j2pDjFNJGabmhgOP86OnWm5FBIpoA4NPFQ55pd2KdgJ'
    'GIzxUJyetBbPWm0wH9RSE0maX69KBMO3JpKCfSjp+NUkSNNM71IcUw1QmMFB9KWm80ALwKKPaimgE+lJ9aUijbTE'
    'GO9PAoAp+M0IbDFOwBRSj9KTYlsA61J2FNHXrTxikNCgd6lFMX+dPA9KEFxwWnBaAacMVQgFP9KBmnUkDDNSAUyn'
    'jr70xW1H04DJyKRcCpB+lMQd6XbmnAZNPAx1oEIBxS0op3WgnqKFxR7CncdKME9KaHYcPSnBRSqKcOKoQYpaO1OU'
    'DGaobHAc0/AoAzzTsU0IYV9KUD1qTAOKcFxTQhAMGvOvinftY+EZwpwZnSP8Opr0evHvi43nWem6d2nuMn8CoH86'
    '5MfLlw8zfCRvViaXiWY2mhRxKcYt41/8dAr4p8bQQam8sV7GHTeQAeoPsa+wfiBcLDZiIjOFAP4CvkPVka4n2ycY'
    'GSPc8185iNz2aWx8h/Ff4Y2uoeHLu50a3C39uRcRnJZm2ZJQEnoRnivgvxHc31+lpBcMzCJPs6qw5UJkqv0ANfq7'
    'rfh2ecyv/a93DbsTmNWXaoPYEjIFfGPxu+HNppUlvrmiBfJG0TDcCd687/fcOtXgqqjNKXyNK6coOzPmuPSobfTI'
    'I5OHuwzEDrgDiub1aBLaEWagBYyDJ6lz2/AV1upPcRQ2hgIle0kbc68rjgj9DiuQnlje6Wa4O/zJOR16nkmveoTk'
    '3ds8utCKVkhiTi20/wC0zYLAkKPc+g+lcmTJLL9plGSxO0HufWulljW4jd35ijkdgO1YePO2yMCSzfKq+3T8BXfR'
    'e5xVEiuYFAds428Fv6CmMjlRFGOmfrW9Papaw7nIJY5x71q+HPD8uqzF3O2JerY9ew9z2qpVlGPMyVTcnyozvBth'
    'FNrtvBNz5jYz6Hufyr2/4mPp8Wgf2XFzPH5cyhf+WaRkfM3pnoPU15gLV9E8SLFCcPbz/Lnr8y8Zr1fTvC83irUI'
    'w6n7EkqyyseTcOvPJPUA/h6CvKxk71Y1W9Fqd+Hh7kqaWp6n8G9EFpoy3twv+kXJMrEjpvO7Fe+bgEA4zXMaHpf2'
    'G3VEAAAAH0rfkDBNo+9/U/4V8viKjnUc+57NOKjBRKk1yuTt7dqbPcm3t17vN29Ezn9T+gpkduZZsYAUctn0HX9K'
    'qXZNw7TEY5GPQDoorJFIWC6dHJz07nuP89a9Q+H/AIgu9H8QWeo20hSa2mSaI+rIc4P15H415AQVdTj8P511Gk3B'
    'jZGTIKnOfpUu8XdFbqx+rPxP06z8S+GdK1wgFLmLcAe8c0YkA/A1+VHjqwt7HXpkg+6kpxX6WeE9fg8Z/BnSZ5pM'
    'TabHLayj1eEYXP1Uqa/OD4gxIviCfJ48w152dSjPMHVj9pL8j38ibjgPZvo3+Z+k/wCyjqMc/wAI1t4xhrbU7lG/'
    '4GqOP517X4w8VaZ4I8K6t4z1+VotN0a0lvblkG5vLiXJCjuScAe5r57/AGOpbdvhtqsP8UeqBj9HgTH8q9z+I3hx'
    'fGvgPxH4Qcbk1jSruzAP96WFgn/j2K/Qsod8FSfl+R+f5sksbV9T8y5P+CoWo3ski+Gfhhc30asVVvtMsrAdtwhj'
    'wGxzjNPg/wCChfxz1R8aP8GJ3B6Zjv3P6KKvf8EqtWW68JfEPwDfQxG90rV7bUVDopcJcwG2kGSM4Etufpmv1P0O'
    '5uZGdbzT2tdq5DbMKSGxgdee9elp0PPVtmfln/w2L+2FqQzpPwWdM9CbO9b/ANCYUn/DSH/BQG7Aax+FKQA9A1gf'
    '/aklfrl9uUcBXP8AwGmGZpsn5lHoeKVzRI/I0/GP/gpbqBxaeA7a3z03WVouP++5Kng1/wD4KkaqQyaLp1oD/fh0'
    '9cfq1frWsY60jPIoxGAPqTSFZH5p+C7b9vIeJrA/Gm+0+18Hy+amox26WhklzGfLiXy0DDc2MkHgCvlz9qHU31P4'
    'hR6FanMGlwRWyhegcjc/6mv1i+LHiA2/2OwkcDyt08gB6EjC5/DJr8UvE2rv4k8a6trMhLCa6lZD7FiF/QV41aop'
    'Yh/3VY1qrlopd2cfqkfkrDa+qcfnXI+MZxHBb2qniJf1PJrqNXuA1/8ANyEwo/CvMfE10bm5YZ9hXZQjqjyp/Ey7'
    '4WvIdPi1PVZB8tpaO34ngV0Hh5bW9t0vr1h5cLPJk9Pmwa4yzjMPhDXJJBxLD5f4GuJ0HWW1uC08JWM5SaFS90T1'
    'IU4AHqAuK6uRyuzOx7LqXifz5Gs9FGxTwzgcn8ajtNHmtbC41a+Ysdjbd3diKTQdFJulgto9yJgFvU11vi5Gi0+P'
    'T1xnGWA7e1RdJ2QkeQWzu7jIrejjJHIPSi3088E1rPbtGFDD8q0bFJox5IsEcEYoVSoq7ONuR3qHtxU9QT0Ix/dx'
    'Ttnr61MowwJ5PrU2wlgT0oYimVwQB3qMg5xmrki9M8VUkO0/pUWKuRsdhU5/iH609tzj6d6r7s7l9MH9avLgkg88'
    'dKuwXEUf3qkLKAcMOtNyoSqkrZPTrUAh7ygjINZcxJzgirB24OelRtHEB60i7GY4cZ4yKg2mWN1HXGePatCRUADL'
    'kVVjdIplbf35yKdzSJHpN/eWUuLdyTyQp6cc4/GqXjXU7e70SHVbUBWjkKkDs7jGPzrZu7N4pRdW2GwQ2B1/+vXl'
    'mtC5k8QSaQ3yWpuFnRB/GWHH4DmqpRUpXQ2tDv8Aw8zqYYjn91aoMfQbjX9Hnhe4N34Z0W6XlZtMsXB9jbJX85fh'
    's772eRx8u0gflgV/Qv8ACW+S++FnhC6zkyaLZZ/4DGF/pSi/3jF9lM745Uda8x+I/jqTw1p32DSvm1W6GI8DJiTo'
    'Xx6ntXp7I0nCjrwB9a43xHY+FdBF1r2vYlvJRtVQRlUQcKp7E15+cV5xo8kHa+78j1MooxnW55q6X5nwdqfgfWNd'
    'uzIIpJbm4JeWSTliT1JJrzfxs9r4EtH0SxkSXUJxidozuCD+5n19a9S+JHxT1TULiaz0aJdKsipUJE2ZGUcZd+Tz'
    'XzHPG13ctLOSxJ5JOT+NfIU463Z9dN6FLS45SxuJ+T159aZqNx5k3+7wtaF3PHbx7RxgVyctzktK/wCArqjdu5yS'
    'dkTS3iIwt15Zu3oK6HToiD9pl+VFG4Adz71xOmxPdX3mHkV093JL+8tVJChsADuDzVyj0Mr9SIs17esycgmta/VY'
    'bdUGOOtXNH0vy1EjgDjvVXWzCPlB5z+dLeVkQYkZLKSOKfE5BI71PAm6IY+WomAR8YqmhxbL4DSR7u44qzazE/I3'
    'BFVbSQFth6Gm3Ia3m384PpWbXQo6mALIMdDWRf2Kxyeco4Jw1S2dxlR69q2J1WWAg9GFZ7MGcxbbVBRsZBK80yUY'
    'bOOKpzu0czo/UY6eo4q0jNJHjNbIyZJGf3brJzE2Ucf7L/Ka/Rj4LRyL8KPC8dw/mPFY+Xu6/KkjBfyGK/O23VJA'
    'Y243Arj619o/sy6++o+DL7QZmzJo94QoPaK4BYD6Bga9bKp2qtd0eVmcL0r9mfRxIUYH51CzZGx+h71ORmomiIBx'
    '0r6C54BQMZWQhaqldwkTGM8/jWjKfusO3Bqu6bpAUOMikFjKdi0YRuoqgy5O3pWo6lWZWHINVvL3SUkSyuYgkir6'
    'datNt25pjf6w59MVHIGJCj8aZIsjjG1eaps7HgmrfCLg1EdpPAoJaP/X+d9R0PVbjwvoviSebzra+FyIsEnypI5R'
    'vVvQk/NWXHoGreDRpWv+IEuLUanDPNpxibEhiClFdT2zIcAf3TnvTNHs/iE32z4dWqSBopTeGwcDcJIkLsyE8AGP'
    '5jg4PFem/HeG50/wh8NpNLWQ+HLuC7n0mS6ObwOfJN3HJ6xpMMxEcYOO1fnypSbaT0OuLsnPqjjPGegeKtI1+80P'
    'X54p7nQrQTXn73cIhMI3aHc333DOFKjv9Kr65o+lzazaaXojy34021M9/NGxaNpSoaUp2CRR7Yy3c5xW/wCCns/H'
    'vjCTQ/FbfaH12f7XqF0eHt7e2DXl5cb+zLEhC9skZ7VhaVoV/Fpep+INNeW20VpVst7na1wHcypBx94hQHkxwOM9'
    'axjU9lDml0Ro5prm6M6qD4jeIfDuhNbaDElpbh1Vp44MlGK/KhlIwDjoM5qv4b+NvifRLsyXIk1NJHSRoCWDSSRn'
    'MbArzuB6H04rovhRJp0niFdM18Tahox825ezCGSOS5KbInMQ6t2GenXtUvjv4QTeE7OPxdo6zLp9xNKsqEgtZMzn'
    'ZGWXkrj5d3Y8VHNTcOd9RxdVwVWnJ6Gx4wt5b280/wAa60skkPiC3S43ocGCXGJLfnI/d9ge1LH4FGr2TXPhLUbf'
    'VpFTzHsx+5vFAGWxE3D47hTn2qv4TuL3xR8OfEPhKAm5uNLaDWLKPGZOH8q5RPqGDYHfNecvofjTR7hNVtLa7SJN'
    's0dxEjgqOzZUZUjofSueyYT1fNa9za0LxhfeEtWjLI8lv5gFxbNuVZBnBHsw7H1619x6DpOgeKtMt9c0lI5ra4GR'
    'nIPup9COhFfKd3A3ivQLbxbqVpsuZi8FxcKv7qaWM7cyKB8khGPmHBr3z9na/UaXq2gM4P2WVLmIf7Mvyv8A+PDN'
    'VQnHm9k+uqO3A1JRl7O+jPX08HaBH0s4yfcVa/4RrRF4+xxcf7IrpKNldyh2PZUn1OfXQdLUfJbRD/gAqwulWa/d'
    'gj/BRWyI+9PEYppFNoyksYAOI1H4Cp1tE7IB+FaPle1O2Y4q0ibmb9nGfuik+zr1xWkUxTPL9apIm5SENL5AFXQm'
    'Kdsq7EtlLySKkWOrGwdqeFxVITkIicVMFwBSqtShatENlcruPtR5XtV1IHk4UZNb1hocspDSKfpWsTCSObjsmf8A'
    'h49avxWSRcgZNd0+k+VHwKyZbEg8Ct4swlE4jXomOmvsyfni4/4GK5a/YrbzY/ut/KvbbbQlubSUyDjGfy5rxHUc'
    'BLhQeAJB+WaxxHRm+G6k3wzYtpER+v8AM17TAxIFeMfDH/kCw/iP1Ney2+McV34b4UcWIXvF5c4qQHPFRDFOrqOY'
    'lBp5JqJTTq0RD3LMUzRkc8V0VtdB1AJrlutWYZWjOQaGhXOuzxmkOazre6DjHWrm/NLcLC7qafemk00mmkA7OaTJ'
    'zQaTgUxDqSkpe9FwE+lJg/Wl7ZpBjrQAnNIfQ0/jOaQ+tAhB1pTmjNLTExhOPxpPpTjkU3OasSQ4Uh6UvakNNCGE'
    'HtTeaf0pnemMTJo96PeigQoNPAzTKeOlAC9sU4cUgpR70MWg73pf1pKXpikDFz7U4U2nLigZL2p49O1RBualXHem'
    'tCdx1O9qaDThnNNlEin1pc0gOe9KeKRKQ9fyqTbUSn1qWgGA9DUqnimDmnDmqEidaeOajBJNOBFBI7mnCm8GnAUx'
    'kgHHNABFBpyjvQhWHgUoGTzSU8LVAhwGOKdjsBR2py81Qtx2OgzTh70nen4poGGKUYpcAUq073ELszXjvxH23Os6'
    'LaL95J4y30aRf8K9l7V4p4iVrrx3ZRnlfNiK/RMn+ledmjtRUe7R2YFfvL9jnvibdKHaIZwxP5dK+ZdRlyzkck55'
    '/Qfzr6D+JEii4fPJHX0Hf+eK+dL/AGr8o/T2r52u9T2KS0OXvQ8iFCOJM5HsT/gK8w8Q+B7W8iWSzt4Sc8pJkA/T'
    'rj8q9UuSPM28nBC/p/8ArqnJGZM59v6mue5uj4o8QfCZ9M0vVwsUam5M0kOwlghblE6DjPAPvXxrc2EktpsjQiWG'
    'Uqydwy9QR61+u+q+EP7UhO+5ntzJk5jboO/Br598YfBLQfC9xD4s0xZ7u4F1HJcwMDL5w3ckKo4P6V6eDxjhpI5K'
    '9BS2PgpNPuU018rww3fQPnB/GjRbCOdmeV1iWLALN0GfQd69x+Jvh65tLltU0zS7iz0+5iCMs6rHhgcjavXFedaJ'
    'oRttVhi1mKSD7QoeMAA5J5BBPHP6V68cTzU272uee6NppWOC1u2updQSGCN0ifAhDDDMucbvxNe/+HNCXR9DF47J'
    'GsXzF2G7JUdh9ePUmrV/8KNc1UrqtmRG1sqmFJD8zhTnBxwK9I8N6fJcGIarDJuhIVY5FCqjD0UcH/erkxWMUoRS'
    'e250UaHLJto8L8PeDtW8SatJrWqQSI00pkCFSuV6KPYYHNfWHh/QY7GFE2BSAOnSuhttLijAfGPbFaaxiLpXk4rF'
    'yqtdjto0VBabjRiPoKgkkYtg8HOSfSklkJYA+vFVZZCnTJLf1rjNixcDyrQsWx5rbAfUDk/0rPKMQVI5HI9+cEH6'
    'danvXcNHa/8APLAPpubk/wCFO8ssu/gg/mD0/lTtoCZnSJjJHTg8+/FXdNliW5VJWKoTtLDt7/hVaUEHOM5z+vP8'
    '81UUFgQo5zU2KPuz4A3076F4g8OXJO23MV0D1BWRTGSPrhTXhvxQgtrW5kjRAQ0hJOxc/wAq639nHxtaJqOo+GdT'
    'G25u7Py7eU/xeQS4jPvjOKyvitbI10+3nDV5GOSVWDPXy+T9lNHt37H/AIoigfUfBLwnfe5vo5geB5CqjIV9wcg1'
    '9+WsSIVdxypB/KvzM/ZfvrbTviFYzS5Cvb3cZwO5jyP5V+i3/CS6YWyTJ+C191keKgsLyylazf3HyWb4aUsTzxW6'
    'Pyd/Zmh/4U3/AMFDPHnwzQGKz8QpqcUCn5QygjUrYgf7u8D61+uF9eSWuq5b7kqAnnp64BPrX5JftL6rp3w5/br+'
    'FXxZt2aO11g2FvdOw2/PHI+nSZ+scsZNfr1qEEUtwrDadrEDIzxmvbjJOKcXoeNUhLVbNCW1yt1uwCNuDk98/Srw'
    'jOKZFGq8AY+gphvrVH2eYpI4ODnn0NDklqx7bhcyR2qeZMwRcgZPqacduwyE5UDccdwBnj8K818Z6+Li4GnW5ysB'
    'y5H98jp+ArCsfFeq2tu1kNsibSAX5KAjt/8AXqpRfs3PocMcwg8R7C3l8z5s+L3ik2dpqGoX0hFzdpdXKITyiKNq'
    'L+AIFfmErrbxSSHq3J/Gvpr9ofxbJc+Nr3TY5DstYGtWAPBLHLCvkzUrgpERnoK8LDU73k+p3Y2rd8q6HPajdZlZ'
    '+teeajLvm39TmupupOGJ5zXHyjNztr16UbHmeZtamWj8Hz24ODcZH/jteafBqN9Q8T3jyRKDBbld+OQ+4KRn3Fd9'
    '4luETTLW1Bx3P41zHwfuY9N8ZajasP3V4jFT6OhBH5jNdFO/sp2JvufUdnaLYWpeMYc9K5a8gkuZy00hbnOK7Zp0'
    'aFRgYxXOyTRFWYZBOa4YbsRhTCK3ULGvNUXMjjJODU90d7Zz+FV/LVYxk4zW62BlSZFK59ahUZ4FWZSuDxn0pIVJ'
    '5FV0JGCMnrUxAGM9qe4wSM4qI98npSYFefHas+Q5xk85q9KGJ6cVnSpgZHamNEBJO4D6Z781YhbJUt3FRYI59f8A'
    'GljY7Rx070xFtnPI6VA5wakOAc9c81BJzyOlRYpMbkHORUbqByBj3pjk9j+FRiVujdKktbkTMQOmR61FKocLgDmr'
    'TLzkHrTXjVhgkDHIqTRGlYh5Y0icKCvA3c5H1rzDUfKuPGF9f7cC2BhjXsAi4J/EmvUbBc7eec15PqTpHqWosDzL'
    'cOo/765q8OvekVN6I67w65IJ/vHHFfu38AvFOij4OeDkuZysselRRuNpOCjMtfhX4bCr5QbqTk1+u/wWjJ+FvhdY'
    'vmd7UqoHUkzOBXlZnjpYZqcLa6Hq5VgI4puE+ivofblhqFjf28lzZyFljOzdjHzEZ4+lfG/xa1Nry7u53uCIIm8m'
    'JcnHHLN17V9B+ItXtvBfhAWqODeOpQ4/56uPnP0UcfhXwF8Qdce6zAJDhs557dz9Sa8PH4qVZx5tz3sHho0U1DY8'
    'u1a+W4neUH5eg+g6VkSSRwRZP3jyf8KrXEoDEk8LzisG6vGZiSeBWEKfY3lMjvZmcnJ68muavJSV46dqvTTlicmo'
    'LK3N7chSPlBroiYSOo8MacY7c3Uwx3yagl1uzivLgoPMZSCPQcf/AFqs+JdYt9E0fyQ20lSWPoo61494SvbjXfPu'
    'ZsKZZdqdsICduffFVTpuac3sZSklZHrkOtXuoyCJPlU9h6Ve1CDZHGT17k9TVnSdOtbCMO8ilsUmozxzOFi+YL37'
    'UJK+hDlcS0g/dBj3/WqF0u05rYsnDDkc4xVK9X5iPxqeoJmdBJscMK6CWNbq33rywFc0cI2MfStzTbnadj85qZrq'
    'aGYsr27bea3tN1FXbyJOh4qnqVpsbzF6e1YqEo2R2qbKSJ5rG/rOnyK4nTkOMf1rJs5drGJ+D6V1+n3i31obZwC6'
    'jcufVef5ZrkdTt2tLnzUB2t8yn2PIopv7LFPuaKZR96npX0F+zfrH9mfEHUdClOE1mzMsXvLAd4H1Kk185Wcwm5y'
    'c13HhHVv+Ec8b+G/EBOEtL6NZG/6Zu21v0Y114SpyVYyZyYmHPTlE/TzBIowelTsoViqnK9vcdj+VMYZr6xny9ih'
    'LHySOh61SOUP0rYZRWdcqF+YVLAzbgbyX9ahgTLE1PIflOaIR8nNCYmiqYwZDineUAOepqxGvUnimyYzkUNk2Krx'
    'q/UdKrNFzkcVdbpUXTmklck//9D4y1/xFo1v4lm03wtqeoXtmDF9nvL9RDeFWQLLHIEYjAPAOeVqnqfxKv45/Cse'
    'sW51ez8JXMuyyu5XaCWOSbzWhC/wIQApA+teTQ3c2owWmsykfaMOspXjLRsOcepyDWl421S1tL426gEkJM/uXQEC'
    'vloYVxrqCW6f4Fqd7u56L4Y+Ilho934h0lrOd9X8T2cNlbGBgqWNjPcLPfjeckO8CCFTjgMc19O678R/ht4pbw14'
    'UkeTwR4W06KWOFCn21hNJjdO5TBYuQoLtzgGvz407W4NMjutfuR5t1chgDxlYgQpx7u2FHsDWrZ+KzfaPHqGoxK0'
    'xmaBF/h6g7voAf0rLFZc5VFyxvFb+bt+RosTJLlP0a8FaXpmrR2ngH4b6pENQuwt3rmvysIPKhyRHbWaSEMxYc8c'
    'kHB4zX1fbfCHwdp2jjQdR0+a4V1+eS6kkLyE8l85xyeeOK/Eyz/4THxhqpsvB+nX2p3Czko1nFI7dNoBZeAvGeSK'
    '/Wn9nzVPiL4D8M3Om/GnVYtQW7tI003RBN9qvLSYEYmln5EK44MYZvwollSUOabt5HdhMTG/LyGjo3wXHg3xtaeI'
    'PC85OnP5kVzBIcuiOP4W/iXIHB5Fe7xWcXl7dq4PUYHf1rRPlhQ0Z4YA/mM1Fn5s15caCg7o9qFKMfhMibRtKks5'
    'NPe0ha3lJLxbFCMT1JAGM+9eV6H8Ln8I+O4PEXhq4KaXdJJDeWbnOwMpKlD3XcBweRXtfX8aeEx1qpUYyafYp04t'
    'ptbDEzjk1NinBadxWli7iBcU4LS8daeoyaLAAX8acF4qQLxTwKpRFcr7aZtq2RjrULCnYVyMLzUip7Uqr2FXIoya'
    'cUSyr5fHFPELZ6VqJas/AFa9tpEsoHyk1ookNo5+GyaQ4AzW9Z6FLOQCuBXWWGiCPBcYxXV21vDCMKBW0YGEqvYw'
    'tN8NQQgMy5NdIlhDGu1VH5VcTFSgitVEwlN3Me4swVyBXM3VoyHOK74gHrVO4tElU8Cr5Rc11Yy9PjT+zJeOQP6V'
    '8m6g5xdZ/wCmn9a+uEja3tbhTxxxXx/qJY/aiPWX+tYYnZHRhuppfDA/8SaHr3/nXs8NeL/C/wD5AkH4/wAzXs0V'
    'duG+E5a25fVs1KPeqwJ7VKrfpXWjla6k4wTUgqEZqQVojNklGcU0U4CmJkscjJyK2be5Vhg9awM4qWNyhzSfcDpt'
    'wpc1nw3CsACashqL3BolJpufemkmkFAiQH1p3fNRU4HtTAfRjv0pM0uadhMO3NJmlOKbxQSOJo96SkzimAppPpRR'
    'jmmAv40Gm0dKYhDmjGeRRzmjPrVANI9KXHrSk8UnNMA/SnUdqTjrSuA4c07pSZoyM0XAcaKSjjvSAdTh0pmR2pwo'
    'BscvWp1PFQgVID2qri2Hg80+mDFLxRcOhKOtPHPWo1p/XrUjJRjFOFR5GKN6DqQPqRTuJJk1PU+1UzdWq/eljH/A'
    'hUbapp0f3rmP/vqpdSK3Y/ZytojUpwrFOu6SD/x8Kfpk/wBKYfEekrx5pP0U0vb0/wCZfeVHD1P5X9x0HXgVMo4r'
    'lj4q0oH/AJaN9FpD4tsMfLHIfyFS8XR/mRX1Ws/snWYzTvpxXGHxfED8luT9WxUZ8XSdVt1H1Yn+lT9dor7Q/qVb'
    '+U7tcZqXNedf8JXeEnbFGPzNNPijU2+6UX6LQ8fSK+o1T0YA1KBgdK8wPiPVmP8ArcfRRR/bmqt1uH/DApf2hT2S'
    'YfUp90epAUDgda8r/tHUHPM7/wDfRFOFzct9+Rm/4Eaf19bco/qT6s9T3p/Eyj6kUefbKPmlQf8AAhXmCu5PzEn8'
    'al2g0vrz6RD6mn1PSft9n0WVC3YBskmvEtPvJNV8Z27uv/HuZmJ9gpx/OutgVUkEhwAgLn6KCa4nw1mPW9Ru/wCG'
    'OByD/wBdCMVxYuu6jgn3OihQUOax578QJ2nvZlVsjd0/T/CvEbhS5OcDBIz/AFr1PxXMZLuRjzyT+PJrzKVfmIPH'
    'AFeNV3PQhoYjxgOTjqCT9T0qIxKBx2GB9ThR/Wrs4xJ9T/Koo1V3QnopLn/gK8fq1ZIu2hFIi+aUXoqhf6ms+6jL'
    'Dn+Ik/gK0sFvYtkn8eT+lVrsAlUHJAAP4/8A1qb2FseZ6t4XstX5voFmA5AcAgZ9M1w2s/DnQ9RgS2u7RSIiDGQM'
    'MhHTaRyK9wkwwJHRj+nasW8xy3BxnHvSi2tmNpHm8Gj/AGO3WEZZR8ozycAetMOnRZyUFdfJECdv90D8yf8A61Z0'
    '6AEduc/4VNxmasSIo39Aev0qlckKpwO9aMoCH5hkqDkep61g30uG2d16/wC91NAyq5zkpztpLNluNQt4h2bcQf8A'
    'ZGaqJOqk5JGf5VTtbhoNftUI+SbeAffaadhMQXLjV54ZyAXYk+nrXTyxhIxhOQQQfTJ7/XvXE6sxt9eSXs549hXc'
    'u/mQIV4A5P4gZ/lVNaIhPWxk3OFAwcDJ/I9PyqigAkDZ9a0rmIbTjsKzsjII6nmpsi0z1D4e6Jcy+LNE1bSiGxeQ'
    'iVQcMoLDcT7YzX0B8RrHTxKyQrvAJBIx/PrXyv4Z1e90i9hvLKUxSxOHUj1ByMivrfWNfg8YaPbahCscCyQp5iJG'
    'o2zKuJMnqfm5+hFefjKSdpPoehg6jXNBdThfhdNa6B480m+Z9lubgxSBv4fOUxg59MkZr71cIxIyMivzpntrm2vI'
    '5I2WRS42SIcjcDnB9D7GvvYyusMUjN9+NGY/VQSa7sHNxi01ocldXadz8s/+Ch12niCP7PpPGpeBZrK4aVT8w/tF'
    'GIx6bJo4fxav2L+FXieLxz8MPCPjeNt663othfEjnLSwKXH13ZzX4BfErxVN8QvHvxDYEmLX49QEOeebHFxb/wDp'
    'OB+Nfq3/AME4fGsPjX9lPQtMdybjw1d32iyDPKoshnt/yilUD6V9llzvQUex83j1as5d0fXnifxFFYWptbZx9pl4'
    '4PKL3P1PQV53Z6w9mXIG7cD17N2NdHeeDi0rGSZ2bPJJWqw8IwKRvlf8xXsWocnI9T5KvDG1KvtIxtbbU4SdzvaU'
    'ZZmOWJ7k155pvjW11fxDqVlYNvg01FhaUfcaYyESKp/i24w3oeK9P+JEtj4T8IXs8JYXtxFLDayZB2SmMnfj1XjF'
    'fCWneK7DwHPovhmzk+0efoy7ZM582dZ2kmkJ7li5NeJm+I52qFN7bnqZPgfq7detu9vI+S/iDrk2qeOtcuZDndqF'
    'yPwEhA/lXmuqSnLc9a6fxDhvEOpyE/M11Mx+pcmuH1WYAgDrRSjayFN80mYc75Y81zm4fasn1rUkly5+lc7NIRcM'
    'V4rsj2IkjF8Q3jSMdzZx09hXpl/4Nt/h/wCFvhJ4zmidLrxxBrN1cM/Tyorpbe0wO3yhj75rA8HeCJ/G/jPR/D8c'
    'bTjUL62tzGvVxNKqbB9c/lX6Rf8ABSvwHpfh3w18LV0W1S0stFN5pdvHGMLGiRpIir/3yTVxrLnVFLc0jQ/cyqs+'
    'VrFmmgBB5x0NUrhCFbg8dcVN4duIrrTIZlPLorH8QKXUInWGVlySemPT1rl2lY5UrnLSYLEgVIwjji+Ybuefyqnz'
    'yScZps95GgABya2SEVJJWOQB2pyPgD5sdKrAySdOn5VOsZUAE81oBLLhlOKh28Ee1WtuRxjjmq9wuwlfWluIj++u'
    'B26+9UmUKSDmrkTgLjGcVDIWzkLxQBRkJznHWo1YEED1q4dpGe/pUflDLEc9KCkgRGfoKe0ZBwRUscgA9MUplUnc'
    'aCTOZMHmoPlJx3q9NsYH61nSRMvzA8VDRonckU8FTxUTsodefvetMRjgndz6U48jDDpyDUs0Rr6ah8za3AHP5V4U'
    'JXvNReU9GkY/mxr3GCdYYpbg8COJ2P4Ka8S0xRt809T0/GtqCtzMc3ojvdKkZXUr/DX7Y/s6aTY6Z8HtB8SXdz9o'
    'u7bSRcRwD7kDTSOIt/q5+8B2HNfippHlRx73781+zPwIls5fhE3h2eeOzNnBZT3MsrBFWOaESIWJ7Y4FfO51FPku'
    'rtNtetj6DIpSXPZ2019LmH4716/voNnmFtrSMWJ6ADlj+pr4417XvtE7szZJJx9BXtHxd+I2gQwXHh/whL9pyGin'
    'vTwpXPzLF7Mep7jpXyQ80sspeRsjrXiYehJ3lM9+tVjtE6Ce6LJjd15NZM0mRVQ3GT60ySbecCuxQsctyGRnY7Rn'
    'JrrNLWKxg86TFYUEabl3fWud8Z+IjZWf2S0b99IpC4/hHdj/AEpqDk1FEuWlzhvH+t3nifWJNJ0yYeTAwEuD95v7'
    'v0Hf3rqPB2jXtnZhZxjkHivF9Is7q1vjcREmUNuOT98E5Oa+lPD2rwzxQiT5MgfSu+uvZwUIbHJFtttnSW0L8btx'
    'GO+eK1EtxgtuwDxW7aR20sYYYORT5oIQ2cCvO5yynYQgDP4VWvkw3161tQRjIwOM1Q1BCSQB3NQ5a3Kgc3NtHQZq'
    'OKVkYNnBzVuRCVzj8aoFSD83P0q7X0C9mdxatHfWvltjOOK5q8szA5XmnaXeG3mG4/KTXT39ql1F50Y6isfhY3qj'
    'j7O5aCQMDgiuijSLVrEQkfvYgQPoD0rmbi3eGTp3q9pV19kvxuJ2yYz/ACNayhdXRKl0ZnvDLZT46AHpW9uGoabK'
    'kRxLEN6j3X0rotU0iO7g+0xYPfiuPiMunXSyMPlzgj270RakjOSsfqh4F1Y6/wCCdC1gnLXVhAzn/bVdjfqtdQwx'
    'XiP7P2sRXvw0s7MOC2n3FzbdeimTzE/Rq9u3KR1r6yhNSpxl5HzNaHLUkvMjYZ/Cs+cb1K9xzWiVz05rPucQ5eQh'
    'F7sxCj9au5kZTAmpY+Frj9T8deENIdhfavaoVJyquHb8lzXC6j+0B8ONNBH2ma4IP/LOMAfmx/pWTrRjuzRUJy2i'
    'ezg4yKiY9jXyprP7VXh23DHTtPL46GaTH6CvMdV/az1qZjHp0MFvkfKUTzPwBJPNZyxMOmposFUe+h95sO+OPWse'
    '41rR7STy7rULWFz0V5kB/U1+bGtfHTx1rY8uS5mKt23bF/IH+lea3uv65qDF57gDPfJY/wAxWMsXK9kjaOXK3vSP'
    '/9H4kj+FnhOwjNtBrepMhZjhoIc5YAH+L2qvqHww8JapqEt9dahqczuRlQYkACqFAHynsK9YvdFljAucYXvWVFAg'
    'mDsMA8E+v1r514mpfm5tT1Y4aly6ROQtPhx8PERElsb26VABiW7KqdvTIRB613+i6b4O0ILPpfhrTtyHKvco10VP'
    'qBKxXP8AwGlt7UCVlxjPQVsvp+E8teVPoPXtWM683pzM0p0oLVJHS6f4z8VXCfYILhobKQ7RbWqrbxfhHCFX8xXo'
    '3gm4me5O8/Mwzzzyp5FcN4a8P3MxWGPCupDFycADpmu40ljoOpNFJhZIXIOR78/mKwm763NYo+1vDlyb3R7aUn5g'
    'uxvqvFbwj9TXnHgXVonD2KMCGXzEGc8DHP5EV6Sr5HSuWorSaPSpScoJhsAFUNZ1fSfDlimpeIb2DTbaQExtO2Hk'
    'A6mOMZdx7gY961BEZRtz14r5y/aH0fwl461K1Ou3t7ouqWsItRcW6faLOaKI4TzbfcrIR6xnn+7WlKmpJt9DOvW5'
    'Gl3F1v8AaW8Eae7RaNa3mrFcjf8ALAhPt941wN1+1Dqsrf8AEv0CCEHoZpXkP44ArxSb4XaqmE8PatpGrpnCCO6+'
    'ySn28u7EeD7BjXN6r4O+Mel7ltvBV1dKvSWOWCZT7gQyH+dP2Unsifar+Y98m/aR8ct/qrbT4f8AtizfzaoU/aS8'
    'fDllsPp9n/8Asq+SryH45RuUTwXqCnsBZO365NZSaZ+0HeNiDwffYz1e2WMfm7Cq+q1g9vDufcFp+054sQg3en6f'
    'OvfCOh/RjXqfhX9obSdYYR6xo0sGTgvbT7se+11/rXwHpPgP45nbJq2laZYIeSbzULSHA91WVm/SvZtA0KPR4ll8'
    'Ra9pcUn8UenCe9b3AJWNM/8AAsVnOlUi/wDhhqrC13I/THRrOw8U6LJrnha9F7FCAZ4JE8qeLd0+Ukq34GsooQee'
    'MV8n+Fvi4vhZ5tN8Gw3RluVEb3d6y8Ac5S3T5AfQsWxX05p93PcWNtLKxd5IY3Zj1ZmXJP4k1U0rLSzClU5m0ndG'
    'ugwa6LR9Ne8DsoztIH51yyOd2CK9Z8CrEba6LY4ZP5GnSV3Yqq+WNyxY6EFILjFdNFaRwqAAKujZ2pjnH4V1KKRx'
    'Sk2VmGOBUBYqeKmeSMfecD6kVTee0H3p41+rD/GndEcrLsc5BweKuJIDzXOvqOlR/eu4R/wMVH/wkWhwj57+EY/2'
    's/ypuUejDkk+h1oanYyOOtcPL478MQDL3yH/AHQT/Ssqf4r+EbcZ+0s/+6v+Jpe1j1Y1Tn2PQ71QbGfPUL1r4p1K'
    'QIl0P+un9a99uPjH4TlUWivIWuCI0+7ksegHNeE6tY3Mi3LRxHDeYRn0OcZrDES5rcp00Fy35iz8Kn3aHb59/wCZ'
    'r22MYAIrxX4b2smnaZDbTdV6n6nNe1xMMCu/DfAclfcsj1py96avPTipNpxmupI5fIkRs8VKDUCD1qWrRJJmnA5q'
    'PoKN34Gne5LQ85oBpm6kB5piaLaSbDmtKGcMKxd/vUiSeWc5pWC50AbNOzmqUEoccGrijPTmmhDqXNMOfSjJA9KY'
    'WH7jTs1BvA6kClE0Y6sKXMg5WWPpQRiqv2qEHlv0oN5D1yT+FPniuoezl2LXsKXFUDfxA8KTTTfgc7D+dL2se41R'
    'n2NDtSd6ym1Mr0jH51EdWk7Io/M0nXgV9XqdjbppHFc++q3J6BR+Gartq176j8hUvEwRawk2dPTTnNckdTvT/wAt'
    'CPwFR/brthzK351H12PYv6lPudiOuKd068VxBuZ26yv+ZqFpHPV2/M1Dxy7FrAvrI7sso/iH51E1xCp+aRB9SK4Y'
    'nPU0xtual499IlLAr+Y7g6hZL1nT86iOq6ep/wBcD9Af8K4clR3pm8dazeYT6JGiy+HdnbnW9PX+Jz9FNQtr9mvK'
    'pI34D/GuODj1pfMH+RWbx9R9i1gKfmdWfEUI+7A/4kUw+JQOluf++v8A61cq0oHaozIDUPG1e5awVLqjqz4ok/hg'
    'A/4EahbxNd/wxoPzNcwCT1pQy96z+t1n9o0+qUV9k6BvEOot0ZR9Fpp1vUm6zY+gA/pWDvWnh1+lJ16nWT+8Fh4L'
    'aKNZ9W1F+DcSD2Bx/KqrX1433riQ/VjVLcDRle4rKU5PqaxpxXQna4mbrK5+rGoyzHrn8ajO0HoadkfhWTuarQOc'
    '04HnGKj3dsUFxSsUWAx9KcH96rZHanrimkyW0WQ4B9aspgjJqmuPSrCkntVpdyGWhsp4wKrBiDxUqs59K0SM22TA'
    'rUgdc8ZqNVNSBWq0iGTKV61Moz3NRJgD1q2h+laJGTHoo75qwoHpTFB61IM1qkZtolUZqZS1Qrn/ACKnXpmqRFyX'
    'eUt7iVuiRN/49xXK6Ioj0vUbluSxSMfTk11N3JFFpd20v3SgBx2BPX8K4qzR4fDrAt/r5pD/AMBXC5/nWFX416M0'
    'hrFnkviBd8shHcZGPU/5zXnFySZScdz+QH/6q9O1q3MO5gScAk59e3X8K88kiyTnsD+tefNHSjnbhSCSR2x+PU05'
    'YyFlI4P3frjk/qf0rQ8oOwVu5yfxOaiVQVUd2zIf+BMcfpUWKbM9iQMDryP6Vk3Uu6VscZJIx/3yP0Fa86MoYr/C'
    'CfxNYc0TBig6525+g5/U0n5CRQkkxGxHBxj/AOv+VY122MknoVT8hub+grQuGCIM9+ePT3/AVz80mQu/ptZ2+hOT'
    '+lZlEE8wUsvq2P8AvkY/mayricF8ds/ywKbcyhSN/VQGP1bLH+lZEkhyx78AD3P/AOursIka4HU/xZz9Ccn9Bisa'
    '4Xe27ueT9TzU00oGQPoPoP8A61Z8suWximokuYslqsiEd68517W5fDF/Z3twN9rHMDIB95R0JX8Oorv3kJXgkfSv'
    'N/F2mNqMJ8z7iAkk9BTpW5rSCTuro7PxAsNzFFqNowkR1WRHHdSAQR+Fa+mXhubNcnBA/lXBeDb1dR8OCzO7dYkw'
    '4bqU5KN9COK6LRpxGWh/umqatoT5nU3DYT5R1H8xx/KsMnkj0Y/4/wCNbD4aP2xx9Kx5YyshxyT/ADBrOxSZs6aw'
    '80Z6V9AeBJHk0vV7B5QqR2pvEUjIYxMA6/8AfLZ49K+bbaVkIOcV674N8QSabPHeJhmTKsrDIZWG1lI7ggkGsqkL'
    '3TN4TtaSGjWIv7RMtvL9nbOCTlon56MPT+XbFfcuneI21f4ZLqdkvmXxspYPKUbiJ40ZBk56ZwQRk49a+VfEdj4f'
    'E3+n6MlnZ3QUW+qWpO2OR+Qk8WcDnuOo6V7p8BbS4fw7qml3B3fYb4KCDlSHjBGD3B7e1FFyh7qKnyyldnwF4Q/Z'
    '9+IkfiCw1X+y1v7eO6UXD208Ug2yHy5Qw3BgdrtkEA+1egf8E5vij4S+C2u/FH4YfEfXbLw9EmoQ3Nk+pTrbxNNa'
    'vLa3Eas+Bu2iM4zniv0ZOh2FteG9hjEVwRgyJ8pb2bs345r8svjt+zh4K1P4k634qutY1LRrfV7uS7uXW0jmtFml'
    'bLlZFDGMFskiRQOeGr28rzKFObp1na+3qedmWCnOKnRV7H633n7VX7Nloha6+JHhvPfZeJKfyTNec6x+3N+ynpLE'
    'S+PLOfH/AD7W11N+W2LFfljafsWeHJdNXV7DX9R122dQ0f8AZ7WmHH+ywDA/nmqPif8AZa8B+FLOyudS0zWL1L5S'
    'wkF0cREEArN5cY2tz0r6P21N7O54DhNbo+yPjn+1Z8LPjD4YtbD4T6zLevZ6paW+pu1tLbGO2vn2bk8xRndsKkjp'
    'mvkPXr6/HiXTbOceXLoPnWitk/OvnMVP/fGB+FUvDfwl0LRLTxHa+FdEmtJJ7Lf55vGuVZrJxOoZW+6xBbaak8Ta'
    'q2qQ6P4rKjzLy1RLoqP+XiL5GYjtv2g/UGvNrcntW0E4ycTh/E526/et3kkL/wDfXNee6i4eT6cV2/iSTzr9Jx/y'
    '1iUmuBlRnJH+1W1KWiOZws2Yt1iNTnuK5mbJPA5PQDrXSantDBe2Ky7abyZw1sgln6R8ZCse/uR2rpT0ujCSVz2L'
    '4Wy+JPD+ptq/hGzmvfE2mRx3djFAQGikLhC5PQFVOfQV3vx08TfHbxx4Ks7n4uWt1bWVpqK/ZDcXKTfvpYnBwq8q'
    'do6mvoz9hn4fbYPEPjvVI/P3vHpcDMA29h++uWAY8hflXPqa9f8A22fD9pdfAma6tLZY3sdYsJtyoFOH3xHkf7wr'
    'hUL4mMr7M9WE7YOStumfmB4DuCNKETEloHaP/gPVf0Nd7dzILGU5BYjaPxry/wAGRy28s0eeHCnH+0M//Xr0C7Um'
    'AMn3Tiu6pFc54MZHO/YzMQCSBTJNPSMA7f8AP1rVtWXexKlmHQE8fU0y7uvkBHyj1/wHarJdzEkBgBB49v8AGqkT'
    'O7e1JcTB5CpP596VcIufpTsBcZgiktxx0qhcSmV9wpWfeT3p4iTbk5B+lNIVyOJQ2cd+tEwWNRk8+hqTIUHAPFUZ'
    'TvJLUPUEyuxbO7Oc0K+XZSfT+VO3qpxj8TUW0CQZH3h1H1xSsVcutH3AzVZw4q7EvGM9KHiU9cgZoUguZTlgOlQF'
    'ynGCR71qPADnBrPnRohkmky1JMrTo6/OOVbuP61Pbp9oXtleoPFQRTPnaF3Keoq95QRfNBC45IqGaRetiDUNltpN'
    '67t8ogcfmMV5FZgHZGnSvRtduvtegX6IcFVXI9RuArgLGJomBNbUU1FsJHeabFHLtiPoQcfSvr/xN/wlEGmWlzqo'
    '+y/abDTonSFmEcsMVuBbOw6ElV596+NrAtHGZc89Pz619NJ8VJfEXhq50jxCq+fZ2dtFayKMErb4CKffFeBm8Z3g'
    '4q+up9Dkbh76k7aHG3lzJ5hjyfeoPMwuO5rObUBczNK3G7oOw9BTt+41yctlY9By1L24Vbt4MqZW4qnAmcFugq5D'
    'LPfXcOl6ehmnuJFijRerO5wAKzkUjY0Lw54h8V3dzaeH7SS4+x20l3dyKPkt7eLl5JG6AdgOpPArxvVrCePVLmO6'
    'bfIkhUn2HTHtiv1s+E/hS0+HfhC88Mpq2lz3GuIw1XK4dy6FBEkpIJSMH5eACcmvzU8caK9j4qvLUr88Mzwv7tGx'
    'TP44qKVX95ZbWN3SSpty3PNVtFtpEuMcKefcV2SSRWOxlTMM2Dkfwk96v/2KJrfbjnFbGj6WtxZPaTjJi6Z9O1dU'
    'ppq7ONrsW9MvriHaI2LIenpXfWMpmUEjJNeX/ZJ7EkW7EMh+71BFdBpviBVwlwuwjg1jOHNsS33PT4ioC+9Z11H8'
    '3J47CqNtqME6jawPpzV/BlyTiuZxsCZjOmZdg6VlXSMjEDt3rpLiFSwGSAMHPrSXNks9uJFHTrS5uVo0WqOMDsrB'
    'vSu80K+WYfZZuA3TPrXGzQNGcYxS29w1u4ZWPBrVxU1oQm0dtqumgbiBXC3m+FkY8bTj8DXpOl38Wq2xikI81Bj6'
    'iuf1jRS2WAyAc1jTnZ8sglHqjJ0fxDcWbgA7k6MjdCK7C4tbLVrX7XacE/eX3ryqWJoJWU+tdppMVzpUIv8AVpfs'
    'tq4yqH/Wyj1VT0Hua25Lu8SHKy1Pof4Barb2d7q+h3k628MsAvFaRtqq8B2tyf7yn9K7bxd8cdA8IEpp9zJfSqeB'
    'nZH+uSfwFfC2sfFV4ZJLTw7AIoydrSZ6/WQ5JPsP0ryXUNZnvXeS8kaV2PIyQP8AE/ia9OjQaiubc5J1b3SPrnxR'
    '+1p4vu5Hh0y4Syj6BbZAZPxbDH+VeHa38XPGOuyF7u6nlz3nlJ/TmvIWujjauAPReP5VC0hJJLE4A/8A1V0NGMUl'
    'sjrLnX9UuzumvNuf7oJ/mf6VQe7Rz++nmk/4EQPyXFYCnpz71L6t1IpWRaNcTWYHywKSO7DcfzOaJb53QLGMZZcY'
    'Hv7VmK5A5604PmZVz93Lf0H9aQzZF3IxG41KsjkcnrWcrAke/tV6PrUlbH//0vMdYELReSMru6kVzEGmod247lPS'
    'tWcXTPuwOvUmmASo3TP418nzKx7ns5XKsGkvHcIwb92O1dhcootwg242g4X1Hr71lRK7Rb2ZQB1Gcmp/tKZVd2Qe'
    'tYymaRpyXQ6bR7uATRfOQzDAwM8ngA1PreorqOpLcELGyIsTuTgO0fG4/hiuLlnFgySWxL7j8uPU+lc7qN/PFIwK'
    '5kJyRnO3PqfX2qo6jkrH1V8KNb8zxLa2cbbo+Yi577h29hX1wlpcPItvGpZ3YIqjqWPAFfnZ8JNXlTxBbSIxyro2'
    'ffeBX2T4wl8fXVlJD4fivVu1jAR7a2ckNK4jLBlH3lTJ+hrKcLyUUbUqjjCT7Hq00mk6M5j1PUYRJGfnSI79pB6F'
    'uF/I18ufGeLzrt9WVkMRkki27hvDfe5Xrgg8GvULb4Oam1orSabf3c20bpbhXLO2OThjxk9sV5J8c9OMK7ZMq6sw'
    'YZ5yoAOfoRWlNOzVrIwxLuld3PnuxmjY4PJ8xD/49VrX9wunCMy9+Dj+Vcxpc5G4HkjB/I1v6nP51wz+oH8q2cba'
    'HHSld3ORuWud/E8gx6O3+NVFWUk75HPPQsTWnOMuT71TJw3IqbG3O7vUljYrwOa0byVlETqPl4XPv1qinNXbrIgQ'
    'HoSDn6UNCbPRfDPlvrWyUcGRvrxX1VD4z8Yf2dbxaV4f+0pHGqJKcKGVRgHO7vXyz4XiRLm3nzuJkG4n3PNfoHpN'
    'msGmWkUbDYIUwMdiM1nJxTXMzfDRlJPlPKLHWviJebpLnT0tctxH8hAAx36nnNbMetfES13JZuIA+N21sZI6dK9P'
    'aAD+IflXV+E/B9j4iiu5rqeSEWzRqAig7t4Y859MVCpqpPljLU7HKdOF5rQ8JXV/iRJ9++Yf8Cb/ABqXf44n5m1B'
    'vzP9TX1Gnw58Owgb5rhvxUfyFTDwR4VQ/MJm+smP5CulYBr/AIcweMv0PlZtN8TS8yahL+BqI+HNal/1l/OfXk19'
    'Zf8ACLeE4RkWxb03SMajGkeG4+lhH+OTTWESJ+stnygPCd23+tu5T/wM1aTwnDx5szt/wM/419UCy0TPyWMA/wCA'
    'Vp20WnR4CW8I+iD/AArRYVXIeIkfKsXgywk+UK7/AEDGrI+HMMv+pspnPtG5/pX13BJboRsRV+iit23uFJ4I/lW8'
    'MJF7mE68lsfE0/wx1WNIp7TR7h3jljK4jORhhzz6Cu4bwT4tnilVNKnbKsBkKOo9yK+t423L1p5TvmtlgoLqZfW5'
    'dj5N0H4beMIIEE2mtCe4Z4xj9a7yDwN4hGN0KL9ZF/8Ar17tg9zTMVvChGKsjOVeT3PIIvBGrnlmhXHqx/wq0PBV'
    '8Rh54gfYMa9TIFQuB1Jq+VGfM2ebr4Il/ju1H0Q/1NTDwbCOHumP0Qf413TMBVV5O1ToUmzkR4T05T880zH2wP6V'
    'KvhbSB18xvq2P5VutLzxVZpTmlcaXczx4c0dOREW+rsf60No+mp922Qj3yf61cM5HBqI3GTilzD5Sjc6bYwgSRW6'
    '7cZwRyB9e4rNfyl+7Ci/gK662vIXUW9wuVJ4YdVJ7/8A1qydY0uW3HnQ/NGepXoPw7VLva6NFa9mYDTFfugD6ACo'
    'TcSdMmoJS6n/ABqsWbvWTkapFxpXI5NRF3PVutV9xFG89TSuOz6DmJ9frUWc8E8UFz1HFRF+3WlcLMfxSELUeaYW'
    'PcVLdx2JDigsOlQlj6UhbPak2MeaiNNLe1NLH0qOYtAQahOelPZ8dTUO4etS2aRGkEU04HXFO49ai2DuTUGlx3y0'
    '049vxph203IxwamwxzcelQsx7U4nPemHPapaKRGd3eo2LDvT2f1qLOegz9OamxQbyKN7HirEVleTH91byvn+6jH+'
    'laUfh3XJRlLSQf72FH6mhUpy2TE6kVuzGw/emnIFdjbeDNYl/wBcYoR7tuP6VqR+A848+8/BE/xNbQwFZ7RMZY2i'
    't5HmxYjnNN34POPxr1yDwRpCY80yzfVsD9MVv2uhaTZ4a3tIlI/iK7j+ZreOV1W/eaRjLMqS2TZ4SuTTia9k1Xwz'
    'puq5dQIJv+ekeOf94dDXnGp+F9Y03L+X9ohH8cWSR9V6/wA6yr4GrT6XXkaUcbTqaXszCyc46U7j1qsJBkgjB6Gl'
    '8welcLR2plrC/wB6mkLjg1B5jeho3seMfrSsO5KFHXNL8g4JqMHjJFBJ7CmoibJwyDpT1kHQAmq2+T0xRvfjNVYV'
    '7l1XYdBU6s7cYqojN6Gp1LZ6VaRm2WlDZ4qRd3rUa5qQZPatFEyciwpI61MGquo74qYKKtJkNlqBHmcRxKXY9FAy'
    'T+ArSfT7yDmWF1+ormNS1a60m23Wkz25YEs8e0ufQZYHAHt1ryqX4t67ZzSIt7FcHOFE8ZTv3ZMj/wAdp88VuZtS'
    '6HvS8df1qwpHYYrwmP4x3ow1/YxsgGS8bB1z9V5H4itC1+N3hOTAuQ0We6MH/Q4NWpxZnJM9qBzzxRk1wNj8R/B+'
    'oNtt9RjVj/DLlD+uK7O2v7W7RXt5kkU9CrAj9KtO5JflUPYTh+QdqkeqkHNUbq3jstJtLRBgRxKcnrljuNbNtALl'
    '0tl581gp/E9awPGF3FFLIgOVUlFA9B8tYVtLyZtDVpI8e8SuDI4A4Y55PPr/APXrzecDDc/ewK7LWJpJHZiD9Prz'
    '/n6VyEqk5OPYfjXmylc61DUx+cuw4O04/E4FKI1yT1BO36BRirEqbMMe3b6f/XNRhWRAo9D+n/1zUjZSkRVRQ3Vj'
    'lvwOaxp40A6ZJ6/VvmNbl0MLgHkAr9M8H+tcrezvtbb1IJ/P5RSbEkc1qBUxN5fBbgD/AHuB+mTXNXBLpICeZAqf'
    'h1P6AV0V84Y7VHA3c/7o2j9cmuZlIBCj0z/31/8AWFJFMxrss5Lf32x9QT/gKxpG6H1JY/mf8K1L+QjAB7Ej2xwP'
    '61i3Bw2wHgAKfyH/AOqqsS3oVJWwOfY4qpnJyeaklJLkjoTUWcCrtoYsnAXvXM6//paLZRDgsA3+FbMs20BV++eg'
    'pI7ZVkUyDJClj9TWTdnc0gcHpNtcafqjiNSIpV2OPp0P1BroYont70N0DVeUO9+sUCZaQhVA/vMcAV7j8e/hLL8O'
    'dd099Lb7RYajZxTxsCD5c6Iq3MTYJ5D/ADDPZvaiMpNu60VjacY8qd9X+h5dbv8AJtPPFQzAABj2NVIXcIu7jPFX'
    'iN6Enqao57lPGGB966LSJXEojU8HGK558YHPSnx3bwOGjOGHSpkrouDPbdS8VC1sMXB860Eq21xEfuvC67XH1BG5'
    'T2IFfUf7KmtNpun+KtLAe9hjvLbynVd25DCdpJ7fLivz4m1PzYJtNm5LwtNnPR1YFf5Gv0P/AGQ9Gk/4V1ea75RL'
    '3mousbdylvGsYx06EEV15ZCTrq3S/wCRhjpJUWfTcdrpWrSOht5LWYDcR04Pf0rmE+FtpHJdOLlLhLgHCyJyCex6'
    'giugv77V0R47W3eJz1faCR/uqRgms/SvEGp2hFlPZajeSlyTNMqKoBPQNuHA+le1Wy/C1mvaQVzzaOY4ikrQmfK/'
    'i79nOytdVk13w79t8Nakx3G90eUxK59ZIhmJwe4ZKzLDW/id4QX7J4r0yDxVYL/y/aeFtb3aO8tq+YZG9ShTPpX2'
    '9Jq+pKrPLaQxxD+KV8ce+cAfnXnPiPx38OtOjI1O906G7OcrBdRyEH3RQ35VwSy2ph/ew9XTszuWY06/u16WvdHh'
    'enfEH4La5dPZXmpWmk6g6FWt9TiOnXBDZBXdMBG/BPRzX57/ABA8HT+E9Qn020mjvLG1vp/IlhdJIZ7O5IkjZXQl'
    'Tg5HB4Ir9TdU8I/D/wCINqItSs9O1SGVA+0iGVgp6EqCWH5DFeJePv2b/DmieDLh/AVq0P2Z2uPsCZZXU/6zygeQ'
    'RjdtHB571zfXJy+KNmaVMFC3uSPzY1zT/wB9CynKiIc15zdAxu3tmvZfEzQ2aMhG1kyMHgjHbFeCavqSjeIyCTmv'
    'SwdVz2PHxVLkWphzyRzOWdsAdc11HgjSJvFniTT/AAt4fEQu9QmWFZ5nWOOMMfmkd3IVUQckn6VneBPAHiH4leII'
    '9H0hoYY9w+0Xdy4jtrdCfvO3Un0VQSfav0t8Bfsr6P4V0c2ui+Mke9uyGu7q3hi3SgfdiUOWKxj+73PJroxuNhQV'
    'nqzLB5fLESvsj7l8BeFvhn4D8G6V4T0S9sHttLhCLN58TNLK3zSzMVY/M7ZJ/CvMf2qb/wAJ6t8BfE+l2uoWst0q'
    'W08MUcgLu8NwjYAGe2a8ht/2VNMvGJ1HX7ubcckxRxxE/iopnjD9lvwbofgjXdWtLm9nvbHT57iDzZcr5kabhkAc'
    'jjpXn0syi5J8rPWrZdJU5Rutmfl5pzPaySqq4YEMD/umu5ExntGVeBKAwI/hz1xWFFZTPNLcLExiVfmbHyjPTJrQ'
    '0iePEltIeEOR/unr+Rr6GeuqPiVuc7NNeWUrBvnUHoe4ouLsXEYKjYQOhPOa6PVLRX4/75Pr71zy6eZpvKVS0jcK'
    'FBLE+gUcn8BTUk1qWZccT+YS561pNHuHTjiu30b4RfFHW8S6T4Z1KeM9JXhMMeP96Yp/KvRLL9nX4pOB9vtLGxGM'
    'n7TfQgj8FzUSxFKPxSRqsNWn8MH9x4NHAf4hn0FS3KoigLjNe/t+z54nRfMudd0GDnH/AB9liP8AvkVGfgDKR/pX'
    'jLQ4/oZX/wAKz+u0P5y1l+I/kPmppGaQqTTW65zX0S3wB05CWPjjSySf4IZm/rSr8CtEUnzPGtrwP4bOU/zej69Q'
    '/m/Mp5biekPyPmtgGPt708MvH4j+Rr6Ob4IeFsbj40hb/dsn/wDi6pyfBbwtCoY+MkbnIxZsP5yUfXqH834P/IP7'
    'OxH8v4r/ADPCEJyRSMwzycV7sfhP4YQE/wDCVAk/3bQ//HKqP8LfCn8Xil8+1oP6yVDxtC/xfg/8h/2biP5fxX+Z'
    '4VPMEGM4qmu6RiW+7Xu8vwn8KKqO/ilgHB2/6KOxwR/rOveof+FXeEUX5vE0rf7tug/m9H12j3/BjWXV/wCX8UeH'
    'TSR2qnn6CspZ7iaYM4/ddCPavfT8MPAjNum8Q3TH2hjH9atr4B+H0UewavdNjvthFL67S7miwFZdPxPnfxNaPbaH'
    'dSR42MigEf7TCuEsWJwpOT6nsK+tdV8F+Ab7TZNLbWLpUfbllEJYbTkY7VyC/Cj4exf6vXbzPuIKqGPpKNnf7i/q'
    'NXt+J5fpsBvJorS3UyNyxVRk7VGWb6Ada6owbWLr/EMH3FeneFvDXgrwneTXseoTXck0JhHmCMbFY/MRg8kjg57V'
    'LL4c8IzO32fWXiBOQrRI2M9shh0rzcTiOefurRHrYKgqVL3nqzyxcq1XY7hIvmc8eldfe+B45kP9k61byOfuiaJk'
    'GfdgWFeaa54V+IOiA3V5p6z2anm5s3+0oB6lU+dfxXHvWSSl1Onm7HQrPdX80draI0kkzLHFFGNzu7nCqoHJJJwB'
    'X1X8Pf2edS08prfjWd7a7wTDZW74eAn+KSVT98f3VOB3Jr5u+F3xS8PfDq9GvvoTa1qqZ+zz3EwjjtwRgmOMKfnP'
    '94nI7Yr1nVf2yvEdzkWPh2wg95JJZD/Na87GQxE706Ksu56WEVGD56ru+x77N8Krszq+m+J9StypBCysswBB/wBs'
    'ZrwT4v8Ah680XxO8mpXH2ye8Rblrkoqea7DEjbV4ByOcV5fqn7UvxWuWY2b6fZg9PKtQxH4uTXO2PxO8X/EO9ktv'
    'GN8t5LbRb7TbGkWxc4lUBAM54PPpWOFwOIpy5ptWNsVi6M4csVqeladFHLArjnIpYrZra+JXhXGDWZoF4qSNayHk'
    '8j+tdfLFuG9RyK6X7smmeXfqUp9MDHzCv3lB/LrWNfaEJAZIxhhXYGUvbRsf4WAbnHB4qCQtHJsk+4TwaSqO+hMk'
    'ebRvPZSbWJUqfwrsdN1c7cSnNXLvRoroFlHJrjL7Sb2zYvBnFbJqej3M72PRvtaTYK89sVp6Syu5gkIIbpXj9nrF'
    '1btsuFIxXYWGsrlZI25B6VlVo6WLhPU6rVNF2sWHSuIubfyj8oya9csb621OEK5G4jH41h6robDLxDcPSuanUcXZ'
    'msoX1RwVhcyWc4lDYxXp1peQ6rbo0I3S8KyDuT6VwTaPczTCCBDvY454A9ST2A7mqWt+JbTwraNpeiObm+mUrJMD'
    'ge4X+6o7t1NdcaHtXoc8qvJubuv6toXhCV7pxHd6keIk+/HC3bA/if8AQfrXheua/qOtTyXOpzMdxz5QPX/fP9Bx'
    'VC8u5Hk864YyzuSC56AeiDsPU9TWFLJuVmPQ169KhGCsjgnUcmJcTvIAV4X24H0rP2NgkHOaskrtwR64qPJwFHJr'
    'Zonci6Pz1pxyV57kmk+Zst+H604KeAPSpGCFuucVYB4HbNMAwozxk1KBgjNSxpi/TrT4DukeQ+y5+n/16ZnAZj25'
    '/Kn24Pl89T1/nR0BPUux+taUADMMdqzUBFbdkuWFZSRa7H//0/GJGyeXPrj1qFiQSA3T15xVq6u4ZCPKjC47ioPP'
    'UkghR9K+PZ9Kmys0knlP5bYYA9BVpQzKh+YgAZIGKQyMVx0U+lWlGAMuAMZAz1qS1roQ6jatbwxNMTsVgVCnnPWu'
    'fQyaleyRwp8zbiB/ujJ/QV1OozQzxRCVwT7c9ulYGmG0i1HfNwucqGHysDwc49qITsiKsG3ZHpnwsMS6rG7ABljL'
    'Y90YNn9K/b9L6Y20MisQGijbg46oPSvw/wDB2nC5vYrzTpFhktvN8yLn96hJIK+/Yiv2o015G020Ldfs0P8A6LWu'
    '3CT1aOWrTaimzT+1SMcknr6mvzY/aJO25m2npJK35sa/RqQn1/Svzg/aEy9zcr6s4GfUMc10V9YnNPofHlk5Rt3r'
    'muguXVk3juBz+Fc3ERnb6VptIDEqnqK5pozg2itIxANVMgn1qaY81SLkH0rNxNUzQRsFTVvU5zIlvH3C44+tY6uc'
    'ZU9KsSOZZofTH9aa2FNu6PVvDGf3XoHU/rX6E2EhGn2uB/ywj/8AQRXwF4PjDx5/usuf6V9+2ZUWNt0P7mPvj+AV'
    'w4roerlv2yczEHmvWfhvP/xLtVJxxJb/AMnryByATgD869N+HkuzTdYI7SW38npYGTVZX8/yO3GxvRfy/M7K8v23'
    'EKTiseS7mY8Z/Oo5pGJ4yaqM7+hr1XUuzy4wViU3EvrTPPkP8RqAu1REsCanmLsjQSeTrmr0E7dzWOm7PpVuP0zW'
    'kWZyidLFOBj5smta2vNpzmuUiY+ua0I5fSt4yMHE7y31BCMGtJbsEZFcFDOR0NasV0cdRmuhTMJQR0/2nNNM5xxW'
    'Ss+ec0jTN2anzsnlNBrmqrXJ7VUeZuxquZ+OannHyl83J9KqyXHJqlJP71WaYHuanmKUS1JN71AZRnk1VaUduaia'
    'fjAqecvlJ3k7VAXI6ZqtJMaj8xzxuqblcpa81s5rotM1FJV+zXLBeyk8g+ze1cgXPr0pBMVOQaFOw3BM6TXvD2yM'
    '3tlwgGXj64919q4GTcgzjNegWOp3rwNCr71AxhueD2rkbiTy5WTZ8uTlSOn0pTtugp8y0eph+dmmmU4qzPHE3zR8'
    'H0NZ7Kqn7rfzrJ3XU2TTJfNJpC59qh2S4+SNzn2NSC2vG6QOfwpJN9B6C76QvxipVsNQbpCw+uBU66RqLjJVV+rC'
    'rVOb2iQ5wXVFEufUU3ze9aq6FdN96VF/M1Zj8PLn95Of+Ar/AI1Sw9V/ZE69JbswTKpFRs+a7KPw9pw+80jn3OP5'
    'Vci0jS4+kAbHdiTV/U6j3M/rdNbXPJ9b1vS/D2l3Gta5dR2djaqGmmkOAuTtUYHJZiQFABJJwK5/wv480DxZqcej'
    'WH2qzvrgFrWDU7WSya7UDJNsZeJcDkqDuxziu88b+A38Ta54Y1COe3TSdCu57690uS2Eo1CTyCtsRJkbHhc748gj'
    'ccnpXxD4j0/4jRaTbeMPG016i32t3FtpPhTUGjt7mGZWLW1xD5T5lKAbx5TCTHByKxq4aUNXqi4YqM9Fofep8Kaz'
    'nEkaRn0ZsH+VSL4Tvv45Yl/M18g+CviHrfg24046R4g1jU5bq6a3l8Jak4uIGBJ82eO7usTWXzHcokYjOV6V9H+F'
    'fjRomv3F7pPiiNPCGu2F2lpJpeqXduHm85d9vLayhgk6SjONmSCMEZrpo0KE11MKmJrR3O1Twk5P7y5X/gK/4mrK'
    'eDrQ/fuZD/ugD/GugjkYtt7jqDVWaG/3bkmJTsAo3D866lhKK+yYPF1X9oqxeENJB+dpWx6tj+Qq8vhjRE58jcfd'
    'iapoXJK/aJywPK7AMVKu9WBZpjj1YCtFQpraKIdeo95M0U0fSYuVtIvxUE/rV2OC0i/1cUaj2UCs8SiThlz9W/wq'
    'VGj6BAMVpGKWyM3OT3bNLzEU4H6ClEynrn8Riqgkz1/nSuVfiqu0RZFov/dx+dRb3zziqqo6DCNwD0PNSKXPXj8a'
    'EwJssf4iPpSEISS2Sfcn+VR8etIcgUwJlKoAFAA9BVgSA+1UBuGCMn8hUhc45AH1NA7FHU/D+k6plrmECT/npH8r'
    '/mOv41wOoeBbyHL6bKs6/wBx/lf8D0NemCUD7zZHsDUinKhhnB9a5a2DpVdZLXudFLF1aeiZ4PJp11byeTdIYHHa'
    'QYP/ANf86d9gXqz/AJCvc54La5jMd1Esqns4B/nXH33hbTgxktpmgz0Qncv4Z5H51xvLYx8zoeYSfkef/YYscO2f'
    'wqCS1dOR849uv5V0F1p11acgCVfVOfzHWsdpOcMcEVhUwsNtjaGLqb7lHaNp9qcgx2qw5VhyOfUf1qmc+o+ma5J4'
    'eUfM64YlS8i2GwO1PWQetUTxyR+tTRt60lEpyNBWHbNTK1UlcemamVmPQVpGJnKReVz7VJk+tVRux2qVSe5rRIy5'
    'mZfiODfpwkP91gfwr4+8ToYruUR5JU9unU19n6mnn6ZJH3Gf1H/1q+RvFVkYNQlHKjGD6nmuWatUY5O8dTy9bu7C'
    '7RIwGex6isy6uXmBjnAkySPmANbckBDnaMAGsW8iyzYHPUGrZgZG542zFJJF/uuf5HIqePxN4ktQJrLUpkZSUT5i'
    'NqKSABtIxk8n3qvIGV8NyD1rIZtjSxMDhZGx7g8j+dCA9D0342/E3SXHl6g84X++27+fNdpbftK+JmG3XdOguwvV'
    'irK2PqCa+fZGCqQPTiqu/gnNWkmS5yWx9YWvx18EakFGo2dxaluvkyggHvw9dPa+Kvh5qQBttc+zk8hbqE4z7sh/'
    'pXwpKyMpSRATnqQD0rPlKbw8ZaPjB2MRz68VHsIPoWsRUXU/RBtOt79UbSb+xvskHENwgbAyfuvtPXFV5dOvLRh9'
    'pgkjwBjcvHHPUZHX3r87f7T1S35gvJVYHjJz+vBro9O+LHjzRUAh1CV0Xt5jf+gtkVEsInsaLFvqfZdzkgsR/Dz9'
    'TXH35Ucrk4YKP+AjP868i0r9ombcI/EVhBcj7pd18t+fR1711tv8QfBWuMPsl1JZSnJCXGHj3MO0i8j8RXLUwtRd'
    'Dop4mDH3e4/IeCw28epHP86527ysknl9sgfog/rXUzRMwSdCskW0kSIQ6EgDow4zXNPZXN6/lQ57sT2HXBP05rC1'
    'tzfRnOXLs7ZHIHGfZaySpc5wSfTHeu4m0q2s0Imb58bcds9T+Qrmr26ijzs4A4H0p3JZjPbnAI4HeqcoRBheTU9x'
    'eSTHbEM9qt2GlTztvkBociUjMs7JpJhI4zT5ZY/tEuOgbaPovFdFqcf9nWu9Rhh0+vb9a4i3gnaLcSWJJJ/Gs1ru'
    'W9D0f4aWOkX3xB0NdXmSCxju0muZX+4kUPzsWwCccelfe3xS8S/BHx14YudGfxDpkF8My2c6rJmOcdAxEf3X+63t'
    'z2r5N/Zt8Ff8JBresazqMJktLG2FqhOcGa4OTg+qop/MV9OTfB/w3ckqUuE3f3GP/wATR7d01KKSaZ0U6EZqMpNq'
    'x+dus2tzpd/NYXQ2PGcccjHUEHuCOQe45rOguycIfevu/wAbfs72ut6Ur6RqEqajaxlbf7YBskTqIncAEAfwk/d6'
    'dK+A/FOk634T1aXSNctZLK7jOdjYIZc4DIykhlOOoqqMlLTqc+IpuLv0LxkycdKdBtafD9F5rkk1F9wLEitOG489'
    'gUbBPXFbuBzRmbkdo99dzyRKzvIBGiqNxPoAB1zX2F8Nf2nNI+G/h3TPBbaWk9npymN5I3lt52Z2LyOVmXbuLE98'
    'V4X8HvF/ws8F6/L4g8ca5HHc2QZLSyjgknYSsMGZyvyjaCQoznOTXuWsftPfs5S7vtUc1+T1xpmc/i5pQq1aU+am'
    'dSpU6kLVUeieLP2yNIMsdt4H8O3esF4wWln2RKsh/g2qxyB614xr/wAZP2ivGTldF0tdHtmH3YpGj492Qbj+dcbP'
    '+0X+zxp9+NR0Hwlem5UkiSOCG35P4/0qtfftmaVEMaN4Oc+huLwD9I1rWrj8XLpYmOCwsTQHw8+OXin59a1NU39Q'
    '7TTY/wC/jkfpWnB+y3rl8udZ8Qzrn7wgCp/KvOZf20/F7ZFj4a023HYvJNLj+QrMuf2xPitOD9nj0u0U/wBy1Dkf'
    'i7VzP28viZvzUY6RR9IeFf2cfC/hHUItXt77UnvYTuEpunXn6LgfhXr+s+ItTdP7NiuJfLiG1mDHcx9261+bupft'
    'O/GS/wAlNeFuPSG3hT/2U153ffGT4pXTM9x4ovfmOTscJ1/3QK5a+CrVFaMjppYunB3lG59M/Ef9nyz8WXlxqun3'
    '95p1zcMXkVCTCzHq20jjPtXyL4p/Z28S6IXa7uJ7iIf8tEfKke44NNufHnjK8H+k67fy7uu65kP9a5W91PVLnP2i'
    '9nkz1Lyuf5munB0sZRtFVtPQwxM8JV1lR19Q0W1vfBkxFnOyDPKlsA/hmvcdC+JzwKjXGorAwHXzcH9K+bpo95y5'
    '3e5OagaJEHGM17CblrN3Z5M4RT9xWP0D0X9o2HQ4Ff8A4Sc5X+AB5fwxiuluv2ytI1PTbvw7ezPdf2nBJZBktWU5'
    'nUoCSWA6nrivzRLleA1PtpUS6gn3D5JUb8mBp/VoPclVpRTSZ9s+G9K0i+8MaraTEC5jjEcK5ADSHq3vgLivCrLQ'
    'dY1LxBbaXoNrNe3tzJ5SW0Cl3ck4wAPTuTgDqTXq2k+Hta8Q+IbLRPDCPPf30wEMae/JdiOiKDlmPAFfUbP4Y+CO'
    'k3Wk+EpYLjxDKpTVtdKh2Eh+/bWef7p4wPlXq5J4rtdf2HM3q3sj5yhhnimraJbs85034I+EfBmnR6j8adZZbnAZ'
    'NF02QGT12TTgEk+ojH409vjhoPhULZfDDwfp2jxxnm4nQNcSAf3nbdJz65rxrxL4lvNSvZbkPIWb70sjl5WJ7tIe'
    'fwGBXCFjkuev864uepPWb+R7UaNKkrU4/Pqev+I/jP8AETXnklutU8lHORFCXwvsMmvNLvX/ABFdPmfUpznrjj+e'
    'awZJG+Vc9SaVpCwwc8A49OapQXYpzb3Y5r3UJQxN5cEf7+P5VC0twSxeedjwOZGpkPCHPehjlDnghgKfKiLslMzR'
    'qCXkJyOC7f40rOAC53nPX52/xqqZCW4HGOv0pJGc44zgdP60WAlcxJwgOCM53N/jVUiFiBtPA5yzf40M4BQE9Bio'
    'ncA496LFE6G2TDGPJI7s3+NDNaMMGIZJPUn/ABqm7AH1BHJ9KazoHXviiw9BZHt9/ltCrJGCyrz95uCevXAqN7i2'
    'XG23Q8c5Bx/OqFxMUmaQegH602aT7pXuM1VgRb86E/8ALvEMtjp/9enGaMceTGPbbWS0jLz2J5qTcSuAeDSsMvrN'
    'GMgRRj1+UU4Xg2riKIY/2RWYCTwe/ekLnb2FVZCNN7wFsGOM8f3R/hVZnjYszQxnj+6Kp7zuFAbOeualoZoR+Rni'
    'MDP90lf5Gtuy1i7sSHtbqaIjsW3L+IP+NcuXK/gKcr8Dn0qWr7gQ+LLWPWw97b26W+pBS58kAQ3ary3y/wAM2Of9'
    'rp1ryeOTeNxPXpXtUY80bN2OQVburDkEe4rx3xpfab4c1p4bhWT7QouERFyMPkMB/wACBrSnTlN8sFdle0UVebsV'
    '5AAMnmmaXqh0jVbbUI8/unG8f3kbhh+VcbdeOdLUfuoZnPvgVhy+M/NP7u04/wBpv8K7qeX1+sTKeNpLaR9oQy4m'
    'ju7c7gMOD2Knn9RXr+nGO8tEmU5DDNfMXwz8RJ4g8MgykC5sZDDKg6hTzGfoV4/CvafDOuLa3IsZmxHKfkJ6BvT8'
    'a8bGYeUW4tao2pVVKzWzO5NuEl2dQwIGfWpDGkyDPQjNXZIw2yXspGeccH6VWKPEzbhwGPA7c15tzrcblFHe1fY/'
    'K9jWl5EN2nY+1JNbiaPcnNZqyNC23pjvWi1RhsynfeHYZSSFAz6VyN1ok9q5aLIx6V6UlwX4Y5NRzwCQHHU1cakk'
    'TJJ7HndprN3p8ilz09K9c8Pa6NeQxIvzIu52PCqo6sx7CuSTwx/acpDlYYV5lmYfKijr9T6Cuc8ReK7SxtW8M+FV'
    '8mJDiab+J2/vSsOrf3VreOGjW6GbrunoaPjbxpFbs+kaDhnYYkl6Z9yR0Udh3rxSac5YsxeR+Wc9WP8AQDsO1PZy'
    'quSSxY/MzHJY+pP+cVmSOC3P5D3r1aVKMFyo4ZTcndlN2Z5Cx6AcVSkJA9M8VccAKfQ1BIBhSPStiSo54IHfGKAC'
    'rE8ccCnOvCg9zkn6U3BOMipY0LyMDtUowSccD0qJcBjjt0pwOOlQVcsLjcCMcd6OvJqFX6j1NSFicYxkUhjscAY4'
    'YgZ/U/oKtIMVTBcuAOwJx9eP8auJ0z1JoewWLCtjjrXU+GrKbVdXtdMgGZLqaOJPq5ArlFwPxr3X4AaSNR+IdnO4'
    '3R6fDNeNnpuRdif+PNn8KztfQctNT//U8CkUomN3Q02Lhst1FUpL+M/KHJGc4qm9xHI2d5BHYV8Zzn1ns2dBHLHn'
    'GSfSlNxGr8VzDzIASrnd2yajEsjMB5mR3pcwKnbU6q7u0lRQoChExx3Pc/jXPKw3KQc7fekkYrGhiJ5+9U1mI2uF'
    '8wbhuGRU8zQ3FM9z+FCtd6pBbxqd08ixg44O9gv9a/ZmC4iihjhYp+7RU5P91QK/L74E2EGueNdKs4IgqWrm5kVe'
    'dqQjPP44r9DnRixIVua6cBOXvTt5GGKgvdidx9tstw3yIOea/L/4162+ra5qdptCpYXF4Aw/jVnxH/3yOtffrxSH'
    'kKRz1r89fiv4Y1rT7vWdRu4JI457mXytwI81N2S6nuBXVUqX+LQ4K1JqPu6s+Xlb5zV7flaoohCM3fNTqw2ihvU5'
    'ErBITnNVH45qSRwOKqSPxUNGq2HJKAcHoeKuWzEzop7GsnOa1bBszDI5xxUPyKTueseEb0x3wtydoYdPUg1+iFop'
    'S0gDY/1Uf/oAr84fDgVr6B/4ty81+kcUg+zQAE58qPp/uCvNxD1SPay9aSaEY5OPlr0HwRIsOk6ucj/W2o4+kled'
    's3U5Ndr4Uf8A4k+qDnme15/CSng3+8Xz/I6cWv3bv5fmdG9xVZrjJ61XJJOOabXoXbOBRRN5ueaBICeprG1DU7HS'
    'o45b6VIRLIIotzBTJIeQi5xkmvJ/EvxjOh71sdFlu5ImG9JJRGxUEbwoAPzYztBOCa1p05T+FHPWxNKlpNnvCFas'
    'o49K+dG+Ml1e25utJtIfLBGN5Yna2djEcYzggjswKnkVkt8XvFjn90LaP6RZ/ma3jhqhxzzSgu/3H1cjircbHstf'
    'HMvxQ8ay9L0R/wC5Eg/oazJvH/jGb/Wavc/RW2/+gito4eXc5pZrS6RZ9xq0uOFNSfahF/rJFX/eYD+Zr4Fk8T6/'
    'cAm41G7fPXM0n+NUnvrmTJlmkf8A3nYn9TWqotdTB5pF7RP0JPiHSrbia/t0x2aVB/WqM3jvwtB/rNWteOwfd/Kv'
    'giGQk5zWrC5Kj0qlT8yfrze0T7Iufin4OhJzfmTH/PONm/wrJm+MXhJf9Wl3J/uxqP5mvlgc8EcU8Y+ntT9mhfXJ'
    '9EfSE3xl0dv9RYXDH/bZV/lmsib4wyHPkaav/A5Cf5CvEUQdjnFTHCjpS5EP61U7nqM/xX1xz+4traPPszH9TWbL'
    '8SvFUoO2aKL/AHIl/rmvPt69DTTIFHXIoUF2F7ep/MdsvxA8WxuJDe+YAfuuilT7YGP516x4V8a6f4iAtZcW1+B8'
    '0JPyv7xk9fp1FfPL29xDAbicJCm0OBK6o7AkKCiMdzZJ7CqDMwYSRsUdTkFSQQR3BHelKnGWxcMTUpu71R9jnANM'
    '/CvEvCvxHk+TTvEbk/wpd/yEoH/oQ/GvXVmDKHUhlYAhgcgj2IrknBxdmerSqxqK8WbEU0kRyhx+NYvifXbXQNCv'
    '/EWopLLBp8LTzCBS8hRfvFVHXGcn0GTUhnNZ+pebdWNxbRytCZYnjDocMu4EZB9RUSeljaMdTy6z+NekQ6zCViWb'
    'TrqAOqgqbhSD80igHDrgjgV7lpeuaXrlot/pU8dxC3dOqn+6y9VPsRX5T+PvhR8QPhdeSazpm/xBoRleUQA+Xc2r'
    'OdzNbyr9zv8AKRsPtXX/AA0+LV1IRqOnX0iSwHZcSbNk8P8AsXtr3H/TRQV+lc+Fx86b5ZK6/FHRisvjNKUXZ9+j'
    'P0+Vs9Kq3epWdlgXEoRiMgck4+grzLwb8WNE1wQ6frDx2F9KB5Uu4G1uM9DHJ0Un+6T9DXpk+wMTgbwMZ74+te/S'
    'rQqx5oM8KrSlTlyzRyOtfEfwnoKCTUr+KDnkSNtbHcheSfyrze6/aW+GlrMYhfmUD/nlDK5/kBXm/wAXv2fdX8Sa'
    're+KvBN3H9quj5s+mXjGOOSXjc0E/IQt12sNue4r5K1DwN4v8POyeJfC2rWbp95hbvNGfdZYgyEe4NJtp6s5Zzmn'
    'ZI+83/an+GES58rU5feO3TH/AI8+a6fwf8f/AIZeNLgWNnqf9nXrNtS21FRbu/OBscko2fTdmvy7fVraKUwW+l6h'
    'O46qlrKf/Zc/pWlDa+LNRVV0nwLrl4zn5cWcoB/FlA/Gq5iYzn1R+zoZhwR/+qneYMV8K/A29/ac0q5t7PXvDyQe'
    'HC4Uwavep58EWOsG0vKCOysNv0r7Y84uM4K+xqlK/Q3LzP6muc1vwz4c8Si0HiHTrbUBY3C3Vt9ojEhhmT7skZPK'
    'sPUVr7j+NKWGKe4HzZ4n+B/9pa/r3ijV75tSbUGe4iuRmK+so4oTst4UjHlzruAAEgz75r5TTQtbfwimr+NdFhvf'
    'DWpwOitd2ayT2pkJRikcxjuIbhSMhkY4OCua/T4muM8YfDzwp49Glf8ACT2huW0S/i1OxYSOhiuovuPlTyPVTkGu'
    'OrhFJ80HZnVSxTj7stUfNfg/4peKPDOnR6louov4i8O2UNpZvbeJ9Rt7a8U5CK9lNHHukcoCDFNkk4Oc19O+Dfi5'
    '4C8eyvZ+H9QI1CIkS6ddxPbXaFfvYjkA3gf3kJHevn3x78HtV1fxprPivV7m20vw1pmmrf6fcaaGF6l/b5kmeaAL'
    'tfcB8roQwxgZrx6HxRqXxB/s/wAY/ES5u18L2kazadqul3rpFa3KoVM8ksKGVZ9pxKj4Ck4IqY150ny1P6/yK9lC'
    'orw/r/M/SCeOKbO4fN6jgiqfkyLjBD46kk5/Kvjf4f8Axi8bWOg3E2i6Rf8Ajzw9puomP7dPdodfGnMQTMLONMTr'
    'EP8AVncHcdRmvrDwn4u8P+NtKg1rw5dfaLecuoWVHt50eM4kjkt5QsiOh+8COPpXbTqxmrxZyzpShubqZHoD9D/h'
    'VmNWY87vr0oLhe+acGrRskw9W8RWGkP5Lgyz4zsHbPTJPSuSuPG2oSE+QqRL7DJ/M1oeKfC1xqE51PTiGmwA8RON'
    '2OhU9jjtXnrW08GRdxPERxtYYOfrWnPCMeZnn1PbyqcsdDol8Q6zcyBBO7FjgKOp/AV19npmsTxrJMxjY8kOxz+l'
    'ed6H4ptdJaSSGFZyTtZifmUjqu4dK7S0+I9gTi6tJkH95CGH9K5XmFB7Ox2U8rr2vUd/mbx0bUQOLgA+xamrp3iK'
    'I7orkMPQt/QiqrfELw8B96YH0Mf/ANemL8RdBIwomOP9kf41P12h/OjZZfU6RZsLf6tZD/iYW4lTuycH/A1oW2pW'
    'd3jy22sf4HG1v8/SuOvPiVpcULmOB5DtOA5ABPbOM8V4teeJ7+aVpTMw3uW2r90E+gHT8K4sTm1Kk1Z3v2O7D5ZV'
    'mnfT1PqSTLKVBK9sjqK4CTW9T0y9ljmvPMVGI2ZHTtxg1yGl+J9dS2jdpGKsATG/Ue4J5Geo61lytLI7TOxLOxZi'
    'epJ5ya9CniFKKkup5dem07LdHqMfjITDy5FCk9HC4Gfpmqv9qC7dgGJI6+/0ryy4vZ7eNmiiaZ1GQqkDP4muIvb/'
    'AF28lMlzDNCq/d2OVC/98/1pO8nuQ8R7NXtdn0Sb2KLlm5rLvr63nBHlKx/vEc/pXjWn69qNsu2SVpk7LL8zD2z1'
    '/Wunt9beVVLxjDeh9PY0+RbMI41S8joHQnlTj2/+vVJlkU/Ov0NSQ3kUhGGwfQ8GroZT1qJ4aMttDqp4l+pnrz05'
    'qwuB2qYxRnkDH0oELjkciuKphZx2VzthiYPRuw5CBwKnVz6VV+6cHilDCsEjZsuq+euKkDAnBJqmj+1TqxzwKoVy'
    '3w8E0Yzkpn8q+ZfHNsftpY4DZIA9uK+mLc5mVT/Flf8AvoYrwX4hWrLclsAEN+JFc1ZWkmWtUzw2aMAkHvXP3qIG'
    'JGORXS3KMsjZrBuV2kZ6e9JmKOUmU8jPI5z+NYFypF23cOit+WVP9K6u5Ub+QcVg3ifvrZ1xj54yfTcu5R+a/rSS'
    'GzJkX5cjrVJ1Hmc9CK23jHlNnqOhrKmUZB71SE0Y8qfMV6Zzjv8ASst0xjn1GK2JQctx71mSD5z371oiWY04wfcV'
    'nz5Ktx1Fasyk7yw5GP1qnNtK4zjK1aM2c9MoIznlu3/1qqRr9nctC5jYH+Hgfl0NaM6Z4HOKoPEc9OM/zqjPY6bR'
    'vH2u6E/7idljPDADcjD0ZDXunhv4iafq1j9nVFgvJDkEH5H+hPQ+gPFfL0sZ3Z6c1HbXElhP59uSPm5U8K3v7H3F'
    'Y1aEZrU2p1pQeh9XXj3c4OVIAz19T1rIOl3E7AbT+NUvAXxDsLoJp2t9MhRK334/QP6j0Ne1Srp8BaUbdpGQR0x6'
    'ivIrU5U3ZnqU5xmro89sPDIUh5uPaunNrb2ULMcADgVXv/ENnbDggZ4Feba34pe8cwQsQSTgA8n2rJQbepXMkhmu'
    '6kNQuhbW/KRncx/Qf1qnCVhUqwpbK3WKIGUje3zMf6fhWN4n1+w0HSrnVJ2BKKRCmeXkI+RR+PJ9BWip3fKiee2p'
    'zdx+0B8RvBd3e+GvBGuTaXp6zb3SBY8tOVAdizKT6Dr2rmb746fF7V2/0/xfqzg9QLgoP/HNteBG5eaZ5pW3SSMX'
    'c85LMck1pxOhAGc16X1eMUlYmNZ9z0S88aeLL9T9t17UZ8/37uZv5tXEXOoakLkTx3s/mL0YyM34fMTxQGj2YA5q'
    'B0VmyD+VEIqLHOXMjVi8Y6+i+XIYpvRmXB/HFH/CR+IpyQ1z5KntENvH1rNitgSD1q8sOO1aSlHojFU9bliBsDJP'
    'J6knrVhniAy7CqnlKOeM0hRcYwM1gzZMspNCDlSKtCRD3BrEcMnfioEniQ/NIB9WAqWkxm60rD7uDVSWeQn5pMAd'
    's1UEkUgxGwY/7PP8qtQ6Nq942yy068uCegitpX/ktVGJL8xhm7b6aSpPJ3V1un/Cz4o6mA+neD9bnB6EWUyg/iwF'
    'dtYfs4fHnUFBi8GXsIPe5eGD/wBDcGtFSl0Rm5xW7PGWcg4H+FQsBjNfTVh+yB8er5h5umadZKe9xqEWR+EYc12l'
    'l+wx8VJwPt+u6JaDuFM8xH5Ioqvq83she2gup8VMN2c9PrVSWMdCK/Qq0/YF1tsNqXja2T2gsHb/ANDkFdFB+wR4'
    'aXB1LxfqU+Ooht4Yv1JY1tGhNGU8TTPzFYhSSCKrSJIylkzkc9K/WSy/Ya+EVsR9tutavcHnddLGD/3yldRcfs6/'
    'AL4d2K+IV8NPf3lrLH9jiurqWXzbvcPIXYSFPzYJBGMDmtZJwi5SZiqkZy5Ujg/CVjc/DLwrCqq0HibWtPgn1K8A'
    '/eadYyoNltET0mm5J9Op4FeJeJNafUpygwkUQ8uKPsiA8D3J6serE5PWvZviHrUkSSQTTGe8nkaa6mHSWduGI/2U'
    'wEQdgM96+dLmTfMXbvk5/GvOUpTk5yZooRpxUIdDn70gdM4YgfiKzgh53dT0q5ONzj3NRKSTtIGR/LFdSMHuUnTL'
    'r+JqFjiMnnHark2AVx3yapyA4CjqQSKtCIEbbGD360N04yc85oIIQYzyOacindnk47UxEADDLKTwMEdueKdJkj3w'
    'OOnGPannBDnkHNRyZUrjnA9aTYypIVLgdOAaickucdvWpGbD4x0qsznJJHWncBxJJqB2IfcKdvAIA5zUTtnJ7UJD'
    'Ksi5yGIIY549iODTjyMkAU3OCd2Dy3FDN0I6Ht702NETFSD6ZzTS7dB0xjFNwCD26nntQcAc/nQMXLdOtJ3Un60L'
    'gEkknjj60gbdzyMUCuhN20gjrinK2BzULHBIXJFKvHXPr7UmguSkhs96kUg4HTFV1y4qxGMHjpUtFI0Ijt5/lXjf'
    'xwtN9po+qj7yvNasfZgJF/UNXsC5IwK8/wDi7bLL4I849be7gcH/AHsof511YCfLiIMwxUealJHyiUZmqRVCjNem'
    '+DPhF4+8bol3pGneTp7nAv71xbWx9SrP8z/8AU17dbfspStAG1PxtplvJ/zztreWbB9NzMn8q+kq42jT0lI8eFCc'
    'vhR4F8OfFy+F/EkZujtsr0C3uPRQx+R/+At+hNfVd68kfzReuQwPA7giuZf9kjTi2G8cxn1K2IP/ALVr2+x+EcEG'
    'nRaePEazJEqJG7w/MFUBQCd/PTrXz2YVqNWaqU3d9T1MLCcIuMiTwj48tL6EadqDhblBjn+LHcV6XCBcBpcghwrL'
    'j0I/qa8dufgm3nrc23iKJHU5DCBs/o9ek6Hp95o1vHa32qQ3RTgMI2UlfTBJrxMRQi9aR6FKtbSRsCN4Gxj5TVG9'
    'sw+XTiuge609kxJcouPxrnL/AMReHLBCJ7wPt7DC1z06FV/ZNKlWn3MtXljlCgFm6YHOa3HeCwt/teryfZ0AzsOP'
    'MbHt2+prgrv4hxfMuhWZGSF84jHU4yXYdPXAri9Tu7vUZDJqcpmYnIjGfLX692P149q9Clg29ZnDOv8AynQ+JPHU'
    '+pxmz0s/ZrNQRuXqfXbnqf8AaP4V5xuESbEGFHPXOST1JPUnuamuNzEgjk4+mKzXJAx3zXowgkrJHM3fVjJWYDGc'
    'ZJOBVIknLDjJxz/OrUjnPptXJxVXcAAOueTmrYiu/wAoAJ6mombgA9/8aJyGbA6gcelMTJn9Rn8scUIaJZyoG0eo'
    '7VXbaTgD2xT5SWfryD1qEMTk59qgoOgJ9aYchaMnaDTSSSPwFIY5RgjFWI8YJqvIwLYxUhO1M9gMmpsDuSRupZ2H'
    'c4H0WrPmhRx+NZ8PyoufTn1yealJy3A4okCL6Pn5e9fXH7NdskEevazKB92C0Q/UtI+P/Ha+RIWBbIr7n+DekDTv'
    'h/aTONsmoyy3beu0ny0/Rc/jWUm1saRSb1P/1fkkzw5yDUJuI8kgHPTNQSMQDlev0qi0yr1wPxr4mzPs9DXF1GUC'
    '7eR3qQX0Wzy9vPqBXPm5XnLBc/jTBfxKrKWz6VXIxOSOrj1BCixKg/E8n8q7TQNGlvyJd2ATwFH9TXkEN9Erg571'
    '9V/s/wDha78d+IY7NmMGlW7LJf3LHASP+4p7u/RQOnU9Kyq05vSC1ZVOUFrI+5P2Xfhy2geH7nxjdR4m1M/Z7Uty'
    'fs8Zy7jP99xgewr6yjyOCRWTpuqaPb2cGn6fsjtraJIoY0xhEQYUD8K0P7QthzkV7FCkqcFG55Fao5ycmi06KwP+'
    'FfH37QmqiGzudIYKU3llyMlSRzg+9fWM2qxKh29P0r4f/aTKw3kVy0yAX4+RCwDb1HzLg9cjkVhjGlA1oQk3ofEM'
    'yAllAwMmofLCgn2q3KAHPSs64mCZCkZqIzutDnnRUXdlGaQAn1qizt3NLNKAeDmsue5UfxVujl3Zc84g8Vbtrzyp'
    'Vf0rmHvo16kYqL+2LSHJlkGB71EovsXG1z6G8JFbq+tnjbdl1AA6kk4xX6URMEjSM/wKq/8AfKgV+SXwu8dadH4s'
    's2tgZ4oJN7SYzEJF+7n1554r9BbH4oQcJfoATzvTgHPsa8rExfOe9gkow16ns5dSef5V2fhj5dH1MjoZrX+T14jb'
    'eLLC/Aa3nH0zg16h4S1WNtI1HEmR59sM/hIaWEl+9+/8joxUf3f3fmdSZMnimM7DkVTN5F1L5qM6hEPU16Op558n'
    'ftS6hqcF14WSBpI7cC7kVxkL9oVo8DP94JyPbNc/4T8SReOrAadqBC6vCmFboZ1Uf+hY5FenftDapf3PhH+xrCC3'
    'la43SZmiDlGj5VkP8DZ7jtXwpo+sXcUq31qXtryzcCRM4aOQc/iD1B7104asoz5Lni5lhZP969mfRd3/AGj4XuZr'
    '9IhMuxgyHIRgccsB24G7HIPzDkEHrbi3RFjuIHEkMyLIjDnhhkA/0Pcc1maD4otPHWjvIFVdTt1zcw9Nw6eag7g/'
    'xDtXMRzt4Zu5JZNzWM5+bPIhY9Af+mZJyD1Q+xNevHVXR89L3dGdeWIGKgeTA6f40rSLjcuQD1z1B9D/AJ5600Yf'
    'inYhsjW4BPl7STWjbwvM2wK25sADHc1mvA2dykg+tOhuNQtJUnglIdCGU9cEfWqSRJ6C3gPVzCHiniR8ZKMSCvtX'
    'PT6frGnP5TujuTjbGSx+uMdKmj8e+JshZJI2GepjGa0Y/H2uRZ2R2r+7wIx/M0nHsa3iVLcaqufNglK+y5rbgjEq'
    'YMciP6nj9DSQfEbWVB3WtifX/R1qebx3qN0oVo7eL/rlCi/0pNM0jOK6jxAV5Bx9ajfI4zmsefWric7nck1ROpEd'
    'T+ZpOLK9qjdclTzxW7ZyadoOjyeL9eCfZkLJZxyHAnmXkvg9Y079ieKx9Igt/ssviLWyq6XZgsVY4FxIoyIhjnb/'
    'AHyO3HWviL47/GyfxfPqNvcXkdjbWNsBClspA8tXCeRBFnAfDfL26lqRtBJtNnQ6t8VrjxT8S9P1Ga/EGn2moKZb'
    'mUZVh1ZFHclemOFHpxX1FZ6zpOoJ5un3CTxk8MhyK/KzwWdd1/U4b28i8i1t0MVlaJysSscsSeryOcF3PU+2K/QL'
    '4e6K2l6UplG2SU7iPSiMGt1qRWxClLlTukexLKp6D866vQPG2oeHSsLf6TZE/NCTyoPUxnt9OlcArMowCacZMjBp'
    'ygmrNBCs4Pmi7M+qtJ13T9ds/tumS706Mp4dG9GXsf0NXGZmBBzzXydYanfaTdreaZKYpV7joR6MOhHsa928M+Or'
    'DWwlpfFbW+PG3+CQ/wCwT0z6H8M159bDyjqtj3MLj4VPdno/zOwmtop4zFOgdGBBUjIIPbFfLXxM/Z203VLz/hKP'
    'BMr6RrMIJR7dthPfHowP91gRX1RJIF4NZ8kwJIGTXBVpxl69z2KU5R227H5jXHjbXvBN22geP7YWLCTH2wIRZTE9'
    'DKgybdz/AHl+UnmvpnwH8d9a0GSHT9UD6rpu0FYpGBuY0P8AFBN92VR2GSPpXsPjLwL4e8bWMljrFqj71IEmBuH4'
    '/wBDXw34m+EPjb4SSPc+Gom1nw8XLPp0jfcyeWtpDzEw67fun2rkjOpSlzJ2ffp80dM6dKtHlt8v8j9UfC3iLQvG'
    'Gmrqvh+7W6h6Ov3ZYm/uyxnlT+noa6PzGh4UlR6AkfyNflV4F+I6Je/2l4Y1Gex1GzA85HUrcQ/7F1D/ABof74DA'
    '9/WvtTwR8dNJ18Q6Z4rEelam+AkwP+h3OejRv/AT3DHGehr38NmUJ2jU0f4HgYrLp0/ehqvxPd5cSkknn171X8hc'
    '8kn6nNTqucHqCAQeuQehB9KkZV/EV6R5xAFCDA6U8OM1Wd3BOEGPUmlDE+g/WmBcDdx1pSxNVcn1P8qA3rx+tKwF'
    'tfqDUocVVWTHOaRn5pgW2IYbTyDxXlvxD+G9t428I3XhPTb6Xw8l1NHM8thHEu8I4d45Iyu1kl6ODyfWvRvMo83i'
    'plFSVmOLad0fGnxX0Bvg+Y/EXw+WbQnuEjiE6RmTTjds6xrHMFybfd95XYGHPXFeczaFZ6PNb6p8Q472w8a2c32x'
    'PFT6hdEhwSWkAiYwyRYwvlKAGHBFfoVMIp0aKZFdG4KsAVI9CCMV4z8UfhSvjvSbfTtLuodO2ahb3tzHPb/aba7j'
    'gJPkyRbkwGJySpBzXDWwr1dN28jqp4haKp955noX7T2srcXza14c1LX9Nh8j7Nf6Dp04uCGwJnu7OU4jRc7lMbNk'
    'Z4r7Bs9RtrzcLW4inZAGYRurMoIBG5QSV69+lfnd8SdH1n4camPC3ge5n8OweIX+xRiS6eCC8YqGeC1uTnyy2cBZ'
    'TyOFbtVK4t/h38OdH0vU77RtV8K+N9HfNtJo0hinvyWGEfcZIrhW/wCWm8ZA6UUsXKGlb7xzoKWtM/SJ7udOjY/C'
    'sbUjHqEYjvF80A5APUH2I5r580T43eKLK303Ufiz4dtvDui6jFu/tuC9WW2tpShdEuocF0342hkLANwQK9307UtJ'
    '1zTIdZ0S9t9QsLhQ0dzbSLLEwIzwykjPsefau2NSM17pyyhKO54Z4yvtD0vWW81LrRrnPyXipvtpf99V7e/X1pum'
    'eMra3CrrMMTwNwuoWjCW3b3fHzRn6jH0r2u9sLDU4mt72JJo24KuAR+teOa98GYEmbVPCF3Jp13ydgOY3/2SDwQf'
    'Qg15lXB1Iyc6T+R6FLFQcVCojtYm0y+RZLV45FcZXG05HsRwfwqVdNtO8S++OK+XtQuPEHgzUC+sQSaJMT/x+WyG'
    'bT5j/wBNoBkpn+8tei6R8WI7eOE+JI1jgmOIr62bzrZ/xHK/Q1jDF00+WvFL5Gs8LUa5qErns32GxYY8hPxGakFj'
    'br9yNV+gAqlp2rWOqW63VhPHcQv0eNgw/T+VbUdehFQavFI82Up3tJsotZB+QBnPXnNQSadKmDHlucnHFbowDUmM'
    'jmtL9jPlORlgdQcgq3+0OKy5rMNncmfda9CMe/jbuH51VmsYAMy7Yx1yxCfzxVKZMqaZ599libgqP+BAdqi+xbRh'
    'eB7f0Jrf1DU/DNg2LzVrKI/3XuIy35Ak1yd3458AW5IGu25f+6gd/wD0FTT+sU18TRH1OUtkaIjkUDDfmM1qwSzI'
    'fvbh6H+leN6l8bfAumzGCU30jg8bbR1Df7rPtBrMb49aW640nQr25PYyOkY/JQxqXjcOvto0hgK3SLPoZJ5CQcAD'
    'vV1JwOM18k6r8evEkKlodKsLBR/FdSsxH13Mg/SvI9d/aY1u3JWfxTpth/s20SMw/FQ5/WsZZlS2im/kdEcuq/aa'
    'XzP0Vd946bvwqtLJawDdNPFB/wBdHVR/48RX5K69+0Z9rVhN4n1bUmP8EIeND+ZQfpXk03xY1O+nLW9lO248PPMW'
    'b64A/rXPUxykv4f3s6qWCkvt/crn7bWms6PfXbWFhqFrc3KIZGihlSRggIBYhScDJxWnkivgb9njxv4QthDr2raN'
    'KuqxI1u12txI+3f1YQsQgJHoPpX3Dp/ibQNZx/Z13G7HnYTtb/vlua5qeJhN2T17HTUw1SCu1p3NtXKsG7gg/lXA'
    'fEW1BywXO45B7YPNegbBj0rB8ZWon0uObuFHT24/pRiFomZwe6PlO+G2V9456Vz1yqspY9q6jWIjHcMG4Jzx+Ncb'
    'cyMAyntWb2MktTLuUUq3HIPX2rm9RwkKyH7scsTH6bgp/nXSu5LFSeSODXN6lG0llcxesbfmo3D9RSQ3sVZFYbuw'
    'rKkGOvODzg1uykOpdemR+tZbxbi2cckVSYdDHkQZ3DrWVIgzzwR+tbMoyq9v8azZgVdu4yD/AI1ojNmJKvLbudwB'
    '/wDrVnSqAF/ukY6deTWxNkAEjOM1mTDa30J4qrktGHMu1sYqmem706itaZMnPXofrVJlAB96tGckUpwpOOoIqlKF'
    'K/katykAL7DFUHJ5GaYhAHikSeB9ki9G/oR3H+RXrei+L9RvtHksIMyXlquYoS2C/cRqTx838BPGeDXju/O3Gc1P'
    'DPPBMs8DeXLH0PY/7J9jWdSnGS1LhNx2MHV/i54gmmcQ2BiZMoyzk7lYHDAqOhB4IrkrT4oeK7e4mkuLeOUt93aN'
    'pAHbPPFep+I9Jh8ZWrazp0YXV7cBbqADm4RR94esij/vpfcV5rZ2UUrbQBleSfSu6jRw8o3UDza2Ir05WcjSi+Kf'
    'iaaznuRbDdEVGxdzYVs5c454OB+NcPqXijWPEMitfmWYrnYiodq564UCu/8AD0uo+HNXTWNGuvI1G2kE8Ei4+Uoc'
    'jKngqejA8EV+lPiH9qvwmvg/SdU8JaDaR63fWaPetLbxiG2ulG2VIlA+f5gSpOAAR1qamHhHWETpw2M5k1Nn5Mw6'
    'PrkiiRdNvNjZIY28gBA6nJXFWIkMLfvgY8f3q958e/Fjxf4wuZrjV9Qlk35GM7Rj0CrhQPYACvnvVJ2fLFsk0Rwr'
    'l8RpLHpP3EW5NY0u2/183T0BNU38X6HETtMkn+6n+JFcPeAuTmsgwnNdEcvpdWxPH1OiR6V/wnmnj/U20rH3IH+N'
    'NPjp2/1Vmo/3mJ/kK8/itvatKKAjk1f1GgvskSx1XudX/wAJVqMxyscSD6E/zNbvhrxdaaZr9jfeJ9NGt6VDKDea'
    'esrWzTxHgqk0Z3Iw6qemRzxXFwW5PPvTeGe4UYwE4+oprDUV9lGTxdZ/aP3K+H/wJ/Zh8c+FNN8a+EfDkOo6XqkX'
    'mQSXM9xJIjA7ZIpVMnyyRtlXX1Feqaf8Bvg7peDY+DtIQju9ssh/8f3V+a/7B3xs/wCET8bv8KtamC6L4vbzLJnO'
    'FttWjTC49BcoPLb/AGwpr9ieVJBGDnkVhOiouyRvGtKSvc5mw8IeFNMULYaJptsB08qzgXH5JXQJEIxtiAjA/uAJ'
    '/wCg4qYDv0p3AFKxTkVHV2+8Wb6kmoPJGeRWgRnpUDMBzjNLUSkQeXTCvpTy+ajJ64p2BsTBx1qEx84qTcT2p+M9'
    'aNBXKTRDtXzv471v+0L+4mVx9g0p2gtz/fu8YllB/wCmYOwe5NeyeNtZk0fShbWDAalqLfZbMddrsPmlP+zEuXP0'
    'r5V8d3MGn6Yum2zHybdBGpPLMBnLt6sxJZvc15WYVLtU0d2EhZObPBPFV80927I4KKOnvXByqOj84FbV9mZ2JHU1'
    'iTErkNxms6cbIJO7MR4lxnOMnIHHFUmLCUrnOR1rQuMcccVnHl8np7V0JGTZXlcvjYeN1RuFMmPwp4ALlum055pB'
    'jdubB5z+VUTcjdCMK3JHTnpTcgAMD1OKfMVP3R7monPUAZHoaB3K5IwxNMkcBh6Dt+FK4wCp6np+NQy/w5607BcZ'
    'KOMn/PNQyqAFGOfXpU0jA4xxk1DMcuq9qYmygeGGPTpRxt/GpCvf8qNuRg/l+NNAUTgHjnOT+bGm5Q8jk0KsmQSu'
    'AVzg+5NKBgnIxzQwWw1hgYbr1qInHH61M2F69+agPKmkU2MLkZI7cdKN3y4PpSEZ+v5004AzjnPSmIXoCT1pxBIG'
    'KjznHbPenAgEYHY0h3HowAwpzU8Tc89Kp5PU9Panxt8uSDyalopM04mB56Vekt9Ju7Nl1u0W+tUZZTbuSEd4zuTd'
    'jqu7qO/Ss2FsgEda0JedPuB0/dsf0qU2pJob1TGXvinUtRmD3UrbVAVUT5I0QcBUVcAKOwFQJejcQ38z/jXIrNwA'
    'TirkcmWyevtXo+zR5/MdSL9RkLkfiR/Wpl1ORRlXdfYOw/rXL7zj6nP5VIrhmwWwfap5EO5039s3mcieYD/ro3p9'
    'aj/te8JLGaU/VzWCXyNykjHWm7nCEZ79eh+lLkXYLs3JNRlcgyO7ZHTe3+NQBokXMaLuPOSAT+ZrH3nIG7J9KsBv'
    'U8Y607CNTzGkG4nJHA/HgipTKWhEg59f/wBVZgLeWccE+lRmU7nXkAncPfPX8jTsBLNISMLz3qg8nKhu+T8vPSiV'
    '29fwqqeMuTnoMUAMlk+U8Y3YFQbgDyadJhmjXPXJNQvtDc87R+dAyLdlmftnApiHaQR1PWjll9M5JH8hTcjk9hxU'
    'sB+SSWOBUPRcGpF+59eP8aeAGwvpSHsRFQqD19KI0B69OlSNksB6U0fKu3uKmxREy5Y+360TZ8vaP4iB+HenH9O9'
    'RO2ZFUc4H/1qaQAXwM1NGePWoGHP481ZjT071NhM0baCSZkhiGZJWVFH+05wP1r9J9Kso9I0qy0qMfLZ28UA/wC2'
    'aBSfxOTXwz8LtHGreN9ItnXMcUxuZP8AdgBk5/ECvu2SbnOOprKRrDzP/9b4KOpFvvn9aha/TBJNcNJpfi7HD255'
    '7K3+NVxo/iuQ/vJo1HshP8zXzioU1vNH0rqVHtBnZvqOe4A+tUpNVt4RuklAHuawI/C2rTf8fF5Jj0QBRWrbeCrZ'
    'TvmVpm9ZCWqn7CO8r+grVn9kaniETv5Wno07f3gPkH1P+FfXvwM+I2peGYF066Y/ZpXDuo4G496+cbHQFgUCNAo9'
    'hXpfhuxkixjI564rmq4qEdYI2hhZSVps/TnRvGcdzbJcWE0gYgEYP+JrqLX4hapERHP+9U9x978cV8e/DvU7iOQW'
    'rszrj1x/Wvoi1SWWIEKD9XP9K7KdZVIpnFOk6UrHt2n+MbW7GJSUI65NeGfGXRNH8cQy2OoYkjAGw55UjoVPYj2r'
    'TWKaFScog9gTXj3i/VLy0uXaNzt9K4swp3p6HZgatqlz5P8AFPw/8aeGJWOnajJc2nOzzh5hUdgT979a83nu/G8J'
    'IaG2m9wzIfyINfW0niA3i+XcrkdMda5HUvDNrekz2q7GPbjFePTx9SnpJXPUqYClU1Wh8r3Gq+OsnGnJj2l/+tWc'
    '1542l4NlGme7SH+i19Fz6Dc27EPESo9qalhGeHjGPcV2LNX/ACo5HlFPuz54i0jxZeH9/cw247hEZj/48a6Cw8Cw'
    'SMG1S4luz12ucJ/3yMCvbho1nJyAq/hirMWhwdUbFZ1M0qSVloa0stpQ1tc53QtNs9NMa2cewKRjaMV9CadqMlxb'
    'IG/hA5P/ANc15fBpLIwKnofrXpOjWrLHtKhvwrlhO7uzqnHTY6yzupomBR8Ht82K958Aarer4Y1qYyktHd2OM88M'
    'swNeEQW0wwyKo/A16z4OE0PhXXCxwTdWHA6dJq7MNb2iv5/kcWI+DQ9JtPFb5AmH1NdTa65ZzgEOMnseK8LM8o5P'
    'f3qwl68eMY/M16aSOGVz0XxnZwaxYsrEEhTtI5xXxB458NTafctqemoBcxjDr0WZO6n+YPY19WDVpJF2lh6d6838'
    'XaMb+J548k49f6Vy4mnK6qQ3RrSlFxdOpsz5p0HxNPp95DrOlu0U0L8r3BH3kcfoR3FfVOl3ukeOtDbUdKRUuUX/'
    'AEu0PVT0LIO6n07V8geJ9Hu9Gu31WwjJzxcwDpIo/iX/AGx29elW/Cfi690C/g1vRpjtODjsy91YfoQa9HB4rnR8'
    'zmOAdGVuj2Z9C2v2jRrxbK6dmtpSI4HdvlQ/wxSMeg7RuTx908Yx1BV4uCCCCQQeCCDyCOxHpT1m0bxroR1awRSk'
    'i7bq3OD5bN14/un9Kw9LupLOcaRqRLggJbXEhyXxwsMrH+MDiNz1HynnBr1YtPU8Vpp2NsTnGMCk85ScOKgnjCtj'
    'JH14/Me3pUIHvmrSIbL42MeKsKgGMjOaySWVsjOakS4ZcetFgujV6cKKQP7VRF0T7+9Hnse1S0PmsaRYVdstO06S'
    'OXVvEF/DpulWhHnTTypE0rnkQwCQjfI3two5Nc1Le2tnGbvUpxa2cXzTztkiKMcu5A54Hbv0r5p+NPxk+HnxQN54'
    'X0zQbS00nTbCaOxv7jP2uRtrETTSltqFmw+FA7A5qHKzszqwtD2l5PZHQfHj46NL5nh/RGFtYWkZQbD+7ijHuPvM'
    'R1Pc18Y6HY3PjPVV1CRWFtET5Qfq2Ty7e5/lXL6Bbav4otrDS5Qz2sCoHc5zM47n/ZHRRX2p8PvAKQxRKYtsagbj'
    'jGT6Ct+Xl0MatW7Nz4ceDEgaO5mjARcbRj9a+m7SJI4wq8YHSsPTdPitYVjQBQoA/KugjKjg1BENNWWctjimFjz/'
    'APqpN6AZ3VA0/XHenYtzQ6SVl/wFVHuW4xwR0I7U15A3eoGAx6mixDmz1jwp8S3tQmneIi0sA+VLgcunoH/vAevW'
    'vaYZLW7hS5tZFlikGVdDkEfWvjg8HnqK6Lw/4w1Hw1MRbN5lu5zJA/3D7j0PuK4q+EUlzQ3PYwWayhaFbVd+x9T7'
    'VA5qncrBNG0MyCRGGCrDII981gaF4p0rxJb+dYPiVB+8hb76H3Hce4rYZt1eTNNe60fT0pRmlOLuj5h+Kf7PGk+K'
    'pl17wrM+j6zb5aGeA7GVuuAR1U91bKmvm218Q674L1MeH/ifbiyJfyxqCoTYTHs0yfet3P8AfXKnvX6Utn/PFcd4'
    'r8HaD4wsXsdatkkDKQHKgsAfr1+hrinSsvdO2NW/x/eeeeBPi1rXhQwWUrf2po7KGjhMgd1jP8VrMMh1A/hz+Ar6'
    'w8N+MvD/AIwtDd6HciQr/rIX+WaI/wC2menuMj3r8t/Ffwr8c/Ceaa88GFtS0J3Mj6bKzFFHXdbt96Fx2wcZre+H'
    'HxMt9TvDcafeXGn6nZj97G42XkBzz50Y4lj/ANtB9RXZhcxnT916r8UcWLyyM1zx0P1KIJ60h/GvEvCXxitbuOK2'
    '8VqkDOAI7+D5raTtl8Z2H1I49QK9pWWKaNJoWWSOQBldCGVgehBHBFfQ0a8KqvFnz9WjOm7SQuTSZppJzUTSqDtz'
    'zWxkWPM7dKaWqt5o7ZP4UBzxhT+lAizu49Kbn1qLLHg8Uwg98D9aALGR9aXJqDBP3Tn6CkkljtkL3DrEB1aQhB+b'
    'ECk/Mdhl5p9jqCIl/bxXCxOJEEqBwrr0Zcg4I7GvH/E/wetfFPxCh8Xazqr3WjR6ZJp50GWFDAskh3faoplxIku4'
    'A7ge2BXaap8RPA2jq39o+INPiK9VEyyN/wB8x7jXmmqftG/DGwLLDdXOoMOgt4CFP/ApCP5VzVatFfHJG1OnV+ym'
    'fPnxHs/EnhTxzY/DrwHNLqGoanZy3sa3MYd7S0ib948Jl/czOQSF+XcpGWHStPwroehaNeTT+FNR1Xw14qC75DfX'
    'cjw3coALR3dtLiJo3IxkBSv8PSui1r9pXSriVbnR/DEdxPCCIpr2RWdA3Xb5YyM98Gvmr40/tE6/ceGp9Q1HR9Lt'
    'mg+S2nEMzTJIwIQCTdnGfXivKlOnGX7mV32/4J6MYTlH95Gy7n6P/DvxTqPjbSLy/wBR0K60C7sLx7OW2uHSZZCq'
    'K4mhkjyrRsG45yCMV1d3rOm6aD/aF3b2oHUzzRx/+hsDX5DeHvj9eXfhazR/FM1tBcQrI9rbySkK7Ab1IjHGD2zX'
    'Aa98SfCoZpnurm6kzkllC5P1lbP6V0rHz+FU3cxeChu5qx+vWuePPhk8bQap4g0llP3lMyy5/BA1fNfjLVvgfBDP'
    'JomvCzlkyzJawzSQSEdN0bKFP1GDX5xT/Gjw/ag+Tbsx/wBuYE/lGp/nXG618Z5LqMpZae5B4yscjfqxA/Ssa3ta'
    'y5ZUlbzNqMadJ3jUZ9l+GfitYxa1Lb+FtWfTr2Ek7X3LBKoOMlTkY9Qw4z1r7G8BfHGK9lTSPGsH2K8cfuLiMD7P'
    'OccANnCsTwOcH2r8OvC/ijUv+EuttRhi+zzZIH2siKFgw2sjEKeo9T+NfXWmeJPEOiqybI5LOT5jbOWkh564zyv1'
    'UivKqOpgZrklo+nQ9eEKeNg+eOvfqfc1v+0vLq+q6ho1ho0dlc2UjKFu5iXKqcZIXHPqB+dc3rP7QGtwFvtGuabp'
    'ag8hPL3D8XJNfDHi3QbbxtfNq2m382n3suN0MsnyMcYwkwx6dHwfc1xUfwV1iSX/AE8yOxOfmJOfx71azC6vUqWI'
    'WWJO0IH2vf8A7ROgybhqvj6U9crBI38owBXBal+0T8KoGLTajqOpt/uSPn/vphXhVn8B5GwfLNdBD8CWTlo/0/8A'
    'rVi8wod2zVZZV8kdJfftO/D0IV03wxe3b9mlZIQfyLGuNm/ac8Tlwvh/wnY265JBleSQ+2cbRmurs/gbECC0XT2r'
    'tbH4Q6ZZgNcKkYHUuQo/M4rOWZUFtE0jlk+sjwLVPjd8bteXylWwtY85Cx2aOR9DJuNcvJd/F/W2b7drN6Eb+CJj'
    'En/fMYAr69/sf4c6OMX+q2ERH8Pmqzfkm41Xl8Y/CvTwRBLPekdra2Yg/wDAn2il/aVR/BT/AAK+oUl8cj5FT4be'
    'JL8+beSXE5bqZHZj+ua6LTvg1eTOPMhP4g19Cz/FXQoRjSvDtzLjo1xKkY/JVJrn7n4teK5DjT9G062B6GTzZSP/'
    'AB5RSeKxUvL5lexw0P8AhjE0n4GxHDSRqD713dj8FLePDeXux6A1wlz8Q/iJLnzNWhsUP/PvDHHj6E5P61yOoeJ5'
    '7ok634hubn1V7hyPyUgVn7KtJ6z/ADK9tSjtE+qNJ0bQ/CqbLq8tbRe/mzxoePYtn9K1n+IfgPT2G3WYpXHQWyyS'
    'n81XH618ONr/AIMhfORM+ep5OfxJP6VIvji3Q7dN0+WTHQhGP9BVxwEm7u7/AAM5Y5LTRfiff2m/tDSWpjsdFjvd'
    'SaR1jjjuEVELMcKAztuGSa+qYLvXNT8IJJ4hsksL/MiywRyeaqjPyncO5HUdq/I3wZqera5rECXkM2nRJIjrIsQz'
    'lSCMbiccjrX6weD9fHieyuoGGGWJZRk5Y87WJH1INenQpzVNxk/xueXiZwc04r8DwrxIMSEgYKnB615zc5LsFPBF'
    'ey+LbCOCRwDn5uR+deRX0YSQ4HStI/DqcM7cxisehzxjJNZjrmTaeh4/A8GtXaBuBPHP+NZsqjcre+KtIlmNbEmz'
    '2PkkKFb/AHlO0/qtVnGHH1q0gCy3UXfzS4HbEgD/AMyapT8s209cfhTsK+hmTn91lhyD/WqFyvAx+P0rRmbduRv/'
    'ANeaoMCYye+OMfhVEXMedMLz2NZzjnjritef5lOP881kzDbgVaRMtzOmBCZ78g1TcButWpjlXBPTkfjVBm4zjFXY'
    'm+hnyfdKnoBmqbLuYZ//AFfWr7D5vUHOB9aqlcZB7UElEgqPoSKjHX64/WrLgEOfU5x6VSyQ+PUf1qgL9pczWc63'
    'Vsds0ZGMcBgOx/oe1XNZ0m31CNtf0mPCyDdeRrwUkJw0gA6An7w7HnoayFI3Fs/hWppuo3Gm3IuoBuQ/62MjKuuM'
    'HK9+OCO4pKTi+ZCqQU48rOWjsY7Z1lt1AYHJz3B6iqkEl7d3N3pNtLGhgkDqkrlf9aOMdsHpz3xXf6xpcEMa6vpQ'
    '36fNglQc+Q5/gP8Asn+A/geRXkhnU+K767H+oggVJsfxDbyv1/rXoUpc6umePUi6crMk1fRPFFm7C8sJ19CFLKR6'
    'grkYrg7/AO0oSJYpE/3kYf0r3XQPGuoaIBZXU8rWDc20sib1KHnDA8qa7S41u11S38wRQSBv4lUEGrdRx3RUZI+M'
    '5Srng80xIM9K+jtW0PSr4l5bWLJ9FAP5ivPtR8HW0eXsmaP/AGc5FaqrFopVDz6O3xxV6OEY+arUtjdWhIlXcB3A'
    'pUZGUjPNNu4rseAsEDydlBPNYMZK2k9w+RkYq7q87LbrBHy0rAY9hTJbfNtFaFgoBBc04qy16hdi2j3NilheW8r2'
    '9xG5eKWM7XjdCHjkU9irYI+lf0A/s4fGWD40/DCw8S3DKNassWGtQr/DexKMygf3J1xIv1I7V+Bd7LbXi2xtjlY/'
    'kJHTI4r6e/ZQ+MDfB/4nxRalKI/Dnicw2GqbvuwuWIt7r0Hlu2GP9xj6VNSN0b0pWZ+5/m98daYZDURIU7Wbp6dC'
    'Pb60xpFHQ81yXR1WuT7ye9QSN3NQtcY4NRmbNJsuzMzW9e07w9plzrOrSiC0tEMkrnrgdAB3JPAHc15bp3xUl8WA'
    '/wDCNJHAB2uATKPqnQfrXK/tOXpg8A2duhIW61aBJAOMrGjPg/jXhngHXYwUjuOq42ODh1+jDkVwYurOOkDfDwi3'
    '759ew6v42tHEtzbwXkR6qqmM49iv9RXS23i/TWidtQjmsmjRnk8xcoqqMk7xwPxxXBaP45TyNqTecYxg70Dkntkq'
    'V/WnX93d6tbrca/MksMJ81bOJQkBZeVMvUvt6gE49q5I42cVqzqeEhLZGLqN9d6jLceJr5WhaeIxWED8GG1PJdh2'
    'eU4J9FwO9fLXjjVvtdw6gjaM55JHB7dq+g/HGsN5BK/NkHuPSvkTWblprp+c4O32Fc9N882zWouWNkYE5zg9j3rn'
    '7tiEJGeDx+NbUp45OPTFY9ypwCe5xjt65rticTMVycrjPP1qoc5JOTz/ACrSlVeMCs5yccZJB4raJmyDJWNyO54p'
    'o6gNyCO1DH90B3Ld6UfeUAcc0yXqV5eWxg89MVXPfk9atOymTryDj9KpSDjjkZoGmMILyADHFQz8ls4yo4o34l3L'
    '1x0qvIxJYk8dDiixREG9vekLFmY54FAAHsc9vSk4wemapCA/cJ/EVEcnABI5zke1PZxxg9OKikfCN6jcf0osJsrx'
    'q3kpITkMqnn3qFiRznNTDiGNB2Vf0FQkcZIxnjHFDKSImOajBO33zT2GBnjPao2PqfwFIYnHOajYkAADFJ8pU46C'
    'n7R/F6AimIb1H0pwPTPYfzprDjPemk5Y5wMKKBkw6UY6Z6A1Cp5A9KmyCM0mUi0hwQMcGtu2AeGRT0KNnPTGKw4x'
    '0NW7mf7Np1xL0xGwH48Vna7Vir2u2cDG59T7e9aMbMrbiev+FZETBRng+3eryTHYCQPzr1mjy0zS3qM49akWXLc+'
    '1Z6zAk9T7U5JvX9KmxXmaQIbcox+P9KkIbnqcHiqAf8AiHOO1XYzu35ByKljHhCR9R+Rp4yF2+nbr+tMDZVRmnqC'
    'GJyeRzSE2TKWOFz/APXqOT5CD3Ixn3B5/Qg07dnIGOKrSvhPk6qQw479Py9aVhiNuIOKglO1Vx39fSpEbzEDZ68k'
    'f0qKRxggjOPX0pgVGbMjH0AX9KpsWZgW/ibHH61OQQGcfxfzNQYAbj+Ggd+hKzY+734/CoscepP9KTcAc5wRyc+9'
    'Ix2hVHpn8TUgh7HoPT+tKvUt6cD+tQu2ScfjQW2jAPWpLuSqdz7qTOQee9Rg4GakAG3B6UgI++fSo1XdIzehxj6V'
    'KSFB496ji+4PXr+fNOxLYDJOatxHPXnmqobk/XFWYAMjNSwWp9L/AAB04PqWqa1KMC2hS2jP+3Mdzf8Ajq/rX028'
    'qkjmvIvhDpA0/wAEW87YWTUJHuWz/dPyJ+i5/GvQpUfj5hWXU0u0j//X+VW0uFl+7j8KQaHEQMKK7B9MkXsfxNMW'
    'zK8H+tfnXtfM/RFSOZXQE77anXw+MAqwP4V1CwMB1qdI5AMK1L2su4ezOXi0YpwW/St2ytRBgBjz7VqR28snJH51'
    'q22nkkcik6rYezS1R1XhKRobmN8ke9fUejuJrdG8xVOP4sV82aHbGOVBkdewr6A0JX8hQqk9O4X+Yr1cBUsjysdT'
    'vqdZMR5ZKupOOwNeK+Lbbzmcgk/hivcWtHMf7xgpYfKNxb88cV5v4g0tW3fMM+gBrqxXvRObC2Uj57nthFITuqe2'
    'liUgMN2PxrpNQ0wI5wo/CsJrZ42PGB+FfP1InvU5GzH9muE2kZB9aoXWg2kxyi4PqOKbEZV6HgVpW8kzvjdXG6ck'
    '7o6FNPQ4y58OyoTsYfSsz+zryJscn6A160luXHz4H40/+y1k5XH1zVKb6hZHm1os8bfOCB713mlXSxKCSRWmmlxj'
    'g8/hV+HSoCPuZx6CtYMzki1FfybQVZ2H516j4NeSfwrrrMDuF3p+AfQiavN4dNtm4Xr6civV/BtokfhnWo0HW5sc'
    '8+glr0MM/fXz/I4cSvc27fmUTFu+8o+uaVbMMeB+tawtMnIAqzHa468V6MW+5wSSMyKy24OAKkezDqVY8Hr0rcS1'
    'iPLECpRbQjoQa0TZmzwXxl4NWVGuIACOcivlLxFo9x4WvXvYAWspTmeJRnYx/wCWij/0Id6/SC5s4Z4zGQCCMV8/'
    'eO/BfEsmwNE4Nc1S9KSqQ+Zo4RrwdKoeI+BvHV14W1CK8s3E1rLxLHnKSI3XIr6T1KPTtd0xdX0xg9ncDDp1MbHq'
    're3oa+HL6wn8I6iYpATpkz/Kf+eDk/8AoJP5GvYPAvjabw5d+TMTLYz4WWI8jB7j3r2cNiYyipI+Px2DlRm4SPc9'
    'LuzIBo+oSF7jpa3Eh/147Qux/wCWo/gY/fHH3hzMxeNirdRVXVrG1ubVbu2YT2N2oaN1P44JHRlP4g81LpV4upJ/'
    'Z2oShNQjVnhkb7t4iDJ57ThRkj+McjnivRT0ujy2r+71JC7/AMLGmb3PfpVcSCRfMQgqejdj9PWkMjjgZOfQVVjM'
    'uKzgcGpRLjvVINIRwG+pGKhmu7SIf6Rcww4/vyov8zSYI2E1CWzYXECRSyx/MiTIJIywHAdDkEZ6g1+bl/8ACfxL'
    'rPiW9uPEDMVluZZPKjG2EbnLcKOMc8V943HjDwfYn/TNb0+PHUG4Qn8gTXJy/E74X27mR9WhncHpDG8p/wDHVpN2'
    '2NI8+yOR+H3wshsEjkuo9kaYIGME4r6JtLWC0QRwoEUcDFeRn40eDh8thbapd46eTZPg/QsRUX/C3WmP+g+G9Uk9'
    'DL5UI/Viah1IR3kaRwtaXwwf3HuYn5+UVaSUlcGvAP8AhZHi6X/jz8Nwx+9xef0RarSeOvidISIbfR7T0z5sxH54'
    'FYvF0VvI6oZbiX9g+jeMVGUZvug180SeIPilc/63xBDbD0trOMY/F8mqU8Xi2+/5CPivVnHcRMkI/wDHFqHmFFdT'
    'aOT4h7pL5n01IDGCXUr9eB+tZFxrmkWY/wBMv7WAD/nrPGn82r5nm8MaRKN2qX97depuL2TH5bgKx5tD+G9ll5RY'
    'bu5kk8w/qTUf2lF/DFs1/sWa1lUSPpK5+IvgC2B8/X7DPok6ufyTNc1efFnwSrFbSe6vD2+y2c0oP0OAK8DbxH8P'
    'NKGYpLdcf88YR/gKoTfGjwhpwxEZXweAAi/zNP61Wfw0vvK/s3Dx+Ot9x9CaT8TdTudYtoPCGg61PqE0gSD5Etd7'
    'HoMu3T619zeDdQ8S33hy0uPGNpDp+sNv861hkEoQBiEy44LFcFscZr8i4f2h7KC4jl0a2lW5Rg0UgLMUYHhgEHX8'
    'a/Q34YfETVfGfhiHWdbt3sppHIiMhAeWLA2ysq/dLHPFc2I9pON6iSf4npZeqNKbjSba/A+j1aJziR9v4ZqJhHk4'
    'YkfSuc0/WIp8RTMFfsT3rcJ4ODXmu63PcTXQjmSCVGilXejDBDAEEe4r5x+JfwD0TxNnWPDjNperxZaK4tz5UgP+'
    'y45x7HIr6JO7nn8qi2HHJNRKCkaQm47H5y23jjxp8M9U/sLx/bPFGTtGoiIm0nHQfaoh9xj/AM9U/GvqX4ffFO6t'
    'PL/sK4VoZQH/ALOnk3wyA8lrWQHBB9V5HcV6f4l8JaF4rsXsNbtknRgQGIG5c+hr4t8a/Bjxd8NPO1XwI39paOX8'
    '2TTpC37vnO6IjmNh6rx7VMak6bTuFSlCqmj9JtG+I/hbVLM3FzexabIn+tivHWIofZmwrD0Ip138Svh3Zgtc+JdL'
    'XHpcox/Jc1+OXin9pGxfSv7B1GCeS5VlL/aomSeMoful0ysn+9gE15bL8YLi7wNL0p3Pr5Lt/wChEV68MfWa0h8z'
    'x55fTTacj9tL74/fCaxJB11LgjtbwySZ+hwB+tcNqH7VPgW33Lp2nanfEdDsSFT/AN9FjX47N4w+J+ot/wASzSZl'
    'B4HypH/QmlGh/G3WG5VbdW/56zO36KBUTx9brKKKjgKfSMmfqLq37X1zGGGmeHreEdmvbonH1C7RXl+rftf+NZc+'
    'VfaNp49IYhIw/Fixr4ftfgp8S9Twb/Vo4QeojjJI/Fs11tj+y9f3gB1DVL64z1VWKD8lFc08a38Vb7johgEtqf3n'
    'tOq/tQeJLsN9u8Y3ajutufJX9NteS658fdLutzXeqXWouP8Antcl8/hlq6zSv2RdKJV5LCe4PrKXOfzNeq6R+y3Y'
    'WqqIdKt4vd8Z/rXPKvCW/NI3jhmv5UfHF38b5pONH0mSZs9Vilf9eBWPN4/+K+rn/iWaPPEp6fu1T9SCa/Rqy/Z4'
    'jgADG2hX/ZUn+ldjY/BHS4CPPuicdkQD+dCq2+Cj97KdGP2qn3I/LKOz+OmpsPMka2RuzTSH9FwK6Oy+EnjrWoim'
    't6uAH5MYUkNjnB3E5Ffqta/CbwnGwMySy49WwP0rXf4b+EiirFZKu3uCc1p7bEW91JeiM/Z0F8TbPyyf4A3GoSif'
    'UruXcAF2W37qMAf7CcV1ui/s9eHosCa0kuW9WBYmv0s0bwXoWh+aLaAN533t/wA3TsM1tDTrKPAihRMeigVNsTJe'
    '/U+4L4eL9ymfnvb/AAEsAB9h0U/Ux4H6it+D4AXlygjbToYR2LBQR+VfdogUcAAUCBcgn+VSsO93NlfWLbRSPg3U'
    '/wBnFbSHN5bpIjDlo13AfWvMdW+Hfizwl+90C4+1WY/5d5wZIsegP3k+or9Q2QFdpUEdwa5ufw1pU8pm8hAzAggD'
    'g59R0qKmGl9l39Tanil1X3H5dWuuW0dz9m1e2bSbhjjbP81vIf8AZl6fg2DXr2h6vqOkeW0Lo8LYIgn+eBx/sP8A'
    'w/ga+m/FPwQ0DXopGtoo0d87onGUbP8AKvmjXfhF4r8JNJF4cuPKQEn7Fdgy2z/7pPK59jXn18PJdLfkdtLEp9f8'
    'w13466jpOoXGmaP4atWNu2wy3EzsCcA5CqBxXF33xq+I1/xENN04H/njbhmH/ApCf5V5f4j8LfFW71Cec2dtZiRs'
    'koWdRxj5fasq0+Fnj29ObzVTEp7RIAfzNb08NRUVdx/Myniarbsmd7deM/G99k6h4mu0U9VgdYR/44BXL3msaTy+'
    'ras879zPcNIT/wB9NV21+BLSkHUr67uT3DSkD8hXYad8EfDtuATaq5Hd/mP65rX9ytpfcrGTdR/Z+9nk58a+E7Ns'
    'Wo89vSNC3/oINSjx5eTnbpejXUvoxiKj/wAer6P0/wCF+j24XyrWNfoortrDwDEMCG1yfZf/AK1PnpX0i36snlqd'
    'ZW9D5AW/+I+oH/RNMS3U9DIT/JRViPwp8S9RI+1XiwK3aOMnH4k1922Hw5vpAAtoVHuMV1lt8LLp8GQxxj8zWkXP'
    '7FNL5f5mUml8c7nwLZfB7V7wA6lql1JnqqttH6V0lp8CdGADzxtO3rIzN/Ovvmz+FdopBmmJPfaK6i1+HmhQgb1L'
    '49TW8aeIfWxzzq0Vsj4T0z4S6PZ7fKtIxj0Uf4V6dpPw8tyFCWgb6JX13B4U0SAfJbJ+IzW5bafawYEUarj0ArWO'
    'Eb1kzF4pL4UfNGl/C+R5FlSzK455XFfQXw90G/0bV0aRNsUkMkLDP95fl/8AHgK6yLjjpitC2k8qaOXP3WBz+Ndk'
    'MPGK0OWdeT3PGvG8ZW6k7Yb+deL36/vORx0zX0R8Q7L95Mw+tfO+okgsRziuOEdGipvW5z7r87DOOayLhT1zyD0F'
    'bErgtkd8dayLgAFsdu1amHUy7hlW+2qR+9gB98xsR/JhWdMw53AgGrGoEo9jMM8SOh+jof6gVSkfIIbJ/rRYZScg'
    'MTyQORVBwUBUHcQSPwq/M+OfzzzWdMfmO3rjPHt1ppBcoykFDx0/xrHm56jrWnMCGOeM5x9azJRgfj/SrREnqZko'
    'yxGOcVQcd8c9K0JVIPHPP41Sc4yPSrRmzOk4wfQ9agkOCx/EVbl288H1FUJGXhjnGMUAVySQwPQggfhVNzgK3UDg'
    'mroxuqFlUqV6Y5phcrx/eIPA7Vdt3wODkiqXAbHX3qRXIPFDQJm5YarNpcjvAnnW0oKz25G5WU9fl757j8RzWZrX'
    'guF9G1DWvBsct4kw3z2iZkuIP7xUD5pIx2IGV7jvTUmKgEcDpmtWwv7rTrkXthcNbzj5sqflYj1A/mOacJuD5oiq'
    '0o1FaR5YurxxXCaZcDzEuLEsqngpNFuKn1BwCK6DSLxWtVvIyFaI7LlF+647SAeuOffmvWXu/BHia/t7rx7oxN1F'
    '01CybyJhnjl0G1xz0dfxr0Dw98KPglcStJaeJdUgieIL5cohOccD5sc8cV0PGU2tdDj+oTT93U8PYhlyvNYl2mGI'
    'wea+ydP+EPwdhjCv4hvLkRqAd00cZIA4PA9K04vA/wCz5ac3CvduP+etzI+fwXArH65TW1y1gKnWx+f93BGwO/H4'
    '1wGq28UTGWB0V17Bhhh/jX6a3I/Z+0hS0OgW0jqeN0Rkz+LvXLX/AI8+EMYaO28L6aQByXt4R/IE045gk9ItmiwE'
    'rayR+aX2+1jJ1K5YFY/kjUEEs/fH0qtHbXersbiWXZETwi5H86+w/GOj/BXxSuY/DyaVckkpc6YzREMf4mjIKMD6'
    'EV82eKdHvfDEieW4u7OQ7YrhBtAPXZIn8D+3Q9jXpYfGU6miVn5nLWw84a7oz1gSFY44wAE6AVKyCbfA3O9D+fXH'
    '5VSt5ZXQPN1PQegrQ3BXR+64/SrkZKR+zP7HvxjHxO+F0OhaxdGfxH4TVLK8MhzJPaci0uDnk/IPLc/3l5619Z7s'
    'jivwF+CHxRu/gx8TbHxfAHexBa11O3X/AJb2ExHmrjuycSJ/tL71+8ljqVtqdjbappkyz2d7BHc20y9JIZlDxsPq'
    'pBrlqx5Xc7qUuZGkQxORSc98VSMkmfmNRvdR26NPcMEiiVpJD2CICzk/RQTWV7m1j45/at+I+gQX2i/C+CQT6yxO'
    'sTohBFvAi7IhJ6NLklR/dGa+edG1eaMqyNt4xXy7H4yvfiL8btc+IN/IW/tq8vTApOdtuCVgQeyxqoAr33TJgmAf'
    'zrLG0OWSXkZ4etzXfme2aFr9zaT43syvwRnn619AaX4iivtJiZmAfBR+fTj9RXyVZ3WCCP0/pXdaZrM1k3yn5GAy'
    'OxrxqlLU9WlW0Ow8Qat5uleTM2Xi3xuwOc7DgfmMV4TeMGdugzya7XWb7zppgCdsp3jnqQMNgfTFefXR+b5uDzir'
    'owsTVncy5ySxXHHGDVG5J2YI+pHNXnZfvE5AHSqFw+FyOoA4rqiczZnyDGc9MVmsv3umMVammOePx96zWkDbsdhV'
    'pEMSQ/KMY7nn61Gz7Wznt0pkkgB/AD25qBmwCCM46e1WkSQO5AYkZHb61G7k7VB6U12bjPKk8flSblMg7DHIoGRD'
    'BOSCKZhSpbkcnFSE4QvnGTUJOEwepoG2hrgDaCe3p71WJyMdsnrViQ7io67f8aqSHpwMj+tMaQZYMMY//UKhdsxS'
    '5IBCN+oqQtxnuAaqSoXt3LD72F/NgDTESSNtxznpn8qrl1JB749KSVx26VGDu79RzxSaLuKwJBI9uaiYZdfbilLg'
    'L14qIsuR2z39aAEJwMDjBpSecZphODj3pSdxKntj2pkiuxz1+lJn/wCvTXb8BnikyAe/ekMcuc+9TrwAOlVyR+Pp'
    'UgYbgKGDNKL168VV8TSiLSMZ5kdV/XJ/lU0HzH2FYHjS4At7O3Hd2Y/8BGB/OnSjeokFV2gzmFmB54qysh24B/Os'
    'NJfmGKvxyZGelekeeaquQc8mlVxnGaqB+nOc9alB5z2NSxo00kIHUjI4rShlJ4POR2rETs2fbFXopApA/wAipKNL'
    'JPyjt68f5+lPViMfrWfvXknvU6yHCntQIujkkA5/CoHBaMg8DpQkm07j+dOYoVweallFaNiBkjAIz+I70x2JBPqe'
    'BTC23IH8JyPx5pCflH4nk0WERPyQOnFVGHBPYnrVhjxnrnpVaTIXnvSYyDdubOep/SpAQXJI71CflH0pA2BuzSYy'
    'RDnPOc0uckAE/lTFOxR79aRG7npU2GObrxzzUpbAA6ZqEkZFIW+YH0pNBcfKxKbfUgfnRyB+HaoS26QD0Gf6VLmj'
    'bQTYikkDtWhawzXUsVvAC0kzrGgHcsQB/Os8DjjvXrnwf0NdY8YQTTDMOmobuT03L8sYP1cg/hSZUdD7BsbWPS7C'
    '202EgJawxwj/AIAoWpWKnHIrMuLaIkncR9DWZJAoGFkb86jlBTvof//Q87lty3rVJ7MHkqTXUEAcAiq7hTwxr8sT'
    'P0w50WPquKnFj1wcewrZCRA8LmrkeOgT9KbkwRgpZ45+Y/nWra2zFgArVpKpP8Bz9auRRNkYX9apO7JkbejWjb1P'
    'Iwa9m0cyRRr8u49+ory3SgY2GABmvTtMlUxr3b3bHH617OEZ5eKudaZGMeSh+hbFcpqsAfO4jntnNdKsu5MKoBH4'
    '1zuoNOxzxgewFdtTY4qa94831LTQSfn/AErk57EKTjJxXo96XGR8pz2IFczcqM9h+FePVjZnqU3ocW0LDIwfz/wq'
    'dIpsZyfwBrbJjBJxk05WUjAUZ9TXM0dCZStzOuMA/wAq2IZp8YNRBSACSDnsOtSqMHgdffNRymidjQilYthwPz5r'
    'fsoQ43HgfrWNbAk4/Pit63BXopNVFEyZtR20RTtXe+F4FXQdXVe89mfy8yvO0+0Y4Xj3NegeGTMdG1ROBmS2bA54'
    'XfXXhv4mvn+Ry4n4Pu/M0UhAqQRjI/rVHzH6FsU9ZnA5kNegpJHA0y8IueT+lToqr1cj8hWYJHY8ktU6P6itFIlx'
    'LrFOzZ/GsjUbO3vrd4ZRuBFaiSLjlRileRSOlVZMnVHyf468CRlZYpY98UmeozkGvnFbKbw7eDS79ibZzi2mbt6R'
    'sf5H8K/RzWdNh1K0eF1BJHFfKXj3wP8Aa45bWZflOcH0PYg1zKTw8+ZbDr4eGLpOE9+5h6J8V7XwJpx0fUrNtW/t'
    'JjFY2avsY3GMht5ztUDlj6VyOq+KPidfZkt5dO04BxJEIoGleJlOVKyMw+ZT0OK+e/H8viPwdr+havcoZ10x5UDu'
    'rGORHGBuK5w+OP1qW6+PV1JbtHaaajOQQColf/2WvbU6s4xlQasz5ung6NJyhiU+ZHvl74/+J3ixLcSa5Fp3kx+W'
    'FtrONQ7KfnkyxPLHkjoKrJpfjK9OdQ8X6m4PaIpEP/HRXz3oXxL1+V4bGW2a3jlJAJgIWJmJO7e3WtBvE3xVupmS'
    'whl2BiAxMaKQO/AJxWc3XTtKol8zpp0sM0nGi2/Q9yk8DR3GTfarq13nqJL2XB/BSKrp8P8AwhCd9xbCQjvPK0n/'
    'AKG1eKf2b8YNVP727EKn/po7fyxUqfC3xxf/APH9qx+brhSf/Qia55VI/bxH3XZ2Qoz/AOXeG/JHuS2HgLSxkjTo'
    'SPXys/1NNbxh4EsTt+22y47RLn/0EV5BB8DLiQ5vdRuJB/snb/IV0Np8B9AQD7R58x775XP9awlWwq+Kcn8jaNDG'
    'PaEV8zspfi14Asgc3LNj0TH/AKERWDc/tAeDoSVtoJJcdPnXn8ADWnafBXwtDjbp8bEf3hu/nXXWHwv0qHC2+nRj'
    '/djH+FZPGYNbQb9WaxwGMfxVEvRHk8nx8Wf5dO0aaQnoQJG/9lFZtx8WPHl6MabockY/vGMD/wBCNfTNl8M5Xx5F'
    'g3thMV1Vp8KdYkwEsSM+oxS+vw+xRX4sayyVv3ld/gj4tPij4x6idsduYFPq4X/0FaryaH8W9Vz9ovxCD23yN/UV'
    '9/Wnwa1dyC6JH9TXSW3wUlxm4uET6DNV/aGI+zTS+Qf2XhvtTb+Z+bCfCnxrdnN3rTjPUIn/AMUTWxafBGdgPtup'
    'XUvrhto/Sv0utvgzpSY+03LN7BQK3bf4V+FIceZG8hHctj+VJ4zGS05rFxwGCj9i5+cFj8FPD6EG5jacj/no7N/W'
    'uzsPhL4ajx5WmQkj/pmCf5V+gkPgbwrbfcskPu3NakWh6NbjENpGv0UVjL6xL4qn4nRGOHj8NP8AA+F7L4aWyun2'
    'PTsY/ux4/pX0R4L8M6zp2mmFrd1UnKqew+le3x21qmNsSjHsK3ojGsYwuKqjScZczkKrUUlyqNjzqystVQYlUhR0'
    'z1rtdK1G6hAhuwWToD3FXpHHYVSkO7tXTLUxjodQEEy74sEGqcqypw3H4VjWl89q/XKdxXQNcw3MYaPn+dc7ujZF'
    'AliD8x/KoSN/ytlh6GrTkZ6VEcc8UNIE2eP+Lfgn4J8USvffY4ra8bkyLGCrH3XH8q4Wy+AUUD4zbogPBWPnH0r6'
    'XAPtUqg1lKjGTuzVVJJaHjmn/B7RbZR58hfHXaoUV1Vt8OfDFtz5Bcj+8a7rb6U7acdatUKf8pDqzfUwIfDWhWvM'
    'VnEMdyM/zrUit7SHiKJFH+yoFTt74NHy961UUtkYyk+rJFYYxjinZ4zUasoz3oMgParSIchSwPamdaC3otIGc8AC'
    'rSM3IU8D0pN5xgGgsfQU0kAc1ViWxcnuc0mKTePWjOarlJbELKOBTC5J4FKT/nNM3EHHH507E3JCzDqKbzTdxz1z'
    'TxmnYOYUbhyvFVr+xtdRhMF1GsikdxyPoatc96QEVMoX0Y1UadzyLVvA/wBnZntVEsZ7Eciuc/4QmS5OEtdhPtiv'
    'oP5SCDQqqPugAVyPBQb0OxYuSR4bbfDK4kI80hQex5rp7T4a6dDgztu9gMV6eFzTtozW0MJTXQxniZvqcnaeEtGt'
    'fuwKT6nmt+HT7WEYijVfoKu4GRT1POa6Y04rZHNObl1IPIXsKkWNQelT4zQQRxWqiZNsQBRSkDrTgDSbfbFWkQ2S'
    'Ajj2p4IPOTUYX8qfiqSJJ1I6g1OH9KqhanXPTitEyTK8aQi4sRcf3o+ffj/GvljVAodlHPJr611xPO0R1HJQsPwP'
    'I/rXyfrETC5kUjHJrga5ZtFT1imcdcZQDuM8/nWdK3zZ9a17hQAR9R9c+lYswxzjGKohsytVJ/s9mUH9yyvj/dYE'
    '/pmsm4fb8ueDW5N+9ikgPO9SMfUY/rXOh/NtIpjyWRSfrjmgTK8rZ65G4CoHjA2nPtUzfNHu9DUL4KBs4wc1VhXM'
    '254cA884z9ayJskkNx9K1rvnnoB+NY8zYfb70xFaRSSRjBAzWZMPlyOPp1rTds7WHORg+1Z849OeRVolmc+d5/2u'
    'g+lUnPGD0BP61dmJ35B5ziqj4O5fxp9CCsVxznrVeZ/m+ox+NSyNtwe4OMVSnfKgjscHPamkDGbzjHcU55OM57VT'
    'LYbae/p3pWccA8E8Dv8AjTaBMnWTAAPb+VTeYWVtrc4xjvyev6VUCEDANQqxy0n944H0Xgf1pWL5jZS+lTp6EGnr'
    'qMalSFKn1Qlf5VilyXznt0pm/ccip5Suc6JtRLnBlm/77PpTf7QUFTukbHIy7f41hF88etLuo5Q5zXk1PeCu0E+4'
    'z/Oq4uXIboAewGKoLgDk4p24kHFJxQ1Jll5mxnOKju1g1S1kstQQOk67C2Pm/wBkk98HkHqKj3Dj3603Ixj/ACKa'
    '02E9jx82zQzPbyja0TFGHupxTyoyw64q74mzD4iuJMYWZUlH1ZRn9az0JAyevU17N7xTPGekmhl2cSK/Xco/McV+'
    'pH7EfxjbXvDlx8J9cn3X2hxm50lnPzS2BP7yAepgY5A/uMPSvy3uhugRv7rEZ9jW14K8Y6v8P/FuleMNBcre6Tcp'
    'cIM4WRRxJC3+zIhKH6+1TKPNGxdKpytM/od84N1NcB8WL64tfhX4yuNPBN1H4f1MxY67vszjj8Cat+B/GehfELwl'
    'pnjPw7IGsdUhEqr1aKQcSQv6PG2VIrZ1HTrfVbG60y6/4972GW2lB6bJ0Mbfo1ci913O9yutD+eD4Y6h9l1XT7eY'
    'bTBPEo90mTCn9a+tLSVgxVvX+VfH3iTR73wJ4tvtDvA0F74fvZbCYMMHFtKfJf6FQOfTFfVVndrOFuFPyyqsikej'
    'DcP51vmML8su5xYOTV4s9M0643IF9K7C3uFki9CBXmenXB457dK6y1nBG09K8OcD04VLFq+nkNwjg8DA/Dof51i3'
    'shBJPQCr96+Fz7EZ+ox/PFYV3MJFDg8EBv0pxiXz3KMkuEYkkEnpWVPcHcAMY6Hv+NPuSRHkHAPSs5G/eEtyOfzF'
    'axiSxJ3BlwO3pWbI3Dc/Wrk4y7be1ZZfDcdeMirsSx7ElWxzz0qvu2qQBzTnmHP1qs0hC4x780yWI52qGY+w/Koi'
    'w3sSegpkj84J4BIxVcyAKzevFOwXJi2UznvSO7AL6dqrs52oFPrQ0oYqD6U7DJDJyxzjFUpXBOMYPvUxYHOef0ql'
    'KuVBH/6qYX6AWIBHY1MpzCRu53IOenJrPml2kKPT8qViREgPRpB+gJoJuI5G7vxTAw5zUe49hTNwKkilY0uSu2Vw'
    'FwTURJ3KB6dKQknr7UoI3E5xgU7C3Iyec+ppwBLE9qVVHHOajZvm9MnFJjuOZvmwOKj3/Nyc8UM4L1Dn5aELqT7/'
    'AJhinqctkVWB+bHtmrEQwc0mh8xq2anr+FcJ40n/AOJnFADny4R+bHP8hXodmMLz3NeLeKPEWlHxRfWk86xvA6xk'
    'MCBwo6N071thIOVR26EV5JRtchjkIIBzWlDMOnWs6F7W5XdazRyj/ZYH9KkCtGa7Wc1jZV8jGc1ZVunNYKysmcVa'
    'S54weamwrm55mRip45MYGe9Yy3CtgDvVgSjOelKwGysg5wcmpBJj6d//AK1ZCz/N8x696k+0jcQOfrSYI2xL1LE9'
    'P5VYJ4U1z63Pcjn19verq3R2jjrSK8y5MQG3Afe4/HqKbjdGP4ip/SoGnypGORgjPcjkVBHOrsxi4VvmA9jz/wDW'
    'qdRj5XAYc8CqrPuOO1PkJz6ZqsQQfY8UkgJJCrAbRjPPfkdqhPXaOAKHPJx/nFJyeR2pFIc+APSgH5cH6U1+uOKQ'
    't8vv3qfILDt2TzSZ/WmFgBUEku1Cc89B9e1FgaJkJJZs98flxUobnmoEyqAHsMU8OoJzyKHuKxdXnrX1n8GtCGle'
    'GH1mfKzas+9eORBGSqfmct+VfPXw+8Jz+M9cWxGRZW+JLyUdFj/uA/3n6D86+4VWG3hjtraIJHCgjRFHCqowAPoK'
    'hopaOxVklgxy9U3ntz0fNSXEobggD8KznKegpKJLl5n/0ecdGHRcVEUf0xWhJ1NU2JzX5e0fpSZXwy8Z/lUkbNnn'
    'mnMBU9uBnpTSuNlmFWetq2gY4+UD3zVaIALwK1LX71XGJlKVjbsYyjAnrXd6ajbARuyT7CuOs/vV6BpoBi5FethY'
    'nnYmWhsINq8ljj3rHvkUjIBxngE11iKPLHA6VkagB5fT1rvnDQ4YT1PP7mJSThPzrIltwBgqK6m5Az0rJfnOa8ur'
    'BHo05s55rOEnFKLaAYzk/TAq7IBlqiAHFcbWp1pipDbqMKv581aSCMfwZ/SlgA21aH3qjlLbJ4BCpAKgfhWvG8R4'
    'AH5VnCtK1A29KuMbEMn3p93+ldr4Xl2W10y9C8QI9Rhs1x2BzXW+Hv8Aj1u/9+L/ANmraN1qjGeujNO6jMMpAHyN'
    'yp9jVbPtW5MAdNjYjJ3kZrLrvhqkzilo2iNWY9KlG7tQKUdKtEvuTKQPvE1KJEHTNVR1NLVCaHPKh9a5PxBpcOoW'
    '7ME+YfjXSGqz8g5qJLmTTKj7ruj5X8UaDaXDNa3luGRuMMK8zf4f26uRZ2m5eowtfW2uwwtdruRT9QK0LC3gEORG'
    'g/4CK8lRlGbipHoylFxTcT4n1T4Y6ldWrtDZsFwQeOxrY+FHhi+1+0ltUj8yWzO189RglefxFfddtbwGwYGNCP8A'
    'dHrXzn+zwAPGviOMfd8+7G3txOccV30abqQlGT7M4a1XknGUV3RtWvwm1STlkCD6V0Nr8H5zjzmCivpkIgThQPwq'
    'BgOaPqkB/WZM8PtvhJYR/wCvcn6cVuW/w48PwD549/1r0xuc5qt2NWqMF0D2sn1OXg8J6BbY2WqH3IrZg03TYP8A'
    'V26D8BV09aB1rRRXREOT7ksaRL9xFH4D/Cp8+mKSLpVggVokSyvub0pDuPJBq1gU0gU3AVyod1JirBppqHEpMh2e'
    '9PEQ/iNPqSly2GMWKPuas+YgXAquOhprE4oRLRJJIexFVXdj3oNV36mqYkMZs9cVNbXDQyblPHcVX71GetDWhR2E'
    'c0cyhl69/aoZFPXccViaezecBk1vHvWVtQ2K30zTwP8AOakHWim4CchvI6in7jjJFIfumkarUSZSGM/HSodxzzUr'
    'dfxqFu9XGJFx4I7mn7kH1qCgdapIiTZY356Um4560g6UtUkRsNJ9TTDg9TUnY0zvSCw3j6/jThS4FL2rSKIY3OPe'
    'oCTngmrNVj9803EBwbGOv507d70zvUnakNobuoyKdTaYhQxqdD61COtTL1/z61ViXJk455700+4pwJzSH7tOxNwy'
    'aVSDUWTU0dUiGyZRxUhx6U1SdoqYdKpIRFx6UDpT2600E1diWxRnrT8560lIelMklDDNTBucmqcZO6rXatEJkkq+'
    'dazwn+JCR+FfMPiW18m+kDdMnAr6gg/1qj6/yr538ZAfbnx/eNcdZe+hr4Dym5UrIcDpzzWFPtJOO/NdJd/eP0rm'
    'Z/vGpsRcz34bgdj/ACrmoU2wPEOPKldf/Htw/Qiuok61yak/bNQGeBNHgf8AbJaaQSGNhWIPfkDt0qizcFOn/wBa'
    'rE3Wqb9/pVW0IkVp3DJkHnGKwrp9zuynAYYx7+9acv3fwrDn/wBYxppBITfhRnsf51DOwKk+uOlNyePoaZddPyqo'
    'onoUZ1zk9cdPwNUWPzbe9Xrj/V1Tf7ue+DVWuJGdMMqwJJ9/pVR9pjII44Oatv0b6H+lUl+431NWgZXbAkRjyMEV'
    'FG4Ys2eATx6Gkcn5fqf5UyLqfqf5ikKxbkcCMIO5/IdTVRsgAL0AxT5yd6/7h/mKibp+dN7Cb1FDEAnpmojJzjPI'
    'p5+7VRvvGpGmWEcsRntU+8ZJ9eBVGImpx0FMaJ9/ABoaQngH8qiphqbaiTLAf5g3NN8zGec1GTSU7Bc4nxOYjqcM'
    'j/eMIA9PlYisYYNXvGPF5aY/55t/6Eax7Ukqee1enTXuo8+svedi3KN1s6jthvyrKfG3dWv/AMs3+lZcPMsAPQyL'
    '/OtL2VzCGskj7g/ZI+MUfw61BfAfiSUR6Lrtx5iyt0tb6TCox9Ek4VvfB9a/UmSUcj0r+f3USVtmKnBCsQR6gEiv'
    '3G+H800/gLw7PO7SSyaXaM7uSzMTEOSTyTXmqbbbZ7lWmopWPxz/AGtHurz49eLZNTs/IMc8UMRT5TJbrEojlJ6N'
    'vGTmrngLU47/AMLae6MS1un2aTcfmDRHGD/wHFd7+3uqp8UNFkQBXk0RN7AYLbZmA3HvgdM14D8HXc2+sxliVEkD'
    'AZ4BKnJx6mvSxEVLDRl2PHotqvJH0bYXOCpJ4rr7G4yBzz6V51Zk12OmE5rxJo9FHTTvujJB7Vzckn7rYT9xio/P'
    'I/Q1uuTsP0rlpCfNlHuv8qiK6GiZDM2U2+3UVncAj0NTzEjNUT978a0SHchJHqecgc/pWe5/eEkcYGRVuX75/H+Z'
    'rNkJ5OarlEyuxIGD1psg3fKRSP2+tNk9fpTsLchckMSwwRyPeqjNlcnrmpyfvHv/APqqsfvH607C6gTnALdKUs24'
    'AHoOtN759aYSeaBj2c5Y8HNQOylFz60jfdP1qux/Q/40xMR1G8nrTZWINupHRyR+CmpOpOfaoJv9fbfWT/0GmkIj'
    'JGSxNRZyPl5zSNyajYnBpFolz8xGc8U9Cu0547YqEU9PukUgJMgEe1VyfTjJzTn+8aiPSgdxhJLdajZsDHbil71F'
    'J92gm+pOjYbcfSraMNwx3qgnarMf3h/nvQJM6W0kRF3uRheT9BzXxRqU8uteIrueJS8l5dSFAOpLOQv6Yr7ClJGn'
    'XRBxiGT/ANANfG/h9iNTtnBIYMCD3zXoZd7qqSRliPelCLPUtQ+H3labAmnTFLuIZdycCRj15HTHQVysF14u0+Z7'
    'Xe0pi6q6hx+Zr3RGYouSTwOtZmtohsw5UbgeuOa56WNmnafvX7ndUwdOSvHQ83t/E2pIMX+n5x1aIkH/AL5b/GtW'
    'DxNpExCPIYHP8Mqlf16VO4DL8wzx3rk9XjjMDEqpI6HArshKM3blscM6PKr3PQ4po5UDwurr2KkH+VTiZgMH9a8P'
    't5poHUwSNGf9glf5V7LCzNbxsxJJUcnk0q1Lke5lCXMrmh5277pxThOTyOMVmMSOhqRCcVjcpm3HJkcdRUscuB1y'
    'AayoyR0J/wAmnREhjimkBsfaPU1CJfKm2r0OXX6H7y/geRWcSQ3Bp0pOxD3Eg/XOaSQzW85TlgevWhZQ2COfT8ay'
    'ASFAFSxE4Iz3oaGi3u+bpwKf5g4HQZ5qtk7aaves2hk/mjGT3pu/OcVVfrQv9KGgRYZ8CqBlElx/sx/+hf8A1qJS'
    'eeaqQ/cX3zQu5TNcSg4xzXo/gf4ceIPG06yW8ZtNNDYlvZV+TA6iMHBdvpx6mvGdYkePTZ2jYqQh5Bwa/THwsT/w'
    'iWh8n/kH2x/8hrU8ulxc3QraF4e0jwjpcek6NF5cScu7cySv3d27k/kBwKvNctzjjNXp/u1lEDmoJfcbJMmMNVN/'
    'JbkEZqdgCapygZPFMg//2Q=='
)
DEVELOPER_NAME = "Young Lee"
DEVELOPER_EMAIL = "lyn0109@gmail.com"
LIFE_ENTRY_VERSION = "life-homepage-2026-08-25-client-visual-v5"
MAX_DIARY_RESTORE_BYTES = 250_000
MAX_DIARY_RESTORE_ENTRIES = 50


@st.cache_data(show_spinner=False)
def image_data_uri(path_text: str) -> str:
    image_path = Path(path_text)
    if not image_path.exists():
        if image_path.name == HOMEPAGE_BG_PATH.name and HOMEPAGE_BG_EMBEDDED_BASE64:
            return f"data:{HOMEPAGE_BG_EMBEDDED_MIME};base64,{HOMEPAGE_BG_EMBEDDED_BASE64}"
        return ""
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    suffix = image_path.suffix.lower()
    mime_type = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
    return f"data:{mime_type};base64,{encoded}"


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

US_STOCK_MAP = {
    "apple": "AAPL",
    "apple inc": "AAPL",
    "aapl": "AAPL",
    "microsoft": "MSFT",
    "microsoft corporation": "MSFT",
    "msft": "MSFT",
    "nvidia": "NVDA",
    "nvidia corporation": "NVDA",
    "nvda": "NVDA",
    "tesla": "TSLA",
    "tesla inc": "TSLA",
    "tsla": "TSLA",
    "amazon": "AMZN",
    "amazon.com": "AMZN",
    "amzn": "AMZN",
    "alphabet": "GOOGL",
    "google": "GOOGL",
    "googl": "GOOGL",
    "goog": "GOOG",
    "meta": "META",
    "facebook": "META",
    "meta platforms": "META",
    "meta platforms inc": "META",
    "netflix": "NFLX",
    "nflx": "NFLX",
    "broadcom": "AVGO",
    "avgo": "AVGO",
    "berkshire": "BRK-B",
    "berkshire hathaway": "BRK-B",
    "brk.b": "BRK-B",
    "brk-b": "BRK-B",
    "jpmorgan": "JPM",
    "jp morgan": "JPM",
    "jpmorgan chase": "JPM",
    "jpm": "JPM",
    "visa": "V",
    "v": "V",
    "mastercard": "MA",
    "ma": "MA",
    "walmart": "WMT",
    "wmt": "WMT",
    "costco": "COST",
    "cost": "COST",
    "procter gamble": "PG",
    "procter & gamble": "PG",
    "pg": "PG",
    "eli lilly": "LLY",
    "lilly": "LLY",
    "lly": "LLY",
    "unitedhealth": "UNH",
    "united health": "UNH",
    "unh": "UNH",
    "johnson johnson": "JNJ",
    "johnson & johnson": "JNJ",
    "jnj": "JNJ",
    "exxon": "XOM",
    "exxon mobil": "XOM",
    "xom": "XOM",
    "chevron": "CVX",
    "cvx": "CVX",
    "home depot": "HD",
    "hd": "HD",
    "oracle": "ORCL",
    "orcl": "ORCL",
    "salesforce": "CRM",
    "crm": "CRM",
    "adobe": "ADBE",
    "adbe": "ADBE",
    "amd": "AMD",
    "advanced micro devices": "AMD",
    "intel": "INTC",
    "intc": "INTC",
    "palantir": "PLTR",
    "pltr": "PLTR",
    "coinbase": "COIN",
    "coin": "COIN",
    "robinhood": "HOOD",
    "hood": "HOOD",
    "spdr s&p 500": "SPY",
    "s&p 500 etf": "SPY",
    "spy": "SPY",
    "nasdaq 100": "QQQ",
    "qqq": "QQQ",
}

US_STOCK_PROFILE_FALLBACKS = {
    "AAPL": {"name": "Apple Inc.", "industry": "Consumer Electronics", "beta": 1.09},
    "MSFT": {"name": "Microsoft Corporation", "industry": "Software - Infrastructure", "beta": 1.10},
    "NVDA": {"name": "NVIDIA Corporation", "industry": "Semiconductors", "beta": 2.20},
    "TSLA": {"name": "Tesla, Inc.", "industry": "Auto Manufacturers", "beta": 2.00},
    "AMZN": {"name": "Amazon.com, Inc.", "industry": "Internet Retail", "beta": 1.30},
    "GOOGL": {"name": "Alphabet Inc.", "industry": "Internet Content & Information", "beta": 1.05},
    "GOOG": {"name": "Alphabet Inc.", "industry": "Internet Content & Information", "beta": 1.05},
    "META": {"name": "Meta Platforms, Inc.", "industry": "Internet Content & Information", "beta": 1.20},
    "NFLX": {"name": "Netflix, Inc.", "industry": "Entertainment", "beta": 1.30},
    "AVGO": {"name": "Broadcom Inc.", "industry": "Semiconductors", "beta": 1.15},
    "BRK-B": {"name": "Berkshire Hathaway Inc.", "industry": "Insurance - Diversified", "beta": 0.90},
    "JPM": {"name": "JPMorgan Chase & Co.", "industry": "Banks - Diversified", "beta": 1.10},
    "V": {"name": "Visa Inc.", "industry": "Credit Services", "beta": 0.95},
    "MA": {"name": "Mastercard Incorporated", "industry": "Credit Services", "beta": 1.00},
    "WMT": {"name": "Walmart Inc.", "industry": "Discount Stores", "beta": 0.60},
    "COST": {"name": "Costco Wholesale Corporation", "industry": "Discount Stores", "beta": 0.80},
    "PG": {"name": "The Procter & Gamble Company", "industry": "Household & Personal Products", "beta": 0.45},
    "LLY": {"name": "Eli Lilly and Company", "industry": "Drug Manufacturers - General", "beta": 0.55},
    "UNH": {"name": "UnitedHealth Group Incorporated", "industry": "Healthcare Plans", "beta": 0.75},
    "JNJ": {"name": "Johnson & Johnson", "industry": "Drug Manufacturers - General", "beta": 0.55},
    "XOM": {"name": "Exxon Mobil Corporation", "industry": "Oil & Gas Integrated", "beta": 0.95},
    "CVX": {"name": "Chevron Corporation", "industry": "Oil & Gas Integrated", "beta": 0.90},
    "HD": {"name": "The Home Depot, Inc.", "industry": "Home Improvement Retail", "beta": 1.00},
    "ORCL": {"name": "Oracle Corporation", "industry": "Software - Infrastructure", "beta": 1.05},
    "CRM": {"name": "Salesforce, Inc.", "industry": "Software - Application", "beta": 1.25},
    "ADBE": {"name": "Adobe Inc.", "industry": "Software - Infrastructure", "beta": 1.15},
    "AMD": {"name": "Advanced Micro Devices, Inc.", "industry": "Semiconductors", "beta": 1.85},
    "INTC": {"name": "Intel Corporation", "industry": "Semiconductors", "beta": 1.10},
    "PLTR": {"name": "Palantir Technologies Inc.", "industry": "Software - Infrastructure", "beta": 1.50},
    "COIN": {"name": "Coinbase Global, Inc.", "industry": "Financial Data & Stock Exchanges", "beta": 2.40},
    "HOOD": {"name": "Robinhood Markets, Inc.", "industry": "Capital Markets", "beta": 1.80},
    "SPY": {"name": "SPDR S&P 500 ETF Trust", "industry": "Large Blend ETF", "beta": 1.00},
    "QQQ": {"name": "Invesco QQQ Trust", "industry": "Large Growth ETF", "beta": 1.10},
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
    st.session_state.setdefault("use_live_us10y", True)
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
    macro = macro_assumption_details()
    risk_free_rate = float(macro["risk_free_rate_pct"])
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


@st.cache_data(ttl=3600, show_spinner=False)
def yahoo_search_symbol(query: str) -> str | None:
    clean = query.strip()
    if not clean:
        return None
    try:
        response = requests.get(
            "https://query1.finance.yahoo.com/v1/finance/search",
            params={"q": clean, "quotesCount": 6, "newsCount": 0},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    quotes = data.get("quotes") if isinstance(data, dict) else []
    if not isinstance(quotes, list):
        return None

    normalized = normalize_company_query(clean)
    upper = clean.upper()
    for quote in quotes:
        symbol = str(quote.get("symbol") or "").upper()
        quote_type = str(quote.get("quoteType") or "").upper()
        if symbol == upper and quote_type in {"EQUITY", "ETF"}:
            return symbol
    for quote in quotes:
        symbol = str(quote.get("symbol") or "").upper()
        quote_type = str(quote.get("quoteType") or "").upper()
        short_name = normalize_company_query(str(quote.get("shortname") or ""))
        long_name = normalize_company_query(str(quote.get("longname") or ""))
        if quote_type in {"EQUITY", "ETF"} and symbol:
            if normalized in {short_name, long_name} or normalized in short_name or normalized in long_name:
                return symbol
    for quote in quotes:
        symbol = str(quote.get("symbol") or "").upper()
        quote_type = str(quote.get("quoteType") or "").upper()
        if quote_type in {"EQUITY", "ETF"} and symbol:
            return symbol
    return None


def resolve_yahoo_ticker(query: str) -> str:
    clean = query.strip()
    normalized = normalize_company_query(clean)
    if normalized in US_STOCK_MAP:
        return US_STOCK_MAP[normalized]

    upper = clean.upper().replace(".", "-")
    if upper in US_STOCK_MAP:
        return US_STOCK_MAP[upper]
    if upper and all(char.isalnum() or char in {"-", "."} for char in upper) and len(upper) <= 12:
        return upper

    yahoo_symbol = yahoo_search_symbol(clean)
    return yahoo_symbol or upper


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


@st.cache_data(ttl=3600, show_spinner=False)
def load_us10y_treasury_rate() -> dict[str, Any]:
    try:
        response = requests.get(US10Y_FRED_CSV_URL, timeout=12)
        response.raise_for_status()
        data = pd.read_csv(StringIO(response.text))
        if {"observation_date", "DGS10"}.issubset(data.columns):
            data["DGS10"] = pd.to_numeric(data["DGS10"], errors="coerce")
            clean = data.dropna(subset=["DGS10"]).sort_values("observation_date")
            if not clean.empty:
                latest = clean.iloc[-1]
                rate_pct = float(latest["DGS10"])
                if 0 < rate_pct < 25:
                    return {
                        "rate_pct": rate_pct,
                        "date": str(latest["observation_date"]),
                        "source": "FRED DGS10 via Federal Reserve Bank of St. Louis",
                    }
    except Exception:
        pass

    history = normalize_price_history(load_price_history_from_yahoo(US10Y_YAHOO_SYMBOL, days=10))
    if not history.empty:
        latest = history.iloc[-1]
        raw_value = positive_float(latest.get("Close"))
        if raw_value:
            rate_pct = raw_value / 10 if raw_value > 20 else raw_value
            if 0 < rate_pct < 25:
                return {
                    "rate_pct": rate_pct,
                    "date": latest["Date"].strftime("%Y-%m-%d"),
                    "source": "Yahoo Finance ^TNX fallback",
                }

    return {"rate_pct": None, "date": None, "source": "Unavailable"}


def macro_assumption_details() -> dict[str, Any]:
    manual_risk_free_pct = float(
        st.session_state.get("risk_free_rate_pct", DEFAULT_RISK_FREE_RATE * 100)
        or DEFAULT_RISK_FREE_RATE * 100
    )
    if st.session_state.get("use_live_us10y", True):
        treasury = load_us10y_treasury_rate()
        if treasury.get("rate_pct"):
            return {
                "risk_free_rate_pct": float(treasury["rate_pct"]),
                "risk_free_rate_source": str(treasury.get("source") or "U.S. 10Y Treasury"),
                "risk_free_rate_date": str(treasury.get("date") or "Latest"),
                "risk_free_rate_mode": "U.S. 10Y Treasury",
                "equity_risk_premium_pct": float(
                    st.session_state.get("equity_risk_premium_pct", DEFAULT_EQUITY_RISK_PREMIUM * 100)
                    or DEFAULT_EQUITY_RISK_PREMIUM * 100
                ),
            }

    return {
        "risk_free_rate_pct": manual_risk_free_pct,
        "risk_free_rate_source": "Manual CAPM input",
        "risk_free_rate_date": "User input",
        "risk_free_rate_mode": "Manual",
        "equity_risk_premium_pct": float(
            st.session_state.get("equity_risk_premium_pct", DEFAULT_EQUITY_RISK_PREMIUM * 100)
            or DEFAULT_EQUITY_RISK_PREMIUM * 100
        ),
    }


def apply_price_implied_baseline(stock: dict[str, Any]) -> dict[str, Any]:
    price = positive_float(stock.get("price"))
    if not price:
        return stock

    has_fundamentals = any(
        positive_float(stock.get(key))
        for key in ("eps", "book_value", "pe", "dividend")
    )
    if has_fundamentals:
        return stock

    baseline_pe = 25.0
    stock["pe"] = baseline_pe
    stock["eps"] = price / baseline_pe
    stock["book_value"] = price / 5.0
    stock["peer_average_pe"] = baseline_pe
    stock["growth_rate"] = stock.get("growth_rate") or 0.05
    stock["beta"] = stock.get("beta") or 1.0
    stock["price_implied_fallback"] = True
    quality = stock.get("data_quality") or "Price data"
    if "price-implied valuation baseline" not in quality:
        stock["data_quality"] = f"{quality} + price-implied valuation baseline"
    return stock


def calculate_valuation(stock: dict[str, Any]) -> dict[str, Any]:
    beta = float(stock.get("beta") or 1.0)
    eps = float(stock.get("eps") or 0)
    dividend = float(stock.get("dividend") or 0)
    growth = float(stock.get("growth_rate") or 0.05)
    book_value = float(stock.get("book_value") or 0)
    peer_pe = float(stock.get("peer_average_pe") or 15)
    price = float(stock.get("price") or 0)

    macro = macro_assumption_details()
    risk_free_rate = float(macro["risk_free_rate_pct"]) / 100
    equity_risk_premium = float(macro["equity_risk_premium_pct"]) / 100
    expected_return = risk_free_rate + beta * equity_risk_premium
    if stock.get("price_implied_fallback") and price > 0:
        stock.update(
            {
                "expected_return": expected_return,
                "risk_free_rate": risk_free_rate,
                "equity_risk_premium": equity_risk_premium,
                "risk_free_rate_source": macro.get("risk_free_rate_source"),
                "risk_free_rate_date": macro.get("risk_free_rate_date"),
                "risk_free_rate_mode": macro.get("risk_free_rate_mode"),
                "fair_price": price,
                "valuation_status": "Fair Value",
                "triangulation": {
                    "income_model": "N/A",
                    "income_value": 0.0,
                    "asset_value": 0.0,
                    "market_model": "Price-implied baseline",
                    "market_value": price,
                    "valid_models": 1,
                },
            }
        )
        return stock

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
            "risk_free_rate_source": macro.get("risk_free_rate_source"),
            "risk_free_rate_date": macro.get("risk_free_rate_date"),
            "risk_free_rate_mode": macro.get("risk_free_rate_mode"),
            "fair_price": fair_price,
            "valuation_status": status,
            "triangulation": {
                "income_model": income_model,
                "income_value": income_value,
                "asset_value": graham_value,
                "market_model": "Peer P/E",
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


def positive_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def load_korean_stock(query: str) -> dict[str, Any]:
    symbol = resolve_korean_ticker(query)
    if not symbol:
        raise ValueError(f"{query} is not recognized as a Korean stock.")

    ticker = yf.Ticker(symbol)
    try:
        info = ticker.get_info()
    except Exception:
        info = {}

    history = normalize_price_history(load_price_history_from_yahoo(symbol, days=30))
    if history.empty:
        try:
            history = normalize_price_history(
                ticker.history(period="30d", interval="1d", auto_adjust=True).reset_index()
            )
        except Exception:
            history = pd.DataFrame()

    closes = history["Close"].astype(float).tolist() if not history.empty and "Close" in history.columns else []
    price = closes[-1] if closes else None
    if price is None:
        for key in ("currentPrice", "regularMarketPrice", "previousClose", "open"):
            price = positive_float(info.get(key))
            if price is not None:
                break

    previous = closes[-2] if len(closes) >= 2 else positive_float(info.get("previousClose")) or price
    change_pct = ((price - previous) / previous * 100) if price and previous else 0.0
    data_quality = (
        "Live Yahoo price history"
        if closes
        else "Yahoo profile price"
        if price
        else "Profile-only fallback; live Yahoo price unavailable"
    )

    market_cap = info.get("marketCap")
    market_cap_millions = float(market_cap) / 1_000_000 if market_cap else None
    trailing_eps = positive_float(info.get("trailingEps")) or 0
    book_value = positive_float(info.get("bookValue")) or 0
    dividend_rate = positive_float(info.get("dividendRate")) or 0
    dividend_yield = (float(info.get("dividendYield") or 0) * 100)
    pe = positive_float(info.get("trailingPE")) or positive_float(info.get("forwardPE"))
    beta = positive_float(info.get("beta")) or 1.0
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
        "data_quality": data_quality,
    }
    stock = apply_price_implied_baseline(stock)
    return calculate_valuation(stock)


def load_yahoo_stock(query: str) -> dict[str, Any]:
    symbol = resolve_yahoo_ticker(query)
    if not symbol:
        raise ValueError(f"{query} could not be resolved to a ticker.")

    profile_fallback = US_STOCK_PROFILE_FALLBACKS.get(symbol, {})
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.get_info()
    except Exception:
        info = {}

    history = normalize_price_history(load_price_history_from_yahoo(symbol, days=30))
    if history.empty:
        try:
            history = normalize_price_history(
                ticker.history(period="30d", interval="1d", auto_adjust=True).reset_index()
            )
        except Exception:
            history = pd.DataFrame()

    closes = history["Close"].astype(float).tolist() if not history.empty and "Close" in history.columns else []
    price = closes[-1] if closes else None
    if price is None:
        for key in ("currentPrice", "regularMarketPrice", "previousClose", "open"):
            price = positive_float(info.get(key))
            if price is not None:
                break
    if price is None:
        raise ValueError(
            f"No current price was returned for {symbol}. If this ticker is valid, try again later or add FINNHUB_API_KEY for the live data provider."
        )

    previous = closes[-2] if len(closes) >= 2 else positive_float(info.get("previousClose")) or price
    change_pct = ((price - previous) / previous * 100) if price and previous else 0.0
    market_cap = info.get("marketCap")
    market_cap_millions = float(market_cap) / 1_000_000 if market_cap else None
    trailing_eps = positive_float(info.get("trailingEps")) or 0
    book_value = positive_float(info.get("bookValue")) or 0
    dividend_rate = positive_float(info.get("dividendRate")) or 0
    dividend_yield_raw = info.get("dividendYield")
    dividend_yield = float(dividend_yield_raw) * 100 if dividend_yield_raw else 0
    pe = positive_float(info.get("trailingPE")) or positive_float(info.get("forwardPE"))
    beta = positive_float(info.get("beta")) or 1.0
    growth_rate = info.get("earningsGrowth")
    if growth_rate is None:
        growth_rate = info.get("revenueGrowth")
    if growth_rate is None:
        growth_rate = 0.05
    currency = str(info.get("currency") or "USD").upper()
    if currency not in {"USD", "KRW"}:
        currency = "USD"
    peer_pe = pe if pe and 0 < float(pe) < 100 else 15.0
    data_quality = (
        "Yahoo Finance price history"
        if closes
        else "Yahoo profile price"
    )

    stock = {
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName") or profile_fallback.get("name") or symbol,
        "industry": info.get("industry") or info.get("sector") or profile_fallback.get("industry") or "US Equity",
        "price": price,
        "change_pct": change_pct,
        "market_cap": market_cap_millions,
        "pe": pe,
        "dividend_yield": dividend_yield,
        "beta": beta if beta != 1.0 else profile_fallback.get("beta", beta),
        "eps": trailing_eps,
        "dividend": dividend_rate,
        "growth_rate": growth_rate,
        "book_value": book_value,
        "peer_average_pe": peer_pe,
        "peers": [],
        "market": "US",
        "currency": currency,
        "data_quality": data_quality,
    }
    stock = apply_price_implied_baseline(stock)
    return calculate_valuation(stock)


def load_finnhub_stock(query: str) -> dict[str, Any]:
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
        "data_quality": "Finnhub live quote and metrics",
    }
    return calculate_valuation(stock)


def load_stock(query: str) -> dict[str, Any]:
    korean_symbol = resolve_korean_ticker(query)
    if korean_symbol:
        return load_korean_stock(korean_symbol)

    if FINNHUB_API_KEY:
        try:
            return load_finnhub_stock(query)
        except Exception:
            return load_yahoo_stock(query)
    return load_yahoo_stock(query)


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


def add_portfolio_position_from_search(symbol: str) -> None:
    stock = st.session_state.stocks.get(symbol)
    if not stock:
        return

    price = positive_float(stock.get("price"))
    value_key = f"portfolio_search_position_size_{symbol}"
    mode_key = f"portfolio_search_position_mode_{symbol}"
    purchase_key = f"portfolio_search_purchase_price_{symbol}"
    position_value = positive_float(st.session_state.get(value_key))
    if not price or not position_value:
        st.session_state.portfolio_search_notice = ui("Enter position size before adding.")
        return

    mode = st.session_state.get(mode_key, "Current value amount")
    shares = position_value if mode == "Share count" else position_value / price
    purchase_price = positive_float(st.session_state.get(purchase_key)) or 0.0
    st.session_state.portfolio[symbol] = {
        "shares": max(float(shares), 0.0),
        "purchase_price": purchase_price,
    }
    st.session_state.pop(f"sidebar_portfolio_{symbol}", None)
    st.session_state.portfolio_search_notice = ui("Position added to portfolio.")
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
    with st.expander(ui("Quick Portfolio Entry"), expanded=not bool(st.session_state.portfolio)):
        st.caption(
            ui(
                "Paste one holding per line: ticker, current value or shares, optional average purchase price. Current value amount should be in the stock's native currency."
            )
        )
        mode_cols = st.columns([1, 2])
        with mode_cols[0]:
            input_mode = st.radio(
                ui("Quick input type"),
                ["Current value amount", "Share count"],
                horizontal=False,
                key="portfolio_quick_input_mode",
                format_func=ui,
            )
        with mode_cols[1]:
            st.text_area(
                ui("Holdings input"),
                key="portfolio_quick_entry",
                height=120,
                placeholder="AAPL, 5000, 180\n005930.KS, 10000000, 72000\nMSFT, 12, 310",
            )
        button_cols = st.columns([1, 2])
        with button_cols[0]:
            if st.button(ui("Apply Holdings"), width="stretch"):
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
                ui(
                    "For a KRW 200M stock portfolio, enter each position value in KRW for Korean stocks or USD for U.S. stocks. The app estimates shares from current price."
                )
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
            "Model": [tri["income_model"], "Graham Number", tri.get("market_model", "Peer P/E")],
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
    return (
        f'<div class="portfolio-score-card {visual_score_tone(safe_score)}" tabindex="0">'
        f'<div class="portfolio-score-label">{ui_html(str(label))}</div>'
        f'<div class="portfolio-score-value">{escape(str(value))}</div>'
        f'<div class="portfolio-score-bar"><span style="--value:{safe_score:.0f}%"></span></div>'
        f'<div class="portfolio-score-detail">{escape(str(detail))}</div>'
        '</div>'
    )


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
    price_display = stock_money(stock, stock.get("price")) if positive_float(stock.get("price")) else "N/A"
    data_quality = str(stock.get("data_quality") or "Market data")
    risk_free_display = f"{float(stock.get('risk_free_rate') or macro_assumptions()[0]) * 100:.2f}%"
    valuation_status = str(stock.get("valuation_status", "Fair Value"))
    signal_class = "flat"
    if upside is not None:
        if upside > 5:
            signal_class = "up"
        elif upside < -5:
            signal_class = "down"
    quality_detail = (
        f"{ui('Growth')} {growth:.1f}% 및 PER {fmt_number(pe)}{ui('are compressed into one visual signal.')}"
        if current_language() == "ko"
        else f"{ui('Growth')} {growth:.1f}% and PER {fmt_number(pe)} {ui('are compressed into one visual signal.')}"
    )
    cards = "".join(
        [
            portfolio_score_card_html(
                "Upside",
                upside_text,
                upside_score,
                f"{ui('Current price')} {price_display}; {ui('blended fair value')} {fair_value}.",
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
                ui("Income, asset, and market approaches are checked when source inputs are available."),
            ),
            portfolio_score_card_html(
                "Growth / Quality",
                f"{quality_score:.0f}",
                quality_score,
                quality_detail,
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
                        <span class="portfolio-valuation-chip">PER {escape(fmt_number(pe))}</span>
                        <span class="portfolio-valuation-chip">{ui_html('Risk-Free Rate')} {escape(risk_free_display)}</span>
                        <span class="portfolio-valuation-chip">{ui_html(data_quality)}</span>
                    </div>
                </div>
                <span class="portfolio-valuation-status" style="background:{status_color(valuation_status)};">
                    {ui_html(valuation_status)}
                </span>
            </div>
            <div class="portfolio-price-stage" aria-label="Price and valuation summary">
                <div class="portfolio-price-card market">
                    <div class="portfolio-price-label">{ui_html('Current price')}</div>
                    <div class="portfolio-price-value">{escape(price_display)}</div>
                    <div class="portfolio-price-note">{ui_html(data_quality)}</div>
                </div>
                <div class="portfolio-price-card fair">
                    <div class="portfolio-price-label">{ui_html('Fair Value')}</div>
                    <div class="portfolio-price-value">{escape(fair_value)}</div>
                    <div class="portfolio-price-note">{ui_html('blended fair value')}</div>
                </div>
                <div class="portfolio-price-card signal {signal_class}">
                    <div class="portfolio-price-label">{ui_html('Upside')}</div>
                    <div class="portfolio-price-value">{escape(upside_text)}</div>
                    <div class="portfolio-price-note"><b>{ui_html(valuation_status)}</b></div>
                </div>
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
    st.markdown(
        f"""
        <div class="portfolio-sr-header" aria-label="{ui_html('SR · Portfolio Search')}">
            <span>SR</span>
            <b>{ui_html('SR · Portfolio Search')}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.caption(ui("Search ticker/company, review valuation, then add it to this portfolio."))
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
                        "Model": tri.get("market_model", "Peer P/E"),
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

        already_in_portfolio = symbol in st.session_state.portfolio
        price_available = positive_float(stock.get("price")) is not None
        mode_key = f"portfolio_search_position_mode_{symbol}"
        value_key = f"portfolio_search_position_size_{symbol}"
        purchase_key = f"portfolio_search_purchase_price_{symbol}"
        position_cols = st.columns([1.15, 1.25, 1.25])
        with position_cols[0]:
            st.radio(
                ui("Position input"),
                ["Current value amount", "Share count"],
                horizontal=False,
                key=mode_key,
                format_func=ui,
            )
        with position_cols[1]:
            st.number_input(
                ui("Position size"),
                min_value=0.0,
                step=100000.0 if stock.get("currency") == "KRW" else 100.0,
                key=value_key,
                help=ui("Enter position size before adding."),
            )
        with position_cols[2]:
            st.number_input(
                ui("Average purchase price (optional)"),
                min_value=0.0,
                step=1000.0 if stock.get("currency") == "KRW" else 1.0,
                key=purchase_key,
            )
        notice = st.session_state.pop("portfolio_search_notice", "")
        if notice:
            st.success(notice)

        action_cols = st.columns(2)
        action_cols[0].button(
            ui("Already in Portfolio")
            if already_in_portfolio
            else ui("Price unavailable")
            if not price_available
            else ui("Add Position to Portfolio"),
            key=f"portfolio_search_add_{symbol}",
            on_click=add_portfolio_position_from_search,
            args=(symbol,),
            width="stretch",
            disabled=already_in_portfolio
            or not price_available,
        )
        action_cols[1].button(
            ui("Open Full Stock Detail"),
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
                "Model": tri.get("market_model", "Peer P/E"),
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
        if current_language() == "ko":
            st.info(
                "FINNHUB_API_KEY가 없어도 티커 검색은 Yahoo Finance/yfinance fallback으로 작동합니다. "
                "Finnhub 키를 추가하면 미국 주식의 보조 지표와 peer 데이터가 더 풍부해집니다."
            )
        else:
            st.info(
                "Ticker search can run through the Yahoo Finance/yfinance fallback without FINNHUB_API_KEY. "
                "Adding Finnhub enables richer US metrics and peer data."
            )

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

    st.subheader(ui("Portfolio Resilience Score"))
    score = float(summary["score"])
    score_color_value = "#10b981" if score >= 75 else "#f59e0b" if score >= 55 else "#ef4444"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(ui("Portfolio Score"), f"{score:.0f}/100", score_color_value)
    with c2:
        metric_card(ui("Status"), str(summary["status"]), score_color_value)
    with c3:
        metric_card(ui("Top Holding"), f"{float(summary['top_holding_weight']) * 100:.1f}%")
    with c4:
        metric_card(ui("Top Sector"), f"{float(summary['top_sector_weight']) * 100:.1f}%")

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
            file_name="ly_scope_ver2_scenario_packet.json",
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


def rationality_tone(score: float) -> str:
    score = max(0.0, min(100.0, float(score)))
    if score >= 74:
        return "good"
    if score >= 55:
        return "mid"
    return "watch"


def rationality_gate_snapshot() -> dict[str, Any]:
    language = current_language()
    goal = active_goal_key()
    personal = st.session_state.get("last_personal_finance_result") or {}
    holdings = portfolio_holdings_snapshot()
    stocks = st.session_state.get("stocks", {})
    scenario = st.session_state.get("last_scenario_packet")
    diary = st.session_state.get("financial_diary", [])

    evidence_count = sum(bool(item) for item in (personal, holdings, stocks, scenario))
    evidence_score = 35 + min(evidence_count, 4) * 13
    model_score = 74 if personal or stocks or scenario else 40
    risk_score = 86 if scenario else 68 if personal or holdings else 38
    memory_score = 88 if diary else 42

    if language == "ko":
        purpose_detail = "목표가 선택되어 판단 기준이 선명합니다." if goal else "아직 목표가 없어 판단 기준이 흔들릴 수 있습니다."
        evidence_detail = f"현재 근거 입력 {evidence_count}/4: 재무, 포트폴리오, 종목, 시나리오."
        model_detail = "모델 결과가 존재해 해석 전 계산 기준을 확인할 수 있습니다." if model_score >= 70 else "아직 모델 결과가 부족해 해석보다 입력이 먼저입니다."
        risk_detail = "시나리오까지 포함되어 위험을 먼저 점검합니다." if scenario else "위험 점검은 시작됐지만 시나리오 스트레스가 아직 약합니다."
        memory_detail = "다이어리/기록이 있어 판단을 나중에 되돌아볼 수 있습니다." if diary else "아직 기록이 없어 같은 판단을 반복 검증하기 어렵습니다."
    else:
        purpose_detail = "A selected goal makes the judgment standard clearer." if goal else "No selected goal yet, so the judgment standard can drift."
        evidence_detail = f"Current evidence inputs {evidence_count}/4: finance, portfolio, stock, scenario."
        model_detail = "Model output exists, so calculations can be checked before interpretation." if model_score >= 70 else "Model output is still thin; inputs should come before interpretation."
        risk_detail = "Scenario stress is included, so risk is checked before action." if scenario else "Risk review has started, but scenario stress is still weak."
        memory_detail = "Diary or report memory exists for later review." if diary else "No memory yet, so repeated judgment is harder to audit."

    pillars = [
        {"glyph": "WHY", "label": "Purpose Fit", "score": 92 if goal else 42, "detail": purpose_detail},
        {"glyph": "EVD", "label": "Evidence Quality", "score": evidence_score, "detail": evidence_detail},
        {"glyph": "MOD", "label": "Model Discipline", "score": model_score, "detail": model_detail},
        {"glyph": "RSK", "label": "Risk Awareness", "score": risk_score, "detail": risk_detail},
        {"glyph": "MEM", "label": "Memory Feedback", "score": memory_score, "detail": memory_detail},
    ]
    score = sum(float(item["score"]) for item in pillars) / len(pillars)
    if score >= 74:
        label = "Disciplined"
    elif score >= 55:
        label = "Developing"
    else:
        label = "Fragile"
    return {"score": score, "label": label, "pillars": pillars}


NORA_GOAL_STRATEGIES = {
    "protect_runway": {
        "icon": "01",
        "color": "#0f766e",
        "view": "finance",
        "label_en": "Protect Runway",
        "label_ko": "생존기간 보호",
        "short_en": "Cash safety first",
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
        "short_en": "Portfolio strategy",
        "short_ko": "포트폴리오 전략",
        "strategy_en": "Start from portfolio quality, concentration, valuation, beta, and downside capacity.",
        "strategy_ko": "포트폴리오 품질, 집중도, 가치평가, 베타, 하락 감당력을 먼저 봅니다.",
    },
    "build_income": {
        "icon": "03",
        "color": "#d97706",
        "view": "scenario",
        "label_en": "Build Income",
        "label_ko": "소득 만들기",
        "short_en": "Income path",
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
        "strategy_en": "Review property value, rent support, cash flow, liquidity, and rate sensitivity.",
        "strategy_ko": "부동산 가치, 임대수익 지지력, 현금흐름, 유동성, 금리 민감도를 확인합니다.",
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
        focus = query_param_value("focus")
        if focus:
            params["focus"] = focus
        client = query_param_value("client")
        if current_view == "advisor" and client:
            params["client"] = client
    return f"?{urlencode(params)}"


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
            <a class="{en_active.strip()}" href="{en_href}" target="_self" title="Switch to English" aria-label="Switch to English">EN</a>
            <a class="{ko_active.strip()}" href="{ko_href}" target="_self" title="한국어로 전환" aria-label="한국어로 전환">한</a>
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
    summary_path = "Goal → Strategy → Situation" if language == "en" else "목표 → 전략 → 상황"
    ontology_html = (
        f'<details class="nora-ontology nora-ontology-minimal" aria-label="{ui_html("NORA Ontology")}">'
        '<summary>'
        f'<b>{escape(summary_label)}</b>'
        f'<span>{escape(summary_path)}</span>'
        '</summary>'
        '<div class="nora-ontology-body">'
        '<div class="nora-ontology-caption">'
        f'{ui_html("NORA starts with the customer purpose, then checks the strategy and current situation before any model.")}'
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
    language = current_language()
    portfolio = context["portfolio"]
    holdings = portfolio.get("holdings", [])
    base_currency = portfolio.get("base_currency", "USD")
    personal = context.get("personal") or {}
    scenario = context.get("scenario")
    diary = context.get("diary", [])
    gain_loss = portfolio_gain_loss_summary(holdings)

    if not holdings:
        portfolio_status = "Needs holdings" if language == "en" else "보유 종목 필요"
        portfolio_advice = (
            "Add stocks first, then enter shares and average purchase price so the coach can compare cost basis with current value."
            if language == "en"
            else "먼저 종목을 추가하고 보유 금액 또는 수량을 입력하세요. 그래야 현재 가치와 원가를 비교할 수 있습니다."
        )
    elif gain_loss["unrealized_gain"] is None:
        portfolio_status = "Needs purchase prices" if language == "en" else "매입가 필요"
        portfolio_advice = (
            "Enter average purchase price for each holding to unlock personal unrealized P/L and return analysis."
            if language == "en"
            else "각 종목의 평균 매입가를 입력하면 개인 기준 손익과 수익률을 볼 수 있습니다."
        )
    else:
        portfolio_status = (
            f"{fmt_signed_money(gain_loss['unrealized_gain'], base_currency)} "
            f"({float(gain_loss['unrealized_return_pct']):+.1f}%)"
        )
        if float(gain_loss["unrealized_gain"]) >= 0:
            portfolio_advice = (
                "Compare gains with concentration, beta, and cash-flow capacity before treating performance as readiness."
                if language == "en"
                else "수익이 있어도 집중도, 베타, 현금흐름 감당력을 함께 확인해야 합니다."
            )
        else:
            portfolio_advice = (
                "Separate market drawdown from life liquidity; review whether cash flow can absorb the current unrealized loss."
                if language == "en"
                else "시장 하락과 생활 유동성을 분리해서 보고, 현재 손실을 현금흐름이 감당할 수 있는지 확인하세요."
            )

    if personal:
        health = float(personal.get("financial_health_score") or 0)
        emergency = float(personal.get("emergency_months") or 0)
        surplus = float(personal.get("monthly_surplus") or 0)
        personal_status = f"Health {health:.1f}/100" if language == "en" else f"건강도 {health:.1f}/100"
        if emergency < 3:
            personal_advice = (
                "Emergency reserve is the first readiness checkpoint before adding investment risk."
                if language == "en"
                else "투자 위험을 늘리기 전에 비상자금이 먼저 확인되어야 합니다."
            )
        elif surplus <= 0:
            personal_advice = (
                "Monthly cash flow should be stabilized before using portfolio gains or losses as the main signal."
                if language == "en"
                else "포트폴리오 손익보다 월 현금흐름 안정성이 먼저입니다."
            )
        else:
            personal_advice = (
                "Use surplus, emergency reserve, and DTI together with portfolio P/L for investment readiness."
                if language == "en"
                else "잉여 현금, 비상자금, 부채 부담, 포트폴리오 손익을 함께 봐야 합니다."
            )
    else:
        personal_status = "Needs baseline" if language == "en" else "재무 기준 필요"
        personal_advice = (
            "Complete Personal Finance once so the coach can connect risk capacity with portfolio behavior."
            if language == "en"
            else "재무 정보를 한 번 입력하면 포트폴리오 위험을 감당할 수 있는지 연결해서 볼 수 있습니다."
        )

    if scenario:
        scenario_delta = float(scenario.get("portfolio", {}).get("scenario_delta_pct") or 0)
        scenario_status = (
            f"Latest scenario {scenario_delta:+.1f}%"
            if language == "en"
            else f"최근 시나리오 {scenario_delta:+.1f}%"
        )
        scenario_advice = (
            "Ask the coach to compare this stress result with emergency fund, P/L, and current portfolio exposure."
            if language == "en"
            else "이 스트레스 결과를 비상자금, 손익, 현재 포트폴리오 노출과 함께 비교해 보세요."
        )
    else:
        scenario_status = "Needs scenario" if language == "en" else "시나리오 필요"
        scenario_advice = (
            "Run one what-if scenario so the coach can reason about downside, FX, rate, income, and expense shocks."
            if language == "en"
            else "하락장, 환율, 금리, 소득, 지출 충격을 함께 보려면 시나리오를 한 번 실행하세요."
        )

    diary_status = (
        f"{len(diary)} saved entr{'y' if len(diary) == 1 else 'ies'}"
        if language == "en"
        else f"{len(diary)}개 기록"
    )
    if diary:
        diary_advice = (
            "Use diary memory to compare today's decision context with prior notes and next actions."
            if language == "en"
            else "오늘의 판단을 이전 메모와 다음 행동 기록과 비교해 보세요."
        )
    else:
        diary_advice = (
            "Save the Current Situation Report so the coach has a memory checkpoint for future review."
            if language == "en"
            else "현재 상황 리포트를 저장하면 이후 판단을 비교할 기준점이 생깁니다."
        )

    details_status = "Formulas ready" if language == "en" else "공식 확인 가능"
    details_advice = (
        "Open Calculation Details when you need the formula, assumption, or limit behind a coach answer."
        if language == "en"
        else "AI Coach 답변의 공식, 가정, 한계가 궁금하면 계산 근거를 열어 확인하세요."
    )

    if language == "ko":
        return [
            {
                "title": "포트폴리오 손익",
                "view": "portfolio",
                "status": portfolio_status,
                "advice": portfolio_advice,
                "question": "내 포트폴리오 원가, 미실현 손익, 현재 가치, 위험 지표를 연결해서 투자 준비도를 설명해 주세요.",
            },
            {
                "title": "재무 상태",
                "view": "finance",
                "status": personal_status,
                "advice": personal_advice,
                "question": "내 재무 기준과 포트폴리오 위험을 연결해서 가장 중요한 준비도 이슈를 알려 주세요.",
            },
            {
                "title": "시나리오 스트레스",
                "view": "scenario",
                "status": scenario_status,
                "advice": scenario_advice,
                "question": "최근 시나리오를 바탕으로 가장 안전한 다음 검토 단계를 설명해 주세요.",
            },
            {
                "title": "다이어리 리포트",
                "view": "diary",
                "status": diary_status,
                "advice": diary_advice,
                "question": "현재 상황 리포트와 다이어리 기록을 사용해 다음에 검토할 내용을 요약해 주세요.",
            },
            {
                "title": "계산 근거",
                "view": "details",
                "status": details_status,
                "advice": details_advice,
                "question": "현재 포트폴리오 손익, 준비도, 위험 신호 뒤의 공식과 가정을 설명해 주세요.",
            },
        ]

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
            "Educational financial reasoning context for LY-Scope-Ver.2 AI Coach. "
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
You are the LY-Scope-Ver.2 Verified AI Model Layer.
Your job is educational financial reasoning, not financial advice.

Rules:
- Do not give buy, sell, hold, short, long, or target-price instructions.
- Do not guarantee returns or predict certainty.
- Do not provide legal, tax, accounting, immigration, or professional advice.
- If the user asks about F-1, work authorization, monetization, or company formation, give only general caution and tell them to consult the DSO and qualified counsel.
- Ground every answer in the provided LY-Scope-Ver.2 context.
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
                        "ly_scope_ver2_context": model_context,
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
                "name": "ly_scope_ver2_verified_ai_response",
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
    language = current_language()
    if language == "ko":
        st.subheader("연결된 근거 카드")
        st.caption(
            "포트폴리오, 재무 상태, 시나리오, 다이어리, 계산 근거에서 만든 카드입니다. "
            "원본 화면을 열거나 이 맥락 그대로 AI Coach에게 물어볼 수 있습니다."
        )
        eyebrow_text = "연결 근거"
        open_text = "열기"
        ask_text = "질문하기"
    else:
        st.subheader("Linked Coach Guidance")
        st.caption(
            "These cards are generated from Portfolio, Personal Finance, Scenario, Diary, and Calculation Details. "
            "Open the source view or ask AI Coach with that exact context."
        )
        eyebrow_text = "Linked source"
        open_text = "Open"
        ask_text = "Ask Coach"
    pending_question = None
    linked_items = build_ai_coach_linked_guidance(context, readiness)
    for start in range(0, len(linked_items), 2):
        cols = st.columns(2, gap="medium")
        for idx, item in enumerate(linked_items[start : start + 2], start=start):
            with cols[idx - start]:
                st.markdown(
                    f"""
                    <div class="linked-coach-card">
                        <div class="eyebrow">{escape(eyebrow_text)}</div>
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
                        open_text,
                        key=f"linked_open_{item['view']}_{idx}",
                        width="stretch",
                        on_click=set_active_nav_key,
                        args=(item["view"],),
                    )
                with ask_col:
                    if st.button(ask_text, key=f"linked_ask_{item['view']}_{idx}", width="stretch"):
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
    language = current_language()
    context = ai_coach_context_snapshot()
    readiness = ai_coach_readiness(context)
    portfolio = context["portfolio"]
    personal = context["personal"]
    diary = context["diary"]
    score = readiness["score"]
    label = readiness["label"]
    missing_text = "Missing" if language == "en" else "입력 필요"
    readiness_label = {
        "Data Needed": "입력 필요",
        "Prepared": "준비됨",
        "Developing": "형성 중",
        "Caution": "주의",
        "Fragile": "취약",
    }.get(label, label) if language == "ko" else label
    health_text = (
        f"{float(personal.get('financial_health_score') or 0):.1f}/100"
        if personal
        else missing_text
    )
    portfolio_text = (
        fmt_money(portfolio["total_value"], portfolio["base_currency"])
        if portfolio["holdings"]
        else missing_text
    )
    hero_copy = (
        "Ask one focused question. NORA reads the goal, situation, evidence, risk, and memory together."
        if language == "en"
        else "한 가지 질문을 입력하세요. NORA가 목표, 상황, 근거, 위험, 메모리를 함께 읽습니다."
    )
    readiness_label_text = "Readiness" if language == "en" else "준비도"
    finance_label_text = "Personal finance" if language == "en" else "재무 상태"
    portfolio_label_text = "Portfolio context" if language == "en" else "포트폴리오"
    diary_label_text = "Diary memories" if language == "en" else "기록"
    disclaimer_text = (
        "Educational reasoning only. NORA answers from visible app context and does not give professional advice."
        if language == "en"
        else "교육용 해석입니다. NORA는 화면의 앱 맥락을 바탕으로 답하며 전문 조언을 제공하지 않습니다."
    )

    st.markdown(
        f"""
        <div class="ai-coach-hero">
            <h1>{ui_html('AI Coach')}</h1>
            <p>{escape(hero_copy)}</p>
            <div class="ai-coach-strip">
                <div class="ai-coach-signal"><b>{escape(readiness_label)}</b><span>{escape(readiness_label_text)} {score:.0f}/100</span></div>
                <div class="ai-coach-signal"><b>{escape(health_text)}</b><span>{escape(finance_label_text)}</span></div>
                <div class="ai-coach-signal"><b>{escape(portfolio_text)}</b><span>{escape(portfolio_label_text)}</span></div>
                <div class="ai-coach-signal"><b>{len(diary)}</b><span>{escape(diary_label_text)}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="coach-disclaimer">
            {escape(disclaimer_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_mobile_ai_coach_deck(context, readiness)

    settings_title = "Verified AI Model Settings" if language == "en" else "AI 모델 설정"
    with st.expander(settings_title, expanded=False):
        if OPENAI_API_KEY:
            if language == "ko":
                st.success(f"OPENAI_API_KEY가 설정되어 있습니다. 모델: {OPENAI_MODEL}.")
            else:
                st.success(f"OPENAI_API_KEY is configured. Model: {OPENAI_MODEL}.")
        else:
            if language == "ko":
                st.warning(
                    "OPENAI_API_KEY가 설정되어 있지 않아 AI Coach는 로컬 규칙 기반 답변을 사용합니다. "
                    "검증된 모델 답변을 사용하려면 Streamlit Secrets에 키를 추가하세요."
                )
            else:
                st.warning(
                    "OPENAI_API_KEY is not configured, so AI Coach will use the local rule-based answer. "
                    "Add OPENAI_API_KEY in Streamlit Secrets to enable verified model responses."
                )
        st.toggle(
            "Use verified OpenAI reasoning model" if language == "en" else "검증된 OpenAI 추론 모델 사용",
            key="use_verified_ai_model",
            disabled=not bool(OPENAI_API_KEY),
            help=(
                "When enabled, structured app context is sent to OpenAI's Responses API and then validated locally before display."
                if language == "en"
                else "켜면 구조화된 앱 맥락을 OpenAI Responses API로 보내고, 표시 전 로컬 검증을 거칩니다."
            ),
        )
        st.checkbox(
            "Include diary note text in model context" if language == "en" else "다이어리 메모를 모델 맥락에 포함",
            key="include_diary_text_for_ai",
            disabled=not bool(OPENAI_API_KEY) or not st.session_state.get("use_verified_ai_model", False),
            help=(
                "Leave off to send only diary count, mood, and next-action summaries."
                if language == "en"
                else "끄면 다이어리 개수, 기분, 다음 행동 요약만 보냅니다."
            ),
        )
        st.caption(
            "Privacy note: do not enter bank account numbers, tax IDs, passwords, or confidential records. "
            "Use this public prototype with minimal, non-sensitive examples."
            if language == "en"
            else "개인정보 주의: 계좌번호, 세금번호, 비밀번호, 민감한 금융 기록은 입력하지 마세요. 공개 프로토타입에서는 최소한의 비민감 예시만 사용하세요."
        )

    pending_question = st.session_state.get("pending_ai_question")
    if pending_question:
        st.session_state.pending_ai_question = None

    if not st.session_state.ai_coach_messages:
        initial_message = (
            "I am ready to review investment readiness, portfolio risk, scenario stress, and diary memory. "
            "Use the linked cards below, start with a quick question, or type your own."
            if language == "en"
            else "투자 준비도, 포트폴리오 위험, 시나리오 스트레스, 다이어리 기록을 함께 검토할 수 있습니다. 아래 카드나 빠른 질문으로 시작하세요."
        )
        st.session_state.ai_coach_messages.append(
            {
                "role": "assistant",
                "content": initial_message,
            }
        )

    linked_question = render_ai_coach_linked_guidance(context, readiness)
    if linked_question:
        pending_question = linked_question

    st.subheader("Quick Questions" if language == "en" else "빠른 질문")
    quick_questions = (
        [
            "Am I investment ready?",
            "Explain my biggest risk.",
            "What happens in my latest scenario?",
            "What should I track next?",
            "Summarize my diary memory.",
            "What privacy or F-1 caution matters?",
        ]
        if language == "en"
        else [
            "지금 투자 준비가 되었나요?",
            "가장 큰 위험은 무엇인가요?",
            "최근 시나리오에서는 어떤 일이 생기나요?",
            "다음에 무엇을 추적해야 하나요?",
            "다이어리 기록을 요약해 주세요.",
            "개인정보나 F-1 관련 주의점은 무엇인가요?",
        ]
    )
    quick_cols = st.columns(2)
    for idx, question in enumerate(quick_questions):
        with quick_cols[idx % 2]:
            if st.button(question, key=f"ai_quick_{idx}", width="stretch"):
                pending_question = question

    chat_placeholder = (
        "Ask about readiness, risk, scenario, or memory"
        if language == "en"
        else "준비도, 위험, 시나리오, 메모리에 대해 물어보세요"
    )
    typed_question = st.chat_input(chat_placeholder)
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
        if st.button("Reset AI Coach Chat" if language == "en" else "대화 초기화", width="stretch"):
            st.session_state.ai_coach_messages = []
            st.rerun()
    with save_col:
        if st.button("Save AI Summary to Diary" if language == "en" else "AI 요약을 다이어리에 저장", width="stretch"):
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
                st.success(
                    "AI Coach summary saved to Financial Diary memory for this session."
                    if language == "en"
                    else "AI Coach 요약이 이번 세션의 금융 다이어리에 저장되었습니다."
                )

    st.subheader("Conversation" if language == "en" else "대화")
    for message in st.session_state.ai_coach_messages[-8:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def ai_reasoning_readiness_tab() -> None:
    render_ai_coach()

    with st.expander("AI Reasoning Product Thesis" if current_language() == "en" else "AI 추론 제품 논리", expanded=False):
        st.write(
            """
            AI interfaces are moving toward voice, agents, and continuous assistance. A future user may ask:
            "Can I absorb this risk?", "What changes if rates rise?", or "What did I decide last time?"
            LY-Scope-Ver.2 prepares the structured context needed to answer those questions responsibly.
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
            <div class="hero-muted">Review the formulas, data inputs, assumptions, and interpretation logic behind LY-Scope-Ver.2.</div>
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
            - **CAPM Required Return:** `Risk-Free Rate + Beta x Equity Risk Premium`.
            - **Risk-Free Rate Basis:** the app uses the U.S. 10-Year Treasury yield when available, with manual override in Settings.
            - **Valuation Status:** if current price is more than 5% above fair value, it is marked Overvalued; if more than 5% below, Undervalued.
            """
        )
        macro = macro_assumption_details()
        basis_cols = st.columns(3)
        with basis_cols[0]:
            metric_card(ui("Risk-Free Rate"), f"{float(macro['risk_free_rate_pct']):.2f}%")
        with basis_cols[1]:
            metric_card(ui("Equity Risk Premium"), f"{float(macro['equity_risk_premium_pct']):.2f}%")
        with basis_cols[2]:
            metric_card(ui("U.S. 10Y Treasury Yield"), str(macro.get("risk_free_rate_mode") or "Manual"))
        st.caption(
            f"{ui('Risk-Free Rate Source')}: {macro.get('risk_free_rate_source') or 'Unavailable'} | "
            f"{ui('Risk-Free Rate Date')}: {macro.get('risk_free_rate_date') or 'N/A'}"
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
                    {"Input": "Risk-Free Rate Source", "Value": str(stock.get("risk_free_rate_source") or macro_assumption_details().get("risk_free_rate_source"))},
                    {"Input": "Risk-Free Rate Date", "Value": str(stock.get("risk_free_rate_date") or macro_assumption_details().get("risk_free_rate_date"))},
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
                    {"Approach": "Market", "Model": tri.get("market_model", "Peer P/E"), "Value": stock_money(stock, tri.get("market_value")) if tri.get("market_value") else "N/A"},
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
            LY-Scope-Ver.2 is being prepared for future AI-assisted financial reasoning. The app should not ask AI
            to make unsupported investment recommendations. Instead, each future AI response should be grounded
            in structured app data.

            **Reasoning context should include:**

            - Portfolio holdings, weights, valuation score, beta, covariance, and correlation.
            - Personal finance readiness: surplus, emergency fund, savings rate, debt-to-income, and health score.
            - Real estate value, rent support, cash flow, leverage, and interest-rate sensitivity.
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
        .advisor-scenario-board {
            display: grid;
            grid-template-columns: repeat(5, minmax(150px, 1fr));
            gap: 10px;
            margin: 16px 0 18px;
        }
        .advisor-scenario-card {
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.94);
            color: #0f172a !important;
            text-decoration: none !important;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
        }
        .advisor-scenario-card:hover,
        .advisor-scenario-card:focus,
        .advisor-scenario-card.active {
            border-color: rgba(14, 165, 233, 0.54);
            background: linear-gradient(135deg, #f0fdfa, #eff6ff);
        }
        .advisor-scenario-card.risk {
            border-color: rgba(239, 68, 68, 0.36);
        }
        .advisor-scenario-card.watch {
            border-color: rgba(245, 158, 11, 0.40);
        }
        .advisor-scenario-card b {
            display: block;
            font-size: 0.88rem;
            color: #0f172a;
            line-height: 1.15;
        }
        .advisor-scenario-card span {
            display: block;
            margin-top: 4px;
            color: #64748b;
            font-size: 0.72rem;
            line-height: 1.2;
        }
        .advisor-scenario-score {
            margin-top: 10px;
            height: 7px;
            border-radius: 999px;
            background: #e2e8f0;
            overflow: hidden;
        }
        .advisor-scenario-score i {
            display: block;
            height: 100%;
            width: var(--score);
            background: linear-gradient(90deg, #22c55e, #0ea5e9);
        }
        .advisor-scenario-pill {
            display: inline-flex !important;
            width: auto;
            margin-top: 9px !important;
            padding: 5px 8px;
            border-radius: 999px;
            color: #0f172a !important;
            background: #e0f2fe;
            font-weight: 900;
        }
        .advisor-scenario-card.risk .advisor-scenario-pill {
            background: #fee2e2;
            color: #991b1b !important;
        }
        .advisor-scenario-card.watch .advisor-scenario-pill {
            background: #fef3c7;
            color: #92400e !important;
        }
        .advisor-stress-review {
            display: grid;
            grid-template-columns: 1.1fr 1.8fr;
            gap: 12px;
            margin: 10px 0 18px;
        }
        .advisor-stress-verdict,
        .advisor-stress-points {
            border-radius: 8px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background: rgba(255, 255, 255, 0.94);
            padding: 14px;
        }
        .advisor-stress-verdict b {
            display: block;
            color: #0f172a;
            font-size: 1rem;
        }
        .advisor-stress-verdict strong {
            display: inline-flex;
            margin: 8px 0;
            padding: 6px 10px;
            border-radius: 999px;
            background: #e0f2fe;
            color: #075985;
        }
        .advisor-stress-verdict.risk strong {
            background: #fee2e2;
            color: #991b1b;
        }
        .advisor-stress-verdict.watch strong {
            background: #fef3c7;
            color: #92400e;
        }
        .advisor-stress-verdict p {
            margin: 0;
            color: #475569;
            line-height: 1.42;
            font-size: 0.9rem;
        }
        .advisor-stress-points {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
        }
        .advisor-stress-point {
            border-radius: 8px;
            background: #f8fafc;
            padding: 10px;
            border: 1px solid rgba(226, 232, 240, 0.9);
        }
        .advisor-stress-point span {
            color: #64748b;
            font-size: 0.72rem;
            font-weight: 850;
        }
        .advisor-stress-point b {
            display: block;
            margin-top: 4px;
            color: #0f172a;
            font-size: 0.92rem;
        }
        @media (max-width: 900px) {
            .advisor-report-grid {
                grid-template-columns: 1fr;
            }
            .advisor-scenario-board,
            .advisor-stress-review,
            .advisor-stress-points {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def advisor_money_compact(value: float, currency: str, language: str) -> str:
    amount = float(value)
    if currency == "KRW":
        if abs(amount) >= 100_000_000:
            return f"{amount / 100_000_000:.1f}억"
        if abs(amount) >= 10_000:
            return f"{amount / 10_000:.0f}만"
        return f"{amount:,.0f}원"
    if abs(amount) >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    return f"${amount / 1_000:.0f}k" if abs(amount) >= 1_000 else f"${amount:,.0f}"


def advisor_client_href(client_id: str) -> str:
    params = {"view": "advisor", "mode": "dashboard", "client": client_id}
    params.update(language_params())
    params.update(active_goal_params())
    params.update(selection_state_params())
    return f"?{urlencode(params)}"


def advisor_scenario_review(report: dict[str, Any], language: str) -> dict[str, Any]:
    result = report["result"]
    client = report["client"]
    stress_rows = report["stress"]
    base_capital = float(stress_rows[0]["Capital"])
    stress_20 = float(stress_rows[1]["Capital"])
    stress_30 = float(stress_rows[2]["Capital"])
    stress_40 = float(stress_rows[3]["Capital"])
    stress_loss = base_capital - stress_40
    stress_loss_pct = 0.0 if base_capital == 0 else stress_loss / abs(base_capital)
    runway = float(result["emergency_months"])
    required = float(result["required_runway_months"])
    weakest_score = float(report["weakest_signal"]["score"])
    no_income = bool(result.get("no_income_mode"))
    monthly_surplus_negative = float(result["monthly_surplus"]) < 0
    runway_gap = runway < required

    if stress_40 <= 0 or report.get("status_key") == "at_risk" or (monthly_surplus_negative and (not no_income or runway_gap)):
        tone = "risk"
        verdict = "At Risk" if language == "en" else "위험"
        summary = (
            "The stress case threatens the financial base. Protection, debt, or liquidity repair should come before growth."
            if language == "en"
            else "스트레스 상황에서 재정 기반이 크게 흔들립니다. 성장보다 보호, 부채, 유동성 점검이 먼저입니다."
        )
    elif runway < required or weakest_score < 55 or stress_loss_pct >= 0.32:
        tone = "watch"
        verdict = "Watch" if language == "en" else "주의"
        summary = (
            "The client can survive the stress case, but the weakest signal should drive the next review."
            if language == "en"
            else "스트레스는 견딜 수 있지만 약한 신호가 분명합니다. 다음 검토는 가장 낮은 준비 신호에 집중해야 합니다."
        )
    else:
        tone = "stable"
        verdict = "Stable" if language == "en" else "안정"
        summary = (
            "The stress case remains usable. Continue scenario review and keep concentration limits visible."
            if language == "en"
            else "스트레스 이후에도 구조는 사용 가능합니다. 다만 시나리오 점검과 집중도 한도는 계속 보여야 합니다."
        )

    return {
        "tone": tone,
        "verdict": verdict,
        "summary": summary,
        "base": base_capital,
        "stress_20": stress_20,
        "stress_30": stress_30,
        "stress_40": stress_40,
        "stress_loss_pct": stress_loss_pct,
        "runway": runway,
        "required": required,
        "weakest": report["weakest_signal"]["label"],
        "weakest_score": weakest_score,
        "currency": client.currency,
    }


def render_advisor_scenario_board(reports: list[dict[str, Any]], selected_id: str, language: str) -> None:
    title = "Client Scenario Board" if language == "en" else "고객 시나리오 보드"
    caption = (
        "Pick a client, then read the stress verdict before opening the full report."
        if language == "en"
        else "고객을 선택한 뒤, 전체 리포트보다 먼저 스트레스 판정을 확인하세요."
    )
    cards: list[str] = []
    for report in reports:
        client = report["client"]
        result = report["result"]
        review = advisor_scenario_review(report, language)
        score = max(0.0, min(100.0, float(result["planning_health_score"])))
        active_class = " active" if client.client_id == selected_id else ""
        cards.append(
            f'<a class="advisor-scenario-card {escape(review["tone"])}{active_class}" '
            f'href="{escape(advisor_client_href(client.client_id), quote=True)}" target="_self">'
            f'<b>{escape(client.client_id)} · {escape(client.name.split()[0])}</b>'
            f'<span>{escape(client.text("segment", language))}</span>'
            f'<span class="advisor-scenario-pill">{escape(review["verdict"])}</span>'
            f'<div class="advisor-scenario-score"><i style="--score: {score:.0f}%;"></i></div>'
            f'<span>{escape(advisor_money_compact(review["stress_40"], client.currency, language))} @ -40%</span>'
            '</a>'
        )

    st.markdown(f"### {escape(title)}")
    st.caption(caption)
    st.markdown(
        f'<div class="advisor-scenario-board">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_selected_client_stress_review(report: dict[str, Any], language: str) -> None:
    review = advisor_scenario_review(report, language)
    labels = (
        ["Base", "-20%", "-30%", "-40%"]
        if language == "en"
        else ["기준", "-20%", "-30%", "-40%"]
    )
    values = [review["base"], review["stress_20"], review["stress_30"], review["stress_40"]]
    point_cards = "".join(
        f'<div class="advisor-stress-point"><span>{escape(label_text)}</span>'
        f'<b>{escape(advisor_money_compact(value, review["currency"], language))}</b></div>'
        for label_text, value in zip(labels, values)
    )
    title = "Scenario Verdict" if language == "en" else "시나리오 판정"
    loss_label = "Stress loss" if language == "en" else "스트레스 손실"
    weakest_label = "Weakest signal" if language == "en" else "가장 약한 신호"
    runway_label = "Runway" if language == "en" else "생존기간"
    month_unit = "mo" if language == "en" else "개월"
    st.markdown(
        f"""
        <section class="advisor-stress-review">
            <div class="advisor-stress-verdict {escape(review['tone'])}">
                <b>{escape(title)}</b>
                <strong>{escape(review['verdict'])}</strong>
                <p>{escape(review['summary'])}</p>
                <p>{escape(loss_label)}: {float(review['stress_loss_pct']) * 100:.1f}% · {escape(weakest_label)}: {escape(str(review['weakest']))} · {escape(runway_label)}: {float(review['runway']):.1f}/{float(review['required']):.1f}{escape(month_unit)}</p>
            </div>
            <div class="advisor-stress-points">{point_cards}</div>
        </section>
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
    client_ids = list(report_map.keys())
    requested_client_id = query_param_value("client")
    session_client_id = st.session_state.get("advisor_selected_client_id", client_ids[0])
    default_client_id = requested_client_id if requested_client_id in report_map else session_client_id
    if default_client_id not in report_map:
        default_client_id = client_ids[0]
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
            ui_html("Review virtual clients through the LY-Scope-Ver.2 decision architecture and export PDF reports."),
        ),
        unsafe_allow_html=True,
    )
    st.caption(
        ui("These fictional reports use the existing Personal Finance engine plus a rule-based advisor layer. They are educational examples, not professional advice.")
    )
    render_advisor_scenario_board(reports, default_client_id, advisor_language)

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
        options=client_ids,
        index=client_ids.index(default_client_id),
        format_func=lambda value: f"{value} - {report_map[value]['client'].name} | {report_map[value]['client'].text('segment', advisor_language)}",
        key=f"advisor_selected_client_select_{default_client_id}",
    )
    st.session_state.advisor_selected_client_id = selected_id
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
    render_selected_client_stress_review(report, advisor_language)
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
                {advisor_label("layer", advisor_language): advisor_label("customer_purpose", advisor_language), advisor_label("reading", advisor_language): client.text("goal", advisor_language)},
                {advisor_label("layer", advisor_language): advisor_label("strategy", advisor_language), advisor_label("reading", advisor_language): client.text("advisor_focus", advisor_language)},
                {advisor_label("layer", advisor_language): advisor_label("situation", advisor_language), advisor_label("reading", advisor_language): client.text("situation", advisor_language)},
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
            file_name=f"ly_scope_ver2_advisor_report_{client.client_id.lower()}.pdf",
            mime="application/pdf",
            width="stretch",
            disabled=selected_pdf is None,
        )
    with button_cols[1]:
        st.download_button(
            ui("Download All Client Reports PDF"),
            data=all_pdf or b"",
            file_name=f"ly_scope_ver2_advisor_reports_{datetime.now().strftime('%Y%m%d')}.pdf",
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
        f"LY-Scope-Ver.2 Current Situation Report - {now_text}",
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
            "LY-Scope-Ver.2 Current Situation Report",
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
            file_name=f"ly_scope_ver2_current_situation_{datetime.now().strftime('%Y%m%d')}.pdf",
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
            file_name=f"ly_scope_ver2_financial_diary_{datetime.now().strftime('%Y%m%d')}.json",
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
        f"""
        <div class="portfolio-title-strip">
            <b>{ui_html('Investment Portfolio')}</b>
            <span>{ui_html('Risk, return, and valuation across holdings')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_portfolio_stock_search()

    fx_col1, fx_col2, fx_col3 = st.columns(3)
    with fx_col1:
        st.selectbox(
            ui("Portfolio base currency"),
            ["USD", "KRW"],
            key="portfolio_base_currency",
            help="Portfolio totals and weights are calculated after converting each holding into this currency.",
        )
    with fx_col2:
        st.checkbox(
            ui("Use live USD/KRW"),
            key="use_live_fx",
            help="Uses Yahoo Finance KRW=X when available. Manual rate is used as fallback.",
        )
    with fx_col3:
        st.number_input(
            ui("Manual USD/KRW rate"),
            min_value=1.0,
            step=1.0,
            key="manual_usdkrw",
        )

    usdkrw, fx_source, fx_date = effective_usdkrw()
    if current_language() == "ko":
        fx_source_text = "수동 입력" if fx_source == "Manual fallback" else fx_source
        fx_date_text = "사용자 입력" if fx_date == "User input" else fx_date
        st.caption(
            f"환율 기준: 1 USD = ₩{usdkrw:,.2f} | 출처: {fx_source_text} | 날짜: {fx_date_text}. "
            "포트폴리오 비중은 기준 통화로 환산해 계산합니다."
        )
    else:
        st.caption(
            f"FX setting: 1 USD = ₩{usdkrw:,.2f} | Source: {fx_source} | Date: {fx_date}. "
            "Portfolio weights use converted base-currency values."
        )

    st.radio(
        ui("Portfolio weighting mode"),
        ["Share-based", "Equal-weighted"],
        horizontal=True,
        key="portfolio_weighting_mode",
        format_func=ui,
        help=(
            "Share-based uses shares x current price. Equal-weighted assigns the same analysis weight "
            "to each holding, which is useful for classroom portfolio analysis."
        ),
    )
    if st.session_state.portfolio_weighting_mode == "Equal-weighted":
        if current_language() == "ko":
            st.info(
                "동일 비중은 각 종목을 같은 무게로 분석합니다. 학습용 비교에는 좋지만, 실제 운용에서는 주기적 리밸런싱이 필요하고 비용과 세금이 성과를 낮출 수 있습니다."
            )
        else:
            st.info(
                "Equal weighting assigns the same analysis weight to each selected security. "
                "This is useful for classroom analysis and simple backtesting concepts, but maintaining "
                "equal weights in practice requires periodic rebalancing. Trading costs and taxes may reduce actual performance."
            )
    else:
        if current_language() == "ko":
            st.caption(
                "보유 수량 기준은 각 종목의 현재 시장가치로 비중을 계산합니다. 보유 금액이 큰 종목이 포트폴리오 판단을 더 크게 움직입니다."
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
        metric_card(ui("Total Market Value"), fmt_money(total_value, st.session_state.portfolio_base_currency))
    with c2:
        metric_card(ui("Weighted Beta"), fmt_number(weighted_beta))
    with c3:
        metric_card(ui("Portfolio Valuation Score"), score_text, score_color)

    with st.expander(ui("Portfolio valuation basis"), expanded=False):
        macro = macro_assumption_details()
        st.caption(
            "Valuation Score estimates the portfolio's weighted upside or downside versus each stock's blended fair value. "
            "Formula: sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight. "
            "Positive means undervalued; negative means overvalued. Holdings without valid fair value are excluded. "
            f"Current analysis mode: {st.session_state.portfolio_weighting_mode}."
        )
        st.caption(
            f"Risk-free rate basis: {float(macro['risk_free_rate_pct']):.2f}% "
            f"({macro['risk_free_rate_source']}, {macro['risk_free_rate_date']})."
        )

    render_quick_portfolio_entry()

    if not st.session_state.portfolio:
        render_mobile_portfolio_deck([], total_value, weighted_beta, valuation_score, 0, None, None)
        st.info(ui("No stocks in your portfolio yet. Add them from the search results."))
        st.button(
            ui("Ask AI Coach About Portfolio Setup"),
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
            f"{ui('Native currency breakdown')}: "
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
                f"{symbol} {ui('shares')}",
                min_value=0.0,
                value=float(holding.get("shares") or 0),
                step=1.0,
                key=f"shares_{symbol}",
            )
        with input_cols[1]:
            purchase_step = 100.0 if currency == "KRW" else 1.0
            purchase_price = st.number_input(
                f"{symbol} {ui('average purchase price')} ({currency})",
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
        st.info(ui("Enter each holding's average purchase price to compare your cost basis with current market value."))

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
        ui("Ask AI Coach About Portfolio P/L"),
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
            f"{ui('Remove')} {symbol}",
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
        "and survivorship-bias controls. LY-Scope-Ver.2 currently focuses on educational portfolio analytics rather than full performance backtesting."
    )
    st.caption(
        "Reference suggested for advanced analysis: Portfolio Visualizer. LY-Scope-Ver.2 can use it as a methodological benchmark while keeping this app focused on learning and interpretation."
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
        "The app uses the U.S. 10-Year Treasury yield as the default risk-free rate when available. "
        "Users can switch to a manual assumption, and updated values are reflected in CAPM required return and valuation calculations."
    )

    treasury = load_us10y_treasury_rate()
    treasury_rate = treasury.get("rate_pct")
    treasury_cols = st.columns([1, 1.4])
    with treasury_cols[0]:
        metric_card(
            ui("U.S. 10Y Treasury Yield"),
            f"{float(treasury_rate):.2f}%" if treasury_rate else ui("Rate unavailable"),
        )
    with treasury_cols[1]:
        st.caption(
            f"Source: {treasury.get('source') or 'Unavailable'} | "
            f"Date: {treasury.get('date') or 'N/A'}"
        )
        if st.button(ui("Refresh U.S. 10Y Treasury yield"), width="stretch"):
            load_us10y_treasury_rate.clear()
            recalculated = recalculate_loaded_stocks()
            st.session_state["treasury_refresh_notice"] = (
                f"U.S. 10Y Treasury yield refreshed. {recalculated} loaded stock(s) were recalculated."
                if recalculated
                else "U.S. 10Y Treasury yield refreshed."
            )
            st.rerun()

    refresh_notice = st.session_state.pop("treasury_refresh_notice", "")
    if refresh_notice:
        st.success(refresh_notice)

    st.checkbox(
        ui("Use U.S. 10Y Treasury yield as Risk-Free Rate"),
        key="use_live_us10y",
        disabled=not bool(treasury_rate),
        help="Uses FRED DGS10 first, then Yahoo Finance ^TNX fallback if FRED is unavailable.",
    )

    if st.button("Reset manual macro assumptions to 4.50%", width="stretch"):
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

    macro = macro_assumption_details()
    use_live_risk_free = bool(st.session_state.get("use_live_us10y", True) and treasury_rate)
    with st.form("macro_assumptions_form"):
        macro_cols = st.columns(2)
        with macro_cols[0]:
            risk_free_pct_text = st.text_input(
                "Risk-Free Rate (%)",
                value=f"{float(macro['risk_free_rate_pct']):.2f}",
                help="Used as the base rate in CAPM. Disable the U.S. 10Y toggle to enter a manual percent value.",
                disabled=use_live_risk_free,
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
            risk_free_pct = (
                float(macro_assumption_details()["risk_free_rate_pct"])
                if use_live_risk_free
                else float(str(risk_free_pct_text).strip().replace("%", ""))
            )
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
    macro = macro_assumption_details()
    st.info(
        f"Current CAPM assumption: Required Return = {risk_free_rate * 100:.2f}% "
        f"+ Beta x {equity_risk_premium * 100:.2f}%. "
        f"Risk-free source: {macro['risk_free_rate_source']} ({macro['risk_free_rate_date']})."
    )


def guide_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">LY-Scope-Ver.2 User Guide</h1>
            <div class="hero-muted">A practical in-app guide based on the English PDF user guide.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if GUIDE_PDF_PATH.exists():
        st.download_button(
            "Download PDF User Guide",
            data=GUIDE_PDF_PATH.read_bytes(),
            file_name="LY-Scope-Ver.2_User_Guide.pdf",
            mime="application/pdf",
            width="stretch",
        )
    else:
        st.info("Upload LY-Scope-Ver.2_User_Guide.pdf to the repository to enable PDF download.")

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
        - Rebalancing can create transaction costs and taxes, so LY-Scope-Ver.2 presents this as educational analysis rather than a full professional backtest.
        """
    )

    st.subheader("6. Educational Scope")
    st.write(
        """
        LY-Scope-Ver.2 is designed to connect finance theory with real market examples. It is not an
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
        The AI Coach menu turns LY-Scope-Ver.2 from a dashboard into a conversation-first financial reasoning
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
        - Risk-Free Rate defaults to the U.S. 10-Year Treasury yield when available; users can switch to a manual CAPM input in Settings.
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
        - LY-Scope-Ver.2 is an educational prototype, not financial, investment, tax, legal, accounting, or professional advice.
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


def sidebar_focus_href(view: str, focus: str, goal: str | None = None) -> str:
    params = {"view": view, "mode": "dashboard", "focus": focus}
    params.update(language_params())
    if goal:
        params["goal"] = goal
    else:
        params.update(active_goal_params())
    params.update(selection_state_params())
    return f"?{urlencode(params)}"


def render_sidebar_path_menu() -> None:
    language = current_language()
    active_view = active_nav_key()
    active_focus = query_param_value("focus")
    goal = active_goal_key()

    if goal:
        goal_config = NORA_GOAL_STRATEGIES[goal]
        goal_label = goal_config[f"label_{language}"]
        goal_short = goal_config[f"short_{language}"]
        strategy_view = goal_config["view"]
        strategy_caption = goal_short
        strategy_goal = goal
        goal_note = f"{ui('Selected goal')}: {goal_label} · {goal_short}"
    else:
        strategy_view = "life"
        strategy_caption = ui("Choose a goal to set strategy.")
        strategy_goal = None
        goal_note = f"{ui('No goal selected')}. {ui('Choose a goal to set strategy.')}"

    strategy_active = (
        active_focus == "strategy"
        or (
            active_focus is None
            and goal is not None
            and active_view == strategy_view
            and strategy_view != "finance"
        )
    )
    situation_active = active_focus == "situation" or (
        active_focus is None and active_view == "finance"
    )

    path_items = [
        {
            "step": "01",
            "label": ui("Goal"),
            "caption": ui("Choose the customer purpose first."),
            "href": sidebar_focus_href("life", "goal"),
            "active": active_focus == "goal" or (active_focus is None and active_view == "life"),
        },
        {
            "step": "02",
            "label": ui("Strategy"),
            "caption": strategy_caption,
            "href": sidebar_focus_href(strategy_view, "strategy", strategy_goal),
            "active": strategy_active,
        },
        {
            "step": "03",
            "label": ui("Situation"),
            "caption": ui("Read cash flow, capital, risk, and runway."),
            "href": sidebar_focus_href("finance", "situation", goal),
            "active": situation_active,
        },
        {
            "step": "04",
            "label": ui("AI Coach"),
            "caption": ui("Ask for a linked interpretation."),
            "href": sidebar_focus_href("ai", "ai", goal),
            "active": active_focus == "ai" or active_view == "ai",
        },
    ]
    links = []
    for item in path_items:
        active_class = " active" if item["active"] else ""
        links.append(
            f'<a class="nora-sidebar-link{active_class}" href="{escape(item["href"], quote=True)}" target="_self">'
            f'<span class="nora-sidebar-step">{escape(item["step"])}</span>'
            f'<span><b>{escape(item["label"])}</b><span>{escape(item["caption"])}</span></span>'
            '</a>'
        )

    st.markdown(f"### {ui('NORA Path')}")
    st.caption(ui("Goal → Strategy → Situation → AI Coach"))
    st.markdown(
        f"""
        <div class="nora-sidebar-path">
            {''.join(links)}
        </div>
        <div class="nora-sidebar-goal">
            <b>{ui_html('Selected goal') if goal else ui_html('No goal selected')}</b>
            {escape(goal_note)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## LY-Scope-Ver.2")
        st.caption(ui("Open or close this sidebar with the arrow in the upper-left corner."))

        if st.button(ui("View Life Design Intro"), width="stretch"):
            st.session_state.life_entry_complete = False
            st.session_state.life_entry_version_seen = ""
            st.rerun()

        render_sidebar_path_menu()

        with st.expander(ui("Support Lists"), expanded=False):
            st.markdown(f"#### {ui('Selected stocks')}")
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

            st.markdown(f"#### {ui('Portfolio holdings')}")
            if st.session_state.portfolio:
                for symbol in list(st.session_state.portfolio.keys()):
                    stock = st.session_state.stocks.get(symbol, {"name": symbol})
                    shares = st.session_state.portfolio.get(symbol, {}).get("shares", 0)
                    key = f"sidebar_portfolio_{symbol}"
                    checked = st.checkbox(
                        f"{symbol} - {stock.get('name', symbol)} ({shares:g} {ui('shares')})",
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
        "LY-Scope-Ver.2 is provided for educational and informational use only and does not constitute or provide financial, investment, legal, tax, accounting, or professional advice. Do not enter sensitive personal financial information into this prototype. Market data and charts may be provided by third-party services such as Finnhub, TradingView, and Yahoo Finance/yfinance, subject to their own terms. All trademarks, company names, and ticker symbols remain the property of their respective owners. This interface uses original CSS/HTML design elements and does not claim ownership of third-party data, logos, or trademarks. Data may be delayed, incomplete, or unavailable and should be verified independently."
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
    # is safer until a LY-Scope-Ver.2-specific image is generated.
    homepage_bg = image_data_uri(str(HOMEPAGE_BG_PATH)) if USE_HOMEPAGE_REFERENCE_IMAGE else ""
    homepage_class = " has-home-image" if homepage_bg else ""
    homepage_image = (
        f'<img class="homepage-bg-img" src="{homepage_bg}" alt="LY-Scope-Ver.2 life design homepage preview">'
        if homepage_bg
        else ""
    )
    language = current_language()
    dashboard_href = escape(app_view_href("life"), quote=True)
    life_title = "목표를 <span>선택하세요</span>" if language == "ko" else 'Choose a <span>Goal</span>'
    life_copy = (
        "목표가 정해지면 전략이 달라집니다."
        if language == "ko"
        else "Choose the goal first. Strategy follows."
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
                        <div>LY-Scope-Ver.2 <small>Decision Intelligence</small></div>
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
    {"key": "advisor", "label": "Advisor", "icon": "AR"},
    {"key": "search", "label": "Search", "icon": "SR"},
    {"key": "compare", "label": "Compare", "icon": "CP"},
    {"key": "reit", "label": "Real Estate", "icon": "RE"},
    {"key": "details", "label": "Details", "icon": "DT"},
    {"key": "scenario", "label": "Scenario", "icon": "SC"},
    {"key": "ai", "label": "AI Coach", "icon": "AI"},
    {"key": "guide", "label": "Guide", "icon": "GD"},
    {"key": "settings", "label": "Settings", "icon": "SE"},
]

PRIMARY_NAV_KEYS = ("life", "finance", "portfolio", "reit", "scenario", "advisor")

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
        "glyph": "STG",
        "label": "Strategy",
        "tag": "Strategy path",
        "color": "#60a5fa",
        "detail_en": "The path that turns the goal into required capital, sequence, resources, and review rhythm.",
        "detail_ko": "목표를 필요한 자본, 실행 순서, 자원, 점검 리듬으로 바꾸는 경로.",
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
    ("Goal", "life"),
    ("Finance", "finance"),
    ("Portfolio / SR", "portfolio"),
    ("Real Estate", "reit"),
    ("Scenario", "scenario"),
    ("Advisor", "advisor"),
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
        <div class="nav-flow-strip" aria-label="LY-Scope-Ver.2 workflow map">
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
        if orbit_item["key"] not in PRIMARY_NAV_KEYS:
            continue
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
            '<div class="desktop-orbit-nav" aria-label="LY-Scope-Ver.2 compact orbit navigation">'
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
        {"key": "finance", "label": "Finance", "icon": "FI", "slot": "mobile-orbit-top-right"},
        {"key": "portfolio", "label": "Port", "icon": "PF", "slot": "mobile-orbit-right"},
        {"key": "reit", "label": "Real Estate", "icon": "RE", "slot": "mobile-orbit-bottom-right"},
        {"key": "scenario", "label": "Scenario", "icon": "SC", "slot": "mobile-orbit-bottom-left"},
        {"key": "advisor", "label": "Advisor", "icon": "AR", "slot": "mobile-orbit-left"},
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
    diary_href = escape(app_view_href("diary"), quote=True)
    st.markdown(
        (
            '<div class="mobile-orbit-nav mobile-only-deck" aria-label="Mobile LY-Scope-Ver.2 orbit navigation">'
            f'<div class="mobile-orbit-stamp">{ui_html("Goal-first mobile map")}</div>'
            '<div class="mobile-orbit-shell">'
            f'{"".join(orbit_links)}'
            f'<a class="mobile-orbit-center{center_active}" href="{diary_href}" target="_self" aria-label="{ui_html("Financial Diary")}">'
            f'<b>{ui_html("Diary")}</b><span>{ui_html("Personal Memory")}</span></a></div>'
            '</div>'
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
        "reit": "Real Estate",
        "details": "Calculation Details",
        "settings": "Settings",
        "guide": "Guide",
    }
    next_map = {
        "life": "Start with a goal, then Finance or Portfolio.",
        "finance": "Check surplus, reserve, debt, and savings.",
        "portfolio": "Enter shares and average purchase price.",
        "advisor": "Review virtual clients and export advisor PDF reports.",
        "ai": "Ask one focused question from your current data.",
        "diary": "Save one short next action after review.",
        "scenario": "Run one downside stress test.",
        "search": "Search a ticker, then add it to Portfolio.",
        "compare": "Compare up to three selected stocks.",
        "reit": "Review property value and rent cash flow first.",
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
                <div class="mobile-card"><div class="eyebrow">{ui_html('Now')}</div><div class="value">{ui_html(title_map.get(active_key, 'LY-Scope-Ver.2'))}</div><span class="label">{ui_html('Current screen')}</span></div>
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
        label = "Choose a Goal" if language == "en" else "목표 선택"
        short = "Strategy follows the goal." if language == "en" else "목표가 정해지면 전략이 달라집니다."
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


def render_rationality_gate() -> None:
    snapshot = rationality_gate_snapshot()
    score = max(0.0, min(100.0, float(snapshot["score"])))
    tone = rationality_tone(score)
    tone_color = {"good": "#0f766e", "mid": "#2563eb", "watch": "#d97706"}[tone]
    pillar_nodes = []
    detail_items = [
        f'<li><b>{ui_html("Rationality Gate")}</b><span>{ui_html("Rationality means goal-fit, evidence, model discipline, risk awareness, and memory before action.")}</span></li>'
    ]
    for item in snapshot["pillars"]:
        pillar_score = max(0.0, min(100.0, float(item["score"])))
        pillar_tone = rationality_tone(pillar_score)
        detail = str(item["detail"])
        pillar_nodes.append(
            f'<span class="rationality-node {pillar_tone}" tabindex="0" '
            f'title="{escape(ui(item["label"]) + ": " + detail, quote=True)}" '
            f'style="--value: {pillar_score:.0f}%;">'
            f'<b>{escape(str(item["glyph"]))}</b></span>'
        )
        detail_items.append(
            f'<li><b>{ui_html(item["label"])}</b><span>{escape(detail)}</span></li>'
        )

    st.markdown(
        f"""
        <section class="rationality-gate {tone}" style="--rational-color: {tone_color};" aria-label="{ui_html('Rationality Gate')}">
            <div class="rationality-gate-main">
                <b>{ui_html('Rationality Gate')}</b>
                <span>{ui_html('Purpose → Evidence → Risk → Memory')}</span>
            </div>
            <div class="rationality-score">
                <strong>{score:.0f}</strong><small>/100</small>
                <em>{ui_html(str(snapshot["label"]))}</em>
            </div>
            <div class="rationality-nodes">{"".join(pillar_nodes)}</div>
            <details class="rationality-detail">
                <summary>{ui_html('Detail')}</summary>
                <ul>{"".join(detail_items)}</ul>
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
    life_image = image_data_uri(str(HOMEPAGE_BG_PATH)) if USE_HOMEPAGE_REFERENCE_IMAGE else ""
    image_html = (
        f'<img class="life-client-image" src="{life_image}" alt="Customer life planning visual">'
        if life_image
        else ""
    )
    panel_class = "life-compact-panel client-life-panel" if life_image else "life-compact-panel"
    st.markdown(
        f"""
        <div class="{panel_class}">
            {image_html}
            <div class="life-compact-content">
                <h1>{escape(compact_title)}</h1>
                <p>
                    {escape(compact_copy)}
                </p>
                <div class="life-goal-board">
                    {"".join(cards)}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_main_app() -> None:
    sync_selection_state_from_query()
    sync_selected_detail_from_query()

    render_sidebar()

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
                    <div class="brand-name">LY-Scope<span class="scope-accent">-Ver.2</span></div>
                    <div class="brand-subtitle">{brand_subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    active_view = active_nav_key()
    render_goal_strategy_strip(active_view)
    render_rationality_gate()
    if active_view in {"life", "details"}:
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
        import reit_analysis_module

        render_reit_analysis = importlib.reload(reit_analysis_module).main
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

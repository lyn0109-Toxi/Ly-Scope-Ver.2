import math
import os
import json
import base64
import re
from html import escape
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import altair as alt
import pandas as pd
import requests
import streamlit as st
import yfinance as yf


st.set_page_config(page_title="LY-Scope-Ver.2", layout="wide", initial_sidebar_state="expanded")

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
    "Use the Menu button at the upper-left to open or close this sidebar.": "왼쪽 위 Menu 버튼으로 사이드바를 열거나 닫을 수 있습니다.",
    "View Life Design Intro": "Life Design 인트로 보기",
    "Ver.2 Module": "Ver.2 모듈",
    "Use the REIT Analysis tab in the main screen.": "메인 화면의 REIT Analysis 메뉴를 사용하세요.",
    "Compare List": "비교 목록",
    "No stocks selected for comparison.": "비교할 종목이 아직 없습니다.",
    "Portfolio List": "포트폴리오 목록",
    "No stocks in portfolio.": "포트폴리오에 담긴 종목이 없습니다.",
    "Developer": "개발자",
    "Feedback & Contact": "피드백 및 연락",
    "Google Feedback Form": "Google 피드백 폼",
    "Connect feedback to a Google Form.": "피드백을 Google Form으로 연결합니다.",
    "Google Form URL": "Google Form URL",
    "Paste Google Form URL for this session.": "이번 세션에서 사용할 Google Form URL을 붙여넣으세요.",
    "Connect Google Form": "Google Form 연결",
    "Open Google Feedback Form": "Google 피드백 폼 열기",
    "Google Form connection is ready.": "Google Form 연결이 준비되었습니다.",
    "Google Form is not connected yet.": "Google Form이 아직 연결되지 않았습니다.",
    "Add GOOGLE_FEEDBACK_FORM_URL in Streamlit secrets, or paste a Google Form URL here.": "Streamlit secrets에 GOOGLE_FEEDBACK_FORM_URL을 추가하거나 여기 Google Form URL을 붙여넣으세요.",
    "Use a Google Forms URL from docs.google.com/forms or forms.gle.": "docs.google.com/forms 또는 forms.gle 형식의 Google Forms URL을 사용하세요.",
    "The Google Form opens in a new tab. This app also keeps a local session copy.": "Google Form은 새 탭에서 열리며, 앱은 이번 세션의 로컬 사본도 함께 보관합니다.",
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
    "NORA asks purpose first, then turns the strategy and situation into evidence.": "NORA는 목적을 먼저 묻고, 전략과 상황을 근거로 바꿉니다.",
    "NORA starts with the customer purpose, then checks the strategy and current situation before any model.": "NORA는 고객의 목적에서 시작하고, 어떤 모델보다 먼저 전략과 현재 상황을 확인합니다.",
    "LY-Scope starts with the customer goal, then checks the strategy and current situation before any model.": "LY-Scope는 고객의 목표에서 시작하고, 어떤 모델보다 먼저 전략과 현재 상황을 확인합니다.",
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
    "Portfolio Search": "포트폴리오 검색",
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
    "Real Estate Analytics": "부동산 분석",
    "Income, real estate exposure, and rate sensitivity lens.": "소득, 부동산 노출, 금리 민감도 관점.",
    "Portfolio Diversification": "포트폴리오 분산",
    "Risk, covariance, correlation, and complementarity.": "위험, 공분산, 상관관계, 보완성.",
    "Financial Health": "재무 건강도",
    "Cash flow, savings, debt, liquidity, and capacity.": "현금흐름, 저축, 부채, 유동성, 감당 능력.",
    "Financial Diary": "금융 다이어리",
    "Advisor Reports": "케이스 스터디",
    "Case Studies": "케이스 스터디",
    "NORA Case Study Lab": "NORA 케이스 스터디 Lab",
    "Read fictional client cases through the current NORA web flow: goal, situation, evidence, decision, and memory.": "현재 NORA 웹 흐름에 맞춰 가상 고객 케이스를 목표, 상황, 근거, 결정, 기억 순서로 검토하세요.",
    "Case Study Board": "케이스 스터디 보드",
    "Pick a client, then read the goal and stress signal before opening details.": "고객을 선택한 뒤 세부내용보다 먼저 목표와 스트레스 신호를 확인하세요.",
    "Customer Goal": "고객 목표",
    "Crisis": "위기",
    "NORA Case Path": "NORA 케이스 경로",
    "Use Case as Decision Draft": "케이스를 결정 초안으로 사용",
    "Case Study Details": "케이스 상세",
    "Case Study Archive": "케이스 스터디 아카이브",
    "Show table details": "표 상세 보기",
    "Open this case in the Decision Capture flow.": "이 케이스를 Decision Capture 흐름에서 엽니다.",
    "Purpose": "목적",
    "Situation": "상황",
    "Decision": "결정",
    "Review": "검토",
    "Visual Case Snapshot": "시각 케이스 스냅샷",
    "Advisor": "어드바이저",
    "Portfolio / SR": "포트폴리오 / SR",
    "Goal-first mobile map": "목표 중심 모바일 맵",
    "Rationality Gate": "합리성 게이트",
    "Disciplined": "절제됨",
    "Developing": "형성 중",
    "Fragile": "취약",
    "Rationality means goal-fit, evidence, model discipline, risk awareness, and memory before action.": "합리성은 행동 전에 목표 적합성, 근거, 모델 절제, 위험 인식, 기억이 연결되는지를 뜻합니다.",
    "Capture → Purpose → Evidence → Decision → Memory": "포착 → 목적 → 근거 → 결정 → 기억",
    "Purpose Fit": "목적 적합성",
    "Capture Quality": "포착 품질",
    "Decision Capture": "결정 포착",
    "User signal": "사용자 신호",
    "Evidence Quality": "근거 품질",
    "Model Discipline": "모델 절제",
    "Risk Awareness": "위험 인식",
    "Decision Draft": "결정 초안",
    "Memory Feedback": "기억 피드백",
    "Capture": "포착",
    "Action": "행동",
    "Action follow-through": "행동 실행",
    "Outcome": "결과",
    "What happened next?": "그 다음 결과는?",
    "NORA starts with the customer purpose, then checks the strategy and current situation before any model.": "NORA는 고객의 목적에서 시작한 뒤 모델보다 먼저 전략과 현재 상황을 확인합니다.",
    "Hover or click each visual node to read its role.": "각 시각 노드에 마우스를 올리거나 클릭하면 역할을 확인할 수 있습니다.",
    "What does the customer want?": "고객은 무엇을 원하는가?",
    "Strategy path": "전략 경로",
    "Current reality": "현재 현실",
    "Structured inputs": "구조화 입력",
    "Calculation engine": "계산 엔진",
    "Proof and assumptions": "근거와 가정",
    "Reasoning layer": "추론 레이어",
    "Action direction": "행동 방향",
    "Decision log": "결정 기록",
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
    "REIT": "REIT",
    "Details": "계산",
    "Scenario": "시나리오",
    "AI Coach": "AI 코치",
    "NORA Path": "NORA 경로",
    "Goal → Strategy → Situation → AI Coach": "목표 → 전략 → 상황 → AI 코치",
    "Choose the customer purpose first.": "고객의 목표를 먼저 선택합니다.",
    "Follow the plan selected by the goal.": "목표가 선택한 전략을 따라갑니다.",
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
    "Use real estate signals as sector education.": "부동산 신호를 섹터 학습용으로 활용하세요.",
    "Review formulas before trusting outputs.": "결과를 신뢰하기 전에 공식을 확인하세요.",
    "Check API and macro assumptions.": "API와 거시 가정을 확인하세요.",
    "Use this for professor/demo walkthroughs.": "교수님/데모 설명용으로 사용하세요.",
    "Review virtual clients and export advisor PDF reports.": "가상 고객 케이스를 검토하고 PDF 리포트를 내보내세요.",
    "Review real estate value, income durability, and rate-sensitive exposure.": "부동산 가치, 소득 지속성, 금리 민감 노출을 검토하세요.",
    "Review virtual clients through the LY-Scope-Ver.2 decision architecture and export PDF reports.": "LY-Scope-Ver.2 의사결정 아키텍처로 가상 고객 케이스를 검토하고 PDF 리포트를 내보내세요.",
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
    "LY-Scope-Ver.2 connects user context, financial data, models, evidence, AI interpretation, decisions, and memory. Use the circular menu above to move between valuation, portfolio risk, real estate exposure, personal finance, scenario stress testing, AI readiness, calculation transparency, and diary reflection.": "LY-Scope-Ver.2는 사용자 맥락, 금융 데이터, 모델, 근거, AI 해석, 결정, 메모리를 연결합니다. 위 원형 메뉴로 가치평가, 포트폴리오 위험, 부동산 노출, 개인 재무, 시나리오 스트레스 테스트, AI 준비도, 계산 투명성, 다이어리 회고를 이동하세요.",
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
    .homepage-visual.has-home-image {
        position: relative;
        overflow: hidden;
        isolation: isolate;
    }
    .homepage-visual.has-home-image::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: 1;
        opacity: 1;
        background:
            linear-gradient(90deg, rgba(248, 252, 255, 0.86) 0%, rgba(248, 252, 255, 0.68) 36%, rgba(248, 252, 255, 0.16) 68%, rgba(248, 252, 255, 0.08) 100%),
            linear-gradient(180deg, rgba(255,255,255,0.36), rgba(255,255,255,0.08));
        pointer-events: none;
    }
    .homepage-visual.has-home-image .home-nav,
    .homepage-visual.has-home-image .home-goal-layout,
    .homepage-visual.has-home-image .homepage-direct-entry {
        position: relative;
        z-index: 2;
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
            height: 196px;
            aspect-ratio: auto;
            object-fit: cover;
            object-position: center 46%;
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
        justify-content: center !important;
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
    html body .stApp .goal-strategy-return {
        display: inline-block;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        text-decoration: none !important;
    }
    html body .stApp .goal-strategy-return:hover b,
    html body .stApp .goal-strategy-return:focus b {
        color: var(--goal-color) !important;
        -webkit-text-fill-color: var(--goal-color) !important;
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
    html body .stApp .rationality-gate {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto auto auto;
        gap: 12px;
        align-items: center;
        margin: 8px 0 12px;
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        background: #ffffff;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }
    html body .stApp .rationality-gate-main b {
        display: block;
        color: #0f172a;
        font-size: 0.90rem;
        line-height: 1.1;
        font-weight: 900;
    }
    html body .stApp .rationality-gate-main span {
        display: block;
        margin-top: 3px;
        color: #64748b;
        font-size: 0.75rem;
        line-height: 1.25;
        font-weight: 650;
    }
    html body .stApp .rationality-path {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 5px 6px;
        margin-top: 7px;
        max-width: 100%;
    }
    html body .stApp .rationality-path span {
        min-width: 52px;
        min-height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0 8px;
        border-radius: 999px;
        color: #0f4a5a;
        background: rgba(14, 165, 233, 0.09);
        border: 1px solid rgba(14, 165, 233, 0.12);
        font-size: 0.66rem;
        line-height: 1;
        font-weight: 850;
        white-space: nowrap;
    }
    html body .stApp .rationality-path i {
        color: #94a3b8;
        font-size: 0.66rem;
        line-height: 1;
        font-style: normal;
        font-weight: 900;
    }
    html body .stApp .rationality-score {
        min-width: 86px;
        display: grid;
        grid-template-columns: auto auto;
        align-items: end;
        justify-content: center;
        column-gap: 2px;
        color: var(--rational-color);
    }
    html body .stApp .rationality-score strong {
        font-size: 1.28rem;
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
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 10px;
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
        font-size: 0.58rem;
        line-height: 1;
        font-weight: 950;
    }
    html body .stApp .rationality-detail summary {
        min-height: 32px;
        padding: 0 11px;
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
    html body .stApp .nora-ontology summary .ly-flow-summary-path {
        display: inline-flex;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;
        flex-wrap: wrap;
        min-width: 0;
    }
    html body .stApp .nora-ontology summary .ly-flow-summary-path i {
        color: #94a3b8;
        font-style: normal;
        line-height: 1;
    }
    html body .stApp .nora-ontology summary .ly-flow-return {
        display: inline-flex;
        align-items: center;
        min-height: 24px;
        padding: 4px 9px;
        border-radius: 999px;
        color: #0f766e !important;
        -webkit-text-fill-color: #0f766e !important;
        background: #ecfeff;
        border: 1px solid rgba(14, 165, 233, 0.18);
        text-decoration: none !important;
        font-size: 0.74rem;
        font-weight: 900;
    }
    html body .stApp .nora-ontology summary .ly-flow-return:hover,
    html body .stApp .nora-ontology summary .ly-flow-return:focus {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: #0f766e;
        outline: none;
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
    html body .stApp .portfolio-sr-header .portfolio-sr-icon {
        width: 30px;
        height: 30px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        background: transparent;
        overflow: hidden;
        flex: 0 0 30px;
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
    /* Finance reference pass: compact overview widgets, hidden detail, calmer chart-room feel. */
    html body .stApp {
        background:
            linear-gradient(90deg, rgba(14, 116, 144, 0.050) 1px, transparent 1px),
            linear-gradient(0deg, rgba(14, 116, 144, 0.036) 1px, transparent 1px),
            radial-gradient(circle at 0% 0%, rgba(224, 242, 254, 0.78), transparent 32%),
            radial-gradient(circle at 100% 10%, rgba(236, 253, 245, 0.72), transparent 30%),
            linear-gradient(135deg, #f8fbff 0%, #f6fbf9 54%, #fffaf0 100%) !important;
        background-size: 58px 58px, 58px 58px, auto, auto, auto !important;
        color: #0f172a !important;
    }
    html body .stApp::before,
    html body .stApp::after {
        opacity: 0.10 !important;
    }
    html body .stApp .block-container {
        max-width: 1240px !important;
        padding-top: 0.75rem !important;
    }
    html body .stApp h1 {
        font-size: 1.92rem !important;
        line-height: 1.1 !important;
    }
    html body .stApp h2 {
        font-size: 1.52rem !important;
        line-height: 1.14 !important;
    }
    html body .stApp h3 {
        font-size: 1.18rem !important;
        line-height: 1.18 !important;
    }
    html body .stApp .brand-header {
        min-height: 50px !important;
        margin-bottom: 8px !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045) !important;
    }
    html body .stApp .brand-name {
        font-size: 1.18rem !important;
    }
    html body .stApp .finance-snapshot-ribbon {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 8px 0 12px;
        position: relative;
        z-index: 5;
    }
    html body .stApp .finance-snapshot-card {
        --snapshot-accent: #0f766e;
        min-height: 92px;
        position: relative;
        display: grid;
        grid-template-columns: 32px minmax(0, 1fr);
        grid-template-rows: auto auto auto;
        column-gap: 10px;
        align-items: center;
        padding: 12px 13px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045);
        outline: none;
    }
    html body .stApp .finance-snapshot-card.mid {
        --snapshot-accent: #2563eb;
    }
    html body .stApp .finance-snapshot-card.watch {
        --snapshot-accent: #d97706;
    }
    html body .stApp .finance-snapshot-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        border-radius: 8px 8px 0 0;
        background: var(--snapshot-accent);
    }
    html body .stApp .finance-snapshot-glyph {
        grid-row: 1 / 4;
        width: 32px;
        height: 32px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        color: #ffffff;
        background: var(--snapshot-accent);
        font-size: 0.68rem;
        line-height: 1;
        font-weight: 950;
        text-transform: uppercase;
    }
    html body .stApp .finance-snapshot-card small {
        color: #64748b;
        font-size: 0.70rem;
        line-height: 1.1;
        font-weight: 850;
        text-transform: uppercase;
    }
    html body .stApp .finance-snapshot-card b {
        min-width: 0;
        color: #0f172a;
        font-size: 1.06rem;
        line-height: 1.12;
        font-weight: 950;
        overflow-wrap: anywhere;
    }
    html body .stApp .finance-snapshot-card em {
        color: #475569;
        font-size: 0.76rem;
        line-height: 1.15;
        font-style: normal;
        font-weight: 720;
        overflow-wrap: anywhere;
    }
    html body .stApp .finance-snapshot-detail {
        position: absolute;
        left: 12px;
        right: 12px;
        top: calc(100% + 8px);
        z-index: 30;
        display: block;
        padding: 10px 11px;
        border-radius: 8px;
        color: #334155;
        background: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.24);
        box-shadow: 0 18px 34px rgba(15, 23, 42, 0.12);
        font-size: 0.76rem;
        line-height: 1.38;
        opacity: 0;
        transform: translateY(-3px);
        pointer-events: none;
        transition: opacity 140ms ease, transform 140ms ease;
    }
    html body .stApp .finance-snapshot-card:hover .finance-snapshot-detail,
    html body .stApp .finance-snapshot-card:focus .finance-snapshot-detail {
        opacity: 1;
        transform: translateY(0);
    }
    html body .stApp .client-visual-report {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        gap: 12px;
        align-items: stretch;
        margin: 8px 0 12px;
    }
    html body .stApp .client-report-cards {
        display: grid;
        grid-template-columns: repeat(3, minmax(210px, 1fr));
        gap: 10px;
        min-width: 0;
    }
    html body .stApp .client-report-card {
        --report-color: #0f766e;
        min-height: 138px;
        position: relative;
        padding: 13px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045);
        overflow: visible;
        outline: none;
    }
    html body .stApp .client-report-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        border-radius: 8px 8px 0 0;
        background: var(--report-color);
    }
    html body .stApp .client-report-main {
        display: grid;
        grid-template-columns: 38px minmax(0, 1fr);
        gap: 10px;
        align-items: center;
    }
    html body .stApp .client-report-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        overflow: hidden;
    }
    html body .stApp .client-report-text small {
        display: block;
        color: #64748b;
        font-size: 0.67rem;
        line-height: 1;
        font-weight: 900;
        text-transform: uppercase;
    }
    html body .stApp .client-report-text b {
        display: block;
        margin-top: 4px;
        color: #0f172a;
        font-size: 1.08rem;
        line-height: 1.08;
        font-weight: 950;
        overflow-wrap: anywhere;
    }
    html body .stApp .client-report-text em {
        display: block;
        margin-top: 4px;
        color: #475569;
        font-size: 0.74rem;
        line-height: 1.2;
        font-style: normal;
        font-weight: 740;
        overflow-wrap: anywhere;
    }
    html body .stApp .client-report-meter {
        height: 8px;
        margin-top: 14px;
        border-radius: 999px;
        overflow: hidden;
        background: #e2e8f0;
    }
    html body .stApp .client-report-meter i {
        display: block;
        width: var(--level);
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--report-color), #38bdf8);
    }
    html body .stApp .client-report-detail {
        position: absolute;
        left: 10px;
        right: 10px;
        top: calc(100% + 8px);
        z-index: 40;
        padding: 10px 11px;
        border-radius: 8px;
        color: #334155;
        background: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.24);
        box-shadow: 0 18px 34px rgba(15, 23, 42, 0.12);
        font-size: 0.74rem;
        line-height: 1.38;
        opacity: 0;
        transform: translateY(-3px);
        pointer-events: none;
        transition: opacity 140ms ease, transform 140ms ease;
    }
    html body .stApp .client-report-card:hover .client-report-detail,
    html body .stApp .client-report-card:focus .client-report-detail {
        opacity: 1;
        transform: translateY(0);
    }
    html body .stApp .client-direction-rail {
        min-height: 92px;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
        padding: 12px;
        border-radius: 8px;
        background:
            linear-gradient(90deg, rgba(15, 118, 110, 0.06), rgba(37, 99, 235, 0.05)),
            rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(148, 163, 184, 0.20);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045);
    }
    html body .stApp .client-direction-step {
        min-width: 0;
        display: grid;
        grid-template-columns: 32px minmax(0, 1fr);
        grid-template-rows: auto auto 6px;
        align-items: start;
        column-gap: 8px;
        row-gap: 4px;
    }
    html body .stApp .client-direction-step span {
        grid-row: 1 / 4;
        width: 32px;
        height: 32px;
        overflow: hidden;
    }
    html body .stApp .client-direction-step b {
        color: #0f172a;
        font-size: 0.80rem;
        line-height: 1.12;
        font-weight: 900;
        overflow-wrap: anywhere;
    }
    html body .stApp .client-direction-step em {
        color: #64748b;
        font-size: 0.68rem;
        line-height: 1.18;
        font-style: normal;
        font-weight: 700;
        overflow-wrap: anywhere;
    }
    html body .stApp .client-direction-step i {
        display: block;
        width: var(--level);
        height: 6px;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--step-color), #38bdf8);
    }
    html body .stApp .client-report-evidence {
        grid-column: 1 / -1;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(255, 255, 255, 0.78);
        overflow: hidden;
    }
    html body .stApp .client-report-evidence summary {
        min-height: 38px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 12px;
        color: #0f172a;
        font-size: 0.78rem;
        font-weight: 900;
        cursor: pointer;
        list-style: none;
    }
    html body .stApp .client-report-evidence summary::-webkit-details-marker {
        display: none;
    }
    html body .stApp .client-report-evidence ul {
        margin: 0;
        padding: 8px 12px 12px 28px;
        color: #475569;
        font-size: 0.76rem;
        line-height: 1.4;
    }
    html body .stApp .goal-strategy-strip,
    html body .stApp .rationality-gate,
    html body .stApp .nora-ontology,
    html body .stApp .life-compact-panel,
    html body .stApp .client-report-card,
    html body .stApp .client-direction-rail,
    html body .stApp .metric-card,
    html body .stApp .portfolio-score-card {
        border-radius: 8px !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045) !important;
    }
    html body .stApp .goal-strategy-strip {
        min-height: 58px;
        padding: 10px 12px !important;
    }
    html body .stApp .goal-strategy-mark {
        height: 36px !important;
    }
    html body .stApp .rationality-gate {
        grid-template-columns: minmax(170px, 1fr) auto auto auto !important;
        align-items: center !important;
        overflow: visible !important;
    }
    html body .stApp .rationality-detail {
        justify-self: end;
        min-width: 0;
    }
    html body .stApp .rationality-detail[open] {
        grid-column: 1 / -1;
        width: 100%;
        justify-self: stretch;
        margin-top: 2px;
    }
    html body .stApp .rationality-detail[open] summary {
        margin-left: auto;
    }
    html body .stApp .rationality-detail[open] ul {
        width: 100%;
        min-width: 0 !important;
        display: grid;
        grid-template-columns: 1fr;
        gap: 0;
        padding: 8px 12px !important;
        border-radius: 8px;
        background: #f8fafc !important;
        border: 1px solid rgba(148, 163, 184, 0.18);
    }
    html body .stApp .rationality-detail[open] li {
        grid-template-columns: minmax(130px, 180px) minmax(0, 1fr) !important;
        word-break: normal !important;
        overflow-wrap: anywhere !important;
    }
    html body .stApp .nora-ontology {
        margin-bottom: 10px !important;
    }
    html body .stApp .desktop-orbit-shell {
        grid-template-columns: repeat(auto-fit, minmax(92px, 1fr)) !important;
    }
    html body .stApp .desktop-orbit-center,
    html body .stApp .desktop-orbit-item {
        height: 34px !important;
        border-radius: 7px !important;
        background: rgba(255, 255, 255, 0.86) !important;
    }
    html body .stApp .desktop-orbit-center span,
    html body .stApp .desktop-orbit-item span {
        min-width: 0 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    html body .stApp .metric-card {
        min-height: 86px !important;
        padding: 14px !important;
    }
    html body .stApp .metric-card .label {
        font-size: 0.70rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0 !important;
    }
    html body .stApp .metric-card .value {
        font-size: 1.20rem !important;
        overflow-wrap: anywhere !important;
    }
    @media (max-width: 900px) {
        html body .stApp .finance-snapshot-ribbon {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        html body .stApp .client-visual-report {
            grid-template-columns: 1fr;
        }
        html body .stApp .client-report-cards,
        html body .stApp .client-direction-rail {
            grid-template-columns: 1fr;
        }
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
        html body .stApp .rationality-detail[open] li {
            grid-template-columns: 1fr !important;
        }
        html body .stApp .life-goal-board {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 680px) {
        html body .stApp .finance-snapshot-ribbon {
            grid-template-columns: 1fr;
        }
        html body .stApp .finance-snapshot-card {
            min-height: 82px;
        }
        html body .stApp .homepage-visual .life-title {
            font-size: 1.78rem !important;
        }
        html body .stApp .goal-compass {
            display: none;
        }
        html body .stApp .goal-compass-caption {
            margin-top: 8px;
        }
        html body .stApp .home-goal-layout {
            padding: 20px 16px;
            gap: 14px;
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
    html body .stApp,
    html body .stApp * {
        box-sizing: border-box;
    }
    html body .stApp .goal-strategy-detail[open] {
        grid-column: 1 / -1;
        width: 100%;
        justify-self: stretch;
    }
    html body .stApp .goal-strategy-detail[open] summary {
        width: max-content;
        max-width: 100%;
    }
    html body .stApp .goal-strategy-detail[open] p {
        max-width: none !important;
        overflow-wrap: anywhere;
    }
    html body .stApp .rationality-gate-main,
    html body .stApp .rationality-score,
    html body .stApp .rationality-nodes,
    html body .stApp .rationality-detail {
        min-width: 0;
    }
    html body .stApp .rationality-nodes {
        flex-wrap: wrap;
        justify-content: flex-start;
        max-width: 100%;
    }
    html body .stApp .rationality-node {
        flex: 0 0 34px;
    }
    html body .stApp .rationality-detail[open] {
        grid-column: 1 / -1 !important;
    }
    html body .stApp .rationality-detail[open] ul,
    html body .stApp .rationality-detail[open] li,
    html body .stApp .rationality-detail[open] span {
        max-width: 100%;
        overflow-wrap: anywhere;
    }
    html body .stApp .top-language-toggle {
        max-width: calc(100vw - 24px);
    }
    html body .stApp div[data-testid="stExpander"] details summary {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid rgba(148, 163, 184, 0.20) !important;
        border-radius: 8px !important;
    }
    html body .stApp div[data-testid="stExpander"] details summary * {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    html body .stApp div[data-testid="stExpander"] details[open] summary {
        border-color: rgba(14, 165, 233, 0.28) !important;
        background: rgba(240, 249, 255, 0.96) !important;
    }
    html body section[data-testid="stSidebar"] {
        color: #0f172a !important;
        background:
            radial-gradient(circle at 20% 5%, rgba(186, 230, 253, 0.82), transparent 28%),
            linear-gradient(180deg, #eef9ff 0%, #ecfdf5 100%) !important;
    }
    html body section[data-testid="stSidebar"] h1,
    html body section[data-testid="stSidebar"] h2,
    html body section[data-testid="stSidebar"] h3,
    html body section[data-testid="stSidebar"] label {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    html body section[data-testid="stSidebar"] p,
    html body section[data-testid="stSidebar"] span,
    html body section[data-testid="stSidebar"] small,
    html body section[data-testid="stSidebar"] li {
        color: #334155 !important;
        -webkit-text-fill-color: #334155 !important;
    }
    html body section[data-testid="stSidebar"] b,
    html body section[data-testid="stSidebar"] strong {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] details {
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.58) !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        overflow: hidden;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: #111827 !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] details > div,
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] details > div *:not(button):not(button *) {
        color: #334155 !important;
        -webkit-text-fill-color: #334155 !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] h1,
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] h2,
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] h3,
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] b,
    html body section[data-testid="stSidebar"] div[data-testid="stExpander"] strong {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    /* Sidebar toggle: make the native Streamlit control visible and understandable. */
    html body section[data-testid="stSidebar"] {
        overflow: visible !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarHeader"] {
        overflow: visible !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] {
        z-index: 100400 !important;
        width: 96px !important;
        height: 38px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    html body section[data-testid="stSidebar"][aria-expanded="true"] div[data-testid="stSidebarCollapseButton"] {
        position: absolute !important;
        top: 14px !important;
        right: 14px !important;
        left: auto !important;
        transform: none !important;
    }
    html body section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarCollapseButton"] {
        position: absolute !important;
        top: 14px !important;
        left: 12px !important;
        transform: translateX(300px) !important;
    }
    html body section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarContent"] > div:not([data-testid="stSidebarHeader"]) {
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        overflow: hidden !important;
    }
    html body section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarCollapseButton"],
    html body section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarCollapseButton"] * {
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button {
        width: 96px !important;
        height: 38px !important;
        min-height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 5px !important;
        padding: 0 12px !important;
        border-radius: 999px !important;
        color: #ffffff !important;
        background: #0f172a !important;
        border: 1px solid rgba(103, 232, 249, 0.32) !important;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.18) !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button span,
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button span[data-testid="stIconMaterial"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button::after {
        content: "Close";
        color: #ffffff;
        font-family: Century, "Century Schoolbook", Georgia, serif;
        font-size: 0.74rem;
        line-height: 1;
        font-weight: 900;
        letter-spacing: 0;
    }
    html body section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarCollapseButton"] button::after {
        content: "Menu";
    }
    @media (max-width: 900px) {
        html body .stApp .rationality-gate {
            grid-template-columns: minmax(0, 1fr) !important;
            align-items: start !important;
        }
        html body .stApp .rationality-score,
        html body .stApp .rationality-detail {
            justify-self: start !important;
        }
        html body .stApp .rationality-nodes {
            width: 100%;
            gap: 6px;
        }
        html body .stApp .rationality-node {
            width: 32px;
            height: 32px;
            flex-basis: 32px;
        }
    }
    @media (max-width: 680px) {
        html body .stApp .rationality-gate {
            gap: 8px !important;
        }
        html body .stApp .rationality-node b {
            font-size: 0.54rem !important;
        }
        html body .stApp .goal-strategy-strip {
            gap: 9px;
        }
        html body .stApp .goal-strategy-detail[open] {
            grid-column: 1 / -1;
        }
    }
    /* Rationality Gate hardening: keep Detail expansion from squeezing the visual summary. */
    html body .stApp .rationality-gate {
        display: flex !important;
        flex-wrap: wrap !important;
        align-items: center !important;
        align-content: flex-start !important;
        gap: 10px 12px !important;
        min-height: auto !important;
        overflow: visible !important;
    }
    html body .stApp .rationality-gate-main {
        flex: 1 1 260px !important;
        min-width: min(260px, 100%) !important;
        max-width: 100% !important;
    }
    html body .stApp .rationality-gate-main > b,
    html body .stApp .rationality-gate-main > span {
        display: block !important;
        white-space: normal !important;
        word-break: normal !important;
        overflow-wrap: normal !important;
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
    }
    html body .stApp .rationality-path {
        display: flex !important;
        flex-wrap: wrap !important;
        align-items: center !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }
    html body .stApp .rationality-path span {
        flex: 0 0 auto !important;
        display: inline-flex !important;
        max-width: 100% !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
    }
    html body .stApp .rationality-path i {
        flex: 0 0 auto !important;
    }
    html body .stApp .rationality-score {
        flex: 0 0 auto !important;
        min-width: 90px !important;
        justify-content: center !important;
    }
    html body .stApp .rationality-nodes {
        flex: 0 1 250px !important;
        width: auto !important;
        min-width: 180px !important;
    }
    html body .stApp .rationality-detail {
        flex: 0 0 auto !important;
        min-width: max-content !important;
        margin-left: auto !important;
        justify-self: auto !important;
    }
    html body .stApp .rationality-detail[open] {
        flex: 1 0 100% !important;
        width: 100% !important;
        min-width: 0 !important;
        margin: 6px 0 0 !important;
        padding-top: 10px !important;
        border-top: 1px solid rgba(148, 163, 184, 0.14) !important;
    }
    html body .stApp .rationality-detail[open] summary {
        width: max-content !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    html body .stApp .rationality-detail[open] ul {
        width: 100% !important;
        min-width: 0 !important;
        margin-top: 10px !important;
    }
    html body .stApp .rationality-detail[open] li {
        grid-template-columns: minmax(150px, 210px) minmax(0, 1fr) !important;
        align-items: start !important;
    }
    @media (max-width: 760px) {
        html body .stApp .rationality-gate-main {
            flex-basis: 100% !important;
        }
        html body .stApp .rationality-path {
            gap: 5px !important;
        }
        html body .stApp .rationality-path span {
            min-width: 50px !important;
            min-height: 22px !important;
            padding: 0 7px !important;
            font-size: 0.62rem !important;
        }
        html body .stApp .rationality-score,
        html body .stApp .rationality-detail {
            margin-left: 0 !important;
        }
        html body .stApp .rationality-nodes {
            flex: 1 1 180px !important;
        }
        html body .stApp .rationality-detail[open] li {
            grid-template-columns: 1fr !important;
        }
    }
    /* Readability polish: separate the LY mark from the name, quiet the page texture,
       and keep the visual data cards crisp. */
    html body .stApp {
        background:
            linear-gradient(90deg, rgba(14, 116, 144, 0.026) 1px, transparent 1px),
            linear-gradient(0deg, rgba(14, 116, 144, 0.020) 1px, transparent 1px),
            radial-gradient(circle at 0% 0%, rgba(224, 242, 254, 0.62), transparent 30%),
            radial-gradient(circle at 100% 9%, rgba(236, 253, 245, 0.52), transparent 28%),
            linear-gradient(135deg, #f9fcff 0%, #f8fcfb 56%, #fffdf6 100%) !important;
        background-size: 64px 64px, 64px 64px, auto, auto, auto !important;
    }
    html body .stApp::before,
    html body .stApp::after {
        opacity: 0.045 !important;
        filter: saturate(0.82);
    }
    html body header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        pointer-events: none !important;
    }
    html body header[data-testid="stHeader"] div[data-testid="stToolbar"] {
        display: none !important;
    }
    html body .stApp .block-container {
        max-width: 1180px !important;
        padding-top: 0.85rem !important;
    }
    html body .stApp .top-language-toggle {
        top: 12px !important;
        right: 16px !important;
        padding: 4px !important;
        gap: 4px !important;
        background: rgba(255, 255, 255, 0.92) !important;
        border-color: rgba(148, 163, 184, 0.22) !important;
        box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10) !important;
    }
    html body .stApp .top-language-toggle .language-toggle-mark,
    html body .stApp .top-language-toggle a {
        width: 30px !important;
        height: 30px !important;
        color: #0f766e !important;
        -webkit-text-fill-color: #0f766e !important;
        border-color: rgba(15, 118, 110, 0.18) !important;
    }
    html body .stApp .top-language-toggle a.active {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: #0f766e !important;
        border-color: rgba(15, 118, 110, 0.38) !important;
        box-shadow: none !important;
    }
    html body .stApp .brand-header {
        width: 100% !important;
        min-height: 72px !important;
        margin: 0 auto 16px !important;
        padding: 14px clamp(16px, 2.8vw, 30px) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        background: rgba(255, 255, 255, 0.965) !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.065) !important;
    }
    html body .stApp .brand-header::after {
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        height: 3px !important;
        opacity: 0.78 !important;
        background: linear-gradient(90deg, rgba(15,118,110,0.08), rgba(37,99,235,0.62), rgba(34,211,238,0.70), rgba(15,118,110,0.52), rgba(15,118,110,0.08)) !important;
        box-shadow: none !important;
    }
    html body .stApp .brand-mark {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 14px !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }
    html body .stApp .brand-icon {
        flex: 0 0 48px !important;
        width: 48px !important;
        height: 48px !important;
        border-radius: 14px !important;
        display: grid !important;
        place-items: center !important;
        overflow: hidden !important;
        background:
            radial-gradient(circle at 30% 20%, rgba(255,255,255,0.45), transparent 32%),
            linear-gradient(135deg, #0f766e 0%, #0891b2 52%, #2563eb 100%) !important;
        border: 1px solid rgba(14, 165, 233, 0.22) !important;
        box-shadow: 0 10px 24px rgba(14, 116, 144, 0.16) !important;
    }
    html body .stApp .brand-icon::before,
    html body .stApp .brand-icon::after {
        content: none !important;
        display: none !important;
    }
    html body .stApp .brand-icon span {
        display: block !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-family: Century, "Century Schoolbook", Georgia, serif !important;
        font-size: 1.28rem !important;
        line-height: 1 !important;
        font-weight: 950 !important;
        letter-spacing: 0 !important;
        transform: translateY(-1px);
    }
    html body .stApp .brand-copy {
        min-width: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
    }
    html body .stApp .brand-wordmark {
        display: flex !important;
        align-items: baseline !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        min-width: 0 !important;
        flex-wrap: wrap !important;
    }
    html body .stApp .brand-name {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-family: Century, "Century Schoolbook", Georgia, serif !important;
        font-size: clamp(1.45rem, 2vw, 1.82rem) !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        white-space: nowrap !important;
        text-shadow: none !important;
    }
    html body .stApp .brand-version {
        display: inline-flex !important;
        align-items: center !important;
        min-height: 22px !important;
        padding: 0 8px !important;
        border-radius: 999px !important;
        color: #0f766e !important;
        -webkit-text-fill-color: #0f766e !important;
        background: #ecfeff !important;
        border: 1px solid rgba(14, 116, 144, 0.18) !important;
        font-size: 0.74rem !important;
        line-height: 1 !important;
        font-weight: 900 !important;
        white-space: nowrap !important;
    }
    html body .stApp .brand-subtitle {
        display: block !important;
        margin-top: 4px !important;
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        font-size: 0.62rem !important;
        line-height: 1.1 !important;
        font-weight: 800 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        text-align: left !important;
        max-width: 100% !important;
    }
    html body .stApp .finance-snapshot-ribbon {
        gap: 12px !important;
        margin: 10px 0 16px !important;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)) !important;
    }
    html body .stApp .finance-snapshot-card {
        min-height: 98px !important;
        padding: 14px !important;
        background: rgba(255, 255, 255, 0.975) !important;
        border-color: rgba(148, 163, 184, 0.24) !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.055) !important;
    }
    html body .stApp .finance-snapshot-card small,
    html body .stApp .finance-snapshot-card b,
    html body .stApp .finance-snapshot-card em {
        display: block !important;
        min-width: 0 !important;
        max-width: 100% !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    html body .stApp .finance-snapshot-card small {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.01em !important;
    }
    html body .stApp .finance-snapshot-card b {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 1.02rem !important;
        line-height: 1.16 !important;
        padding-bottom: 1px !important;
    }
    html body .stApp .finance-snapshot-card em {
        color: #475569 !important;
        -webkit-text-fill-color: #475569 !important;
        font-size: 0.72rem !important;
    }
    html body .stApp .goal-strategy-strip,
    html body .stApp .rationality-gate,
    html body .stApp .nora-ontology,
    html body .stApp .section-header,
    html body .stApp .metric-card,
    html body .stApp .portfolio-score-card {
        background: rgba(255, 255, 255, 0.975) !important;
        border-color: rgba(148, 163, 184, 0.22) !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.055) !important;
    }
    html body .stApp .desktop-orbit-center,
    html body .stApp .desktop-orbit-item {
        background: rgba(255, 255, 255, 0.96) !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05) !important;
    }
    html body .stApp .desktop-orbit-item.active,
    html body .stApp .desktop-orbit-center.active,
    html body .stApp .nora-module.active {
        box-shadow: 0 10px 24px rgba(15, 118, 110, 0.14) !important;
    }
    html body .stApp .rationality-score strong,
    html body .stApp .rationality-score small,
    html body .stApp .rationality-score em {
        display: block !important;
        min-width: 0 !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    html body .stApp .rationality-score strong {
        line-height: 1.12 !important;
        padding-bottom: 1px !important;
    }
    html body .stApp .decision-capture-panel {
        margin: 8px 0 14px;
        padding: 16px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.975);
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.055);
    }
    html body .stApp .decision-capture-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }
    html body .stApp .decision-capture-title {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
    }
    html body .stApp .decision-capture-title span {
        width: 36px;
        height: 36px;
        display: grid;
        place-items: center;
        border-radius: 9px;
        color: #ffffff;
        background: linear-gradient(135deg, #0f766e, #2563eb);
        font-size: 0.68rem;
        font-weight: 950;
    }
    html body .stApp .decision-capture-title b {
        display: block;
        color: #0f172a;
        font-size: 1.02rem;
        line-height: 1.05;
        font-weight: 950;
    }
    html body .stApp .decision-capture-title small,
    html body .stApp .decision-capture-head em {
        display: block;
        color: #64748b;
        font-size: 0.72rem;
        line-height: 1.18;
        font-style: normal;
        font-weight: 760;
    }
    html body .stApp .decision-capture-flow {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 5px;
        flex-wrap: wrap;
        color: #64748b;
        font-size: 0.70rem;
        line-height: 1;
        font-weight: 850;
        text-align: right;
    }
    html body .stApp div[data-testid="stForm"] {
        max-width: none !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid rgba(148, 163, 184, 0.24) !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.055) !important;
    }
    html body .stApp div[data-testid="stForm"] div[data-testid="stTextInput"] label,
    html body .stApp div[data-testid="stForm"] div[data-testid="stTextInput"] label *,
    html body .stApp div[data-testid="stForm"] div[data-testid="stWidgetLabel"],
    html body .stApp div[data-testid="stForm"] div[data-testid="stWidgetLabel"] *,
    html body .stApp div[data-testid="stForm"] label,
    html body .stApp div[data-testid="stForm"] label p,
    html body .stApp div[data-testid="stForm"] label span {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }
    html body .stApp div[data-testid="stForm"] div[data-baseweb="input"],
    html body .stApp div[data-testid="stForm"] textarea {
        color: #0f172a !important;
        background: #ffffff !important;
        border-color: rgba(148, 163, 184, 0.34) !important;
        box-shadow: none !important;
    }
    html body .stApp .decision-draft-card {
        margin: 8px 0 12px;
        padding: 14px;
        border-radius: 10px;
        background: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.20);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.045);
    }
    html body .stApp .decision-draft-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) repeat(3, minmax(120px, 0.8fr));
        gap: 10px;
    }
    html body .stApp .decision-draft-cell {
        min-height: 76px;
        padding: 12px;
        border-radius: 9px;
        background: #f8fafc;
        border: 1px solid rgba(148, 163, 184, 0.16);
    }
    html body .stApp .decision-draft-cell.primary {
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.96), rgba(239, 246, 255, 0.94));
        border-color: rgba(15, 118, 110, 0.18);
    }
    html body .stApp .decision-draft-cell small,
    html body .stApp .evidence-status-card small,
    html body .stApp .action-chip small {
        display: block;
        color: #64748b;
        font-size: 0.66rem;
        line-height: 1.05;
        font-weight: 900;
        text-transform: uppercase;
    }
    html body .stApp .decision-draft-cell b {
        display: block;
        margin-top: 5px;
        color: #0f172a;
        font-size: 0.92rem;
        line-height: 1.22;
        font-weight: 920;
        overflow-wrap: anywhere;
    }
    html body .stApp .decision-evidence-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 9px;
        margin: 8px 0 12px;
    }
    html body .stApp .evidence-status-card {
        min-height: 98px;
        padding: 12px;
        border-radius: 9px;
        background: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.035);
    }
    html body .stApp .evidence-status-card.verified { border-top: 4px solid #0f766e; }
    html body .stApp .evidence-status-card.user { border-top: 4px solid #2563eb; }
    html body .stApp .evidence-status-card.ai { border-top: 4px solid #7c3aed; }
    html body .stApp .evidence-status-card.missing { border-top: 4px solid #d97706; }
    html body .stApp .evidence-status-card b {
        display: block;
        margin-top: 5px;
        color: #0f172a;
        font-size: 0.86rem;
        line-height: 1.22;
        font-weight: 900;
    }
    html body .stApp .evidence-status-card span {
        display: block;
        margin-top: 5px;
        color: #475569;
        font-size: 0.72rem;
        line-height: 1.30;
        font-weight: 720;
    }
    html body .stApp .action-chip-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 8px 0 12px;
    }
    html body .stApp .action-chip {
        min-height: 52px;
        flex: 1 1 170px;
        padding: 10px 12px;
        border-radius: 9px;
        background: #f8fafc;
        border: 1px solid rgba(148, 163, 184, 0.18);
    }
    html body .stApp .action-chip b {
        display: block;
        margin-top: 4px;
        color: #0f172a;
        font-size: 0.82rem;
        line-height: 1.22;
        font-weight: 880;
    }
    html body .stApp .evidence-footer {
        margin: 10px 0 2px;
        padding: 12px;
        border-radius: 9px;
        color: #334155;
        background: #f8fafc;
        border: 1px dashed rgba(100, 116, 139, 0.26);
        font-size: 0.76rem;
        line-height: 1.42;
    }
    html body .stApp .evidence-footer b {
        color: #0f172a;
    }
    @media (max-width: 760px) {
        html body .stApp .brand-header {
            min-height: 64px !important;
            padding: 12px 14px !important;
        }
        html body .stApp .brand-icon {
            flex-basis: 42px !important;
            width: 42px !important;
            height: 42px !important;
            border-radius: 12px !important;
        }
        html body .stApp .brand-icon span {
            font-size: 1.08rem !important;
        }
        html body .stApp .brand-name {
            font-size: 1.30rem !important;
        }
        html body .stApp .brand-subtitle {
            display: none !important;
        }
        html body .stApp .decision-capture-head,
        html body .stApp .decision-capture-flow {
            align-items: flex-start;
            justify-content: flex-start;
            text-align: left;
        }
        html body .stApp .decision-draft-grid,
        html body .stApp .decision-evidence-grid {
            grid-template-columns: 1fr !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <style id="ly-century-visual-system">
    :root {
        --ly-century: Century, "Century Schoolbook", Georgia, "Times New Roman", serif;
    }
    html,
    body,
    button,
    input,
    textarea,
    select,
    svg text,
    [class^="st-"],
    [class*=" st-"],
    [data-testid],
    [data-testid] *,
    .stApp,
    .stApp * {
        font-family: var(--ly-century) !important;
        letter-spacing: 0 !important;
    }
    html body .stApp .visual-icon,
    html body .stApp .brand-logo-image,
    html body .stApp .nav-image-icon,
    html body .stApp .mobile-nav-image-icon,
    html body .stApp .finance-snapshot-icon,
    html body .stApp .rationality-icon,
    html body .stApp .nora-node-icon,
    html body .stApp .module-image-icon,
    html body .stApp .goal-number-icon,
    html body .stApp .life-goal-icon,
    html body .stApp .case-study-avatar-icon,
    html body .stApp .home-brand-icon,
    html body .stApp .language-image-icon,
    html body .stApp .decision-capture-icon {
        display: block !important;
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
        border: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    html body span[data-testid="stIconMaterial"],
    html body span[data-testid="stIconMaterial"] *,
    html body .material-symbols-rounded,
    html body .material-icons {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        letter-spacing: normal !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: "liga" !important;
        -webkit-font-smoothing: antialiased !important;
    }
    html body span[data-testid="stIconMaterial"] {
        display: inline-block !important;
        width: 1.12em !important;
        height: 1.12em !important;
        min-width: 1.12em !important;
        overflow: hidden !important;
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
        vertical-align: -0.12em !important;
    }
    html body span[data-testid="stIconMaterial"]::before {
        content: "" !important;
        display: block !important;
        width: 100% !important;
        height: 100% !important;
        background: #64748b !important;
        -webkit-mask: url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M9 5l7 7-7 7' fill='none' stroke='black' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / contain no-repeat !important;
        mask: url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M9 5l7 7-7 7' fill='none' stroke='black' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / contain no-repeat !important;
    }
    html body section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"]::before {
        background: #ffffff !important;
        -webkit-mask: url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M13 6l-6 6 6 6M19 6l-6 6 6 6' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / contain no-repeat !important;
        mask: url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M13 6l-6 6 6 6M19 6l-6 6 6 6' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / contain no-repeat !important;
    }
    html body .stApp .brand-icon {
        padding: 0 !important;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    html body .stApp .brand-icon::before,
    html body .stApp .brand-icon::after {
        content: none !important;
        display: none !important;
    }
    html body .stApp .brand-logo-image {
        width: 48px !important;
        height: 48px !important;
        filter: drop-shadow(0 10px 20px rgba(14, 116, 144, 0.16));
    }
    html body .stApp .top-language-toggle .language-toggle-mark {
        padding: 5px !important;
        background: #ecfeff !important;
    }
    html body .stApp .finance-snapshot-card {
        grid-template-rows: auto auto auto 7px !important;
    }
    html body .stApp .finance-snapshot-glyph,
    html body .stApp .finance-snapshot-glyph.image-glyph {
        padding: 0 !important;
        overflow: hidden !important;
        background: transparent !important;
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
    }
    html body .stApp .finance-snapshot-meter {
        grid-column: 1 / -1;
        height: 7px;
        margin-top: 7px;
        border-radius: 999px;
        overflow: hidden;
        background: #e2e8f0;
    }
    html body .stApp .finance-snapshot-meter i {
        display: block;
        width: var(--level);
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--snapshot-accent), #38bdf8);
    }
    html body .stApp .metric-card-meter {
        height: 7px;
        margin-top: 12px;
        border-radius: 999px;
        overflow: hidden;
        background: #e2e8f0;
    }
    html body .stApp .metric-card-meter span {
        display: block;
        width: var(--level);
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #0f766e, #38bdf8);
    }
    html body .stApp .rationality-node {
        padding: 5px !important;
    }
    html body .stApp .rationality-node .rationality-icon {
        position: relative;
        z-index: 2;
        width: 24px !important;
        height: 24px !important;
    }
    html body .stApp .desktop-orbit-item,
    html body .stApp .desktop-orbit-center {
        min-height: 40px !important;
    }
    html body .stApp .desktop-orbit-item .nav-image-icon,
    html body .stApp .desktop-orbit-center .nav-image-icon {
        width: 24px !important;
        height: 24px !important;
        flex: 0 0 24px !important;
    }
    html body .stApp .mobile-orbit-item .mobile-nav-image-icon {
        width: 26px !important;
        height: 26px !important;
    }
    html body .stApp .mobile-orbit-center .mobile-nav-image-icon {
        width: 34px !important;
        height: 34px !important;
    }
    html body .stApp .nora-glyph {
        padding: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }
    html body .stApp .nora-node-icon {
        width: 34px !important;
        height: 34px !important;
    }
    html body .stApp .nora-module {
        gap: 6px !important;
    }
    html body .stApp .nora-module .module-image-icon {
        width: 20px !important;
        height: 20px !important;
        flex: 0 0 20px !important;
    }
    html body .stApp .nora-module span {
        display: inline-flex !important;
        min-width: 0 !important;
        align-items: center !important;
    }
    html body .stApp .goal-number,
    html body .stApp .life-goal-link span,
    html body .stApp .decision-capture-title span,
    html body .stApp .case-study-avatar {
        padding: 0 !important;
        overflow: hidden !important;
        background: transparent !important;
    }
    html body .stApp .goal-number-icon,
    html body .stApp .life-goal-icon,
    html body .stApp .decision-capture-icon {
        width: 100% !important;
        height: 100% !important;
    }
    html body .stApp .case-study-profile-top em {
        display: inline-flex !important;
        align-items: center !important;
        gap: 7px !important;
    }
    html body .stApp .case-study-score-ring {
        width: 24px;
        height: 24px;
        flex: 0 0 24px;
        border-radius: 50%;
        background: conic-gradient(#0f766e var(--score), #e2e8f0 0);
        box-shadow: inset 0 0 0 6px #ffffff;
    }
    html body .stApp .case-study-avatar-icon {
        width: 48px !important;
        height: 48px !important;
    }
    html body .stApp .client-report-image-icon,
    html body .stApp .client-direction-image-icon {
        width: 100% !important;
        height: 100% !important;
        display: block !important;
        object-fit: contain !important;
    }
    @media (max-width: 760px) {
        html body .stApp .brand-logo-image {
            width: 42px !important;
            height: 42px !important;
        }
        html body .stApp .desktop-orbit-item .nav-image-icon,
        html body .stApp .desktop-orbit-center .nav-image-icon {
            width: 22px !important;
            height: 22px !important;
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
GOOGLE_FEEDBACK_FORM_URL = get_secret_or_env("GOOGLE_FEEDBACK_FORM_URL")
PUBLIC_APP_URL = get_secret_or_env("PUBLIC_APP_URL", "https://ly-scope-ver2.streamlit.app").rstrip("/")
DEFAULT_RISK_FREE_RATE = 0.045
DEFAULT_EQUITY_RISK_PREMIUM = 0.045
RISK_FREE_RATE = DEFAULT_RISK_FREE_RATE
EQUITY_RISK_PREMIUM = DEFAULT_EQUITY_RISK_PREMIUM


GUIDE_PDF_PATH = Path(__file__).with_name("LY-Scope-Ver.2_User_Guide.pdf")
GUIDE_SCREENSHOT_DIR = Path(__file__).with_name("guide_assets") / "screenshots"
APP_ASSET_DIR = Path(__file__).parent / "assets"
HOMEPAGE_BG_PATH = APP_ASSET_DIR / "ly_visual_life_path_app.jpg"
APP_BACKGROUND_PATH = APP_ASSET_DIR / "ly_visual_data_corridor_app.jpg"
CLIENT_REPORT_BG_PATH = APP_ASSET_DIR / "ly_visual_lens_report_app.jpg"
ONTOLOGY_BG_PATH = APP_ASSET_DIR / "ly_visual_system_nodes_app.jpg"
DIRECTION_FLOW_BG_PATH = APP_ASSET_DIR / "ly_visual_direction_arrow_app.jpg"
GOAL_STRATEGY_SITUATION_PATH = APP_ASSET_DIR / "ly_visual_goal_strategy_situation_app.jpg"
USE_HOMEPAGE_REFERENCE_IMAGE = True
DEVELOPER_NAME = "Young Lee"
DEVELOPER_EMAIL = "lyn0109@gmail.com"
APP_BUILD_STAMP = "2026-09-02-modern-visual-ui"
LIFE_ENTRY_VERSION = "life-homepage-2026-09-02-modern-visual-ui-v1"
MAX_DIARY_RESTORE_BYTES = 250_000
MAX_DIARY_RESTORE_ENTRIES = 50


@st.cache_data(show_spinner=False)
def image_data_uri(path_text: str) -> str:
    image_path = Path(path_text)
    if not image_path.exists():
        return ""
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(image_path.suffix.lower(), "image/png")
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_visual_asset_theme() -> None:
    app_bg = image_data_uri(str(APP_BACKGROUND_PATH))
    report_bg = image_data_uri(str(CLIENT_REPORT_BG_PATH))
    ontology_bg = image_data_uri(str(ONTOLOGY_BG_PATH))
    direction_bg = image_data_uri(str(DIRECTION_FLOW_BG_PATH))

    st.markdown(
        f"""
        <style>
        html body .stApp {{
            background:
                linear-gradient(90deg, rgba(15, 118, 110, 0.026) 1px, transparent 1px),
                linear-gradient(0deg, rgba(15, 118, 110, 0.020) 1px, transparent 1px),
                linear-gradient(135deg, #f7fbff 0%, #fbfdff 45%, #f8fafc 100%) !important;
            background-size: 72px 72px, 72px 72px, auto !important;
            color: #0f172a !important;
        }}
        html body .stApp,
        html body .stApp * {{
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Arial, sans-serif !important;
            letter-spacing: 0 !important;
        }}
        html body span[data-testid="stIconMaterial"],
        html body span[data-testid="stIconMaterial"] *,
        html body .material-symbols-rounded,
        html body .material-icons {{
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        }}
        html body .stApp .brand-name,
        html body .stApp .brand-icon span,
        html body .stApp .home-brand,
        html body .stApp .homepage-visual .life-title,
        html body .stApp .life-compact-panel h1 {{
            font-family: Century, "Century Schoolbook", Georgia, serif !important;
        }}
        html body .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.28), rgba(255,255,255,0.78)),
                url("{direction_bg}") center 88px / min(980px, 70vw) auto no-repeat !important;
            opacity: 0.10 !important;
            animation: none !important;
            clip-path: none !important;
        }}
        html body .stApp::after {{
            content: "";
            position: fixed;
            right: -160px !important;
            bottom: -120px !important;
            top: auto !important;
            width: min(620px, 48vw) !important;
            height: 360px !important;
            pointer-events: none;
            z-index: 0;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.55), rgba(255,255,255,0.18)),
                url("{report_bg}") right bottom / contain no-repeat !important;
            opacity: 0.07 !important;
            animation: none !important;
            clip-path: none !important;
        }}
        html body .stApp .block-container {{
            max-width: 1180px !important;
            padding-top: 0.8rem !important;
        }}
        html body .stApp .homepage-visual {{
            max-width: 1120px !important;
            min-height: 560px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(148, 163, 184, 0.20) !important;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.985) 0%, rgba(255,255,255,0.94) 56%, rgba(255,255,255,0.82) 100%),
                url("{app_bg}") right center / 56% auto no-repeat,
                #ffffff !important;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.085) !important;
            overflow: hidden !important;
        }}
        html body .stApp .homepage-visual.has-home-image::before {{
            display: block !important;
            opacity: 1 !important;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.99) 0%, rgba(255,255,255,0.93) 44%, rgba(255,255,255,0.64) 100%) !important;
        }}
        html body .stApp .homepage-visual.has-home-image .homepage-bg-img {{
            display: block !important;
            position: absolute !important;
            inset: 0 0 0 auto !important;
            width: 52% !important;
            height: 100% !important;
            object-fit: cover !important;
            object-position: center center !important;
            opacity: 0.16 !important;
            filter: saturate(0.82) contrast(0.98) !important;
        }}
        html body .stApp .home-flow-visual {{
            width: min(380px, 100%);
            margin: 18px 0 12px;
            border-radius: 8px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(148, 163, 184, 0.20);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.075);
        }}
        html body .stApp .home-flow-visual img {{
            display: block;
            width: 100%;
            height: auto;
            opacity: 0.94;
        }}
        html body .stApp .goal-compass {{
            display: none !important;
        }}
        html body .stApp .goal-compass-caption,
        html body .stApp .home-skip-link {{
            display: inline-flex !important;
            align-items: center;
            min-height: 28px;
            padding: 5px 10px;
            border-radius: 999px;
            color: #334155 !important;
            -webkit-text-fill-color: #334155 !important;
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(148, 163, 184, 0.18);
            backdrop-filter: blur(8px);
        }}
        html body .stApp .home-skip-link:hover,
        html body .stApp .home-skip-link:focus {{
            color: #0f766e !important;
            -webkit-text-fill-color: #0f766e !important;
            background: #ffffff;
            text-decoration: none !important;
        }}
        html body .stApp .home-nav {{
            border-bottom-color: rgba(148, 163, 184, 0.12) !important;
            background: rgba(255, 255, 255, 0.96) !important;
        }}
        html body .stApp .home-goal-layout {{
            grid-template-columns: minmax(0, 0.88fr) minmax(360px, 1fr) !important;
            gap: 34px !important;
            padding: 38px !important;
        }}
        html body .stApp .home-goal-card {{
            border-radius: 8px !important;
            background: rgba(255, 255, 255, 0.96) !important;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.055) !important;
            transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
        }}
        html body .stApp .home-goal-card:hover,
        html body .stApp .home-goal-card:focus-within {{
            transform: translateY(-2px);
            box-shadow: 0 16px 32px rgba(15, 23, 42, 0.095) !important;
        }}
        html body .stApp .brand-header {{
            background:
                linear-gradient(90deg, rgba(255,255,255,0.99), rgba(255,255,255,0.96)),
                #ffffff !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06) !important;
            overflow: hidden !important;
        }}
        html body .stApp .brand-header::after {{
            height: 2px !important;
            background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.52), rgba(15, 118, 110, 0.28), transparent) !important;
        }}
        html body .stApp .brand-mark {{
            isolation: isolate;
        }}
        html body .stApp .finance-snapshot-ribbon {{
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)) !important;
            gap: 10px !important;
        }}
        html body .stApp .finance-snapshot-card {{
            min-height: 94px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.050) !important;
        }}
        html body .stApp .finance-snapshot-card small,
        html body .stApp .client-report-text small {{
            font-size: 0.66rem !important;
            font-weight: 760 !important;
            color: #64748b !important;
        }}
        html body .stApp .finance-snapshot-card b,
        html body .stApp .client-report-text b {{
            font-weight: 800 !important;
            letter-spacing: 0 !important;
        }}
        html body .stApp .finance-snapshot-card em,
        html body .stApp .client-report-text em,
        html body .stApp .client-direction-step em {{
            font-weight: 560 !important;
            color: #64748b !important;
        }}
        html body .stApp .client-visual-report {{
            position: relative;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background:
                linear-gradient(90deg, rgba(255,255,255,0.99) 0%, rgba(255,255,255,0.97) 66%, rgba(255,255,255,0.86) 100%),
                url("{report_bg}") right center / 360px auto no-repeat,
                #ffffff !important;
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.065);
        }}
        html body .stApp .client-report-cards {{
            gap: 12px !important;
        }}
        html body .stApp .client-report-card,
        html body .stApp .finance-snapshot-card,
        html body .stApp .metric-card,
        html body .stApp .portfolio-score-card {{
            background: rgba(255, 255, 255, 0.982) !important;
            backdrop-filter: blur(10px);
            border-color: rgba(148, 163, 184, 0.18) !important;
        }}
        html body .stApp .client-report-card {{
            min-height: 132px !important;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.055) !important;
        }}
        html body .stApp .client-report-icon,
        html body .stApp .finance-snapshot-glyph {{
            border-radius: 8px !important;
            box-shadow: none !important;
        }}
        html body .stApp .client-report-meter,
        html body .stApp .finance-snapshot-meter {{
            height: 6px !important;
            background: #e8edf3 !important;
        }}
        html body .stApp .client-direction-rail {{
            min-height: 84px !important;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.985), rgba(255,255,255,0.92)),
                url("{direction_bg}") center center / 74% auto no-repeat,
                #ffffff !important;
            border-color: rgba(148, 163, 184, 0.16) !important;
        }}
        html body .stApp .nora-ontology {{
            background:
                linear-gradient(90deg, rgba(255,255,255,0.985), rgba(255,255,255,0.94)),
                url("{ontology_bg}") right center / 420px auto no-repeat,
                #ffffff !important;
            border-color: rgba(148, 163, 184, 0.16) !important;
        }}
        html body .stApp .nora-node {{
            background: rgba(255, 255, 255, 0.94) !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.040);
        }}
        html body section[data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(255,255,255,0.96), rgba(240, 249, 255, 0.92)) !important;
            border-right: 1px solid rgba(148, 163, 184, 0.18) !important;
        }}
        @media (max-width: 900px) {{
            html body .stApp {{
                background:
                    linear-gradient(90deg, rgba(15, 118, 110, 0.026) 1px, transparent 1px),
                    linear-gradient(0deg, rgba(15, 118, 110, 0.020) 1px, transparent 1px),
                    linear-gradient(135deg, #f7fbff 0%, #fbfdff 45%, #f8fafc 100%) !important;
            }}
            html body .stApp::before,
            html body .stApp::after {{
                display: none !important;
            }}
            html body .stApp .homepage-visual {{
                min-height: auto !important;
            }}
            html body .stApp .homepage-visual.has-home-image .homepage-bg-img {{
                display: none !important;
            }}
            html body .stApp .home-goal-layout {{
                grid-template-columns: 1fr !important;
                padding: 22px !important;
                gap: 18px !important;
            }}
            html body .stApp .client-visual-report,
            html body .stApp .client-direction-rail,
            html body .stApp .nora-ontology {{
                background: rgba(255, 255, 255, 0.96) !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def clean_hex_color(value: Any, fallback: str = "#0f766e") -> str:
    color = str(value or "").strip()
    return color if re.fullmatch(r"#[0-9A-Fa-f]{6}", color) else fallback


def visual_icon_kind(value: Any) -> str:
    key = re.sub(r"[^a-z0-9]+", "", str(value or "").lower())
    return {
        "ta": "goal",
        "target": "goal",
        "goal": "goal",
        "life": "life",
        "lf": "life",
        "runway": "runway",
        "ru": "runway",
        "finance": "finance",
        "fi": "finance",
        "portfolio": "portfolio",
        "pf": "portfolio",
        "po": "portfolio",
        "reit": "estate",
        "realestate": "estate",
        "re": "estate",
        "property": "estate",
        "risk": "risk",
        "ri": "risk",
        "rsk": "risk",
        "scenario": "scenario",
        "sc": "scenario",
        "advisor": "case",
        "casestudies": "case",
        "case": "case",
        "cs": "case",
        "ar": "case",
        "diary": "memory",
        "memory": "memory",
        "dy": "memory",
        "mem": "memory",
        "search": "search",
        "sr": "search",
        "compare": "compare",
        "cp": "compare",
        "details": "model",
        "dt": "model",
        "model": "model",
        "mod": "model",
        "data": "data",
        "dat": "data",
        "evidence": "evidence",
        "evd": "evidence",
        "decision": "decision",
        "dec": "decision",
        "capture": "capture",
        "cap": "capture",
        "action": "action",
        "act": "action",
        "outcome": "outcome",
        "out": "outcome",
        "ai": "ai",
        "settings": "settings",
        "se": "settings",
        "guide": "guide",
        "gd": "guide",
        "language": "language",
    }.get(key, "data")


def visual_icon_svg(kind: Any, accent: str = "#0f766e", secondary: str = "#2563eb") -> str:
    kind = visual_icon_kind(kind)
    primary = clean_hex_color(accent)
    secondary = clean_hex_color(secondary, "#2563eb")
    common = (
        f'<defs><linearGradient id="g" x1="8" y1="6" x2="56" y2="58">'
        f'<stop offset="0" stop-color="{primary}"/><stop offset="1" stop-color="{secondary}"/>'
        f'</linearGradient></defs>'
        '<rect x="3" y="3" width="58" height="58" rx="16" fill="url(#g)"/>'
        '<circle cx="18" cy="15" r="9" fill="#ffffff" opacity=".22"/>'
    )
    drawings = {
        "goal": '<circle cx="32" cy="32" r="16" fill="none" stroke="#fff" stroke-width="4"/><circle cx="32" cy="32" r="7" fill="#fff"/><path d="M39 25l11-11M43 14h7v7" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>',
        "life": '<path d="M32 48C20 39 14 32 14 24c0-6 4-10 10-10 4 0 7 2 8 5 1-3 4-5 8-5 6 0 10 4 10 10 0 8-6 15-18 24z" fill="#fff" opacity=".94"/>',
        "runway": '<path d="M13 43h38" stroke="#fff" stroke-width="5" stroke-linecap="round"/><path d="M16 34l8-9 8 6 9-13 8 8" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="24" cy="25" r="4" fill="#fff"/><circle cx="41" cy="18" r="4" fill="#fff"/>',
        "finance": '<path d="M16 45h32a5 5 0 005-5V26a5 5 0 00-5-5H16a5 5 0 00-5 5v14a5 5 0 005 5z" fill="none" stroke="#fff" stroke-width="4"/><path d="M38 33h13" stroke="#fff" stroke-width="5" stroke-linecap="round"/><circle cx="22" cy="33" r="5" fill="#fff"/>',
        "portfolio": '<path d="M33 13a19 19 0 11-18 25h18z" fill="#fff" opacity=".92"/><path d="M36 13a19 19 0 0116 16H36z" fill="#fff" opacity=".54"/><circle cx="33" cy="33" r="7" fill="url(#g)"/>',
        "estate": '<path d="M13 31l19-16 19 16" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 29v20h26V29" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><path d="M29 49V37h7v12" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
        "risk": '<path d="M32 13l22 39H10z" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round"/><path d="M32 25v13" stroke="#fff" stroke-width="5" stroke-linecap="round"/><circle cx="32" cy="45" r="3" fill="#fff"/>',
        "scenario": '<path d="M14 32h9c7 0 9-12 18-12h9" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/><path d="M14 32h9c7 0 9 12 18 12h9" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/><path d="M45 14l7 6-7 6M45 38l7 6-7 6" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>',
        "case": '<rect x="16" y="14" width="32" height="38" rx="6" fill="#fff" opacity=".92"/><path d="M23 25h18M23 33h18M23 41h11" stroke="url(#g)" stroke-width="4" stroke-linecap="round"/><circle cx="42" cy="44" r="7" fill="url(#g)"/>',
        "memory": '<path d="M18 13h25a5 5 0 015 5v33H18a5 5 0 01-5-5V18a5 5 0 015-5z" fill="#fff" opacity=".9"/><path d="M24 13v20l6-5 6 5V13" fill="url(#g)"/><path d="M23 42h18" stroke="url(#g)" stroke-width="4" stroke-linecap="round"/>',
        "search": '<circle cx="28" cy="28" r="13" fill="none" stroke="#fff" stroke-width="5"/><path d="M39 39l12 12" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
        "compare": '<path d="M17 46V26M32 46V16M47 46V34" stroke="#fff" stroke-width="8" stroke-linecap="round"/><path d="M13 48h38" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
        "model": '<circle cx="32" cy="32" r="13" fill="none" stroke="#fff" stroke-width="5"/><circle cx="32" cy="32" r="4" fill="#fff"/><path d="M32 11v8M32 45v8M11 32h8M45 32h8M17 17l6 6M41 41l6 6M47 17l-6 6M23 41l-6 6" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
        "data": '<rect x="15" y="15" width="34" height="34" rx="7" fill="none" stroke="#fff" stroke-width="4"/><path d="M24 24h16M24 32h16M24 40h10" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
        "evidence": '<path d="M16 34l10 10 22-25" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 18h22" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".65"/>',
        "decision": '<path d="M15 33h26" stroke="#fff" stroke-width="5" stroke-linecap="round"/><path d="M34 22l11 11-11 11" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="20" cy="20" r="5" fill="#fff" opacity=".75"/><circle cx="20" cy="46" r="5" fill="#fff" opacity=".75"/>',
        "capture": '<path d="M15 18h34a6 6 0 016 6v13a6 6 0 01-6 6H32l-10 8v-8h-7a6 6 0 01-6-6V24a6 6 0 016-6z" fill="#fff" opacity=".9"/><path d="M21 29h22M21 36h14" stroke="url(#g)" stroke-width="4" stroke-linecap="round"/>',
        "action": '<path d="M15 47l34-30" stroke="#fff" stroke-width="6" stroke-linecap="round"/><path d="M35 16h15v15" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
        "outcome": '<path d="M14 45h38" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".7"/><path d="M16 40l9-10 8 5 13-18" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="25" cy="30" r="4" fill="#fff"/><circle cx="46" cy="17" r="4" fill="#fff"/>',
        "ai": '<circle cx="20" cy="24" r="6" fill="#fff"/><circle cx="44" cy="24" r="6" fill="#fff"/><circle cx="32" cy="44" r="6" fill="#fff"/><path d="M25 27l14 14M39 27L25 41M26 24h12" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".72"/>',
        "settings": '<path d="M18 22h28M18 32h28M18 42h28" stroke="#fff" stroke-width="4" stroke-linecap="round"/><circle cx="27" cy="22" r="5" fill="#fff"/><circle cx="39" cy="32" r="5" fill="#fff"/><circle cx="30" cy="42" r="5" fill="#fff"/>',
        "guide": '<path d="M18 13h24l8 8v30H18z" fill="#fff" opacity=".92"/><path d="M42 13v10h10M25 31h17M25 39h17" stroke="url(#g)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>',
        "language": '<circle cx="32" cy="32" r="18" fill="none" stroke="#fff" stroke-width="4"/><path d="M14 32h36M32 14c7 7 7 29 0 36M32 14c-7 7-7 29 0 36" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
    }
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{common}{drawings.get(kind, drawings["data"])}</svg>'


def svg_data_uri(svg_text: str) -> str:
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def visual_icon_html(kind: Any, accent: str = "#0f766e", class_name: str = "visual-icon", title: str = "") -> str:
    title_attr = f' title="{escape(title, quote=True)}"' if title else ""
    return (
        f'<img class="{escape(class_name, quote=True)}" '
        f'src="{svg_data_uri(visual_icon_svg(kind, accent))}" alt="" aria-hidden="true"{title_attr}>'
    )


def brand_logo_html() -> str:
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
        <defs>
            <linearGradient id="brand" x1="12" y1="10" x2="84" y2="88">
                <stop offset="0" stop-color="#0f766e"/>
                <stop offset=".52" stop-color="#0891b2"/>
                <stop offset="1" stop-color="#2563eb"/>
            </linearGradient>
        </defs>
        <rect x="5" y="5" width="86" height="86" rx="24" fill="url(#brand)"/>
        <circle cx="28" cy="24" r="13" fill="#fff" opacity=".22"/>
        <path d="M20 68c16-24 34-33 56-38" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity=".32"/>
        <text x="49" y="61" text-anchor="middle" fill="#ffffff"
              font-family="Century, Century Schoolbook, Georgia, serif"
              font-size="38" font-style="italic" font-weight="700" letter-spacing="-1">LY</text>
    </svg>
    """
    return f'<img class="brand-logo-image" src="{svg_data_uri(dedent(svg))}" alt="LY">'


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
    st.session_state.setdefault("google_feedback_form_url", GOOGLE_FEEDBACK_FORM_URL)
    st.session_state.setdefault("google_feedback_form_url_draft", GOOGLE_FEEDBACK_FORM_URL)
    st.session_state.setdefault("comment_saved_notice", False)
    st.session_state.setdefault("decision_capture_text", "")
    st.session_state.setdefault("decision_capture_amount_text", "")
    st.session_state.setdefault("decision_capture_draft", None)
    st.session_state.setdefault("decision_capture_saved_notice", False)
    st.session_state.setdefault("decision_outcome_saved_notice", False)
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


def fmt_money_compact(value: float | int | None, currency: str = "USD", language: str | None = None) -> str:
    if value is None:
        return "N/A"
    language = language or current_language()
    amount = float(value)
    absolute = abs(amount)
    sign = "-" if amount < 0 else ""
    if currency == "KRW":
        if language == "ko" and absolute >= 100_000_000:
            return f"{sign}{absolute / 100_000_000:.1f}억"
        if absolute >= 1_000_000_000:
            return f"{sign}₩{absolute / 1_000_000_000:.1f}B"
        if absolute >= 1_000_000:
            return f"{sign}₩{absolute / 1_000_000:.1f}M"
        return f"{sign}₩{absolute:,.0f}"
    if absolute >= 1_000_000_000:
        return f"{sign}${absolute / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"{sign}${absolute / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{sign}${absolute / 1_000:.1f}K"
    return f"{sign}${absolute:,.0f}"


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
    return calculate_valuation(stock)


def load_yahoo_stock(query: str) -> dict[str, Any]:
    symbol = query.strip().upper()
    if not symbol:
        raise ValueError("Enter a ticker symbol.")

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
        raise ValueError(f"Yahoo Finance did not return a current price for {symbol}. Try the ticker symbol directly.")

    previous = closes[-2] if len(closes) >= 2 else positive_float(info.get("previousClose")) or price
    change_pct = ((price - previous) / previous * 100) if price and previous else 0.0
    market_cap = info.get("marketCap")
    market_cap_millions = float(market_cap) / 1_000_000 if market_cap else None
    trailing_eps = positive_float(info.get("trailingEps")) or 0
    book_value = positive_float(info.get("bookValue")) or 0
    dividend_rate = positive_float(info.get("dividendRate")) or 0
    dividend_yield = float(info.get("dividendYield") or 0) * 100
    pe = positive_float(info.get("trailingPE")) or positive_float(info.get("forwardPE"))
    beta = positive_float(info.get("beta")) or 1.0
    growth_rate = info.get("earningsGrowth")
    if growth_rate is None:
        growth_rate = info.get("revenueGrowth")
    if growth_rate is None:
        growth_rate = 0.05

    stock = {
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName") or symbol,
        "industry": info.get("industry") or info.get("sector") or "Equity",
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
        "peer_average_pe": pe if pe and 0 < float(pe) < 100 else 15.0,
        "peers": [],
        "market": "US",
        "currency": info.get("currency") or "USD",
        "data_quality": "Yahoo Finance fallback price history",
    }
    return calculate_valuation(stock)


def load_stock(query: str) -> dict[str, Any]:
    korean_symbol = resolve_korean_ticker(query)
    if korean_symbol:
        return load_korean_stock(korean_symbol)

    if not FINNHUB_API_KEY:
        return load_yahoo_stock(query)

    try:
        symbol = resolve_ticker(query)
        profile = finnhub_get("stock/profile2", symbol=symbol)
        quote = finnhub_get("quote", symbol=symbol)
        metric = safe_metric(symbol)
        peer_pe, peers = average_peer_pe(symbol)
    except Exception:
        return load_yahoo_stock(query)

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
    level_html = ""
    value_text = str(value)
    score_match = re.search(r"(-?\d+(?:\.\d+)?)\s*/\s*100", value_text)
    pct_match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", value_text)
    if score_match:
        level = max(0.0, min(100.0, float(score_match.group(1))))
        level_html = f'<div class="metric-card-meter"><span style="--level:{level:.0f}%;"></span></div>'
    elif pct_match:
        pct_value = float(pct_match.group(1))
        if 0 <= pct_value <= 100:
            level_html = f'<div class="metric-card-meter"><span style="--level:{pct_value:.0f}%;"></span></div>'
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{escape(str(label))}</div>
            <div class="value" style="color:{escape(str(color))};">{escape(value_text)}</div>
            {level_html}
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
                        <span class="portfolio-valuation-chip">{ui_html('Price')} {escape(price_display)}</span>
                        <span class="portfolio-valuation-chip">{ui_html('Fair')} {escape(fair_value)}</span>
                        <span class="portfolio-valuation-chip">PER {escape(fmt_number(pe))}</span>
                        <span class="portfolio-valuation-chip">{ui_html(data_quality)}</span>
                    </div>
                </div>
                <span class="portfolio-valuation-status" style="background:{status_color(str(stock.get("valuation_status", "Fair Value")))};">
                    {ui_html(str(stock.get("valuation_status", "N/A")))}
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
            <span class="portfolio-sr-icon" aria-hidden="true">{visual_icon_html("search", "#0f766e", "portfolio-sr-image-icon")}</span>
            <b>{ui_html('Portfolio Search')}</b>
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
        st.info(
            "FINNHUB_API_KEY is not configured, so LY-Scope-Ver.2 uses Yahoo Finance fallback data "
            "for ticker-based stock search. Add FINNHUB_API_KEY in Streamlit Cloud Secrets for richer "
            "company search, peer metrics, and live Finnhub fields."
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

    covariance = returns.cov()
    portfolio_variance = float(weights.T.dot(covariance).dot(weights))
    portfolio_daily_returns = returns.mul(weights, axis=1).sum(axis=1)
    daily_vol = float(portfolio_daily_returns.std())
    covariance_daily_vol = portfolio_variance ** 0.5 if portfolio_variance > 0 else 0.0
    annual_vol = daily_vol * (252 ** 0.5)
    historical_annual_return = float(portfolio_daily_returns.mean()) * 252
    correlation = returns.corr()
    weighted_individual_daily_vol = float((returns.std() * weights).sum())
    diversification_benefit = max(0.0, weighted_individual_daily_vol - daily_vol)

    return {
        "returns": returns,
        "weights": weights,
        "covariance": covariance,
        "correlation": correlation,
        "portfolio_variance": portfolio_variance,
        "daily_vol": daily_vol,
        "covariance_daily_vol": covariance_daily_vol,
        "annual_vol": annual_vol,
        "annual_return": historical_annual_return,
        "historical_annual_return": historical_annual_return,
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
        metric_card("Historical Annualized Return", f"{risk['historical_annual_return'] * 100:+.1f}%", "#60a5fa")
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
            "historical_annual_return": risk["historical_annual_return"],
            "expected_annual_return": risk["historical_annual_return"],
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
        "decision_capture": st.session_state.get("decision_capture_draft") or None,
        "outcome_review": {},
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
    decision_capture = st.session_state.get("decision_capture_draft") or {}

    missing: list[str] = []
    if not decision_capture:
        missing.append("Decision capture draft")
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
        "decision_capture": decision_capture,
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
    decision_capture = context.get("decision_capture") or {}

    score = 0.0
    reasons: list[str] = []

    if decision_capture:
        score += 4
        reasons.append("Decision capture draft exists.")
    else:
        reasons.append("Decision capture draft is missing.")

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
    decision_capture = st.session_state.get("decision_capture_draft") or {}

    evidence_count = sum(bool(item) for item in (decision_capture, personal, holdings, stocks, scenario))
    evidence_score = 30 + min(evidence_count, 5) * 12
    model_score = 74 if personal or stocks or scenario else 40
    risk_score = 86 if scenario else 68 if personal or holdings else 38
    memory_score = 88 if diary else 42

    if language == "ko":
        capture_detail = "고객의 고민이 결정 초안으로 포착되었습니다." if decision_capture else "아직 고객의 고민이 Capture되지 않았습니다."
        purpose_detail = "목표가 선택되어 판단 기준이 선명합니다." if goal else "아직 목표가 없어 판단 기준이 흔들릴 수 있습니다."
        evidence_detail = f"현재 근거 입력 {evidence_count}/5: Capture, 재무, 포트폴리오, 종목, 시나리오."
        decision_detail = "결정 초안이 있어 행동 전 검토할 수 있습니다." if decision_capture else "결정 초안이 없어 해석이 행동으로 연결되기 어렵습니다."
        model_detail = "모델 결과가 존재해 해석 전 계산 기준을 확인할 수 있습니다." if model_score >= 70 else "아직 모델 결과가 부족해 해석보다 입력이 먼저입니다."
        risk_detail = "시나리오까지 포함되어 위험을 먼저 점검합니다." if scenario else "위험 점검은 시작됐지만 시나리오 스트레스가 아직 약합니다."
        memory_detail = "다이어리/기록이 있어 판단을 나중에 되돌아볼 수 있습니다." if diary else "아직 기록이 없어 같은 판단을 반복 검증하기 어렵습니다."
    else:
        capture_detail = "The user's decision question has been captured as a draft." if decision_capture else "No decision question has been captured yet."
        purpose_detail = "A selected goal makes the judgment standard clearer." if goal else "No selected goal yet, so the judgment standard can drift."
        evidence_detail = f"Current evidence inputs {evidence_count}/5: capture, finance, portfolio, stock, scenario."
        decision_detail = "A decision draft exists, so action can be reviewed before commitment." if decision_capture else "No decision draft exists, so interpretation is harder to turn into action."
        model_detail = "Model output exists, so calculations can be checked before interpretation." if model_score >= 70 else "Model output is still thin; inputs should come before interpretation."
        risk_detail = "Scenario stress is included, so risk is checked before action." if scenario else "Risk review has started, but scenario stress is still weak."
        memory_detail = "Diary or report memory exists for later review." if diary else "No memory yet, so repeated judgment is harder to audit."

    pillars = [
        {"glyph": "CAP", "label": "Capture Quality", "score": 90 if decision_capture else 35, "detail": capture_detail},
        {"glyph": "WHY", "label": "Purpose Fit", "score": 92 if goal else 42, "detail": purpose_detail},
        {"glyph": "EVD", "label": "Evidence Quality", "score": evidence_score, "detail": evidence_detail},
        {"glyph": "MOD", "label": "Model Discipline", "score": model_score, "detail": model_detail},
        {"glyph": "RSK", "label": "Risk Awareness", "score": risk_score, "detail": risk_detail},
        {"glyph": "DEC", "label": "Decision Draft", "score": 86 if decision_capture else 38, "detail": decision_detail},
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


COMMON_DECISION_SYMBOLS = {
    "tesla": "TSLA",
    "tsla": "TSLA",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "apple": "AAPL",
    "aapl": "AAPL",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "meta": "META",
    "johnson": "JNJ",
    "jnj": "JNJ",
    "voo": "VOO",
    "spy": "SPY",
    "schd": "SCHD",
    "삼성전자": "005930.KS",
    "삼성": "005930.KS",
    "하이닉스": "000660.KS",
    "sk하이닉스": "000660.KS",
    "현대차": "005380.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS",
}


def decision_text(language: str, en: str, ko: str) -> str:
    return ko if language == "ko" else en


def decision_goal_label(goal_key: str | None, language: str) -> str:
    goal_key = normalized_goal_key(goal_key)
    if not goal_key:
        return decision_text(language, "Goal not selected", "목표 미선택")
    config = NORA_GOAL_STRATEGIES[goal_key]
    return str(config[f"label_{language}"])


def parse_capture_amount(text: str) -> tuple[float | None, str]:
    clean = text.strip()
    if not clean:
        return None, "USD"

    normalized = clean.replace(",", "")
    won_match = re.search(r"(\d+(?:\.\d+)?)\s*억", normalized)
    if won_match:
        return float(won_match.group(1)) * 100_000_000, "KRW"

    manwon_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:만\s*원|만원|만)", normalized)
    if manwon_match:
        return float(manwon_match.group(1)) * 10_000, "KRW"

    krw_match = re.search(r"(?:₩|krw|원)\s*(\d+(?:\.\d+)?)", normalized, flags=re.IGNORECASE)
    if krw_match:
        return float(krw_match.group(1)), "KRW"

    usd_match = re.search(r"(?:\$|usd)\s*(\d+(?:\.\d+)?)", normalized, flags=re.IGNORECASE)
    if usd_match:
        return float(usd_match.group(1)), "USD"

    trailing_usd = re.search(r"(\d+(?:\.\d+)?)\s*(?:usd|달러)", normalized, flags=re.IGNORECASE)
    if trailing_usd:
        return float(trailing_usd.group(1)), "USD"

    trailing_krw = re.search(r"(\d+(?:\.\d+)?)\s*(?:krw|원)", normalized, flags=re.IGNORECASE)
    if trailing_krw:
        return float(trailing_krw.group(1)), "KRW"

    return None, st.session_state.get("portfolio_base_currency", "USD")


def extract_decision_symbols(text: str) -> list[str]:
    clean = text.strip()
    lower = clean.lower()
    symbols: list[str] = []

    def add(symbol: str) -> None:
        symbol = symbol.strip().upper()
        if symbol and symbol not in symbols:
            symbols.append(symbol)

    for hint, symbol in COMMON_DECISION_SYMBOLS.items():
        if hint in lower:
            add(symbol)

    for symbol, stock in st.session_state.get("stocks", {}).items():
        if symbol.lower() in lower or str(stock.get("name", "")).lower() in lower:
            add(symbol)

    for symbol in st.session_state.get("portfolio", {}).keys():
        stock = st.session_state.get("stocks", {}).get(symbol, {})
        if symbol.lower() in lower or str(stock.get("name", "")).lower() in lower:
            add(symbol)

    excluded = {
        "A",
        "AI",
        "AM",
        "AND",
        "API",
        "BUT",
        "DCF",
        "ETF",
        "I",
        "IF",
        "KRW",
        "LY",
        "NORA",
        "OR",
        "PBR",
        "PER",
        "REIT",
        "THE",
        "USD",
    }
    single_letter_tickers = {"C", "F", "O", "T", "V"}
    for token in re.findall(r"\b[A-Z]{1,5}(?:\.[A-Z]{2})?\b", clean):
        upper = token.upper()
        if upper in excluded:
            continue
        if len(upper) == 1 and upper not in single_letter_tickers:
            continue
        add(upper)

    korean_symbol = resolve_korean_ticker(clean)
    if korean_symbol:
        add(korean_symbol)

    return symbols[:5]


def infer_decision_kind(text: str, symbols: list[str]) -> str:
    lower = text.lower()
    real_estate_terms = (
        "house",
        "home",
        "mortgage",
        "property",
        "real estate",
        "부동산",
        "주택",
        "아파트",
        "콘도",
        "집값",
        "내집",
        "전세",
        "월세",
        "모기지",
    )
    if any(word in lower for word in real_estate_terms):
        return "real_estate"
    if any(word in lower for word in ("debt", "loan", "pay off", "repay", "부채", "대출", "상환")):
        return "debt_cash"
    if any(word in lower for word in ("sell", "reduce", "trim", "exit", "매도", "줄이", "정리")):
        return "reduce_sell"
    if any(word in lower for word in ("buy", "add", "purchase", "increase", "추가", "매수", "늘리")) or symbols:
        return "add_buy"
    if any(word in lower for word in ("income", "job", "career", "study", "tuition", "소득", "직장", "커리어", "학업")):
        return "income_path"
    return "decision_review"


def infer_capture_goal(text: str, decision_kind: str) -> str | None:
    active = active_goal_key()
    if active:
        return active
    lower = text.lower()
    if decision_kind == "real_estate":
        return "real_estate_plan"
    if decision_kind == "income_path":
        return "build_income"
    if decision_kind == "debt_cash":
        return "protect_runway"
    if any(word in lower for word in ("cash", "runway", "emergency", "expense", "liquidity", "no income", "현금", "유동성", "비상", "소득이", "수입이")):
        return "protect_runway"
    if decision_kind in {"add_buy", "reduce_sell"} or any(word in lower for word in ("stock", "portfolio", "invest", "주식", "투자", "포트폴리오")):
        return "grow_capital"
    return None


def decision_kind_label(kind: str, language: str) -> str:
    labels = {
        "add_buy": ("Add or buy investment", "투자 추가/매수"),
        "reduce_sell": ("Reduce or sell investment", "투자 축소/매도"),
        "real_estate": ("Real estate decision", "부동산 의사결정"),
        "debt_cash": ("Debt versus cash decision", "부채 상환/현금 선택"),
        "income_path": ("Income path decision", "소득 경로 의사결정"),
        "decision_review": ("Decision review", "의사결정 검토"),
    }
    en, ko = labels.get(kind, labels["decision_review"])
    return decision_text(language, en, ko)


def build_decision_capture_draft(statement: str, amount_text: str = "") -> dict[str, Any]:
    language = current_language()
    clean_statement = compact_text(statement, 1200)
    amount, amount_currency = parse_capture_amount(f"{statement} {amount_text}")
    symbols = extract_decision_symbols(statement)
    kind = infer_decision_kind(statement, symbols)
    goal_key = infer_capture_goal(statement, kind)
    goal_label = decision_goal_label(goal_key, language)
    holdings = portfolio_holdings_snapshot()
    total_value, weighted_beta, valuation_score, _ = portfolio_metrics()
    personal = st.session_state.get("last_personal_finance_result") or {}
    scenario = st.session_state.get("last_scenario_packet")
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M")
    review_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    if kind == "add_buy":
        decision_line = decision_text(language, "Review before adding risk", "위험 추가 전 검토")
        benefit = decision_text(language, "Potential upside if the thesis is right.", "가정이 맞을 경우 상승 기회.")
        default_risk = decision_text(language, "Cash runway and concentration can weaken.", "현금 생존기간과 집중도가 약해질 수 있음.")
        next_step = decision_text(language, "Check 12-month cash needs, position size, and downside scenario before action.", "실행 전 12개월 현금수요, 포지션 크기, 하락 시나리오를 확인하세요.")
    elif kind == "reduce_sell":
        decision_line = decision_text(language, "Review partial reduction", "부분 축소 검토")
        benefit = decision_text(language, "Risk and concentration may fall.", "위험과 집중도가 낮아질 수 있음.")
        default_risk = decision_text(language, "Selling may reduce future upside or create tax impact.", "매도는 미래 상승 여력이나 세금에 영향을 줄 수 있음.")
        next_step = decision_text(language, "Compare hold, partial trim, and full trim before deciding.", "보유, 부분 축소, 전량 축소를 비교하세요.")
    elif kind == "real_estate":
        decision_line = decision_text(language, "Review affordability and rate risk", "구매여력과 금리 위험 검토")
        benefit = decision_text(language, "A property plan can support stability or long-term wealth.", "부동산 계획은 안정성 또는 장기 자산 형성에 기여할 수 있음.")
        default_risk = decision_text(language, "Debt, taxes, insurance, maintenance, and liquidity risk can dominate.", "부채, 세금, 보험, 유지비, 유동성 위험이 커질 수 있음.")
        next_step = decision_text(language, "Compare monthly ownership cost with rent and emergency reserve.", "월 보유비용, 임대비용, 비상자금을 비교하세요.")
    elif kind == "debt_cash":
        decision_line = decision_text(language, "Compare payoff versus liquidity", "상환과 유동성 비교")
        benefit = decision_text(language, "Debt pressure may fall.", "부채 압력이 낮아질 수 있음.")
        default_risk = decision_text(language, "Using too much cash can weaken resilience.", "현금을 과도하게 쓰면 회복력이 약해질 수 있음.")
        next_step = decision_text(language, "Keep emergency cash visible before any payoff decision.", "상환 전 비상현금 수준을 먼저 확인하세요.")
    elif kind == "income_path":
        decision_line = decision_text(language, "Review income bridge", "소득 브릿지 검토")
        benefit = decision_text(language, "A clearer income path can protect long-term planning.", "명확한 소득 경로는 장기 계획을 보호할 수 있음.")
        default_risk = decision_text(language, "Runway can shorten if expenses are not updated.", "지출이 갱신되지 않으면 생존기간이 짧아질 수 있음.")
        next_step = decision_text(language, "Update monthly expenses and target runway.", "월 지출과 목표 생존기간을 갱신하세요.")
    else:
        decision_line = decision_text(language, "Turn the thought into a decision draft", "생각을 결정 초안으로 전환")
        benefit = decision_text(language, "The decision becomes easier to audit.", "의사결정을 나중에 검토하기 쉬워짐.")
        default_risk = decision_text(language, "The issue is still too broad for a confident reading.", "아직 범위가 넓어 확신도 높은 판단이 어려움.")
        next_step = decision_text(language, "Add the decision amount, deadline, and main constraint.", "결정 금액, 기한, 핵심 제약조건을 추가하세요.")

    user_concern = default_risk
    lower = statement.lower()
    if any(word in lower for word in ("cash", "liquidity", "runway", "현금", "유동성", "생존")):
        user_concern = decision_text(language, "The user's own concern is cash or liquidity pressure.", "사용자가 직접 말한 우려는 현금 또는 유동성 압력입니다.")
    elif any(word in lower for word in ("risk", "drawdown", "loss", "위험", "손실", "하락")):
        user_concern = decision_text(language, "The user's own concern is downside or loss risk.", "사용자가 직접 말한 우려는 하락 또는 손실 위험입니다.")

    verified_data: list[str] = []
    if goal_key:
        verified_data.append(decision_text(language, f"Selected goal: {goal_label}", f"선택 목표: {goal_label}"))
    if total_value > 0:
        verified_data.append(
            decision_text(
                language,
                f"Portfolio value: {fmt_money_compact(total_value, base_currency, language)}",
                f"포트폴리오 가치: {fmt_money_compact(total_value, base_currency, language)}",
            )
        )
    if weighted_beta:
        verified_data.append(decision_text(language, f"Weighted beta: {fmt_number(weighted_beta)}", f"가중 베타: {fmt_number(weighted_beta)}"))
    if valuation_score is not None:
        verified_data.append(decision_text(language, f"Portfolio valuation: {valuation_score:+.1f}%", f"포트폴리오 valuation: {valuation_score:+.1f}%"))
    if personal:
        verified_data.append(
            decision_text(
                language,
                f"Runway: {float(personal.get('emergency_months', 0)):.1f} months",
                f"생존기간: {float(personal.get('emergency_months', 0)):.1f}개월",
            )
        )

    symbol_notes: list[str] = []
    weights = portfolio_analysis_weights()
    for symbol in symbols:
        if symbol in weights:
            symbol_notes.append(
                decision_text(
                    language,
                    f"{symbol} weight: {weights[symbol] * 100:.1f}%",
                    f"{symbol} 비중: {weights[symbol] * 100:.1f}%",
                )
            )
    verified_data.extend(symbol_notes)
    if scenario:
        verified_data.append(decision_text(language, "Scenario packet exists.", "시나리오 패킷이 있습니다."))

    not_verified = []
    if not personal:
        not_verified.append(decision_text(language, "12-month cash need has not been calculated.", "12개월 현금수요가 아직 계산되지 않았습니다."))
    if not scenario:
        not_verified.append(decision_text(language, "Downside scenario has not been run.", "하락 시나리오가 아직 실행되지 않았습니다."))
    if amount is None:
        not_verified.append(decision_text(language, "Decision amount is not explicit.", "결정 금액이 명확하지 않습니다."))
    if symbols and any(symbol not in st.session_state.get("stocks", {}) for symbol in symbols):
        not_verified.append(decision_text(language, "Some mentioned tickers are not loaded in the app.", "언급된 일부 티커가 앱에 로드되지 않았습니다."))
    not_verified.append(decision_text(language, "Tax impact, time horizon, and loss tolerance still need user confirmation.", "세금 영향, 투자기간, 손실감내 수준은 사용자 확인이 필요합니다."))

    interpretations = []
    if not verified_data:
        interpretations.append(decision_text(language, "The draft is mostly based on the user's statement, not app data yet.", "현재 초안은 앱 데이터보다 사용자 발언에 더 크게 의존합니다."))
    if symbol_notes:
        heavy = [note for note in symbol_notes if re.search(r"([4-9]\d|\d{3,})\.\d%", note)]
        if heavy:
            interpretations.append(decision_text(language, "A mentioned holding may already be a large portfolio driver.", "언급된 종목이 이미 포트폴리오의 큰 동인일 수 있습니다."))
    if valuation_score is not None and valuation_score < -5:
        interpretations.append(decision_text(language, "The current valued portfolio appears expensive versus the app's blended fair value estimate.", "현재 valuation 기준 포트폴리오는 앱의 혼합 적정가 대비 비싸게 보입니다."))
    if not scenario:
        interpretations.append(decision_text(language, "The decision should remain a draft until at least one downside case is visible.", "최소 하나의 하락 케이스가 보이기 전까지는 결정 초안으로 유지하는 편이 좋습니다."))
    if not interpretations:
        interpretations.append(decision_text(language, "The app has enough context to compare options, but the user should confirm assumptions.", "옵션 비교에 필요한 맥락은 있으나 가정은 사용자가 확인해야 합니다."))

    amount_label = (
        decision_text(language, "Needs amount", "금액 필요")
        if amount is None
        else fmt_money_compact(amount, amount_currency, language)
    )
    negative_amount = (
        decision_text(language, "Needs amount", "금액 필요")
        if amount is None
        else fmt_money_compact(-amount, amount_currency, language)
    )
    half_amount = (
        decision_text(language, "Partial amount", "부분 금액")
        if amount is None
        else fmt_money_compact(-amount * 0.5, amount_currency, language)
    )
    scenario_rows = [
        {
            "scenario": decision_text(language, "Act now", "지금 실행"),
            "benefit": benefit,
            "risk": user_concern,
            "cash_impact": negative_amount,
            "reversible": decision_text(language, "Partial", "부분 가능"),
        },
        {
            "scenario": decision_text(language, "Partial action", "부분 실행"),
            "benefit": decision_text(language, "Keeps optionality.", "선택지를 유지."),
            "risk": decision_text(language, "Upside and conviction are both reduced.", "상승 여력과 확신이 모두 줄어듦."),
            "cash_impact": half_amount,
            "reversible": decision_text(language, "More flexible", "더 유연"),
        },
        {
            "scenario": decision_text(language, "Wait and review", "보류 후 검토"),
            "benefit": decision_text(language, "Protects liquidity and gives time for evidence.", "유동성을 보호하고 근거를 확인할 시간 확보."),
            "risk": decision_text(language, "Opportunity may pass.", "기회를 놓칠 수 있음."),
            "cash_impact": fmt_money_compact(0, amount_currency, language) if amount is not None else "0",
            "reversible": decision_text(language, "Yes", "가능"),
        },
    ]

    action_items = [
        next_step,
        decision_text(language, "Separate user belief from verified data before acting.", "행동 전 사용자 믿음과 검증 데이터를 분리하세요."),
        decision_text(language, "Save this draft as a Memory checkpoint after review.", "검토 후 이 초안을 메모리 체크포인트로 저장하세요."),
    ]
    if symbols:
        action_items.insert(1, decision_text(language, f"Open Portfolio/Search for {', '.join(symbols)} valuation.", f"{', '.join(symbols)} valuation을 Portfolio/Search에서 확인하세요."))

    confidence = decision_text(language, "Moderate", "중간") if personal and (holdings or symbols) else decision_text(language, "Low", "낮음")
    return {
        "display_language": language,
        "created_at": now_text,
        "user_statement": clean_statement,
        "amount_text": compact_text(amount_text, 140),
        "decision_kind": kind,
        "decision_kind_label": decision_kind_label(kind, language),
        "proposed_decision": decision_line,
        "goal_key": goal_key,
        "goal_label": goal_label,
        "symbols": symbols,
        "amount": amount,
        "amount_currency": amount_currency,
        "amount_label": amount_label,
        "main_benefit": benefit,
        "main_risk": user_concern,
        "recommended_next_step": next_step,
        "review_date": review_date,
        "confidence": confidence,
        "user_reported": [clean_statement],
        "verified_data": verified_data or [decision_text(language, "No app-verified data attached yet.", "아직 앱 검증 데이터가 연결되지 않았습니다.")],
        "ai_interpretation": interpretations,
        "not_verified": not_verified,
        "scenario_rows": scenario_rows,
        "action_items": action_items,
        "evidence_footer": {
            "data_used": [
                decision_text(language, f"Portfolio session data as of {now_text}", f"{now_text} 기준 포트폴리오 세션 데이터"),
                decision_text(language, f"User statement recorded {now_text}", f"{now_text} 기록된 사용자 발언"),
            ],
            "not_verified": not_verified[:3],
            "ai_confidence": confidence,
            "last_updated": now_text,
        },
    }


def render_decision_evidence_cards(draft: dict[str, Any]) -> None:
    language = current_language()
    cards = [
        ("user", "USER SAID", "사용자 발언", draft.get("user_statement", "")),
        ("verified", "VERIFIED DATA", "검증 데이터", " · ".join(draft.get("verified_data", [])[:3])),
        ("ai", "AI INTERPRETATION", "AI 해석", " · ".join(draft.get("ai_interpretation", [])[:2])),
        ("missing", "UNCERTAINTY", "불확실성", " · ".join(draft.get("not_verified", [])[:2])),
    ]
    html_cards = []
    for tone, en_label, ko_label, body in cards:
        html_cards.append(
            f"""
            <div class="evidence-status-card {tone}">
                <small>{escape(decision_text(language, en_label, ko_label))}</small>
                <b>{escape(compact_text(body, 120))}</b>
                <span>{escape(decision_text(language, "Click details below for the full reasoning.", "아래 상세에서 전체 근거를 확인하세요."))}</span>
            </div>
            """
        )
    st.markdown(f'<div class="decision-evidence-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def render_decision_draft_board(draft: dict[str, Any]) -> None:
    language = current_language()
    symbols_text = ", ".join(draft.get("symbols") or []) or decision_text(language, "No ticker", "티커 없음")
    draft_html = f"""
    <div class="decision-draft-card">
        <div class="decision-draft-grid">
            <div class="decision-draft-cell primary">
                <small>{escape(decision_text(language, "PROPOSED DECISION", "결정 초안"))}</small>
                <b>{escape(str(draft.get("proposed_decision", "")))}</b>
            </div>
            <div class="decision-draft-cell">
                <small>{escape(decision_text(language, "GOAL", "목표"))}</small>
                <b>{escape(str(draft.get("goal_label", "")))}</b>
            </div>
            <div class="decision-draft-cell">
                <small>{escape(decision_text(language, "FOCUS", "대상"))}</small>
                <b>{escape(symbols_text)}</b>
            </div>
            <div class="decision-draft-cell">
                <small>{escape(decision_text(language, "REVIEW", "재검토"))}</small>
                <b>{escape(str(draft.get("review_date", "")))}</b>
            </div>
        </div>
    </div>
    """
    st.markdown(draft_html, unsafe_allow_html=True)
    render_decision_evidence_cards(draft)

    with st.expander(decision_text(language, "Decision Draft Details", "결정 초안 상세"), expanded=False):
        st.write(f"**{decision_text(language, 'Decision type', '결정 유형')}:** {draft.get('decision_kind_label')}")
        st.write(f"**{decision_text(language, 'Main benefit', '주요 장점')}:** {draft.get('main_benefit')}")
        st.write(f"**{decision_text(language, 'Main risk', '주요 위험')}:** {draft.get('main_risk')}")
        st.write(f"**{decision_text(language, 'Recommended next step', '다음 확인')}:** {draft.get('recommended_next_step')}")
        st.write(f"**{decision_text(language, 'Confidence', '확신도')}:** {draft.get('confidence')}")
        st.dataframe(draft.get("scenario_rows", []), hide_index=True, width="stretch")
        st.json(
            {
                "user_reported": draft.get("user_reported", []),
                "verified_data": draft.get("verified_data", []),
                "ai_interpretation": draft.get("ai_interpretation", []),
                "not_verified": draft.get("not_verified", []),
            }
        )

    action_html = []
    for index, item in enumerate(draft.get("action_items", []), start=1):
        action_html.append(
            f"""
            <div class="action-chip">
                <small>{escape(decision_text(language, f"Action {index}", f"행동 {index}"))}</small>
                <b>{escape(str(item))}</b>
            </div>
            """
        )
    st.markdown(f'<div class="action-chip-row">{"".join(action_html)}</div>', unsafe_allow_html=True)
    footer = draft.get("evidence_footer", {})
    st.markdown(
        f"""
        <div class="evidence-footer">
            <b>{escape(decision_text(language, "Evidence Footer", "근거 푸터"))}</b><br>
            {escape(decision_text(language, "Data used", "사용 데이터"))}: {escape(" · ".join(footer.get("data_used", [])))}<br>
            {escape(decision_text(language, "Not verified", "미검증"))}: {escape(" · ".join(footer.get("not_verified", [])))}<br>
            {escape(decision_text(language, "AI confidence", "AI 확신도"))}: {escape(str(footer.get("ai_confidence", "")))} ·
            {escape(decision_text(language, "Last updated", "마지막 업데이트"))}: {escape(str(footer.get("last_updated", "")))}
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_decision_draft_to_diary() -> None:
    draft = st.session_state.get("decision_capture_draft")
    if not draft:
        return
    note = (
        f"Decision Draft: {draft.get('proposed_decision')}\n"
        f"User said: {draft.get('user_statement')}\n"
        f"Main risk: {draft.get('main_risk')}\n"
        f"Not verified: {'; '.join(draft.get('not_verified', [])[:4])}"
    )
    snapshot = build_financial_snapshot(
        compact_text(note, 1800),
        "Decision Draft",
        str(draft.get("recommended_next_step", "")),
    )
    snapshot["decision_capture"] = draft
    snapshot["outcome_review"] = {}
    st.session_state.financial_diary.append(snapshot)
    st.session_state.decision_capture_saved_notice = True
    set_active_nav_key("diary")


def queue_decision_draft_ai_question() -> None:
    draft = st.session_state.get("decision_capture_draft") or {}
    question = (
        "Use this Decision Draft plus current Portfolio, Finance, Scenario, Evidence, and Diary context. "
        "Separate user statement, verified data, AI interpretation, uncertainty, action, outcome, and memory. "
        f"Draft: {json.dumps(draft, ensure_ascii=False)[:1800]}"
    )
    queue_ai_coach_question(question)


def render_decision_capture_panel() -> None:
    language = current_language()
    flow_label = decision_text(language, "Capture → Draft → Evidence → Action → Memory", "포착 → 초안 → 근거 → 행동 → 기억")
    if st.session_state.pop("decision_capture_saved_notice", False):
        st.success(decision_text(language, "Decision card saved to Diary Memory.", "결정 카드가 다이어리 메모리에 저장되었습니다."))

    st.markdown(
        f"""
        <section class="decision-capture-panel" aria-label="Decision Capture">
            <div class="decision-capture-head">
                <div class="decision-capture-title">
                    <span>{visual_icon_html("capture", "#0f766e", "decision-capture-icon")}</span>
                    <div>
                        <b>{escape(decision_text(language, "Decision Capture", "결정 포착"))}</b>
                        <small>{escape(decision_text(language, "Say the decision first. LY-Scope structures it before analysis.", "결정을 먼저 말하면 LY-Scope가 분석 전에 구조화합니다."))}</small>
                    </div>
                </div>
                <em class="decision-capture-flow">{escape(flow_label)}</em>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.form("decision_capture_form"):
        st.text_area(
            decision_text(language, "What are you trying to decide?", "무엇을 결정하려고 하나요?"),
            placeholder=decision_text(
                language,
                "Example: TSLA dropped a lot. I am considering buying more, but I worry about cash and concentration.",
                "예: TSLA가 많이 떨어져서 추가 매수를 고민 중이지만 현금과 집중도가 걱정됩니다.",
            ),
            height=118,
            key="decision_capture_text",
        )
        st.text_input(
            decision_text(language, "Optional amount", "선택 입력: 금액"),
            placeholder=decision_text(language, "Example: $5,000 or 2,000만원", "예: $5,000 또는 2,000만원"),
            key="decision_capture_amount_text",
        )
        submitted = st.form_submit_button(
            decision_text(language, "Create Decision Draft", "결정 초안 만들기"),
            width="stretch",
        )
    if submitted:
        statement = str(st.session_state.get("decision_capture_text", "")).strip()
        if not statement:
            st.warning(decision_text(language, "Write one decision question first.", "먼저 결정 질문을 한 문장으로 적어주세요."))
        else:
            st.session_state.decision_capture_draft = build_decision_capture_draft(
                statement,
                str(st.session_state.get("decision_capture_amount_text", "")),
            )
            st.rerun()

    draft = st.session_state.get("decision_capture_draft")
    if draft and draft.get("display_language") != language:
        st.session_state.decision_capture_draft = build_decision_capture_draft(
            str(draft.get("user_statement", "")),
            str(draft.get("amount_text", "")),
        )
        draft = st.session_state.get("decision_capture_draft")
    if draft:
        render_decision_draft_board(draft)
        action_cols = st.columns(3)
        with action_cols[0]:
            st.button(
                decision_text(language, "Save Decision Card", "결정 카드 저장"),
                width="stretch",
                on_click=save_decision_draft_to_diary,
            )
        with action_cols[1]:
            st.button(
                decision_text(language, "Ask AI Coach", "AI 코치에게 묻기"),
                width="stretch",
                on_click=queue_decision_draft_ai_question,
            )
        with action_cols[2]:
            st.download_button(
                decision_text(language, "Download Draft JSON", "초안 JSON 다운로드"),
                data=json.dumps(draft, indent=2, ensure_ascii=False),
                file_name=f"ly_scope_decision_draft_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                width="stretch",
            )


def goal_href(goal: str) -> str:
    goal = normalized_goal_key(goal) or "protect_runway"
    config = NORA_GOAL_STRATEGIES[goal]
    params = {"view": config["view"], "mode": "dashboard", "goal": goal}
    params.update(language_params())
    params.update(selection_state_params())
    return f"?{urlencode(params)}"


def life_entry_href() -> str:
    params = {"mode": "intro"}
    params.update(language_params())
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
            <span class="language-toggle-mark" aria-hidden="true">{visual_icon_html("language", "#0f766e", "language-image-icon")}</span>
            <a class="{en_active.strip()}" href="{en_href}" target="_self" title="Switch to English" aria-label="Switch to English">EN</a>
            <a class="{ko_active.strip()}" href="{ko_href}" target="_self" title="Switch to Korean" aria-label="Switch to Korean">KR</a>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def render_nora_ontology(active_key: str) -> None:
    language = current_language()
    start_href = escape(life_entry_href(), quote=True)
    step_nodes = []
    for step in NORA_ONTOLOGY_STEPS:
        detail = step["detail_ko"] if language == "ko" else step["detail_en"]
        step_nodes.append(
            f'<div class="nora-node" role="button" tabindex="0" title="{escape(detail, quote=True)}" '
            f'style="--nora-color: {escape(step["color"])};">'
            f'<div class="nora-glyph">{visual_icon_html(step["glyph"], step["color"], "nora-node-icon")}</div>'
            f'<strong>{ui_html(step["label"])}</strong>'
            f'<span>{ui_html(step["tag"])}</span>'
            f'<div class="nora-detail">{escape(detail)}</div>'
            '</div>'
        )

    module_links = []
    module_colors = {
        "life": "#14b8a6",
        "finance": "#0ea5e9",
        "portfolio": "#84cc16",
        "reit": "#f59e0b",
        "scenario": "#f97316",
        "advisor": "#ec4899",
        "diary": "#ec4899",
    }
    for label, view in NORA_MODULE_MAP:
        active_class = " active" if view == active_key else ""
        href = escape(app_view_href(view), quote=True)
        module_links.append(
            f'<a class="nora-module{active_class}" href="{href}" target="_self" title="{ui_html(label)}">'
            f'{visual_icon_html(view, module_colors.get(view, "#0f766e"), "module-image-icon")}'
            f'<span>{ui_html(label)}</span></a>'
        )

    summary_label = "LY-Scope Goal Flow" if language == "en" else "LY-Scope 목표 흐름"
    goal_label = "Goal" if language == "en" else "목표"
    strategy_label = "Strategy" if language == "en" else "전략"
    situation_label = "Situation" if language == "en" else "상황"
    summary_path = (
        f'<a class="ly-flow-return" href="{start_href}" target="_self">{escape(goal_label)}</a>'
        '<i aria-hidden="true">→</i>'
        f'<a class="ly-flow-return" href="{start_href}" target="_self">{escape(strategy_label)}</a>'
        '<i aria-hidden="true">→</i>'
        f'<span>{escape(situation_label)}</span>'
    )
    ontology_html = (
        f'<details class="nora-ontology nora-ontology-minimal" aria-label="{ui_html("NORA Ontology")}">'
        '<summary>'
        f'<b>{escape(summary_label)}</b>'
        f'<span class="ly-flow-summary-path">{summary_path}</span>'
        '</summary>'
        '<div class="nora-ontology-body">'
        '<div class="nora-ontology-caption">'
        f'{ui_html("LY-Scope starts with the customer goal, then checks the strategy and current situation before any model.")}'
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
    decision_capture = context.get("decision_capture") or {}
    gain_loss = portfolio_gain_loss_summary(holdings)

    if decision_capture:
        decision_status = compact_text(str(decision_capture.get("proposed_decision") or "Draft captured"), 70)
        decision_advice = (
            "Review verified data and uncertainty before treating this thought as an action."
            if language == "en"
            else "이 생각을 행동으로 옮기기 전에 검증 데이터와 불확실성을 먼저 확인하세요."
        )
    else:
        decision_status = "Needs decision draft" if language == "en" else "결정 초안 필요"
        decision_advice = (
            "Start with one plain-language decision question so NORA can connect purpose, evidence, action, and memory."
            if language == "en"
            else "NORA가 목적, 근거, 행동, 기억을 연결할 수 있도록 결정 질문을 한 문장으로 먼저 입력하세요."
        )

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
                "title": "결정 초안",
                "view": "life",
                "status": decision_status,
                "advice": decision_advice,
                "question": "내 결정 초안을 사용자 발언, 검증 데이터, AI 해석, 불확실성, 다음 행동으로 나누어 검토해 주세요.",
            },
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
            "title": "Decision Draft",
            "view": "life",
            "status": decision_status,
            "advice": decision_advice,
            "question": "Review my decision draft by separating user statement, verified data, AI interpretation, uncertainty, and next action.",
        },
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
    if any(token in q for token in ("decision", "draft", "capture", "decide", "action", "결정", "판단", "초안", "포착", "행동")):
        return "decision"
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
                "decision_capture": clean_restored_json_value(entry.get("decision_capture")),
                "outcome_review": clean_restored_json_value(entry.get("outcome_review", {})),
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
    decision_capture = context.get("decision_capture") or {}
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
                "historical_annual_return_pct": safe_float(float(risk["historical_annual_return"]) * 100, 2),
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
        "decision_capture": None
        if not decision_capture
        else {
            "created_at": decision_capture.get("created_at"),
            "user_statement": compact_text(decision_capture.get("user_statement"), 520),
            "decision_kind": decision_capture.get("decision_kind"),
            "proposed_decision": decision_capture.get("proposed_decision"),
            "goal_label": decision_capture.get("goal_label"),
            "symbols": list(decision_capture.get("symbols", []))[:8],
            "amount": safe_float(decision_capture.get("amount"), 2),
            "amount_currency": decision_capture.get("amount_currency"),
            "main_benefit": compact_text(decision_capture.get("main_benefit"), 260),
            "main_risk": compact_text(decision_capture.get("main_risk"), 260),
            "recommended_next_step": compact_text(decision_capture.get("recommended_next_step"), 320),
            "review_date": decision_capture.get("review_date"),
            "confidence": decision_capture.get("confidence"),
            "user_reported": [compact_text(item, 240) for item in decision_capture.get("user_reported", [])[:4]],
            "verified_data": [compact_text(item, 240) for item in decision_capture.get("verified_data", [])[:8]],
            "ai_interpretation": [compact_text(item, 260) for item in decision_capture.get("ai_interpretation", [])[:6]],
            "not_verified": [compact_text(item, 260) for item in decision_capture.get("not_verified", [])[:8]],
            "scenario_rows": decision_capture.get("scenario_rows", [])[:3],
            "action_items": [compact_text(item, 260) for item in decision_capture.get("action_items", [])[:5]],
            "memory_rule": "A decision draft becomes trusted memory only after action and outcome review are compared.",
        },
        "diary_memory": [
            {
                "time": entry.get("time"),
                "mood": entry.get("mood"),
                "next_action": compact_text(entry.get("next_action"), 220),
                "note": compact_text(entry.get("note"), 320) if include_diary_text else "[hidden unless user opts in]",
                "decision_capture": None
                if not entry.get("decision_capture")
                else compact_text((entry.get("decision_capture") or {}).get("proposed_decision"), 220),
                "outcome_review": clean_restored_json_value(entry.get("outcome_review", {}), 2),
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
- If decision_capture exists, treat it as the user's current decision draft.
- Keep user statement, app-verified data, AI interpretation, uncertainty, next action, outcome review, and memory separate.
- Do not turn a decision draft into a buy/sell recommendation.
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
    decision_capture = context.get("decision_capture") or {}

    evidence: list[str] = []
    if decision_capture:
        evidence.append(f"Decision draft: {decision_capture.get('proposed_decision')}.")
        evidence.append(f"User statement: {compact_text(decision_capture.get('user_statement'), 220)}.")
        verified_line = "; ".join(decision_capture.get("verified_data", [])[:3])
        if verified_line:
            evidence.append(f"Draft verified data: {verified_line}.")
        uncertainty_line = "; ".join(decision_capture.get("not_verified", [])[:3])
        if uncertainty_line:
            evidence.append(f"Draft uncertainty: {uncertainty_line}.")
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

    if intent == "decision":
        if decision_capture:
            short = (
                f"The current captured decision is **{decision_capture.get('proposed_decision')}**. "
                "NORA is keeping it as a draft until verified data, downside risk, and user constraints are checked."
            )
            next_step = str(decision_capture.get("recommended_next_step") or "Run the relevant evidence screen before action.")
        else:
            short = (
                "No decision draft has been captured yet. Start with one plain sentence about what you are trying to decide."
            )
            next_step = "Open Goal/Life, write the decision question, then create a Decision Draft before using AI interpretation."
    elif intent == "readiness":
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
            "Review my decision draft.",
            "Am I investment ready?",
            "Explain my biggest risk.",
            "What happens in my latest scenario?",
            "What should I track next?",
            "Summarize my diary memory.",
            "What privacy or F-1 caution matters?",
        ]
        if language == "en"
        else [
            "내 결정 초안을 검토해 주세요.",
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
                {"Layer": "Decision Capture", "Current foundation": "Plain-language decision draft, evidence split, uncertainty list", "Future question": "What exactly am I trying to decide?"},
                {"Layer": "Scenario", "Current foundation": "What-if Scenario Lab", "Future question": "What if income falls, FX moves, or rates rise?"},
                {"Layer": "Portfolio", "Current foundation": "Valuation score, beta, covariance, correlation", "Future question": "Where is my risk concentrated?"},
                {"Layer": "Personal finance", "Current foundation": "Surplus, emergency fund, DTI, health score", "Future question": "Can my life absorb this investment risk?"},
                {"Layer": "Outcome / Memory", "Current foundation": "Financial Diary JSON plus outcome review", "Future question": "Did the decision work, and what should I remember?"},
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

    with st.expander("0. Three-Pass Formula Reference Validation", expanded=True):
        st.markdown(
            """
            LY-Scope-Ver.2 separates **reference-backed formulas** from **internal judgment scores**.
            Market value, runway, DTI, CAPM, covariance, and cap-rate math can be traced to known
            finance references. Composite scores are LY-Scope heuristics that make risk easier to see.
            """
        )
        st.dataframe(
            [
                {
                    "Layer": "Personal finance",
                    "Formula or theory": "Cash flow, net worth, emergency runway, DTI",
                    "Validation": "Reference-backed formula; score weights are internal.",
                    "Primary reference": "FINRA Financial Foundations; CFPB DTI definition",
                },
                {
                    "Layer": "Stock valuation",
                    "Formula or theory": "CAPM required return, Gordon Growth, Graham Number, peer P/E",
                    "Validation": "Classic valuation inputs; blended fair value is an internal triangulation heuristic.",
                    "Primary reference": "Sharpe 1964; CFA Institute DDM; Graham value screen",
                },
                {
                    "Layer": "Portfolio risk",
                    "Formula or theory": "Portfolio variance = w' covariance w; annualized SD = daily SD x sqrt(252)",
                    "Validation": "Reference-backed portfolio math; complementarity score is internal.",
                    "Primary reference": "Markowitz 1952; SEC Investor.gov diversification",
                },
                {
                    "Layer": "Real estate",
                    "Formula or theory": "NOI / cap rate, LTV, rate-sensitive stress",
                    "Validation": "Reference-backed valuation concepts; resilience score weights are internal.",
                    "Primary reference": "Federal Reserve CRE policy; Appraisal Institute guide notes",
                },
                {
                    "Layer": "Scenario / AI",
                    "Formula or theory": "User-selected shocks applied to portfolio, FX, income, expenses, and rates",
                    "Validation": "Educational stress model; not a forecast or recommendation.",
                    "Primary reference": "Scenario disclosure and app data-source boundaries",
                },
            ],
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "Full validation notes are kept in docs/FORMULA_REFERENCE_VALIDATION.md. "
            "Third-party prices can be delayed, unavailable, or restricted by provider terms."
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
                        {"Metric": "Covariance Check SD", "Value": f"{risk['covariance_daily_vol'] * 100:.3f}%"},
                        {"Metric": "Annualized Portfolio Risk", "Value": f"{risk['annual_vol'] * 100:.1f}%"},
                        {"Metric": "Historical Annualized Return", "Value": f"{risk['historical_annual_return'] * 100:+.1f}%"},
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

            - Decision capture: user statement, proposed draft, verified data, AI interpretation, and uncertainty.
            - Portfolio holdings, weights, valuation score, beta, covariance, and correlation.
            - Personal finance readiness: surplus, emergency fund, savings rate, debt-to-income, and health score.
            - Real estate exposure, income durability, LTV, and interest-rate sensitivity.
            - Diary snapshots, notes, next actions, and outcome reviews when the user chooses to restore them.
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
        .case-study-hero {
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 10px;
            padding: 18px;
            margin: 0 0 16px;
            background:
                radial-gradient(circle at 8% 0%, rgba(20, 184, 166, 0.12), transparent 32%),
                radial-gradient(circle at 94% 12%, rgba(59, 130, 246, 0.11), transparent 30%),
                rgba(255, 255, 255, 0.98);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
        }
        .case-study-hero small {
            display: block;
            color: #0f766e;
            font-size: 0.72rem;
            line-height: 1;
            font-weight: 950;
            text-transform: uppercase;
        }
        .case-study-hero h1 {
            margin: 8px 0 5px;
            color: #0f172a;
            font-size: 1.72rem;
            line-height: 1.05;
            font-weight: 950;
        }
        .case-study-hero p {
            max-width: 760px;
            margin: 0;
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
            font-weight: 720;
        }
        .case-study-flow {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 14px;
        }
        .case-study-flow span {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 0 10px;
            border-radius: 999px;
            color: #0f4a5a;
            background: #ecfeff;
            border: 1px solid rgba(14, 116, 144, 0.14);
            font-size: 0.72rem;
            font-weight: 900;
            white-space: nowrap;
        }
        .case-study-snapshot {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(260px, 0.9fr);
            gap: 14px;
            margin: 14px 0 16px;
        }
        .case-study-profile-card,
        .case-study-decision-card {
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, 0.24);
            background: rgba(255, 255, 255, 0.98);
            padding: 16px;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.055);
        }
        .case-study-profile-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 13px;
        }
        .case-study-person {
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
        }
        .case-study-avatar {
            flex: 0 0 48px;
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            color: #ffffff;
            background: linear-gradient(135deg, #0f766e, #2563eb);
            font-size: 1rem;
            font-weight: 950;
        }
        .case-study-person b {
            display: block;
            color: #0f172a;
            font-size: 1.12rem;
            line-height: 1.08;
            font-weight: 950;
        }
        .case-study-person span,
        .case-study-profile-top em {
            display: block;
            color: #64748b;
            font-size: 0.75rem;
            line-height: 1.2;
            font-style: normal;
            font-weight: 820;
        }
        .case-study-goal-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
        }
        .case-study-goal-cell {
            min-height: 94px;
            border-radius: 9px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: #f8fafc;
            padding: 12px;
        }
        .case-study-goal-cell small,
        .case-study-decision-card small {
            display: block;
            color: #64748b;
            font-size: 0.66rem;
            line-height: 1.05;
            font-weight: 950;
            text-transform: uppercase;
        }
        .case-study-goal-cell b,
        .case-study-decision-card b {
            display: block;
            margin-top: 6px;
            color: #0f172a;
            font-size: 0.88rem;
            line-height: 1.28;
            font-weight: 880;
        }
        .case-study-decision-card {
            border-color: rgba(15, 118, 110, 0.22);
            background:
                linear-gradient(135deg, rgba(236, 253, 245, 0.98), rgba(239, 246, 255, 0.96));
        }
        .case-study-decision-card strong {
            display: block;
            margin: 8px 0 10px;
            color: #0f172a;
            font-size: 1.24rem;
            line-height: 1.08;
            font-weight: 950;
        }
        .case-study-evidence-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-top: 12px;
        }
        .case-study-evidence-mini {
            border-radius: 9px;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 10px;
        }
        .case-study-evidence-mini span {
            display: block;
            color: #64748b;
            font-size: 0.66rem;
            font-weight: 900;
        }
        .case-study-evidence-mini b {
            display: block;
            margin-top: 4px;
            color: #0f172a;
            font-size: 0.9rem;
            line-height: 1.15;
            font-weight: 940;
        }
        .case-study-details {
            margin: 10px 0 16px;
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, 0.22);
            background: rgba(255, 255, 255, 0.96);
            padding: 10px 14px;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.045);
        }
        .case-study-details summary {
            cursor: pointer;
            color: #0f172a;
            font-size: 0.86rem;
            font-weight: 920;
        }
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
            border: 1px solid rgba(20, 184, 166, 0.18);
            border-radius: 8px;
            background: linear-gradient(135deg, #0f766e, #164e63);
            color: #ffffff;
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
            grid-template-columns: repeat(auto-fit, minmax(158px, 1fr));
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
        .advisor-scenario-top {
            display: flex;
            align-items: center;
            gap: 9px;
            min-width: 0;
        }
        .advisor-scenario-icon {
            width: 34px;
            height: 34px;
            flex: 0 0 34px;
            display: grid;
            place-items: center;
        }
        .advisor-scenario-image-icon {
            width: 34px;
            height: 34px;
            display: block;
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
            .case-study-snapshot,
            .advisor-report-grid {
                grid-template-columns: 1fr;
            }
            .case-study-goal-grid,
            .case-study-evidence-row {
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
    return fmt_money_compact(float(value), currency, language)


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
    title = ui("Case Study Board")
    caption = ui("Pick a client, then read the goal and stress signal before opening details.")
    cards: list[str] = []
    for report in reports:
        client = report["client"]
        result = report["result"]
        review = advisor_scenario_review(report, language)
        score = max(0.0, min(100.0, float(result["planning_health_score"])))
        active_class = " active" if client.client_id == selected_id else ""
        tone_color = {"risk": "#dc2626", "watch": "#d97706", "stable": "#0f766e"}.get(review["tone"], "#0f766e")
        cards.append(
            f'<a class="advisor-scenario-card {escape(review["tone"])}{active_class}" '
            f'href="{escape(advisor_client_href(client.client_id), quote=True)}" target="_self">'
            f'<div class="advisor-scenario-top"><span class="advisor-scenario-icon">'
            f'{visual_icon_html("case", tone_color, "advisor-scenario-image-icon")}</span>'
            f'<div><b>{escape(client.client_id)} · {escape(client.name.split()[0])}</b>'
            f'<span>{escape(client.text("segment", language))}</span></div></div>'
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


def case_study_statement(report: dict[str, Any], language: str) -> str:
    client = report["client"]
    weakest = report["weakest_signal"]["label"]
    if language == "ko":
        return (
            f"{client.name} 케이스 스터디: {client.text('goal', language)} "
            f"현재 상황은 {client.text('situation', language)} "
            f"가장 약한 신호는 {weakest}이고, 결정 방향은 {report['decision_compass']}입니다. "
            f"어드바이저 초점은 {client.text('advisor_focus', language)}입니다."
        )
    return (
        f"Case study for {client.name}: {client.text('goal', language)} "
        f"Current situation: {client.text('situation', language)} "
        f"The weakest signal is {weakest}, and the decision direction is {report['decision_compass']}. "
        f"Advisor focus: {client.text('advisor_focus', language)}."
    )


def apply_case_study_to_decision_capture(report: dict[str, Any]) -> None:
    language = current_language()
    statement = case_study_statement(report, language)
    st.session_state.decision_capture_text = statement
    st.session_state.decision_capture_amount_text = ""
    st.session_state.decision_capture_draft = build_decision_capture_draft(statement, "")
    set_active_nav_key("life")


def render_case_study_hero(language: str) -> None:
    flow = ["Purpose", "Situation", "Evidence", "Decision", "Memory"]
    if language == "ko":
        flow = ["목적", "상황", "근거", "결정", "기억"]
    flow_html = "".join(f"<span>{escape(item)}</span>" for item in flow)
    st.markdown(
        f"""
        <section class="case-study-hero">
            <small>{ui_html("NORA Case Study Lab")}</small>
            <h1>{ui_html("Case Studies")}</h1>
            <p>{ui_html("Read fictional client cases through the current NORA web flow: goal, situation, evidence, decision, and memory.")}</p>
            <div class="case-study-flow">{flow_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_case_study_snapshot(report: dict[str, Any], language: str, advisor_label: Any) -> None:
    client = report["client"]
    result = report["result"]
    review = advisor_scenario_review(report, language)
    runway = float(result["emergency_months"])
    required = float(result["required_runway_months"])
    exposure = float(result["investment_exposure_ratio"]) * 100
    portfolio_score = float(report["portfolio"]["score"])
    weakest = report["weakest_signal"]

    html = f"""
    <section class="case-study-snapshot" aria-label="{ui_html('Visual Case Snapshot')}">
        <div class="case-study-profile-card">
            <div class="case-study-profile-top">
                <div class="case-study-person">
                    <div class="case-study-avatar" aria-label="{escape(client.name, quote=True)}">{visual_icon_html("case", "#0f766e", "case-study-avatar-icon")}</div>
                    <div>
                        <b>{escape(client.name)}</b>
                        <span>{escape(client.client_id)} · {escape(client.text('segment', language))}</span>
                    </div>
                </div>
                <em><span class="case-study-score-ring" style="--score: {float(result['planning_health_score']):.0f}%;"></span>{escape(report['status'])} · {float(result['planning_health_score']):.0f}/100</em>
            </div>
            <div class="case-study-goal-grid">
                <div class="case-study-goal-cell">
                    <small>{ui_html('Customer Goal')}</small>
                    <b>{escape(compact_text(client.text('goal', language), 145))}</b>
                </div>
                <div class="case-study-goal-cell">
                    <small>{ui_html('Current Situation')}</small>
                    <b>{escape(compact_text(client.text('situation', language), 145))}</b>
                </div>
                <div class="case-study-goal-cell">
                    <small>{ui_html('Crisis')}</small>
                    <b>{escape(str(weakest['label']))} · {float(weakest['score']):.0f}/100</b>
                </div>
            </div>
        </div>
        <div class="case-study-decision-card">
            <small>{ui_html('NORA Case Path')}</small>
            <strong>{escape(report['decision_compass'])}</strong>
            <b>{escape(review['summary'])}</b>
            <div class="case-study-evidence-row">
                <div class="case-study-evidence-mini">
                    <span>{escape(advisor_label('cash_runway', language))}</span>
                    <b>{runway:.1f}/{required:.1f}</b>
                </div>
                <div class="case-study-evidence-mini">
                    <span>{escape(advisor_label('investment_exposure', language))}</span>
                    <b>{exposure:.1f}%</b>
                </div>
                <div class="case-study-evidence-mini">
                    <span>{escape(advisor_label('portfolio_quality', language))}</span>
                    <b>{portfolio_score:.0f}/100</b>
                </div>
            </div>
        </div>
    </section>
    """
    st.markdown(html, unsafe_allow_html=True)


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

    render_case_study_hero(advisor_language)
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
    with st.expander(ui("Show table details"), expanded=False):
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

    render_case_study_snapshot(report, advisor_language, advisor_label)

    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button(ui("Use Case as Decision Draft"), width="stretch"):
            apply_case_study_to_decision_capture(report)
            st.rerun()
    with action_cols[1]:
        if st.button(ui("Load Client Into Finance"), width="stretch"):
            apply_advisor_client_to_finance(report)
            set_active_nav_key("finance")
            st.rerun()
    st.caption(ui("Open this case in the Decision Capture flow."))

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

    with st.expander(ui("Case Study Details"), expanded=False):
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
        if portfolio_rows:
            st.subheader(ui("Portfolio / Valuation Sample"))
            st.dataframe(portfolio_rows, hide_index=True, width="stretch")
            st.caption(
                f"{ui('Portfolio beta')} {float(report['portfolio']['weighted_beta']):.2f} · "
                f"{ui('Largest holding')} {float(report['portfolio']['largest_weight']) * 100:.1f}% · "
                f"{ui('Sector concentration')} {float(report['portfolio']['sector_concentration']) * 100:.1f}%"
            )
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

    button_cols = st.columns(2)
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

    if pdf_error:
        st.warning(f"PDF export is unavailable until reportlab is installed: {pdf_error}")

    st.subheader(ui("Case Study Archive"))
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
    decision_capture = context.get("decision_capture") or {}

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
                f"- Historical annualized return: {float(risk['historical_annual_return']) * 100:+.1f}%",
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

    lines.append("")
    lines.append("5. Decision Capture")
    if decision_capture:
        lines.extend(
            [
                f"- User statement: {compact_text(decision_capture.get('user_statement'), 320)}",
                f"- Decision draft: {decision_capture.get('proposed_decision')}",
                f"- Goal link: {decision_capture.get('goal_label')}",
                f"- Main risk: {decision_capture.get('main_risk')}",
                f"- Next step: {decision_capture.get('recommended_next_step')}",
                f"- Review date: {decision_capture.get('review_date')}",
            ]
        )
        if decision_capture.get("verified_data"):
            lines.append("- Verified data attached:")
            lines.extend(f"  - {item}" for item in decision_capture.get("verified_data", [])[:4])
        if decision_capture.get("not_verified"):
            lines.append("- Not verified yet:")
            lines.extend(f"  - {item}" for item in decision_capture.get("not_verified", [])[:4])
    else:
        lines.append("- No decision draft has been captured yet.")

    missing = context.get("missing", [])
    lines.extend(["", "6. Missing Inputs"])
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- No major missing inputs detected for the current prototype.")

    lines.extend(
        [
            "",
            "7. Next Reflection Prompt",
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


def render_decision_outcome_review() -> None:
    language = current_language()
    if st.session_state.pop("decision_outcome_saved_notice", False):
        st.success(decision_text(language, "Outcome review saved to Memory.", "결과 리뷰가 메모리에 저장되었습니다."))

    decision_entries = [
        (idx, entry)
        for idx, entry in enumerate(st.session_state.get("financial_diary", []), start=1)
        if entry.get("decision_capture")
    ]
    if not decision_entries:
        return

    st.subheader(decision_text(language, "Outcome Review", "결과 리뷰"))
    selected_idx = st.selectbox(
        decision_text(language, "Select a saved decision card", "저장된 결정 카드 선택"),
        options=[idx for idx, _ in decision_entries],
        format_func=lambda idx: (
            f"Entry {idx} · "
            f"{compact_text((st.session_state.financial_diary[idx - 1].get('decision_capture') or {}).get('proposed_decision'), 70)}"
        ),
        key="decision_outcome_entry_index",
    )
    entry = st.session_state.financial_diary[int(selected_idx) - 1]
    draft = entry.get("decision_capture") or {}
    outcome = entry.get("outcome_review") or {}

    st.markdown(
        f"""
        <div class="decision-draft-card">
            <div class="decision-draft-grid">
                <div class="decision-draft-cell primary">
                    <small>{escape(decision_text(language, "DECISION", "결정"))}</small>
                    <b>{escape(str(draft.get("proposed_decision", "")))}</b>
                </div>
                <div class="decision-draft-cell">
                    <small>{escape(decision_text(language, "EXPECTED", "예상"))}</small>
                    <b>{escape(str(draft.get("main_benefit", "")))}</b>
                </div>
                <div class="decision-draft-cell">
                    <small>{escape(decision_text(language, "RISK ACCEPTED", "수용 위험"))}</small>
                    <b>{escape(str(draft.get("main_risk", "")))}</b>
                </div>
                <div class="decision-draft-cell">
                    <small>{escape(decision_text(language, "REVIEW DATE", "리뷰 날짜"))}</small>
                    <b>{escape(str(draft.get("review_date", "")))}</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("decision_outcome_form"):
        expected = st.text_input(
            decision_text(language, "Expected outcome", "예상 결과"),
            value=str(outcome.get("expected_outcome") or draft.get("main_benefit") or ""),
        )
        actual = st.text_area(
            decision_text(language, "Actual outcome", "실제 결과"),
            value=str(outcome.get("actual_outcome") or ""),
            height=90,
        )
        changed = st.text_area(
            decision_text(language, "What changed?", "무엇이 바뀌었나요?"),
            value=str(outcome.get("what_changed") or ""),
            height=80,
        )
        misunderstood = st.text_area(
            decision_text(language, "What did I misunderstand?", "무엇을 잘못 이해했나요?"),
            value=str(outcome.get("what_misunderstood") or ""),
            height=80,
        )
        same_decision = st.selectbox(
            decision_text(language, "Would I make the same decision again?", "다시 같은 결정을 할까요?"),
            options=[
                decision_text(language, "Not reviewed", "미검토"),
                decision_text(language, "Yes", "예"),
                decision_text(language, "Partially", "부분적으로"),
                decision_text(language, "No", "아니오"),
            ],
            index=0,
        )
        saved = st.form_submit_button(decision_text(language, "Save Outcome Review", "결과 리뷰 저장"), width="stretch")
    if saved:
        entry["outcome_review"] = {
            "reviewed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "expected_outcome": compact_text(expected, 600),
            "actual_outcome": compact_text(actual, 1200),
            "what_changed": compact_text(changed, 1000),
            "what_misunderstood": compact_text(misunderstood, 1000),
            "would_make_same_decision": same_decision,
        }
        st.session_state.decision_outcome_saved_notice = True
        st.rerun()


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
    if st.session_state.pop("decision_capture_saved_notice", False):
        st.success(decision_text(current_language(), "Decision card saved to Diary Memory.", "결정 카드가 다이어리 메모리에 저장되었습니다."))
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

    render_decision_outcome_review()

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
            decision_capture = entry.get("decision_capture") or {}
            if decision_capture:
                st.write(f"**Decision Draft:** {decision_capture.get('proposed_decision')}")
                st.write(f"**User Said:** {decision_capture.get('user_statement')}")
                st.write(f"**Evidence Used:** {'; '.join(decision_capture.get('verified_data', [])[:4])}")
                st.write(f"**Uncertainty:** {'; '.join(decision_capture.get('not_verified', [])[:4])}")
                outcome_review = entry.get("outcome_review") or {}
                if outcome_review:
                    st.write(f"**Outcome Review:** {outcome_review.get('would_make_same_decision')}")
                    st.write(f"**Actual Outcome:** {outcome_review.get('actual_outcome') or 'Not recorded'}")
                    st.write(f"**What Changed:** {outcome_review.get('what_changed') or 'Not recorded'}")
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
        st.caption(
            "Valuation Score estimates the portfolio's weighted upside or downside versus each stock's blended fair value. "
            "Formula: sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight. "
            "Positive means undervalued; negative means overvalued. Holdings without valid fair value are excluded. "
            f"Current analysis mode: {st.session_state.portfolio_weighting_mode}."
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
        This follows Markowitz-style portfolio risk logic: diversification works when assets do not move perfectly together.
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
    start_href = life_entry_href()

    path_items = [
        {
            "step": "01",
            "label": ui("Goal"),
            "caption": "Return to goal start." if language == "en" else "목표 선택 화면으로 돌아가기.",
            "href": start_href,
            "active": active_focus == "goal" or (active_focus is None and active_view == "life"),
        },
        {
            "step": "02",
            "label": ui("Strategy"),
            "caption": strategy_caption,
            "href": start_href,
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

    st.markdown(f"### {'LY-Scope Path' if language == 'en' else 'LY-Scope 경로'}")
    st.caption("LY-Scope Goal Flow → AI Coach" if language == "en" else "LY-Scope 목표 흐름 → AI 코치")
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


def google_feedback_form_base_url() -> str:
    return str(st.session_state.get("google_feedback_form_url") or GOOGLE_FEEDBACK_FORM_URL).strip()


def is_google_feedback_form_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if parsed.scheme not in {"http", "https"}:
        return False
    return (host == "forms.gle") or (host == "docs.google.com" and "/forms/" in path)


def google_feedback_form_href(comment: dict[str, Any] | None = None) -> str:
    base_url = google_feedback_form_base_url()
    if not is_google_feedback_form_url(base_url):
        return ""

    parsed = urlparse(base_url)
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    existing_keys = {key for key, _ in query_items}
    context_items = [
        ("ly_app", "LY-Scope-Ver.2"),
        ("ly_public_url", PUBLIC_APP_URL),
        ("ly_build", APP_BUILD_STAMP),
        ("ly_language", current_language()),
        ("ly_view", active_nav_key()),
        ("ly_goal", active_goal_key() or ""),
        ("ly_symbols", ",".join(selected_symbols_for_url())),
        ("ly_portfolio", ",".join(st.session_state.get("portfolio", {}).keys())),
    ]
    if comment:
        context_items.extend(
            [
                ("ly_comment_time", str(comment.get("time", ""))),
                ("ly_comment_text", str(comment.get("comment", ""))[:600]),
            ]
        )

    for key, value in context_items:
        if key not in existing_keys and value:
            query_items.append((key, value))

    return urlunparse(parsed._replace(query=urlencode(query_items)))


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## LY-Scope-Ver.2")
        st.caption(ui("Use the Menu button at the upper-left to open or close this sidebar."))

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
        with st.expander(ui("Feedback & Contact"), expanded=False):
            if st.session_state.pop("comment_saved_notice", False):
                st.success(ui("Comment saved in this session."))
            st.markdown(f"#### {ui('Google Feedback Form')}")
            st.caption(ui("Connect feedback to a Google Form."))
            draft_form_url = st.text_input(
                ui("Google Form URL"),
                placeholder="https://forms.gle/...",
                help=ui("Paste Google Form URL for this session."),
                key="google_feedback_form_url_draft",
            )
            if st.button(ui("Connect Google Form"), width="stretch"):
                st.session_state.google_feedback_form_url = str(draft_form_url).strip()
                st.rerun()
            form_url = google_feedback_form_base_url()
            recent_comment = st.session_state.comments[-1] if st.session_state.comments else None
            if form_url:
                if is_google_feedback_form_url(form_url):
                    st.success(ui("Google Form connection is ready."))
                    st.link_button(
                        ui("Open Google Feedback Form"),
                        google_feedback_form_href(recent_comment),
                        width="stretch",
                    )
                    st.caption(
                        ui(
                            "The Google Form opens in a new tab. This app also keeps a local session copy."
                        )
                    )
                else:
                    st.warning(ui("Use a Google Forms URL from docs.google.com/forms or forms.gle."))
            else:
                st.info(
                    ui(
                        "Add GOOGLE_FEEDBACK_FORM_URL in Streamlit secrets, or paste a Google Form URL here."
                    )
                )

            st.divider()
            st.markdown(f"#### {ui('Developer')}")
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
                            "screen": active_nav_key(),
                            "goal": active_goal_key() or "",
                        }
                    )
                    st.session_state.comment_saved_notice = True
                    st.rerun()
                else:
                    st.warning(ui("Please enter a comment first."))

            if st.session_state.comments:
                with st.expander(ui("Saved comments"), expanded=False):
                    for item in reversed(st.session_state.comments[-5:]):
                        screen_text = f" [{item.get('screen', '')}]" if item.get("screen") else ""
                        st.caption(f"{item.get('time', '')}{screen_text} - {item.get('comment', '')}")


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
    render_visual_asset_theme()
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
    homepage_bg = image_data_uri(str(HOMEPAGE_BG_PATH)) if USE_HOMEPAGE_REFERENCE_IMAGE else ""
    homepage_class = " has-home-image" if homepage_bg else ""
    homepage_image = (
        f'<img class="homepage-bg-img" src="{homepage_bg}" alt="LY-Scope-Ver.2 life design homepage preview">'
        if homepage_bg
        else ""
    )
    flow_visual_bg = image_data_uri(str(GOAL_STRATEGY_SITUATION_PATH))
    flow_visual_image = (
        f'<div class="home-flow-visual" aria-hidden="true"><img src="{flow_visual_bg}" alt=""></div>'
        if flow_visual_bg
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
                    <span class="goal-number">{visual_icon_html(goal_key, config['color'], 'goal-number-icon')}</span>
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
                        <div class="home-brand-mark">{visual_icon_html("life", "#0f766e", "home-brand-icon")}</div>
                        <div>LY-Scope-Ver.2 <small>Decision Intelligence</small></div>
                    </div>
                </div>
                <div class="home-goal-layout">
                    <section class="home-goal-intro" aria-label="NORA goal start">
                        <div class="life-kicker">{'Goal comes before strategy.' if language == 'en' else '전략보다 목표가 먼저입니다.'}</div>
                        <h1 class="life-title">{life_title}</h1>
                        <div class="life-copy">{escape(life_copy)}</div>
                        {flow_visual_image}
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
    render_decision_capture_panel()


NAV_ITEMS = [
    {"key": "life", "label": "Life", "icon": "LF"},
    {"key": "finance", "label": "Finance", "icon": "FI"},
    {"key": "portfolio", "label": "Portfolio", "icon": "PF"},
    {"key": "diary", "label": "Diary", "icon": "DY"},
    {"key": "advisor", "label": "Case Studies", "icon": "CS"},
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
        "glyph": "CAP",
        "label": "Decision Capture",
        "tag": "User signal",
        "color": "#14b8a6",
        "detail_en": "The customer's plain-language thought, worry, question, or intent before it becomes structured data.",
        "detail_ko": "구조화된 데이터가 되기 전 고객의 자연스러운 생각, 걱정, 질문, 의도.",
    },
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
        "detail_en": "Cash flow, assets, debt, stocks, real estate, goals, decision drafts, and diary snapshots.",
        "detail_ko": "현금흐름, 자산, 부채, 주식, 부동산, 목표, 결정 초안, 다이어리 스냅샷.",
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
        "glyph": "ACT",
        "label": "Action",
        "tag": "Action follow-through",
        "color": "#fb7185",
        "detail_en": "Whether the customer waited, acted partially, acted fully, or changed course after seeing evidence.",
        "detail_ko": "근거를 본 뒤 고객이 보류, 부분 실행, 전체 실행, 방향 전환 중 무엇을 했는지.",
    },
    {
        "glyph": "OUT",
        "label": "Outcome",
        "tag": "What happened next?",
        "color": "#38bdf8",
        "detail_en": "Observed result, changed facts, misunderstood assumptions, and whether the same decision would be repeated.",
        "detail_ko": "관찰된 결과, 바뀐 사실, 잘못 이해한 가정, 같은 결정을 반복할지 여부.",
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
    ("Case Studies", "advisor"),
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


def intro_mode_requested() -> bool:
    return query_param_value("mode") == "intro"


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
            f'{visual_icon_html(nav_item["key"], orbit_item["accent"], "nav-image-icon")}'
            f'<span>{ui_html(nav_item["label"])}</span></a>'
        )

    center_active = " active" if active_key == "diary" else ""
    diary_href = escape(app_view_href("diary"), quote=True)
    st.markdown(
        (
            '<div class="desktop-orbit-nav" aria-label="LY-Scope-Ver.2 compact orbit navigation">'
            '<div class="desktop-orbit-shell">'
            f'{"".join(orbit_links)}'
            f'<a class="desktop-orbit-item{center_active}" href="{diary_href}" target="_self" aria-label="{ui_html("Financial Diary")}" '
            'style="--accent: #ec4899; --accent-rgb: 236, 72, 153;">'
            f'{visual_icon_html("diary", "#ec4899", "nav-image-icon")}<span>{ui_html("Diary")}</span></a>'
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
        {"key": "advisor", "label": "Case Studies", "icon": "CS", "slot": "mobile-orbit-left"},
    ]
    orbit_links = []
    for item in orbit_items:
        active_class = " active" if item["key"] == active_key else ""
        href = escape(app_view_href(item["key"]), quote=True)
        orbit_links.append(
            f'<a class="mobile-orbit-item {item["slot"]}{active_class}" href="{href}" target="_self" aria-label="{ui_html(item["label"])}">'
            f'{visual_icon_html(item["key"], "#0f766e", "mobile-nav-image-icon")}'
            f'<span>{ui_html(item["label"])}</span></a>'
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
            f'{visual_icon_html("diary", "#ec4899", "mobile-nav-image-icon")}<span>{ui_html("Personal Memory")}</span></a></div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_mobile_view_summary(active_key: str) -> None:
    title_map = {
        "life": "Life Context",
        "finance": "Finance Readiness",
        "portfolio": "Portfolio Check",
        "advisor": "Case Studies",
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
        "reit": "Review real estate value, income durability, and rate-sensitive exposure.",
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


def level_pct(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def finance_result_from_current_inputs() -> tuple[dict[str, Any], str]:
    finance_keys = [
        "pf_monthly_income",
        "pf_fixed_expenses",
        "pf_variable_expenses",
        "pf_cash_savings",
        "pf_taxable_investments",
        "pf_retirement_accounts",
        "pf_real_estate_value",
        "pf_credit_card_debt",
        "pf_student_loan",
        "pf_auto_loan",
        "pf_mortgage",
        "pf_monthly_debt_payment",
        "pf_monthly_savings_goal",
        "pf_target_goal_amount",
        "pf_current_goal_savings",
        "pf_investment_risk_score",
        "pf_runway_target_months",
        "pf_study_months_remaining",
    ]
    if not all(key in st.session_state for key in finance_keys):
        return st.session_state.get("last_personal_finance_result") or {}, st.session_state.get("pf_display_currency", "USD")
    try:
        from personal_finance_engine import PersonalFinanceProfile, calculate_personal_finance

        profile = PersonalFinanceProfile(
            monthly_income=float(st.session_state.get("pf_monthly_income") or 0),
            fixed_expenses=float(st.session_state.get("pf_fixed_expenses") or 0),
            variable_expenses=float(st.session_state.get("pf_variable_expenses") or 0),
            cash_savings=float(st.session_state.get("pf_cash_savings") or 0),
            taxable_investments=float(st.session_state.get("pf_taxable_investments") or 0),
            retirement_accounts=float(st.session_state.get("pf_retirement_accounts") or 0),
            real_estate_value=float(st.session_state.get("pf_real_estate_value") or 0),
            credit_card_debt=float(st.session_state.get("pf_credit_card_debt") or 0),
            student_loan=float(st.session_state.get("pf_student_loan") or 0),
            auto_loan=float(st.session_state.get("pf_auto_loan") or 0),
            mortgage=float(st.session_state.get("pf_mortgage") or 0),
            monthly_debt_payment=float(st.session_state.get("pf_monthly_debt_payment") or 0),
            monthly_savings_goal=float(st.session_state.get("pf_monthly_savings_goal") or 0),
            target_goal_amount=max(1.0, float(st.session_state.get("pf_target_goal_amount") or 1)),
            current_goal_savings=float(st.session_state.get("pf_current_goal_savings") or 0),
            investment_risk_score=float(st.session_state.get("pf_investment_risk_score") or 0),
            runway_target_months=max(1.0, float(st.session_state.get("pf_runway_target_months") or 6)),
            study_months_remaining=max(0.0, float(st.session_state.get("pf_study_months_remaining") or 0)),
        )
        return calculate_personal_finance(profile), st.session_state.get("pf_display_currency", "USD")
    except Exception:
        return st.session_state.get("last_personal_finance_result") or {}, st.session_state.get("pf_display_currency", "USD")


def client_report_state() -> dict[str, Any]:
    language = current_language()
    goal = active_goal_key()
    goal_config = NORA_GOAL_STRATEGIES.get(goal or "")
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    personal, personal_currency = finance_result_from_current_inputs()
    personal_currency = personal_currency or base_currency
    scenario = st.session_state.get("last_scenario_packet")
    total_value, weighted_beta, valuation_score, sector_values = portfolio_metrics()
    holdings = portfolio_holdings_snapshot() if st.session_state.get("portfolio") else []
    resilience = portfolio_resilience_summary(holdings, sector_values, weighted_beta, valuation_score)

    no_income = bool(personal.get("no_income_mode"))
    monthly_surplus = float(personal.get("monthly_surplus") or 0)
    emergency = float(personal.get("emergency_months") or 0)
    required_runway = max(1.0, float(personal.get("required_runway_months") or 6))
    runway_gap = float(personal.get("runway_gap_months") or 0)
    planning_health = float(
        personal.get("planning_health_score")
        or personal.get("financial_health_score")
        or 0
    )
    investment_exposure = float(personal.get("investment_exposure_ratio") or 0)
    top_holding_weight = float(resilience.get("top_holding_weight") or 0) if resilience else 0.0
    top_sector_weight = float(resilience.get("top_sector_weight") or 0) if resilience else 0.0

    if personal:
        if no_income and monthly_surplus < 0:
            problem_title = "소득 공백" if language == "ko" else "Income Gap"
            problem_sub = (
                f"{fmt_money_compact(abs(monthly_surplus), personal_currency, language)}/월 소진"
                if language == "ko"
                else f"{fmt_money_compact(abs(monthly_surplus), personal_currency, language)}/mo burn"
            )
            problem_detail = (
                "현재 돈을 벌지 않는 기간에는 저축률보다 현금 생존기간과 강제매도 위험이 핵심 문제입니다."
                if language == "ko"
                else "During a no-income period, cash runway and forced-selling risk matter more than savings-rate benchmarks."
            )
            problem_level = 82
            problem_color = "#d97706"
        elif monthly_surplus < 0:
            problem_title = "현금흐름 적자" if language == "ko" else "Cashflow Leak"
            problem_sub = (
                f"{fmt_money_compact(abs(monthly_surplus), personal_currency, language)}/월 부족"
                if language == "ko"
                else f"{fmt_money_compact(abs(monthly_surplus), personal_currency, language)}/mo gap"
            )
            problem_detail = (
                "월 지출이 월 수입보다 커서 투자 판단보다 지출 속도와 현금 완충력이 먼저입니다."
                if language == "ko"
                else "Monthly outflow is above monthly income, so burn rate and cash buffer come before asset decisions."
            )
            problem_level = 88
            problem_color = "#dc2626"
        elif emergency < required_runway:
            problem_title = "생존기간 부족" if language == "ko" else "Runway Gap"
            problem_sub = (
                f"{emergency:.1f}/{required_runway:.1f}개월"
                if language == "ko"
                else f"{emergency:.1f}/{required_runway:.1f} months"
            )
            problem_detail = (
                "목표 생존기간보다 현금 완충 기간이 짧아 큰 포트폴리오 결정보다 현금 계획이 먼저입니다."
                if language == "ko"
                else "Cash runway is below the selected target, so the cash plan should precede large portfolio decisions."
            )
            problem_level = 76
            problem_color = "#d97706"
        elif investment_exposure >= 0.60:
            problem_title = "시장 노출 높음" if language == "ko" else "Market Heavy"
            problem_sub = f"{investment_exposure * 100:.0f}%"
            problem_detail = (
                "총자산 중 투자자산 비중이 높아 생활비와 시장 하락이 같은 시점에 겹칠 수 있습니다."
                if language == "ko"
                else "Investment exposure is high, so living-cost needs and market drawdown can collide."
            )
            problem_level = 68
            problem_color = "#d97706"
        else:
            problem_title = "큰 결함 없음" if language == "ko" else "No Major Gap"
            problem_sub = (
                f"건강도 {planning_health:.0f}/100"
                if language == "ko"
                else f"Health {planning_health:.0f}/100"
            )
            problem_detail = (
                "현재 입력값에서는 유동성, 부채, 현금흐름의 큰 단절은 보이지 않습니다."
                if language == "ko"
                else "Current inputs do not show a major break in liquidity, debt, or cash flow."
            )
            problem_level = max(30, 100 - planning_health)
            problem_color = "#0f766e"
    else:
        problem_title = "상황 입력 필요" if language == "ko" else "Situation Missing"
        problem_sub = "재무 입력 먼저" if language == "ko" else "Finance first"
        problem_detail = (
            "수입, 지출, 현금, 투자자산을 입력해야 현재 문제가 실제로 현금흐름인지, 포트폴리오인지 구분됩니다."
            if language == "ko"
            else "Enter income, spending, cash, and investments before the app can separate cashflow risk from portfolio risk."
        )
        problem_level = 72
        problem_color = "#d97706"

    scenario_delta = None
    if scenario:
        try:
            scenario_delta = float(scenario.get("portfolio", {}).get("scenario_delta_pct"))
        except (TypeError, ValueError):
            scenario_delta = None

    if scenario_delta is not None:
        if scenario_delta <= -25:
            crisis_title = "충격 손실" if language == "ko" else "Stress Loss"
            crisis_sub = f"{scenario_delta:+.1f}%"
            crisis_detail = (
                "최근 시나리오에서 자산 하락 폭이 큽니다. 생활비 충당을 위해 투자자산을 팔아야 하는지 먼저 봐야 합니다."
                if language == "ko"
                else "The latest stress case shows a large drawdown. Check whether living needs could force asset sales."
            )
            crisis_level = min(100, abs(scenario_delta) * 2.8)
            crisis_color = "#dc2626"
        elif scenario_delta < 0:
            crisis_title = "하락 주의" if language == "ko" else "Stress Watch"
            crisis_sub = f"{scenario_delta:+.1f}%"
            crisis_detail = (
                "시나리오 손실은 감당 가능 범위일 수 있지만, 반복 검토와 현금 완충 확인이 필요합니다."
                if language == "ko"
                else "The stress loss may be usable, but it still needs repeat review and cash-buffer confirmation."
            )
            crisis_level = max(42, min(82, abs(scenario_delta) * 2.2))
            crisis_color = "#d97706"
        else:
            crisis_title = "충격 감당" if language == "ko" else "Stress Usable"
            crisis_sub = f"{scenario_delta:+.1f}%"
            crisis_detail = (
                "최근 시나리오에서는 큰 위험 신호가 낮습니다. 다음은 실제 생활비와 포트폴리오 집중도 확인입니다."
                if language == "ko"
                else "The latest scenario does not show a large stress signal. Next, confirm living costs and concentration."
            )
            crisis_level = 28
            crisis_color = "#0f766e"
    elif no_income and investment_exposure >= 0.55:
        crisis_title = "강제매도 위험" if language == "ko" else "Forced Sale Risk"
        crisis_sub = "생활비 + 하락장" if language == "ko" else "Living costs + drawdown"
        crisis_detail = (
            "수입이 없는 기간에 주식 비중이 높으면 시장 하락 때 생활비 때문에 불리한 가격에 팔 위험이 생깁니다."
            if language == "ko"
            else "A no-income period with high stock exposure creates the risk of selling assets at poor prices during a drawdown."
        )
        crisis_level = 86
        crisis_color = "#dc2626"
    elif total_value > 0 and not scenario:
        crisis_title = "하락 미검증" if language == "ko" else "Downside Untested"
        crisis_sub = "-30% 필요" if language == "ko" else "-30% needed"
        crisis_detail = (
            "포트폴리오가 입력됐지만 하락 시나리오가 없어 위기 때 자본과 생존기간이 어떻게 바뀌는지 아직 모릅니다."
            if language == "ko"
            else "Portfolio data exists, but no downside scenario shows how capital and runway change in crisis."
        )
        crisis_level = 66
        crisis_color = "#d97706"
    elif not personal:
        crisis_title = "블라인드 스팟" if language == "ko" else "Blind Spot"
        crisis_sub = "위기 미측정" if language == "ko" else "Risk unknown"
        crisis_detail = (
            "상황 입력이 부족해 위기가 부족한 현금인지, 높은 투자 노출인지, 목표 불일치인지 아직 구분되지 않습니다."
            if language == "ko"
            else "Without situation inputs, the app cannot tell whether the crisis is cash, market exposure, or goal mismatch."
        )
        crisis_level = 70
        crisis_color = "#d97706"
    elif top_holding_weight >= 0.40 or top_sector_weight >= 0.60:
        crisis_title = "집중 위험" if language == "ko" else "Concentration Risk"
        crisis_sub = (
            f"최대 {max(top_holding_weight, top_sector_weight) * 100:.0f}%"
            if language == "ko"
            else f"Top {max(top_holding_weight, top_sector_weight) * 100:.0f}%"
        )
        crisis_detail = (
            "한 종목이나 한 섹터가 결과를 크게 좌우합니다. 고객이 이해하기 쉬운 한도 규칙이 필요합니다."
            if language == "ko"
            else "One holding or sector can dominate the result. A simple client-readable limit rule is needed."
        )
        crisis_level = 74
        crisis_color = "#d97706"
    else:
        crisis_title = "큰 위기 낮음" if language == "ko" else "Low Crisis Signal"
        crisis_sub = "시나리오 권장" if language == "ko" else "Scenario advised"
        crisis_detail = (
            "현재 입력상 큰 위기 신호는 낮지만, 하락 시나리오는 아직 별도로 확인하는 편이 좋습니다."
            if language == "ko"
            else "Current inputs show a lower crisis signal, but a downside scenario is still worth running."
        )
        crisis_level = 34
        crisis_color = "#0f766e"

    if not personal:
        direction_title = "상황 입력" if language == "ko" else "Enter Situation"
        direction_sub = "수입·지출·현금" if language == "ko" else "Income, spend, cash"
        direction_detail = (
            "첫 방향은 계산 가능한 현재 상황을 만드는 것입니다. Finance에서 입력 후 다시 계산을 누르세요."
            if language == "ko"
            else "The first direction is to make the current situation calculable. Enter Finance inputs and apply the calculation."
        )
        direction_level = 48
    elif no_income:
        direction_title = "생존기간 우선" if language == "ko" else "Runway First"
        direction_sub = "현금 바닥선 고정" if language == "ko" else "Lock cash floor"
        direction_detail = (
            "생활비를 버틸 현금 바닥선을 먼저 정하고, 그 다음 포트폴리오 하락과 소득 회복 계획을 봅니다."
            if language == "ko"
            else "Set the cash floor for living costs first, then review portfolio drawdown and income recovery."
        )
        direction_level = 92
    elif goal == "grow_capital" and total_value > 0:
        direction_title = "품질 성장" if language == "ko" else "Quality Growth"
        direction_sub = "집중도·가치평가" if language == "ko" else "Concentration + valuation"
        direction_detail = (
            "성장은 가능하지만 종목 집중도, 베타, valuation, 하락 감당력을 함께 봐야 합니다."
            if language == "ko"
            else "Growth can be reviewed, but concentration, beta, valuation, and downside capacity should stay visible."
        )
        direction_level = 78
    elif goal_config:
        direction_title = goal_config[f"label_{language}"]
        direction_sub = goal_config[f"short_{language}"]
        direction_detail = goal_config[f"strategy_{language}"]
        direction_level = 72
    else:
        direction_title = "목표 선택" if language == "ko" else "Choose Goal"
        direction_sub = "전략 기준 필요" if language == "ko" else "Strategy anchor needed"
        direction_detail = (
            "고객이 원하는 목적을 먼저 선택해야 같은 데이터도 다르게 해석할 수 있습니다."
            if language == "ko"
            else "Choose the customer's purpose first, because the same data means different things under different goals."
        )
        direction_level = 44

    runway_priority = 94 if no_income or monthly_surplus < 0 else 72 if emergency < required_runway else 42
    portfolio_priority = 88 if investment_exposure >= 0.55 or top_holding_weight >= 0.40 else 64 if total_value > 0 else 30
    scenario_priority = 90 if total_value > 0 and not scenario else 58 if scenario else 36
    direction_steps = [
        {
            "icon": "runway",
            "title": "현금 바닥선" if language == "ko" else "Cash Floor",
            "sub": "생활비 생존기간" if language == "ko" else "Living runway",
            "level": runway_priority,
            "color": "#0f766e",
        },
        {
            "icon": "portfolio",
            "title": "포트폴리오 한도" if language == "ko" else "Portfolio Guard",
            "sub": "집중도와 하락" if language == "ko" else "Concentration + downside",
            "level": portfolio_priority,
            "color": "#2563eb",
        },
        {
            "icon": "scenario",
            "title": "위기 리허설" if language == "ko" else "Crisis Rehearsal",
            "sub": "-30%와 소득 공백" if language == "ko" else "-30% and income gap",
            "level": scenario_priority,
            "color": "#d97706",
        },
    ]

    evidence = []
    if personal:
        evidence.extend(
            [
                (
                    f"월 잉여 현금 {fmt_money_compact(monthly_surplus, personal_currency, language)}"
                    if language == "ko"
                    else f"Monthly surplus {fmt_money_compact(monthly_surplus, personal_currency, language)}"
                ),
                (
                    f"현금 생존기간 {emergency:.1f}개월 / 필요 {required_runway:.1f}개월"
                    if language == "ko"
                    else f"Cash runway {emergency:.1f} months / required {required_runway:.1f} months"
                ),
                (
                    f"투자자산 노출 {investment_exposure * 100:.1f}%"
                    if language == "ko"
                    else f"Investment exposure {investment_exposure * 100:.1f}%"
                ),
            ]
        )
        if no_income:
            evidence.append(
                "무소득 학업/전환 모드: 저축률보다 생존기간과 하락 감당력이 우선"
                if language == "ko"
                else "No-income transition mode: runway and drawdown capacity come before savings rate"
            )
        if runway_gap:
            evidence.append(
                f"생존기간 차이 {runway_gap:+.1f}개월"
                if language == "ko"
                else f"Runway gap {runway_gap:+.1f} months"
            )
    else:
        evidence.append(
            "Finance 입력이 없어 현금흐름과 생존기간은 아직 계산 전입니다."
            if language == "ko"
            else "Finance inputs are missing, so cashflow and runway are not yet calculated."
        )

    if total_value > 0:
        evidence.append(
            (
                f"포트폴리오 {fmt_money_compact(total_value, base_currency, language)}, 베타 {fmt_number(weighted_beta)}, valuation {valuation_score:+.1f}%"
                if valuation_score is not None
                else f"포트폴리오 {fmt_money_compact(total_value, base_currency, language)}, 베타 {fmt_number(weighted_beta)}"
            )
            if language == "ko"
            else (
                f"Portfolio {fmt_money_compact(total_value, base_currency, language)}, beta {fmt_number(weighted_beta)}, valuation {valuation_score:+.1f}%"
                if valuation_score is not None
                else f"Portfolio {fmt_money_compact(total_value, base_currency, language)}, beta {fmt_number(weighted_beta)}"
            )
        )
        if resilience:
            evidence.append(
                (
                    f"최대 종목 {top_holding_weight * 100:.1f}%, 최대 섹터 {top_sector_weight * 100:.1f}%"
                    if language == "ko"
                    else f"Top holding {top_holding_weight * 100:.1f}%, top sector {top_sector_weight * 100:.1f}%"
                )
            )
    else:
        evidence.append(
            "Portfolio 입력이 없어 시장 하락 충격은 아직 제한적으로만 볼 수 있습니다."
            if language == "ko"
            else "Portfolio inputs are missing, so market drawdown can only be read in a limited way."
        )

    evidence.append(
        (
            f"최근 시나리오 {scenario_delta:+.1f}%"
            if scenario_delta is not None
            else "시나리오 미실행"
        )
        if language == "ko"
        else (
            f"Latest scenario {scenario_delta:+.1f}%"
            if scenario_delta is not None
            else "No scenario run yet"
        )
    )

    return {
        "cards": [
            {
                "icon": "risk",
                "label": "문제" if language == "ko" else "Problem",
                "title": problem_title,
                "sub": problem_sub,
                "detail": problem_detail,
                "level": problem_level,
                "color": problem_color,
            },
            {
                "icon": "scenario",
                "label": "위기" if language == "ko" else "Crisis",
                "title": crisis_title,
                "sub": crisis_sub,
                "detail": crisis_detail,
                "level": crisis_level,
                "color": crisis_color,
            },
            {
                "icon": "decision",
                "label": "방향" if language == "ko" else "Direction",
                "title": direction_title,
                "sub": direction_sub,
                "detail": direction_detail,
                "level": direction_level,
                "color": "#0f766e" if direction_level >= 75 else "#2563eb",
            },
        ],
        "direction_steps": direction_steps,
        "evidence": evidence[:7],
    }


def render_client_visual_report() -> None:
    language = current_language()
    report = client_report_state()
    card_html = []
    for card in report["cards"]:
        level = level_pct(float(card["level"]))
        color = clean_hex_color(card["color"], "#0f766e")
        card_html.append(
            f'<div class="client-report-card" tabindex="0" style="--report-color: {color};" '
            f'title="{escape(str(card["detail"]), quote=True)}">'
            '<div class="client-report-main">'
            f'<span class="client-report-icon">{visual_icon_html(card["icon"], color, "client-report-image-icon")}</span>'
            '<div class="client-report-text">'
            f'<small>{escape(str(card["label"]))}</small>'
            f'<b>{escape(str(card["title"]))}</b>'
            f'<em>{escape(str(card["sub"]))}</em>'
            '</div></div>'
            f'<div class="client-report-meter" aria-hidden="true"><i style="--level: {level:.0f}%;"></i></div>'
            f'<span class="client-report-detail">{escape(str(card["detail"]))}</span>'
            '</div>'
        )

    step_html = []
    for step in report["direction_steps"]:
        level = level_pct(float(step["level"]))
        color = clean_hex_color(step["color"], "#0f766e")
        step_html.append(
            f'<div class="client-direction-step" style="--step-color: {color};">'
            f'<span>{visual_icon_html(step["icon"], color, "client-direction-image-icon")}</span>'
            f'<b>{escape(str(step["title"]))}</b>'
            f'<em>{escape(str(step["sub"]))}</em>'
            f'<i style="--level: {level:.0f}%;"></i>'
            '</div>'
        )

    evidence_title = "근거 보기" if language == "ko" else "Show Evidence"
    evidence_note = "계산값은 필요할 때만 확인" if language == "ko" else "Numbers stay behind the visual layer"
    evidence_items = "".join(f"<li>{escape(str(item))}</li>" for item in report["evidence"])
    st.markdown(
        f"""
        <section class="client-visual-report" aria-label="{escape('고객 시각 리포트' if language == 'ko' else 'Client Visual Report')}">
            <div class="client-report-cards">{"".join(card_html)}</div>
            <div class="client-direction-rail">{"".join(step_html)}</div>
            <details class="client-report-evidence">
                <summary><span>{escape(evidence_title)}</span><span>{escape(evidence_note)}</span></summary>
                <ul>{evidence_items}</ul>
            </details>
        </section>
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
        target_href = escape(life_entry_href(), quote=True)
        target_text = "Change goal or strategy" if language == "en" else "목표/전략 다시 선택"
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
                <a class="goal-strategy-return" href="{target_href}" target="_self" title="{escape(target_text, quote=True)}">
                    <b>{escape(label)}</b>
                </a>
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


def render_finance_snapshot_ribbon(active_key: str) -> None:
    language = current_language()
    goal = active_goal_key()
    personal = st.session_state.get("last_personal_finance_result") or {}
    scenario = st.session_state.get("last_scenario_packet")
    total_value, weighted_beta, valuation_score, _ = portfolio_metrics()
    holdings_count = len(st.session_state.get("portfolio", {}))
    base_currency = st.session_state.get("portfolio_base_currency", "USD")

    if goal:
        config = NORA_GOAL_STRATEGIES[goal]
        goal_value = config[f"label_{language}"]
        goal_sub = config[f"short_{language}"]
        goal_detail = config[f"strategy_{language}"]
        goal_tone = "good"
        goal_level = 100.0
    else:
        goal_value = "No goal" if language == "en" else "목표 없음"
        goal_sub = "Choose first" if language == "en" else "먼저 선택"
        goal_detail = (
            "Goal selection guides the strategy before any calculation."
            if language == "en"
            else "목표 선택이 계산보다 먼저 전략의 기준을 정합니다."
        )
        goal_tone = "watch"
        goal_level = 28.0

    if personal:
        emergency = float(personal.get("emergency_months") or 0)
        health = float(personal.get("financial_health_score") or 0)
        required_runway = max(1.0, float(personal.get("required_runway_months") or 6))
        surplus = float(personal.get("monthly_surplus") or 0)
        runway_value = f"{emergency:.1f} mo" if language == "en" else f"{emergency:.1f}개월"
        runway_sub = f"Health {health:.0f}/100" if language == "en" else f"건강도 {health:.0f}/100"
        runway_detail = (
            f"Monthly surplus: {fmt_money_compact(surplus, 'KRW' if base_currency == 'KRW' else 'USD', language)}. "
            "Liquidity and planning health show whether the life situation can absorb risk."
            if language == "en"
            else f"월 잉여 현금: {fmt_money_compact(surplus, 'KRW' if base_currency == 'KRW' else 'USD', language)}. "
            "유동성과 계획 건강도는 현재 삶이 위험을 감당할 수 있는지 보여줍니다."
        )
        runway_tone = "good" if emergency >= 6 and health >= 70 else "mid" if emergency >= 3 and health >= 50 else "watch"
        runway_level = max(5.0, min(100.0, (emergency / required_runway) * 100))
    else:
        runway_value = "Input" if language == "en" else "입력"
        runway_sub = "No finance data" if language == "en" else "재무 데이터 없음"
        runway_detail = (
            "Enter income, expenses, cash, debt, and goals to unlock runway and health."
            if language == "en"
            else "수입, 지출, 현금, 부채, 목표를 입력하면 생존기간과 건강도가 열립니다."
        )
        runway_tone = "watch"
        runway_level = 18.0

    if total_value > 0:
        portfolio_value = fmt_money_compact(total_value, base_currency, language)
        valuation_text = "N/A" if valuation_score is None else f"{valuation_score:+.1f}%"
        portfolio_sub = f"Valuation {valuation_text}" if language == "en" else f"가치평가 {valuation_text}"
        beta_text = fmt_number(weighted_beta)
        portfolio_detail = (
            f"{holdings_count} holding(s). Weighted beta {beta_text}. "
            "Portfolio value and valuation score show market exposure before action."
            if language == "en"
            else f"{holdings_count}개 보유. 가중 베타 {beta_text}. "
            "포트폴리오 가치와 valuation 점수는 행동 전 시장 노출을 보여줍니다."
        )
        portfolio_tone = "good" if valuation_score is not None and valuation_score >= 5 else "watch" if valuation_score is not None and valuation_score <= -5 else "mid"
        portfolio_level = max(22.0, min(100.0, holdings_count * 18.0 + (50.0 if valuation_score is not None else 22.0)))
    else:
        portfolio_value = "Add holdings" if language == "en" else "종목 추가"
        portfolio_sub = "No portfolio" if language == "en" else "포트폴리오 없음"
        portfolio_detail = (
            "Search ticker or company name from Portfolio, then add positions for valuation."
            if language == "en"
            else "포트폴리오에서 티커나 회사명을 검색한 뒤 포지션을 추가하면 가치평가가 계산됩니다."
        )
        portfolio_tone = "watch"
        portfolio_level = 16.0

    if scenario:
        risk_value = "Stress ready" if language == "en" else "스트레스 준비"
        risk_sub = "Scenario exists" if language == "en" else "시나리오 있음"
        risk_tone = "good"
        risk_level = 88.0
    elif personal or total_value > 0:
        risk_value = "Watch" if language == "en" else "주의"
        risk_sub = "Scenario needed" if language == "en" else "시나리오 필요"
        risk_tone = "mid"
        risk_level = 54.0
    else:
        risk_value = "Needs data" if language == "en" else "데이터 필요"
        risk_sub = "Finance + portfolio" if language == "en" else "재무 + 포트폴리오"
        risk_tone = "watch"
        risk_level = 18.0
    risk_detail = (
        "Risk signal combines scenario, portfolio, finance, and memory readiness."
        if language == "en"
        else "위험 신호는 시나리오, 포트폴리오, 재무, 메모리 준비도를 함께 봅니다."
    )

    cards = [
        ("target", "Goal" if language == "en" else "목표", goal_value, goal_sub, goal_detail, goal_tone, goal_level),
        ("runway", "Runway" if language == "en" else "생존기간", runway_value, runway_sub, runway_detail, runway_tone, runway_level),
        ("portfolio", "Portfolio Value" if language == "en" else "포트폴리오 가치", portfolio_value, portfolio_sub, portfolio_detail, portfolio_tone, portfolio_level),
        ("risk", "Risk Signal" if language == "en" else "위험 신호", risk_value, risk_sub, risk_detail, risk_tone, risk_level),
    ]
    card_html = []
    tone_colors = {"good": "#0f766e", "mid": "#2563eb", "watch": "#d97706"}
    for glyph, label, value, sub, detail, tone, level in cards:
        level = max(0.0, min(100.0, float(level)))
        card_html.append(
            f'<div class="finance-snapshot-card {escape(tone)}" tabindex="0" title="{escape(detail, quote=True)}">'
            f'<span class="finance-snapshot-glyph image-glyph">{visual_icon_html(glyph, tone_colors.get(tone, "#0f766e"), "finance-snapshot-icon")}</span>'
            f'<small>{escape(label)}</small>'
            f'<b>{escape(value)}</b>'
            f'<em>{escape(sub)}</em>'
            f'<span class="finance-snapshot-meter" aria-hidden="true"><i style="--level: {level:.0f}%;"></i></span>'
            f'<span class="finance-snapshot-detail">{escape(detail)}</span>'
            '</div>'
        )

    st.markdown(
        f'<section class="finance-snapshot-ribbon" aria-label="{escape("Client Snapshot" if language == "en" else "고객 스냅샷")}">'
        f'{"".join(card_html)}'
        '</section>',
        unsafe_allow_html=True,
    )


def render_rationality_gate() -> None:
    snapshot = rationality_gate_snapshot()
    score = max(0.0, min(100.0, float(snapshot["score"])))
    tone = rationality_tone(score)
    tone_color = {"good": "#0f766e", "mid": "#2563eb", "watch": "#d97706"}[tone]
    pillar_nodes = []
    path_labels = ["Capture", "Purpose", "Evidence", "Decision", "Memory"]
    path_html = "".join(
        f'<span>{ui_html(label)}</span>'
        + ('<i aria-hidden="true">&rarr;</i>' if index < len(path_labels) - 1 else "")
        for index, label in enumerate(path_labels)
    )
    detail_items = [
        f'<li><b>{ui_html("Rationality Gate")}</b><span>{ui_html("Rationality means goal-fit, evidence, model discipline, risk awareness, and memory before action.")}</span></li>'
    ]
    for item in snapshot["pillars"]:
        pillar_score = max(0.0, min(100.0, float(item["score"])))
        pillar_tone = rationality_tone(pillar_score)
        detail = str(item["detail"])
        node_color = {"good": "#0f766e", "mid": "#2563eb", "watch": "#d97706"}[pillar_tone]
        pillar_nodes.append(
            f'<span class="rationality-node {pillar_tone}" tabindex="0" '
            f'title="{escape(ui(item["label"]) + ": " + detail, quote=True)}" '
            f'style="--value: {pillar_score:.0f}%;">'
            f'{visual_icon_html(item["glyph"], node_color, "rationality-icon")}</span>'
        )
        detail_items.append(
            f'<li><b>{ui_html(item["label"])}</b><span>{escape(detail)}</span></li>'
        )

    st.markdown(
        f"""
        <section class="rationality-gate {tone}" style="--rational-color: {tone_color};" aria-label="{ui_html('Rationality Gate')}">
            <div class="rationality-gate-main">
                <b>{ui_html('Rationality Gate')}</b>
                <div class="rationality-path" aria-label="{ui_html('Capture → Purpose → Evidence → Decision → Memory')}">{path_html}</div>
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
    render_decision_capture_panel()
    cards = []
    for goal_key, config in NORA_GOAL_STRATEGIES.items():
        cards.append(
            f'<a class="life-goal-link" style="--goal-color: {escape(config["color"])};" '
            f'href="{escape(goal_href(goal_key), quote=True)}" target="_self">'
            f'<span>{visual_icon_html(goal_key, config["color"], "life-goal-icon")}</span><b>{escape(config[f"label_{language}"])}</b>'
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
    render_visual_asset_theme()

    brand_subtitle = (
        "개인 의사결정 인텔리전스"
        if current_language() == "ko"
        else "PERSONAL DECISION INTELLIGENCE"
    )
    st.markdown(
        f"""
        <div class="brand-header">
            <div class="brand-mark">
                <div class="brand-icon" aria-hidden="true">{brand_logo_html()}</div>
                <div class="brand-copy">
                    <div class="brand-wordmark">
                        <div class="brand-name">LY-Scope</div>
                        <div class="brand-version">Ver.2</div>
                    </div>
                    <div class="brand-subtitle">{brand_subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    active_view = active_nav_key()
    render_finance_snapshot_ribbon(active_view)
    render_client_visual_report()
    render_goal_strategy_strip(active_view)
    render_rationality_gate()
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
if intro_mode_requested():
    st.session_state.life_entry_complete = False
    st.session_state.life_entry_version_seen = ""
elif dashboard_mode_requested():
    st.session_state.life_entry_complete = True
    st.session_state.life_entry_version_seen = LIFE_ENTRY_VERSION
show_life_entry = (
    intro_mode_requested()
    or
    not st.session_state.life_entry_complete
    or st.session_state.life_entry_version_seen != LIFE_ENTRY_VERSION
)
if show_life_entry:
    render_life_entry_screen()
else:
    render_main_app()

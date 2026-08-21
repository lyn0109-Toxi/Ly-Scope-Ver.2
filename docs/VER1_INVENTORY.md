# LY-Scope Ver.1 Inventory

Ver.1 원본 코드는 이번 작업에서 건드리지 않았습니다. 로컬 원본은 `/Users/leeyoung-nam/Documents/LY-STScope/LY-Scope-v1`에 있고, Ver.2 내부에는 `.git`, `__pycache__`, `*.pyc`를 제외한 복사본을 `legacy/ver1-reference/`로 보존했습니다.

## Observed Ver.1 Structure

| Area | Files | Status in Ver.2 |
| --- | --- | --- |
| Streamlit app shell | `app.py`, `ly_scope/views/*` | Legacy reference copy |
| Stock, REIT, real estate, finance formulas | `ly_scope/analytics.py` | Core formulas ported to JavaScript |
| Financial objectives | `ly_scope/objectives.py` | Current Ver.2 goals exist; detailed return/tax model remains next migration |
| Life Board context | `ly_scope/life_context.py` | Core component weighting ported |
| Local JSON storage | `ly_scope/storage.py`, `ly_scope/data_loader.py` | Preserved and mapped to Ver.2 adapter boundary |
| Sample data | `data/*.json` | Active reference data for Ver.2 legacy panel |
| Reports and visual assets | `reports/*` | Preserved as reference assets |
| Operations docs | `OPERATIONS.md`, `DATA_SOURCES.md`, `PRIVACY_NOTICE.md`, `THIRD_PARTY_NOTICES.md` | Preserved as production guardrail references |

## Classification

| Ver.1 Area | Ver.2 Decision | Target Module | Rule |
| --- | --- | --- | --- |
| User profile inputs | Keep or adjust | `domain/user` | 사용자 선호, 의사결정 스타일, 기본 프로필은 보존합니다. |
| Raw financial inputs | Keep | `domain/financial-foundation` | 입력 필드와 계산 의미가 명확하면 그대로 옮깁니다. |
| Net worth and cash flow logic | Keep with tests | `domain/financial-foundation` | 수식은 테스트로 고정한 뒤 이전합니다. |
| Stock scoring | Keep with tests | `domain/market-assets` | Ver.1 valuation, momentum, quality, risk balance 수식을 옮겼습니다. |
| REIT scoring | Keep with tests | `domain/market-assets` | valuation, income, property, supply, rate 수식을 옮겼습니다. |
| Real estate scoring | Keep with tests | `domain/real-estate` | market score, warnings, forecast, property calculator를 옮겼습니다. |
| Portfolio snapshot | Keep with tests | `domain/portfolio` | holdings 기반 market value, P/L, weight, beta 계산을 옮겼습니다. |
| Life Board | Modify | `domain/life-board` | Streamlit session 의존성은 제거하고 component scoring만 옮겼습니다. |
| Goal tracking | Keep or adjust | `domain/goals` | 목표 구조는 유지하되 due date, priority, funding pressure를 표준화합니다. |
| Projection logic | Keep if deterministic | `domain/projection` | 시계열 계산은 순수 함수로 분리합니다. |
| Scenario logic | Modify | `domain/scenario` | 임의 UI 상태와 분리하고 입력값 기반 비교 함수로 바꿉니다. |
| Risk labels | Modify | `domain/risk-resilience` | 단순 경고 문구는 점수, severity, evidence source로 재구성합니다. |
| AI prompts or text output | Modify | `domain/ai-interpretation` | 프롬프트와 해석은 evidence 기반으로 재작성합니다. |
| Saved decisions | Keep | `domain/decision` and `domain/memory` | 기록, 날짜, 점수, 근거를 표준 record로 옮깁니다. |
| Local storage | Keep with adapter | `src/storage` | 저장 key와 schema migration을 분리합니다. |
| Global mutable state | Retire | `src/app` | 앱 state orchestration으로 대체합니다. |
| Monolithic UI components | Retire gradually | `src/ui` | 화면은 보존 가능하지만 domain logic은 UI에서 제거합니다. |
| Dead prototype screens | Retire | N/A | 현재 Ver.2 흐름에 연결되지 않으면 이전하지 않습니다. |

## Migration Rule

1. Ver.1 파일은 원본 그대로 둡니다.
2. 필요한 로직만 Ver.2 모듈에 복사하거나 재작성합니다.
3. 이전한 계산식은 테스트로 잠급니다.
4. UI보다 domain function을 먼저 이전합니다.
5. decision memory에 영향을 주는 변경은 migration note를 남깁니다.

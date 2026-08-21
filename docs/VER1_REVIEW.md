# Ver.1 Content Review

검토한 Ver.1 위치:

```text
/Users/leeyoung-nam/Documents/LY-STScope/LY-Scope-v1
```

Ver.1 원본은 수정하지 않았고, Ver.2에는 다음 위치로 복사했습니다.

```text
legacy/ver1-reference
```

## Ver.1 Product Shape

Ver.1은 Streamlit 기반의 life asset decision console입니다. 주요 흐름은 다음입니다.

```text
Search asset or region
-> Score opportunity
-> Show forecast ranges
-> Screen warnings
-> Save decision to diary
```

Ver.2 목표 아키텍처와의 매핑:

| Ver.1 Flow | Ver.2 Architecture |
| --- | --- |
| Search asset or region | Data |
| Score opportunity | Model |
| Forecast ranges | Projection / Scenario |
| Screen warnings | Evidence / Risk-Resilience |
| Save decision to diary | Decision / Memory |

## Key Findings

- `ly_scope/analytics.py` contains the most valuable reusable logic: stock score, REIT score, real estate market score, real estate forecast, mortgage math, property calculator, personal finance score, and aggregate life score.
- `ly_scope/objectives.py` adds a financial objective planning layer with expected return, tax/fee drag, required monthly contribution, readiness score, and scenario stress.
- `ly_scope/life_context.py` already behaves like a Ver.2 evidence context builder. It combines Market Assets, Real Estate, Personal Assets, Financial Objectives, warnings, missing data, and next actions.
- `ly_scope/storage.py` and `ly_scope/data_loader.py` are good boundaries for future durable storage because they hide local JSON details behind adapter functions.
- `ly_scope/views/*` should be treated as workflow reference, not copied directly into Ver.2 UI, because they are Streamlit-specific.
- `data/*.json` provides useful prototype seed data for stocks, REITs, real estate markets, state coverage, diary, and portfolio examples.

## Already Moved Into Ver.2

| Ver.1 Logic | Ver.2 File |
| --- | --- |
| Stock scoring and warnings | `src/domain/market-assets/stocks.js` |
| REIT scoring, warnings, forecast | `src/domain/market-assets/reits.js` |
| Real estate scoring, warnings, forecast | `src/domain/real-estate/markets.js` |
| Mortgage and property calculator | `src/domain/real-estate/markets.js` |
| Portfolio snapshot | `src/domain/portfolio/portfolio.js` |
| Life Board weighted context | `src/domain/life-board/lifeContext.js` |
| Ver.1 copied-data loader | `src/adapters/ver1/ver1Data.js` |
| Ver.1 module inventory | `src/adapters/ver1/ver1Manifest.js` |

## Still To Migrate Later

- Full financial objective return/tax-drag model from `ly_scope/objectives.py`
- AI Coach response rules from `ly_scope/life_context.py`
- Diary import from Ver.1 user-state JSON into Ver.2 Memory schema
- Streamlit operation status concepts from `ly_scope/operations.py`
- Internationalization from `ly_scope/i18n.py` and `display_i18n.py`
- Visual report assets and report generator behavior

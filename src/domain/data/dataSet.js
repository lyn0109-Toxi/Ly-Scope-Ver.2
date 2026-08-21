import { normalizeProfile } from '../user/profile.js';
import { normalizeFinancialSnapshot } from '../financial-foundation/foundation.js';
import { normalizeGoals } from '../goals/goals.js';
import { DEFAULT_MARKET_ASSET_DETAIL } from '../market-assets/stocks.js';
import {
  DEFAULT_PORTFOLIO_HOLDINGS,
  normalizePortfolioHoldings,
} from '../portfolio/portfolio.js';
import { DEFAULT_REAL_ESTATE_DETAIL } from '../real-estate/markets.js';
import { normalizeScenario } from '../scenario/scenario.js';

export function buildDataLayer(rawState = {}) {
  return {
    profile: normalizeProfile(rawState.profile),
    financialSnapshot: normalizeFinancialSnapshot(rawState.financialSnapshot),
    goals: normalizeGoals(rawState.goals),
    marketAsset: {
      ...DEFAULT_MARKET_ASSET_DETAIL,
      ...(rawState.marketAsset || {}),
    },
    portfolioHoldings: normalizePortfolioHoldings(
      rawState.portfolioHoldings ?? DEFAULT_PORTFOLIO_HOLDINGS,
    ),
    realEstateAsset: {
      ...DEFAULT_REAL_ESTATE_DETAIL,
      ...(rawState.realEstateAsset || {}),
    },
    scenario: normalizeScenario(rawState.scenario),
    decisionQuestion: String(
      rawState.decisionQuestion ||
        'Should I move forward with this financial decision?',
    ).trim(),
    capturedAt: rawState.capturedAt || new Date().toISOString(),
  };
}

export function summarizeDataLayer(dataLayer) {
  return {
    owner: dataLayer.profile.name,
    goalCount: dataLayer.goals.length,
    scenarioName: dataLayer.scenario.name,
    decisionQuestion: dataLayer.decisionQuestion,
  };
}

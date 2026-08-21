import { DEFAULT_USER_PROFILE } from '../domain/user/profile.js';
import { DEFAULT_FINANCIAL_SNAPSHOT } from '../domain/financial-foundation/foundation.js';
import { DEFAULT_GOALS } from '../domain/goals/goals.js';
import { DEFAULT_SCENARIO } from '../domain/scenario/scenario.js';
import { DEFAULT_MARKET_ASSET_DETAIL } from '../domain/market-assets/stocks.js';
import { DEFAULT_PORTFOLIO_HOLDINGS } from '../domain/portfolio/portfolio.js';
import { DEFAULT_REAL_ESTATE_DETAIL } from '../domain/real-estate/markets.js';

export const DEFAULT_APP_STATE = {
  profile: DEFAULT_USER_PROFILE,
  financialSnapshot: DEFAULT_FINANCIAL_SNAPSHOT,
  goals: DEFAULT_GOALS,
  scenario: {
    ...DEFAULT_SCENARIO,
    name: 'New commitment',
    expenseChangePct: 8,
    oneTimeCost: 3500,
    horizonMonths: 18,
  },
  marketAsset: DEFAULT_MARKET_ASSET_DETAIL,
  portfolioHoldings: DEFAULT_PORTFOLIO_HOLDINGS,
  realEstateAsset: DEFAULT_REAL_ESTATE_DETAIL,
  decisionQuestion: 'Should I move forward with this new commitment?',
  decisionLog: [],
  memory: [],
};

export function cloneDefaultState() {
  return structuredClone(DEFAULT_APP_STATE);
}

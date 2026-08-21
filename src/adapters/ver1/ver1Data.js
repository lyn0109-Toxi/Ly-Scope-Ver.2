import { getVer1InventorySummary, VER1_REFERENCE_ROOT } from './ver1Manifest.js';
import { buildLifeBoardContext } from '../../domain/life-board/lifeContext.js';
import { buildPortfolioSnapshot } from '../../domain/portfolio/portfolio.js';

export const VER1_DATA_PATHS = {
  stocks: `${VER1_REFERENCE_ROOT}/data/stock_universe.json`,
  reits: `${VER1_REFERENCE_ROOT}/data/reit_universe.json`,
  realEstateMarkets: `${VER1_REFERENCE_ROOT}/data/real_estate_markets.json`,
  stateCoverage: `${VER1_REFERENCE_ROOT}/data/state_coverage.json`,
  portfolioHoldings: `${VER1_REFERENCE_ROOT}/data/portfolio_holdings.json`,
};

async function fetchJson(path, fallback) {
  const response = await fetch(path);
  if (!response.ok) {
    if (fallback !== undefined) return fallback;
    throw new Error(`Unable to load ${path}: ${response.status}`);
  }
  const payload = await response.json();
  return payload ?? fallback;
}

export async function loadVer1DataBundle() {
  const [stocks, reits, realEstateMarkets, stateCoverage, portfolioHoldings] =
    await Promise.all([
      fetchJson(VER1_DATA_PATHS.stocks, []),
      fetchJson(VER1_DATA_PATHS.reits, []),
      fetchJson(VER1_DATA_PATHS.realEstateMarkets, []),
      fetchJson(VER1_DATA_PATHS.stateCoverage, []),
      fetchJson(VER1_DATA_PATHS.portfolioHoldings, {}),
    ]);

  return {
    stocks,
    reits,
    realEstateMarkets,
    stateCoverage,
    portfolioHoldings,
  };
}

export function createVer1DataSummary(bundle, pipeline) {
  if (!bundle) {
    return {
      inventory: getVer1InventorySummary(),
      status: 'empty',
    };
  }

  const lifeBoard = buildLifeBoardContext({
    stocks: bundle.stocks,
    reits: bundle.reits,
    markets: bundle.realEstateMarkets,
    foundation: pipeline.foundation,
    goalsEvaluation: pipeline.goalsEvaluation,
  });
  const portfolio = buildPortfolioSnapshot({
    holdings: bundle.portfolioHoldings,
    stocks: bundle.stocks,
  });

  return {
    status: 'ready',
    inventory: getVer1InventorySummary(),
    counts: {
      stocks: bundle.stocks.length,
      reits: bundle.reits.length,
      realEstateMarkets: bundle.realEstateMarkets.length,
      states: bundle.stateCoverage.length,
      portfolioHoldings: Object.keys(bundle.portfolioHoldings || {}).length,
    },
    lifeBoard,
    portfolio,
  };
}

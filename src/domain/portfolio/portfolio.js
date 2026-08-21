import { enrichStock, enrichStocks } from '../market-assets/stocks.js';

export const DEFAULT_PORTFOLIO_HOLDINGS = {
  MSFT: {
    shares: 60,
    purchase_price: 390,
    company: 'Microsoft',
    sector: 'Technology',
    price: 426.7,
    pe: 32.2,
    dividend_yield: 0.7,
    beta: 0.9,
    momentum_6m: 13.1,
    revenue_growth: 12.0,
    margin_quality: 90,
    debt_risk: 24,
  },
  AAPL: {
    shares: 70,
    purchase_price: 175,
    company: 'Apple',
    sector: 'Technology',
    price: 189.9,
    pe: 28.4,
    dividend_yield: 0.5,
    beta: 1.2,
    momentum_6m: 9.5,
    revenue_growth: 4.1,
    margin_quality: 86,
    debt_risk: 34,
  },
  NVDA: {
    shares: 80,
    purchase_price: 92,
    company: 'NVIDIA',
    sector: 'Semiconductors',
    price: 109.6,
    pe: 45.5,
    dividend_yield: 0,
    beta: 1.7,
    momentum_6m: 31.8,
    revenue_growth: 29,
    margin_quality: 93,
    debt_risk: 28,
  },
  JPM: {
    shares: 22,
    purchase_price: 188,
    company: 'JPMorgan Chase',
    sector: 'Financials',
    price: 208.4,
    pe: 12.6,
    dividend_yield: 2.1,
    beta: 1.1,
    momentum_6m: 6.8,
    revenue_growth: 5.4,
    margin_quality: 72,
    debt_risk: 42,
  },
};

const numericHoldingFields = [
  'shares',
  'purchase_price',
  'price',
  'pe',
  'dividend_yield',
  'beta',
  'momentum_6m',
  'revenue_growth',
  'margin_quality',
  'debt_risk',
];

const textHoldingFields = ['company', 'sector', 'thesis'];

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, low = 0, high = 100) {
  return Math.max(low, Math.min(high, Number(value)));
}

export function normalizePortfolioHoldings(holdings = {}) {
  return Object.entries(holdings).reduce((result, [symbol, holding]) => {
    if (!symbol || typeof holding !== 'object' || holding === null) {
      return result;
    }
    const cleanSymbol = String(symbol).trim().toUpperCase();
    if (!cleanSymbol) return result;

    const normalized = {
      symbol: cleanSymbol,
      company: String(holding.company || cleanSymbol),
    };

    numericHoldingFields.forEach((field) => {
      normalized[field] = Math.max(0, toNumber(holding[field]));
    });

    textHoldingFields.forEach((field) => {
      if (holding[field] !== undefined) {
        normalized[field] = String(holding[field] || '').trim();
      }
    });

    normalized.sector = normalized.sector || 'Saved Holding';

    result[cleanSymbol] = normalized;
    return result;
  }, {});
}

export function buildPortfolioSnapshot({ holdings = {}, stocks = [] } = {}) {
  const normalizedHoldings = normalizePortfolioHoldings(holdings);
  const stockSource =
    stocks.length > 0
      ? stocks
      : Object.values(normalizedHoldings).map((holding) => ({
          ...holding,
          symbol: holding.symbol,
        }));
  const enrichedStocks = enrichStocks(stockSource);
  const stockMap = new Map(enrichedStocks.map((stock) => [stock.symbol, stock]));
  const rows = Object.entries(normalizedHoldings).map(([symbol, holding]) => {
    const stock = stockMap.get(symbol) || enrichStock(holding);
    const price = stock?.price || holding.price || holding.purchase_price;
    const marketValue = holding.shares * price;
    const costBasis = holding.shares * holding.purchase_price;
    const gainLoss = marketValue - costBasis;

    return {
      symbol,
      company: stock?.company || holding.company,
      sector: stock?.sector || 'Saved Holding',
      shares: holding.shares,
      price,
      purchase_price: holding.purchase_price,
      market_value: marketValue,
      cost_basis: costBasis,
      gain_loss: gainLoss,
      return_pct: costBasis ? (gainLoss / costBasis) * 100 : 0,
      score: stock?.life_stock_score ?? 50,
      beta: stock?.beta ?? 1,
    };
  });
  const totalValue = rows.reduce((sum, row) => sum + row.market_value, 0);
  const totalCost = rows.reduce((sum, row) => sum + row.cost_basis, 0);

  rows.forEach((row) => {
    row.weight = totalValue ? row.market_value / totalValue : 0;
  });

  const sectorWeights = rows.reduce((weights, row) => {
    weights[row.sector] = (weights[row.sector] || 0) + row.weight;
    return weights;
  }, {});
  const topSector = Object.entries(sectorWeights).sort((a, b) => b[1] - a[1])[0];
  const topWeight = Math.max(0, ...rows.map((row) => row.weight));
  const weightedScore = totalValue
    ? rows.reduce((sum, row) => sum + row.score * row.market_value, 0) /
      totalValue
    : null;
  const weightedBeta = totalValue
    ? rows.reduce((sum, row) => sum + row.beta * row.market_value, 0) /
      totalValue
    : null;
  const topSectorWeight = topSector?.[1] || 0;
  const concentrationScore = clamp(
    100 -
      Math.max(0, topWeight - 0.25) * 150 -
      Math.max(0, topSectorWeight - 0.5) * 100,
  );
  const betaScore = clamp(90 - Math.max(0, (weightedBeta || 1) - 1) * 42);
  const performanceScore = clamp(55 + (totalCost ? ((totalValue - totalCost) / totalCost) * 100 : 0) * 1.2);
  const portfolioScore = Math.round(
    (weightedScore ?? 50) * 0.45 +
      concentrationScore * 0.25 +
      betaScore * 0.15 +
      performanceScore * 0.15,
  );
  const warnings = [];

  if (topWeight > 0.45) warnings.push('Top holding concentration is high.');
  if (topSectorWeight > 0.62) warnings.push('Sector concentration is elevated.');
  if ((weightedBeta || 0) > 1.3) warnings.push('Portfolio beta can amplify volatility.');
  if ((weightedScore || 0) < 55) warnings.push('Weighted holding quality needs review.');
  if (totalCost && totalValue < totalCost * 0.9) {
    warnings.push('Portfolio unrealized loss is greater than 10%.');
  }

  return {
    rows,
    count: rows.length,
    total_value: totalValue,
    total_cost: totalCost,
    gain_loss: totalValue - totalCost,
    return_pct: totalCost ? ((totalValue - totalCost) / totalCost) * 100 : 0,
    top_weight: topWeight,
    top_sector: topSector?.[0] || '',
    top_sector_weight: topSectorWeight,
    weighted_score: weightedScore,
    weighted_beta: weightedBeta,
    concentration_score: concentrationScore,
    beta_score: betaScore,
    performance_score: performanceScore,
    portfolio_score: portfolioScore,
    band: getPortfolioBand(portfolioScore),
    warnings,
  };
}

export function getPortfolioBand(score) {
  if (score >= 80) return 'strong';
  if (score >= 64) return 'stable';
  if (score >= 48) return 'watch';
  return 'fragile';
}

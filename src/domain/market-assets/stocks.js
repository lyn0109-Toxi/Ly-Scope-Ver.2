export const DEFAULT_MARKET_ASSET_DETAIL = {
  symbol: 'MSFT',
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
  thesis: 'Durable enterprise platform with AI and cloud optionality.',
};

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, low = 0, high = 100) {
  return Math.max(low, Math.min(high, Number(value)));
}

export function enrichStock(record = {}) {
  const pe = toNumber(record.pe);
  const dividendYield = toNumber(record.dividend_yield);
  const momentum6m = toNumber(record.momentum_6m);
  const marginQuality = toNumber(record.margin_quality);
  const revenueGrowth = toNumber(record.revenue_growth);
  const debtRisk = toNumber(record.debt_risk);
  const beta = toNumber(record.beta, 1);
  const valueScore = clamp(95 - Math.max(0, pe - 10) * 2 + dividendYield * 2.5);
  const momentumScore = clamp(48 + momentum6m * 2.1);
  const qualityScore = clamp(
    marginQuality * 0.72 + revenueGrowth * 1.2 - debtRisk * 0.18,
  );
  const riskBalanceScore = clamp(
    92 - Math.abs(beta - 1) * 28 - debtRisk * 0.22,
  );
  const lifeStockScore =
    valueScore * 0.25 +
    momentumScore * 0.25 +
    qualityScore * 0.3 +
    riskBalanceScore * 0.2;

  return {
    ...record,
    symbol: String(record.symbol || '').trim().toUpperCase(),
    company: String(record.company || record.symbol || '').trim(),
    price: toNumber(record.price),
    pe,
    dividend_yield: dividendYield,
    beta,
    momentum_6m: momentum6m,
    revenue_growth: revenueGrowth,
    margin_quality: marginQuality,
    debt_risk: debtRisk,
    value_score: valueScore,
    momentum_score: momentumScore,
    quality_score: qualityScore,
    risk_balance_score: riskBalanceScore,
    life_stock_score: lifeStockScore,
  };
}

export function enrichStocks(records = []) {
  return records.map(enrichStock);
}

export function stockWarnings(record = {}) {
  const row = enrichStock(record);
  const warnings = [];

  if (row.pe >= 35) warnings.push('Valuation expectations are high.');
  if (row.beta >= 1.45) warnings.push('High beta can amplify drawdowns.');
  if (row.momentum_6m < 0) warnings.push('Price momentum is negative.');
  if (row.debt_risk >= 55) warnings.push('Debt risk needs review.');

  return warnings;
}

export function findStock(records = [], query = '') {
  const clean = String(query).trim().toUpperCase();
  if (!clean) return null;
  const enriched = enrichStocks(records);

  return (
    enriched.find((item) => item.symbol === clean) ||
    enriched.find((item) => item.company.toUpperCase().includes(clean)) ||
    null
  );
}

export function summarizeStocks(records = []) {
  const enriched = enrichStocks(records);
  const scores = enriched.map((item) => item.life_stock_score);
  const averageScore =
    scores.length > 0
      ? scores.reduce((sum, score) => sum + score, 0) / scores.length
      : null;
  const strongest = [...enriched].sort(
    (a, b) => b.life_stock_score - a.life_stock_score,
  )[0];
  const warningCount = enriched.reduce(
    (sum, item) => sum + stockWarnings(item).length,
    0,
  );

  return {
    count: enriched.length,
    averageScore,
    strongest,
    warningCount,
    items: enriched,
  };
}

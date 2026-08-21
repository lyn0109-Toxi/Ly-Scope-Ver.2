function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, low = 0, high = 100) {
  return Math.max(low, Math.min(high, Number(value)));
}

export function enrichReit(record = {}) {
  const navDiscount = toNumber(record.nav_discount);
  const priceToFfo = toNumber(record.price_to_ffo);
  const dividendYield = toNumber(record.dividend_yield);
  const affoPayout = toNumber(record.affo_payout);
  const occupancy = toNumber(record.occupancy);
  const debtToEbitda = toNumber(record.debt_to_ebitda);
  const rentGrowth = toNumber(record.rent_growth);
  const demandScore = toNumber(record.demand_score);
  const rateRisk = toNumber(record.rate_risk);
  const supplyPressure = toNumber(record.supply_pressure);

  const valuationScore = clamp(
    56 +
      Math.max(0, -navDiscount) * 1.2 +
      (18 - priceToFfo) * 2 +
      (dividendYield - 3.5) * 3.2 -
      Math.max(0, affoPayout - 78) * 1.4,
  );
  const incomeScore = clamp(
    45 +
      dividendYield * 6 +
      (82 - affoPayout) * 0.55 +
      (occupancy - 90) * 1.25 -
      Math.max(0, debtToEbitda - 5.5) * 6,
  );
  const propertyScore = clamp(
    occupancy * 0.62 + rentGrowth * 4 + demandScore * 0.24,
  );
  const rateScore = clamp(100 - rateRisk);
  const supplyScore = clamp(100 - supplyPressure);
  const lyReitScore =
    valuationScore * 0.22 +
    incomeScore * 0.26 +
    propertyScore * 0.24 +
    supplyScore * 0.14 +
    rateScore * 0.14;

  return {
    ...record,
    symbol: String(record.symbol || '').trim().toUpperCase(),
    company: String(record.company || record.symbol || '').trim(),
    price: toNumber(record.price),
    dividend_yield: dividendYield,
    price_to_ffo: priceToFfo,
    affo_payout: affoPayout,
    nav_discount: navDiscount,
    debt_to_ebitda: debtToEbitda,
    occupancy,
    rent_growth: rentGrowth,
    demand_score: demandScore,
    supply_pressure: supplyPressure,
    liquidity_score: toNumber(record.liquidity_score),
    rate_risk: rateRisk,
    valuation_score: valuationScore,
    income_score: incomeScore,
    property_score: propertyScore,
    rate_score: rateScore,
    supply_score: supplyScore,
    ly_reit_score: lyReitScore,
  };
}

export function enrichReits(records = []) {
  return records.map(enrichReit);
}

export function reitWarnings(record = {}) {
  const row = enrichReit(record);
  const warnings = [];

  if (row.supply_pressure >= 65) {
    warnings.push('Supply pressure / oversupply risk');
  }
  if (row.price_to_ffo >= 24 || row.nav_discount > 7) {
    warnings.push('Valuation premium needs peer review');
  }
  if (row.liquidity_score < 55) {
    warnings.push('Trading liquidity slowdown');
  }
  if (row.rate_risk >= 65 || row.debt_to_ebitda >= 6.5) {
    warnings.push('Rate and refinancing pressure');
  }
  if (row.affo_payout >= 80) {
    warnings.push('Dividend payout cushion is thin');
  }

  return warnings;
}

export function reitForecast(record = {}) {
  const row = enrichReit(record);
  const basePrice = row.price;
  const qualityPush = (row.demand_score - 55) * 0.1;
  const growthPush =
    toNumber(row.ffo_growth) * 0.55 + toNumber(row.rent_growth) * 0.35;
  const momentumPush = toNumber(row.price_momentum) * 0.28;
  const supplyDrag = Math.max(0, row.supply_pressure - 45) * 0.12;
  const rateDrag = Math.max(0, row.rate_risk - 50) * 0.1;
  const annualMid = clamp(
    growthPush + momentumPush + qualityPush - supplyDrag - rateDrag,
    -10,
    14,
  );
  const uncertainty = clamp(
    5 + row.rate_risk * 0.045 + row.supply_pressure * 0.035,
    6,
    14,
  );

  return [1, 2, 4].map((year) => {
    const midReturn = annualMid * year;
    const band = uncertainty * Math.pow(year, 0.55);

    return {
      horizon: `${year}Y`,
      low: basePrice * (1 + (midReturn - band) / 100),
      base: basePrice * (1 + midReturn / 100),
      high: basePrice * (1 + (midReturn + band) / 100),
      midReturnPct: midReturn,
    };
  });
}

export function summarizeReits(records = []) {
  const enriched = enrichReits(records);
  const scores = enriched.map((item) => item.ly_reit_score);
  const averageScore =
    scores.length > 0
      ? scores.reduce((sum, score) => sum + score, 0) / scores.length
      : null;
  const strongest = [...enriched].sort(
    (a, b) => b.ly_reit_score - a.ly_reit_score,
  )[0];
  const warningCount = enriched.reduce(
    (sum, item) => sum + reitWarnings(item).length,
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

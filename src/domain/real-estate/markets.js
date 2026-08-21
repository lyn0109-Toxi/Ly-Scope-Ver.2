export const DEFAULT_REAL_ESTATE_DETAIL = {
  market_id: 'CLT-28202',
  city: 'Charlotte',
  county: 'Mecklenburg County',
  state: 'NC',
  zip_code: '28202',
  market_type: 'Banking / migration growth',
  median_price: 421000,
  price_momentum_12m: 3.4,
  pir: 4.9,
  affordability_index: 86,
  inventory_months: 3.5,
  active_inventory_yoy: 15,
  rent_estimate: 2290,
  gross_rent_yield: 6.5,
  permits_per_1k: 4.8,
  employment_growth: 2.4,
  migration_score: 81,
  disaster_risk: 38,
  insurance_pressure: 35,
  market_note:
    'Strong demand, decent affordability, and manageable risk make this a high-quality MVP sample.',
};

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, low = 0, high = 100) {
  return Math.max(low, Math.min(high, Number(value)));
}

export function enrichRealEstateMarket(record = {}) {
  const priceMomentum12m = toNumber(record.price_momentum_12m);
  const pir = toNumber(record.pir);
  const affordabilityIndex = toNumber(record.affordability_index);
  const inventoryMonths = toNumber(record.inventory_months);
  const activeInventoryYoy = toNumber(record.active_inventory_yoy);
  const grossRentYield = toNumber(record.gross_rent_yield);
  const insurancePressure = toNumber(record.insurance_pressure);
  const permitsPer1k = toNumber(record.permits_per_1k);
  const employmentGrowth = toNumber(record.employment_growth);
  const migrationScore = toNumber(record.migration_score);
  const disasterRisk = toNumber(record.disaster_risk);

  const priceMomentumScore = clamp(
    58 + priceMomentum12m * 4 - Math.max(0, priceMomentum12m - 7) * 5.5,
  );
  const affordabilityScore = clamp(
    100 - Math.max(0, pir - 3.8) * 8 + (affordabilityIndex - 75) * 0.45,
  );
  const inventoryScore = clamp(
    88 -
      Math.abs(inventoryMonths - 4) * 6 -
      Math.max(0, activeInventoryYoy - 35) * 0.6,
  );
  const rentalScore = clamp(
    42 + grossRentYield * 5 - Math.max(0, insurancePressure - 45) * 0.35,
  );
  const supplyScore = clamp(96 - Math.max(0, permitsPer1k - 2) * 3.7);
  const employmentScore = clamp(
    55 + employmentGrowth * 7 + (migrationScore - 50) * 0.45,
  );
  const hazardScore = clamp(
    100 - disasterRisk * 0.55 - insurancePressure * 0.42,
  );
  const lyMarketScore =
    priceMomentumScore * 0.15 +
    affordabilityScore * 0.18 +
    inventoryScore * 0.14 +
    rentalScore * 0.18 +
    supplyScore * 0.12 +
    employmentScore * 0.15 +
    hazardScore * 0.08;

  return {
    ...record,
    market_id: String(record.market_id || '').trim(),
    city: String(record.city || '').trim(),
    state: String(record.state || '').trim().toUpperCase(),
    median_price: toNumber(record.median_price),
    price_momentum_12m: priceMomentum12m,
    pir,
    affordability_index: affordabilityIndex,
    inventory_months: inventoryMonths,
    active_inventory_yoy: activeInventoryYoy,
    gross_rent_yield: grossRentYield,
    permits_per_1k: permitsPer1k,
    employment_growth: employmentGrowth,
    migration_score: migrationScore,
    disaster_risk: disasterRisk,
    insurance_pressure: insurancePressure,
    price_momentum_score: priceMomentumScore,
    affordability_score: affordabilityScore,
    inventory_score: inventoryScore,
    rental_score: rentalScore,
    supply_score: supplyScore,
    employment_score: employmentScore,
    hazard_score: hazardScore,
    ly_market_score: lyMarketScore,
  };
}

export function enrichRealEstateMarkets(records = []) {
  return records.map(enrichRealEstateMarket);
}

export function realEstateWarnings(record = {}) {
  const row = enrichRealEstateMarket(record);
  const warnings = [];

  if (row.supply_score < 45) warnings.push('Supply pressure is elevated.');
  if (row.affordability_score < 45) {
    warnings.push('Income-relative housing cost is stretched.');
  }
  if (row.hazard_score < 50) {
    warnings.push('Hazard or insurance pressure needs review.');
  }
  if (row.inventory_score < 50) {
    warnings.push('Inventory / liquidity is weakening.');
  }

  return warnings;
}

export function realEstateForecast(record = {}) {
  const row = enrichRealEstateMarket(record);
  const basePrice = row.median_price;
  const annualMid = clamp(
    row.price_momentum_12m * 0.42 +
      (row.employment_score - 60) * 0.04 -
      Math.max(0, 65 - row.affordability_score) * 0.045 -
      Math.max(0, 70 - row.supply_score) * 0.035 +
      (row.rental_score - 60) * 0.035 -
      Math.max(0, 60 - row.hazard_score) * 0.045,
    -7.5,
    9.5,
  );
  const uncertainty = clamp(
    5.5 + (100 - row.inventory_score) * 0.045 + (100 - row.hazard_score) * 0.045,
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

export function mortgagePayment(principal, annualRatePct, years) {
  const loanPrincipal = toNumber(principal);
  const monthlyRate = toNumber(annualRatePct) / 100 / 12;
  const months = toNumber(years) * 12;

  if (loanPrincipal <= 0) return 0;
  if (months <= 0) return loanPrincipal;
  if (monthlyRate <= 0) return loanPrincipal / months;

  return (
    (loanPrincipal * monthlyRate * Math.pow(1 + monthlyRate, months)) /
    (Math.pow(1 + monthlyRate, months) - 1)
  );
}

export function propertyCalculatorResult({
  purchasePrice,
  monthlyRent,
  downPaymentPct,
  mortgageRatePct,
  loanYears,
  propertyTaxPct,
  insuranceMonthly,
  hoaMonthly,
  maintenancePct,
  vacancyPct,
}) {
  const price = toNumber(purchasePrice);
  const rent = toNumber(monthlyRent);
  const downPayment = (price * toNumber(downPaymentPct)) / 100;
  const loanAmount = Math.max(0, price - downPayment);
  const debtService = mortgagePayment(loanAmount, mortgageRatePct, loanYears);
  const monthlyTax = (price * toNumber(propertyTaxPct)) / 100 / 12;
  const monthlyMaintenance = (price * toNumber(maintenancePct)) / 100 / 12;
  const monthlyVacancy = (rent * toNumber(vacancyPct)) / 100;
  const monthlyNoi =
    rent -
    monthlyTax -
    toNumber(insuranceMonthly) -
    toNumber(hoaMonthly) -
    monthlyMaintenance -
    monthlyVacancy;
  const monthlyCashFlow = monthlyNoi - debtService;
  const cashInvested = downPayment + price * 0.03;
  const capRate = price ? (monthlyNoi * 12 * 100) / price : 0;
  const cashOnCash = cashInvested
    ? (monthlyCashFlow * 12 * 100) / cashInvested
    : 0;
  const fixedBeforeVacancy =
    debtService +
    monthlyTax +
    toNumber(insuranceMonthly) +
    toNumber(hoaMonthly) +
    monthlyMaintenance;
  const breakEvenRent =
    fixedBeforeVacancy / Math.max(0.01, 1 - toNumber(vacancyPct) / 100);

  return {
    monthly_cash_flow: monthlyCashFlow,
    monthly_noi: monthlyNoi,
    cap_rate: capRate,
    cash_on_cash: cashOnCash,
    break_even_rent: breakEvenRent,
    cash_invested: cashInvested,
  };
}

export function summarizeRealEstateMarkets(records = []) {
  const enriched = enrichRealEstateMarkets(records);
  const scores = enriched.map((item) => item.ly_market_score);
  const averageScore =
    scores.length > 0
      ? scores.reduce((sum, score) => sum + score, 0) / scores.length
      : null;
  const strongest = [...enriched].sort(
    (a, b) => b.ly_market_score - a.ly_market_score,
  )[0];
  const warningCount = enriched.reduce(
    (sum, item) => sum + realEstateWarnings(item).length,
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

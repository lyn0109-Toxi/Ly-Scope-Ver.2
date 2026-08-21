export const DEFAULT_FINANCIAL_SNAPSHOT = {
  monthlyIncome: 6500,
  monthlyFixedExpense: 3400,
  monthlyVariableExpense: 1200,
  debtMinimumPayment: 350,
  cash: 24000,
  investments: 52000,
  debt: 9000,
  emergencyFundTargetMonths: 6,
};

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function normalizeFinancialSnapshot(snapshot = {}) {
  const merged = {
    ...DEFAULT_FINANCIAL_SNAPSHOT,
    ...snapshot,
  };

  return {
    monthlyIncome: Math.max(0, toNumber(merged.monthlyIncome)),
    monthlyFixedExpense: Math.max(0, toNumber(merged.monthlyFixedExpense)),
    monthlyVariableExpense: Math.max(0, toNumber(merged.monthlyVariableExpense)),
    debtMinimumPayment: Math.max(0, toNumber(merged.debtMinimumPayment)),
    cash: Math.max(0, toNumber(merged.cash)),
    investments: Math.max(0, toNumber(merged.investments)),
    debt: Math.max(0, toNumber(merged.debt)),
    emergencyFundTargetMonths: clamp(
      toNumber(merged.emergencyFundTargetMonths, 6),
      1,
      24,
    ),
  };
}

export function calculateFoundation(snapshot = {}) {
  const normalized = normalizeFinancialSnapshot(snapshot);
  const monthlyExpenses =
    normalized.monthlyFixedExpense +
    normalized.monthlyVariableExpense +
    normalized.debtMinimumPayment;
  const netMonthlyCashFlow = normalized.monthlyIncome - monthlyExpenses;
  const savingsRate =
    normalized.monthlyIncome > 0
      ? netMonthlyCashFlow / normalized.monthlyIncome
      : 0;
  const liquidRunwayMonths =
    monthlyExpenses > 0 ? normalized.cash / monthlyExpenses : 24;
  const emergencyFundTarget =
    monthlyExpenses * normalized.emergencyFundTargetMonths;
  const emergencyFundGap = Math.max(0, emergencyFundTarget - normalized.cash);
  const netWorth =
    normalized.cash + normalized.investments - normalized.debt;
  const annualIncome = normalized.monthlyIncome * 12;
  const debtToIncome = annualIncome > 0 ? normalized.debt / annualIncome : 1;

  const emergencyScore = clamp(
    liquidRunwayMonths / normalized.emergencyFundTargetMonths,
    0,
    1,
  );
  const cashFlowScore = clamp((savingsRate + 0.1) / 0.35, 0, 1);
  const debtScore = clamp(1 - debtToIncome, 0, 1);
  const netWorthScore = netWorth > 0 ? 1 : 0.35;
  const healthScore = Math.round(
    (emergencyScore * 0.35 +
      cashFlowScore * 0.3 +
      debtScore * 0.2 +
      netWorthScore * 0.15) *
      100,
  );

  return {
    snapshot: normalized,
    monthlyExpenses,
    netMonthlyCashFlow,
    savingsRate,
    liquidRunwayMonths,
    emergencyFundTarget,
    emergencyFundGap,
    netWorth,
    debtToIncome,
    healthScore,
    band: getFoundationBand(healthScore),
  };
}

export function getFoundationBand(score) {
  if (score >= 80) return 'strong';
  if (score >= 62) return 'stable';
  if (score >= 45) return 'watch';
  return 'fragile';
}

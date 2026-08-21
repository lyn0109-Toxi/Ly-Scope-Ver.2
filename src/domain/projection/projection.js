import { calculateFoundation } from '../financial-foundation/foundation.js';

function clampMonthCount(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return 12;
  return Math.min(60, Math.max(1, Math.round(number)));
}

export function buildProjection(snapshot, horizonMonths = 12) {
  const foundation = calculateFoundation(snapshot);
  const months = clampMonthCount(horizonMonths);
  const monthlyInvestmentGrowth = 0.0025;
  const monthlyDebtPaydown = foundation.snapshot.debtMinimumPayment;

  return Array.from({ length: months + 1 }, (_, month) => {
    const cash = foundation.snapshot.cash + foundation.netMonthlyCashFlow * month;
    const investments =
      foundation.snapshot.investments *
      Math.pow(1 + monthlyInvestmentGrowth, month);
    const debt = Math.max(
      0,
      foundation.snapshot.debt - monthlyDebtPaydown * month,
    );

    return {
      month,
      cash,
      investments,
      debt,
      netWorth: cash + investments - debt,
    };
  });
}

export function summarizeProjection(points) {
  const finalPoint = points[points.length - 1];
  const minCash = Math.min(...points.map((point) => point.cash));
  const crossesZero = points.find((point) => point.cash < 0);

  return {
    finalCash: finalPoint?.cash ?? 0,
    finalNetWorth: finalPoint?.netWorth ?? 0,
    minCash,
    crossesZeroMonth: crossesZero?.month ?? null,
  };
}

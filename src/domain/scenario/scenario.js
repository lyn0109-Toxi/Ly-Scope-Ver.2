import { calculateFoundation } from '../financial-foundation/foundation.js';
import { buildProjection, summarizeProjection } from '../projection/projection.js';

export const DEFAULT_SCENARIO = {
  name: 'Base Case',
  incomeChangePct: 0,
  expenseChangePct: 0,
  oneTimeCost: 0,
  horizonMonths: 12,
};

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function normalizeScenario(scenario = {}) {
  return {
    ...DEFAULT_SCENARIO,
    ...scenario,
    name: String(scenario.name || DEFAULT_SCENARIO.name).trim(),
    incomeChangePct: clamp(toNumber(scenario.incomeChangePct), -100, 200),
    expenseChangePct: clamp(toNumber(scenario.expenseChangePct), -100, 300),
    oneTimeCost: Math.max(0, toNumber(scenario.oneTimeCost)),
    horizonMonths: clamp(Math.round(toNumber(scenario.horizonMonths, 12)), 1, 60),
  };
}

export function applyScenarioToSnapshot(snapshot, scenario) {
  const normalizedScenario = normalizeScenario(scenario);
  const incomeMultiplier = 1 + normalizedScenario.incomeChangePct / 100;
  const expenseMultiplier = 1 + normalizedScenario.expenseChangePct / 100;

  return {
    ...snapshot,
    monthlyIncome: snapshot.monthlyIncome * incomeMultiplier,
    monthlyFixedExpense: snapshot.monthlyFixedExpense * expenseMultiplier,
    monthlyVariableExpense: snapshot.monthlyVariableExpense * expenseMultiplier,
    cash: Math.max(0, snapshot.cash - normalizedScenario.oneTimeCost),
  };
}

export function compareScenario(baseSnapshot, scenario) {
  const normalizedScenario = normalizeScenario(scenario);
  const scenarioSnapshot = applyScenarioToSnapshot(baseSnapshot, normalizedScenario);
  const baseFoundation = calculateFoundation(baseSnapshot);
  const scenarioFoundation = calculateFoundation(scenarioSnapshot);
  const baseProjection = buildProjection(
    baseSnapshot,
    normalizedScenario.horizonMonths,
  );
  const scenarioProjection = buildProjection(
    scenarioSnapshot,
    normalizedScenario.horizonMonths,
  );

  return {
    scenario: normalizedScenario,
    baseFoundation,
    scenarioFoundation,
    baseProjection,
    scenarioProjection,
    baseSummary: summarizeProjection(baseProjection),
    scenarioSummary: summarizeProjection(scenarioProjection),
    deltas: {
      monthlyCashFlow:
        scenarioFoundation.netMonthlyCashFlow - baseFoundation.netMonthlyCashFlow,
      healthScore: scenarioFoundation.healthScore - baseFoundation.healthScore,
      finalCash:
        summarizeProjection(scenarioProjection).finalCash -
        summarizeProjection(baseProjection).finalCash,
    },
  };
}

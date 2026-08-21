function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function evaluateRiskResilience({
  foundation,
  goalsEvaluation,
  scenarioComparison,
}) {
  const risks = [];
  const buffers = [];

  if (foundation.netMonthlyCashFlow < 0) {
    risks.push({
      id: 'negative-cash-flow',
      severity: 'high',
      label: 'Negative monthly cash flow',
      impact: 20,
    });
  } else {
    buffers.push({
      id: 'positive-cash-flow',
      label: 'Positive monthly cash flow',
      impact: 8,
    });
  }

  if (
    foundation.liquidRunwayMonths < foundation.snapshot.emergencyFundTargetMonths
  ) {
    risks.push({
      id: 'runway-gap',
      severity: 'medium',
      label: 'Emergency runway below target',
      impact: 12,
    });
  } else {
    buffers.push({
      id: 'runway-ready',
      label: 'Emergency runway meets target',
      impact: 10,
    });
  }

  if (goalsEvaluation.summary.strainedCount > 0) {
    risks.push({
      id: 'goal-strain',
      severity: 'medium',
      label: 'One or more goals need more monthly funding',
      impact: goalsEvaluation.summary.strainedCount * 8,
    });
  }

  if (scenarioComparison.scenarioSummary.crossesZeroMonth !== null) {
    risks.push({
      id: 'scenario-liquidity-break',
      severity: 'high',
      label: 'Scenario cash balance drops below zero',
      impact: 24,
    });
  }

  if (scenarioComparison.deltas.finalCash > 0) {
    buffers.push({
      id: 'scenario-upside',
      label: 'Scenario improves projected cash',
      impact: 6,
    });
  }

  const riskPenalty = risks.reduce((sum, risk) => sum + risk.impact, 0);
  const bufferBoost = buffers.reduce((sum, buffer) => sum + buffer.impact, 0);
  const resilienceScore = Math.round(
    clamp(foundation.healthScore - riskPenalty + bufferBoost, 0, 100),
  );

  return {
    risks,
    buffers,
    resilienceScore,
    tier: getResilienceTier(resilienceScore),
  };
}

export function getResilienceTier(score) {
  if (score >= 82) return 'resilient';
  if (score >= 64) return 'steady';
  if (score >= 46) return 'sensitive';
  return 'exposed';
}

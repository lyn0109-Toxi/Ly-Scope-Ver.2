import { summarizeEvidence } from '../evidence/evidence.js';

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function buildDecisionModel({
  data,
  foundation,
  goalsEvaluation,
  scenarioComparison,
  risk,
  assetContext,
  evidence,
}) {
  const evidenceSummary = summarizeEvidence(evidence);
  const goalScore = Math.round(
    clamp(100 - goalsEvaluation.summary.strainedCount * 18, 0, 100),
  );
  const scenarioScore = Math.round(
    clamp(60 + scenarioComparison.deltas.healthScore * 2, 0, 100),
  );
  const assetScores = [
    {
      score: assetContext?.portfolio?.portfolio_score,
      weight: 0.5,
    },
    {
      score: assetContext?.realEstate?.detail?.ly_market_score,
      weight: 0.3,
    },
    {
      score: assetContext?.investment?.detail?.life_stock_score,
      weight: 0.2,
    },
  ].filter((item) => Number.isFinite(item.score));
  const assetWeight = assetScores.reduce((sum, item) => sum + item.weight, 0);
  const assetDetailScore =
    assetWeight > 0
      ? Math.round(
          assetScores.reduce(
            (sum, item) => sum + item.score * item.weight,
            0,
          ) / assetWeight,
        )
      : 60;

  const score = Math.round(
    foundation.healthScore * 0.3 +
      goalScore * 0.16 +
      scenarioScore * 0.14 +
      risk.resilienceScore * 0.18 +
      assetDetailScore * 0.1 +
      evidenceSummary.strengthScore * 0.12,
  );

  return {
    question: data.decisionQuestion,
    score,
    recommendation: getRecommendation(score, risk.risks),
    factors: {
      foundation: foundation.healthScore,
      goals: goalScore,
      scenario: scenarioScore,
      resilience: risk.resilienceScore,
      assetDetail: assetDetailScore,
      evidence: evidenceSummary.strengthScore,
    },
    evidenceSummary,
  };
}

export function getRecommendation(score, risks = []) {
  const hasHighRisk = risks.some((risk) => risk.severity === 'high');
  if (score >= 76 && !hasHighRisk) return 'proceed';
  if (score >= 60) return 'proceed-with-guardrails';
  if (score >= 44) return 'defer';
  return 'do-not-proceed';
}

export function getRecommendationLabel(recommendation) {
  const labels = {
    proceed: 'Proceed',
    'proceed-with-guardrails': 'Proceed with guardrails',
    defer: 'Defer',
    'do-not-proceed': 'Do not proceed',
  };

  return labels[recommendation] || 'Review';
}

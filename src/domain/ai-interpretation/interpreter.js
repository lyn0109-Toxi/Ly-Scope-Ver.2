import { getRecommendationLabel } from '../model/decisionModel.js';

function formatEvidenceTitle(item) {
  return `${item.title}: ${item.detail}`;
}

export function interpretDecision({ model, evidence, risk, foundation }) {
  const strongestEvidence = [...evidence]
    .sort((a, b) => Math.abs(b.score) - Math.abs(a.score))
    .slice(0, 3);
  const highRisks = risk.risks.filter((item) => item.severity === 'high');
  const recommendationLabel = getRecommendationLabel(model.recommendation);

  const headline =
    model.recommendation === 'proceed'
      ? 'The decision has enough financial support.'
      : model.recommendation === 'proceed-with-guardrails'
        ? 'The decision can work with clear limits.'
        : model.recommendation === 'defer'
          ? 'The decision needs more buffer before commitment.'
          : 'The decision is not financially supported yet.';

  const nextActions =
    model.recommendation === 'proceed'
      ? ['Set review checkpoints', 'Track actual cash flow after commitment']
      : model.recommendation === 'proceed-with-guardrails'
        ? ['Cap the downside', 'Predefine exit conditions']
        : model.recommendation === 'defer'
          ? ['Improve monthly cash flow', 'Close the highest-priority buffer gap']
          : ['Avoid commitment', 'Rebuild the financial foundation first'];

  return {
    headline,
    recommendationLabel,
    summary: `${recommendationLabel} with a score of ${model.score}/100.`,
    rationale: strongestEvidence.map(formatEvidenceTitle),
    watchpoints:
      highRisks.length > 0
        ? highRisks.map((item) => item.label)
        : risk.risks.slice(0, 2).map((item) => item.label),
    nextActions,
    confidence:
      foundation.healthScore >= 70 && evidence.length >= 4 ? 'medium-high' : 'medium',
  };
}

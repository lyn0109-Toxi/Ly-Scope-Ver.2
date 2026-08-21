export function composeDecisionRecord({ data, model, interpretation, evidence }) {
  return {
    id: `decision-${Date.now()}`,
    createdAt: new Date().toISOString(),
    owner: data.profile.name,
    question: data.decisionQuestion,
    recommendation: model.recommendation,
    score: model.score,
    headline: interpretation.headline,
    evidenceIds: evidence.map((item) => item.id),
    nextActions: interpretation.nextActions,
  };
}

export function mergeDecisionLog(decisionLog = [], record, limit = 25) {
  return [record, ...decisionLog].slice(0, limit);
}

function signal(score) {
  if (score >= 15) return 'supporting';
  if (score <= -15) return 'cautionary';
  return 'neutral';
}

export function buildEvidence({
  foundation,
  goalsEvaluation,
  scenarioComparison,
  risk,
  assetContext,
}) {
  const items = [
    {
      id: 'foundation-health',
      title: 'Foundation health',
      source: 'financial-foundation',
      score: foundation.healthScore - 60,
      value: foundation.healthScore,
      detail: foundation.band,
    },
    {
      id: 'cash-flow',
      title: 'Monthly cash flow',
      source: 'financial-foundation',
      score: foundation.netMonthlyCashFlow >= 0 ? 22 : -28,
      value: foundation.netMonthlyCashFlow,
      detail:
        foundation.netMonthlyCashFlow >= 0
          ? 'cash-positive'
          : 'cash-negative',
    },
    {
      id: 'goal-pressure',
      title: 'Goal funding pressure',
      source: 'goals',
      score: goalsEvaluation.summary.strainedCount > 0 ? -18 : 14,
      value: goalsEvaluation.summary.strainedCount,
      detail:
        goalsEvaluation.summary.strainedCount > 0 ? 'strained' : 'on-track',
    },
    {
      id: 'scenario-impact',
      title: 'Scenario projected cash',
      source: 'scenario',
      score: scenarioComparison.deltas.finalCash >= 0 ? 12 : -18,
      value: scenarioComparison.deltas.finalCash,
      detail:
        scenarioComparison.deltas.finalCash >= 0
          ? 'cash-improves'
          : 'cash-declines',
    },
    {
      id: 'resilience',
      title: 'Risk and resilience',
      source: 'risk-resilience',
      score: risk.resilienceScore - 60,
      value: risk.resilienceScore,
      detail: risk.tier,
    },
  ];

  if (assetContext?.investment?.detail) {
    const investment = assetContext.investment.detail;
    const warningCount = assetContext.investment.warnings.length;
    items.push(
      {
        id: 'investment-score',
        title: 'Selected stock detail',
        source: 'market-assets',
        score: investment.life_stock_score - 60,
        value: investment.life_stock_score,
        detail: investment.symbol || investment.company || 'stock detail',
      },
      {
        id: 'investment-warnings',
        title: 'Investment warnings',
        source: 'market-assets',
        score: warningCount > 0 ? warningCount * -9 : 10,
        value: warningCount,
        detail: warningCount > 0 ? `${warningCount} warning(s)` : 'clear',
      },
    );
  }

  if (assetContext?.portfolio) {
    const portfolio = assetContext.portfolio;
    const warningCount = portfolio.warnings.length;
    items.push(
      {
        id: 'portfolio-score',
        title: 'Portfolio score',
        source: 'portfolio',
        score: portfolio.portfolio_score - 60,
        value: portfolio.portfolio_score,
        detail: `${portfolio.count} holding(s)`,
      },
      {
        id: 'portfolio-concentration',
        title: 'Portfolio concentration',
        source: 'portfolio',
        score:
          portfolio.top_weight > 0.45 || portfolio.top_sector_weight > 0.62
            ? -16
            : 12,
        value: Math.round(portfolio.top_weight * 100),
        detail:
          warningCount > 0
            ? `${warningCount} portfolio warning(s)`
            : 'balanced',
      },
    );
  }

  if (assetContext?.realEstate?.detail) {
    const realEstate = assetContext.realEstate.detail;
    const warningCount = assetContext.realEstate.warnings.length;
    items.push(
      {
        id: 'real-estate-score',
        title: 'Real estate detail',
        source: 'real-estate',
        score: realEstate.ly_market_score - 60,
        value: realEstate.ly_market_score,
        detail:
          realEstate.city && realEstate.state
            ? `${realEstate.city}, ${realEstate.state}`
            : 'market detail',
      },
      {
        id: 'real-estate-warnings',
        title: 'Real estate warnings',
        source: 'real-estate',
        score: warningCount > 0 ? warningCount * -9 : 10,
        value: warningCount,
        detail: warningCount > 0 ? `${warningCount} warning(s)` : 'clear',
      },
    );
  }

  return items.map((item) => ({
    ...item,
    signal: signal(item.score),
  }));
}

export function summarizeEvidence(evidenceItems) {
  const supporting = evidenceItems.filter(
    (item) => item.signal === 'supporting',
  ).length;
  const cautionary = evidenceItems.filter(
    (item) => item.signal === 'cautionary',
  ).length;
  const rawScore = evidenceItems.reduce((sum, item) => sum + item.score, 0);

  return {
    supporting,
    cautionary,
    neutral: evidenceItems.length - supporting - cautionary,
    strengthScore: Math.max(0, Math.min(100, 50 + rawScore)),
  };
}

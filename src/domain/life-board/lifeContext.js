import { stockWarnings, summarizeStocks } from '../market-assets/stocks.js';
import { reitWarnings, summarizeReits } from '../market-assets/reits.js';
import {
  realEstateWarnings,
  summarizeRealEstateMarkets,
} from '../real-estate/markets.js';

function clamp(value, low = 0, high = 100) {
  return Math.max(low, Math.min(high, Number(value)));
}

function scoreOrNull(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function componentWeight(area) {
  return {
    'Market Assets': 0.25,
    'Real Estate': 0.2,
    'Personal Assets': 0.3,
    'Financial Objectives': 0.25,
  }[area] ?? 0;
}

export function buildLifeBoardContext({
  stocks = [],
  reits = [],
  markets = [],
  foundation,
  goalsEvaluation,
} = {}) {
  const stockSummary = summarizeStocks(stocks);
  const reitSummary = summarizeReits(reits);
  const marketSummary = summarizeRealEstateMarkets(markets);
  const marketAssetScores = [
    scoreOrNull(stockSummary.averageScore),
    scoreOrNull(reitSummary.averageScore),
  ].filter((score) => score !== null);
  const marketAssetScore =
    marketAssetScores.length > 0
      ? marketAssetScores.reduce((sum, score) => sum + score, 0) /
        marketAssetScores.length
      : null;
  const realEstateScore = scoreOrNull(marketSummary.averageScore);
  const personalScore = scoreOrNull(foundation?.healthScore);
  const objectiveScore =
    goalsEvaluation?.summary?.averageProgress !== undefined
      ? clamp(goalsEvaluation.summary.averageProgress * 100)
      : null;
  const components = [
    {
      area: 'Market Assets',
      score: marketAssetScore,
      ready: marketAssetScore !== null,
      source: `${stockSummary.count} stock(s), ${reitSummary.count} REIT(s)`,
    },
    {
      area: 'Real Estate',
      score: realEstateScore,
      ready: realEstateScore !== null,
      source: `${marketSummary.count} market sample(s)`,
    },
    {
      area: 'Personal Assets',
      score: personalScore,
      ready: personalScore !== null,
      source: 'Financial Foundation',
    },
    {
      area: 'Financial Objectives',
      score: objectiveScore,
      ready: objectiveScore !== null,
      source: `${goalsEvaluation?.summary?.total ?? 0} goal(s)`,
    },
  ];
  const readyCount = components.filter((item) => item.ready).length;
  const weightedScore = components.reduce(
    (sum, item) =>
      item.score === null
        ? sum
        : sum + item.score * componentWeight(item.area),
    0,
  );
  const scoreWeight = components.reduce(
    (sum, item) => (item.score === null ? sum : sum + componentWeight(item.area)),
    0,
  );
  const rawScore = scoreWeight ? weightedScore / scoreWeight : 0;
  const coverage = components.length ? readyCount / components.length : 0;
  const warnings = [
    ...stockSummary.items.flatMap(stockWarnings),
    ...reitSummary.items.flatMap(reitWarnings),
    ...marketSummary.items.flatMap(realEstateWarnings),
  ];
  const overallScore = clamp(rawScore * (0.7 + coverage * 0.3));

  return {
    overallScore,
    coverage,
    readyCount,
    components,
    warnings: [...new Set(warnings)],
    summaries: {
      stocks: stockSummary,
      reits: reitSummary,
      realEstate: marketSummary,
    },
  };
}

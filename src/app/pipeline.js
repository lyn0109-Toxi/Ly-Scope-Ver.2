import { createPipelineTrace } from '../core/architecture.js';
import { buildDataLayer } from '../domain/data/dataSet.js';
import { calculateFoundation } from '../domain/financial-foundation/foundation.js';
import { evaluateGoals } from '../domain/goals/goals.js';
import { compareScenario } from '../domain/scenario/scenario.js';
import { evaluateRiskResilience } from '../domain/risk-resilience/risk.js';
import { buildEvidence } from '../domain/evidence/evidence.js';
import { enrichStock, stockWarnings } from '../domain/market-assets/stocks.js';
import {
  enrichRealEstateMarket,
  realEstateForecast,
  realEstateWarnings,
} from '../domain/real-estate/markets.js';
import { buildPortfolioSnapshot } from '../domain/portfolio/portfolio.js';
import { buildDecisionModel } from '../domain/model/decisionModel.js';
import { interpretDecision } from '../domain/ai-interpretation/interpreter.js';
import {
  composeDecisionRecord,
  mergeDecisionLog,
} from '../domain/decision/decision.js';
import {
  createMemoryEntry,
  deriveMemoryInsights,
  mergeMemory,
} from '../domain/memory/memory.js';

export function runDecisionPipeline(rawState) {
  const baseData = buildDataLayer(rawState);
  const portfolio = buildPortfolioSnapshot({
    holdings: baseData.portfolioHoldings,
  });
  const data = {
    ...baseData,
    financialSnapshot: {
      ...baseData.financialSnapshot,
      investments:
        portfolio.total_value > 0
          ? portfolio.total_value
          : baseData.financialSnapshot.investments,
    },
  };
  const foundation = calculateFoundation(data.financialSnapshot);
  const goalsEvaluation = evaluateGoals(data.goals, foundation);
  const scenarioComparison = compareScenario(
    data.financialSnapshot,
    data.scenario,
  );
  const investmentDetail = enrichStock(data.marketAsset);
  const realEstateDetail = enrichRealEstateMarket(data.realEstateAsset);
  const assetContext = {
    investment: {
      detail: investmentDetail,
      warnings: stockWarnings(investmentDetail),
    },
    portfolio,
    realEstate: {
      detail: realEstateDetail,
      warnings: realEstateWarnings(realEstateDetail),
      forecast: realEstateForecast(realEstateDetail),
    },
  };
  const risk = evaluateRiskResilience({
    foundation,
    goalsEvaluation,
    scenarioComparison,
  });
  const evidence = buildEvidence({
    foundation,
    goalsEvaluation,
    scenarioComparison,
    risk,
    assetContext,
  });
  const model = buildDecisionModel({
    data,
    foundation,
    goalsEvaluation,
    scenarioComparison,
    risk,
    assetContext,
    evidence,
  });
  const interpretation = interpretDecision({
    model,
    evidence,
    risk,
    foundation,
  });
  const memoryInsights = deriveMemoryInsights(rawState.memory || []);
  const situation = {
    foundation,
    risk,
    scenarioComparison,
    assetContext,
  };
  const decision = {
    recommendation: model.recommendation,
    score: model.score,
    headline: interpretation.headline,
  };

  return {
    customerPurpose: data.profile,
    strategy: goalsEvaluation,
    situation,
    user: data.profile,
    data,
    foundation,
    goalsEvaluation,
    scenarioComparison,
    assetContext,
    risk,
    evidence,
    model,
    interpretation,
    decision,
    memoryInsights,
    trace: createPipelineTrace({
      customerPurpose: data.profile,
      strategy: goalsEvaluation,
      situation,
      data,
      model,
      evidence,
      aiInterpretation: interpretation,
      decision,
      memory: memoryInsights,
    }),
  };
}

export function commitCurrentDecision(rawState, pipelineResult) {
  const record = composeDecisionRecord({
    data: pipelineResult.data,
    model: pipelineResult.model,
    interpretation: pipelineResult.interpretation,
    evidence: pipelineResult.evidence,
  });
  const memoryEntry = createMemoryEntry(record);

  return {
    ...rawState,
    decisionLog: mergeDecisionLog(rawState.decisionLog, record),
    memory: mergeMemory(rawState.memory, memoryEntry),
  };
}

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { calculateFoundation } from '../src/domain/financial-foundation/foundation.js';
import { evaluateGoals } from '../src/domain/goals/goals.js';
import { buildLifeBoardContext } from '../src/domain/life-board/lifeContext.js';
import { enrichReit, reitForecast } from '../src/domain/market-assets/reits.js';
import { enrichStock, stockWarnings } from '../src/domain/market-assets/stocks.js';
import { buildPortfolioSnapshot } from '../src/domain/portfolio/portfolio.js';
import {
  enrichRealEstateMarket,
  realEstateForecast,
  propertyCalculatorResult,
} from '../src/domain/real-estate/markets.js';
import { createVer1DataSummary } from '../src/adapters/ver1/ver1Data.js';
import { runDecisionPipeline } from '../src/app/pipeline.js';
import { cloneDefaultState } from '../src/app/seed.js';

const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '..',
);
const legacyRoot = path.join(projectRoot, 'legacy', 'ver1-reference');

async function pathExists(relativePath) {
  try {
    await stat(path.join(legacyRoot, relativePath));
    return true;
  } catch (error) {
    if (error?.code === 'ENOENT') return false;
    throw error;
  }
}

async function readLegacyJson(relativePath) {
  const raw = await readFile(path.join(legacyRoot, relativePath), 'utf8');
  return JSON.parse(raw);
}

async function readOptionalLegacyJson(relativePath, fallback) {
  try {
    return await readLegacyJson(relativePath);
  } catch (error) {
    if (error?.code === 'ENOENT') return fallback;
    throw error;
  }
}

function roundNumber(value, digits = 6) {
  return Number(value.toFixed(digits));
}

function pickRounded(record, keys) {
  return Object.fromEntries(
    keys.map((key) => [key, roundNumber(record[key])]),
  );
}

const legacySkip = (await pathExists('app.py'))
  ? false
  : 'Local Ver.1 reference is not committed to the public repository.';

test('Ver.1 reference copy is present without Git metadata', { skip: legacySkip }, async () => {
  const appFile = await stat(path.join(legacyRoot, 'app.py'));
  assert.equal(appFile.isFile(), true);

  await assert.rejects(stat(path.join(legacyRoot, '.git')));
});

test('ported stock score matches Ver.1 formula for AAPL sample', { skip: legacySkip }, async () => {
  const stocks = await readLegacyJson('data/stock_universe.json');
  const aapl = enrichStock(stocks.find((stock) => stock.symbol === 'AAPL'));

  assert.equal(Number(aapl.value_score.toFixed(2)), 59.45);
  assert.equal(Number(aapl.momentum_score.toFixed(2)), 67.95);
  assert.equal(Number(aapl.quality_score.toFixed(2)), 60.72);
  assert.equal(Number(aapl.risk_balance_score.toFixed(2)), 78.92);
  assert.equal(Number(aapl.life_stock_score.toFixed(2)), 65.85);
  assert.deepEqual(stockWarnings(aapl), []);
});

test('ported REIT forecast creates Ver.1 horizon bands', { skip: legacySkip }, async () => {
  const reits = await readLegacyJson('data/reit_universe.json');
  const pld = enrichReit(reits.find((reit) => reit.symbol === 'PLD'));
  const forecast = reitForecast(pld);

  assert.deepEqual(
    pickRounded(pld, [
      'valuation_score',
      'income_score',
      'property_score',
      'supply_score',
      'rate_score',
      'ly_reit_score',
    ]),
    {
      valuation_score: 56.4,
      income_score: 80.8,
      property_score: 98.344,
      supply_score: 52,
      rate_score: 42,
      ly_reit_score: 70.17856,
    },
  );
  assert.deepEqual(
    forecast.map((item) => ({
      horizon: item.horizon,
      low: roundNumber(item.low),
      base: roundNumber(item.base),
      high: roundNumber(item.high),
      midReturnPct: roundNumber(item.midReturnPct),
    })),
    [
      {
        horizon: '1Y',
        low: 109.423764,
        base: 119.772824,
        high: 130.121884,
        midReturnPct: 7.516,
      },
      {
        horizon: '2Y',
        low: 112.993737,
        base: 128.145648,
        high: 143.297559,
        midReturnPct: 15.032,
      },
      {
        horizon: '4Y',
        low: 122.7076,
        base: 144.891296,
        high: 167.074992,
        midReturnPct: 30.064,
      },
    ],
  );
});

test('ported real estate and property calculator preserve Ver.1 semantics', { skip: legacySkip }, async () => {
  const markets = await readLegacyJson('data/real_estate_markets.json');
  const charlotte = enrichRealEstateMarket(
    markets.find((market) => market.market_id === 'CLT-28202'),
  );
  const forecast = realEstateForecast(charlotte);
  const property = propertyCalculatorResult({
    purchasePrice: charlotte.median_price,
    monthlyRent: 2290,
    downPaymentPct: 20,
    mortgageRatePct: 6.5,
    loanYears: 30,
    propertyTaxPct: 1.05,
    insuranceMonthly: 180,
    hoaMonthly: 0,
    maintenancePct: 1,
    vacancyPct: 5,
  });

  assert.deepEqual(
    pickRounded(charlotte, [
      'price_momentum_score',
      'affordability_score',
      'inventory_score',
      'rental_score',
      'supply_score',
      'employment_score',
      'hazard_score',
      'ly_market_score',
    ]),
    {
      price_momentum_score: 71.6,
      affordability_score: 96.15,
      inventory_score: 85,
      rental_score: 74.5,
      supply_score: 85.64,
      employment_score: 85.75,
      hazard_score: 64.4,
      ly_market_score: 81.6483,
    },
  );
  assert.deepEqual(
    forecast.map((item) => ({
      horizon: item.horizon,
      low: roundNumber(item.low),
      base: roundNumber(item.base),
      high: roundNumber(item.high),
      midReturnPct: roundNumber(item.midReturnPct),
    })),
    [
      {
        horizon: '1Y',
        low: 400743.585,
        base: 433484.755,
        high: 466225.925,
        midReturnPct: 2.9655,
      },
      {
        horizon: '2Y',
        low: 398033.631334,
        base: 445969.51,
        high: 493905.388666,
        midReturnPct: 5.931,
      },
      {
        horizon: '4Y',
        low: 400756.785723,
        base: 470939.02,
        high: 541121.254277,
        midReturnPct: 11.862,
      },
    ],
  );
  assert.deepEqual(
    pickRounded(property, [
      'monthly_cash_flow',
      'monthly_noi',
      'cap_rate',
      'cash_on_cash',
      'break_even_rent',
      'cash_invested',
    ]),
    {
      monthly_cash_flow: -852.513436,
      monthly_noi: 1276.291667,
      cap_rate: 3.637886,
      cash_on_cash: -10.565074,
      break_even_rent: 3187.382565,
      cash_invested: 96830,
    },
  );
});

test('Ver.1 copied data can feed Ver.2 Life Board summary', { skip: legacySkip }, async () => {
  const [stocks, reits, realEstateMarkets, portfolioHoldings] =
    await Promise.all([
      readLegacyJson('data/stock_universe.json'),
      readLegacyJson('data/reit_universe.json'),
      readLegacyJson('data/real_estate_markets.json'),
      readOptionalLegacyJson('data/portfolio_holdings.json', {}),
    ]);
  const foundation = calculateFoundation();
  const goalsEvaluation = evaluateGoals([], foundation);
  const lifeBoard = buildLifeBoardContext({
    stocks,
    reits,
    markets: realEstateMarkets,
    foundation,
    goalsEvaluation,
  });
  const portfolio = buildPortfolioSnapshot({
    holdings: portfolioHoldings,
    stocks,
  });

  assert.equal(lifeBoard.components.length, 4);
  assert.ok(lifeBoard.overallScore > 0);
  assert.ok(portfolio.count >= 0);
  assert.equal(typeof portfolio.portfolio_score, 'number');
  assert.ok(portfolio.portfolio_score >= 0);
});

test('Ver.1 adapter creates integrated summary for Ver.2 pipeline', { skip: legacySkip }, async () => {
  const [stocks, reits, realEstateMarkets, stateCoverage, portfolioHoldings] =
    await Promise.all([
      readLegacyJson('data/stock_universe.json'),
      readLegacyJson('data/reit_universe.json'),
      readLegacyJson('data/real_estate_markets.json'),
      readLegacyJson('data/state_coverage.json'),
      readOptionalLegacyJson('data/portfolio_holdings.json', {}),
    ]);
  const summary = createVer1DataSummary(
    {
      stocks,
      reits,
      realEstateMarkets,
      stateCoverage,
      portfolioHoldings,
    },
    runDecisionPipeline(cloneDefaultState()),
  );

  assert.equal(summary.status, 'ready');
  assert.equal(summary.counts.stocks, stocks.length);
  assert.equal(summary.counts.reits, reits.length);
  assert.equal(summary.counts.realEstateMarkets, realEstateMarkets.length);
  assert.ok(summary.inventory.moduleCount >= 8);
});

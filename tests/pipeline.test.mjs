import test from 'node:test';
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { getArchitectureMap } from '../src/core/architecture.js';
import { cloneDefaultState } from '../src/app/seed.js';
import {
  commitCurrentDecision,
  runDecisionPipeline,
} from '../src/app/pipeline.js';
import { calculateFoundation } from '../src/domain/financial-foundation/foundation.js';
import { compareScenario } from '../src/domain/scenario/scenario.js';

const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '..',
);

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map((entry) => {
      const fullPath = path.join(directory, entry.name);
      return entry.isDirectory() ? walk(fullPath) : fullPath;
    }),
  );

  return files.flat();
}

test('pipeline materializes the target architecture stages', () => {
  const result = runDecisionPipeline(cloneDefaultState());
  const architecture = getArchitectureMap();

  assert.deepEqual(architecture.flow, [
    'User',
    'Data',
    'Model',
    'Evidence',
    'AI Interpretation',
    'Decision',
    'Memory',
  ]);
  assert.equal(result.trace.length, architecture.flow.length);
  assert.ok(result.trace.every((stage) => stage.status === 'ready'));
  assert.equal(typeof result.model.score, 'number');
});

test('section-level asset details feed the evidence layer', () => {
  const result = runDecisionPipeline(cloneDefaultState());
  const evidenceIds = result.evidence.map((item) => item.id);

  assert.ok(evidenceIds.includes('investment-score'));
  assert.ok(evidenceIds.includes('investment-warnings'));
  assert.ok(evidenceIds.includes('portfolio-score'));
  assert.ok(evidenceIds.includes('portfolio-concentration'));
  assert.ok(evidenceIds.includes('real-estate-score'));
  assert.ok(evidenceIds.includes('real-estate-warnings'));
  assert.equal(result.assetContext.investment.detail.symbol, 'MSFT');
  assert.equal(result.assetContext.portfolio.count, 4);
  assert.equal(
    Math.round(result.foundation.snapshot.investments),
    Math.round(result.assetContext.portfolio.total_value),
  );
  assert.equal(result.assetContext.realEstate.detail.market_id, 'CLT-28202');
  assert.equal(typeof result.model.factors.assetDetail, 'number');
});

test('financial foundation calculates the core Ver.2 baseline', () => {
  const foundation = calculateFoundation({
    monthlyIncome: 5000,
    monthlyFixedExpense: 2000,
    monthlyVariableExpense: 1000,
    debtMinimumPayment: 500,
    cash: 15000,
    investments: 0,
    debt: 6000,
    emergencyFundTargetMonths: 6,
  });

  assert.equal(foundation.monthlyExpenses, 3500);
  assert.equal(foundation.netMonthlyCashFlow, 1500);
  assert.equal(foundation.netWorth, 9000);
  assert.equal(Number(foundation.savingsRate.toFixed(2)), 0.3);
});

test('scenario comparison captures downside assumptions', () => {
  const comparison = compareScenario(
    {
      monthlyIncome: 5000,
      monthlyFixedExpense: 2000,
      monthlyVariableExpense: 1000,
      debtMinimumPayment: 500,
      cash: 15000,
      investments: 0,
      debt: 6000,
      emergencyFundTargetMonths: 6,
    },
    {
      name: 'Expense shock',
      incomeChangePct: 0,
      expenseChangePct: 20,
      oneTimeCost: 2000,
      horizonMonths: 12,
    },
  );

  assert.ok(comparison.deltas.monthlyCashFlow < 0);
  assert.ok(comparison.deltas.finalCash < 0);
});

test('committing a decision writes both decision and memory records', () => {
  const state = cloneDefaultState();
  const result = runDecisionPipeline(state);
  const nextState = commitCurrentDecision(state, result);

  assert.equal(nextState.decisionLog.length, 1);
  assert.equal(nextState.memory.length, 1);
  assert.equal(nextState.memory[0].type, 'decision');
  assert.equal(nextState.memory[0].score, nextState.decisionLog[0].score);
});

test('domain modules do not depend on UI or storage', async () => {
  const domainRoot = path.join(projectRoot, 'src', 'domain');
  const files = (await walk(domainRoot)).filter((file) => file.endsWith('.js'));
  const forbiddenImports = [];

  for (const file of files) {
    const source = await readFile(file, 'utf8');
    if (source.includes('../ui') || source.includes('../storage')) {
      forbiddenImports.push(path.relative(projectRoot, file));
    }
  }

  assert.deepEqual(forbiddenImports, []);
});

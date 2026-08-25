import { commitCurrentDecision, runDecisionPipeline } from './pipeline.js';
import { cloneDefaultState } from './seed.js';
import {
  createVer1DataSummary,
  loadVer1DataBundle,
} from '../adapters/ver1/ver1Data.js';
import { createGoal } from '../domain/goals/goals.js';
import { updateProfile } from '../domain/user/profile.js';
import {
  clearState,
  loadState,
  saveState,
} from '../storage/localRepository.js';
import { renderApp } from '../ui/render.js';

const numericFinancialFields = [
  'monthlyIncome',
  'monthlyFixedExpense',
  'monthlyVariableExpense',
  'debtMinimumPayment',
  'cash',
  'debt',
  'emergencyFundTargetMonths',
];

const numericScenarioFields = [
  'incomeChangePct',
  'expenseChangePct',
  'oneTimeCost',
  'horizonMonths',
];

const numericMarketAssetFields = [
  'price',
  'pe',
  'dividend_yield',
  'beta',
  'momentum_6m',
  'revenue_growth',
  'margin_quality',
  'debt_risk',
];

const numericPortfolioHoldingFields = ['shares', 'purchase_price'];

const numericRealEstateFields = [
  'median_price',
  'price_momentum_12m',
  'pir',
  'affordability_index',
  'inventory_months',
  'active_inventory_yoy',
  'rent_estimate',
  'gross_rent_yield',
  'permits_per_1k',
  'employment_growth',
  'migration_score',
  'disaster_risk',
  'insurance_pressure',
];

function formDataToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function numberPatch(source, keys) {
  return keys.reduce((patch, key) => {
    patch[key] = Number(source[key]);
    return patch;
  }, {});
}

function downloadState(state) {
  const blob = new Blob([JSON.stringify(state, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = 'ly-scope-ver2-state.json';
  link.click();
  URL.revokeObjectURL(url);
}

export function createLyScopeApp(root) {
  if (!root) {
    throw new Error('LY-Scope-Ver.2 root element was not found.');
  }

  let state = loadState(cloneDefaultState());
  let legacy = {
    status: 'loading',
    summary: null,
    error: '',
  };

  function replaceState(nextState) {
    state = nextState;
    saveState(state);
    render();
  }

  function patchState(patch) {
    replaceState({
      ...state,
      ...patch,
    });
  }

  const actions = {
    updateProfile(form) {
      const data = formDataToObject(form);
      patchState({
        profile: updateProfile(state.profile, {
          name: data.name,
          householdType: data.householdType,
          decisionStyle: data.decisionStyle,
          priorities: String(data.priorities || '')
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean),
        }),
      });
    },

    updateFinancialFoundation(form) {
      const data = formDataToObject(form);
      patchState({
        financialSnapshot: {
          ...state.financialSnapshot,
          ...numberPatch(data, numericFinancialFields),
        },
      });
    },

    addGoal(form) {
      const data = formDataToObject(form);
      const nextGoal = createGoal({
        title: data.title,
        targetAmount: Number(data.targetAmount),
        currentAmount: Number(data.currentAmount),
        dueDate: data.dueDate,
        priority: data.priority,
      });

      patchState({
        goals: [...state.goals, nextGoal],
      });
      form.reset();
    },

    removeGoal(goalId) {
      patchState({
        goals: state.goals.filter((goal) => goal.id !== goalId),
      });
    },

    updateScenario(form) {
      const data = formDataToObject(form);
      patchState({
        scenario: {
          ...state.scenario,
          name: data.name,
          ...numberPatch(data, numericScenarioFields),
        },
      });
    },

    loadVer1StockSample(form) {
      const data = formDataToObject(form);
      const symbol = String(data.symbol || '').trim().toUpperCase();
      const sample = legacy.bundle?.stocks?.find(
        (item) => String(item.symbol || '').toUpperCase() === symbol,
      );

      if (!sample) return;
      patchState({
        marketAsset: sample,
      });
    },

    updateMarketAsset(form) {
      const data = formDataToObject(form);
      patchState({
        marketAsset: {
          ...state.marketAsset,
          symbol: String(data.symbol || '').trim().toUpperCase(),
          company: String(data.company || '').trim(),
          sector: String(data.sector || '').trim(),
          thesis: String(data.thesis || '').trim(),
          ...numberPatch(data, numericMarketAssetFields),
        },
      });
    },

    upsertPortfolioHolding(form) {
      const data = formDataToObject(form);
      const symbol = String(data.symbol || '').trim().toUpperCase();
      const sample = legacy.bundle?.stocks?.find(
        (item) => String(item.symbol || '').toUpperCase() === symbol,
      );
      const selectedStock =
        String(state.marketAsset?.symbol || '').toUpperCase() === symbol
          ? state.marketAsset
          : null;
      const sourceStock = sample || selectedStock;
      const existing = state.portfolioHoldings?.[symbol] || {};
      const fallbackPrice =
        sourceStock?.price || existing.price || existing.purchase_price || 0;
      const patch = numberPatch(data, numericPortfolioHoldingFields);

      if (!symbol || patch.shares <= 0) return;

      patch.purchase_price =
        data.purchase_price === '' ? fallbackPrice : patch.purchase_price;

      patchState({
        portfolioHoldings: {
          ...(state.portfolioHoldings || {}),
          [symbol]: {
            ...existing,
            ...(sourceStock || {}),
            symbol,
            company: sourceStock?.company || existing.company || symbol,
            ...patch,
          },
        },
      });
    },

    removePortfolioHolding(symbol) {
      const nextHoldings = {
        ...(state.portfolioHoldings || {}),
      };

      delete nextHoldings[String(symbol || '').trim().toUpperCase()];
      patchState({
        portfolioHoldings: nextHoldings,
      });
    },

    loadVer1RealEstateSample(form) {
      const data = formDataToObject(form);
      const marketId = String(data.market_id || '').trim();
      const sample = legacy.bundle?.realEstateMarkets?.find(
        (item) => String(item.market_id || '') === marketId,
      );

      if (!sample) return;
      patchState({
        realEstateAsset: sample,
      });
    },

    updateRealEstateAsset(form) {
      const data = formDataToObject(form);
      patchState({
        realEstateAsset: {
          ...state.realEstateAsset,
          market_id: String(data.market_id || '').trim(),
          city: String(data.city || '').trim(),
          county: String(data.county || '').trim(),
          state: String(data.state || '').trim().toUpperCase(),
          zip_code: String(data.zip_code || '').trim(),
          market_type: String(data.market_type || '').trim(),
          market_note: String(data.market_note || '').trim(),
          ...numberPatch(data, numericRealEstateFields),
        },
      });
    },

    updateDecisionQuestion(form) {
      const data = formDataToObject(form);
      patchState({
        decisionQuestion: data.decisionQuestion,
      });
    },

    saveDecision() {
      const pipelineResult = runDecisionPipeline(state);
      replaceState(commitCurrentDecision(state, pipelineResult));
    },

    exportState() {
      downloadState(state);
    },

    resetState() {
      const confirmed = window.confirm('Reset LY-Scope-Ver.2 sample data?');
      if (!confirmed) return;
      clearState();
      replaceState(cloneDefaultState());
    },
  };

  function render() {
    const pipeline = runDecisionPipeline(state);
    renderApp(root, {
      state,
      pipeline,
      actions,
      legacy: {
        ...legacy,
        summary:
          legacy.status === 'ready'
            ? createVer1DataSummary(legacy.bundle, pipeline)
            : legacy.summary,
      },
    });
  }

  render();

  loadVer1DataBundle()
    .then((bundle) => {
      legacy = {
        status: 'ready',
        bundle,
        summary: null,
        error: '',
      };
      render();
    })
    .catch((error) => {
      legacy = {
        status: 'error',
        bundle: null,
        summary: null,
        error: error.message || 'Unable to load Ver.1 reference data.',
      };
      render();
    });
}

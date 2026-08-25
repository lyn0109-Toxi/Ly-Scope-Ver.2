import { getRecommendationLabel } from '../domain/model/decisionModel.js';

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 0,
});

const percentFormatter = new Intl.NumberFormat('en-US', {
  style: 'percent',
  maximumFractionDigits: 0,
});

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatCurrency(value) {
  return currencyFormatter.format(Math.round(value || 0));
}

function formatNumber(value) {
  return numberFormatter.format(Math.round(value || 0));
}

function formatPercent(value) {
  return percentFormatter.format(value || 0);
}

function formatMonths(value) {
  if (!Number.isFinite(value)) return '24+ mo';
  return `${value.toFixed(1)} mo`;
}

function bindSubmit(root, selector, handler) {
  const form = root.querySelector(selector);
  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    handler(form);
  });
}

function renderMetric(label, value, detail, tone = 'neutral') {
  return `
    <article class="metric metric-${tone}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(detail)}</small>
    </article>
  `;
}

function renderPipeline(trace) {
  return trace
    .map(
      (stage, index) => `
        <article class="pipeline-step ${stage.status}">
          <span>${String(index + 1).padStart(2, '0')}</span>
          <strong>${escapeHtml(stage.label)}</strong>
          <small>${escapeHtml(stage.module)}</small>
        </article>
      `,
    )
    .join('');
}

function renderArchitectureRail(trace, legacy) {
  const legacyStatus =
    legacy?.status === 'ready'
      ? 'Ver.1 data active'
      : legacy?.status === 'error'
        ? 'Ver.1 reference only'
        : 'Loading Ver.1';
  const targetByStage = {
    customerPurpose: 'stage-customer-purpose',
    strategy: 'stage-strategy',
    situation: 'stage-situation',
    data: 'stage-asset-details',
    model: 'stage-model',
    evidence: 'stage-evidence',
    aiInterpretation: 'stage-aiInterpretation',
    decision: 'stage-decision',
    memory: 'stage-memory',
  };

  return `
    <aside class="architecture-rail" aria-label="Decision architecture">
      <div class="rail-header">
        <span>Core Flow</span>
        <strong>Purpose to Memory</strong>
      </div>
      <nav class="rail-nav">
        ${trace
          .map(
            (stage, index) => `
              <a class="rail-step ${stage.status}" href="#${escapeHtml(
                targetByStage[stage.id] || `stage-${stage.id}`,
              )}">
                <span>${String(index + 1).padStart(2, '0')}</span>
                <div>
                  <strong>${escapeHtml(stage.label)}</strong>
                  <small>${escapeHtml(stage.purpose)}</small>
                </div>
              </a>
            `,
          )
          .join('')}
      </nav>
      <div class="rail-status">
        <span>Reference Base</span>
        <strong>${escapeHtml(legacyStatus)}</strong>
      </div>
    </aside>
  `;
}

function renderCockpitStat(label, value, detail) {
  return `
    <div class="cockpit-stat">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(detail)}</small>
    </div>
  `;
}

function statusTone(score) {
  if (score >= 78) return 'strong';
  if (score >= 62) return 'stable';
  if (score >= 45) return 'watch';
  return 'fragile';
}

function titleCase(value) {
  return String(value || '')
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function getGoalRouteLabel(goalsEvaluation, scenarioComparison) {
  const strainedCount = goalsEvaluation.summary.strainedCount;
  const scenarioCashDelta = scenarioComparison.deltas.finalCash;

  if (strainedCount > 0 && scenarioCashDelta < 0) return 'Re-route';
  if (strainedCount > 0) return 'Needs Lift';
  if (scenarioCashDelta < 0) return 'Protect';
  return 'On Route';
}

function getRiskSignalLabel(risk) {
  if (risk.risks.some((item) => item.severity === 'high')) return 'Crisis';
  if (risk.risks.length > 0) return 'Watch';
  return 'Clear';
}

function renderMiniBar(label, value, tone = 'stable') {
  const safeValue = Math.max(0, Math.min(100, Math.round(value)));
  return `
    <div class="mini-bar mini-bar-${escapeHtml(tone)}">
      <span>${escapeHtml(label)}</span>
      <i aria-hidden="true"><b style="width:${safeValue}%"></b></i>
    </div>
  `;
}

function renderVisualSignalBoard({
  foundation,
  goalsEvaluation,
  scenarioComparison,
  risk,
  model,
}) {
  const goalProgress = Math.round(goalsEvaluation.summary.averageProgress * 100);
  const riskCount = risk.risks.length;
  const scenarioIsPositive = scenarioComparison.deltas.finalCash >= 0;
  const goalRoute = getGoalRouteLabel(goalsEvaluation, scenarioComparison);
  const riskSignal = getRiskSignalLabel(risk);
  const runwayProgress = Math.min(
    100,
    Math.round(
      (foundation.liquidRunwayMonths /
        foundation.snapshot.emergencyFundTargetMonths) *
        100,
    ),
  );
  const cashFlowProgress = Math.max(
    0,
    Math.min(100, Math.round((foundation.savingsRate / 0.25) * 100)),
  );
  const riskLights = Array.from({ length: 5 }, (_, index) => {
    const active = index < Math.min(5, Math.max(1, riskCount || 1));
    const tone = riskCount === 0 ? 'green' : riskCount <= 2 ? 'amber' : 'red';
    return `<span class="${active ? tone : 'off'}"></span>`;
  }).join('');

  return `
    <section class="visual-signal-board" aria-label="Visual decision summary">
      <article class="signal-card reveal-card signal-${statusTone(foundation.healthScore)}" tabindex="0">
        <div class="signal-card-head">
          <span>Now</span>
          <strong>${titleCase(foundation.band)}</strong>
        </div>
        <div class="signal-orbit" style="--value:${foundation.healthScore}">
          <b>${titleCase(foundation.band)}</b>
        </div>
        <div class="signal-bars">
          ${renderMiniBar('Cash', cashFlowProgress, statusTone(foundation.healthScore))}
          ${renderMiniBar('Runway', runwayProgress, statusTone(runwayProgress))}
        </div>
        <p class="reveal-detail">${foundation.healthScore}/100 foundation. ${formatCurrency(foundation.netMonthlyCashFlow)} monthly cash flow and ${formatMonths(foundation.liquidRunwayMonths)} runway define the current capacity.</p>
      </article>

      <article class="signal-card reveal-card signal-${statusTone(goalProgress)}" tabindex="0">
        <div class="signal-card-head">
          <span>Direction</span>
          <strong>${escapeHtml(goalRoute)}</strong>
        </div>
        <div class="goal-path" aria-hidden="true">
          <i style="width:${Math.max(8, Math.min(100, goalProgress))}%"></i>
          <span></span>
        </div>
        <div class="direction-arrow ${scenarioIsPositive ? 'positive' : 'caution'}" aria-hidden="true">
          <span></span>
          <b></b>
        </div>
        <p class="reveal-detail">${goalProgress}% average goal progress. ${goalsEvaluation.summary.strainedCount} strained goal(s). Scenario cash changes by ${formatCurrency(scenarioComparison.deltas.finalCash)}, shaping the route to the goal.</p>
      </article>

      <article class="signal-card reveal-card signal-${riskCount === 0 ? 'strong' : riskCount <= 2 ? 'watch' : 'fragile'}" tabindex="0">
        <div class="signal-card-head">
          <span>Crisis</span>
          <strong>${escapeHtml(riskSignal)}</strong>
        </div>
        <div class="risk-radar" aria-hidden="true">
          ${riskLights}
        </div>
        <div class="resilience-scale" aria-hidden="true">
          <i style="width:${risk.resilienceScore}%"></i>
        </div>
        <p class="reveal-detail">${riskCount === 0 ? 'No major active risk flags.' : `${riskCount} active risk flag(s).`} ${titleCase(risk.tier)} resilience is ${risk.resilienceScore}/100, and the model score is ${model.score}/100.</p>
      </article>
    </section>
  `;
}

function renderDecisionCockpit({
  state,
  foundation,
  goalsEvaluation,
  scenarioComparison,
  risk,
  model,
  interpretation,
}) {
  return `
    <section class="decision-cockpit reveal-card" aria-label="Current decision cockpit" tabindex="0">
      <div class="cockpit-main">
        <div class="cockpit-copy">
          <span class="section-kicker">Current Decision</span>
          <h2>${escapeHtml(state.decisionQuestion)}</h2>
          <p class="reveal-detail">${escapeHtml(interpretation.headline)} ${escapeHtml(interpretation.summary)}</p>
          <div class="cockpit-badges">
            <span>${escapeHtml(getRecommendationLabel(model.recommendation))}</span>
            <span>${escapeHtml(risk.tier)}</span>
            <span>${escapeHtml(interpretation.confidence)} confidence</span>
          </div>
        </div>
        <div class="score-dial" style="--score:${model.score}">
          <strong>${model.score}</strong>
          <span>/100</span>
        </div>
      </div>
      <div class="cockpit-stat-grid reveal-detail">
        ${renderCockpitStat('Foundation', `${foundation.healthScore}/100`, foundation.band)}
        ${renderCockpitStat('Goal Pressure', `${goalsEvaluation.summary.strainedCount}`, 'strained goals')}
        ${renderCockpitStat('Scenario Cash', formatCurrency(scenarioComparison.deltas.finalCash), `${scenarioComparison.scenario.horizonMonths} months`)}
        ${renderCockpitStat('Resilience', `${risk.resilienceScore}/100`, risk.tier)}
      </div>
    </section>
  `;
}

function reasoningTone(condition, fallback = 'neutral') {
  if (condition === true) return 'supporting';
  if (condition === false) return 'cautionary';
  return fallback;
}

function renderReasoningStep(index, label, value, claim, tone) {
  return `
    <article class="reasoning-step reveal-card reasoning-${escapeHtml(tone)}" tabindex="0">
      <span>${String(index).padStart(2, '0')}</span>
      <div>
        <strong>${escapeHtml(label)}</strong>
        <em>${escapeHtml(value)}</em>
        <p class="reveal-detail">${escapeHtml(claim)}</p>
      </div>
    </article>
  `;
}

function renderReasoningChain({
  foundation,
  goalsEvaluation,
  scenarioComparison,
  risk,
  evidence,
  model,
  interpretation,
}) {
  const supporting = model.evidenceSummary.supporting;
  const cautionary = model.evidenceSummary.cautionary;
  const scenarioCashDelta = scenarioComparison.deltas.finalCash;
  const hasHighRisk = risk.risks.some((item) => item.severity === 'high');
  const topEvidence = [...evidence].sort(
    (a, b) => Math.abs(b.score) - Math.abs(a.score),
  )[0];
  const scenarioClaim =
    scenarioCashDelta >= 0
      ? `The scenario adds ${formatCurrency(scenarioCashDelta)} to projected cash, so the decision has upside room.`
      : `The scenario uses ${formatCurrency(Math.abs(scenarioCashDelta))} of projected cash, so guardrails matter.`;
  const decisionClaim =
    model.recommendation === 'proceed'
      ? 'The model can recommend proceeding because support outweighs the current cautions.'
      : model.recommendation === 'proceed-with-guardrails'
        ? 'The model can support action only if limits and review points are defined first.'
        : model.recommendation === 'defer'
          ? 'The model points to waiting because the caution signals need more buffer.'
          : 'The model does not support the decision yet because core capacity is not ready.';

  const steps = [
    {
      label: 'Financial Base',
      value: `${foundation.healthScore}/100`,
      claim:
        foundation.netMonthlyCashFlow >= 0
          ? `${formatCurrency(foundation.netMonthlyCashFlow)} monthly cash flow and ${formatMonths(foundation.liquidRunwayMonths)} runway create decision capacity.`
          : `${formatCurrency(Math.abs(foundation.netMonthlyCashFlow))} monthly cash flow gap weakens decision capacity.`,
      tone: reasoningTone(
        foundation.netMonthlyCashFlow >= 0 && foundation.healthScore >= 62,
      ),
    },
    {
      label: 'Goal Pressure',
      value: `${goalsEvaluation.summary.strainedCount} strained`,
      claim:
        goalsEvaluation.summary.strainedCount === 0
          ? 'Current goals do not require extra funding beyond available monthly capacity.'
          : 'One or more goals need more monthly funding, so the decision competes with priorities.',
      tone: reasoningTone(goalsEvaluation.summary.strainedCount === 0),
    },
    {
      label: 'Scenario Effect',
      value: formatCurrency(scenarioCashDelta),
      claim: scenarioClaim,
      tone: reasoningTone(scenarioCashDelta >= 0),
    },
    {
      label: 'Risk Filter',
      value: `${risk.resilienceScore}/100`,
      claim: hasHighRisk
        ? 'A high-severity risk is present, so the recommendation cannot be read as unconditional.'
        : `${risk.tier} resilience means the current setup can absorb ordinary stress.`,
      tone: hasHighRisk ? 'cautionary' : reasoningTone(risk.resilienceScore >= 64),
    },
    {
      label: 'Evidence Balance',
      value: `${supporting} support / ${cautionary} caution`,
      claim: topEvidence
        ? `${topEvidence.title} is the strongest signal shaping the recommendation.`
        : 'Evidence has not produced a dominant signal yet.',
      tone: supporting >= cautionary ? 'supporting' : 'cautionary',
    },
    {
      label: 'Decision',
      value: getRecommendationLabel(model.recommendation),
      claim: `${decisionClaim} ${interpretation.headline}`,
      tone:
        model.recommendation === 'proceed' ||
        model.recommendation === 'proceed-with-guardrails'
          ? 'supporting'
          : 'cautionary',
    },
  ];

  return `
    <section class="reasoning-chain" aria-label="Decision logic chain">
      <div class="section-heading compact reveal-card" tabindex="0">
        <div>
          <span>Decision Logic</span>
          <h2>Why This Recommendation Follows</h2>
        </div>
        <p class="reveal-detail">The chain makes the decision feel traceable: each signal explains how it pushes the final recommendation.</p>
      </div>
      <div class="reasoning-grid">
        ${steps
          .map((step, index) =>
            renderReasoningStep(
              index + 1,
              step.label,
              step.value,
              step.claim,
              step.tone,
            ),
          )
          .join('')}
      </div>
    </section>
  `;
}

function renderSectionHeading(kicker, title, detail) {
  return `
    <div class="section-heading reveal-card" tabindex="0">
      <div>
        <span>${escapeHtml(kicker)}</span>
        <h2>${escapeHtml(title)}</h2>
      </div>
      <p class="reveal-detail">${escapeHtml(detail)}</p>
    </div>
  `;
}

function renderProfileForm(state) {
  return `
    <form id="profile-form" class="panel-form profile-form">
      <label>
        Name
        <input name="name" value="${escapeHtml(state.profile.name)}" />
      </label>
      <label>
        Household
        <select name="householdType">
          ${option('individual', 'Individual', state.profile.householdType)}
          ${option('family', 'Family', state.profile.householdType)}
          ${option('business', 'Business', state.profile.householdType)}
        </select>
      </label>
      <label>
        Style
        <select name="decisionStyle">
          ${option('balanced', 'Balanced', state.profile.decisionStyle)}
          ${option('conservative', 'Conservative', state.profile.decisionStyle)}
          ${option('growth', 'Growth', state.profile.decisionStyle)}
        </select>
      </label>
      <label class="wide-field">
        Priorities
        <input name="priorities" value="${escapeHtml(
          state.profile.priorities.join(', '),
        )}" />
      </label>
      <button type="submit" class="button primary">Save profile</button>
    </form>
  `;
}

function option(value, label, selectedValue) {
  return `<option value="${escapeHtml(value)}" ${
    value === selectedValue ? 'selected' : ''
  }>${escapeHtml(label)}</option>`;
}

function renderFoundationForm(snapshot) {
  const fields = [
    ['monthlyIncome', 'Monthly income'],
    ['monthlyFixedExpense', 'Fixed expense'],
    ['monthlyVariableExpense', 'Variable expense'],
    ['debtMinimumPayment', 'Debt payment'],
    ['cash', 'Cash'],
    ['debt', 'Debt'],
    ['emergencyFundTargetMonths', 'Runway target'],
  ];

  return `
    <form id="foundation-form" class="panel-form field-grid">
      ${fields
        .map(
          ([name, label]) => `
            <label>
              ${escapeHtml(label)}
              <input
                type="number"
                name="${escapeHtml(name)}"
                min="0"
                step="${name === 'emergencyFundTargetMonths' ? '1' : '100'}"
                value="${escapeHtml(snapshot[name])}"
              />
            </label>
          `,
        )
        .join('')}
      <button type="submit" class="button primary wide-field">Save foundation</button>
    </form>
  `;
}

function renderGoals(goalsEvaluation) {
  return goalsEvaluation.items
    .map((goal) => {
      const progressPercent = Math.round(goal.progressRatio * 100);
      return `
        <li class="goal-row">
          <div>
            <div class="row-title">
              <strong>${escapeHtml(goal.title)}</strong>
              <span class="status-pill status-${escapeHtml(goal.status)}">
                ${escapeHtml(goal.status)}
              </span>
            </div>
            <div class="progress-track" aria-label="${escapeHtml(
              goal.title,
            )} progress">
              <span style="width: ${progressPercent}%"></span>
            </div>
            <small>
              ${formatCurrency(goal.currentAmount)} of ${formatCurrency(
                goal.targetAmount,
              )}
            </small>
          </div>
          <button
            type="button"
            class="icon-button"
            data-remove-goal="${escapeHtml(goal.id)}"
            aria-label="Remove ${escapeHtml(goal.title)}"
            title="Remove goal"
          >
            x
          </button>
        </li>
      `;
    })
    .join('');
}

function renderGoalForm() {
  return `
    <form id="goal-form" class="panel-form field-grid">
      <label class="wide-field">
        Goal
        <input name="title" required placeholder="New goal" />
      </label>
      <label>
        Target
        <input type="number" min="0" step="100" name="targetAmount" required />
      </label>
      <label>
        Current
        <input type="number" min="0" step="100" name="currentAmount" value="0" />
      </label>
      <label>
        Due date
        <input type="date" name="dueDate" />
      </label>
      <label>
        Priority
        <select name="priority">
          <option value="high">High</option>
          <option value="medium" selected>Medium</option>
          <option value="low">Low</option>
        </select>
      </label>
      <button type="submit" class="button secondary wide-field">Add goal</button>
    </form>
  `;
}

function renderScenarioForm(scenario) {
  return `
    <form id="scenario-form" class="panel-form field-grid">
      <label class="wide-field">
        Scenario
        <input name="name" value="${escapeHtml(scenario.name)}" />
      </label>
      <label>
        Income change %
        <input type="number" name="incomeChangePct" step="1" value="${escapeHtml(
          scenario.incomeChangePct,
        )}" />
      </label>
      <label>
        Expense change %
        <input type="number" name="expenseChangePct" step="1" value="${escapeHtml(
          scenario.expenseChangePct,
        )}" />
      </label>
      <label>
        One-time cost
        <input type="number" name="oneTimeCost" min="0" step="100" value="${escapeHtml(
          scenario.oneTimeCost,
        )}" />
      </label>
      <label>
        Horizon months
        <input type="number" name="horizonMonths" min="1" max="60" step="1" value="${escapeHtml(
          scenario.horizonMonths,
        )}" />
      </label>
      <button type="submit" class="button primary wide-field">Save scenario</button>
    </form>
  `;
}

function renderOptions(records, getValue, getLabel, selectedValue) {
  return records
    .map((record) => {
      const value = getValue(record);
      return `<option value="${escapeHtml(value)}" ${
        value === selectedValue ? 'selected' : ''
      }>${escapeHtml(getLabel(record))}</option>`;
    })
    .join('');
}

function renderWarningList(warnings, emptyText) {
  if (!warnings.length) {
    return `<p class="empty-state compact-empty">${escapeHtml(emptyText)}</p>`;
  }

  return `
    <ul class="risk-list detail-warning-list">
      ${warnings
        .map(
          (warning) => `
            <li>
              <span>${escapeHtml(warning)}</span>
              <small>watch</small>
            </li>
          `,
        )
        .join('')}
    </ul>
  `;
}

function renderPortfolioRows(portfolio) {
  if (!portfolio.rows.length) {
    return '<p class="empty-state compact-empty">No holdings saved yet.</p>';
  }

  return `
    <ul class="plain-list portfolio-list">
      ${portfolio.rows
        .map(
          (row) => `
            <li class="portfolio-row">
              <div>
                <strong>${escapeHtml(row.symbol)}</strong>
                <small>${escapeHtml(row.company)} · ${escapeHtml(row.sector)}</small>
              </div>
              <div class="portfolio-row-bars">
                <span style="width:${Math.max(4, Math.round(row.weight * 100))}%"></span>
              </div>
              <div class="portfolio-row-meta">
                <strong>${formatCurrency(row.market_value)}</strong>
                <small>${formatPercent(row.weight)} · score ${formatNumber(row.score)}</small>
              </div>
              <button
                type="button"
                class="icon-button"
                data-remove-holding="${escapeHtml(row.symbol)}"
                aria-label="Remove ${escapeHtml(row.symbol)}"
                title="Remove holding"
              >
                x
              </button>
            </li>
          `,
        )
        .join('')}
    </ul>
  `;
}

function renderPortfolioDetail(state, assetContext, legacy) {
  const portfolio = assetContext.portfolio;
  const samples = legacy?.bundle?.stocks || [];
  const holdingSymbols = Object.keys(state.portfolioHoldings || {});
  const sampleOptions =
    renderOptions(
      samples,
      (item) => String(item.symbol || '').toUpperCase(),
      (item) => `${item.symbol} · ${item.company}`,
      state.marketAsset.symbol,
    ) ||
    holdingSymbols
      .map((symbol) => `<option value="${escapeHtml(symbol)}">${escapeHtml(symbol)}</option>`)
      .join('');

  return `
    <section class="panel detail-panel span-two">
      <div class="panel-heading">
        <h2>Portfolio</h2>
        <span>${portfolio.portfolio_score}/100 · ${escapeHtml(portfolio.band)}</span>
      </div>
      <dl class="compact-stats">
        <div>
          <dt>Total Value</dt>
          <dd>${formatCurrency(portfolio.total_value)}</dd>
        </div>
        <div>
          <dt>Top Holding</dt>
          <dd>${formatPercent(portfolio.top_weight)}</dd>
        </div>
        <div>
          <dt>Beta</dt>
          <dd>${portfolio.weighted_beta ? portfolio.weighted_beta.toFixed(2) : 'n/a'}</dd>
        </div>
      </dl>
      ${renderPortfolioRows(portfolio)}
      ${renderWarningList(portfolio.warnings, 'Portfolio balance has no major concentration warnings.')}
      <form id="portfolio-holding-form" class="sample-loader portfolio-loader">
        <label>
          Stock sample
          <select name="symbol">
            ${sampleOptions || '<option value="MSFT">MSFT</option>'}
          </select>
        </label>
        <label>
          Shares
          <input type="number" min="0" step="0.01" name="shares" value="1" required />
        </label>
        <label>
          Cost / share
          <input type="number" min="0" step="0.01" name="purchase_price" placeholder="sample price" />
        </label>
        <button type="submit" class="button primary">Add / update</button>
      </form>
    </section>
  `;
}

function renderInvestmentDetail(state, assetContext, legacy) {
  const detail = assetContext.investment.detail;
  const samples = legacy?.bundle?.stocks || [];
  const sampleOptions = renderOptions(
    samples,
    (item) => String(item.symbol || '').toUpperCase(),
    (item) => `${item.symbol} · ${item.company}`,
    detail.symbol,
  );

  return `
    <section class="panel detail-panel">
      <div class="panel-heading">
        <h2>Selected Stock Research</h2>
        <span>${Math.round(detail.life_stock_score)}/100</span>
      </div>
      <form id="stock-sample-form" class="sample-loader">
        <label>
          Ver.1 stock sample
          <select name="symbol">
            ${sampleOptions || `<option value="${escapeHtml(detail.symbol)}">${escapeHtml(detail.symbol || 'Manual stock')}</option>`}
          </select>
        </label>
        <button type="submit" class="button secondary">Load sample</button>
      </form>
      <dl class="compact-stats">
        <div>
          <dt>Valuation</dt>
          <dd>${formatNumber(detail.value_score)}</dd>
        </div>
        <div>
          <dt>Momentum</dt>
          <dd>${formatNumber(detail.momentum_score)}</dd>
        </div>
        <div>
          <dt>Risk Balance</dt>
          <dd>${formatNumber(detail.risk_balance_score)}</dd>
        </div>
      </dl>
      ${renderWarningList(assetContext.investment.warnings, 'No major stock warnings from the current inputs.')}
      <form id="market-asset-form" class="panel-form field-grid detail-form">
        <label>
          Symbol
          <input name="symbol" value="${escapeHtml(detail.symbol)}" />
        </label>
        <label>
          Company
          <input name="company" value="${escapeHtml(detail.company)}" />
        </label>
        <label>
          Sector
          <input name="sector" value="${escapeHtml(detail.sector || '')}" />
        </label>
        <label>
          Price
          <input type="number" step="0.1" name="price" value="${escapeHtml(detail.price)}" />
        </label>
        <label>
          P/E
          <input type="number" step="0.1" name="pe" value="${escapeHtml(detail.pe)}" />
        </label>
        <label>
          Dividend %
          <input type="number" step="0.1" name="dividend_yield" value="${escapeHtml(detail.dividend_yield)}" />
        </label>
        <label>
          Beta
          <input type="number" step="0.1" name="beta" value="${escapeHtml(detail.beta)}" />
        </label>
        <label>
          6M Momentum %
          <input type="number" step="0.1" name="momentum_6m" value="${escapeHtml(detail.momentum_6m)}" />
        </label>
        <label>
          Revenue Growth %
          <input type="number" step="0.1" name="revenue_growth" value="${escapeHtml(detail.revenue_growth)}" />
        </label>
        <label>
          Margin Quality
          <input type="number" step="1" name="margin_quality" value="${escapeHtml(detail.margin_quality)}" />
        </label>
        <label>
          Debt Risk
          <input type="number" step="1" name="debt_risk" value="${escapeHtml(detail.debt_risk)}" />
        </label>
        <label class="wide-field">
          Thesis
          <textarea name="thesis" rows="3">${escapeHtml(detail.thesis || '')}</textarea>
        </label>
        <button type="submit" class="button primary wide-field">Save selected stock</button>
      </form>
    </section>
  `;
}

function renderRealEstateDetail(state, assetContext, legacy) {
  const detail = assetContext.realEstate.detail;
  const samples = legacy?.bundle?.realEstateMarkets || [];
  const sampleOptions = renderOptions(
    samples,
    (item) => String(item.market_id || ''),
    (item) => `${item.city}, ${item.state} ${item.zip_code}`,
    detail.market_id,
  );
  const forecast = assetContext.realEstate.forecast || [];

  return `
    <section class="panel detail-panel">
      <div class="panel-heading">
        <h2>Real Estate</h2>
        <span>${Math.round(detail.ly_market_score)}/100</span>
      </div>
      <form id="real-estate-sample-form" class="sample-loader">
        <label>
          Ver.1 real estate sample
          <select name="market_id">
            ${sampleOptions || `<option value="${escapeHtml(detail.market_id)}">${escapeHtml(detail.market_id || 'Manual market')}</option>`}
          </select>
        </label>
        <button type="submit" class="button secondary">Load sample</button>
      </form>
      <dl class="compact-stats">
        <div>
          <dt>Affordability</dt>
          <dd>${formatNumber(detail.affordability_score)}</dd>
        </div>
        <div>
          <dt>Rental Score</dt>
          <dd>${formatNumber(detail.rental_score)}</dd>
        </div>
        <div>
          <dt>Hazard Score</dt>
          <dd>${formatNumber(detail.hazard_score)}</dd>
        </div>
      </dl>
      <div class="forecast-strip">
        ${forecast
          .map(
            (item) => `
              <div>
                <span>${escapeHtml(item.horizon)}</span>
                <strong>${formatCurrency(item.base)}</strong>
                <small>${formatCurrency(item.low)} - ${formatCurrency(item.high)}</small>
              </div>
            `,
          )
          .join('')}
      </div>
      ${renderWarningList(assetContext.realEstate.warnings, 'No major real estate warnings from the current inputs.')}
      <form id="real-estate-form" class="panel-form field-grid detail-form">
        <label>
          Market ID
          <input name="market_id" value="${escapeHtml(detail.market_id)}" />
        </label>
        <label>
          City
          <input name="city" value="${escapeHtml(detail.city)}" />
        </label>
        <label>
          State
          <input name="state" value="${escapeHtml(detail.state)}" />
        </label>
        <label>
          ZIP
          <input name="zip_code" value="${escapeHtml(detail.zip_code)}" />
        </label>
        <label class="wide-field">
          County
          <input name="county" value="${escapeHtml(detail.county || '')}" />
        </label>
        <label class="wide-field">
          Market Type
          <input name="market_type" value="${escapeHtml(detail.market_type || '')}" />
        </label>
        <label>
          Median Price
          <input type="number" step="1000" name="median_price" value="${escapeHtml(detail.median_price)}" />
        </label>
        <label>
          12M Price %
          <input type="number" step="0.1" name="price_momentum_12m" value="${escapeHtml(detail.price_momentum_12m)}" />
        </label>
        <label>
          PIR
          <input type="number" step="0.1" name="pir" value="${escapeHtml(detail.pir)}" />
        </label>
        <label>
          Affordability
          <input type="number" step="1" name="affordability_index" value="${escapeHtml(detail.affordability_index)}" />
        </label>
        <label>
          Inventory Months
          <input type="number" step="0.1" name="inventory_months" value="${escapeHtml(detail.inventory_months)}" />
        </label>
        <label>
          Inventory YoY %
          <input type="number" step="1" name="active_inventory_yoy" value="${escapeHtml(detail.active_inventory_yoy)}" />
        </label>
        <label>
          Rent Estimate
          <input type="number" step="50" name="rent_estimate" value="${escapeHtml(detail.rent_estimate)}" />
        </label>
        <label>
          Rent Yield %
          <input type="number" step="0.1" name="gross_rent_yield" value="${escapeHtml(detail.gross_rent_yield)}" />
        </label>
        <label>
          Permits / 1K
          <input type="number" step="0.1" name="permits_per_1k" value="${escapeHtml(detail.permits_per_1k)}" />
        </label>
        <label>
          Job Growth %
          <input type="number" step="0.1" name="employment_growth" value="${escapeHtml(detail.employment_growth)}" />
        </label>
        <label>
          Migration
          <input type="number" step="1" name="migration_score" value="${escapeHtml(detail.migration_score)}" />
        </label>
        <label>
          Disaster Risk
          <input type="number" step="1" name="disaster_risk" value="${escapeHtml(detail.disaster_risk)}" />
        </label>
        <label>
          Insurance
          <input type="number" step="1" name="insurance_pressure" value="${escapeHtml(detail.insurance_pressure)}" />
        </label>
        <label class="wide-field">
          Market Note
          <textarea name="market_note" rows="3">${escapeHtml(detail.market_note || '')}</textarea>
        </label>
        <button type="submit" class="button primary wide-field">Save real estate detail</button>
      </form>
    </section>
  `;
}

function renderEvidence(evidence) {
  return evidence
    .map(
      (item) => `
        <li class="evidence-row signal-${escapeHtml(item.signal)}">
          <div>
            <strong>${escapeHtml(item.title)}</strong>
            <small>${escapeHtml(item.source)} · ${escapeHtml(item.detail)}</small>
          </div>
          <span>${item.score > 0 ? '+' : ''}${formatNumber(item.score)}</span>
        </li>
      `,
    )
    .join('');
}

function renderDecisionLog(decisionLog) {
  if (!decisionLog.length) {
    return '<p class="empty-state">No saved decisions yet.</p>';
  }

  return decisionLog
    .map(
      (record) => `
        <li class="history-row">
          <div>
            <strong>${escapeHtml(record.question)}</strong>
            <small>${new Date(record.createdAt).toLocaleString()}</small>
          </div>
          <span>${escapeHtml(getRecommendationLabel(record.recommendation))}</span>
        </li>
      `,
    )
    .join('');
}

function renderMemory(memory, insights) {
  if (!memory.length) {
    return '<p class="empty-state">Decision memory is empty.</p>';
  }

  return `
    <div class="memory-summary">
      <span>${formatNumber(insights.decisionCount)} decisions</span>
      <span>Average score ${insights.averageScore ?? 'n/a'}</span>
    </div>
    <ul class="plain-list">
      ${memory
        .slice(0, 6)
        .map(
          (item) => `
            <li class="memory-row">
              <strong>${escapeHtml(item.title)}</strong>
              <small>${escapeHtml(item.note)}</small>
            </li>
          `,
        )
        .join('')}
    </ul>
  `;
}

function renderRiskList(risk) {
  const rows = risk.risks.length > 0 ? risk.risks : risk.buffers;

  return rows
    .map(
      (item) => `
        <li>
          <span>${escapeHtml(item.label)}</span>
          <small>${escapeHtml(item.severity || 'buffer')}</small>
        </li>
      `,
    )
    .join('');
}

function renderVer1Status(legacy) {
  if (!legacy || legacy.status === 'loading') {
    return `
      <section class="panel span-two legacy-panel">
        <div class="panel-heading">
          <h2>Ver.1 Legacy Integration</h2>
          <span>Loading</span>
        </div>
        <p class="empty-state">Reading copied Ver.1 reference data.</p>
      </section>
    `;
  }

  if (legacy.status === 'error') {
    return `
      <section class="panel span-two legacy-panel">
        <div class="panel-heading">
          <h2>Ver.1 Legacy Integration</h2>
          <span>Reference preserved</span>
        </div>
        <p class="empty-state">${escapeHtml(
          legacy.error ||
            'Ver.1 files are preserved in legacy/ver1-reference. Open the app through the local server to load JSON summaries.',
        )}</p>
      </section>
    `;
  }

  const summary = legacy.summary;
  const lifeBoard = summary.lifeBoard;
  const counts = summary.counts;
  const strongestStock = lifeBoard.summaries.stocks.strongest;
  const strongestReit = lifeBoard.summaries.reits.strongest;
  const strongestMarket = lifeBoard.summaries.realEstate.strongest;

  return `
    <section class="panel span-two legacy-panel">
      <div class="panel-heading">
        <h2>Ver.1 Legacy Integration</h2>
        <span>${escapeHtml(summary.inventory.referenceRoot)}</span>
      </div>
      <div class="legacy-summary-grid">
        ${renderMetric('Stocks', String(counts.stocks), strongestStock?.symbol || 'sample data', 'neutral')}
        ${renderMetric('REITs', String(counts.reits), strongestReit?.symbol || 'sample data', 'neutral')}
        ${renderMetric('Real Estate', String(counts.realEstateMarkets), strongestMarket?.city || 'sample data', 'neutral')}
        ${renderMetric('Life Board', `${Math.round(lifeBoard.overallScore)}/100`, `${lifeBoard.readyCount}/4 ready`, 'stable')}
      </div>
      <div class="legacy-grid">
        <div>
          <h3>Ported Ver.1 Logic</h3>
          <ul class="plain-list legacy-list">
            ${summary.inventory.modules
              .map(
                (item) => `
                  <li class="legacy-row">
                    <div>
                      <strong>${escapeHtml(item.path)}</strong>
                      <small>${escapeHtml(item.ver2Target)}</small>
                    </div>
                    <span>${escapeHtml(item.migrationDecision)}</span>
                  </li>
                `,
              )
              .join('')}
          </ul>
        </div>
        <div>
          <h3>Ver.1 Life Board Components</h3>
          <ul class="plain-list legacy-list">
            ${lifeBoard.components
              .map(
                (item) => `
                  <li class="legacy-row">
                    <div>
                      <strong>${escapeHtml(item.area)}</strong>
                      <small>${escapeHtml(item.source)}</small>
                    </div>
                    <span>${item.score === null ? 'N/A' : `${Math.round(item.score)}/100`}</span>
                  </li>
                `,
              )
              .join('')}
          </ul>
          <div class="legacy-callout">
            <strong>Portfolio reference</strong>
            <span>${formatCurrency(summary.portfolio.total_value)} value · ${formatPercent(summary.portfolio.top_weight)} top weight</span>
          </div>
        </div>
      </div>
    </section>
  `;
}

function bindActions(root, actions) {
  bindSubmit(root, '#profile-form', actions.updateProfile);
  bindSubmit(root, '#foundation-form', actions.updateFinancialFoundation);
  bindSubmit(root, '#goal-form', actions.addGoal);
  bindSubmit(root, '#scenario-form', actions.updateScenario);
  bindSubmit(root, '#decision-form', actions.updateDecisionQuestion);
  bindSubmit(root, '#stock-sample-form', actions.loadVer1StockSample);
  bindSubmit(root, '#market-asset-form', actions.updateMarketAsset);
  bindSubmit(root, '#portfolio-holding-form', actions.upsertPortfolioHolding);
  bindSubmit(root, '#real-estate-sample-form', actions.loadVer1RealEstateSample);
  bindSubmit(root, '#real-estate-form', actions.updateRealEstateAsset);

  root.querySelectorAll('[data-remove-goal]').forEach((button) => {
    button.addEventListener('click', () => {
      actions.removeGoal(button.dataset.removeGoal);
    });
  });

  root.querySelectorAll('[data-remove-holding]').forEach((button) => {
    button.addEventListener('click', () => {
      actions.removePortfolioHolding(button.dataset.removeHolding);
    });
  });

  root.querySelector('#save-decision')?.addEventListener('click', () => {
    actions.saveDecision();
  });

  root.querySelector('#export-state')?.addEventListener('click', () => {
    actions.exportState();
  });

  root.querySelector('#reset-state')?.addEventListener('click', () => {
    actions.resetState();
  });

  root.querySelectorAll('.reveal-card').forEach((card) => {
    card.addEventListener('click', () => {
      card.classList.toggle('is-open');
    });
    card.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      card.classList.toggle('is-open');
    });
  });
}

export function renderApp(root, { state, pipeline, actions, legacy }) {
  const {
    foundation,
    goalsEvaluation,
    scenarioComparison,
    assetContext,
    risk,
    evidence,
    model,
    interpretation,
    memoryInsights,
    trace,
  } = pipeline;

  root.innerHTML = `
    <div class="app-shell">
      <header class="app-header">
        <div class="brand-block">
          <span>LY-Scope-Ver.2</span>
          <h1>Decision Intelligence Workspace</h1>
        </div>
        <div class="header-actions">
          <button id="save-decision" type="button" class="button primary">Save decision</button>
          <button id="export-state" type="button" class="button secondary">Export</button>
          <button id="reset-state" type="button" class="button ghost">Reset</button>
        </div>
      </header>

      <main>
        ${renderDecisionCockpit({
          state,
          foundation,
          goalsEvaluation,
          scenarioComparison,
          risk,
          model,
          interpretation,
        })}
        ${renderVisualSignalBoard({
          foundation,
          goalsEvaluation,
          scenarioComparison,
          risk,
          model,
        })}
        ${renderReasoningChain({
          foundation,
          goalsEvaluation,
          scenarioComparison,
          risk,
          evidence,
          model,
          interpretation,
        })}

        <section class="workspace-layout">
          ${renderArchitectureRail(trace, legacy)}

          <div class="workspace-main">
            <section id="stage-decision-inputs" class="workspace-section">
              ${renderSectionHeading('01 Customer Purpose + Strategy + Situation', 'Decision Inputs', 'Profile, financial foundation, and goals create the current decision baseline.')}
              <div class="workspace-grid">
                <section id="stage-customer-purpose" class="panel span-two">
                  <div class="panel-heading">
                    <h2>Customer Purpose</h2>
                    <span>${escapeHtml(state.profile.decisionStyle)}</span>
                  </div>
                  ${renderProfileForm(state)}
                </section>

                <section id="stage-situation" class="panel">
                  <div class="panel-heading">
                    <h2>Situation</h2>
                    <span>${formatCurrency(foundation.netWorth)}</span>
                  </div>
                  <dl class="compact-stats">
                    <div>
                      <dt>Cash flow</dt>
                      <dd>${formatCurrency(foundation.netMonthlyCashFlow)}</dd>
                    </div>
                    <div>
                      <dt>Savings rate</dt>
                      <dd>${formatPercent(foundation.savingsRate)}</dd>
                    </div>
                    <div>
                      <dt>Portfolio value</dt>
                      <dd>${formatCurrency(foundation.snapshot.investments)}</dd>
                    </div>
                  </dl>
                  ${renderFoundationForm(state.financialSnapshot)}
                </section>

                <section id="stage-strategy" class="panel">
                  <div class="panel-heading">
                    <h2>Strategy / Goals</h2>
                    <span>${formatPercent(goalsEvaluation.summary.averageProgress)}</span>
                  </div>
                  <ul class="plain-list goal-list">
                    ${renderGoals(goalsEvaluation)}
                  </ul>
                  ${renderGoalForm()}
                </section>
              </div>
            </section>

            <section id="stage-asset-details" class="workspace-section">
              ${renderSectionHeading('04 Data', 'Portfolio, Stock Research, and Real Estate', 'Portfolio holdings feed Finance, while selected stock and real estate inputs keep section-level assumptions explainable.')}
              <div class="workspace-grid">
                ${renderPortfolioDetail(state, assetContext, legacy)}
                ${renderInvestmentDetail(state, assetContext, legacy)}
                ${renderRealEstateDetail(state, assetContext, legacy)}
              </div>
            </section>

            <section id="stage-model" class="workspace-section">
              ${renderSectionHeading('05 Model', 'Scenario Model', 'Scenario assumptions and resilience checks translate inputs into decision pressure.')}
              <div class="workspace-grid">
                <section class="panel">
                  <div class="panel-heading">
                    <h2>Scenario</h2>
                    <span>${escapeHtml(scenarioComparison.scenario.name)}</span>
                  </div>
                  <dl class="compact-stats">
                    <div>
                      <dt>Cash flow delta</dt>
                      <dd>${formatCurrency(scenarioComparison.deltas.monthlyCashFlow)}</dd>
                    </div>
                    <div>
                      <dt>Health delta</dt>
                      <dd>${scenarioComparison.deltas.healthScore > 0 ? '+' : ''}${formatNumber(scenarioComparison.deltas.healthScore)}</dd>
                    </div>
                    <div>
                      <dt>Final cash</dt>
                      <dd>${formatCurrency(scenarioComparison.scenarioSummary.finalCash)}</dd>
                    </div>
                  </dl>
                  ${renderScenarioForm(state.scenario)}
                </section>

                <section class="panel">
                  <div class="panel-heading">
                    <h2>Risk & Resilience</h2>
                    <span>${risk.resilienceScore}/100</span>
                  </div>
                  <p class="decision-headline">${escapeHtml(risk.tier)}</p>
                  <ul class="risk-list">
                    ${renderRiskList(risk)}
                  </ul>
                </section>
              </div>
            </section>

            <section id="stage-evidence" class="workspace-section">
              ${renderSectionHeading('06 Evidence', 'Decision Evidence', 'Structured signals show why the current recommendation is moving up or down.')}
              <div class="workspace-grid">
                <section class="panel span-two">
                  <div class="panel-heading">
                    <h2>Evidence</h2>
                    <span>${evidence.length} signals</span>
                  </div>
                  <ul class="plain-list evidence-list">
                    ${renderEvidence(evidence)}
                  </ul>
                </section>
              </div>
            </section>

            <section id="stage-aiInterpretation" class="workspace-section">
              ${renderSectionHeading('07 AI Interpretation', 'Decision Reading', 'The interpretation layer turns evidence into a plain-language recommendation.')}
              <div class="workspace-grid">
                <section class="panel decision-panel span-two">
                  <div class="panel-heading">
                    <h2>AI Interpretation</h2>
                    <span>${escapeHtml(interpretation.confidence)}</span>
                  </div>
                  <form id="decision-form" class="panel-form">
                    <label>
                      Decision question
                      <textarea name="decisionQuestion" rows="3">${escapeHtml(
                        state.decisionQuestion,
                      )}</textarea>
                    </label>
                    <button type="submit" class="button primary">Update question</button>
                  </form>
                  <p class="decision-headline">${escapeHtml(interpretation.headline)}</p>
                  <p class="decision-summary">${escapeHtml(interpretation.summary)}</p>
                  <div class="split-list">
                    <div>
                      <h3>Rationale</h3>
                      <ul>
                        ${interpretation.rationale
                          .map((item) => `<li>${escapeHtml(item)}</li>`)
                          .join('')}
                      </ul>
                    </div>
                    <div>
                      <h3>Next Actions</h3>
                      <ul>
                        ${interpretation.nextActions
                          .map((item) => `<li>${escapeHtml(item)}</li>`)
                          .join('')}
                      </ul>
                    </div>
                  </div>
                </section>
              </div>
            </section>

            <section id="stage-decision" class="workspace-section">
              ${renderSectionHeading('08 Decision + 09 Memory', 'Decision Memory', 'Saved decisions become reusable context for the next round of analysis.')}
              <div class="workspace-grid">
                <section class="panel">
                  <div class="panel-heading">
                    <h2>Decision Log</h2>
                    <span>${state.decisionLog.length}</span>
                  </div>
                  <ul class="plain-list history-list">
                    ${renderDecisionLog(state.decisionLog)}
                  </ul>
                </section>

                <section id="stage-memory" class="panel">
                  <div class="panel-heading">
                    <h2>Memory</h2>
                    <span>${memoryInsights.averageScore ?? 'n/a'}</span>
                  </div>
                  ${renderMemory(state.memory, memoryInsights)}
                </section>
              </div>
            </section>

            <section id="stage-legacy" class="workspace-section">
              ${renderSectionHeading('Reference Base', 'Ver.1 Logic', 'Ver.1 source, data, and ported logic stay visible as the reference base for Ver.2.')}
              <div class="workspace-grid">
                ${renderVer1Status(legacy)}
              </div>
            </section>
          </div>
        </section>
      </main>
    </div>
  `;

  bindActions(root, actions);
}

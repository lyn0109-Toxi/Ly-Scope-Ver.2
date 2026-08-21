export const DEFAULT_GOALS = [
  {
    id: 'goal-emergency-fund',
    title: 'Emergency fund',
    targetAmount: 30000,
    currentAmount: 24000,
    dueDate: '2027-08-01',
    priority: 'high',
  },
  {
    id: 'goal-investing-runway',
    title: 'Investment runway',
    targetAmount: 75000,
    currentAmount: 52000,
    dueDate: '2028-01-01',
    priority: 'medium',
  },
];

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function monthsUntil(dateText) {
  if (!dateText) return null;
  const dueDate = new Date(`${dateText}T00:00:00`);
  if (Number.isNaN(dueDate.getTime())) return null;
  const now = new Date();
  const monthDiff =
    (dueDate.getFullYear() - now.getFullYear()) * 12 +
    dueDate.getMonth() -
    now.getMonth();
  return Math.max(0, monthDiff);
}

export function normalizeGoal(goal = {}, index = 0) {
  const title = String(goal.title || `Goal ${index + 1}`).trim();
  const targetAmount = Math.max(0, toNumber(goal.targetAmount));
  const currentAmount = Math.max(0, toNumber(goal.currentAmount));

  return {
    id: goal.id || `goal-${Date.now()}-${index}`,
    title,
    targetAmount,
    currentAmount,
    dueDate: goal.dueDate || '',
    priority: goal.priority || 'medium',
  };
}

export function normalizeGoals(goals = []) {
  const source = Array.isArray(goals) && goals.length > 0 ? goals : DEFAULT_GOALS;
  return source.map(normalizeGoal);
}

export function createGoal(input = {}) {
  return normalizeGoal({
    ...input,
    id: `goal-${Date.now()}`,
  });
}

export function evaluateGoalProgress(goal, foundation) {
  const normalized = normalizeGoal(goal);
  const remaining = Math.max(
    0,
    normalized.targetAmount - normalized.currentAmount,
  );
  const progressRatio =
    normalized.targetAmount > 0
      ? Math.min(1, normalized.currentAmount / normalized.targetAmount)
      : 1;
  const monthsRemaining = monthsUntil(normalized.dueDate);
  const requiredMonthlyContribution =
    monthsRemaining && monthsRemaining > 0
      ? remaining / monthsRemaining
      : remaining;
  const affordable =
    foundation.netMonthlyCashFlow >= requiredMonthlyContribution;

  return {
    ...normalized,
    remaining,
    progressRatio,
    monthsRemaining,
    requiredMonthlyContribution,
    status: remaining === 0 ? 'complete' : affordable ? 'on-track' : 'strained',
  };
}

export function evaluateGoals(goals, foundation) {
  const items = normalizeGoals(goals).map((goal) =>
    evaluateGoalProgress(goal, foundation),
  );
  const strainedCount = items.filter((goal) => goal.status === 'strained').length;
  const averageProgress =
    items.length > 0
      ? items.reduce((sum, goal) => sum + goal.progressRatio, 0) / items.length
      : 1;

  return {
    items,
    summary: {
      total: items.length,
      strainedCount,
      averageProgress,
      requiredMonthlyContribution: items.reduce(
        (sum, goal) => sum + goal.requiredMonthlyContribution,
        0,
      ),
    },
  };
}

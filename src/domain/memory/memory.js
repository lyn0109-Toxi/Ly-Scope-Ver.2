export function createMemoryEntry(decisionRecord) {
  return {
    id: `memory-${decisionRecord.id}`,
    type: 'decision',
    createdAt: decisionRecord.createdAt,
    title: decisionRecord.question,
    signal: decisionRecord.recommendation,
    score: decisionRecord.score,
    note: decisionRecord.headline,
  };
}

export function mergeMemory(memory = [], entry, limit = 50) {
  const withoutDuplicate = memory.filter((item) => item.id !== entry.id);
  return [entry, ...withoutDuplicate].slice(0, limit);
}

export function deriveMemoryInsights(memory = []) {
  const decisions = memory.filter((item) => item.type === 'decision');
  const averageScore =
    decisions.length > 0
      ? Math.round(
          decisions.reduce((sum, item) => sum + item.score, 0) /
            decisions.length,
        )
      : null;
  const recentSignals = decisions.slice(0, 5).map((item) => item.signal);

  return {
    decisionCount: decisions.length,
    averageScore,
    recentSignals,
  };
}

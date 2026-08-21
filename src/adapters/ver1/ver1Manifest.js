export const VER1_REFERENCE_ROOT = 'legacy/ver1-reference';

export const VER1_MODULE_INVENTORY = [
  {
    path: 'app.py',
    type: 'streamlit-shell',
    ver2Target: 'src/app + src/ui',
    migrationDecision: 'reference-only',
    note: 'Main navigation and session wiring are preserved as legacy reference, not reused directly.',
  },
  {
    path: 'ly_scope/analytics.py',
    type: 'domain-logic',
    ver2Target:
      'domain/market-assets, domain/real-estate, domain/financial-foundation',
    migrationDecision: 'ported-core-formulas',
    note: 'Stock, REIT, real estate, finance, mortgage, and property formulas have JS equivalents.',
  },
  {
    path: 'ly_scope/objectives.py',
    type: 'domain-logic',
    ver2Target: 'domain/goals',
    migrationDecision: 'partial-port',
    note: 'Existing Ver.2 goals cover readiness; detailed objective return/tax drag can be added next.',
  },
  {
    path: 'ly_scope/life_context.py',
    type: 'decision-context',
    ver2Target: 'domain/life-board + domain/evidence',
    migrationDecision: 'ported-core-context',
    note: 'Life Board component weighting and warnings are represented in Ver.2.',
  },
  {
    path: 'ly_scope/data_loader.py',
    type: 'data-boundary',
    ver2Target: 'adapters/ver1 + storage',
    migrationDecision: 'ported-data-loader',
    note: 'Ver.2 reads copied Ver.1 JSON samples through a browser-safe adapter.',
  },
  {
    path: 'ly_scope/storage.py',
    type: 'storage-boundary',
    ver2Target: 'storage + memory',
    migrationDecision: 'reference-for-production-adapter',
    note: 'User-scoped local JSON pattern is preserved for future DB migration.',
  },
  {
    path: 'ly_scope/views',
    type: 'streamlit-ui',
    ver2Target: 'src/ui',
    migrationDecision: 'reference-only',
    note: 'Screens are not copied as UI code because Ver.2 is a browser app, but all views are preserved under legacy.',
  },
  {
    path: 'data/*.json',
    type: 'sample-data',
    ver2Target: 'adapters/ver1',
    migrationDecision: 'active-reference-data',
    note: 'Stock, REIT, real estate, state coverage, diary, and portfolio sample data are inside Ver.2.',
  },
];

export function getVer1InventorySummary() {
  const byDecision = VER1_MODULE_INVENTORY.reduce((result, item) => {
    result[item.migrationDecision] = (result[item.migrationDecision] || 0) + 1;
    return result;
  }, {});

  return {
    referenceRoot: VER1_REFERENCE_ROOT,
    moduleCount: VER1_MODULE_INVENTORY.length,
    byDecision,
    modules: VER1_MODULE_INVENTORY,
  };
}

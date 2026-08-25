export const ARCHITECTURE_STAGES = [
  {
    id: 'customerPurpose',
    label: 'Customer Purpose',
    module: 'domain/user',
    purpose: 'desired outcome, priorities, constraints, and decision question',
  },
  {
    id: 'strategy',
    label: 'Strategy',
    module: 'domain/goals',
    purpose: 'goal path, required resources, sequence, and review rhythm',
  },
  {
    id: 'situation',
    label: 'Situation',
    module: 'domain/financial-foundation',
    purpose: 'current capital, income state, liquidity, exposure, and risk pressure',
  },
  {
    id: 'data',
    label: 'Data',
    module: 'domain/data',
    purpose: 'normalized input state and captured facts',
  },
  {
    id: 'model',
    label: 'Model',
    module: 'domain/model',
    purpose: 'scoring and recommendation rules',
  },
  {
    id: 'evidence',
    label: 'Evidence',
    module: 'domain/evidence',
    purpose: 'signals that support or challenge a decision',
  },
  {
    id: 'aiInterpretation',
    label: 'AI Interpretation',
    module: 'domain/ai-interpretation',
    purpose: 'plain-language decision reading',
  },
  {
    id: 'decision',
    label: 'Decision',
    module: 'domain/decision',
    purpose: 'decision record and outcome framing',
  },
  {
    id: 'memory',
    label: 'Memory',
    module: 'domain/memory',
    purpose: 'long-term learning from prior decisions',
  },
];

export const EXTENSION_MODULES = [
  'financial-foundation',
  'goals',
  'market-assets',
  'real-estate',
  'portfolio',
  'projection',
  'scenario',
  'risk-resilience',
  'life-board',
];

export function createPipelineTrace(outputs = {}) {
  return ARCHITECTURE_STAGES.map((stage) => ({
    ...stage,
    status: outputs[stage.id] ? 'ready' : 'pending',
    output: outputs[stage.id] ?? null,
  }));
}

export function getArchitectureMap() {
  return {
    name: 'LY-Scope-Ver.2 Core Decision Architecture',
    flow: ARCHITECTURE_STAGES.map((stage) => stage.label),
    extensionModules: EXTENSION_MODULES,
  };
}

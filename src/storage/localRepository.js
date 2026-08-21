const STORAGE_KEY = 'ly-scope-ver2-state';

export function loadState(defaultState) {
  if (typeof localStorage === 'undefined') return defaultState;

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState;
    return {
      ...defaultState,
      ...JSON.parse(raw),
    };
  } catch {
    return defaultState;
  }
}

export function saveState(state) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function clearState() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(STORAGE_KEY);
}

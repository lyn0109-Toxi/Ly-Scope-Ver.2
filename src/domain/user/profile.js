export const DEFAULT_USER_PROFILE = {
  id: 'local-user',
  name: 'LY',
  householdType: 'individual',
  decisionStyle: 'balanced',
  priorities: ['stability', 'growth', 'clarity'],
  updatedAt: null,
};

export function normalizeProfile(profile = {}) {
  const priorities = Array.isArray(profile.priorities)
    ? profile.priorities.filter(Boolean)
    : DEFAULT_USER_PROFILE.priorities;

  return {
    ...DEFAULT_USER_PROFILE,
    ...profile,
    name: String(profile.name || DEFAULT_USER_PROFILE.name).trim(),
    householdType: profile.householdType || DEFAULT_USER_PROFILE.householdType,
    decisionStyle: profile.decisionStyle || DEFAULT_USER_PROFILE.decisionStyle,
    priorities,
  };
}

export function updateProfile(profile, patch) {
  return normalizeProfile({
    ...profile,
    ...patch,
    updatedAt: new Date().toISOString(),
  });
}

export function describeUser(profile) {
  const normalized = normalizeProfile(profile);
  return {
    owner: normalized.name,
    decisionStyle: normalized.decisionStyle,
    primaryPriority: normalized.priorities[0] ?? 'clarity',
  };
}

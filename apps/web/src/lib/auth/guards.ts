import { DEFAULT_ROLE, type Role } from "./roles";

function toArray<T>(value: T | T[]): T[] {
  return Array.isArray(value) ? value : [value];
}

export function normalizeRoles(roles: Role[] | null | undefined): Role[] {
  if (!roles || roles.length === 0) {
    return [DEFAULT_ROLE];
  }

  return [...new Set(roles)];
}

export function hasRequiredRole(
  roles: Role[] | null | undefined,
  required: Role | Role[]
): boolean {
  const normalized = normalizeRoles(roles);
  const requiredList = toArray(required);

  return requiredList.some((role) => normalized.includes(role));
}

export function ensureRequiredRole(
  roles: Role[] | null | undefined,
  required: Role | Role[]
): Role[] {
  if (!hasRequiredRole(roles, required)) {
    throw new Error("Forbidden: missing required role");
  }

  return normalizeRoles(roles);
}

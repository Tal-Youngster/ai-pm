export const Roles = {
  Admin: "admin",
  Lead: "lead",
  Client: "client"
} as const;

export type Role = (typeof Roles)[keyof typeof Roles];

export const ALL_ROLES: Role[] = Object.values(Roles);

export const DEFAULT_ROLE: Role = Roles.Client;

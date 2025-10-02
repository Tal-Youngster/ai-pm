import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";

import { ALL_ROLES, DEFAULT_ROLE, type Role } from "./roles";
import { normalizeRoles } from "./guards";

function parseRoleList(rawRoles: unknown): Role[] {
  if (Array.isArray(rawRoles)) {
    const normalized = rawRoles
      .map((role) => (typeof role === "string" ? role.trim().toLowerCase() : ""))
      .filter((role): role is Role => ALL_ROLES.includes(role as Role));

    return normalized.length > 0 ? normalizeRoles(normalized) : [DEFAULT_ROLE];
  }

  if (typeof rawRoles !== "string") {
    return [DEFAULT_ROLE];
  }

  const matched = rawRoles
    .split(",")
    .map((role) => role.trim().toLowerCase())
    .filter((role): role is Role => ALL_ROLES.includes(role as Role));

  return matched.length > 0 ? normalizeRoles(matched) : [DEFAULT_ROLE];
}

const googleClientId = process.env.GOOGLE_CLIENT_ID ?? "";
const googleClientSecret = process.env.GOOGLE_CLIENT_SECRET ?? "";
const isGoogleProviderConfigured = Boolean(googleClientId && googleClientSecret);
const devSignInEmail = process.env.NEXTAUTH_DEV_FAKE_EMAIL ?? "dev@example.com";
const devDefaultRoles = parseRoleList(process.env.NEXTAUTH_DEV_DEFAULT_ROLES);

const providers: NextAuthOptions["providers"] = [];

if (isGoogleProviderConfigured) {
  providers.push(
    GoogleProvider({
      clientId: googleClientId,
      clientSecret: googleClientSecret
    })
  );
} else if (process.env.NODE_ENV !== "production") {
  providers.push(
    CredentialsProvider({
      id: "dev",
      name: "Dev Sign-In",
      credentials: {
        email: { label: "Email", type: "email", placeholder: devSignInEmail }
      },
      async authorize(credentials) {
        const email = (credentials?.email ?? devSignInEmail).trim().toLowerCase();
        if (!email) {
          return null;
        }

        return {
          id: email,
          email,
          roles: devDefaultRoles
        } satisfies { id: string; email: string; roles: Role[] };
      }
    })
  );
} else {
  throw new Error("Google OAuth provider must be configured in production");
}

export const primaryAuthProviderId = isGoogleProviderConfigured ? "google" : "dev";
export const hasGoogleAuthProvider = isGoogleProviderConfigured;
export const devAuthEmail = devSignInEmail;

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: "jwt"
  },
  providers,
  callbacks: {
    async jwt({ token, user, profile }) {
      if (profile?.email) {
        token.email = profile.email;
      }

      if (user && typeof user === "object" && "roles" in user) {
        token.roles = parseRoleList((user as { roles?: unknown }).roles);
      } else {
        token.roles = parseRoleList(token.roles ?? devDefaultRoles);
      }

      return token;
    },
    async session({ session, token }) {
      if (!session.user) {
        return session;
      }

      session.user.id = token.sub ?? session.user.email ?? "";
      session.user.email = session.user.email ?? (token.email as string | undefined) ?? "";
      session.user.roles = parseRoleList(token.roles ?? devDefaultRoles);

      return session;
    }
  }
};

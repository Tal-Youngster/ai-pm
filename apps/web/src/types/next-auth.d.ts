import type { Role } from "@/lib/auth/roles";
import type { DefaultSession, DefaultUser } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: DefaultSession["user"] & {
      id: string;
      roles: Role[];
    };
  }

  interface User extends DefaultUser {
    roles: Role[];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    roles?: Role[];
  }
}

export {};

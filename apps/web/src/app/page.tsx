import Link from "next/link";
import { getServerSession } from "next-auth";

import { SignInOutButtons } from "@/components/auth/SignInOutButtons";
import { Button } from "@/components/ui/button";
import {
  authOptions,
  devAuthEmail,
  hasGoogleAuthProvider,
  primaryAuthProviderId
} from "@/lib/auth/options";
import { hasRequiredRole } from "@/lib/auth/guards";
import { Roles } from "@/lib/auth/roles";

export default async function Page() {
  const session = await getServerSession(authOptions);
  const canAccessConsole = session?.user
    ? hasRequiredRole(session.user.roles, [Roles.Admin, Roles.Lead])
    : false;

  return (
    <main className="container flex min-h-screen flex-col items-center justify-center gap-8 py-16">
      <div className="max-w-2xl space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">AI PM Control Center</h1>
        <p className="text-muted-foreground">
          Kickstart the AI PM web experience with secure auth scaffolding. Sign in, explore the protected console,
          and iterate quickly with a modern frontend stack.
        </p>
      </div>
      <div className="flex flex-col items-center gap-4">
        <SignInOutButtons
          providerId={primaryAuthProviderId}
          hasGoogleProvider={hasGoogleAuthProvider}
          devEmail={devAuthEmail}
        />
        <div className="flex flex-wrap justify-center gap-3">
          <Button asChild>
            <Link href="/health">View Health Status</Link>
          </Button>
          <Button asChild disabled={!canAccessConsole} variant={canAccessConsole ? "default" : "secondary"}>
            <Link href={canAccessConsole ? "/console" : "#"}>
              {canAccessConsole ? "Open Console" : "Console requires admin or lead role"}
            </Link>
          </Button>
        </div>
        {session?.user && !canAccessConsole ? (
          <p className="text-sm text-muted-foreground">
            Signed in users with the admin or lead role can access the console. Update the assigned roles to proceed.
          </p>
        ) : null}
      </div>
    </main>
  );
}

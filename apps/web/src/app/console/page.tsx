import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";

import { SignInOutButtons } from "@/components/auth/SignInOutButtons";
import {
  authOptions,
  devAuthEmail,
  hasGoogleAuthProvider,
  primaryAuthProviderId
} from "@/lib/auth/options";
import { ensureRequiredRole } from "@/lib/auth/guards";
import { Roles } from "@/lib/auth/roles";

export default async function ConsolePage() {
  const session = await getServerSession(authOptions);

  if (!session?.user) {
    redirect("/api/auth/signin?callbackUrl=/console");
  }

  try {
    ensureRequiredRole(session.user.roles, [Roles.Admin, Roles.Lead]);
  } catch (error) {
    redirect("/?unauthorized=1");
  }

  return (
    <main className="container flex min-h-screen flex-col gap-8 py-12">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-wide text-muted-foreground">Console</p>
        <h1 className="text-3xl font-semibold">Welcome back, {session.user.name ?? session.user.email}</h1>
        <p className="text-muted-foreground">
          This protected workspace is gated behind admin and lead roles. Replace the fake RBAC data with
          production-grade claims once the identity provider is ready.
        </p>
      </header>
      <section className="grid gap-6 rounded-lg border bg-card p-6 shadow-sm">
        <article className="space-y-2">
          <h2 className="text-xl font-semibold">Session details</h2>
          <div className="space-y-1 text-sm">
            <p>Email: {session.user.email}</p>
            <p>Roles: {session.user.roles.join(", ")}</p>
          </div>
        </article>
        <div>
          <SignInOutButtons
            providerId={primaryAuthProviderId}
            hasGoogleProvider={hasGoogleAuthProvider}
            devEmail={devAuthEmail}
          />
        </div>
      </section>
    </main>
  );
}

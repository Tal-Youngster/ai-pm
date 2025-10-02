"use client";

import { signIn, signOut, useSession } from "next-auth/react";

import { Button } from "@/components/ui/button";

type SignInOutButtonsProps = {
  providerId: string;
  hasGoogleProvider: boolean;
  devEmail?: string;
};

export function SignInOutButtons({ providerId, hasGoogleProvider, devEmail }: SignInOutButtonsProps) {
  const { data: session, status } = useSession();

  const handleSignIn = () => {
    if (providerId === "dev") {
      void signIn(providerId, {
        callbackUrl: "/console",
        email: devEmail ?? "dev@example.com"
      });
      return;
    }

    void signIn(providerId, { callbackUrl: "/console" });
  };

  if (status === "loading") {
    return (
      <Button disabled variant="secondary">
        Checking session...
      </Button>
    );
  }

  if (!session?.user) {
    return (
      <div className="flex flex-col items-center gap-2">
        <Button onClick={handleSignIn}>
          {hasGoogleProvider ? "Sign in with Google" : "Sign in (dev mock)"}
        </Button>
        {!hasGoogleProvider ? (
          <p className="text-xs text-muted-foreground">
            Uses the dev credential provider with {devEmail ?? "dev@example.com"}.
          </p>
        ) : null}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-3 sm:flex-row">
      <span className="text-sm text-muted-foreground">Signed in as {session.user.email}</span>
      <Button variant="secondary" onClick={() => signOut({ callbackUrl: "/" })}>
        Sign out
      </Button>
    </div>
  );
}

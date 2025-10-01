"use client";

import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { getApiHealth } from "@/lib/api";

export default function HealthPage() {
  const { data, isError, error, isPending, refetch, isFetching } = useQuery({
    queryKey: ["health"],
    queryFn: getApiHealth,
    retry: false
  });

  return (
    <main className="container flex min-h-screen flex-col items-center justify-center gap-6 py-16">
      <div className="max-w-lg space-y-4 text-center">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">API Health Check</h1>
        <p className="text-muted-foreground">
          We call the platform endpoint <code>/v1/ping</code> to surface the latest status.
        </p>
      </div>

      <div className="w-full max-w-md rounded-lg border bg-card p-6 text-left shadow-sm">
        <h2 className="text-sm font-medium text-muted-foreground">Current status</h2>
        <div className="mt-3 space-y-2">
          {isPending ? (
            <p className="font-semibold text-muted-foreground">Loading...</p>
          ) : isError ? (
            <div className="space-y-1">
              <p className="font-semibold text-destructive">Unable to reach /v1/ping</p>
              <p className="text-sm text-muted-foreground">{error instanceof Error ? error.message : "Unknown error"}</p>
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-2xl font-bold">{data?.status ?? "Unknown"}</p>
              {data?.message ? <p className="text-sm text-muted-foreground">{data.message}</p> : null}
            </div>
          )}
        </div>
      </div>

      <Button onClick={() => refetch()} disabled={isFetching} variant="secondary">
        {isFetching ? "Refreshing..." : "Refresh"}
      </Button>
    </main>
  );
}


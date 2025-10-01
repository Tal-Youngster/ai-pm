import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Page() {
  return (
    <main className="container flex min-h-screen flex-col items-center justify-center gap-6 py-16">
      <div className="max-w-2xl space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">AI PM Control Center</h1>
        <p className="text-muted-foreground">
          Kickstart the AI PM web experience. Build new workflows, inspect health, and iterate quickly with
          a modern frontend stack.
        </p>
      </div>
      <Button asChild>
        <Link href="/health">View Health Status</Link>
      </Button>
    </main>
  );
}


"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

export default function Home() {
  const [pong, setPong] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function ping() {
    setLoading(true);
    setPong(null);
    try {
      const data = await apiFetch<{ pong: boolean }>("/api/ping/");
      setPong(JSON.stringify(data));
    } catch (err) {
      setPong(`error: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>django_next_starter</CardTitle>
          <CardDescription>
            Django + DRF + Allauth Headless backend, Next.js frontend.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 pb-4">
          <Button onClick={ping} size="lg" disabled={loading}>
            {loading ? "Pinging..." : "Ping backend"}
          </Button>
          <pre className="min-h-10 rounded-md bg-muted p-3 text-xs text-muted-foreground">
            {pong ?? "// click Ping backend"}
          </pre>
        </CardContent>
        <CardFooter className="gap-2">
          <Link href="/login">
            <Button variant="outline">Log in</Button>
          </Link>
          <Link href="/signup">
            <Button variant="outline">Sign up</Button>
          </Link>
          <Link href="/dashboard" className="ml-auto">
            <Button variant="ghost">Dashboard →</Button>
          </Link>
        </CardFooter>
      </Card>
    </main>
  );
}

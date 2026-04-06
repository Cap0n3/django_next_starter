"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiFetch, ApiError } from "@/lib/api";
import { logout } from "@/lib/auth";

interface Me {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Me>("/api/me/")
      .then(setMe)
      .catch((err) => {
        if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
          router.replace("/login");
          return;
        }
        setError((err as Error).message);
      });
  }, [router]);

  async function onLogout() {
    try {
      await logout();
    } finally {
      router.replace("/login");
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl items-center p-8">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Dashboard</CardTitle>
          <CardDescription>Authenticated session via Django + Allauth Headless.</CardDescription>
        </CardHeader>
        <CardContent>
          {error && <p className="text-sm text-red-600">{error}</p>}
          {!me && !error && <p className="text-sm text-black/60">Loading...</p>}
          {me && (
            <pre className="rounded bg-black/5 p-3 text-xs">
              {JSON.stringify(me, null, 2)}
            </pre>
          )}
        </CardContent>
        <CardFooter>
          <Button variant="destructive" onClick={onLogout}>
            Log out
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}

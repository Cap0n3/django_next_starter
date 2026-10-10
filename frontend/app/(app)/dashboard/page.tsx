"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircleIcon } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
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
import { formatAuthError, logout } from "@/lib/auth";

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
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    apiFetch<Me>("/api/me/")
      .then(setMe)
      .catch((err) => {
        if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
          router.replace("/login");
          return;
        }
        setError(formatAuthError(err));
      });
  }, [router]);

  async function onLogout() {
    setLoggingOut(true);
    try {
      await logout();
      router.replace("/login");
    } catch (err) {
      setError(formatAuthError(err));
      setLoggingOut(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl items-center p-8">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Dashboard</CardTitle>
          <CardDescription>Authenticated session via Django + Allauth Headless.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>Something went wrong</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {!me && !error && <p className="text-sm text-muted-foreground">Loading...</p>}
          {me && (
            <pre className="rounded-md bg-muted p-3 text-xs text-muted-foreground">
              {JSON.stringify(me, null, 2)}
            </pre>
          )}
        </CardContent>
        <CardFooter>
          <Button variant="destructive" onClick={onLogout} disabled={loggingOut}>
            {loggingOut ? "Logging out..." : "Log out"}
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}

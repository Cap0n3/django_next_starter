"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AlertCircleIcon, CheckCircle2Icon } from "lucide-react";
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
import { formatAuthError, getEmailVerification, getSession, verifyEmail } from "@/lib/auth";

type State =
  | { kind: "loading" }
  | { kind: "ready"; email: string }
  | { kind: "verifying"; email: string }
  | { kind: "done"; email: string; loggedIn: boolean }
  | { kind: "error"; message: string };

/**
 * Landing page for the link in the verification email
 * (HEADLESS_FRONTEND_URLS["account_confirm_email"] on the backend).
 */
export default function VerifyEmailPage() {
  const { key } = useParams<{ key: string }>();
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await getSession(); // ensure csrftoken cookie
        const info = await getEmailVerification(key);
        if (!cancelled) setState({ kind: "ready", email: info.data?.email ?? "" });
      } catch (err) {
        if (!cancelled) {
          setState({ kind: "error", message: linkError(err) });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [key]);

  async function onConfirm() {
    if (state.kind !== "ready") return;
    const { email } = state;
    setState({ kind: "verifying", email });
    try {
      const res = await verifyEmail(key);
      setState({ kind: "done", email, loggedIn: res.meta?.is_authenticated === true });
    } catch (err) {
      setState({ kind: "error", message: linkError(err) });
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Verify your email</CardTitle>
          <CardDescription>Confirm that this address belongs to you.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 pb-4">
          {state.kind === "loading" && (
            <p className="text-sm text-muted-foreground">Checking your link...</p>
          )}
          {(state.kind === "ready" || state.kind === "verifying") && (
            <p className="text-sm">
              Verify <span className="font-medium">{state.email}</span>?
            </p>
          )}
          {state.kind === "done" && (
            <Alert>
              <CheckCircle2Icon />
              <AlertTitle>Email verified</AlertTitle>
              <AlertDescription>{state.email} is now confirmed.</AlertDescription>
            </Alert>
          )}
          {state.kind === "error" && (
            <Alert variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>Verification failed</AlertTitle>
              <AlertDescription>{state.message}</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          {(state.kind === "ready" || state.kind === "verifying") && (
            <Button
              size="lg"
              className="w-full"
              onClick={onConfirm}
              disabled={state.kind === "verifying"}
            >
              {state.kind === "verifying" ? "Verifying..." : "Confirm"}
            </Button>
          )}
          {state.kind === "done" && (
            <Button size="lg" className="w-full" asChild>
              <Link href={state.loggedIn ? "/dashboard" : "/login"}>
                {state.loggedIn ? "Go to dashboard" : "Log in"}
              </Link>
            </Button>
          )}
          {state.kind === "error" && (
            <Button size="lg" variant="outline" className="w-full" asChild>
              <Link href="/login">Back to login</Link>
            </Button>
          )}
        </CardFooter>
      </Card>
    </main>
  );
}

function linkError(err: unknown): string {
  const msg = formatAuthError(err);
  return msg.startsWith("Request failed")
    ? "This verification link is invalid or has expired."
    : msg;
}

/**
 * Thin wrappers around the django-allauth Headless "browser" endpoints.
 *
 * Docs: https://docs.allauth.org/en/latest/headless/openapi-specification/
 *
 * Browser flows rely on Django's session cookie, which is exactly what we
 * want here — the Next.js dev server (3000) talks to Django (8001) and the
 * session cookie is shared via CORS + credentials.
 */

import { apiFetch, ApiError } from "./api";

const BASE = "/_allauth/browser/v1";

export interface AuthUser {
  id: number;
  email: string;
  display?: string;
  has_usable_password?: boolean;
}

export interface AuthError {
  message: string;
  code: string;
  param?: string;
}

export interface SessionResponse {
  status: number;
  data?: { user?: AuthUser };
  meta?: { is_authenticated?: boolean };
  errors?: AuthError[];
}

export interface EmailVerificationInfo {
  status: number;
  data?: { email: string; user: AuthUser };
  meta?: { is_authenticating?: boolean };
}

function isSessionResponse(data: unknown): data is SessionResponse {
  return typeof data === "object" && data !== null && "status" in data;
}

/**
 * allauth answers 401 whenever the session is *not* authenticated — including
 * right after a successful logout. For the calls below that is a valid state,
 * not a failure, so unwrap it instead of throwing.
 */
async function unauthenticatedOk(
  request: Promise<SessionResponse>
): Promise<SessionResponse> {
  try {
    return await request;
  } catch (err) {
    if (err instanceof ApiError && err.status === 401 && isSessionResponse(err.data)) {
      return err.data;
    }
    throw err;
  }
}

/** Current session state. Also makes Django set the `csrftoken` cookie. */
export function getSession(): Promise<SessionResponse> {
  return unauthenticatedOk(apiFetch<SessionResponse>(`${BASE}/auth/session`));
}

export function signup(input: { email: string; password: string }) {
  return apiFetch<SessionResponse>(`${BASE}/auth/signup`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function login(input: { email: string; password: string }) {
  return apiFetch<SessionResponse>(`${BASE}/auth/login`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

/** Ends the session. Resolves (with the now-anonymous session) on success. */
export function logout(): Promise<SessionResponse> {
  return unauthenticatedOk(
    apiFetch<SessionResponse>(`${BASE}/auth/session`, { method: "DELETE" })
  );
}

/** Looks up which address a verification key belongs to (does not verify). */
export function getEmailVerification(key: string) {
  return apiFetch<EmailVerificationInfo>(`${BASE}/auth/email/verify`, {
    headers: { "X-Email-Verification-Key": key },
  });
}

/**
 * Confirms an email address. allauth returns 200 when the user is logged in
 * and 401 when the address was verified but no session exists; both mean the
 * address is now verified.
 */
export function verifyEmail(key: string): Promise<SessionResponse> {
  return unauthenticatedOk(
    apiFetch<SessionResponse>(`${BASE}/auth/email/verify`, {
      method: "POST",
      body: JSON.stringify({ key }),
    })
  );
}

/**
 * Turns any thrown error into user-facing text. allauth validation errors
 * arrive as `{ errors: [{ message, code, param }] }`; everything else gets a
 * generic message rather than a raw JSON dump.
 */
export function formatAuthError(err: unknown): string {
  if (err instanceof ApiError) {
    const data = err.data as Partial<SessionResponse> | null;
    if (data?.errors?.length) {
      return data.errors
        .map((e) => (e.param ? `${capitalize(e.param)}: ${e.message}` : e.message))
        .join(" ");
    }
    if (err.status === 429) return "Too many attempts. Please wait a moment and try again.";
    if (err.status >= 500) return "The server had a problem. Please try again later.";
    return "Request failed. Please check your input and try again.";
  }
  if (err instanceof TypeError) {
    // fetch() network failure (backend down, CORS, DNS)
    return "Could not reach the server. Is the backend running?";
  }
  return "Something went wrong. Please try again.";
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

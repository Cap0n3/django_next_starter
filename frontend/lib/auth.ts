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

export interface SessionResponse {
  status: number;
  data?: { user?: AuthUser };
  meta?: { is_authenticated?: boolean };
}

export async function getSession(): Promise<SessionResponse | null> {
  try {
    return await apiFetch<SessionResponse>(`${BASE}/auth/session`);
  } catch (err) {
    // 401 just means "not logged in" — surface as null instead of throwing
    if (err instanceof ApiError && err.status === 401) {
      return err.data as SessionResponse;
    }
    throw err;
  }
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

export function logout() {
  return apiFetch<SessionResponse>(`${BASE}/auth/session`, {
    method: "DELETE",
  });
}

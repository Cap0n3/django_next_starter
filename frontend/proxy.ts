import { NextResponse, type NextRequest } from "next/server";

/**
 * Soft route protection based on the Django `sessionid` cookie.
 *
 * (Next.js 16 renamed `middleware.ts` to `proxy.ts`; same API, Node runtime.)
 *
 * - PROTECTED routes redirect to /login when the cookie is missing.
 * - GUEST_ONLY routes redirect to /dashboard when the cookie is present.
 *
 * This is just a UX optimization — the backend is the source of truth.
 * Cookie presence ≠ valid session. /api/me/ will still 401 on a stale
 * sessionid, and the dashboard handles that case.
 */
const PROTECTED = ["/dashboard"];
const GUEST_ONLY = ["/login", "/signup"];

export function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const hasSession = req.cookies.has("sessionid");

  if (PROTECTED.some((p) => pathname.startsWith(p)) && !hasSession) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }

  if (GUEST_ONLY.some((p) => pathname.startsWith(p)) && hasSession) {
    const url = req.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/signup"],
};

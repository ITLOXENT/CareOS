import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SESSION_COOKIE, tokenHash } from "../../../lib/auth";
import { revokeSession } from "../../../lib/session-store";

export async function POST() {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (token) {
    revokeSession(tokenHash(token));
  }
  const response = NextResponse.json({ ok: true });
  response.cookies.set(SESSION_COOKIE, "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 0,
    path: "/"
  });
  return response;
}

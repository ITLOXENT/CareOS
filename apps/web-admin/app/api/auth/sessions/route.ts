import { NextResponse } from "next/server";

import { getSession, tokenHash } from "../../../lib/auth";
import { listSessions, revokeSession } from "../../../lib/session-store";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }
  return NextResponse.json({ results: listSessions() });
}

export async function POST(request: Request) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }
  const payload = await request.json().catch(() => ({}));
  const tokenHashValue = String(payload.token_hash ?? "");
  if (!tokenHashValue) {
    return NextResponse.json({ detail: "token_hash required" }, { status: 400 });
  }
  revokeSession(tokenHashValue);
  return NextResponse.json({ ok: true });
}

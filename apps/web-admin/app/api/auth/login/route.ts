import crypto from "crypto";

import { NextResponse } from "next/server";

import {
  createSessionToken,
  recordSession,
  SESSION_COOKIE,
  SESSION_MAX_AGE_SECONDS
} from "../../../lib/auth";

const MAX_ATTEMPTS = 5;
const WINDOW_SECONDS = 600;
const LOCKOUT_SECONDS = 900;
const attempts = new Map<string, { count: number; firstAt: number; lockedUntil?: number }>();

function timingSafeMatch(a: string, b: string): boolean {
  const aBuf = Buffer.from(a);
  const bBuf = Buffer.from(b);
  if (aBuf.length !== bBuf.length) {
    return false;
  }
  return crypto.timingSafeEqual(aBuf, bBuf);
}

function getClientKey(request: Request, username: string) {
  const forwarded = request.headers.get("x-forwarded-for") ?? "";
  const ip = forwarded.split(",")[0]?.trim() || request.headers.get("x-real-ip") || "unknown";
  return `${ip}:${username}`;
}

function enforceRateLimit(key: string): { allowed: boolean; retryAfter?: number } {
  const now = Math.floor(Date.now() / 1000);
  const entry = attempts.get(key) ?? { count: 0, firstAt: now };
  if (entry.lockedUntil && entry.lockedUntil > now) {
    return { allowed: false, retryAfter: entry.lockedUntil - now };
  }
  if (now - entry.firstAt > WINDOW_SECONDS) {
    entry.count = 0;
    entry.firstAt = now;
  }
  if (entry.count >= MAX_ATTEMPTS) {
    entry.lockedUntil = now + LOCKOUT_SECONDS;
    attempts.set(key, entry);
    return { allowed: false, retryAfter: LOCKOUT_SECONDS };
  }
  attempts.set(key, entry);
  return { allowed: true };
}

function registerFailure(key: string) {
  const now = Math.floor(Date.now() / 1000);
  const entry = attempts.get(key) ?? { count: 0, firstAt: now };
  if (now - entry.firstAt > WINDOW_SECONDS) {
    entry.count = 0;
    entry.firstAt = now;
  }
  entry.count += 1;
  if (entry.count >= MAX_ATTEMPTS) {
    entry.lockedUntil = now + LOCKOUT_SECONDS;
  }
  attempts.set(key, entry);
}

function passwordPolicySatisfied(password: string) {
  return password.length >= 12;
}

function base32ToBytes(secret: string): Buffer {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  const cleaned = secret.replace(/=+$/, "").toUpperCase().replace(/[^A-Z2-7]/g, "");
  let bits = "";
  for (const char of cleaned) {
    const value = alphabet.indexOf(char);
    if (value === -1) {
      continue;
    }
    bits += value.toString(2).padStart(5, "0");
  }
  const bytes = [];
  for (let i = 0; i + 8 <= bits.length; i += 8) {
    bytes.push(parseInt(bits.slice(i, i + 8), 2));
  }
  return Buffer.from(bytes);
}

function verifyTotp(secret: string, code: string, window = 1): boolean {
  const key = base32ToBytes(secret);
  const timestep = 30;
  const counter = Math.floor(Date.now() / 1000 / timestep);
  const normalized = code.replace(/\s+/g, "");
  for (let offset = -window; offset <= window; offset += 1) {
    const buf = Buffer.alloc(8);
    buf.writeBigInt64BE(BigInt(counter + offset));
    const hmac = crypto.createHmac("sha1", key).update(buf).digest();
    const hashOffset = hmac[hmac.length - 1] & 0xf;
    const binary =
      ((hmac[hashOffset] & 0x7f) << 24) |
      ((hmac[hashOffset + 1] & 0xff) << 16) |
      ((hmac[hashOffset + 2] & 0xff) << 8) |
      (hmac[hashOffset + 3] & 0xff);
    const otp = String(binary % 1_000_000).padStart(6, "0");
    if (timingSafeMatch(otp, normalized)) {
      return true;
    }
  }
  return false;
}

async function sendAuditEvent(outcome: "success" | "failure", username: string) {
  const baseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL || "";
  const auditSecret = process.env.ADMIN_AUDIT_SECRET || "";
  if (!baseUrl || !auditSecret) {
    return;
  }
  try {
    await fetch(`${baseUrl}/auth/admin/audit/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Audit-Token": auditSecret
      },
      body: JSON.stringify({ outcome, username })
    });
  } catch {
    // ignore audit failures
  }
}

export async function POST(request: Request) {
  const configuredUser = process.env.ADMIN_USERNAME;
  const configuredPassword = process.env.ADMIN_PASSWORD;
  const totpSecret = process.env.ADMIN_TOTP_SECRET;
  const mfaRequired =
    (process.env.ADMIN_MFA_REQUIRED ?? (process.env.NODE_ENV === "production" ? "true" : "false")) ===
    "true";

  if (!configuredUser || !configuredPassword) {
    return NextResponse.json(
      { detail: "Admin credentials are not configured." },
      { status: 500 }
    );
  }

  if (!passwordPolicySatisfied(configuredPassword)) {
    return NextResponse.json(
      { detail: "Admin password policy not satisfied." },
      { status: 500 }
    );
  }

  if (mfaRequired && !totpSecret) {
    return NextResponse.json(
      { detail: "MFA is required but no TOTP secret is configured." },
      { status: 500 }
    );
  }

  const body = await request.json().catch(() => ({}));
  const username = String(body.username ?? "");
  const password = String(body.password ?? "");
  const otp = String(body.otp ?? "");
  const key = getClientKey(request, username);
  const limit = enforceRateLimit(key);
  if (!limit.allowed) {
    return NextResponse.json(
      { detail: "Too many attempts. Try later." },
      { status: 429 }
    );
  }

  const userMatches = timingSafeMatch(username, configuredUser);
  const passwordMatches = timingSafeMatch(password, configuredPassword);

  if (!userMatches || !passwordMatches) {
    registerFailure(key);
    await sendAuditEvent("failure", username);
    return NextResponse.json({ detail: "Invalid credentials." }, { status: 401 });
  }

  if (totpSecret && !verifyTotp(totpSecret, otp)) {
    registerFailure(key);
    await sendAuditEvent("failure", username);
    return NextResponse.json({ detail: "Invalid MFA code." }, { status: 401 });
  }

  const token = createSessionToken(username, { mfaVerified: Boolean(totpSecret) || !mfaRequired });
  const issuedAt = Math.floor(Date.now() / 1000);
  recordSession(token, username, issuedAt);
  await sendAuditEvent("success", username);
  const response = NextResponse.json({ ok: true });
  response.cookies.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: SESSION_MAX_AGE_SECONDS,
    path: "/"
  });

  return response;
}

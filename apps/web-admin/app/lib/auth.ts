import crypto from "crypto";

import { cookies } from "next/headers";

import {
  getSessionRecord,
  getTokenHash,
  isRevoked,
  registerSession,
  revokeSession,
  touchSession,
  listSessions
} from "./session-store";
export type Session = {
  username: string;
  role: string;
  orgId?: string;
  orgName?: string;
  issuedAt: number;
  mfaVerified: boolean;
};

export const SESSION_COOKIE = "careos_admin_session";
export const SESSION_MAX_AGE_SECONDS = 60 * 60 * 8;
export const SESSION_IDLE_SECONDS = Number(process.env.ADMIN_SESSION_IDLE_SECONDS ?? 30 * 60);

const DEFAULT_ROLE = "ADMIN";

function getSecret(): string {
  const secret = process.env.ADMIN_SESSION_SECRET;
  if (!secret && process.env.NODE_ENV === "production") {
    throw new Error("ADMIN_SESSION_SECRET must be set in production.");
  }
  return secret ?? "dev-insecure-secret";
}

function base64UrlEncode(value: string): string {
  return Buffer.from(value).toString("base64url");
}

function base64UrlDecode(value: string): string {
  return Buffer.from(value, "base64url").toString("utf8");
}

function sign(value: string): string {
  return crypto.createHmac("sha256", getSecret()).update(value).digest("base64url");
}

function safeEqual(a: string, b: string): boolean {
  const aBuf = Buffer.from(a);
  const bBuf = Buffer.from(b);
  if (aBuf.length !== bBuf.length) {
    return false;
  }
  return crypto.timingSafeEqual(aBuf, bBuf);
}

export function createSessionToken(
  username: string,
  options?: { mfaVerified?: boolean }
): string {
  const payload = {
    username,
    role: process.env.ADMIN_ROLE ?? DEFAULT_ROLE,
    orgId: process.env.ADMIN_ORG_ID,
    orgName: process.env.ADMIN_ORG_NAME,
    issuedAt: Math.floor(Date.now() / 1000),
    mfaVerified: options?.mfaVerified ?? false
  };
  const encoded = base64UrlEncode(JSON.stringify(payload));
  const signature = sign(encoded);
  return `${encoded}.${signature}`;
}

export function verifySessionToken(token: string): Session | null {
  if (isRevoked(token)) {
    return null;
  }
  const parts = token.split(".");
  if (parts.length !== 2) {
    return null;
  }
  const [payload, signature] = parts;
  const expected = sign(payload);
  if (!safeEqual(signature, expected)) {
    return null;
  }
  const data = JSON.parse(base64UrlDecode(payload)) as Session;
  const now = Math.floor(Date.now() / 1000);
  if (now - data.issuedAt > SESSION_MAX_AGE_SECONDS) {
    return null;
  }
  const record = getSessionRecord(token);
  if (record && now - record.lastSeenAt > SESSION_IDLE_SECONDS) {
    revokeSession(record.tokenHash);
    return null;
  }
  if (!listSessions().some((session) => session.tokenHash === getTokenHash(token))) {
    registerSession(token, data.username, data.issuedAt);
  } else {
    touchSession(token);
  }
  return data;
}

export function recordSession(token: string, username: string, issuedAt: number): string {
  return registerSession(token, username, issuedAt);
}

export function tokenHash(token: string): string {
  return getTokenHash(token);
}

export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (!token) {
    return null;
  }
  return verifySessionToken(token);
}

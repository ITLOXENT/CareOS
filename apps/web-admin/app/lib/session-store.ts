import crypto from "crypto";

import { SESSION_MAX_AGE_SECONDS } from "./auth";

type SessionRecord = {
  tokenHash: string;
  username: string;
  issuedAt: number;
  lastSeenAt: number;
  revokedAt?: number;
};

const sessions = new Map<string, SessionRecord>();
const revoked = new Set<string>();

function hashToken(token: string): string {
  return crypto.createHash("sha256").update(token).digest("hex");
}

function prune() {
  const now = Math.floor(Date.now() / 1000);
  for (const [tokenHash, record] of sessions.entries()) {
    if (now - record.issuedAt > SESSION_MAX_AGE_SECONDS || record.revokedAt) {
      sessions.delete(tokenHash);
    }
  }
}

export function registerSession(token: string, username: string, issuedAt: number) {
  const tokenHash = hashToken(token);
  sessions.set(tokenHash, {
    tokenHash,
    username,
    issuedAt,
    lastSeenAt: issuedAt
  });
  return tokenHash;
}

export function touchSession(token: string) {
  const tokenHash = hashToken(token);
  const record = sessions.get(tokenHash);
  if (record) {
    record.lastSeenAt = Math.floor(Date.now() / 1000);
  }
}

export function getSessionRecord(token: string) {
  const tokenHash = hashToken(token);
  return sessions.get(tokenHash) ?? null;
}

export function listSessions() {
  prune();
  return Array.from(sessions.values()).map((record) => ({
    tokenHash: record.tokenHash,
    username: record.username,
    issuedAt: record.issuedAt,
    lastSeenAt: record.lastSeenAt,
    revokedAt: record.revokedAt ?? null
  }));
}

export function revokeSession(tokenHash: string) {
  revoked.add(tokenHash);
  const record = sessions.get(tokenHash);
  if (record) {
    record.revokedAt = Math.floor(Date.now() / 1000);
  }
}

export function isRevoked(token: string): boolean {
  const tokenHash = hashToken(token);
  return revoked.has(tokenHash);
}

export function getTokenHash(token: string): string {
  return hashToken(token);
}

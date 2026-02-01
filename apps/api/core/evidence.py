from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

from .models import EpisodeEvent, Signature


def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_event_hash(event: EpisodeEvent, previous_hash: str) -> str:
    payload = json.dumps(
        {
            "id": event.id,
            "event_type": event.event_type,
            "from_state": event.from_state,
            "to_state": event.to_state,
            "note": event.note,
            "payload_json": event.payload_json,
            "created_at": event.created_at.isoformat(),
            "prev": previous_hash,
        },
        sort_keys=True,
    )
    return _hash_payload(payload)


def build_manifest(events: Iterable[EpisodeEvent], signatures: Iterable[Signature]) -> dict:
    chain: list[dict] = []
    previous_hash = "GENESIS"
    for event in events:
        event_hash = build_event_hash(event, previous_hash)
        chain.append(
            {
                "id": event.id,
                "event_type": event.event_type,
                "from_state": event.from_state,
                "to_state": event.to_state,
                "note": event.note,
                "payload_json": event.payload_json,
                "created_at": event.created_at.isoformat(),
                "prev_hash": previous_hash,
                "hash": event_hash,
            }
        )
        previous_hash = event_hash

    signatures_payload = [
        {
            "id": signature.id,
            "response_id": signature.response_id,
            "signer_id": signature.signer_id,
            "template_version": signature.template_version,
            "signed_at": signature.signed_at.isoformat(),
        }
        for signature in signatures
    ]

    return {
        "events": chain,
        "signatures": signatures_payload,
        "final_hash": previous_hash,
    }


def verify_hash_chain(events_payload: list[dict]) -> bool:
    previous_hash = "GENESIS"
    for event in events_payload:
        payload = json.dumps(
            {
                "id": event["id"],
                "event_type": event["event_type"],
                "from_state": event["from_state"],
                "to_state": event["to_state"],
                "note": event["note"],
                "payload_json": event.get("payload_json", {}),
                "created_at": event["created_at"],
                "prev": previous_hash,
            },
            sort_keys=True,
        )
        expected = _hash_payload(payload)
        if event["hash"] != expected:
            return False
        previous_hash = expected
    return True


def build_pdf(text_lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 12 Tf", "72 720 Td"]
    for index, line in enumerate(text_lines):
        if index > 0:
            content_lines.append("0 -16 Td")
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"({safe}) Tj")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines)
    content_bytes = content_stream.encode("utf-8")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj"
    )
    objects.append(
        f"4 0 obj << /Length {len(content_bytes)} >> stream\n{content_stream}\nendstream endobj".encode(
            "utf-8"
        )
    )
    objects.append(
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj"
    )

    xref_positions = []
    output = b"%PDF-1.4\n"
    for obj in objects:
        xref_positions.append(len(output))
        output += obj + b"\n"

    xref_start = len(output)
    output += f"xref\n0 {len(objects) + 1}\n".encode("utf-8")
    output += b"0000000000 65535 f \n"
    for pos in xref_positions:
        output += f"{pos:010d} 00000 n \n".encode("utf-8")
    output += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode(
            "utf-8"
        )
    )
    return output

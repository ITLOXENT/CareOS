#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import urllib.request


def main() -> int:
    base_url = os.environ.get("SMOKE_BASE_URL", "").rstrip("/")
    if not base_url:
        print("SMOKE_BASE_URL is required.")
        return 1
    url = f"{base_url}/health/"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except Exception as exc:  # pragma: no cover
        print(f"Smoke test failed: {exc}")
        return 1
    if status != 200 or '"status"' not in body:
        print(f"Unexpected response: {status} {body}")
        return 1
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

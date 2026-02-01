from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from django.conf import settings


class EvidenceStorage:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = Path(base_dir or settings.EVIDENCE_STORAGE_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_obj) -> tuple[str, str, int]:
        extension = Path(file_obj.name).suffix
        file_id = uuid.uuid4().hex
        storage_name = f"{file_id}{extension}"
        destination = self.base_dir / storage_name
        hasher = hashlib.sha256()
        size = 0
        with destination.open("wb") as handle:
            for chunk in file_obj.chunks():
                handle.write(chunk)
                hasher.update(chunk)
                size += len(chunk)
        return storage_name, hasher.hexdigest(), size

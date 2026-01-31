from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from core.openapi import build_openapi_spec


class Command(BaseCommand):
    help = "Generate OpenAPI schema for CareOS API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="openapi.json",
            help="Output path relative to apps/api (default: openapi.json).",
        )

    def handle(self, *args, **options):
        output_rel = options["output"]
        output_path = Path(__file__).resolve().parents[3] / output_rel
        spec = build_openapi_spec()
        output_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        self.stdout.write(f"Wrote OpenAPI schema to {output_path}")

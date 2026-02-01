from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from core.models import AuditEvent, Organization


class Command(BaseCommand):
    help = "Export audit events for an organization to JSON."

    def add_arguments(self, parser):
        parser.add_argument("--org-slug", required=True)
        parser.add_argument("--output", default="audit-events.json")

    def handle(self, *args, **options):
        org_slug = options["org_slug"]
        output_path = Path(options["output"]).resolve()
        org = Organization.objects.filter(slug=org_slug).first()
        if not org:
            self.stderr.write("Organization not found.")
            return
        events = AuditEvent.objects.filter(organization=org).order_by("created_at")
        payload = [
            {
                "id": event.id,
                "action": event.action,
                "target_type": event.target_type,
                "target_id": event.target_id,
                "created_at": event.created_at.isoformat(),
                "metadata": event.metadata,
            }
            for event in events
        ]
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
        self.stdout.write(f"Exported {len(payload)} events to {output_path}")

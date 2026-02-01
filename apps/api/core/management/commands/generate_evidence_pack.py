from __future__ import annotations

from django.core.management.base import BaseCommand

from core.evidence import build_manifest, build_pdf, verify_hash_chain
from core.models import AIArtifact, EvidencePack, Episode, EpisodeEvent, Signature


class Command(BaseCommand):
    help = "Generate an evidence pack for an episode."

    def add_arguments(self, parser):
        parser.add_argument("--episode-id", type=int, required=True)

    def handle(self, *args, **options):
        episode_id = options["episode_id"]
        episode = Episode.objects.filter(id=episode_id).first()
        if not episode:
            self.stderr.write("Episode not found.")
            return
        unapproved = AIArtifact.objects.filter(episode=episode).exclude(status="approved")
        if unapproved.exists():
            self.stderr.write("AI artifacts must be approved before export.")
            return
        events = EpisodeEvent.objects.filter(episode=episode).order_by("created_at", "id")
        signatures = Signature.objects.filter(response__episode=episode).order_by("signed_at")
        manifest = build_manifest(events, signatures)
        if not verify_hash_chain(manifest["events"]):
            self.stderr.write("Hash chain invalid.")
            return
        pdf = build_pdf(
            [
                "CareOS Evidence Pack",
                f"Episode: {episode.id}",
                f"Events: {len(manifest['events'])}",
                f"Signatures: {len(manifest['signatures'])}",
                f"Final hash: {manifest['final_hash']}",
            ]
        )
        pack = EvidencePack.objects.create(
            organization=episode.organization,
            episode=episode,
            manifest=manifest,
            pdf_bytes=pdf,
        )
        self.stdout.write(f"Evidence pack generated: {pack.id}")

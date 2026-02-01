from __future__ import annotations

import os

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_storage_key(apps, schema_editor) -> None:
    EvidenceItem = apps.get_model("core", "EvidenceItem")
    for item in EvidenceItem.objects.all():
        if not item.storage_key:
            item.storage_key = os.path.basename(item.storage_path or "")
            item.save(update_fields=["storage_key"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_episode_tables_fix"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="evidenceitem",
            name="storage_key",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="evidenceitem",
            name="uploaded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="uploaded_evidence_items",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="EpisodeEvidence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "added_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.episode"
                    ),
                ),
                (
                    "evidence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.evidenceitem",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.organization",
                    ),
                ),
            ],
            options={"unique_together": {("episode", "evidence")}},
        ),
        migrations.RunPython(backfill_storage_key, reverse_code=migrations.RunPython.noop),
    ]

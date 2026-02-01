from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_evidence_storage_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="kind",
            field=models.CharField(default="general", max_length=64),
        ),
    ]

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0022_indexes_and_pagination"),
    ]

    operations = [
        migrations.AddField(
            model_name="evidenceitem",
            name="retention_class",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="evidenceitem",
            name="retention_until",
            field=models.DateField(blank=True, null=True),
        ),
    ]

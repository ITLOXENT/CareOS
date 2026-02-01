from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0025_privacy_dsar"),
    ]

    operations = [
        migrations.AddField(
            model_name="auditevent",
            name="request_id",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]

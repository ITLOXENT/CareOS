from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_integrations_framework"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AIReviewRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("input_type", models.CharField(max_length=120)),
                ("payload", models.JSONField(default=dict)),
                ("status", models.CharField(default="pending", max_length=32)),
                ("output", models.JSONField(blank=True, default=dict)),
                ("model_provider", models.CharField(blank=True, max_length=64)),
                ("model_version", models.CharField(blank=True, max_length=64)),
                ("model_name", models.CharField(blank=True, max_length=64)),
                ("error", models.TextField(blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization"),
                ),
            ],
        ),
    ]

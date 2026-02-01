from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_evidence_mvp"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField(blank=True)),
                ("url", models.CharField(blank=True, max_length=512)),
                ("unread", models.BooleanField(default=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("dedupe_key", models.CharField(blank=True, max_length=120, null=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization"),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                fields=("organization", "recipient", "dedupe_key"),
                name="unique_notification_dedupe",
                condition=Q(("dedupe_key__isnull", False)),
            ),
        ),
    ]

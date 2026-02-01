from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_ai_artifacts"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InteropMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("external_system", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("queued", "Queued"), ("sent", "Sent"), ("delivered", "Delivered"), ("failed", "Failed")], default="draft", max_length=16)),
                ("status_reason", models.TextField(blank=True)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("last_error", models.TextField(blank=True)),
                ("simulator_mode", models.BooleanField(default=False)),
                ("external_id", models.CharField(blank=True, max_length=128)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("episode", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.episode")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization")),
            ],
        ),
        migrations.CreateModel(
            name="InteropStatusEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("queued", "Queued"), ("sent", "Sent"), ("delivered", "Delivered"), ("failed", "Failed")], max_length=16)),
                ("detail", models.TextField(blank=True)),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_events", to="core.interopmessage")),
            ],
        ),
    ]

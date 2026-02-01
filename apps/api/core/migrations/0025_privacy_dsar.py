from __future__ import annotations

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0024_integration_api_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="retention_class",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="patient",
            name="retention_until",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="episode",
            name="retention_class",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="episode",
            name="retention_until",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ConsentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("subject_type", models.CharField(max_length=32)),
                ("subject_id", models.CharField(max_length=64)),
                ("consent_type", models.CharField(max_length=120)),
                ("policy_version", models.CharField(max_length=64)),
                ("channel", models.CharField(blank=True, max_length=64)),
                ("granted", models.BooleanField(default=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DsarExport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("subject_type", models.CharField(max_length=32)),
                ("subject_id", models.CharField(max_length=64)),
                ("status", models.CharField(default="pending", max_length=32)),
                ("params_json", models.JSONField(blank=True, default=dict)),
                ("artifact_path", models.CharField(blank=True, max_length=512)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
